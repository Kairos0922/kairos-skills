#!/usr/bin/env python3
"""
kairos-x-scraper — 抓取 X.com 公开推文
用法: python3 fetch_tweets.py <handle> <月数> <输出目录> [--user-query-id ID] [--tweets-query-id ID]
"""

import json, time, sys, re, os, argparse
from datetime import datetime, timedelta, timezone

try:
    import requests
except ImportError:
    print("❌ 缺少 requests 库。运行: pip3 install requests")
    sys.exit(1)

# ---- 公开常量 ----
BEARER = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"

# ---- 命令行参数 ----
parser = argparse.ArgumentParser(description="抓取 X.com 公开推文")
parser.add_argument("handle", help="目标账号 @handle（不用加 @）")
parser.add_argument("months", type=int, nargs="?", default=1, help="往前翻的月数（默认1）")
parser.add_argument("output_dir", nargs="?", default=".", help="JSONL 输出目录（默认当前目录）")
parser.add_argument("--user-query-id", help="手动指定 UserByScreenName GraphQL ID")
parser.add_argument("--tweets-query-id", help="手动指定 UserTweets GraphQL ID")
args = parser.parse_args()

HANDLE = args.handle.lstrip("@")
MONTHS = args.months
OUTPUT_DIR = os.path.abspath(args.output_dir)
SINCE = (datetime.now(timezone.utc) - timedelta(days=MONTHS * 30)).strftime("%Y-%m-%d")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, f"{HANDLE}_tweets.jsonl")
CONFIG_PATH = os.path.expanduser("~/.kairos/kairos-x-scraper-config.json")

# ---- 错误文案（中文） ----
MSG_NO_TOKEN = f"""❌ 未找到 X 认证信息。

请在浏览器中:
1. 打开 https://x.com 并登录
2. F12 → Application → Cookies → https://x.com
3. 找到 auth_token 和 ct0，复制它们的 Value
4. 粘贴给我（格式: auth_token: xxx; ct0: yyy）

这些信息将保存在 {CONFIG_PATH}，下次无需重复提供。"""

MSG_TOKEN_EXPIRED = """❌ auth_token 已过期。

请重新获取:
1. 打开 https://x.com，退出登录后重新登录
2. F12 → Application → Cookies → https://x.com
3. 复制新的 auth_token 和 ct0
4. 粘贴给我"""

MSG_QUERY_EXPIRED = """❌ X 的内部 API 已更新（GraphQL query ID 过期）。

请手动获取新的 query ID:
1. 打开 https://x.com/{handle}
2. F12 → Network → 清空 → 刷新页面
3. 搜索框输入: UserByScreenName
4. 点击该请求 → 复制 URL 中 /graphql/ 后面的那串 ID
5. 同样搜索 UserTweets，再复制一个 ID
6. 把两个 ID 告诉我"""

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

# ---- 建立 session ----
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
})

def api_get(url, params=None):
    for attempt in range(3):
        resp = session.get(url, params=params, timeout=30)
        if resp.status_code == 429:
            wait = 60 * (attempt + 1)
            print(f"   ⏳ 限流，等待 {wait} 秒...")
            time.sleep(wait)
            continue
        return resp
    return resp

# ---- 获取 guest token ----
print("🔑 获取 guest token...")
gt = session.post(
    "https://api.x.com/1.1/guest/activate.json",
    headers={"Authorization": f"Bearer {BEARER}"},
    timeout=20,
)
if gt.status_code != 200:
    print(f"❌ 无法获取 guest token (HTTP {gt.status_code})")
    print(MSG_TOKEN_EXPIRED)
    sys.exit(1)

guest_token = gt.json().get("guest_token", "")
print(f"   ✅ {guest_token[:25]}...")

session.cookies.set("guest_token", guest_token, domain=".x.com")
session.cookies.set("auth_token", AUTH_TOKEN, domain=".x.com")
session.cookies.set("ct0", CT0, domain=".x.com")
session.headers.update({
    "x-guest-token": guest_token,
    "x-csrf-token": CT0,
    "Authorization": f"Bearer {BEARER}",
})

# ---- 发现/确认 query ID ----
def discover_query_ids():
    """尝试从首页 JS 中自动提取 query ID"""
    query_map = {}

    # 策略A: 从首页 HTML 提取
    resp = session.get("https://x.com/", timeout=30, headers={"Accept": "text/html"})
    if resp.status_code == 200:
        html = resp.text
        # 内联 script
        for s in re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL):
            for m in re.finditer(r'queryId:\s*"([^"]+)"\s*,\s*operationName:\s*"([^"]+)"', s):
                query_map[m.group(2)] = m.group(1)
            for m in re.finditer(r'operationName:\s*"([^"]+)"\s*,\s*queryId:\s*"([^"]+)"', s):
                query_map[m.group(1)] = m.group(2)

        # 策略B: 从 JS bundle 提取
        js_urls = set()
        for m in re.finditer(r'/_next/static/chunks/[^"]+\.js', html):
            js_urls.add(m.group(0))
        for m in re.finditer(r'src="(https://abs\.twimg\.com/[^"]+\.js[^"]*)"', html):
            js_urls.add(m.group(1))

        for js_url in list(js_urls)[:5]:
            full = f"https://x.com{js_url}" if js_url.startswith("/") else js_url
            try:
                js = session.get(full, timeout=30, headers={"Accept": "*/*"}).text
                for m in re.finditer(r'\{queryId:"([^"]+)",operationName:"([^"]+)"', js):
                    query_map[m.group(2)] = m.group(1)
                for m in re.finditer(r'operationName:"([^"]+)",queryId:"([^"]+)"', js):
                    query_map[m.group(1)] = m.group(2)
            except:
                pass

    return query_map

# 确定 UserByScreenName ID
USER_QID = args.user_query_id
TWEETS_QID = args.tweets_query_id

if not USER_QID or not TWEETS_QID:
    print("🔍 自动发现 GraphQL query ID...")
    qmap = discover_query_ids()
    print(f"   发现 {len(qmap)} 个 query")

    if not USER_QID:
        for name in ["UserByScreenName"]:
            if name in qmap:
                USER_QID = qmap[name]
                print(f"   ✅ UserByScreenName: {USER_QID}")
                break

    if not TWEETS_QID:
        for name in ["UserTweets"]:
            if name in qmap:
                TWEETS_QID = qmap[name]
                print(f"   ✅ UserTweets: {TWEETS_QID}")
                break

# 自动发现失败 → fallback
FALLBACK_USER_IDS = [
    "2qvSHpkWTMS9i0zJAwDNiA", "32pL5BWe_3mEHPq_2bMeiA",
    "G3KGOASz96HQu8jAk6qP2w", "B9xW2SH5gcX5R8Dq4K8a7Q",
]
FALLBACK_TWEETS_IDS = [
    "hr4gzZONlq23okjU8fIe_A", "nrd2A_7XhJZY6XgK7f8Chg",
    "EoMjnH-Nn1yBulIpSJhMYA", "V7H0j_H0q3nWwHEFVJmJzQ",
]

if not USER_QID:
    print("   🔄 尝试 fallback UserByScreenName ID...")
    for qid in FALLBACK_USER_IDS:
        test = api_get(
            f"https://x.com/i/api/graphql/{qid}/UserByScreenName",
            params={
                "variables": json.dumps({"screen_name": HANDLE}),
                "features": json.dumps({"hidden_profile_subgroups_enabled": True}),
                "fieldToggles": json.dumps({"withAuxiliaryUserLabels": False}),
            },
        )
        if test.status_code == 200 and "errors" not in test.json():
            USER_QID = qid
            print(f"   ✅ 命中: {qid}")
            break

if not TWEETS_QID:
    print("   🔄 尝试 fallback UserTweets ID...")
    # 先得有 user_id 才能测试
    pass  # 等拿到 user_id 后再试

if not USER_QID:
    print(MSG_QUERY_EXPIRED.replace("{handle}", HANDLE))
    sys.exit(1)

# ---- 获取用户信息 ----
print(f"\n🔍 查找 @{HANDLE}...")
UR = api_get(
    f"https://x.com/i/api/graphql/{USER_QID}/UserByScreenName",
    params={
        "variables": json.dumps({"screen_name": HANDLE, "withGrokTranslatedBio": True}),
        "features": json.dumps({
            "hidden_profile_subscriptions_enabled": True,
            "profile_label_improvements_pcf_label_in_post_enabled": True,
            "responsive_web_profile_redirect_enabled": False,
            "rweb_tipjar_consumption_enabled": False,
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
    print(MSG_TOKEN_EXPIRED)
    sys.exit(1)

ud = UR.json()
if "errors" in ud:
    print(f"❌ API 错误: {ud['errors']}")
    sys.exit(1)

ur = ud["data"]["user"]["result"]
user_id = ur["rest_id"]
leg = ur.get("legacy", {})
print(f"   ✅ {leg.get('name')} | ID={user_id}")
print(f"   👥 {leg.get('followers_count', 0):,} 粉丝 | 📊 {leg.get('statuses_count', 0):,} 推文")

# ---- 补全 TWEETS_QID ----
if not TWEETS_QID:
    print("   🔄 fallback UserTweets ID...")
    for qid in FALLBACK_TWEETS_IDS:
        test = api_get(
            f"https://x.com/i/api/graphql/{qid}/UserTweets",
            params={
                "variables": json.dumps({"userId": user_id, "count": 1, "includePromotedContent": True}),
                "features": json.dumps({"responsive_web_graphql_exclude_directive_enabled": True}),
            },
        )
        if test.status_code == 200 and "errors" not in test.json():
            TWEETS_QID = qid
            print(f"   ✅ 命中: {qid}")
            break

if not TWEETS_QID:
    print(MSG_QUERY_EXPIRED.replace("{handle}", HANDLE))
    sys.exit(1)

# ---- 抓取 ----
print(f"\n📥 抓取 @{HANDLE} 的推文（往前 {MONTHS} 个月，从 {SINCE} 起）...")

FEATURES = json.dumps({
    "rweb_video_screen_enabled": False,
    "rweb_cashtags_enabled": True,
    "profile_label_improvements_pcf_label_in_post_enabled": True,
    "responsive_web_profile_redirect_enabled": False,
    "rweb_tipjar_consumption_enabled": False,
    "verified_phone_label_enabled": False,
    "creator_subscriptions_tweet_preview_api_enabled": True,
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
    "articles_preview_enabled": True,
    "responsive_web_edit_tweet_api_enabled": True,
    "rweb_conversational_replies_downvote_enabled": False,
    "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
    "view_counts_everywhere_api_enabled": True,
    "longform_notetweets_consumption_enabled": True,
    "responsive_web_twitter_article_tweet_consumption_enabled": True,
    "content_disclosure_indicator_enabled": True,
    "content_disclosure_ai_generated_indicator_enabled": True,
    "responsive_web_grok_show_grok_translated_post": True,
    "responsive_web_grok_analysis_button_from_backend": True,
    "post_ctas_fetch_enabled": False,
    "freedom_of_speech_not_reach_fetch_enabled": True,
    "standardized_nudges_misinfo": True,
    "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
    "longform_notetweets_rich_text_read_enabled": True,
    "longform_notetweets_inline_media_enabled": False,
    "responsive_web_grok_image_annotation_enabled": True,
    "responsive_web_grok_imagine_annotation_enabled": True,
    "responsive_web_grok_community_note_auto_translation_is_enabled": True,
    "responsive_web_enhance_cards_enabled": False,
})

all_tweets = []
cursor = None
page = 0
reached_boundary = False

while page < 500:
    v = {
        "userId": user_id, "count": 100,
        "includePromotedContent": True,
        "withQuickPromoteEligibilityTweetFields": True,
        "withVoice": True,
    }
    if cursor:
        v["cursor"] = cursor

    resp = api_get(
        f"https://x.com/i/api/graphql/{TWEETS_QID}/UserTweets",
        params={
            "variables": json.dumps(v),
            "features": FEATURES,
            "fieldToggles": json.dumps({"withArticlePlainText": False}),
        },
    )

    if resp.status_code == 401:
        print(MSG_TOKEN_EXPIRED)
        sys.exit(1)
    if resp.status_code != 200:
        print(f"❌ HTTP {resp.status_code}: {resp.text[:300]}")
        break

    data = resp.json()
    if "errors" in data:
        print(f"⚠️ {data['errors']}")
        break

    tl = (data.get("data", {}).get("user", {}).get("result", {})
          .get("timeline", {}).get("timeline", {}))
    entries = []
    for ins in tl.get("instructions", []):
        if ins.get("type") == "TimelineAddEntries":
            entries = ins.get("entries", [])
            break

    new = 0
    cursor = None
    for e in entries:
        eid = e.get("entryId", "")
        ct = e.get("content", {})
        if ct.get("cursorType") == "Bottom":
            cursor = ct.get("value")
            continue
        if not (eid.startswith("tweet-") or eid.startswith("profile-conversation-")):
            continue

        tr = ct.get("itemContent", {}).get("tweet_results", {}).get("result", {})
        if not tr:
            items = ct.get("items", [])
            if items:
                tr = items[0].get("item", {}).get("itemContent", {}).get("tweet_results", {}).get("result", {})
        if tr.get("__typename") == "TweetWithVisibilityResults":
            tr = tr.get("tweet", {})
        lg = tr.get("legacy", {})
        if not lg:
            continue

        ca = lg.get("created_at", "")
        if ca < SINCE:
            reached_boundary = True
            continue

        all_tweets.append({
            "id": tr.get("rest_id") or lg.get("id_str", ""),
            "created_at": ca,
            "text": lg.get("full_text", ""),
            "likes": lg.get("favorite_count", 0),
            "retweets": lg.get("retweet_count", 0),
            "replies": lg.get("reply_count", 0),
            "quotes": lg.get("quote_count", 0),
            "views": tr.get("views", {}).get("count", 0),
            "lang": lg.get("lang", ""),
            "urls": [u.get("expanded_url", "") for u in lg.get("entities", {}).get("urls", [])],
        })
        new += 1

    page += 1
    earliest = min((t["created_at"] for t in all_tweets), default=SINCE)
    print(f"   📄 第{page}页 | +{new}条 | 累计{len(all_tweets)}条 | 最早 {earliest[:10]}", flush=True)

    if reached_boundary or (new == 0 and cursor is None):
        break
    time.sleep(1.5)

# ---- 保存 ----
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for t in all_tweets:
        f.write(json.dumps(t, ensure_ascii=False) + "\n")

# ---- 统计 ----
print(f"\n{'='*50}")
print(f"✅ 抓取完成")
print(f"   账号: @{HANDLE}")
print(f"   推文: {len(all_tweets)} 条")
print(f"   文件: {OUTPUT_FILE}")
print(f"   大小: {os.path.getsize(OUTPUT_FILE) / 1024:.1f} KB")

if all_tweets:
    print(f"   日期: {all_tweets[-1]['created_at'][:10]} → {all_tweets[0]['created_at'][:10]}")

    # 股票代码统计
    tickers = {}
    for t in all_tweets:
        for m in re.findall(r'\$([A-Z]{1,5})', t["text"]):
            # 过滤假阳性
            if m in ("I", "A", "THE", "AND", "FOR", "NOT", "ALL", "NEW", "ONE",
                     "AI", "AT", "IN", "ON", "IT", "OR", "TO", "NO"):
                continue
            tickers[m] = tickers.get(m, 0) + 1

    if tickers:
        print(f"   💹 股票代码: {len(tickers)} 个")
        print(f"   TOP 20:")
        for i, (tk, n) in enumerate(sorted(tickers.items(), key=lambda x: x[1], reverse=True)[:20], 1):
            print(f"      {i:2}. ${tk:5s} {n}次")
    else:
        print(f"   💹 未检测到股票代码提及")
