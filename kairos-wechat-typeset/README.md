# kairos-wechat-typeset

`kairos-wechat-typeset` 用来把标准 Markdown 文章转换成更适合微信公众号编辑器粘贴的 HTML。

它的核心目标很直接：

- 样式尽量不被微信编辑器打散
- 输出黑白灰极简风格
- 直接生成可预览、可复制的 HTML 文件
- 中文以宋体为主，英文和数字有独立的衬线搭配

## 60 秒上手

```bash
python3 /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-wechat-typeset/scripts/render.py \
  --input /absolute/path/article.md \
  --output /absolute/path/article.html
```

如果只想拿可粘贴到微信编辑器 HTML 模式里的正文片段：

```bash
python3 /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-wechat-typeset/scripts/render.py \
  --input /absolute/path/article.md \
  --output /absolute/path/article.fragment.html \
  --fragment-only
```

## 设计原则

### 1. 兼容性优先

- 所有样式都写在标签的 `style` 属性里
- 不使用外部 CSS，也不输出 `<style>` 标签
- 块级结构以平铺的 `<p>` 为主
- 行内强调优先使用 `<span>`

说明：

严格的嵌套 `<p>` 在 HTML 里是无效结构，浏览器和微信编辑器都可能自动改写。为了让最终粘贴效果更稳定，渲染器采用“平铺块 + 重复基础样式”的方式来模拟统一容器。

### 2. 视觉规范

- 主标题：`22px`
- 正文/小标题/列表：`16px`
- 章节数字：`42px`
- 中文字体：优先 `Songti SC / STSong / Noto Serif CJK SC`
- 英文与数字：自动用 `Iowan Old Style / Baskerville / Georgia / Times New Roman` 一类衬线字体做平衡
- 正文颜色：`#333`
- 标题颜色：`#000`
- 引用/辅助信息：`#555`
- 分割与浅底：`#e0e0e0`、`#f5f5f5`、`#f9f9f9`
- 重点划线：`border-bottom: 1px dashed #07C160`
- 最大宽度：`680px`
- 行高：`1.7`
- 默认左对齐

## 支持的 Markdown 能力

- `# / ## / ###` 标题
- 段落
- 无序列表 / 有序列表
- 引用块
- 分割线 `---` / `***` / `<!--段落分割线-->`
- 粗体、斜体、删除线、行内代码
- 链接、图片
- 围栏代码块
- 简单表格

当前列表、代码块、表格会做“公众号友好”的再设计：

- 列表：改为更轻的悬挂缩进和更克制的标记符号
- 代码块：改为编辑部注释感更强的细线标题 + 浅底代码卡片
- 表格：不直接模拟原生表格，而是转成更稳定的卡片式信息块

## 额外语法约定

### 章节标题

以下标题会自动转成“章节数字 + 下划线标题”：

```md
## 01 为什么这段值得单独展开
## 1. 为什么这段值得单独展开
## 02｜为什么这段值得单独展开
```

### 虚线强调

使用 `==...==` 标记需要重点划线的内容：

```md
这是正文，==这一句会被渲染成绿色虚线底边==。
```

### 提示框

支持常见提示块写法：

```md
> [!NOTE]
> 这是备注信息

> [!TIP]
> 这是提示信息

> [!WARNING]
> 这是警告信息
```

## 微信后台使用方式

1. 运行脚本生成 `.html`
2. 用浏览器打开快速预览，确认层级、间距、图片和强调样式
3. 进入微信公众号后台，新建图文消息
4. 切到编辑器右上角的 HTML 模式
5. 粘贴生成文件中的 `body` 内容，或直接使用 `--fragment-only` 生成的片段
6. 回到可视化模式做最终检查

## 示例输入

仓库内附了一个示例文件：

[`examples/demo.md`](./examples/demo.md)

你可以直接运行：

```bash
python3 /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-wechat-typeset/scripts/render.py \
  --input /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-wechat-typeset/examples/demo.md \
  --output /Users/kenpetex/Documents/GitHub/kairos-skills/kairos-wechat-typeset/examples/demo.html
```

## 限制说明

- 复杂嵌套列表会自动降级为更稳定的段落列表
- 表格会转换成更适合公众号的“行文本”结构，而不是原生 `<table>`
- 原始 HTML 会被转义，避免把不稳定的标签直接带进微信编辑器
- 本地图片路径不会自动上传到微信素材库，建议使用可访问的远程地址
