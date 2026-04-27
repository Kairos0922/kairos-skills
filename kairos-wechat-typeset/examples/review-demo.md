---
title: 微信公众号排版 Skill 全量语法验收 Demo
---

# 微信公众号排版 Skill 全量语法验收 Demo

这是一份用于人工审核的综合示例。它覆盖了常规 Markdown 写作里最常见的结构，包括标题、段落、强调、链接、图片、列表、引用、分割线、代码块、表格，以及一些在公众号场景里常见的混排细节。到了 2026 年，像 AI Agent、Markdown、HTML、JSON、Python 3.12 这样的英文和数字，也应该在宋体正文里看起来协调而克制。

这是同一段里的第二行，使用 Markdown 的行尾两个空格触发换行。  
这一行应该和上一行保持紧密的段内节奏，而不是断成两个完全独立的段落。

## 01 标题系统

我们先看标题层级。

### 三级标题

这里用于观察较浅层级的小标题是否依旧干净。

#### 四级标题

四级标题通常很少用，但在长文里偶尔会出现，因此也应该被稳定处理。

##### 五级标题

五级标题主要用于验证退化样式是否自然。

###### 六级标题

六级标题一般只用于非常细的说明，这里主要检查兼容性。

---

## 02 行内强调

这是普通正文，其中 **粗体**、*斜体*、~~删除线~~、`行内代码` 都应该能被识别。

这一段里还包含 [外部链接](https://example.com)、[OpenAI Docs](https://platform.openai.com/docs/overview) 和 ==虚线强调句==，用于观察重点信息的视觉节奏。

**这一整段只有一句话，但它应该被识别为整段重点句。**

---

## 03 无序列表与有序列表

- 第一条无序列表，用来观察项目符号的质感与缩进。
- 第二条无序列表，其中包含 **粗体强调** 与 `inline code`。
- 第三条无序列表，包含链接：[示例网站](https://example.com)

1. 第一条有序列表，用来观察数字标记与正文的距离。
2. 第二条有序列表，其中混合 AI Agent、HTML Email、Markdown Table 等英文短语。
3. 第三条有序列表，后面跟一段续行
   这一句是列表项的续行文本，用来测试缩进和换行后的对齐。

---

## 04 引用块与提示块

> 这是普通引用块。它适合承接解释、旁白、备注和语气上的停顿。

> [!NOTE]
> 这是一个 NOTE 提示块，用来承接普通说明。

> [!TIP]
> 这是一个 TIP 提示块，用来承接建议、窍门和轻量提醒。

> [!WARNING]
> 这是一个 WARNING 提示块，用来承接需要读者多留意的信息。

---

## 05 图片与说明文字

下面是一张远程图片：

![留白风格的建筑空间](https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1400&q=80)

图片之后应该带有说明文字，而且说明文字要比正文更轻，不应抢夺主叙事。

---

## 06 代码块

下面分别放一段 Python、JavaScript 和 Bash：

```python
def render_article(title: str, blocks: list[str]) -> str:
    return f"{title}: {len(blocks)} blocks"
```

```javascript
function balanceTypography(content) {
  return content.replaceAll("Markdown", "Editorial Markdown");
}
```

```bash
python3 scripts/render.py --input article.md --output article.html --fragment-only
```

---

## 07 表格

| 项目 | 用途 | 备注 |
| --- | --- | --- |
| 标题 | 建立结构层级 | 适合长文分段 |
| 列表 | 承接并列信息 | 不宜过密 |
| 代码块 | 承接命令与代码 | 需要更强区分度 |
| 表格 | 承接对照信息 | 在公众号里建议卡片化 |

---

## 08 混合内容段

你可以把很多常见语法混在一起，例如：**重点句** 配合 [链接](https://example.com)，再带一点 *斜体语气*、一点 `code token`、一点 ~~删除内容~~，最后用 ==一小段虚线强调== 收束读者视线。

> [!TIP]
> 如果一篇文章里既有 AI Agent，也有 Python 3.12、JSON Schema、Markdown Renderer 这样的英文术语，中英混排的节奏是否自然，会非常影响高级感。

---

## 09 任务列表降级观察

- [x] 已完成项，用于观察 task list 在当前 skill 中的降级呈现
- [ ] 未完成项，用于观察方括号内容是否依然可读
- [ ] 第三项里加入 API、SDK、CLI、URL 等常见英文缩写

---

## 10 原始 HTML 转义观察

下面这行原始 HTML 在当前 skill 中应该被安全转义，而不是直接渲染：

<div class="raw-html-test">这是一段原始 HTML</div>

---

## 11 结尾收束

如果这份 demo 渲染正常，你应该能在一个 HTML 文件里同时检查：

- 字体气质是否符合“优雅宋体 + 平衡西文衬线”
- 列表、代码块、表格是否已经有新的艺术化处理
- 常规 Markdown 语法在公众号风格下是否都还能稳定输出
- 图片、链接、强调、引用、提示块是否都保留了清晰层次
