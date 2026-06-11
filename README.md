<div align="center">
  <h1>Kairos Skills</h1>
  <p><b>Agent Harness Engineering — 给 AI 套上缰绳</b></p>
  <p>让 AI agent 输出稳定、高级、可重复的内容产物，不靠运气靠系统。</p>
</div>

---

## 什么是 Agent Harness Engineering？

**一句话**：给 AI 套上缰绳，让它按规矩办事，而不是乱来。

### 没有 Harness 的 AI

你让 AI 帮你排版一篇文章：
- 第一次：挺好看
- 第二次：怎么变丑了？
- 第三次：风格又不一样了

因为 AI 每次都在"即兴发挥"。它没有固定标准，每次从零猜。

### 有 Harness 的 AI

给 AI 套上 Kairos Harness：
- 只能用 4 套主题，不允许自己发明颜色
- 只能用 6 种语义组件，不允许随意加装饰
- 输出必须通过验证脚本检查
- 每次结果都一样

**这就是 Agent Harness Engineering**——用确定性的脚本、主题契约和验证规则，约束 AI 的输出质量。

### 效果对比

| 没有 Harness | 有 Harness（Kairos） |
|-------------|---------------------|
| 每次输出都不一样 | 每次输出都一样 |
| 颜色乱配 | 只能从预设选 |
| 样式靠运气 | 样式靠系统 |
| 出错了不知道怎么改 | 有验证脚本自动检查 |
| 像 AI 即兴拼凑 | 像人工精修的作品 |

---

## 两个 Skill

### [kairos-wechat-typeset](./kairos-wechat-typeset/) — 微信公众号排版

把 Markdown 文章转换成微信公众号编辑器可粘贴的内联 HTML。

- 4 套主题（宋式美学 / 稳境白纸 / 科技 / WISME 规范）
- 语义组件系统（lead / insight / pullquote / figure / soft-list / closing-note）
- 确定性渲染：同一输入 × 同一主题 = 相同输出
- Web 字体可选加载（本地预览用）
- 版本化输出（`~/.wechat-typeset/<slug>/vNNN/`）

```bash
cd kairos-wechat-typeset
python3 scripts/render.py --theme song --input article.md --output article.html --verify
```

### [kairos-consulting-visual-generator](./kairos-consulting-visual-generator/) — 商业视觉卡片

把商业主题转化为有隐喻、有克制、有杂志感的视觉卡片。

- 12 套主题预设（8 Editorial + 4 Swiss）
- 11 个版式骨架（E01-E03 + S01-S08）
- 2 种视觉系统（Editorial Magazine / Swiss Consulting）
- 5 种画幅比例（4:5 / 3:4 / 1:1 / 5:2 / 16:9）
- Intake Gate 信息校验

```bash
cd kairos-consulting-visual-generator
python3 scripts/select_metaphor.py --title "增长" --usage "封面"
```

---

## 快速开始

### 前置条件

- Python 3.8+
- Git
- 支持本地 skill 的 AI coding agent

### 安装

```bash
git clone https://github.com/Kairos0922/kairos-skills.git
cd kairos-skills
```

### AI Agent 使用

1. 读 [`AGENTS.md`](./AGENTS.md) — 仓库约定和工具偏好
2. 读 [`skills.json`](./skills.json) — 机器可读的技能清单
3. 读目标 skill 的 `SKILL.md` 和 `README.md`
4. 按 `CHEATSHEET.md` 快速操作

### 验证

```bash
# 微信排版 skill
cd kairos-wechat-typeset
python3 scripts/check_all.py --smoke

# 咨询视觉 skill
cd kairos-consulting-visual-generator
python3 scripts/verify_design_system.py
```

---

## 项目结构

```text
kairos-skills/
├── README.md                              # 本文件
├── AGENTS.md                              # Agent 操作规范
├── CONTRIBUTING.md                        # 贡献指南
├── skills.json                            # 机器可读技能清单
├── LICENSE                                # MIT
│
├── kairos-wechat-typeset/                 # 微信公众号排版
│   ├── SKILL.md                           # 机器指令
│   ├── README.md                          # 人类文档
│   ├── CHEATSHEET.md                      # 一页速查
│   ├── PRODUCT.md                         # 设计决策
│   ├── COMPONENTS.md                      # 语义组件契约
│   ├── DESIGN.md                          # 设计架构
│   ├── references/                        # 参考规范
│   │   ├── anti-patterns.md               # 反模式 + Bad/Fix 对照
│   │   ├── category-routing.md            # 文章类型 → 推荐策略
│   │   └── layout-recipes.md              # 编号版式骨架
│   ├── themes/                            # 主题系统
│   │   ├── registry.json                  # 主题索引
│   │   ├── METHODOLOGY.md                 # 扩展方法论
│   │   ├── song.json / song/              # 宋式美学
│   │   ├── wending.json / wending/        # 稳境白纸
│   │   ├── tech.json / tech/              # 科技
│   │   └── wisme.json / wisme/            # WISME 规范
│   ├── scripts/                           # 确定性脚本
│   ├── renderer/                          # 渲染器
│   ├── verify/                            # 验证器
│   ├── fixtures/                          # 测试输入
│   └── goldens/                           # 视觉母版
│
└── kairos-consulting-visual-generator/    # 商业视觉卡片
    ├── SKILL.md                           # 机器指令
    ├── README.md                          # 人类文档
    ├── CHEATSHEET.md                      # 一页速查
    ├── PRODUCT.md                         # 设计决策
    ├── references/                        # 设计规范
    │   ├── design_system.md               # 字体、颜色、网格、版式
    │   └── consulting_visual_methodology.md # 工作流、隐喻、QA
    └── scripts/                           # 辅助脚本
```

---

## 设计原则

1. **确定性优先**：脚本决定视觉，AI 只做编辑判断
2. **美学保护优先于用户自由**：不允许自定义颜色、不允许即兴写样式
3. **反模式驱动**：每条规则都来自真实踩坑，Bad/Fix 对照比正向规范更有效
4. **分层规范加载**：按任务复杂度读取不同深度的规范，不每次加载全部
5. **自包含**：每个 skill 目录独立，不依赖私有路径或外部服务

---

## 贡献

欢迎贡献。详见 [`CONTRIBUTING.md`](./CONTRIBUTING.md)。

核心要求：
- 新增 skill 必须有 `SKILL.md` + `README.md`
- 修改 skill 必须更新 `skills.json` 和验证命令
- 提交前运行验证，清除 `__pycache__`
- 不要引入私有路径、密钥或外部依赖

---

## 许可证

MIT. See [LICENSE](./LICENSE).
