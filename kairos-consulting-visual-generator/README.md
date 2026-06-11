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

## 两套视觉系统

<table>
<tr>
  <td align="center" width="50%">
    <b>Editorial Magazine</b><br>
    <sub>衬线 · 墨水 · 杂志结构</sub><br>
    <sub>观点、文化、人物、叙事</sub>
  </td>
  <td align="center" width="50%">
    <b>Swiss Consulting</b><br>
    <sub>Inter · accent · 网格</sub><br>
    <sub>流程、方法、矩阵、数据</sub>
  </td>
</tr>
</table>

<br>

## 12 套预设

<table>
<tr>
  <td><b>Editorial</b></td>
  <td>Ink Classic · Indigo Porcelain · Forest Ink · Kraft Paper · Dune · Midnight Ink · Graphite Red · Olive Editorial · Kami Paper</td>
</tr>
<tr>
  <td><b>Swiss</b></td>
  <td>IKB 克莱因蓝 · Lemon 柠檬黄 · Lemon Green · Safety Orange</td>
</tr>
</table>

<br>

## 用法

```bash
# 检查输入是否足够
python3 scripts/select_metaphor.py --check-intake --title "增长" --usage "封面"

# 查看隐喻建议
python3 scripts/select_metaphor.py --title "用户转化漏斗优化" --usage "信息图"
```

<br>

## 核心机制

```text
用户主题 → LLM 需求理解 → LLM 隐喻选择 → LLM 标题重构 → 渲染输出
             ↑ Intake Gate      ↑ 脚本辅助        ↑ 设计规范
             (不确定)            (半确定)          (确定)
```

- **LLM 做**：需求理解、隐喻选择、标题重构、内容架构
- **代码做**：主题预设、版式骨架、验证、度量检查
- **硬规则**：不允许自定义颜色 · 只允许一个 accent · 不允许模块堆叠

<br>

## 画幅

| 比例 | 尺寸 | 适合 |
|------|------|------|
| `4:5` | 1080×1350 | 小红书 / Instagram |
| `3:4` | 1080×1440 | 小红书竖版 |
| `1:1` | 1080×1080 | 公众号分享卡 |
| `5:2` | 1500×600 | 公众号头图 |
| `16:9` | 1600×900 | PPT 封面 / 报告 |

<br>

## 验证

```bash
python3 scripts/verify_design_system.py
```

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
