---
name: kairos-wechat-typeset
description: |
  把标准 Markdown 文章转换成适合微信公众号编辑器粘贴的极简黑白灰 HTML。

  触发场景：
  - “把这篇 md 排成公众号样式”
  - “把 Markdown 转成可直接贴进微信编辑器的 HTML”
  - “给公众号文章做兼容微信编辑器的排版”
  - “把 .md 文件输出成排版好的 html 文件”
metadata:
  version: "1.0"
---

# kairos-wechat-typeset

## Purpose / 目的

将标准 Markdown `.md` 文件转换为“公众号编辑器友好”的 HTML 文件，目标是：

- 直接切到微信公众号编辑器的 HTML 模式即可粘贴
- 样式以内联样式为主，尽量避免被微信重置后排版错乱
- 输出风格统一为黑白灰极简版式
- 保留文章的阅读层级、节奏和重点

## When to use / 何时使用

- 用户已经写好一篇 Markdown 文章，需要排成公众号版式
- 需要把文章交给微信编辑器，且希望样式尽量稳定
- 需要把 `.md` 文件落地成可预览、可复制的 `.html` 文件

## Input / 输入

一个标准 Markdown 文件路径，例如：

```text
/absolute/path/article.md
```

支持的常见 Markdown 结构：

- `# / ## / ###` 标题
- 普通段落
- 无序列表 / 有序列表
- 引用块 `>`
- 分割线 `---` / `***` / `<!--段落分割线-->`
- 粗体、斜体、删除线、行内代码、链接、图片
- 简单表格（会降级为更适合微信的段落行）
- 围栏代码块

额外约定：

- `## 01 标题`、`## 1. 标题`、`## 02｜标题` 这类结构会自动渲染成“大号灰色数字 + 下划线标题”
- `==需要强调的句子==` 会渲染成绿色虚线底边强调
- `> [!NOTE]`、`> [!WARNING]`、`> [!TIP]` 这类提示块会渲染成不同风格的信息框

## Output / 输出

输出一个 HTML 文件：

- 默认输出完整 HTML 文档，可直接浏览器打开预览
- `body` 内部内容可直接复制到微信公众号编辑器 HTML 模式
- 如果传入 `--fragment-only`，则只输出可粘贴的正文片段

## Core Workflow / 核心流程

1. 读取 Markdown 文件
如果文件包含 YAML frontmatter，会自动剥离，并优先读取 `title` 作为页面标题。

2. 解析常见 Markdown 结构
脚本会把标题、段落、列表、引用、分割线、图片、链接、代码块等转换为适合微信编辑器的块级结构。

3. 输出微信友好 HTML
核心约束：

- 只使用内联样式
- 块级内容优先输出为平铺的 `<p>` 标签
- 行内强调优先输出为 `<span>`
- 避免依赖 `<div> / <section> / <style>`

4. 最终检查
生成后建议：

- 在浏览器打开 HTML 文件快速预览
- 复制 `body` 内内容到微信公众号后台 HTML 模式
- 回到可视化模式检查图片、间距、强调样式是否保留

## Commands / 命令

基础用法：

```bash
python3 /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-wechat-typeset/scripts/render.py \
  --input /absolute/path/article.md \
  --output /absolute/path/article.html
```

仅输出可粘贴正文片段：

```bash
python3 /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-wechat-typeset/scripts/render.py \
  --input /absolute/path/article.md \
  --output /absolute/path/article.fragment.html \
  --fragment-only
```

## Style Rules / 样式规则

- 主标题：`22px`，黑色，加粗
- 正文：`16px`，深灰，`line-height: 1.7`
- 章节数字：`42px`，浅灰
- 章节标题：`16px`，黑色，加粗，底部细线
- 列表：用多个 `<p>` 模拟，不依赖 `<ul>/<li>`
- 引用块：浅灰背景 + 左边框
- 强调句：绿色虚线底边
- 最大内容宽度：`680px`

## Gotchas / 注意事项

- 为了避免无效 HTML 被浏览器或微信自动重写，渲染器默认输出“平铺的 `<p>` 块”，而不是嵌套 `<p>`。
- 微信编辑器对远程图片更友好；如果 Markdown 使用本地图片路径，最终是否可显示取决于粘贴环境。
- 复杂嵌套列表、复杂表格会被有意降级为更稳定的公众号段落结构。
- 如果输入中包含原始 HTML，脚本会按纯文本转义，而不是原样透传。

## Example / 示例

输入：

```md
# 一篇公众号文章

## 01 为什么这件事值得写

这是正文，其中 **重点句** 会被加粗，==核心观点== 会加虚线强调。

> [!NOTE]
> 这是一个提示框。

- 第一条
- 第二条
```

输出：

- 一个可直接预览的 `.html` 文件
- 文章保留黑白灰极简风格
- 章节标题自动转换成大数字样式
- 列表与引用在微信编辑器中更稳定
