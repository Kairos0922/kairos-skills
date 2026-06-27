# AGENTS.md

Kairos Skills 是一个高质量、可沉淀的个人 skill 集合。AI agent 在这里实现、重构、验证和文档化 skill，让仓库对人和未来的 agent 都保持可用、可扩展。

skill 有不同形态：有的是**确定性内容渲染型**（脚本锁定视觉，AI 只做编辑判断，如 kairos-wechat-typeset、kairos-visual-generator），有的是**对话/推理型**（通过对话产出高质量产物，如 kairos-loop）。不要假设所有 skill 都长一个样，也不要把一种形态的约束强加给另一种。

## Agent 起步顺序

1. 读本文件。
2. 读根 `README.md` 了解仓库总览。
3. 读目标 skill 的 `SKILL.md`（必读，机读指令）。
4. 编辑前看一眼现有目录结构和脚本，别急着造新结构。
5. 编辑前 `git status --short`，不要覆盖无关的用户改动。

## Skill 的唯一硬约束

每个 skill 是一个顶级目录，**只有两条必须遵守的规则**：

1. **有 `SKILL.md`**，且 YAML frontmatter 至少含 `name` 和 `description`（description 是触发依据，要写清"何时加载"）。
2. **自包含、可移植**：不硬编码 `/Users/...` 等私有绝对路径，不含密钥，不依赖跨 skill 的共享目录或私有上下文。

其余一切（README、scripts/、references/、themes/、assets/ 等）**按需添加**，不强制。一个 skill 该有什么结构，由它自己的形态决定。

## 质量准则（不是硬约束，但请遵循）

- skill 聚焦：把一个工作流做好，而不是什么都做一点。
- 稳定行为尽量沉淀到脚本或结构化配置，减少 LLM 即兴发挥——**对渲染型 skill 尤其重要**；推理型 skill 则把判断逻辑写进 SKILL.md 的清晰规则里。
- `SKILL.md` 保持精简，深度细节移到脚本或 `references/`。
- 渲染型 skill 的资产（字体、图片）必须本地化，不引外部 CDN，验证脚本随代码更新。
- 不为了"看起来规范"而过度设计：按当前真实规模做，能随规模长大即可。

## 验证

仓库根的 `check.py` 自动发现所有 skill 并验证：

```bash
python3 check.py          # 全量：基线检查 + 各 skill 的 validate.sh
python3 check.py --smoke  # 只做基线检查（frontmatter + 私有路径扫描）
```

基线检查对所有 skill 一视同仁（SKILL.md frontmatter 合法、无私有路径/密钥）。
如果一个 skill 需要更深的验证（编译脚本、跑渲染、校验 JSON），在它自己的目录下放一个 `validate.sh`，`check.py` 会自动调用。没有 `validate.sh` 的 skill 只跑基线检查即可——这对推理型 skill 完全正常。

提交前清掉缓存：

```bash
find . -type d -name __pycache__ -prune -exec rm -rf {} +
```

## 新增一个 Skill

1. 建顶级目录，短小稳定的全小写名称。
2. 写 `SKILL.md`（含 frontmatter）。其余文件按 skill 形态按需添加。
3. 如需深度验证，加 `validate.sh`。
4. 跑 `python3 check.py` 确认通过。

**不需要**改任何中心清单或 Makefile——`check.py` 会自动发现新目录。

## Git 纪律

- 一次提交只包含一个连贯任务的改动，不夹带无关变更。
- 不擅自回退用户改动。
- commit message 用简洁的 conventional 风格（`feat:` / `fix:` / `docs:` / `refactor:` / `chore:`）。
- 提交前扫一遍私有路径、密钥、过时引用和缓存文件。
