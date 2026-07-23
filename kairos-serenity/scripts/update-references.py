#!/usr/bin/env python3
"""
kairos-serenity 参考数据半自动更新管道 (Class E)
从 Serenity 推文 JSONL 中提取新信号，生成 reference 草稿更新。

用法:
  python3 update-references.py --since 2026-07-01                    # 从指定日期起
  python3 update-references.py --days 7                               # 最近N天
  python3 update-references.py --ticker SIVE                          # 只看特定标的
  python3 update-references.py --dry-run                              # 预览，不写入

输出:
  references/_auto/ticker-updates.md     # ticker-theses.md 风格的新条目
  references/_auto/track-record-new.md   # 新 track-record 条目
  references/_auto/methodology-notes.md  # 新方法论笔记
"""

import json, sys, os, re, argparse
from datetime import datetime, timedelta, timezone
from collections import Counter, defaultdict

SCRAPER_DIR = os.path.expanduser("~/.kairos/x-scraper/aleabitoreddit")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "references", "_auto")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---- 工具函数 ----
def parse_x_date(s):
    return datetime.strptime(s, '%a %b %d %H:%M:%S %z %Y')

def extract_tickers(text):
    """提取 $TICKER，过滤假阳性"""
    false_positives = {
        'I','A','THE','AND','FOR','NOT','ALL','NEW','ONE','OUT','TOP',
        'AI','AT','IN','ON','IT','OR','TO','NO','BE','S','T','M',
        'JUST','FROM','WITH','LIKE','MORE','OVER','INTO','ALSO',
        'CEO','OFC','GTC','API','CPU','GPU','TPU','HBM','CPO','SIPH',
        'BIDEN','TRUMP','CHINA','JAPAN','KOREA','EU',
    }
    tickers = []
    for m in re.findall(r'\$([A-Z]{1,5})', text):
        if m not in false_positives:
            tickers.append(m)
    return tickers

def load_tweets(since_dt=None, days=None):
    """加载指定时间范围的推文"""
    if days:
        since_dt = datetime.now(timezone.utc) - timedelta(days=days)
    if not since_dt:
        since_dt = datetime.now(timezone.utc) - timedelta(days=7)

    tweets = []
    if not os.path.isdir(SCRAPER_DIR):
        print(f"❌ 推文目录不存在: {SCRAPER_DIR}")
        return tweets

    for fname in sorted(os.listdir(SCRAPER_DIR)):
        if not fname.endswith('.jsonl'):
            continue
        fpath = os.path.join(SCRAPER_DIR, fname)
        try:
            with open(fpath) as f:
                for line in f:
                    try:
                        t = json.loads(line)
                        dt = parse_x_date(t["created_at"])
                        if dt >= since_dt:
                            tweets.append(t)
                    except (json.JSONDecodeError, ValueError, KeyError):
                        pass
        except Exception as e:
            print(f"   ⚠️ 读取 {fname} 失败: {e}")
    return sorted(tweets, key=lambda t: t["created_at"])

# ---- 信号检测 ----
POSITION_KEYWORDS = ['disclosure','own','position','holding','concentration',
                     'adding','bought','long on','favorite','heavily added',
                     'starter position','largest position','core position']
BULLISH_KEYWORDS = ['bullish','validation','confirmed','catalyst','supercycle',
                    'bottleneck','chokepoint','monopoly','reaffirm','upside']
BEARISH_KEYWORDS = ['bearish','avoid','short','dilution','bagholder','f-tier',
                    'lowest signal','designed out','downgrade','sell']
METHODOLOGY_KEYWORDS = ['principle','methodology','framework','checklist',
                        'pattern','template','playbook','repeatable',
                        'distinction','formal','arbitrage','paradox']

def detect_signals(tweets):
    """检测多空信号和方法论内容"""
    positions = defaultdict(list)
    bullish = defaultdict(list)
    bearish = defaultdict(list)
    methodology = []

    for t in tweets:
        txt = t["text"].lower()
        tickers = list(set(extract_tickers(t["text"])))

        # 方法论内容
        if any(kw in txt for kw in METHODOLOGY_KEYWORDS):
            methodology.append({
                "date": t["created_at"][:10],
                "id": t["id"],
                "text": t["text"][:300],
                "tickers": tickers,
            })

        for tk in tickers:
            entry = {"date": t["created_at"][:10], "id": t["id"], "text": t["text"][:300]}

            if any(kw in txt for kw in POSITION_KEYWORDS):
                positions[tk].append(entry)
            elif any(kw in txt for kw in BULLISH_KEYWORDS):
                bullish[tk].append(entry)
            elif any(kw in txt for kw in BEARISH_KEYWORDS):
                bearish[tk].append(entry)

    return positions, bullish, bearish, methodology

# ---- 生成输出 ----
def gen_ticker_updates(tweets, positions, bullish, bearish):
    """生成 ticker-theses.md 风格的更新条目"""
    ticker_counts = Counter()
    for t in tweets:
        ticker_counts.update(set(extract_tickers(t["text"])))

    lines = [
        f"# Auto-generated ticker updates",
        f"# Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"# Review before merging into ticker-theses.md",
        f"",
    ]

    # 按提及频率排序
    for ticker, count in ticker_counts.most_common(30):
        lines.append(f"## ${ticker} — {count} mentions")
        lines.append("")

        if ticker in positions:
            lines.append(f"### Position/Disclosure signals ({len(positions[ticker])}):")
            for s in positions[ticker][-5:]:
                lines.append(f"- [{s['date']}] {s['text'][:200]}")
            lines.append("")

        if ticker in bullish:
            lines.append(f"### Bullish signals ({len(bullish[ticker])}):")
            for s in bullish[ticker][-5:]:
                lines.append(f"- [{s['date']}] {s['text'][:200]}")
            lines.append("")

        if ticker in bearish:
            lines.append(f"### Bearish/avoid signals ({len(bearish[ticker])}):")
            for s in bearish[ticker][-5:]:
                lines.append(f"- [{s['date']}] {s['text'][:200]}")
            lines.append("")

    return "\n".join(lines)

def gen_track_record(positions, bullish, bearish):
    """生成 track-record.md 风格的新条目"""
    lines = [
        f"# Auto-generated track record entries",
        f"# Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"# Review before merging into track-record.md",
        f"",
        f"| Date | Ticker | Signal | Evidence |",
        f"|------|--------|--------|----------|",
    ]

    all_signals = []
    for tk, entries in positions.items():
        for e in entries:
            all_signals.append((e["date"], tk, "Position", e["text"][:150]))
    for tk, entries in bullish.items():
        for e in entries:
            all_signals.append((e["date"], tk, "Bullish", e["text"][:150]))
    for tk, entries in bearish.items():
        for e in entries:
            all_signals.append((e["date"], tk, "Bearish", e["text"][:150]))

    all_signals.sort(key=lambda x: x[0], reverse=True)
    for date, tk, sig, text in all_signals[:50]:
        text = text.replace("|", "/")
        lines.append(f"| {date} | ${tk} | {sig} | {text} |")

    return "\n".join(lines)

def gen_methodology_notes(methodology_tweets):
    """生成方法论笔记"""
    if not methodology_tweets:
        return "# No new methodology signals detected."

    lines = [
        f"# Auto-generated methodology notes",
        f"# Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"# Review before merging into methodology.md incremental notes",
        f"",
    ]

    for m in methodology_tweets[:20]:
        tickers_str = ",".join(f"${t}" for t in m["tickers"][:5])
        lines.append(f"### [{m['date']}] — {tickers_str}")
        lines.append(f"Source: {m['id']}")
        lines.append(f"")
        lines.append(f"> {m['text']}")
        lines.append(f"")

    return "\n".join(lines)

# ---- 主流程 ----
def main():
    parser = argparse.ArgumentParser(description="更新 serenity references 从推文数据")
    parser.add_argument("--since", help="起始日期 YYYY-MM-DD")
    parser.add_argument("--days", type=int, help="最近N天")
    parser.add_argument("--ticker", help="只看特定标的")
    parser.add_argument("--dry-run", action="store_true", help="预览不写入")
    args = parser.parse_args()

    since_dt = None
    if args.since:
        since_dt = datetime.strptime(args.since, "%Y-%m-%d").replace(tzinfo=timezone.utc)

    print(f"📥 加载推文...")
    tweets = load_tweets(since_dt=since_dt, days=args.days)
    if not tweets:
        print("❌ 无推文数据")
        sys.exit(1)

    dates = sorted(set(parse_x_date(t["created_at"]) for t in tweets))
    print(f"   {len(tweets)} 条推文 | {dates[0].strftime('%Y-%m-%d')} → {dates[-1].strftime('%Y-%m-%d')}")

    # 如果指定 ticker，过滤
    if args.ticker:
        tk_upper = args.ticker.upper().lstrip("$")
        tweets = [t for t in tweets if tk_upper in extract_tickers(t["text"])]
        print(f"   过滤 ${tk_upper}: {len(tweets)} 条相关推文")
        if not tweets:
            print(f"❌ 无 ${tk_upper} 相关推文")
            sys.exit(0)

    # 检测信号
    print(f"🔍 检测信号...")
    positions, bullish, bearish, methodology = detect_signals(tweets)

    pos_count = sum(len(v) for v in positions.values())
    bull_count = sum(len(v) for v in bullish.values())
    bear_count = sum(len(v) for v in bearish.values())
    print(f"   持仓信号: {pos_count} | 看多: {bull_count} | 看空: {bear_count} | 方法论: {len(methodology)}")

    # 生成输出
    ticker_updates = gen_ticker_updates(tweets, positions, bullish, bearish)
    track_record = gen_track_record(positions, bullish, bearish)
    method_notes = gen_methodology_notes(methodology)

    if args.dry_run:
        print(f"\n{'='*60}")
        print("📋 DRY RUN — 预览（不写入文件）")
        print(f"{'='*60}")
        print(f"\n--- ticker-updates.md ---")
        print(ticker_updates[:2000])
        print(f"\n--- track-record-new.md ---")
        print(track_record[:1000])
        print(f"\n--- methodology-notes.md ---")
        print(method_notes[:1000])
    else:
        for name, content in [
            ("ticker-updates.md", ticker_updates),
            ("track-record-new.md", track_record),
            ("methodology-notes.md", method_notes),
        ]:
            path = os.path.join(OUTPUT_DIR, name)
            with open(path, "w") as f:
                f.write(content)
            print(f"✅ 已写入: {path}")

        print(f"\n💡 下一步: 人工审核 {OUTPUT_DIR}/ 中的草稿，合并到 references/")

if __name__ == "__main__":
    main()
