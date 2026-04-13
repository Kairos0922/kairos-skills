# kairos-collect-signals

`kairos-collect-signals` 是一个通用的微信公众号选题 Skill。

它的目标不是生成标题库，而是把多源信号转成可写的公众号选题报告。核心流程是：

`信号采集 -> 去重 -> 过滤 -> 张力 -> 因果 -> 抽象 -> 选题报告`

## 60 秒上手

第一次跑之前，先把 `TAVILY_API_KEY` 放进本地系统钥匙串：

```bash
pip install keyring
python3 /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/scripts/setup_tavily_key.py
```

然后直接执行一轮完整流程：

```bash
python3 /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/scripts/collect.py \
  --domain ai-engineering \
  --tier 2 \
  --limit 80 \
  --output /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/.kairos-temp/signals.json

python3 /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/scripts/dedup.py \
  --input /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/.kairos-temp/signals.json \
  --output /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/.kairos-temp/signals-deduped.json

python3 /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/scripts/filter.py \
  --domain ai-engineering \
  --input /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/.kairos-temp/signals-deduped.json \
  --output /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/.kairos-temp/signals-filtered.json

python3 /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/scripts/analyze.py \
  --domain ai-engineering \
  --input /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/.kairos-temp/signals-filtered.json \
  --output /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/.kairos-temp/topic-report.md
```

当前默认领域已经收敛到三类高价值关注点：

- `AI Agent` 设计、开发到生产落地
- `Skill` 设计、开发到生产落地
- `OpenClaw`

OpenClaw cron（allowlist 模式）建议使用单命令入口：

```bash
python3 /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/scripts/run_pipeline.py \
  --domain ai-engineering \
  --tier 1 \
  --limit 100
```

默认内置一个领域插件：

- `ai-engineering`（精简关键词，聚焦：AI Agent 设计/从开发到生产、Skill 设计/从开发到生产、OpenClaw）

这套架构支持通过配置文件切换垂直领域，也支持通过 adapter 扩展新的数据源类型。

## 适用场景

- 想从近期信号里找到值得写的公众号选题
- 想输出带问题意识、机制洞察和写作切口的选题
- 想按不同垂直领域切换数据源、关键词、读者画像和默认策略
- 想把 Skill 做成可插拔的长期选题基础设施

## 当前能力

- 通用领域插件架构
- 默认策略自动跟随领域切换
- 自然语言选题报告输出
- 输出中强制包含来源、时间、网址
- 支持按数据源类型分发采集 adapter
- 支持 Tavily 搜索与 GitHub 仓库搜索
- 内置本地回归测试

## 当前限制

- 当前采集器虽然已经是 adapter 架构，但内置的 `rss / github / reddit / x` 仍然走 feed 形态接入
- 还没有实现原生 `GitHub API / Reddit API / X API`
- 领域插件默认只内置了一个：`ai-engineering`

## 运行前提

- 使用 `tavily` adapter 或 `discover_sources.py` 时，运行环境必须提供 `TAVILY_API_KEY`
- 使用 `github-search` adapter 时，运行环境必须安装并可用 `gh` CLI

### 首次使用（密钥配置）
- 我们不再使用 `.env` 或 `.env.encrypted` 文件存储密钥。
- 推荐把 `TAVILY_API_KEY` 写入操作系统钥匙串（Keychain）：

```bash
pip install keyring
python3 /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/scripts/setup_tavily_key.py
```

说明：运行时会优先读取环境变量 `TAVILY_API_KEY`，如未设置则回退读取系统钥匙串（`service=kairos-collect-signals, user=tavily_api_key`）。
缺少密钥时，不会导致整个采集器崩溃，但 `tavily` 相关搜索源会被跳过。

## 目录结构

```text
kairos-collect-signals/
├── SKILL.md
├── README.md
├── domains/
│   └── ai-engineering/
│       ├── profile.json
│       ├── sources.json
│       ├── search_queries.json
│       ├── keywords.json
│       ├── high_quality_authors.json
│       ├── strategy_binding.json
│       └── topic_rules.json
├── strategies/
│   └── problem-solving/
│       ├── banned_patterns.json
│       ├── config.json
│       ├── tension_prompt.md
│       ├── causal_prompt.md
│       ├── abstraction_prompt.md
│       └── angle_prompt.md
├── scripts/
│   ├── collect.py
│   ├── collector.py
│   ├── dedup.py
│   ├── filter.py
│   ├── analyze.py
│   ├── run_evals.py
│   └── source_adapters/
└── evals/
    └── evals.json
```

## 核心设计

### 1. 通用引擎

引擎负责固定流程：

- 采集信号
- 去重
- 过滤低质量内容
- 识别 expectation vs reality 的张力
- 推导机制和因果链
- 抽象成可复用模式
- 生成自然语言选题报告

### 2. 领域插件

每个领域通过 `domains/<domain>/` 接入。

领域配置负责：

- 数据源
- 关键词
- 高质量作者
- 读者画像
- 选题偏好
- 默认策略绑定

当前默认领域是：

- `ai-engineering`

### 3. 策略插件

策略通过 `strategies/<strategy>/` 接入。

策略负责：

- banned patterns
- tension 识别要求
- causal derivation 规则
- abstraction 规则
- 选题报告的生成要求

当前默认策略是：

- `problem-solving`

### 4. 数据源 adapter

采集层通过 `sources.json[].type` 分发 adapter。

当前内置：

- `rss`
- `github`
- `github-search`
- `reddit`
- `tavily`
- `x`

说明：

- `rss / github / reddit / x` 当前都以 feed 形式工作
- `github-search` 通过 `gh` CLI 查询仓库
- `tavily` 通过 `TAVILY_API_KEY` 调用 Tavily Search API
- `tavily` 已添加噪声域排除，优先减少视频站、内容农场和泛社媒结果
- 如果以后要接 API、鉴权、分页、搜索，应该新增新的 adapter，而不是堆在 `collector.py`

## 运行流程

### 1. 采集信号

```bash
python3 /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/scripts/collect.py \
  --domain ai-engineering \
  --tier 1 \
  --limit 100 \
  --output /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/.kairos-temp/signals.json
```

### 2. 去重

```bash
python3 /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/scripts/dedup.py \
  --input /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/.kairos-temp/signals.json \
  --output /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/.kairos-temp/signals-deduped.json
```

### 3. 过滤

```bash
python3 /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/scripts/filter.py \
  --domain ai-engineering \
  --input /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/.kairos-temp/signals-deduped.json \
  --output /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/.kairos-temp/signals-filtered.json
```

### 4. 生成选题报告

```bash
python3 /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/scripts/analyze.py \
  --domain ai-engineering \
  --input /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/.kairos-temp/signals-filtered.json \
  --output /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/.kairos-temp/topic-report.md
```

### 5. 清理

```bash
python3 /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/scripts/cleanup.py
```

## 输出说明

最终输出必须是自然语言报告，不是 JSON。

每个选题至少包含：

- 选题题面
- 要回答的问题
- 为什么现在值得写
- 核心洞察
- 建议切口
- 目标读者
- 文章形态
- 来源
- 时间
- 网址
- 支撑依据

如果没有形成可写选题，也必须输出自然语言说明，而不是返回空 JSON。

## 输出示例

```md
# 微信公众号选题报告

领域：ai-engineering
策略：problem-solving
扫描信号数：12
过滤后信号数：3
形成选题数：1

## 选题 1
选题题面：RAG 系统 为什么会在生产环境里失效：一次围绕准确率下降 19% 的排查复盘
要回答的问题：为什么 RAG 系统会在关键场景中失效，而且这种失效不是偶发事件？
为什么现在值得写：这类失败正在从个例变成共性，公众号最缺的是能把失败讲成结构的文章。
核心洞察：真实约束会把被忽略的系统假设放大成显性故障。
建议切口：从多跳问题、长上下文和排查路径切入。
目标读者：AI 工程师
文章形态：问题复盘型
来源：OpenAI Blog
时间：2026-04-03T10:00:00+08:00
网址：https://openai.com/blog/example
支撑依据：
- 实测 RAG 在多跳问题下准确率下降至 62%
- 来源: OpenAI Blog
- 时间: 2026-04-03T10:00:00+08:00
- 网址: https://openai.com/blog/example
- 机制: 真实约束会把被忽略的系统假设放大成显性故障。
```

## 配置说明

### `domains/<domain>/sources.json`

定义这个领域要采集哪些数据源。

关键字段：

- `name`
- `url`
- `type`
- `tier`
- `category`
- `enabled`

可选字段：

- `query_set`
- `query_template`
- `query_suffix`
- `limit`
- `max_results`
- `search_depth`

示例：

```json
{
  "sources": [
    {
      "name": "GitHub Trending",
      "url": "https://github.com/trending.rss",
      "type": "github",
      "tier": 2,
      "category": "community",
      "enabled": true
    }
  ]
}
```

### `domains/<domain>/keywords.json`

定义领域关键词和时效窗口。

关键字段：

- `default_keywords`
- `recency_days`

### `domains/<domain>/search_queries.json`

定义 query 型 adapter 使用的查询集合。

关键结构：

- `query_sets`

示例：

```json
{
  "query_sets": {
    "pain-topics": ["self-improving AI agent", "skill evaluation failure", "OpenClaw"],
    "official-blog-targets": ["OpenAI", "Anthropic", "OpenClaw"]
  }
}
```

### `domains/<domain>/high_quality_authors.json`

定义领域内可直接放行的高质量作者或社区。

### `domains/<domain>/strategy_binding.json`

定义这个领域默认使用什么策略。

示例：

```json
{
  "default_strategy": "problem-solving",
  "allowed_strategies": ["problem-solving"],
  "strategy_overrides": {
    "problem-solving": {
      "config": {}
    }
  }
}
```

## 如何新增一个领域

在 `domains/<new-domain>/` 下至少补齐这些文件：

- `profile.json`
- `sources.json`
- `search_queries.json`
- `keywords.json`
- `high_quality_authors.json`
- `strategy_binding.json`
- `topic_rules.json`

完成后，直接切换：

```bash
python3 /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/scripts/analyze.py \
  --domain <new-domain> \
  --input /path/to/signals.json \
  --output /path/to/topic-report.md
```

## 如何新增一个数据源 adapter

### 1. 新建 adapter 文件

例如：

- `scripts/source_adapters/notion.py`

### 2. 实现 adapter

要求：

- 输入 `source / cutoff_date / keywords / context`
- 输出 `List[Signal]`

### 3. 注册到 registry

修改：

- `scripts/source_adapters/registry.py`

### 4. 在领域 `sources.json` 中使用新 `type`

例如：

```json
{
  "name": "Notion Signals",
  "url": "https://...",
  "type": "notion",
  "tier": 1,
  "category": "workspace",
  "enabled": true
}
```

## 测试

### 选题回归

```bash
python3 /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/scripts/run_evals.py
```

### 当前测试覆盖

- banned patterns 过滤
- 来源白名单过滤
- 高质量作者放行
- 质量门控
- 跨主题信号抽象
- 默认策略绑定
- 自然语言报告输出
- `rss / github / github-search / reddit / tavily / x` adapter 注册与分发

说明：

- adapter 分发测试已经并入 `/Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/scripts/run_evals.py`

## 开发建议

- 不要把领域逻辑写死在脚本里
- 不要把 banned patterns 放回领域层
- 不要把 sources、keywords、authors 放回共享层
- 输出必须是自然语言报告，不要回退成 JSON
- 只在确实需要时新增 adapter，不要为了抽象而抽象

## 关键文件

- `/Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/SKILL.md`
- `/Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/README.md`
- `/Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/scripts/collector.py`
- `/Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/scripts/analyze.py`
- `/Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/scripts/filter.py`
- `/Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/scripts/discover_sources.py`
- `/Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/scripts/source_adapters/registry.py`
- `/Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/domains/ai-engineering/sources.json`
- `/Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/domains/ai-engineering/search_queries.json`
- `/Users/kenpetex/Documents/GitHub/kairos-skills/kairos-collect-signals/domains/ai-engineering/strategy_binding.json`
