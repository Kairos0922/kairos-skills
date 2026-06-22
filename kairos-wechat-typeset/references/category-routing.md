# 品类路由 — kairos-wechat-typeset

WeChat 文章类型 → 推荐排版策略的确定性查找表。

---

## 路由表

| 文章类型 | 推荐主题 | 推荐 Kairos 组件 | 图文比例 | 常见 pitfalls |
| --- | --- | --- | --- | --- |
| 技术长文 | `tech` | CodeBlock + Steps + Insight + Table | 少图（0-2 张概念图） | 代码块过长不截断、表格横向溢出 |
| 方法论文章 | `song` | Lead + Insight + Pullquote + SoftList | 少图（0-1 张框架图） | 全文高亮过多、引用块当自己观点用 |
| 人文评论 | `song` | Lead + Pullquote + ClosingNote | 极少图（0-1 张氛围图） | 段落过长不换行、缺少呼吸节奏 |
| 个人成长 | `wending` | Lead + Insight + SoftList + ClosingNote | 少图（0-1 张定调图） | 鸡汤感过重、缺乏具体案例 |
| 工具教程 | `tech` | Steps + CodeBlock + Figure + Callout | 多图（3-5 张截图） | 截图不清晰、步骤顺序混乱 |
| 产品方案 | `tech` | Insight + Table + Figure + Steps | 中图（2-3 张架构图） | 概念堆砌不落地、缺少数据支撑 |
| 知识科普 | `wisme` | Insight + Table + Callout + SoftList | 中图（2-3 张解释图） | 术语不解释、信息密度不足 |
| 研究报告 | `wisme` | Table + Insight + Figure + Callout | 多图（3-5 张数据图） | 数据无来源、结论不明确 |
| 生活方式 | `wending` | Lead + Figure + Pullquote + ClosingNote | 多图（3-5 张生活图） | 图文脱节、文字过少 |
| 书评 | `song` | Lead + Pullquote + Insight + ClosingNote | 极少图（0-1 张封面图） | 大段摘抄不评论、缺少个人判断 |
| 开发者文档 | `pi` | CodeBlock + Steps + Insight + Callout | 少图（0-2 张架构图） | 代码示例不完整、步骤跳步 |
| API 参考 | `pi` | CodeBlock + Table + Insight + Figure | 少图（0-1 张流程图） | 参数说明不全、返回值缺失 |

---

## 内容长度 → 组件密度映射

| 文章长度 | 推荐 Kairos 组件数 | 推荐 Divider 数 | 推荐 Quote/Insight 数 |
| --- | --- | --- | --- |
| < 800 字 | 1-2 个 | 0-1 个 | 0-1 个 |
| 800-1500 字 | 2-4 个 | 1-2 个 | 1-2 个 |
| 1500-3000 字 | 4-6 个 | 2-3 个 | 2-3 个 |
| > 3000 字 | 6-8 个 | 3-4 个 | 3-4 个 |

---

## 主题选择决策树

```
用户说"技术/AI/工程/代码" → tech
用户说"方法论/框架/思考" → song
用户说"个人/成长/心理/慢阅读" → wending
用户说"科普/报告/规范/说明" → wisme
用户说"开发者文档/API/工具指南/编程实战" → pi
用户不确定 → 问"这篇文章的核心是什么？"
  - 核心是判断/观点 → song
  - 核心是步骤/操作 → tech
  - 核心是感受/体验 → wending
  - 核心是事实/数据 → wisme
  - 核心是代码/接口/工具 → pi
```

---

## 图片取用优先级

1. **用户自己的图片**（最不"AI 感"）
2. **AI 生成**（宿主 agent 有能力时）
3. **网络取图**（Pexels → Unsplash → Flickr CC）
4. **不配图**（文章不需要时）

配图前先问用户一次："这篇我需要 1-2 张图。三种走法：A. 你自己有照片/截图；B. 我去图库找；C. 用 AI 生成。"推荐 A，接受用户选的任何选项，不再追问。
