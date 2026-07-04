---
name: kairos-x-scraper
description: |
  抓取 X.com（Twitter）任意公开账号的推文。触发词："抓取推文"、"抓X"、"爬twitter"、"fetch tweets"、"抓他的推文"、"抓一下XXX的X"、提到 X/Twitter 账号想抓取其内容。当用户想获取某个账号的推文数据用于分析时加载。
metadata:
  version: "1.1.0"
---

# kairos-x-scraper

按博主增量抓取 X.com 推文，数据持久化，自动跳过已有数据。

## 数据存储

```
~/.kairos/x-scraper/
├── aleabitoreddit/
│   └── tweets.jsonl      ← 该博主全部已抓取推文（增量追加 + 去重）
├── elonmusk/
│   └── tweets.jsonl
└── ...
```

每次抓取前自动检查：如果已有数据足够新（在 `--days` 范围内），直接跳过，秒级返回。

## 密钥配置

首次使用需提供 X.com 认证信息。配置保存在 `~/.kairos/kairos-x-scraper-config.json`。

### 引导用户获取 auth_token 和 ct0

1. 打开 https://x.com 并登录
2. 按 `F12` → **Application** → Cookies → `https://x.com`
3. 在列表中分别复制 `auth_token` 和 `ct0` 的 **Value**
4. 粘贴给我

> 去 X 设置中登出再重新登录可使 token 失效。

---

## 流程

### Step 1：确认信息

| 信息 | 默认值 |
|------|--------|
| 目标账号 | 必须提供 |
| 时间范围 | 3 天 |
| 强制抓取 | 否（已有足够新数据则跳过） |

展示确认摘要，等用户说"确认"。

### Step 2：检查密钥

`~/.kairos/kairos-x-scraper-config.json`：

- 存在 → Step 3
- 不存在 → 引导获取教程 → 写入配置 → Step 3

### Step 3：执行

```bash
python3 scripts/fetch_tweets.py <handle> --days 3
```

常用参数：

| 参数 | 说明 |
|------|------|
| `--days N` | 往前 N 天（默认 3） |
| `--months N` | 往前 N 月 |
| `--force` | 忽略已有数据，强制重抓 |
| `--user-query-id ID` | 手动指定 query ID（自动发现失败时） |
| `--tweets-query-id ID` | 同上 |

### 分析已抓取数据

```bash
python3 scripts/analyze_tweets.py ~/.kairos/x-scraper/<handle>/tweets.jsonl --days 3 --mode all
```

| mode | 输出 |
|------|------|
| `summary` | 条数、日期、主题分布 |
| `tickers` | 股票代码 TOP 20 |
| `signals` | 持仓/看多/看空信号 |
| `all` | 以上全部 |

### Step 4：处理结果

- **"已有数据足够新"** → 秒级返回，直接告诉用户
- **新增 N 条** → 告知新增数、总计、TOP 代码
- **401** → auth_token 过期，回到获取教程
- **429 / 限流** → 脚本自动等，告知用户耐心
- **query ID 全部失败** → 引导用户手动获取

---

## 注意事项

- 按昵称自动分目录，不覆盖历史数据
- tweet ID 去重，重复运行不产生冗余
- 遵守 X 服务条款，勿频繁抓取同一账号
