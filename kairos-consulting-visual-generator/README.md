<div align="center">
  <h1>kairos-consulting-visual-generator</h1>
  <p><b>让 AI 帮你做咨询公司级别的商业卡片</b></p>
</div>

---

## 什么是 Agent Harness Engineering？

你让 AI 帮你做一张封面图，它给你一个"标题放中间 + 渐变背景 + emoji"——这就是没有约束的 AI。

**Agent Harness Engineering（AI 约束工程）**是给 AI 套上缰绳：

| 没有约束的 AI | 有约束的 AI（Harness） |
|--------------|----------------------|
| 每次风格都不一样 | 只有 2 套视觉系统、12 套预设 |
| 颜色乱配 | 只能从预设里选，不允许自定义 |
| 模块堆满画面 | 有密度上限和留白规则 |
| 像 PPT 模板 | 像麦肯锡报告封面 |

kairos-consulting-visual-generator 就是一个 Harness——它告诉 AI："你只能用 Editorial 或 Swiss 两套风格，12 套颜色预设，11 种版式骨架。不允许自由发挥。"

---

## 效果展示

### 4 种风格对比

![咨询卡片预览](./assets/showcase/cards-preview.png)

| 卡片 | 风格 | 特点 |
|------|------|------|
| 增长的底层逻辑 | Editorial · Ink Classic | 衬线大字 + 暖纸 + 墨蓝点缀 |
| 用户留存率 87% | Swiss · IKB | 无衬线 + 克莱因蓝 + 数据大字报 |
| 好的产品让用户忘记技术 | Kami Paper | 温纸 + 墨蓝 + 书卷气 |
| 竞争风险倍增 3× | Swiss · Safety Orange | 安全橙 + 数据 + 风险感 |

---

## 它能做什么

把一个商业主题，变成一张精致的视觉卡片。

**输入**：一个主题词（如"增长策略"）
**输出**：一张可以直接发到社交媒体的卡片图

```bash
# 检查输入是否足够
python3 scripts/select_metaphor.py --check-intake --title "增长" --usage "封面"

# 查看隐喻建议
python3 scripts/select_metaphor.py --title "用户转化漏斗优化" --usage "信息图"
```

---

## 两套视觉系统

| 系统 | 风格 | 适合 |
|------|------|------|
| **Editorial Magazine** | 衬线 + 墨水 + 杂志结构 | 观点、文化、人物、叙事 |
| **Swiss Consulting** | Inter + 一种 accent + 网格 | 流程、方法、矩阵、数据 |

**核心原则**：不允许自定义颜色。12 套预设是经过验证的上限。

---

## 12 套主题预设

### Editorial（8 套）

| 预设 | 适合 |
|------|------|
| Ink Classic | 通用默认、商业发布 |
| Indigo Porcelain | 科技、AI、研究 |
| Forest Ink | 自然、可持续 |
| Kraft Paper | 怀旧、人文 |
| Dune | 艺术、设计 |
| Midnight Ink | 游戏、夜景、影调 |
| Graphite Red | 风险、治理 |
| Olive Editorial | 组织、长期主义 |
| Kami Paper | 印刷感中文卡片 |

### Swiss（4 套）

| 预设 | 适合 |
|------|------|
| IKB 克莱因蓝 | 通用 Swiss 默认 |
| Lemon 柠檬黄 | 年轻、零售 |
| Lemon Green 柠檬绿 | 生态、健康 |
| Safety Orange 安全橙 | 警示、新闻 |

---

## 快速开始

### 前置条件

- Python 3.8+
- 一个商业主题

### 3 步上手

```bash
# 1. 进入 skill 目录
cd kairos-consulting-visual-generator

# 2. 检查输入是否足够
python3 scripts/select_metaphor.py --check-intake --title "增长策略" --usage "封面"

# 3. 根据 AI agent 的指引生成卡片
```

### 健康检查

```bash
python3 scripts/verify_design_system.py
```

---

## 它不是什么

- ❌ 不是 Canva（不能拖拽编辑，只能通过 AI agent 生成）
- ❌ 不是数据可视化工具（不做图表，只做卡片）
- ❌ 不允许自定义颜色（保护美学一致性）
- ❌ 不做卡通/少女/Y2K 风格（和两套视觉系统冲突）

---

## 文档导航

| 文件 | 给谁看 | 说明 |
|------|--------|------|
| `CHEATSHEET.md` | 所有人 | 一页速查，日常操作看这个 |
| `SKILL.md` | AI Agent | 完整的工作流和规则 |
| `PRODUCT.md` | 想了解"为什么"的人 | 设计决策和产品边界 |
| `references/design_system.md` | 开发者 | 字体、颜色、网格、版式 |
| `references/consulting_visual_methodology.md` | 开发者 | 工作流、隐喻语法、QA |

---

## 许可证

MIT
