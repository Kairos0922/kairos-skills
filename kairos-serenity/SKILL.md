---
name: kairos-serenity
description: |
  基于 X 账号 @aleabitoreddit（Serenity）的 AI 供应链瓶颈投资框架，推荐标的、评估股票/基金、诊断持仓组合（含最优基金推荐）。熟悉支付宝基金定投规则。触发词："选股"、"推荐标的"、"帮我看看这个基金"、"评估持仓"、"Serenity"、"瓶颈股"、"AI供应链"、"光通信标的"、"这个股票怎么样"、"有没有类似的标的"、"帮我用Serenity框架分析"、"诊断持仓"、"修改定投方案"、"定投规则"、"支付宝定投"。每次执行强制抓取 Serenity 最新推文，基于实时数据+框架进行评估。任务完成后自动提炼可沉淀的方法论。
allowed-tools:
  - Bash(python3 *fetch_tweets.py *)
  - Bash(python3 *analyze_tweets.py *)
  - Bash(python3 *config.py *)
  - Read
  - Write
  - WebSearch
  - Grep
  - Glob
metadata:
  version: "1.2.0"
---

# kairos-serenity

基于 @aleabitoreddit 的 AI 供应链瓶颈投资框架，帮你推荐、评估、诊断。

## 运行前提：每次执行前抓取最新数据

**🚫 硬约束：不抓新数据 = 不评估。** 每次被调用时，必须先用 kairos-x-scraper 抓取 @aleabitoreddit 最近 3 天推文。不得使用本地旧缓存代替实时数据。

```bash
# 交易/评估场景：始终获取最新数据（15分钟内也重抓）
python3 .claude/skills/kairos-x-scraper/scripts/fetch_tweets.py aleabitoreddit --days 3 --freshness realtime --insecure
```

> `--freshness realtime` 确保评估永远基于最新数据。`--insecure` 解决中国网络环境 SSL 阻断问题。

x-scraper 交付按日/月/年归档的原始推文 JSONL：`~/.kairos/x-scraper/aleabitoreddit/`。

### 新鲜度闸门

开始分析前，必须验证数据新鲜度：

```
1. 检查最新 JSONL 文件中推文的 created_at 时间戳
2. 如果最新推文 > 24 小时 → ⚠️ 标注"Serenity 近 24 小时无新推文，分析基于此前最新数据"
3. 如果最新推文 > 72 小时 → 🚫 严重警告："Serenity 已超过 3 天未更新，以下分析可能已过时，请等待新推文后重新评估"
4. 所有输出必须标注数据时间窗口（"数据: 7/24-7/26"）
```

### 两步提炼流程（Class D 优化：先统计再深入）

1. **快速统计**：先跑 analyze_tweets.py 拿结构化基线
   ```bash
   python3 .claude/skills/kairos-x-scraper/scripts/analyze_tweets.py \
     ~/.kairos/x-scraper/aleabitoreddit --days 3 --mode all
   ```
   获得：ticker 频率 TOP20、主题分布、多空信号分类

2. **深度分析**：基于统计结果，只深度读相关推文 → 结合 references/ 框架分析

> ⚠️ **铁律：不得在缺少实时推文数据的情况下推测 Serenity 的当前观点。** 如果没有最近3天数据，告诉用户"无法获取 Serenity 最新推文，评估无法继续"，不继续分析。3天以上无新推文时标注数据间隔风险，但仍可基于最新可用数据给出分析（需明确标注）。

---

## 配置文件

路径：`~/.kairos/kairos-serenity-config.json`

**所有配置修改统一走 config.py**（Class C：状态完整性），不再用 Edit 工具直接编辑 JSON：

```bash
python3 .claude/skills/kairos-serenity/scripts/config.py list       # 列出持仓
python3 .claude/skills/kairos-serenity/scripts/config.py validate   # 校验完整性
python3 .claude/skills/kairos-serenity/scripts/config.py add <code> --name "..." --market QDII --amount "200/日"
python3 .claude/skills/kairos-serenity/scripts/config.py update <code> --status active
python3 .claude/skills/kairos-serenity/scripts/config.py remove <code>
```

每次修改自动：备份旧文件 → 原子写入 → 读回校验。

```json
{
  "holdings": {},
  "preferences": {}
}
```

### holdings 结构

```json
{
  "018816": {
    "type": "fund",
    "code": "018816",
    "name": "方正富邦核心优势混合C",
    "market": "A",
    "amount": "100/日",
    "method": "定投",
    "status": "active"
  }
}
```

### preferences 结构

用户在对话中透露的偏好，逐次累积：

```json
{
  "market": "A股",
  "fund_type": "场外",
  "risk_tolerance": "high",
  "investment_style": "定投",
  "notes": "用户偏好小额分散定投，不追涨杀跌"
}
```

对话中用户说了新的偏好 → 更新配置文件对应字段。

---

## 三种模式

### 模式 1：推荐

**触发**：用户说"推荐"、"最近有什么"、"帮我选"、"有没有好的标的"等，且没有给出具体代码。

**流程**：

1. **读取偏好**。检查配置文件中 `preferences.market` 和 `preferences.fund_type`：
   - 已记录 → 展示给用户确认："上次你偏好A股场外基金，这次一样？"
   - 未记录 → 追问：美股/A股/港股？场内/场外？

2. **分析最新推文**。从刚抓取的 tweets JSONL 中：
   - 统计最近3天提及最多的股票代码
   - 识别 Serenity 明确表达 bullish / bearish 的标的
   - 提取新的持仓披露或论点更新

3. **结合 references/ 框架**：
   - 实时提及的标的 → 🔴 高信心推荐（标注推文证据）
   - 框架中符合当前主题方向但最近未提及 → 🟡 框架匹配（标注"近3天未直接提及"）
   - Serenity 明确回避的 → ❌ 明确排除

4. **输出**：

   ```
   ## 🔴 高位推荐（有实时推文支撑）
   
   | 标的 | 方向 | 证据 | 
   |------|------|------|
   | $SIVE | 光学/CPO激光 | 近3天提及X次，7/2重申持仓 |
   
   ## 🟡 框架匹配（近3天未直接提及）
   
   ...
   
   ## ❌ 当前回避
   
   ...
   ```

---

### 模式 2：评估标的

**触发**：用户给了股票代码（$XXX）或基金代码（6位数字）。

**流程**：

1. **读取持仓配置**。如果标的已在 `holdings` 中，一并展示。

2. **如果是基金**：查最新季报持仓 → 提取前十大重仓股。

3. **从实时推文中提取该标的的所有提及**：
   - Serenity 最近3天有没有说？
   - 说了什么？bullish / bearish / 持有 / 回避？
   - 有没有更新论点？

4. **结合框架评估**。对每个相关标的跑 Serenity 22项原则中的关键维度：

   | 维度 | 评分 | 依据 |
   |------|------|------|
   | 瓶颈vs卡脖子 | 瓶颈/卡脖子 | 产能限制还是架构依赖？只有卡脖子才有定价权（§16） |
   | 架构护城河 | ⭐ 1-5 | 替换是否需要下游重新设计？（§17） |
   | 双重暴露 | ✅/❌ | 是否同时受益两条独立主线？（§20） |
   | 所处阶段 | 🟢认证期 / 🟡爬坡期 / 🔴定价期 | 量产时间轴位置（§6） |
   | 融资质量 | ✅健康 / ⚠️关注 / ❌危险 | ATM/SBC/债务（§7, §8） |
   | 垂直整合空间 | 高/中/低 | 3-5年全栈演化路径（§19） |
   | 宏观顺逆风 | 🟢顺风 / 🟡中性 / 🔴逆风 | Fed+CapEx+AI竞争格局（§21） |

5. **输出结论**：

   ```
   ## 标的评估
   
   ### 卡脖子纯度: 瓶颈 / 卡脖子
   依据: 是否唯一来源，撤掉会怎样
   
   ### 架构护城河 ⭐⭐⭐⭐ (4/5)  
   依据: 替换成本/架构绑定程度
   
   ### Serenity 实时信号
   近3天提及X次。7/2: "xxx"
   
   ### 结论
   ✅ Serenity会买 / 🟡 关注但不重仓 / ❌ 会回避
   理由: ...
   ```

---

### 模式 3：持仓诊断

**触发**：用户说"看持仓"、"诊断"、"评估我的持仓"、"修改方案"、"我的定投"等。

**流程**：

1. **读取配置中的 holdings**，展示给用户确认：

   ```
   当前持仓:
   - 018816 方正富邦核心优势  每日100元定投  ✅
   - 012922 易方达全球成长    暂停中(额度)    ⏸️
   
   确认这些信息？如有变动请告诉我。
   ```

2. **逐只评估**。每只基金/股票跑模式2的评估流程。

3. **组合层面诊断**：

   - 从实时推文分析 Serenity 当前主题权重分布
   - 对比用户持仓主题覆盖
   - 画出暴露热力图

   ```
   主题暴露对比:
   Serenity关注  光学 ████████████████████████ 53%
   你的持仓      光学 ████████████████████████ 70%  ← 过度集中
   Serenity关注  存储 ██████████ 20%  
   你的持仓      存储 ██████████ 30%
   Serenity关注  电网 ███ 6%
   你的持仓      电网 ▏ 0%   ← 缺失
   ```

4. **给出修改建议**：

   - 每只标的：维持 / 加大 / 减小 / 停止
   - 方向性建议（不给精确金额）
   - 如发现新标的值得加入 → 推荐插入

5. **用户确认后更新配置**。持仓变动写入 `holdings`。

6. **最优基金推荐**（新增）。诊断完现有持仓后，必须推荐一只当前最值得加入的基金：

   1. **从参考文献和实时推文中筛选候选池**：
      - Serenity 当前最高频提及的方向（从 analyze_tweets.py 统计结果提取）
      - 用户持仓中**主题覆盖不足**的方向（从 Step 3 暴露热力图中的缺失区域提取）
      - 满足用户偏好约束（市场类型、场内/场外、定投/一次性）

   2. **候选池评分**（每项 1-5）：

      | 维度 | 权重 | 说明 |
      |------|:---:|------|
      | Serenity 实时信号强度 | 30% | 近3天提及频率 + 方向明确度 |
      | 组合缺口匹配度 | 25% | 填补当前持仓缺失的主题 |
      | 框架契合度 | 20% | 瓶颈/卡脖子纯度 + 架构护城河 |
      | 定投可操作性 | 15% | 是否可场外定投、当前是否限额、费率结构 |
      | 宏观顺风 | 10% | 当前宏观环境是否有利于该方向 |

   3. **输出格式**：

      ```
      ## 🏆 最优基金推荐
      
      ### [基金代码] [基金名称]
      
      | 维度 | 评分 | 依据 |
      |------|:---:|------|
      | Serenity 实时信号 | ⭐⭐⭐⭐ | 近3天提及X次，[引用推文] |
      | 组合缺口匹配 | ⭐⭐⭐⭐⭐ | 填补[XX]主题 0% 暴露 |
      | 框架契合度 | ⭐⭐⭐ | 卡脖子纯度/架构护城河判断 |
      | 定投可操作性 | ⭐⭐⭐ | 场外可定投/限额情况/费率 |
      | 宏观顺风 | ⭐⭐⭐⭐ | [宏观环境判断] |
      
      **综合评分: X.X/5.0**
      
      **推荐方案**：[日/周/月]定投 [金额] 元
      **理由**：[一句话总结为什么这只基金是当前最优选择]
      
      > ⚠️ 仅为框架分析推荐，不构成投资建议。请自行判断后决定是否加入。
      ```

   4. **如果候选池为空**（当前所有合适方向已覆盖或限购），诚实告知：
      > 🟡 当前持仓已较好覆盖 Serenity 核心方向，且无符合偏好的新标的推荐。建议等待 QDII 额度释放或 Serenity 新方向浮现。

7. **支付宝定投规则合规检查**。给出任何定投建议前，必须对照 `references/alipay-rules.md` 检查：
   - 建议的日定投金额 ≤ 该基金当前单日限额
   - 如基金限购/暂停，标注并给出替代方案（预约买入、同类基金分散、场内 ETF）
   - 多笔定投不设在同一日（避免节假日顺延集中扣款失败）

---

## 数据来源优先级

```
1. 原始推文（~/.kairos/x-scraper/aleabitoreddit/ 当月日文件+历史月/年文件）
   → 直接读取，serenity 自己做全部提炼和分析
   → 最高权重

2. 基金季报（WebSearch 获取最新持仓）
   → 基金的实际底层暴露

3. references/ 静态框架
   → 35条原则、供应链地图、历史论点
   → 仅在实时推文无覆盖时作为背景参考
```

> ⚠️ references/ 中的 ticker-theses.md 和 track-record.md 记录的是历史论点。**如果实时推文中 Serenity 已经改变了观点，以实时推文为准。** 每个论断必须标注证据来源和新鲜度。

---

## 偏好积累

对话中识别到以下信息时，自动写入 `preferences`：

| 用户说了什么 | 记录字段 |
|-------------|---------|
| "我只买A股" | `market: "A股"` |
| "只买QDII"/"QDII" | `market: "QDII"` |
| "场外基金" | `fund_type: "场外"` |
| "定投"/"日定投" | `investment_style: "定投"` |
| "不要一次性买入" | `notes: "..."` |
| "我能承受高风险" | `risk_tolerance: "high"` |
| "排除A股"/"不买港股" | `exclude: "..."` |
| "暂停"/"限购" | 更新 holdings status（非偏好） |

### 基金持仓缓存

holdings 中可缓存基金季报数据，避免每次 WebSearch：

```json
"012922": {
  ...
  "portfolio": {
    "as_of": "2026-Q2",
    "fetched": "2026-07-23",
    "top10": [...]
  }
}
```

超过 14 天自动刷新 WebSearch，否则直接用缓存。

下次执行时先检查已有配置，跳过已记录的问题。

---

## 任务后沉淀

**每次分析任务完成后，执行以下反思流程**：

### 沉淀判断标准

任务中出现了以下情况之一 → 必须沉淀：

| 情况 | 沉淀内容 | 示例 |
|------|---------|------|
| Serenity 提出了**新的分析视角/方法论** | 提取为新的方法论原则 | 如 §23-§30 的新增原则 |
| 某个评估维度的**判断逻辑被验证有效** | 提炼为可复用的判断模板 | "如何判断一只 QDII 基金是否值得定投" |
| 发现**references 中的信息已过时** | 更新对应文件 | 某 ticker thesis 论点已被推翻 |
| 用户表达了**新的偏好或约束** | 更新 preferences | 新增排除条件、风险偏好变化 |
| **跨任务的重复模式**出现 | 抽象为通用规则 | "用户连续两次问同一类标的" |

### 沉淀流程

```
1. 反思：这次任务中有没有新的认知？
   - Serenity 的论点有没有新发展？
   - 有没有发现某个判断规则可以泛化？
   - 有没有发现 references 陈旧或错误的信息？

2. 判断：是否值得写入文件？
   - 是方法论进步 → 写入 references/methodology.md（仿照现有格式，作为增量笔记）
   - 是 ticker 论点变化 → 更新 references/ticker-theses.md
   - 是 track record 更新 → 更新 references/track-record.md
   - 是工作流优化 → 更新本 SKILL.md
   - 是用户偏好变化 → 更新 ~/.kairos/kairos-serenity-config.json

3. 写入：简洁精炼，标注日期和来源推文 ID
   - 格式参照 methodology.md 中 "Recent incremental methodology notes" 区块
   - 每条增量笔记 ≤ 5 行，标注 Source tweet ID

4. 告知用户：
   > 📝 已沉淀: [一句话描述沉淀了什么] → [写入位置]
   
   如果无新内容可沉淀：
   > 💤 本次无新方法论沉淀（Serenity 论点无实质性更新 / 分析模式与此前一致）
```

### 不做的事

- ❌ 不为了沉淀而沉淀——没有新认知就诚实说没有
- ❌ 不重复写入已有的方法论
- ❌ 不沉淀纯个案判断（"XX 基金今天值得买"不是方法论）

---

## 安全声明

每次输出末尾加：

> ⚠️ 以上分析基于 @aleabitoreddit 的公开推文框架和 [$日期] 的实时数据。不构成投资建议。Serenity 的标的普遍为高波动小盘股，请自行判断风险。

---

## References

### 分层加载策略（Class D：上下文效率）

不再每次全量加载5个文件。按三层按需加载：

**L1 骨架（始终加载，~4K tokens）**：
- `references/supply-chain-map.json`（公司层位 + Serenity stance）
- `references/alipay-rules.md`（定投规则：限额/费率/交易确认/扣款失败场景）

**L2 标的详情（按需加载）**：
- `references/ticker-theses.md` → 仅 grep/Read 基金持仓中涉及的 ticker 段落
- `references/track-record.md` → 仅 grep 相关日期范围条目

**L3 方法论（仅在详细评分时加载）**：
- `references/methodology.md` 的 checklist 部分（§15-§28）
- `references/chain_map.md`（供应链详细描述）

### 数据陈旧度检查

读取 references 时检查最后更新日期。如果 > 7 天，在输出中标注：
> ⚠️ references 数据截止 X 月 X 日，最新推文可能包含未归档的新观点。

### 文件清单

| 文件 | 用途 | 加载层 |
|------|------|:---:|
| `references/supply-chain-map.json` | AI 供应链各层级 → 对应公司 | L1 |
| `references/alipay-rules.md` | 支付宝基金定投规则（限额/费率/交易确认） | L1 |
| `references/ticker-theses.md` | Serenity 历史论点（每个标的） | L2 |
| `references/track-record.md` | 历史推荐 + 验证状态 | L2 |
| `references/methodology.md` | 35条原则 + 33项checklist | L3 |
| `references/chain_map.md` | 供应链详细 Mermaid 图 | L3 |
