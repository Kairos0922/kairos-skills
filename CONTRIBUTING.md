# Contributing to Kairos Skills

Kairos Skills 是一个确定性的 AI 内容生产工作流集合。贡献的目标是让 skill 更容易被人类和 AI agent 理解、运行、验证和扩展。

---

## 操作模型

- **Owner**：定义优先级、产品方向和美学标准
- **AI Agent**：实现、重构、文档化、验证和清理
- **贡献者**：确保 skill 在 owner 的机器之外也能用，不依赖私有上下文

---

## 开发环境

### 前置条件

- Python 3.8+
- Git

### 快速验证

```bash
# 一键检查
make install

# 运行所有测试
make test

# 重新生成 golden 文件
make showcase

# 清除缓存
make clean
```

### 手动验证

```bash
# 微信排版 skill
cd kairos-wechat-typeset
python3 scripts/check_all.py --smoke

# 咨询视觉 skill
cd kairos-visual-generator
python3 scripts/verify_design_system.py

# JSON 语法
python3 -m json.tool skills.json > /dev/null
```

---

## Skill 目录合约

详见 `AGENTS.md` 中的 "Skill Directory Contract"。

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

## 文档地图

| 文件 | 给谁看 | 作用 |
|------|--------|------|
| 根 `README.md` | 用户 | 项目总览 |
| `AGENTS.md` | AI Agent | 仓库级规则（权威来源） |
| `CONTRIBUTING.md` | 贡献者 | 贡献流程 |
| Skill `README.md` | 用户 | Skill 介绍和用法 |
| Skill `SKILL.md` | AI Agent | 完整工作流指令 |
| Skill `CHEATSHEET.md` | 所有人 | 一页速查 |
| Skill `PRODUCT.md` | 贡献者 | 设计决策 |
| Skill `references/` | Agent + 贡献者 | 详细规范 |

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
