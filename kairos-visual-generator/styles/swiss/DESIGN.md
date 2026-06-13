# Swiss Consulting Design System

## 风格定位

分析、框架、方法论、产品、技术组织主题。特征是网格、极强字号对比、发丝线、单一锚点色、克制模块。

适合：流程、方法、矩阵、系统、数据、AI、产品、技术。

## 视觉 DNA

- **色彩哲学**：单一 accent + 黑白灰。以 ink/paper/muted 为基底，accent 色点缀关键节点。
- **结构元素**：瑞士网格、发丝线、精确对齐、strong type contrast。
- **质感**：企业级、干净、理性、专业。
- **信息密度**：中高，支持封面和信息图两种模式。

## 色彩系统

以黑白灰为基底，单一 accent 色点缀：

| 语义角色 | 说明 |
|----------|------|
| ink | 主文字色，深色 |
| paper | 背景色，干净白 |
| muted | 辅助灰色 |
| accent | 强调色，覆盖不超过 8% 画布 |
| line | 发丝线色 |

## 字体配方

默认使用 Swiss Sans 配方：

```css
--font-display-zh: "Noto Sans SC", "PingFang SC", sans-serif;
--font-text-zh: "Noto Sans SC", "PingFang SC", sans-serif;
--font-en: "Inter", "Helvetica Neue", sans-serif;
```

规则：
- display 使用无衬线，传达现代专业感
- 越大越细：56px 以上 display weight <= 580
- 大号中文不用 `font-weight: 700`
- 英文标签可以用 uppercase + letter-spacing

## 网格系统

- 12 列网格，24px gap
- 外边距 72-96px
- 精确对齐是核心
- 发丝线（1px）用于结构分隔

## 文字重构

Swiss 的文字重构以商业结构为主：
- 文字成为画面主体结构
- 可以被切割、框架化、路径化、模块化
- 与隐喻图形融合

## 质感规则

**必须**：
- 精确网格对齐
- 发丝线分隔
- 单一 accent 色
- 干净白底

**禁止**：
- 衬线装饰
- 水墨效果
- 渐变
- 多色 accent

## 反模式

- 做成普通 PPT 模板
- accent 色超过 8% 画布
- 多个 accent 色
- 模块没有具体内容

## 专项 QA 规则

- accent 色占比是否 ≤ 8%
- 网格对齐是否精确
- 发丝线是否清晰
- 是否保持克制专业气质
- 大号文字是否足够细（weight <= 580）
