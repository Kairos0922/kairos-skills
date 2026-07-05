# AGENTS.md

This file provides guidance to AI agents when working with code in this repository.

## 项目概要

Kairos Skills 是一个个人 AI skill 集合。每个 skill 是顶级目录下自包含的独立模块，可跨项目移植。仓库不强制统一内部结构——每个 skill 的形态由它的任务决定。

**Skill 分两种形态**：
- **内容渲染型**（kairos-wechat-typeset、kairos-visual-generator）：脚本锁定视觉输出，LLM 只做编辑判断。确定性渲染管线。
- **对话/推理型**（kairos-loop、kairos-serenity、kairos-x-scraper）：通过对话产出高质量产物，规则写在 SKILL.md 中。

## 起步顺序

1. 读本文件。
2. 读根 `README.md` 了解仓库总览。
3. 读目标 skill 的 `SKILL.md`（必读，机读指令）。
4. 编辑前看一眼现有目录结构和脚本，别急着造新结构。
5. 编辑前 `git status --short`，不要覆盖无关的用户改动。

## Skill 硬约束（新增/修改 skill 必读）

每个 skill 只需满足两条规则：

1. **有 `SKILL.md`**，YAML frontmatter 至少含 `name` 和 `description`（description 是触发依据，要写清"何时加载"）。
2. **自包含、可移植**：不硬编码私有绝对路径（如 `/Users/...`），不含密钥，不依赖跨 skill 的共享目录。

其余（README、scripts/、references/、themes/、assets/ 等）按需添加，不强制。新增 skill 时**不需要**改任何中心清单——`check.py` 自动发现。

## 质量准则（非硬约束）

- 一个 skill 把一个工作流做好，而不是什么都做一点。
- 稳定行为尽量沉淀到脚本或结构化配置，减少 LLM 即兴发挥——渲染型 skill 尤其重要；推理型 skill 则把判断逻辑写进 SKILL.md 的清晰规则里。
- `SKILL.md` 保持精简，深度细节移到脚本或 `references/`。
- 渲染型 skill 的资产（字体、图片）必须本地化，不引外部 CDN，验证脚本随代码更新。

## 常用命令

```bash
python3 check.py              # 验证所有 skill
python3 check.py --smoke       # 仅基线检查
find . -type d -name __pycache__ -prune -exec rm -rf {} +
```
各 skill 的命令见对应 `SKILL.md` 或 `README.md`。

## 核心架构

### 验证管线（`check.py`）

```
自动发现 */SKILL.md → 基线检查（frontmatter + 禁止模式扫描）→ 运行 skill 自己的 validate.sh（如有）
```

- 禁止模式：`/Users/`、`/home/`、`API_KEY`、`SECRET`、`PASSWORD` 出现在文本文件中即判为不通过。
- `check.py` 不维护技能列表——靠 glob 自动发现。
- CI（`.github/workflows/ci.yml`）在 push/PR 时对 Python 3.10/3.11/3.12 运行 `python3 check.py`。

### 内容渲染型 skill 的通用管线

```
用户输入 → LLM 编辑判断（不确定）→ 确定性脚本渲染 → 验证脚本 → 输出
```

- **LLM 做**：理解需求、选择主题/风格、规划结构、编辑内容。
- **代码做**：字号、颜色、间距、渲染、验证。
- **LLM 不许做**：直接生成 HTML、CSS、`style`、`class`、自定义颜色。

### 各 Skill 职责

各 skill 职责见各自 `SKILL.md`；`check.py` 自动发现所有 skill，无需维护中心清单。

**skill 间协作**：`kairos-serenity` 依赖 `kairos-x-scraper` 抓取源数据，但两者独立——scraper 只交付原始 JSONL，serenity 自己做全部提炼和分析。

### 输出目录约定

- 微信排版产物：`~/.wechat-typeset/<article-slug>/vNNN/`
- 视觉卡片产物：`~/.visual-generator/<topic-slug>/vNNN/`
- X 推文数据：`~/.kairos/x-scraper/<handle>/`（当月按天/历史月按月/历史年按年）
- Kairos 配置：`~/.kairos/kairos-x-scraper-config.json`、`~/.kairos/kairos-serenity-config.json`

输出目录全部使用 `Path.home()` 而非硬编码路径。

## Git 纪律

- 一次提交只含一个连贯任务，commit message 用 conventional 风格：`feat:` / `fix:` / `docs:` / `refactor:` / `chore:`
- 提交前跑 `python3 check.py` + 清理 `__pycache__`
- 不擅自回退用户已有的改动
