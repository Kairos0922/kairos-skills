<div align="center">
  <img src="https://img.shields.io/badge/visual-商业卡片-111111?style=flat-square" />
  <img src="https://img.shields.io/badge/themes-12套预设-002FA7?style=flat-square" />
  <img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" />
  <h1>kairos-consulting-visual-generator</h1>
  <p><b>商业主题 → 杂志感视觉卡片</b></p>
</div>

<br>

<img src="./assets/showcase/cards-preview.png" width="100%" alt="4 种风格对比" />

<br>

## 30 秒上手

```bash
# 检查输入是否足够
python3 scripts/select_metaphor.py --check-intake --title "增长" --usage "封面"

# 查看隐喻建议
python3 scripts/select_metaphor.py --title "用户转化漏斗优化" --usage "信息图"
```

然后告诉 AI agent："帮我用这个主题做一张封面"，它会引导你完成。

<br>

## 它是什么

一个确定性的商业视觉生成系统。AI 做需求理解和隐喻选择，主题预设、版式骨架、验证规则由代码控制。

```text
用户主题 → LLM 需求理解 → LLM 隐喻选择 → 设计规范约束 → 渲染输出
```

**核心承诺**：12 套预设 + 11 个版式骨架，不允许自定义颜色，保护美学下限。

<br>

## 两套视觉系统

| 系统 | 风格 | 适合 |
|------|------|------|
| **Editorial Magazine** | 衬线 · 墨水 · 杂志结构 | 观点、文化、人物、叙事 |
| **Swiss Consulting** | Inter · accent · 网格 | 流程、方法、矩阵、数据 |

<br>

## 12 套预设

| Editorial | Swiss |
|-----------|-------|
| Ink Classic · Indigo Porcelain · Forest Ink · Kraft Paper · Dune · Midnight Ink · Graphite Red · Olive Editorial · Kami Paper | IKB 克莱因蓝 · Lemon · Lemon Green · Safety Orange |

<br>

## 画幅

`4:5` · `3:4` · `1:1` · `5:2` · `16:9`

<br>

## 文档

| 文件 | 给谁看 |
|------|--------|
| [`CHEATSHEET.md`](./CHEATSHEET.md) | 所有人 · 一页速查 |
| [`SKILL.md`](./SKILL.md) | AI Agent · 完整工作流 |
| [`PRODUCT.md`](./PRODUCT.md) | 了解"为什么" |
| [`references/design_system.md`](./references/design_system.md) | 字体、颜色、网格、版式 |

<br>

## License

MIT
