<div align="center">
  <img src="https://img.shields.io/badge/visual-多风格视觉平台-111111?style=flat-square" />
  <img src="https://img.shields.io/badge/styles-3套系统-002FA7?style=flat-square" />
  <img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" />
  <h1>kairos-visual-generator</h1>
  <p><b>主题 → 高质量视觉卡片/海报</b></p>
</div>

<br>

<img src="./assets/showcase/cards-preview.png" width="100%" alt="风格对比" />

<br>

## 30 秒上手

```bash
# 风格路由测试
python3 scripts/select_style.py '帮我做一张小红书封面，主题是用户增长飞轮'

# 查看隐喻建议
python3 scripts/select_metaphor.py --title "用户转化漏斗优化" --usage "信息图"
```

然后告诉 AI agent："帮我用这个主题做一张封面"，它会引导你完成。

<br>

## 它是什么

一个确定性的多风格视觉生成平台。AI 做编辑判断，视觉系统由代码和契约决定。

```text
用户主题 → Intake Engine → 风格路由 → Visual Brief → 确定性渲染 → QA → 输出
```

**核心承诺**：三套视觉系统，风格即插件，不允许自定义颜色，保护美学下限。

<br>

## 三套视觉系统

| 系统 | 风格 | 适合 |
|------|------|------|
| **Editorial Magazine** | 衬线 · 墨水 · 杂志结构 | 观点、文化、人物、叙事 |
| **Swiss Consulting** | Inter · accent · 网格 | 流程、方法、矩阵、数据 |
| **Mondrian / De Stijl** | 五原色 · 色块网格 · 文字即结构 | 设计、艺术、建筑、创意 |

<br>

## 设计原则

1. **质量第一**：质量 > 稳定 > 效率
2. **风格即插件**：新增风格 = 新增目录，不改核心代码
3. **确定性优先**：能用代码验证的不用 AI 猜测
4. **最小输入**：用户只需提供主题和用途

<br>

## 质量门禁

```bash
python3 scripts/verify_design_system.py    # 设计系统验证
python3 scripts/select_style.py '测试输入'  # 风格路由测试
```

<br>

## 文档

| 文件 | 给谁看 |
|------|--------|
| [`CHEATSHEET.md`](./CHEATSHEET.md) | 所有人 · 一页速查 |
| [`SKILL.md`](./SKILL.md) | AI Agent · 完整工作流 |
| [`PRODUCT.md`](./PRODUCT.md) | 设计决策和产品边界 |
| [`styles/METHODOLOGY.md`](./styles/METHODOLOGY.md) | 新增风格时 |

<br>

## License

MIT
