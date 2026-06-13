# Editorial Magazine Design System

## 风格定位

杂志感、叙事、观点、人物/组织/文化主题。特征是大留白、强主句、宋黑混排或优雅无衬线、少量细节标注、纸张质感。

适合：观点、文化、组织、人物、叙事、长文综合、反思分析。

## 视觉 DNA

- **色彩哲学**：墨水 + 纸感，自然色调。以 ink/paper/muted 为核心三色，偶尔用 accent 点缀。
- **结构元素**：不对称留白、细线标注、editorial metadata、纸张纹理。
- **质感**：高级印刷品、杂志卡片、纸张颗粒感。
- **信息密度**：中等偏低，封面为主，让标题和留白承载情绪。

## 色彩系统

以墨水和纸张为基调的自然色系。每套主题锁定 3-4 色：

| 语义角色 | 说明 |
|----------|------|
| ink | 主文字色，深色 |
| paper | 背景色，温暖纸张感 |
| muted | 辅助灰色，用于 caption 和 metadata |
| accent | 可选强调色，克制使用 |

## 字体配方

默认使用 Editorial Serif 配方：

```css
--font-display-zh: "Noto Serif SC", "Songti SC", Georgia, serif;
--font-text-zh: "Noto Sans SC", "PingFang SC", sans-serif;
--font-en: "Inter", "Helvetica Neue", sans-serif;
--font-serif: "Noto Serif SC", "Songti SC", Georgia, serif;
```

规则：
- display 使用衬线字体，传达文学权威感
- body 使用无衬线，保持可读性
- 越大越细：56px 以上 display weight <= 680
- 大号中文不用 `font-weight: 700`

## 网格系统

- 12 列网格，24px gap
- 外边距 72-96px（根据画幅）
- 大面积留白是核心设计语言
- hero 区域占画布 40-60%

## 文字重构

Editorial 的文字重构以叙事为主：
- 标题是画面主体，承载情绪和观点
- 通过字号对比、留白、衬线气质传达权威感
- 文字不需要被色块或网格"重构"，而是通过排版本身传达力量

## 质感规则

**必须**：
- 纸张纹理或印刷颗粒感
- 大面积留白
- 细线标注
- 克制的 metadata

**禁止**：
- 网格发丝线系统（这是 Swiss 的）
- 霓虹色
- 复杂阴影
- 卡通质感

## 反模式

- 做成生活方式海报，没有商业结构
- 做成 PPT 模板
- 颜色超过 3 种
- 模块没有具体内容

## 专项 QA 规则

- 留白是否充足（hero 区域不应拥挤）
- 衬线字体是否正确加载
- 纸张质感是否自然
- 标题是否是第一视觉焦点
- 整体是否有杂志感而非 PPT 感
