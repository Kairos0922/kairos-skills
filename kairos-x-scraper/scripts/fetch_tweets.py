#!/usr/bin/env python3
"""
kairos-x-scraper — 按博主增量抓取 X.com 公开推文
用法: python3 fetch_tweets.py <handle> [--days N] [--force]

数据按博主+日期分文件: ~/.kairos/x-scraper/{handle}/YYYY-MM-DD.jsonl
读取最近N天 = N个小文件，不碰历史数据。
"""

import json, time, sys, re, os, argparse
from datetime import datetime, timedelta, timezone

try:
    import requests
    import urllib3
except ImportError:
    print("❌ 缺少 requests 库。运行: pip3 install requests")
    sys.exit(1)

# ---- 错误分类体系 (Class F) ----
class ScraperError(Exception):
    """基础异常，携带退出码"""
    def __init__(self, msg, exit_code=1):
        super().__init__(msg)
        self.exit_code = exit_code

class NetworkError(ScraperError):
    """网络不可达（ConnectionError/Timeout/SSLError/DNS）"""
    def __init__(self, msg, original=None):
        hint = ""
        if isinstance(original, requests.exceptions.SSLError):
            hint = "  💡 尝试加 --insecure 绕过 SSL 验证"
        elif isinstance(original, requests.exceptions.ConnectionError):
            hint = "  💡 检查网络连接或代理设置"
        elif isinstance(original, requests.exceptions.Timeout):
            hint = "  💡 网络超时，可重试"
        super().__init__(f"🌐 网络错误: {msg}{hint}", exit_code=2)
        self.original = original

class AuthError(ScraperError):
    """认证失败（401 / token过期）"""
    def __init__(self, msg):
        super().__init__(f"🔑 认证失败: {msg}\n   💡 请重新获取 auth_token 和 ct0，写入 {CONFIG_PATH}", exit_code=1)

class RateLimitError(ScraperError):
    """限流（429）"""
    def __init__(self, msg):
        super().__init__(f"⏳ 限流: {msg}", exit_code=2)

# 抓取统计（Class F: 不再静默吞错误）
_stats = {"skipped_parse": 0, "retries": 0, "degraded": False, "degraded_reason": ""}

BEARER = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
CONFIG_PATH = os.path.expanduser("~/.kairos/kairos-x-scraper-config.json")
DATA_BASE = os.path.expanduser("~/.kairos/x-scraper")

# ---- 命令行 ----
parser = argparse.ArgumentParser(description="增量抓取 X.com 公开推文")
parser.add_argument("handle", help="@handle")
parser.add_argument("--days", type=int, default=3, help="往前几天（默认3）")
parser.add_argument("--months", type=int, default=None, help="往前几月（会覆盖--days）")
parser.add_argument("--force", action="store_true", help="强制抓取，忽略已有数据")
parser.add_argument("--insecure", action="store_true", help="禁用 SSL 证书验证（防火墙/中国网络环境）")
parser.add_argument("--freshness", choices=["realtime","recent","daily","any"], default="recent",
                    help="新鲜度要求: realtime(15min)/recent(6h默认)/daily(24h)/any(跳过不检查)")
parser.add_argument("--user-query-id")
parser.add_argument("--tweets-query-id")
args = parser.parse_args()

HANDLE = args.handle.lstrip("@")
if args.months is not None:
    args.days = args.months * 30
SINCE_DT = datetime.now(timezone.utc) - timedelta(days=args.days)
RANGE_LABEL = f"{args.months}个月" if args.months else f"{args.days}天"

# 数据目录（按天分文件）
DATA_DIR = os.path.join(DATA_BASE, HANDLE)

MSG_NO_TOKEN = f"""❌ 未找到 X 认证信息。
请在浏览器中获取 auth_token 和 ct0，配置保存在 {CONFIG_PATH}"""
MSG_TOKEN_EXPIRED = "❌ auth_token 已过期。请重新登录 X。"

# ---- 工具函数 ----
def parse_x_date(s):
    return datetime.strptime(s, '%a %b %d %H:%M:%S %z %Y')

def list_archive_files():
    """列出所有归档文件（日/月/年）"""
    files = []
    if os.path.exists(DATA_DIR):
        for fname in os.listdir(DATA_DIR):
            if fname.endswith('.jsonl'):
                files.append(fname)
    return sorted(files)

def load_existing():
    """扫描所有归档文件，返回 (id集合, 最新日期)"""
    ids = set()
    newest = None
    for fname in list_archive_files():
        with open(os.path.join(DATA_DIR, fname)) as f:
            for line in f:
                try:
                    t = json.loads(line)
                    ids.add(t["id"])
                    try:
                        dt = parse_x_date(t["created_at"])
                        if newest is None or dt > newest:
                            newest = dt
                    except ValueError:
                        pass
                except json.JSONDecodeError:
                    _stats["skipped_parse"] += 1
                    continue
    return ids, newest

def file_for_tweet(date_str):
    """推文日期 → 当前月按天文件"""
    dt = parse_x_date(date_str)
    return os.path.join(DATA_DIR, f"{dt.strftime('%Y-%m-%d')}.jsonl")

def save_new_tweets(tweets):
    """新推文写入当天日文件，天内去重"""
    os.makedirs(DATA_DIR, exist_ok=True)
    for t in tweets:
        df = file_for_tweet(t["created_at"])
        day_ids = set()
        if os.path.exists(df):
            with open(df) as f:
                for line in f:
                    try: day_ids.add(json.loads(line)["id"])
                    except: pass
        if t["id"] not in day_ids:
            with open(df, "a") as f:
                f.write(json.dumps(t, ensure_ascii=False) + "\n")

def archive():
    """归档旧数据: 上月日文件→月文件, 去年月文件→年文件"""
    now = datetime.now(timezone.utc)
    this_month = now.strftime('%Y-%m')
    this_year = now.strftime('%Y')

    merged = []
    for fname in list_archive_files():
        base = fname.replace('.jsonl', '')
        parts = base.split('-')

        if len(parts) == 3:  # 日文件 YYYY-MM-DD
            if base[:7] < this_month:  # 上月的日文件 → 合并为月文件
                merged.append(fname)
        elif len(parts) == 2:  # 月文件 YYYY-MM
            if parts[0] < this_year:  # 去年的月文件 → 合并为年文件
                merged.append(fname)

    if not merged:
        return

    # 按目标归档文件分组
    groups = {}
    for fname in merged:
        base = fname.replace('.jsonl', '')
        parts = base.split('-')
        if len(parts) == 3:  # 日→月
            target = f"{parts[0]}-{parts[1]}.jsonl"
        else:  # 月→年
            target = f"{parts[0]}.jsonl"
        groups.setdefault(target, []).append(fname)

    for target, sources in groups.items():
        target_path = os.path.join(DATA_DIR, target)
        seen = set()
        # 目标文件已有 ID
        if os.path.exists(target_path):
            with open(target_path) as f:
                for line in f:
                    try: seen.add(json.loads(line)["id"])
                    except: pass
        # 合并源文件
        with open(target_path, "a") as out:
            for src in sorted(sources):
                src_path = os.path.join(DATA_DIR, src)
                with open(src_path) as f:
                    for line in f:
                        try:
                            t = json.loads(line)
                            if t["id"] not in seen:
                                out.write(line)
                                seen.add(t["id"])
                        except: pass
                os.remove(src_path)  # 归档后删除源文件
        # 去重写入
        _dedup_file(target_path)

def _dedup_file(path):
    """文件内按 ID 去重"""
    seen = set()
    lines = []
    with open(path) as f:
        for line in f:
            try:
                tid = json.loads(line)["id"]
                if tid not in seen:
                    seen.add(tid)
                    lines.append(line)
            except: pass
    with open(path, "w") as f:
        f.writelines(lines)

# ---- 新鲜度策略 (Class B) ----
FRESHNESS_THRESHOLDS = {
    "realtime": 0.25,   # 15 分钟——交易/评估场景
    "recent":    6,      # 6 小时——一般查询（默认）
    "daily":    24,      # 24 小时——批量归档
    "any":      None,    # 不检查——有数据就跳过
}
existing_ids, newest_existing = load_existing()

# 每次执行都归档（合并旧日文件→月文件，旧月文件→年文件）
archive()

if not args.force:
    threshold_hours = FRESHNESS_THRESHOLDS.get(args.freshness)
    if threshold_hours is not None and newest_existing:
        age_hours = (datetime.now(timezone.utc) - newest_existing).total_seconds() / 3600
        if age_hours < threshold_hours:
            freshness_labels = {"realtime": "≤15分钟", "recent": "≤6小时", "daily": "≤24小时"}
            label = freshness_labels.get(args.freshness, f"≤{threshold_hours:.0f}h")
            print(f"✅ 已有数据足够新（{age_hours:.0f}小时前 < {label}阈值），无需重复抓取。")
            print(f"   目录: {DATA_DIR}")
            print(f"   已有: {len(existing_ids)} 条（按日分文件）")
            print(f"   💡 需要强制刷新？加 --force 或 --freshness realtime")
            sys.exit(0)
    elif threshold_hours is None:  # "any" 模式
        if newest_existing:
            age_hours = (datetime.now(timezone.utc) - newest_existing).total_seconds() / 3600
            print(f"✅ freshness=any: 已有数据（{age_hours:.0f}小时前），跳过抓取。")
            print(f"   目录: {DATA_DIR}")
            print(f"   已有: {len(existing_ids)} 条（按日分文件）")
            sys.exit(0)

# 有旧数据 → 只抓增量（从最新推文日期起）
if newest_existing:
    SINCE_DT = min(SINCE_DT, newest_existing - timedelta(hours=1))
    print(f"📌 增量模式: 已有 {len(existing_ids)} 条，最新 {newest_existing.strftime('%Y-%m-%d %H:%M')}")

# ---- 读取配置 ----
def load_config():
    if not os.path.exists(CONFIG_PATH):
        print(MSG_NO_TOKEN)
        sys.exit(1)
    with open(CONFIG_PATH) as f:
        return json.load(f)

cfg = load_config()
AUTH_TOKEN = cfg.get("auth_token", "")
CT0 = cfg.get("ct0", "")
if not AUTH_TOKEN or not CT0:
    print(MSG_NO_TOKEN)
    sys.exit(1)

# ---- 网络层 (Class A: 集中化 session + 异常处理) ----
def create_session():
    """创建配置好的 requests Session（SSL/代理/UA 集中管理）"""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    })
    if args.insecure:
        session.verify = False
        urllib3.disable_warnings()
    # 代理支持（环境变量 HTTP_PROXY / HTTPS_PROXY 由 requests 自动读取）
    return session

def safe_request(method, url, **kwargs):
    """
    带重试+异常分类的统一网络请求（替代原 api_get）。
    返回 requests.Response，网络错误抛出 NetworkError/AuthError。
    """
    timeout = kwargs.pop("timeout", 30)
    max_retries = kwargs.pop("max_retries", 3)
    last_error = None

    for attempt in range(max_retries):
        try:
            resp = session.request(method, url, timeout=timeout, **kwargs)
            if resp.status_code == 429:
                wait = min(30 * (attempt + 1), 90)
                print(f"   ⏳ 限流 {wait}s...")
                time.sleep(wait)
                _stats["retries"] += 1
                continue
            return resp
        except (AuthError, ScraperError):
            raise  # 不重试致命错误
        except requests.exceptions.SSLError as e:
            last_error = e
            if args.insecure:
                _stats["retries"] += 1
                continue  # 已 insecure 再重试一次
            else:
                raise NetworkError("SSL 验证失败（防火墙阻断？）", original=e)
        except requests.exceptions.ConnectionError as e:
            last_error = e
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                print(f"   🔄 连接失败，{wait}s 后重试 ({attempt+1}/{max_retries})...")
                time.sleep(wait)
                _stats["retries"] += 1
                continue
            raise NetworkError("无法连接到 X.com", original=e)
        except requests.exceptions.Timeout as e:
            last_error = e
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                print(f"   🔄 超时，{wait}s 后重试 ({attempt+1}/{max_retries})...")
                time.sleep(wait)
                _stats["retries"] += 1
                continue
            raise NetworkError("请求超时", original=e)
        except requests.exceptions.RequestException as e:
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(2)
                _stats["retries"] += 1
                continue
            raise NetworkError(str(e), original=e)

    raise NetworkError(f"重试 {max_retries} 次后仍失败", original=last_error)

session = create_session()

# ---- guest token ----
print("🔑 guest token...")
gt = safe_request("POST", "https://api.x.com/1.1/guest/activate.json",
                  headers={"Authorization": f"Bearer {BEARER}"}, timeout=20)
if gt.status_code != 200:
    print(f"❌ guest token 失败 (HTTP {gt.status_code})")
    sys.exit(2)

guest_token = gt.json().get("guest_token", "")
session.cookies.set("guest_token", guest_token, domain=".x.com")
session.cookies.set("auth_token", AUTH_TOKEN, domain=".x.com")
session.cookies.set("ct0", CT0, domain=".x.com")
session.headers.update({
    "x-guest-token": guest_token,
    "x-csrf-token": CT0,
    "Authorization": f"Bearer {BEARER}",
})

# ---- 自动发现 query ID ----
def discover_query_ids():
    qm = {}
    try:
        resp = safe_request("GET", "https://x.com/", timeout=30, headers={"Accept": "text/html"})
        if resp.status_code != 200:
            return qm
    except (NetworkError, AuthError):
        print("   ⚠️ x.com 首页不可达，跳过自动发现，使用 fallback")
        _stats["degraded"] = True
        _stats["degraded_reason"] = "x.com 首页不可达"
        return qm
    html = resp.text

    for s in re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL):
        for m in re.finditer(r'queryId:"([^"]+)",operationName:"([^"]+)"', s):
            qm[m.group(2)] = m.group(1)
        for m in re.finditer(r'operationName:"([^"]+)",queryId:"([^"]+)"', s):
            qm[m.group(1)] = m.group(2)
        for m in re.finditer(r'"(\w+)":\s*\{[^}]*queryId:\s*"([^"]+)"', s):
            if m.group(1) not in qm:
                qm[m.group(1)] = m.group(2)

    js_urls = set()
    for m in re.finditer(r'/_next/static/chunks/[^"]+\.js', html):
        js_urls.add(m.group(0))
    for m in re.finditer(r'src="(https://abs\.twimg\.com/[^"]+\.js[^"]*)"', html):
        js_urls.add(m.group(1))

    for js_url in list(js_urls)[:8]:
        full = f"https://x.com{js_url}" if js_url.startswith("/") else js_url
        try:
            js_resp = safe_request("GET", full, timeout=30, headers={"Accept": "*/*", "Referer": "https://x.com/"})
            if js_resp.status_code != 200: continue
            js = js_resp.text
            for m in re.finditer(r'\{queryId:"([^"]+)",operationName:"([^"]+)"', js):
                qm[m.group(2)] = m.group(1)
            for m in re.finditer(r'operationName:"([^"]+)",queryId:"([^"]+)"', js):
                qm[m.group(1)] = m.group(2)
        except (NetworkError, Exception):
            pass
    return qm

# ---- Query ID 本地缓存 (Class A: 第三层保护) ----
def load_query_cache():
    cache_path = os.path.join(DATA_BASE, ".query_cache.json")
    if os.path.exists(cache_path):
        try:
            with open(cache_path) as f:
                return json.load(f)
        except: pass
    return {}

def save_query_cache(user_qid, tweets_qid):
    cache_path = os.path.join(DATA_BASE, ".query_cache.json")
    try:
        os.makedirs(DATA_BASE, exist_ok=True)
        with open(cache_path, "w") as f:
            json.dump({"UserByScreenName": user_qid, "UserTweets": tweets_qid, "updated": datetime.now(timezone.utc).isoformat()}, f)
    except: pass

FALLBACK_USER = [
    "2qvSHpkWTMS9i0zJAwDNiA","32pL5BWe_3mEHPq_2bMeiA","G3KGOASz96HQu8jAk6qP2w",
    "B9xW2SH5gcX5R8Dq4K8a7Q","k7nNZE7LiuyGimNj2R7ZPA","qWb2gmqRSj5gQcStp0V1uQ",
    "1CLoG7dqY7dPJvL3YcV0Gw","ZzCRx1bFFjqRRU_VNcDjzg","lpG3Q4lTf6pmTXtzDVAi2Q",
    "yIo1h5N-I2o-vNMXoMhx3A","6ZDCjABfIuXsAqJIQ8gHlQ","Gd3w-NsHbgTngiEcOKTR7Q",
]
FALLBACK_TWEETS = [
    "hr4gzZONlq23okjU8fIe_A","nrd2A_7XhJZY6XgK7f8Chg","EoMjnH-Nn1yBulIpSJhMYA",
    "V7H0j_H0q3nWwHEFVJmJzQ","8ISBPy1DQ0FZ9TvhYqRfaw","5Lu2Dng3M4CwZ2tqkF8VYw",
    "1AcDLhJgE5YKqBUIvXhK2Q","bD40GweSqNRMtqD9B_M9SQ","C8XGpRqP4LtJmNkWsc0UOw",
    "69hU7DprHxXIjRgFYCbRAg","xT8_QeRMYhGxR8uD4Ka7PA","Y0JDg6r8H_kIx2RtAQHmYg",
]

def fallback_test(endpoint, qids, variables):
    # UserTweets now requires the full feature set + withVoice; minimal features get 422 "must be defined"
    if "ScreenName" in endpoint:
        test_features = json.dumps({"hidden_profile_subgroups_enabled": True})
        test_toggles = json.dumps({"withAuxiliaryUserLabels": False})
    else:
        # X API now mandates withVoice + withQuickPromoteEligibilityTweetFields
        variables = {**variables, "withVoice": True, "withQuickPromoteEligibilityTweetFields": True}
        test_features = json.dumps({
            "rweb_video_screen_enabled": False, "rweb_cashtags_enabled": True,
            "profile_label_improvements_pcf_label_in_post_enabled": True,
            "responsive_web_profile_redirect_enabled": False, "rweb_tipjar_consumption_enabled": False,
            "verified_phone_label_enabled": False, "creator_subscriptions_tweet_preview_api_enabled": True,
            "responsive_web_graphql_timeline_navigation_enabled": True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "premium_content_api_read_enabled": False,
            "communities_web_enable_tweet_community_results_fetch": True,
            "c9s_tweet_anatomy_moderator_badge_enabled": True,
            "responsive_web_grok_analyze_button_fetch_trends_enabled": False,
            "responsive_web_grok_analyze_post_followups_enabled": True,
            "rweb_cashtags_composer_attachment_enabled": True,
            "responsive_web_jetfuel_frame": True,
            "responsive_web_grok_share_attachment_enabled": True,
            "responsive_web_grok_annotations_enabled": True,
            "articles_preview_enabled": True, "responsive_web_edit_tweet_api_enabled": True,
            "rweb_conversational_replies_downvote_enabled": False,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
            "view_counts_everywhere_api_enabled": True,
            "longform_notetweets_consumption_enabled": True,
            "responsive_web_twitter_article_tweet_consumption_enabled": True,
            "content_disclosure_indicator_enabled": True,
            "content_disclosure_ai_generated_indicator_enabled": True,
            "responsive_web_grok_show_grok_translated_post": True,
            "responsive_web_grok_analysis_button_from_backend": True,
            "post_ctas_fetch_enabled": False, "freedom_of_speech_not_reach_fetch_enabled": True,
            "standardized_nudges_misinfo": True,
            "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
            "longform_notetweets_rich_text_read_enabled": True,
            "longform_notetweets_inline_media_enabled": False,
            "responsive_web_grok_image_annotation_enabled": True,
            "responsive_web_grok_imagine_annotation_enabled": True,
            "responsive_web_grok_community_note_auto_translation_is_enabled": True,
            "responsive_web_enhance_cards_enabled": False,
        })
        test_toggles = json.dumps({"withArticlePlainText": False})
    for qid in qids:
        resp = safe_request("GET",
            f"https://x.com/i/api/graphql/{qid}/{endpoint}",
            params={
                "variables": json.dumps(variables),
                "features": test_features,
                "fieldToggles": test_toggles,
            },
        )
        if resp.status_code == 200 and "errors" not in resp.json():
            return qid
    return None

# ---- 确定 query ID ----
USER_QID = args.user_query_id
TWEETS_QID = args.tweets_query_id

# 先尝试从本地缓存加载（Class A: 第三层保护）
query_cache = load_query_cache()
if not USER_QID and "UserByScreenName" in query_cache:
    USER_QID = query_cache["UserByScreenName"]
    print(f"   📦 从缓存加载 UserByScreenName: {USER_QID}")
if not TWEETS_QID and "UserTweets" in query_cache:
    TWEETS_QID = query_cache["UserTweets"]
    print(f"   📦 从缓存加载 UserTweets: {TWEETS_QID}")

if not USER_QID or not TWEETS_QID:
    print("🔍 自动发现 query ID...")
    qmap = discover_query_ids()
    print(f"   首页+JS: {len(qmap)} 个")
    if not USER_QID:
        for n in ["UserByScreenName"]:
            if n in qmap: USER_QID = qmap[n]; print(f"   ✅ UserByScreenName: {USER_QID}")
    if not TWEETS_QID:
        for n in ["UserTweets"]:
            if n in qmap: TWEETS_QID = qmap[n]; print(f"   ✅ UserTweets: {TWEETS_QID}")

if not USER_QID:
    print("   🔄 fallback UserByScreenName...")
    USER_QID = fallback_test("UserByScreenName", FALLBACK_USER, {"screen_name": HANDLE})
    if USER_QID: print(f"   ✅ {USER_QID}")
if not USER_QID:
    print("❌ UserByScreenName 全部失败。"); sys.exit(1)

# ---- 获取用户 ID ----
print(f"\n🔍 @{HANDLE}...")
UR = safe_request("GET",
    f"https://x.com/i/api/graphql/{USER_QID}/UserByScreenName",
    params={
        "variables": json.dumps({"screen_name": HANDLE, "withGrokTranslatedBio": True}),
        "features": json.dumps({
            "hidden_profile_subscriptions_enabled": True,
            "profile_label_improvements_pcf_label_in_post_enabled": True,
            "verified_phone_label_enabled": False,
            "highlights_tweets_tab_ui_enabled": True,
            "creator_subscriptions_tweet_preview_api_enabled": True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "responsive_web_graphql_timeline_navigation_enabled": True,
        }),
        "fieldToggles": json.dumps({"withPayments": False, "withAuxiliaryUserLabels": True}),
    },
)
if UR.status_code == 401:
    raise AuthError("auth_token 已过期或无效")
ud = UR.json()
if "errors" in ud:
    print(f"❌ API 错误: {ud['errors']}")
    sys.exit(2)

ur = ud["data"]["user"]["result"]
user_id = ur["rest_id"]
leg = ur.get("legacy", {})
print(f"   ✅ {leg.get('name')} | ID={user_id} | 👥{leg.get('followers_count',0):,}")

# ---- 补全 TWEETS_QID ----
if not TWEETS_QID:
    print("   🔄 fallback UserTweets...")
    TWEETS_QID = fallback_test("UserTweets", FALLBACK_TWEETS, {"userId": user_id, "count": 1, "includePromotedContent": True})
    if TWEETS_QID: print(f"   ✅ {TWEETS_QID}")
if not TWEETS_QID:
    print("❌ UserTweets 全部失败。"); sys.exit(2)

# 保存成功的 query ID 到本地缓存 (Class A)
if USER_QID and TWEETS_QID:
    save_query_cache(USER_QID, TWEETS_QID)

# ---- 抓取 ----
print(f"\n📥 抓取（{RANGE_LABEL}，从 {SINCE_DT.strftime('%Y-%m-%d')} 起）...")

FEATURES = json.dumps({
    "rweb_video_screen_enabled": False, "rweb_cashtags_enabled": True,
    "profile_label_improvements_pcf_label_in_post_enabled": True,
    "responsive_web_profile_redirect_enabled": False, "rweb_tipjar_consumption_enabled": False,
    "verified_phone_label_enabled": False, "creator_subscriptions_tweet_preview_api_enabled": True,
    "responsive_web_graphql_timeline_navigation_enabled": True,
    "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
    "premium_content_api_read_enabled": False,
    "communities_web_enable_tweet_community_results_fetch": True,
    "c9s_tweet_anatomy_moderator_badge_enabled": True,
    "responsive_web_grok_analyze_button_fetch_trends_enabled": False,
    "responsive_web_grok_analyze_post_followups_enabled": True,
    "rweb_cashtags_composer_attachment_enabled": True,
    "responsive_web_jetfuel_frame": True,
    "responsive_web_grok_share_attachment_enabled": True,
    "responsive_web_grok_annotations_enabled": True,
    "articles_preview_enabled": True, "responsive_web_edit_tweet_api_enabled": True,
    "rweb_conversational_replies_downvote_enabled": False,
    "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
    "view_counts_everywhere_api_enabled": True,
    "longform_notetweets_consumption_enabled": True,
    "responsive_web_twitter_article_tweet_consumption_enabled": True,
    "content_disclosure_indicator_enabled": True,
    "content_disclosure_ai_generated_indicator_enabled": True,
    "responsive_web_grok_show_grok_translated_post": True,
    "responsive_web_grok_analysis_button_from_backend": True,
    "post_ctas_fetch_enabled": False, "freedom_of_speech_not_reach_fetch_enabled": True,
    "standardized_nudges_misinfo": True,
    "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
    "longform_notetweets_rich_text_read_enabled": True,
    "longform_notetweets_inline_media_enabled": False,
    "responsive_web_grok_image_annotation_enabled": True,
    "responsive_web_grok_imagine_annotation_enabled": True,
    "responsive_web_grok_community_note_auto_translation_is_enabled": True,
    "responsive_web_enhance_cards_enabled": False,
})

new_tweets = []
cursor = None
page = 0
consecutive_oob = 0

while page < 500:
    v = {"userId": user_id, "count": 100, "includePromotedContent": True,
         "withQuickPromoteEligibilityTweetFields": True, "withVoice": True}
    if cursor: v["cursor"] = cursor

    try:
        resp = safe_request("GET",
            f"https://x.com/i/api/graphql/{TWEETS_QID}/UserTweets",
            params={"variables": json.dumps(v), "features": FEATURES,
                    "fieldToggles": json.dumps({"withArticlePlainText": False})},
        )
    except NetworkError as e:
        print(f"⚠️ 网络错误: {e}")
        _stats["degraded"] = True
        _stats["degraded_reason"] = str(e)
        break
    if resp.status_code == 401: raise AuthError("auth_token 已过期或无效")
    if resp.status_code == 429: print("❌ 限流过度"); break
    if resp.status_code != 200: print(f"❌ HTTP {resp.status_code}"); break

    data = resp.json()
    if "errors" in data: print(f"⚠️ {data['errors']}"); break

    tl = (data.get("data",{}).get("user",{}).get("result",{})
          .get("timeline",{}).get("timeline",{}))
    entries = []
    for ins in tl.get("instructions",[]):
        if ins.get("type") == "TimelineAddEntries":
            entries = ins.get("entries",[]); break

    n_new, n_dup, n_oob = 0, 0, 0
    cursor = None
    for e in entries:
        eid = e.get("entryId",""); ct = e.get("content",{})
        if ct.get("cursorType") == "Bottom": cursor = ct.get("value"); continue
        if not (eid.startswith("tweet-") or eid.startswith("profile-conversation-")): continue

        tr = ct.get("itemContent",{}).get("tweet_results",{}).get("result",{})
        if not tr:
            items = ct.get("items",[])
            if items: tr = items[0].get("item",{}).get("itemContent",{}).get("tweet_results",{}).get("result",{})
        if tr.get("__typename") == "TweetWithVisibilityResults": tr = tr.get("tweet",{})
        lg = tr.get("legacy",{})
        if not lg: continue

        tid = tr.get("rest_id") or lg.get("id_str","")
        ca = lg.get("created_at","")
        try: ca_dt = parse_x_date(ca)
        except ValueError: continue

        if ca_dt < SINCE_DT: n_oob += 1; continue
        if tid in existing_ids: n_dup += 1; continue

        new_tweets.append({
            "id": tid, "created_at": ca, "text": lg.get("full_text",""),
            "likes": lg.get("favorite_count",0), "retweets": lg.get("retweet_count",0),
            "replies": lg.get("reply_count",0), "quotes": lg.get("quote_count",0),
            "views": tr.get("views",{}).get("count",0), "lang": lg.get("lang",""),
            "urls": [u.get("expanded_url","") for u in lg.get("entities",{}).get("urls",[])],
        })
        n_new += 1
        existing_ids.add(tid)

    page += 1
    print(f"   📄 p{page} | +{n_new} 🆕 | ~{n_dup}已有 | 《{n_oob}越界 | ∑{len(new_tweets)}", flush=True)

    if n_oob > 0 and n_new == 0:
        consecutive_oob += 1
    else:
        consecutive_oob = 0
    if consecutive_oob >= 2:
        print("   ✅ 已到日期边界"); break
    time.sleep(0.8 if n_new > 0 else 1.2)

# ---- 保存 ----
if new_tweets:
    save_new_tweets(new_tweets)
    archive()

# ---- 统计报告 (Class F: 不再静默) ----
total_final = len(existing_ids) + len(new_tweets)
print(f"\n{'='*50}")
if new_tweets:
    print(f"✅ 新增 {len(new_tweets)} 条")
else:
    print(f"📭 无新推文")
print(f"   📊 {RANGE_LABEL}内: {len(new_tweets)} 条 | 总计: {total_final} 条")
if _stats["skipped_parse"] > 0:
    print(f"   ⚠️ 跳过 {_stats['skipped_parse']} 条 JSON 解析错误")
if _stats["retries"] > 0:
    print(f"   🔄 重试 {_stats['retries']} 次")
if _stats["degraded"]:
    print(f"   ⚠️ 降级运行: {_stats['degraded_reason']}")
print(f"   📂 {DATA_DIR}/  (按日分文件)")
# 退出码: 降级运行 → 2, 正常 → 0
sys.exit(2 if _stats["degraded"] else 0)
