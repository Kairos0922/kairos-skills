#!/usr/bin/env python3
"""
kairos-x-scraper 分析工具 — 从抓取的 JSONL 中提取信号
用法:
  python3 analyze_tweets.py <tweets.jsonl> [--days 3] [--mode summary|signals|tickers|all]
"""

import json, sys, re, argparse
from datetime import datetime, timedelta, timezone
from collections import Counter

def parse_x_date(s):
    return datetime.strptime(s, '%a %b %d %H:%M:%S %z %Y')

def filter_recent(tweets, days):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    return [t for t in tweets if parse_x_date(t['created_at']) >= cutoff]

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

def detect_signals(tweets):
    """识别 bullish / bearish / position 信号"""
    bullish, bearish, positions = [], [], []
    for t in tweets:
        txt = t['text'].lower()
        tk = list(set(extract_tickers(t['text'])))
        entry = {'date': t['created_at'][4:10], 'tickers': tk, 'text': t['text'][:200]}

        # 持仓/看多信号
        if any(w in txt for w in ['disclosure','own','position','holding','concentration',
                                    'adding','bought','long on','favorite','heavily added']):
            positions.append(entry)
        elif any(w in txt for w in ['bullish','validation','confirmed','catalyst',
                                      'supercycle','bottleneck','chokepoint','monopoly']):
            bullish.append(entry)

        # 看空/回避信号
        if any(w in txt for w in ['bearish','avoid','short','dilution','bagholder',
                                    'f-tier','lowest signal','designed out']):
            bearish.append(entry)

    return bullish, bearish, positions

THEME_KEYWORDS = {
    '光学/CPO/光子': ['optical','CPO','photonics','laser','CW','DFB','InP','transceiver',
                      'LITE','SIVE','AAOI','COHR','POET','AXTI','SOI'],
    '存储/HBM': ['memory','NAND','DRAM','HBM','SNDK','Samsung','Hynix','MU'],
    'AI/GPU/算力': ['NVDA','GPU','NVIDIA','AMD','AVGO','MRVL','ASIC','TPU','TSM','ARM'],
    '新云/数据中心': ['NBIS','neocloud','datacenter','IREN','CRWV','CIFR','capex'],
    '人形机器人': ['humanoid','robot','Agility','CCXI','physical AI','Unitree','Optimus'],
    '电网/能源': ['power','grid','energy','transformer','VRT','XLU','AOSL'],
    '太空/卫星': ['space','RKLB','satellite','ASTS','SPCX','Starlink'],
}

def theme_analysis(tweets):
    """统计各主题推文占比"""
    counts = {}
    for theme, kws in THEME_KEYWORDS.items():
        count = sum(1 for t in tweets if any(kw.lower() in t['text'].lower() for kw in kws))
        counts[theme] = count
    return counts

def main():
    parser = argparse.ArgumentParser(description="分析推文 JSONL")
    parser.add_argument("jsonl", help="tweets JSONL 文件路径")
    parser.add_argument("--days", type=int, default=None, help="只分析最近N天")
    parser.add_argument("--mode", default="all", choices=["summary","signals","tickers","all"])
    args = parser.parse_args()

    tweets = [json.loads(l) for l in open(args.jsonl)]
    total = len(tweets)

    if args.days:
        tweets = filter_recent(tweets, args.days)

    if args.mode in ("summary", "all"):
        print(f"📊 摘要: {len(tweets)}/{total}条")
        if tweets:
            dates = sorted([parse_x_date(t['created_at']) for t in tweets])
            print(f"   📅 {dates[0].strftime('%m-%d')} → {dates[-1].strftime('%m-%d')}")

        themes = theme_analysis(tweets)
        if themes:
            print("   🔑 主题:")
            for theme, n in sorted(themes.items(), key=lambda x: x[1], reverse=True):
                pct = n / len(tweets) * 100 if tweets else 0
                bar = '█' * int(pct / 3)
                print(f"      {theme:12s} {n:3d}条 {pct:4.0f}% {bar}")

    if args.mode in ("tickers", "all"):
        tc = Counter()
        for t in tweets:
            tc.update(set(extract_tickers(t['text'])))
        print(f"\n🏷️ 股票代码 TOP 20:")
        for tk, n in tc.most_common(20):
            print(f"   ${tk:5s} {n:3d}")

    if args.mode in ("signals", "all"):
        bullish, bearish, positions = detect_signals(tweets)
        if positions:
            print(f"\n📗 持仓信号 ({len(positions)}):")
            for s in positions[-10:]:
                tks = ','.join(f'${x}' for x in s['tickers'][:5])
                print(f"   [{s['date']}] {tks}")
                print(f"   {s['text'][:140]}")
        if bullish:
            print(f"\n🟢 看多信号 ({len(bullish)}):")
            for s in bullish[-10:]:
                tks = ','.join(f'${x}' for x in s['tickers'][:5])
                print(f"   [{s['date']}] {tks}: {s['text'][:120]}")
        if bearish:
            print(f"\n🔴 看空信号 ({len(bearish)}):")
            for s in bearish[-10:]:
                tks = ','.join(f'${x}' for x in s['tickers'][:5])
                print(f"   [{s['date']}] {tks}: {s['text'][:120]}")

if __name__ == "__main__":
    main()
