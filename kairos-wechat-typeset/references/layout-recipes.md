# Layout Recipes — kairos-wechat-typeset

编号版式骨架 + 最小内容量阈值。每种 WeChat 文章类型对应一个推荐 recipe。

---

## Recipe 列表

### W01 纯文字长文

```
[Lead]
[Paragraph] x N
[Divider]
[Insight]
[Paragraph] x N
[ClosingNote]
```

- **适合**：方法论、人文评论、个人成长
- **最小内容量**：800 字
- **最大内容量**：5000 字
- **组件上限**：Lead x1, Insight x3, Pullquote x2, ClosingNote x1
- **呼吸规则**：每 3 段长文字后必须有 Divider 或 Quote

### W02 引用密集型

```
[Lead]
[Paragraph]
[Pullquote]
[Paragraph]
[Insight]
[Paragraph]
[Quote]
[Paragraph]
[ClosingNote]
```

- **适合**：书评、影评、观点文章
- **最小内容量**：600 字
- **最大内容量**：3000 字
- **组件上限**：Lead x1, Insight x2, Pullquote x3, Quote x2
- **呼吸规则**：Pullquote 之间至少间隔 1 段正文

### W03 教程/步骤型

```
[Lead]
[Paragraph]
[Steps] (3-8 步)
[CodeBlock] (可选)
[Callout]
[Paragraph]
[Figure] (可选)
[ClosingNote]
```

- **适合**：工具教程、操作指南、技术实践
- **最小内容量**：500 字
- **最大内容量**：4000 字
- **组件上限**：Lead x1, Steps x1, CodeBlock x3, Callout x2, Figure x3
- **呼吸规则**：每个步骤之间不需要 Divider，但 CodeBlock 后需要

### W04 数据/报告型

```
[Lead]
[Paragraph]
[Table]
[Insight]
[Paragraph]
[Figure]
[Callout]
[Table] (可选)
[Paragraph]
[ClosingNote]
```

- **适合**：研究报告、数据分析、产品方案
- **最小内容量**：1000 字
- **最大内容量**：5000 字
- **组件上限**：Lead x1, Table x2, Insight x3, Figure x3, Callout x2
- **呼吸规则**：每个 Table 后必须有 Insight 解读

### W05 图文混排型

```
[Lead]
[Figure]
[Paragraph]
[Figure]
[Paragraph]
[Insight]
[Figure]
[Paragraph]
[ClosingNote]
```

- **适合**：生活方式、旅行、产品展示
- **最小内容量**：400 字
- **最大内容量**：2000 字
- **组件上限**：Lead x1, Figure x5, Insight x2, ClosingNote x1
- **呼吸规则**：禁止连续 2 张 Figure 不带文字

### W06 综合型

```
[Lead]
[Paragraph]
[Insight]
[Paragraph]
[Table]
[Paragraph]
[Figure]
[Callout]
[Paragraph]
[Steps]
[Paragraph]
[Pullquote]
[Paragraph]
[ClosingNote]
```

- **适合**：产品发布、综合分析、深度长文
- **最小内容量**：1500 字
- **最大内容量**：6000 字
- **组件上限**：所有组件各 x2-3
- **呼吸规则**：每 4 段文字后必须有非文字组件

---

## Recipe 选择决策树

```
文章主要是步骤/操作？ → W03
文章有大量数据/表格？ → W04
文章有 3 张以上配图？ → W05
文章是综合分析/长文？ → W06
文章以引用/观点为主？ → W02
其他情况 → W01
```

---

## 密度硬规则

- 每 500 字至少有 1 个非文字组件（Divider / Quote / List / Callout / Figure）
- 连续长段落 <= 3 段
- 连续 emphasis <= 2 段
- Highlight 占比 <= 8%
- Heading 层级禁止跳级
- 移动端 390px / 430px 无横向滚动

---

## 禁止构图

1. 不要把标题居中 + 正文居中（微信文章标题应该左对齐）
2. 不要连续 3 段以上纯文字无任何组件
3. 不要每个段落都加背景色
4. 不要标题比正文还小
5. 不要引用块连续出现 2 个以上
6. 不要表格之后不加解读文字
