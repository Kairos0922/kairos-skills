<div align="center">
  <img src="https://img.shields.io/badge/wechat-公众号排版-07C160?style=flat-square&logo=wechat&logoColor=white" />
  <img src="https://img.shields.io/badge/theme-4套主题-111111?style=flat-square" />
  <img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" />
  <h1>kairos-wechat-typeset</h1>
  <p><b>Markdown → 微信公众号排版，每次结果都一样好看</b></p>
</div>

<br>

<table>
<tr>
  <td align="center" width="50%">
    <img src="./assets/showcase/song-preview.png" width="260" alt="宋式美学" /><br>
    <b>宋式美学 · song</b><br>
    <sub>技术长文、方法论、书评</sub>
  </td>
  <td align="center" width="50%">
    <img src="./assets/showcase/tech-preview.png" width="260" alt="科技主题" /><br>
    <b>科技 · tech</b><br>
    <sub>AI 技术、工程实践、工具教程</sub>
  </td>
</tr>
</table>

<br>

## 用法

```bash
# 渲染一篇文章
python3 scripts/render.py --theme song --input article.md --output article.html

# 带 Web 字体（本地预览用）
python3 scripts/render.py --theme song --input article.md --output article.html --web-fonts
```

**输入**：Markdown 文件 → **输出**：可粘贴到微信公众号的 HTML

<br>

## 4 套主题

| 主题 | 风格 | 适合 |
|------|------|------|
| `song` | 暖纸 · 宋体 · 克制细线 | 技术长文、方法论、书评 |
| `wending` | 安静白纸 · 灰度规格 | 个人成长、心理秩序、慢阅读 |
| `tech` | 沉稳蓝 · 暗色代码 · accent bar | AI 技术、工程实践、工具教程 |
| `wisme` | 黑字 · 红色短线 · 灰色表格 | 知识科普、研究报告、组件规范 |

<br>

## 核心机制

```text
Markdown → LLM 编辑判断 → Renderer 渲染 → Verify 验证 → HTML 输出
              ↑ 语义组件            ↑ 主题 JSON        ↑ 硬规则
              (不确定)              (确定)             (确定)
```

- **LLM 做**：结构、标题层级、重点句、引用、列表、步骤
- **代码做**：字号、颜色、字体、间距、验证、渲染
- **LLM 不许做**：生成 HTML、CSS、style、class、自定义颜色

<br>

## 质量门禁

```bash
python3 scripts/check_all.py --smoke    # 快速健康检查
python3 scripts/check_all.py            # 完整回归
python3 scripts/verify.py --input out.html  # 验证单个文件
```

验证项：无 `<style>` · 无 `class=` · heading 不跳级 · 连续 emphasis ≤ 2 · highlight ≤ 8% · 移动端无溢出

<br>

## 文档

| 文件 | 给谁看 |
|------|--------|
| [`CHEATSHEET.md`](./CHEATSHEET.md) | 所有人 · 一页速查 |
| [`SKILL.md`](./SKILL.md) | AI Agent · 完整工作流 |
| [`PRODUCT.md`](./PRODUCT.md) | 了解"为什么" |
| [`references/anti-patterns.md`](./references/anti-patterns.md) | 21 条反模式 Bad/Fix |
| [`references/category-routing.md`](./references/category-routing.md) | 文章类型 → 推荐策略 |

<br>

## License

MIT
