# kairos-wechat-typeset · Cheatsheet

一页速查。日常操作只需这份文件。完整规范见 `SKILL.md` 和 `COMPONENTS.md`。

---

## 10 条不变量

1. 输出无 `<style>` 标签
2. 输出无 `class=`
3. 输出无外部 CSS 引用
4. 输出无 `<script>`
5. 输出无原生 `<table>`、`<ul>`、`<ol>`
6. 所有样式内联，微信编辑器可直接粘贴
7. 图片必须 `max-width: 100%`
8. Heading 层级禁止跳级
9. Highlight 占比 <= 8%
10. 移动端 390px / 430px 无横向滚动

---

## 4 套主题速查

| ID | 名称 | 适用场景 | 一句话描述 |
|----|------|----------|-----------|
| `song` | 宋式美学 | 技术长文、方法论、人文评论、书评 | 暖纸 + 宋体层级 + 克制细线 |
| `wending` | 稳境白纸 | 个人成长、心理秩序、慢阅读 | 安静白纸 + 灰度规格 + 重宋标题 |
| `tech` | 科技 | AI 技术文章、工程实践、工具教程 | 蓝色编号 + 暗色代码 + 浅蓝信息块 |
| `wisme` | WISME 规范 | 知识科普、研究报告、组件规范 | 黑字标题 + 红色短线 + 灰色表格 |

选择规则：
- 不知道选什么 → `song`
- 技术/工程/AI → `tech`
- 个人/心理/慢阅读 → `wending`
- 科普/报告/规范 → `wisme`

---

## Kairos 组件白名单

只允许以下 Markdown 容器语法，不允许 HTML / CSS / style / class：

| 组件 | 语法 | 用途 |
|------|------|------|
| `lead` | `:::lead ... :::` | 正文开头导语 |
| `insight` | `:::insight ... :::` | 核心判断 / 关键结论 |
| `pullquote` | `:::pullquote ... :::` | 杂志感摘引 |
| `figure` | `:::figure ... :::` | 图片 + 图注 |
| `soft-list` | `:::soft-list ... :::` | 非步骤型柔和列表 |
| `closing-note` | `:::closing-note ... :::` | 结尾收束语 |

扩展语法：
- `==重点句==` → 主题强调样式
- `> [!NOTE]` / `> [!TIP]` / `> [!WARNING]` → 语义提示块
- `## 01 标题` → 主题化章节数字

---

## 命令速查

### 完整工作流（推荐）

```bash
python3 scripts/typeset.py --input article.md --theme song --optimize-layout yes
```

### 非交互式

```bash
python3 scripts/typeset.py --input article.md --theme song --optimize-layout no --non-interactive
```

### 底层渲染

```bash
python3 scripts/render.py --theme song --input article.md --output article.html --verify
```

### 仅输出正文片段

```bash
python3 scripts/render.py --theme song --input article.md --output article.fragment.html --fragment-only --verify
```

### 加载 Web 字体

```bash
python3 scripts/render.py --theme song --input article.md --output article.html --web-fonts --verify
```

衬线主题加载 LXGW WenKai，无衬线主题加载 LXGW Neo XiHei + Inter。不开此参数时使用系统字体回退链。

### 验证

```bash
python3 scripts/verify.py --input article.html
python3 scripts/verify_markdown.py --input layout.md
python3 scripts/verify_image_plan.py --input image-plan.json --theme tech
python3 scripts/check_all.py --smoke
python3 scripts/check_all.py
```

### 列出主题

```bash
python3 scripts/render.py --list-themes
```

---

## 质量门控速查

生成后必须通过的检查：

| 检查项 | 脚本 | 通过标准 |
|--------|------|----------|
| HTML 安全 | html_verify.py | 无 `<style>` / `class=` / 外部 CSS / `<script>` / 原生 table |
| Markdown 安全 | markdown_verify.py | 无 raw HTML / `style=` / `class=` / `<script>` |
| 编辑质量 | editorial_verify.py | 连续长段 <= 3、连续 emphasis <= 2、heading 不跳级 |
| 配图计划 | verify_image_plan.py | 图片有 purpose / why_needed / prompt / avoid |
| 视觉库存 | audit_visual.py | 字号无漂移、间距合理、边框不过密 |

---

## 输出结构

```text
~/.wechat-typeset/
  article-slug/
    v001/
      layout.md          # 可选，优化布局时输出
      image-plan.json    # 可选，配图计划
      image-prompts.md   # 可选，无生图能力时输出
      images/            # 可选，配图资产
      output.html        # 必选，排版后的 HTML
      meta.json          # 必选，版本元数据
```

---

## 反馈处理

当用户给出模糊反馈时，先报告当前值，再提供选项：

| 用户说 | 先报告 | 选项 |
|--------|--------|------|
| "太挤了" | 当前 spacing_scale | (a) compressed (b) relaxed |
| "不够高级" | 当前 emphasis_mode | (a) minimal (b) editorial |
| "颜色不对" | 当前主题 ID | (a) song (b) wending (c) tech (d) wisme |
| "标题太大了" | 当前 H1 字号 | 降低到下一级 |
| "段落太长" | 当前段落长度 | 拆分为多段 |
