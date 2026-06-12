# kairos-consulting-visual-generator · Cheatsheet

一页速查。完整规范见 `SKILL.md` 和 `references/design_system.md`。

---

## 两套视觉系统

| 系统 | 特征 | 适合 |
|------|------|------|
| **Editorial Magazine** | serif + 墨水 + 杂志结构 + 大留白 | 观点、文化、组织、人物、叙事 |
| **Swiss Consulting** | Inter + 一种 accent + 网格 + 发丝线 | 流程、方法、矩阵、系统、数据 |

选择规则：强调观点 → Editorial；强调流程/数据 → Swiss。

---

## 12 套主题预设

### Editorial（8 套）

| 预设 | 色调 | 适合 |
|------|------|------|
| Ink Classic | 暖白 + 墨黑 | 通用默认 |
| Indigo Porcelain | 瓷白 + 深蓝 | 科技 / AI |
| Forest Ink | 深橄榄 + 暖纸 | 自然 / 可持续 |
| Kraft Paper | 牛皮纸 + 深棕 | 怀旧 / 人文 |
| Dune | 暖沙 + 深褐 | 艺术 / 设计 |
| Midnight Ink | 暗黑 + 金辉 | 游戏 / 夜景 / 影调 |
| Graphite Red | 炭黑 + 红 | 风险 / 治理 |
| Olive Editorial | 深橄榄 + 暖灰 | 组织 / 长期主义 |
| Kami Paper | 暖纸 + 墨蓝 | 印刷感中文卡片 |

### Swiss（4 套）

| 预设 | 锚点色 | 适合 |
|------|--------|------|
| IKB | 克莱因蓝 `#002FA7` | 通用 Swiss 默认 |
| Lemon | 柠檬黄 `#FFD500` | 年轻 / 零售 |
| Lemon Green | 柠檬绿 `#C5E803` | 生态 / 健康 |
| Safety Orange | 安全橙 `#FF6B35` | 警示 / 新闻 |

规则：一张卡片只用一套预设。Accent 色覆盖不超过 8% 画布。

---

## 5 种画幅比例

| 比例 | 尺寸 | 适合 |
|------|------|------|
| `4:5` | 1080×1350 | 小红书 / Instagram |
| `3:4` | 1080×1440 | 小红书竖版 |
| `1:1` | 1080×1080 | 公众号分享卡 / 头像 |
| `5:2` | 1500×600 | 公众号头图 / Banner |
| `16:9` | 1600×900 | PPT 封面 / 报告 |

---

## 11 个版式骨架

### Editorial（3 个）

| 编号 | 名称 | 适合 |
|------|------|------|
| E01 | Hero Thesis | 文章洞察 / 思想领导力 |
| E02 | Magazine Feature | 杂志专题 / 人物故事 |
| E03 | Split Tension | 对比张力 / 转型叙事 |

### Swiss（8 个）

| 编号 | 名称 | 适合 |
|------|------|------|
| S01 | Swiss Mechanism | 框架 / 机制 / 方法论 |
| S02 | Flow Ribbon | 流程 / 链路 / 管线 |
| S03 | Matrix Spotlight | 矩阵 / 定位 / 竞争格局 |
| S04 | KPI Editorial | 数据大字报 / 关键指标 |
| S05 | Executive Ladder | 阶梯 / 升级 / 层级 |
| S06 | Architecture Stack | 架构 / 分层 / 底座 |
| S07 | Annotated Field | 标注图 / 产品拆解 |
| S08 | Evidence Ladder | 证据墙 / 数据支撑 |

---

## 字体系统

```css
--font-display-zh: "Noto Sans SC", "PingFang SC", sans-serif;
--font-text-zh: "Noto Sans SC", "PingFang SC", sans-serif;
--font-en: "Inter", "Helvetica Neue", sans-serif;
--font-serif: "Noto Serif SC", "Songti SC", Georgia, serif;
```

规则：
- 越大越细：56px 以上 display weight <= 600
- 大号中文不用 `font-weight: 700`
- 中英混排用独立 span，英文用 `--font-en`

---

## 内容密度

| 类型 | 内容原子 | 模块数 |
|------|----------|--------|
| Cover | 1 主句 + 2-3 锚点 + 1 结论 | 0-1 |
| Light Card | 1 主句 + 3-4 信息点 | 3-4 |
| Standard Infographic | 1 中心结构 + 4-6 原子 + 1-2 结论 | 4-6 |
| Deep Analysis | 1 中心结构 + 5-7 原子 + 变量/约束 | 5-7 |

---

## Intake 追问优先级

1. **用途**：封面 / 信息图 / 流程图 / 矩阵图？
2. **画幅**：4:5 / 3:4 / 1:1 / 5:2 / 16:9？
3. **受众和场景**：想表达什么情绪？

---

## 验证

```bash
python3 scripts/verify_design_system.py
python3 scripts/select_metaphor.py --check-intake --title "增长" --usage "封面"
python3 scripts/select_metaphor.py --title "风险治理体系" --usage "商业报告封面"
```

---

## 交付前 5 秒自检

1. 只有一个主隐喻吗？（多个 → 砍掉，只留最强的）
2. 文字经过重构吗？（只是普通标题 → 加隐喻融合）
3. 颜色克制吗？（超过 1 个 accent → 砍掉）
4. 模块有具体内容吗？（空泛套话 → 补充真实信息）
5. 像杂志卡片，还是像 PPT 模板？（后者 → 检查反模式）
