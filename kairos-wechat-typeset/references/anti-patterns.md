# Anti-Patterns — kairos-wechat-typeset

反模式比正向规范更有效。每条都来自真实迭代中的踩坑。遇到不确定时，先查这里。

---

## 1. 排版反模式

### AP-01 纯白背景
**Bad**: `background-color: #ffffff`
**Fix**: 使用主题的暖白背景（song: `#f7f5f0`, wending: `#fbfaf7`）。纯白在手机上刺眼，暖白有纸张感。

### AP-02 字号超过 4 种
**Bad**: 正文 16px、小字 14px、注释 13px、代码 12px、标题 28px、章节 25px、副标题 22px（7 种）
**Fix**: 严格使用主题 JSON 中的 typography token，不超过 5 种字号。字号越少越统一。

### AP-03 标题字重过粗
**Bad**: `font-weight: 900` 或 `font-weight: bold`
**Fix**: 中文标题用 `font-weight: 700`（song）或 `800`（wending/tech/wisme）。超过 800 在手机上显脏。

### AP-04 连续 emphasis 超过 2 段
**Bad**: 连续 3 段以上 `**加粗**` 或 `==高亮==`
**Fix**: 连续 emphasis <= 2 段。超过时用 Divider 或 Quote 做呼吸。

### AP-05 Highlight 占比超过 8%
**Bad**: 全文超过 8% 的文字用 `==高亮==`
**Fix**: 高亮只用于核心判断句。1000 字文章最多 3-5 处高亮。

### AP-06 Heading 层级跳级
**Bad**: H1 直接到 H3，跳过 H2
**Fix**: Heading hierarchy 禁止跳级。H1 → H2 → H3 严格递进。

### AP-07 连续长段落超过 3 段
**Bad**: 连续 4 段以上超过 240 字的段落
**Fix**: 连续长段落 <= 3 段。超过时用 Divider、List 或 Quote 做呼吸。

### AP-08 移动端横向溢出
**Bad**: 表格依赖横向滚动、代码块超出屏幕宽度
**Fix**: 表格用 faux table，代码块截断或换行。390px / 430px 无横向滚动。

---

## 2. 内容反模式

### AP-09 LLM 临场写样式
**Bad**: Agent 直接生成 `<style>`、`class=`、`style="font-size: 20px"` 等
**Fix**: 所有样式由主题 renderer 决定。Agent 只做编辑判断（结构、节奏、语义组件）。

### AP-10 空泛模块堆叠
**Bad**: "流程重设计"、"标准成为杠杆"、"赋能数字化转型"
**Fix**: 内容必须具体。每个段落都要有信息增量，不写可套任何主题的空话。

### AP-11 伪造配图证据
**Bad**: 生成图片伪造截图、数据、图表、品牌、引用
**Fix**: evidence_figure 必须有 source_note。生成图不得伪造事实证据。

### AP-12 标题信息不足
**Bad**: 标题只写"AI 产品发布"，没有判断、没有张力
**Fix**: 标题要有核心判断或张力点。"AI 产品发布复盘" → "真正影响留存的不是惊艳演示，而是用户第二天还愿不愿意打开"。

---

## 3. 组件反模式

### AP-13 把语义组件当装饰
**Bad**: 每段都用 `:::lead` 或 `:::insight`
**Fix**: `:::lead` 只用于正文开头。`:::insight` 只用于核心判断。`:::pullquote` 每个大节最多 1 个。

### AP-14 Quote 当作者自己的观点用
**Bad**: 用自己的观点套 `>` 引用块
**Fix**: `>` 用于外部引用。作者自己的观点用 `:::insight` 或 `:::pullquote`。

### AP-15 Figure 没有 caption
**Bad**: `:::figure` 里只有图片没有图注
**Fix**: caption 是 figure 的一部分，不是可选装饰。每张图都要说明"为什么这张图在这里"。

### AP-16 无意义的分隔线
**Bad**: 每个短段落后都加 `---`
**Fix**: Divider 只用于真正的节奏转换。不要为了"好看"而加。

---

## 4. 配图反模式

### AP-17 硬插无意义配图
**Bad**: 每篇文章都必须有图，即使文章不需要
**Fix**: 默认允许 0 张图。图片必须降低理解成本、提供证据、解释结构或建立开场气质。

### AP-18 低必要性图片进入计划
**Bad**: `necessity: low` 的图片被加入 image-plan.json
**Fix**: necessity 只能是 `high` 或 `medium`。低必要性图片直接不进入计划。

### AP-19 Prompt 允许生成可读文字
**Bad**: prompt 中写"图片中包含中文标题 '增长策略'"
**Fix**: prompt 必须禁止图片内生成可读文字，除非用户提供的证据图片本身包含文字。

---

## 5. 验证反模式

### AP-20 不验证就交付
**Bad**: 渲染完 HTML 直接交付，不跑 verify
**Fix**: 至少跑 `--smoke` 验证。完整交付跑 `check_all.py`。

### AP-21 Golden 文件与渲染器不同步
**Bad**: 修改了 render.py 但没有重新生成 goldens/
**Fix**: 修改渲染逻辑后必须重新生成对应的 golden 文件。

---

## 6. 风格漂移反模式

### AP-22 科技主题变成赛博风
**Bad**: tech 主题加了渐变、霓虹色、发光效果
**Fix**: tech 主题只有 accent bar + 暗色代码块，没有渐变

### AP-23 人文主题变成古风
**Bad**: song 主题加了印章、水墨、竖排
**Fix**: song 主题是现代宋体，不是古风装饰

### AP-24 商业主题变成 PPT 风
**Bad**: 信息图堆满模块、每个模块都有背景色
**Fix**: 信息图也要克制，模块用 border 而非 background

### AP-25 成长主题变成鸡汤风
**Bad**: wending 主题加了暖色渐变、emoji、装饰性图标
**Fix**: wending 主题是安静白纸 + 灰度，不加彩色装饰
