# Contributing to Kairos Skills

Kairos Skills 是一个确定性的 AI 内容生产工作流集合。贡献的目标是让 skill 更容易被人类和 AI agent 理解、运行、验证和扩展。

---

## 操作模型

- **Owner**：定义优先级、产品方向和美学标准
- **AI Agent**：实现、重构、文档化、验证和清理
- **贡献者**：确保 skill 在 owner 的机器之外也能用，不依赖私有上下文

---

## Skill 目录合约

每个 skill 目录必须自包含，不依赖私有路径。

### 必需文件

| 文件 | 用途 |
|------|------|
| `SKILL.md` | 机器指令（YAML frontmatter + `name` + `description`） |
| `README.md` | 人类文档（用途、前置条件、用法、验证、维护） |

### 推荐文件

| 文件 | 用途 |
|------|------|
| `CHEATSHEET.md` | 一页速查 |
| `PRODUCT.md` | 设计决策和产品边界 |
| `scripts/` | 确定性辅助脚本 |
| `references/` | 参考规范和方法论 |
| `fixtures/` | 稳定测试输入 |
| `goldens/` | 视觉母版 |

### 不允许

- 私有路径（`/Users/...`、`/tmp/...`）
- 密钥、token、密码
- 运行时缓存（`__pycache__`、`.DS_Store`）
- 对外部 API 的硬依赖

---

## 新增 Skill

1. 创建顶级目录，短小稳定的全小写名称
2. 编写 `SKILL.md`（含 YAML frontmatter）和 `README.md`
3. 在根目录 `skills.json` 中注册
4. 编写验证命令并确保通过
5. 更新根 `README.md` 的 skill 列表

---

## 更新 Skill

1. 读取目标 skill 的 `SKILL.md`、`README.md` 和相关脚本
2. 保留现有工作流契约，除非任务明确要求修改
3. 文档和验证命令随代码一起更新
4. 更新 `skills.json`（如适用）
5. 运行验证命令
6. 清除生成的缓存

---

## 文档标准

- 根目录文档描述整个仓库
- Skill 文档放在 skill 目录内
- 使用相对路径命令（如 `python3 scripts/render.py`）
- 不要引入私有路径、本地主机名、密钥或过时的引用
- 文档要简洁，告诉读者"去哪里看下一步"

---

## 提交前检查

```bash
# 检查私有路径
rg -n "/Users/|/private/|/tmp/|API_KEY|SECRET|TOKEN|PASSWORD" .

# 检查缓存文件
find . -type d -name __pycache__ -o -name ".DS_Store" -o -name "*.pyc" -o -name ".env"

# 检查 JSON 语法
python3 -m json.tool skills.json >/dev/null
```

---

## 提交风格

使用简洁的 conventional-style 消息：

| 前缀 | 用途 |
|------|------|
| `feat:` | 新增功能 |
| `fix:` | 修复问题 |
| `docs:` | 文档变更 |
| `refactor:` | 重构（不改变行为） |
| `chore:` | 清理、缓存、杂项 |

示例：
- `feat: add anti-patterns reference for kairos-wechat-typeset`
- `fix: correct font fallback chain in tech theme`
- `docs: redesign project README for open-source readability`
