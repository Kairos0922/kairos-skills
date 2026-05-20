---
title: Agent Skills 技术文章样例
---

# Agent Skills：把 AI Agent 能力封装成可复用工程资产

:::lead
Agent Skills 是一种轻量、开放的能力封装格式。它把专业知识、工作流、脚本、参考资料和模板放进一个可版本化的目录，让 AI Agent 在真正需要时再加载对应能力。
:::

原创　Kairos Skills　｜　2026.05.20

本文用一篇标准技术文章的结构介绍 Agent Skills，同时展示 `song` 主题在微信公众号正文里的技术排版能力。

资料来源包括 [Agent Skills Overview](https://agentskills.io/home)、[Specification](https://agentskills.io/specification) 和 [Best practices for skill creators](https://agentskills.io/skill-creation/best-practices)。

如果只记住一句话，可以先记住这个判断：==Skill 不是提示词的长版本，而是可验证的能力接口==。它把 **触发条件**、*执行顺序*、`scripts/`、模板和边界说明放在一起，减少 ~~临场发挥~~ 不必要的不确定性。

> [!NOTE]
> 这篇文章不是普通视觉矩阵，而是一篇接近真实发布场景的技术文样例：它包含概念解释、结构图、配置代码、命令、表格、提示块、检查清单和结尾总结。

![Agent Skills 工作流概览](https://placehold.co/1200x520/e9eef7/26364a.png?text=Skill+Workflow+Overview)

## 01 Agent Skills 解决什么问题

AI Agent 已经能处理复杂任务，但它常常缺少项目上下文、团队约定和领域流程。Agent Skills 的核心价值，是把这些隐性知识沉淀成可复用的工程资产。

一个 skill 通常用来封装三类内容：

- 领域知识：例如法务审查、数据分析、文档排版、投研流程。
- 可重复工作流：例如先解析输入，再执行脚本，最后运行验证。
- 项目上下文：例如目录结构、命名规则、输出格式、常见坑。

:::pullquote
好的 skill 不只是告诉 Agent “做什么”，更要告诉它“何时使用、如何执行、如何验证”。
:::

### 渐进披露是关键设计

Agent Skills 使用 progressive disclosure。Agent 启动时只需要看到 skill 的 `name` 和 `description`，当用户任务匹配时再读取完整的 `SKILL.md`，必要时继续加载 `scripts/`、`references/` 或 `assets/`。

这种机制的好处是：你可以拥有很多 skills，但不会在每次对话里一次性塞满上下文窗口。

:::insight
渐进披露的真正价值，不是少读几个文件，而是让 Agent 在正确的时刻读取正确的上下文。
:::

## 02 一个标准 Skill 的目录结构

根据规范，一个 skill 至少是一个包含 `SKILL.md` 的目录。可选目录用于承载脚本、参考资料和模板资产。

```text
my-skill/
├── SKILL.md
├── scripts/
│   └── validate.py
├── references/
│   └── api-errors.md
├── assets/
│   └── report-template.md
└── README.md
```

:::figure
![Agent Skills 目录结构示意图](https://placehold.co/1200x760/f1e8dc/3f3932.png?text=Agent+Skills+Directory)
一个 skill 目录应当像一个小型工程包：入口清晰，资源按需加载，验证路径可重复。
:::

### `SKILL.md` 的最小结构

`SKILL.md` 必须包含 YAML frontmatter，然后是 Markdown 正文。`name` 和 `description` 是必填字段。

```yaml
---
name: markdown-report
description: Convert research notes into a structured Markdown report. Use when the user asks for a repeatable report format, source synthesis, or technical writing workflow.
---

# markdown-report

## Workflow

1. Read the source notes.
2. Extract claims, evidence, and open questions.
3. Render the final report using the template in `assets/report-template.md`.
4. Run `scripts/validate_report.py` before returning the result.
```

> [!WARNING]
> `name` 应该和目录名匹配，并使用小写字母、数字和连字符。`description` 需要同时说明能力和触发场景，否则 Agent 很难准确激活它。

## 03 Frontmatter 字段速查

下面这张表适合放在技术文章里做规范速查。微信公众号移动端不适合原生宽表格，所以 `song` 会把它降级成堆叠信息块。

| 字段 | 是否必填 | 用途 |
| --- | --- | --- |
| `name` | 是 | skill 的机器可读名称，建议短而稳定 |
| `description` | 是 | 描述能力和触发条件，是 discovery 阶段的关键 |
| `license` | 否 | 标注许可或指向许可文件 |
| `compatibility` | 否 | 说明产品、系统依赖或网络访问要求 |
| `metadata` | 否 | 存储自定义键值信息 |
| `allowed-tools` | 否 | 实验字段，用于声明预批准工具 |

### 常见可选目录

- `scripts/`：放可执行代码，适合校验、转换、抓取、生成等确定性步骤。
- `references/`：放按需读取的技术文档、API 说明、错误码、领域规则。
- `assets/`：放模板、图片、静态数据、示例输入输出。
- `evals/`：放评测样例，帮助迭代 skill 的可靠性。

## 04 写好 Skill 的工程方法

官方最佳实践强调：不要让 LLM 凭空生成泛泛而谈的 skill。更可靠的方法，是从真实任务、真实修正和真实失败里提取可复用流程。

:::soft-list
- 从一次成功任务中抽取步骤，而不是从抽象概念开始写。
- 记录你纠正 Agent 的地方，因为这些往往就是 skill 最有价值的约束。
- 把输入、输出、验证命令和常见边界情况写清楚。
- 让脚本承担确定性工作，让说明承担判断边界。
:::

### 适度详细，而不是无限详细

Skill 需要补足 Agent 缺少的上下文，而不是解释它已经知道的常识。比如处理 PDF 时，通常不需要解释 PDF 是什么；更有价值的是指定项目采用的库、扫描件 fallback、输出格式和验证方式。

> [!TIP]
> 一个实用判断：如果没有这条说明，Agent 大概率会做错，就保留；如果 Agent 本来就会，删掉。

### 给默认路径，不要给菜单

当多个工具都能完成任务时，skill 应该给出默认选择，并简短说明替代方案。这样 Agent 不会在等价选项之间消耗上下文和时间。

```python
def choose_pdf_parser(scanned: bool) -> str:
    if scanned:
        return "pdf2image + pytesseract"
    return "pdfplumber"
```

## 05 验证循环：让 Skill 可维护

一个成熟 skill 不应该只是一段说明。它最好自带验证循环，让 Agent 每次执行后能发现问题并自我修正。

```bash
python scripts/validate.py output/
python scripts/evaluate.py fixtures/*.json
```

推荐的执行模式如下：

1. 读取用户输入和 skill 说明。
2. 按 workflow 执行任务。
3. 运行验证脚本或检查清单。
4. 修复失败项。
5. 只在验证通过后返回结果。

### 任务检查清单

- [x] `SKILL.md` 有清晰的 `name` 和 `description`
- [x] 工作流步骤能被 Agent 顺序执行
- [ ] 关键边界情况有 gotchas
- [ ] 有可运行脚本或人工检查清单
- [ ] 输出格式有模板或示例

## 06 发布前的常见问答

### Q1：Skill 应该写多长？

够 Agent 做对任务即可。与其写一篇百科，不如把触发条件、输入输出、验证命令和容易踩错的边界写清楚。

### Q2：脚本一定要有吗？

不一定。纯判断型 workflow 可以没有脚本，但只要任务里出现转换、校验、抓取、渲染或批处理，就应该优先沉淀成可运行脚本。

### Q3：什么时候拆成多个 skills？

当两个任务的触发场景、输入资产和验证方式明显不同，就应该拆开。一个 skill 只解决一个连贯 workflow，后续维护会轻很多。

---

## 07 一个实用 Skill 的设计模板

下面是一个更接近生产使用的模板。它把触发条件、执行步骤、验证和常见坑放在同一个入口文件里。

```markdown
# data-quality-check

## When to use

Use this skill when the user asks to validate a CSV export, compare schema drift, or produce a data quality report.

## Workflow

1. Inspect the input file path and schema.
2. Run `scripts/profile_csv.py`.
3. Compare required columns against `references/schema.md`.
4. Generate the report with `assets/report-template.md`.
5. Run `scripts/validate_report.py`.

## Gotchas

- Empty strings and `NULL` must be counted separately.
- Date columns are expected in ISO 8601.
- Do not modify source data files.
```

---

## 08 延伸阅读

- [Agent Skills Overview](https://agentskills.io/home)
- [Agent Skills Specification](https://agentskills.io/specification)
- [Best practices for skill creators](https://agentskills.io/skill-creation/best-practices)

## 09 小结

Agent Skills 把 Agent 的能力从“临场提示词”推进到“可维护工程包”。它的核心不是写更多说明，而是把任务触发、执行步骤、项目约定、脚本工具和验证循环放到一个稳定结构里。

:::closing-note
当一个 skill 能被复用、能被验证、能被迭代，它就不再是一段提示词，而是一份真正的团队资产。
:::
