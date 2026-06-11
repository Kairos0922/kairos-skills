<div align="center">
  <h1>kairos-wechat-typeset</h1>
  <p><b>让 AI 帮你排版公众号文章，每次结果都一样好看</b></p>
</div>

---

## 什么是 Agent Harness Engineering？

你可能听过"AI 写代码"、"AI 生成内容"。但你有没有发现一个问题：

> **AI 每次生成的东西都不一样。**

你让 AI 帮你排版一篇文章，第一次可能很好看，第二次就变丑了。为什么？因为 AI 每次都在"即兴发挥"——它没有一个固定的标准，每次都是从零开始猜。

**Agent Harness Engineering（AI 约束工程）**就是解决这个问题的：

| 没有约束的 AI | 有约束的 AI（Harness） |
|--------------|----------------------|
| 每次输出都不一样 | 每次输出都一样 |
| 样式靠运气 | 样式靠系统 |
| 不知道什么能做、什么不能做 | 有明确的规则和边界 |
| 出错了不知道怎么改 | 有验证脚本自动检查 |

简单说：**Agent Harness Engineering 就是给 AI 套上缰绳，让它按规矩办事，而不是乱来。**

kairos-wechat-typeset 就是一个 Harness——它告诉 AI："你只能用这 4 套主题、这 6 种组件、这些字号和颜色。不许自己发明。"

---

## 效果展示

### 宋式美学主题（song）

适合技术长文、方法论、人文评论。

![宋式美学主题预览](./assets/showcase/song-preview.png)

### 科技主题（tech）

适合 AI 技术文章、工程实践、工具教程。

![科技主题预览](./assets/showcase/tech-preview.png)

---

## 它能做什么

把一篇 Markdown 文章，变成可以直接粘贴到微信公众号编辑器的 HTML。

```bash
# 一行命令完成排版
python3 scripts/render.py --theme song --input article.md --output article.html
```

**输入**：一篇 Markdown 文章
**输出**：排版好的 HTML，直接复制粘贴到微信公众号

---

## 4 套主题

| 主题 | 风格 | 适合什么文章 |
|------|------|-------------|
| `song` 宋式美学 | 暖纸 + 宋体 + 克制细线 | 技术长文、方法论、书评 |
| `wending` 稳境白纸 | 安静白纸 + 灰度规格 | 个人成长、心理秩序、慢阅读 |
| `tech` 科技 | 蓝色编号 + 暗色代码 | AI 技术、工程实践、工具教程 |
| `wisme` WISME 规范 | 黑字 + 红色短线 + 灰色表格 | 知识科普、研究报告、组件规范 |

---

## 快速开始

### 前置条件

- Python 3.8+
- 一篇 Markdown 文章

### 3 步上手

```bash
# 1. 进入 skill 目录
cd kairos-wechat-typeset

# 2. 渲染一篇文章
python3 scripts/render.py --theme song --input your-article.md --output output.html

# 3. 打开 output.html，复制内容粘贴到微信公众号编辑器
```

### 健康检查

```bash
python3 scripts/check_all.py --smoke
```

---

## 它不是什么

- ❌ 不是 Markdown 渲染器（Markdown 渲染器只管格式，不管美感）
- ❌ 不是 CSS 生成器（它不用 CSS class，只用内联样式）
- ❌ 不是微信编辑器（它只生成正文内容，标题和封面图需要在微信里设置）
- ❌ 不允许自定义颜色（保护美学一致性，只能从 4 套预设选）

---

## 文档导航

| 文件 | 给谁看 | 说明 |
|------|--------|------|
| `CHEATSHEET.md` | 所有人 | 一页速查，日常操作看这个 |
| `SKILL.md` | AI Agent | 完整的工作流和规则 |
| `PRODUCT.md` | 想了解"为什么"的人 | 设计决策和产品边界 |
| `COMPONENTS.md` | 开发者 | 语义组件契约 |
| `references/anti-patterns.md` | 审查输出的人 | 21 条反模式 + Bad/Fix 对照 |
| `references/category-routing.md` | 选主题的人 | 文章类型 → 推荐策略 |
| `references/layout-recipes.md` | 规划文章结构的人 | 6 个编号版式骨架 |

---

## 许可证

MIT
