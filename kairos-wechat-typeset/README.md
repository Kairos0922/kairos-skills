<div align="center">
  <img src="https://img.shields.io/badge/wechat-公众号排版-07C160?style=flat-square&logo=wechat&logoColor=white" />
  <img src="https://img.shields.io/badge/theme-4套主题-111111?style=flat-square" />
  <img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" />
  <h1>kairos-wechat-typeset</h1>
  <p><b>Markdown → 微信公众号排版，每次结果都一样好看</b></p>
</div>

<br>

<p align="center"><sub>以下 4 张效果图使用同一篇文章（<code>fixtures/universal-showcase.md</code>）渲染，覆盖标题、正文、加粗、斜体、删除线、高亮、链接、内联代码、有序/无序/任务列表、代码块、表格、引用、提示块、图片、分隔线、引言、洞察、软列表、结尾注等全部组件，便于直观对比同一内容在不同主题下的表现。</sub></p>

<table>
<tr>
  <td align="center" width="50%">
    <img src="./assets/showcase/song-preview.png" width="260" alt="宋式美学" /><br>
    <b>宋式美学 · song</b><br>
    <sub>技术长文、方法论、书评</sub>
  </td>
  <td align="center" width="50%">
    <img src="./assets/showcase/wending-preview.png" width="260" alt="稳境白纸" /><br>
    <b>稳境白纸 · wending</b><br>
    <sub>个人成长、心理秩序、慢阅读</sub>
  </td>
</tr>
<tr>
  <td align="center" width="50%">
    <img src="./assets/showcase/tech-preview.png" width="260" alt="科技主题" /><br>
    <b>科技 · tech</b><br>
    <sub>AI 技术、工程实践、工具教程</sub>
  </td>
  <td align="center" width="50%">
    <img src="./assets/showcase/wisme-preview.png" width="260" alt="WISME 规范" /><br>
    <b>WISME 规范 · wisme</b><br>
    <sub>知识科普、研究报告、组件规范</sub>
  </td>
</tr>
</table>

<br>

## 30 秒上手

```bash
# 渲染一篇文章
python3 scripts/render.py --theme song --input article.md --output article.html

# 打开 article.html，复制内容粘贴到微信公众号编辑器
```

**输入**：Markdown 文件 → **输出**：可粘贴到微信公众号的 HTML

<br>

## 它是什么

一个确定性的微信排版系统。AI 只做编辑判断（结构、节奏、重点句），字号、颜色、字体、间距全部由代码和主题 JSON 决定。

```text
Markdown → LLM 编辑判断 → render.py 渲染 → verify 验证 → HTML 输出
```

**核心承诺**：同一输入 × 同一主题 = 相同输出。不漂移，不即兴发挥。

<br>

## 4 套主题

| 主题 | 风格 | 适合 |
|------|------|------|
| `song` | 暖纸 · 宋体 · 克制细线 | 技术长文、方法论、书评 |
| `wending` | 安静白纸 · 灰度规格 | 个人成长、心理秩序、慢阅读 |
| `tech` | 沉稳蓝 · 暗色代码 | AI 技术、工程实践、工具教程 |
| `wisme` | 黑字 · 红色短线 | 知识科普、研究报告、组件规范 |

<br>

## 质量门禁

```bash
python3 scripts/check_all.py --smoke    # 快速健康检查
python3 scripts/check_all.py            # 完整回归
```

验证项：无 `<style>` · 无 `class=` · heading 不跳级 · 连续 emphasis ≤ 2 · highlight ≤ 8% · 移动端无溢出

<br>

## 文档

| 文件 | 给谁看 |
|------|--------|
| [`CHEATSHEET.md`](./CHEATSHEET.md) | 所有人 · 一页速查 |
| [`SKILL.md`](./SKILL.md) | AI Agent · 完整工作流 |
| [`PRODUCT.md`](./PRODUCT.md) | 设计决策和产品边界 |
| [`references/anti-patterns.md`](./references/anti-patterns.md) | 25 条反模式 Bad/Fix |
| [`themes/README.md`](./themes/README.md) | 主题扩展指南 |

<br>

## License

MIT
