---
name: kairos-collect-signals
description: |
  通用的微信公众号选题 Skill。通过“张力 → 因果 → 结构 → 选题卡”把信号转化为可写选题。

  触发场景：
  - "帮我看看最近有什么值得写的"
  - "我想找某个方向的独特角度"
  - "有什么有问题意识的选题可以写"
  - "从信号里提炼机制和结构"
  - "做一轮选题方向扫描"

  注意：
  - 引擎是通用的，默认内置 `ai-engineering` 领域插件
  - 垂直领域通过 `domains/<domain>/` 的配置文件可插拔接入
  - 默认策略由 `domains/<domain>/strategy_binding.json` 决定，切换领域即可切换默认策略
  - `sources / keywords / high_quality_authors` 只属于领域插件，不做共享
  - `banned_patterns` 只属于策略，不放在领域插件或 references
  - 策略可插拔（strategies/<strategy>/）
metadata:
  version: "6.2"
---

# kairos-collect-signals

## Purpose / 目的

从多源信号中提取认知张力，推导因果机制与结构模式，输出真正可用的公众号选题卡。
Skill 本体是通用引擎；某个垂直领域只通过配置文件接入，不把领域逻辑写死在核心流程里。

## When to use / 何时使用

- 需要从近期信号中找“问题意识”的选题
- 需要提炼机制/结构，而非热点罗列
- 需要基于失败、权衡、异常的具体写作角度
- 需要为某个垂直领域快速挂载数据源、关键词、读者画像、选题偏好

## Files / 目录结构

```text
kairos-collect-signals/
├── SKILL.md
├── scripts/
├── strategies/
│   └── problem-solving/
│       ├── banned_patterns.json
│       ├── config.json
│       └── *.md
├── domains/
│   └── ai-engineering/
│       ├── profile.json
│       ├── sources.json
│       ├── keywords.json
│       ├── high_quality_authors.json
│       ├── strategy_binding.json
│       └── topic_rules.json
```

领域插件约定：
- `profile.json`: 领域说明、默认读者、文章结构、why_now 模板
- `sources.json`: 当前领域的数据源
- `sources.json[].type`: 数据源 adapter 类型，当前支持 `rss / github / reddit / x`
- `keywords.json`: 当前领域的关键词与时效配置
- `high_quality_authors.json`: 当前领域的高质量作者 / 社区名单
- `strategy_binding.json`: 当前领域默认绑定的策略、允许的策略、策略级配置覆盖
- `topic_rules.json`: 焦点覆盖、读者细分、结构偏好、why_now 模板

## Core workflow / 核心流程

1. 选择领域插件
默认领域为 `ai-engineering`。若接入新领域，优先在 `domains/<domain>/` 下补齐配置文件，而不是改核心脚本。
默认策略由 `domains/<domain>/strategy_binding.json` 自动解析，通常只切换 `domain` 即可。

2. 信号采集
如果 `./.kairos-temp/signals.json` 已存在（evals 或 harness 预填充），跳过采集。

当前采集器按 `sources.json[].type` 分发 adapter。已内置：
- `rss`
- `github`
- `reddit`
- `x`

注意：
- 当前这 4 类 adapter 都通过 feed 形式接入
- 如果某个平台需要原生 API、鉴权、分页或复杂查询，应新增独立 adapter，不要继续堆在 `collector.py`

```bash
python3 scripts/collect.py --domain ai-engineering --tier 1 --limit 100 --output ./.kairos-temp/signals.json
python3 scripts/collect.py --domain ai-engineering --tier 1 --limit 100 --keywords "LangChain RAG" --output ./.kairos-temp/signals.json
```

3. 去重

```bash
python3 scripts/dedup.py --input ./.kairos-temp/signals.json --output ./.kairos-temp/signals-deduped.json
```

4. 过滤信号（必须执行）
使用 `scripts/filter.py`。来源白名单与高质量作者来自 `domains/<domain>/`；禁用模式来自 `strategies/<strategy>/banned_patterns.json`。

```bash
python3 scripts/filter.py --domain ai-engineering --input ./.kairos-temp/signals-deduped.json --output ./.kairos-temp/signals-filtered.json
```

5. 载入策略
策略目录必须符合命名规范（小写 + 连字符）。默认策略通过 `domains/<domain>/strategy_binding.json` 决定；仅在需要高级覆盖时显式传 `--strategy`。

读取：
- `strategies/{strategy}/banned_patterns.json`
- `strategies/{strategy}/config.json`
- `strategies/{strategy}/tension_prompt.md`
- `strategies/{strategy}/causal_prompt.md`
- `strategies/{strategy}/abstraction_prompt.md`
- `strategies/{strategy}/angle_prompt.md`

6. 张力检测（Tension Detection）
使用 `tension_prompt.md` 对 `signals-filtered.json` 进行张力提取，输出：

```
./.kairos-temp/tensions.json
```

规则：
- 必须有 expectation vs reality
- tension_strength >= config.tension_filter.min_strength
- 无张力则丢弃

7. 因果推导（Causal Derivation）
使用 `causal_prompt.md`，输出：

```
./.kairos-temp/causal_chains.json
```

规则：
- 必须给出机制和因果链
- 无因果链则丢弃

8. 结构抽象（Abstraction）
使用 `abstraction_prompt.md`，输出：

```
./.kairos-temp/patterns.json
```

9. 选题生成（Topic Generation）
使用 `angle_prompt.md` 基于 patterns 生成自然语言选题报告。内部可以保留结构化中间结果，但最终输出必须是自然语言，而不是 JSON：

```
./.kairos-temp/topic-report.md
```

10. 本地回归测试（推荐）
开发或优化 skill 时，使用启发式分析脚本与 evals 做回归验证：

```bash
python3 scripts/run_evals.py
```

如需对单个 signals 文件做结构化分析，可运行：

```bash
python3 scripts/analyze.py --domain ai-engineering --input ./.kairos-temp/signals.json --output ./.kairos-temp/topic-report.md
python3 scripts/analyze.py --domain ai-engineering --strategy problem-solving --input ./.kairos-temp/signals.json --output ./.kairos-temp/topic-report.md
```

11. 输出结果
输出 Markdown 自然语言报告。如果没有形成可写选题，也必须输出自然语言说明为什么没有选题。

12. 清理
最后执行清理，删除 `./.kairos-temp/`。

```bash
python3 scripts/cleanup.py
```

## Input / 输入

```json
{
  "domain": "ai-engineering",   // 可选：领域插件名（默认 ai-engineering）
  "keywords": "LLM RAG",        // 可选：用户关键词
  "tier": 1,                    // 可选：采集 tier（默认 1）
  "limit": 100,                 // 可选：信号数量限制（默认 100）
  "strategy": "problem-solving", // 可选：策略目录名；留空则从 strategy_binding.json 自动解析
  "domain_context": {}          // 可选：未来用于传递垂直领域额外上下文
}
```

## Output / 输出

最终输出必须是自然语言报告，例如：

```md
# 微信公众号选题报告

领域：ai-engineering
策略：problem-solving
扫描信号数：40
过滤后信号数：8
形成选题数：2

以下是本轮可写的选题：

## 选题 1
选题题面：RAG 为什么会在多跳问题里失效：一次围绕准确率下降 19% 的排查复盘
要回答的问题：为什么 RAG 系统会在关键场景中失效，而且这种失效不是偶发事件？
为什么现在值得写：很多团队都在上线 RAG，但大多数讨论只讲方案，不讲为什么会慢、为什么会失效。
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

## Examples / 示例

输入：
"帮我看看最近有什么值得写的信号"

输出：
- 输出是一份自然语言选题报告
- 每个选题都必须带 `来源 / 时间 / 网址`
- 如果没有网址，也要明确写出 `网址：未提供`

## Gotchas / 注意事项

- 没有张力就没有选题，不能硬生成。
- 没有因果链就不输出结果，避免伪机制。
- 选题必须来源于 failure 或 tradeoff，禁止综述与趋势预测。
- 最终输出不能是 JSON，必须是自然语言报告。
- 每个选题都必须写清楚 `来源 / 时间 / 网址`，其中网址如果存在必须完整带出。
- 内部可以保留结构化中间结果用于测试，但对外输出必须是自然语言。
- 对反馈闭环优化类信号，优先输出“闭环为什么跑偏 / 奖励为什么被投机 / verifier 为什么带偏优化方向”这类机制题。
- 如果你要覆盖 AI 以外的领域，优先新增 `domains/<domain>/`，不要直接改默认 `ai-engineering` 领域。
- 新领域至少补齐 `sources.json / keywords.json / high_quality_authors.json / profile.json / topic_rules.json / strategy_binding.json`。
- strategies 目录名必须是小写+连字符，避免下划线。

## Validation / 验证

- `tensions` 中必须同时包含 expectation 与 reality。
- `causal_chains.causal_chain` 必须是因果序列。
- 自然语言报告必须至少包含 `选题题面 / 要回答的问题 / 为什么现在值得写 / 核心洞察 / 目标读者 / 来源 / 时间 / 网址`。
- 优化后运行 `python3 scripts/run_evals.py`，应确保关键 case 通过。

## Files / 关键文件

- `domains/ai-engineering/profile.json`
- `domains/ai-engineering/topic_rules.json`
- `domains/ai-engineering/sources.json`
- `domains/ai-engineering/keywords.json`
- `domains/ai-engineering/high_quality_authors.json`
- `domains/ai-engineering/strategy_binding.json`
- `scripts/collect.py`
- `scripts/dedup.py`
- `scripts/filter.py`
- `scripts/domain_config.py`
- `scripts/analyze.py`
- `scripts/run_evals.py`
- `scripts/cleanup.py`
- `scripts/source_adapters/base.py`
- `scripts/source_adapters/registry.py`
- `scripts/source_adapters/rss.py`
- `scripts/source_adapters/github.py`
- `scripts/source_adapters/reddit.py`
- `scripts/source_adapters/x.py`
- `strategies/problem-solving/banned_patterns.json`
- `strategies/problem-solving/config.json`
- `strategies/problem-solving/tension_prompt.md`
- `strategies/problem-solving/causal_prompt.md`
- `strategies/problem-solving/abstraction_prompt.md`
- `strategies/problem-solving/angle_prompt.md`
