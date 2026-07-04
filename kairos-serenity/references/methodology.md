# Serenity's Methodology — the reusable lens

His analytical framework distilled into named, transferable principles. Each one
states *what it is*, *the signal he looks for*, *how to apply it*, and a short
dated example from the corpus. A runnable checklist is at the bottom.

> Use this file to vet any name — including ones he never tweeted about. The
> principles are the durable part; the specific tickers decay.

## Table of contents

1. [Bottleneck hunting (the core lens)](#1-bottleneck-hunting-the-core-lens)
2. [Multi-hop BOM / OSINT supply-chain mapping](#2-multi-hop-bom--osint-supply-chain-mapping)
3. [Signed-contract ARR vs. market-cap mismatch](#3-signed-contract-arr-vs-market-cap-mismatch)
4. [Mag7 customer-concentration filter](#4-mag7-customer-concentration-filter)
5. [The GAAP-margin war](#5-the-gaap-margin-war)
6. [Qualification cycle vs. TTM revenue](#6-qualification-cycle-vs-ttm-revenue)
7. [Dilution / ATM calendar as a disqualifier](#7-dilution--atm-calendar-as-a-disqualifier)
8. [Counterparty / financing-quality spectrum](#8-counterparty--financing-quality-spectrum)
9. [Short-squeeze setup (profitable-grower variant)](#9-short-squeeze-setup-profitable-grower-variant)
10. [Tariff/macro-shock-as-buy](#10-tariffmacro-shock-as-buy)
11. [Institutional lag / dark-pool & flow reading](#11-institutional-lag--dark-pool--flow-reading)
12. [Vega / IV mispricing (options structure)](#12-vega--iv-mispricing-options-structure)
13. [Conviction tiering, sizing, and timing](#13-conviction-tiering-sizing-and-timing)
14. [Anti-patterns he calls out](#14-anti-patterns-he-calls-out)
15. [The checklist (run this on any new name)](#15-the-checklist-run-this-on-any-new-name)
16. [Bottleneck vs. Chokepoint — formal distinction](#16-bottleneck-vs-chokepoint--formal-distinction)
17. [Architecture moat identification](#17-architecture-moat-identification)
18. [News second-order effects](#18-news-second-order-effects)
19. [Vertical-integration roadmap prediction](#19-vertical-integration-roadmap-prediction)
20. [Cross-exposure / dual-theme screening](#20-cross-exposure--dual-theme-screening)
21. [Structured macro filter](#21-structured-macro-filter)
22. [IPO anchor + starter-position scaling](#22-ipo-anchor--starter-position-scaling)

---

## Recent incremental methodology notes after June 8, 2026

- **China AI capability is also a cybersecurity/risk signal, not only a model
  leaderboard signal.** Jun 28 update cites WSJ reporting that Zhipu AI matched
  Anthropic in some cybersecurity exploit benchmarks, framing it as an adverse
  AI-race reset rather than a simple "China model caught up" victory lap. Use
  this as a policy/geopolitical overlay when evaluating AI infra, cyber tooling,
  and China-exposed AI supply-chain names. Source:
  [2071074680253911267](https://x.com/aleabitoreddit/status/2071074680253911267).

---

## 1. Bottleneck hunting (the core lens)

- **What:** Find the single point of failure in a fast-growing supply chain —
  the upstream chokepoint a downstream buyer must pay through rather than design
  around. "Who is the *real* bottleneck?"
- **Signal:** A supplier with sole- or near-sole-source position, pricing power,
  no near-term qualified substitute, in a TAM expanding on AI capex, still small
  cap. He distinguishes *quantity* (how much supply) from *price* (monopoly
  pricing power): "You don't need to produce 3000% more material… just increase
  the prices."
- **Apply:** For any thesis, ask "if this layer stopped shipping, what breaks
  downstream, and is there a second source?" The fewer substitutes and the
  bigger the downstream dependency, the better the asymmetry. He compares each
  new bottleneck to historical price-spike precedents (Neon gas +2000% in 2022;
  Dysprosium +2300% in 2010; HBM 2024-25).
- **Capital-sovereignty overlay:** For European supply-chain chokepoints, he
  treats capital availability and control as part of the bottleneck analysis.
  Underfunded critical monopolies can be sold abroad, while US/strategic capital
  may be needed to keep companies alive and scaling for hyperscaler supply
  chains. May 28 example: ficonTEC framed as a critical chokepoint lost to
  foreign/China-linked ownership because Europe underfunded it.
- **Architecture-transition overlay:** Treat bottleneck hunting as partly a
  judgment call on the next technical architecture shift. May 31 example:
  Serenity said the InP/optical long worked because he acted before consensus
  accepted that optical interconnect would replace copper for AI scale-out.
- **Example:** AXTI (2025-12-26) — "the entire AI industry will likely be
  bottlenecked by AXTI ($700M)…" framing InP substrate control as the chokepoint
  for $15T+ of hyperscaler value. ("Strait of $AXTI" analogy to Strait of
  Hormuz, March 2026.) Jun 25 2026 addendum: he contrasted Japanese companies
  with active monopolies over hyperscaler AI chokepoints at roughly $150M-$350M
  valuations against Silicon Valley AI seed rounds near $200M, reinforcing the
  public-market/private-market valuation-arbitrage version of the chokepoint
  lens.

## 2. Multi-hop BOM / OSINT supply-chain mapping

- **What:** Build a Bill-of-Materials for hyperscaler infrastructure by chaining
  hops from capex commitment down to feedstock, then identify who chokes each
  layer. He notes AI chatbots fail at this because the connections are obscured
  multi-hop.
- **Signal:** Conference slides (OFC, GTC, JP Morgan fireside), investor decks,
  SEC filings, LinkedIn job postings, partner-section changes on startup
  websites, BOM-percentage estimates.
- **Apply:** Map the chain explicitly. Estimate what % of cluster BOM flows to
  the supplier — a cheap component (optical ~8-12% of a TPU BOM) means
  hyperscalers will pay through a price hike rather than cut AI capex. For
  optical-communications theses, require the analyst to describe the whole chain
  from upstream InP substrate through downstream optical-module manufacturers;
  if they cannot do that from memory, treat the conviction as underbuilt.
- **Example:** Ayar Labs quietly removed LITE and MTSI from its website partner
  section, leaving only SIVE (April 2026) — read as Sivers becoming Ayar's
  primary merchant laser supplier, before any press release.

## 3. Signed-contract ARR vs. market-cap mismatch

- **What:** Price stocks on forward ARR implied by signed take-or-pay contracts,
  not trailing multiples. Contract signing flips a name from "watch" to "high
  conviction."
- **Signal:** A multi-year hyperscaler contract worth a large multiple of
  current revenue, against a market cap that hasn't re-rated.
- **Apply:** Compare contracted forward revenue to market cap. If a 300%+ ARR
  contract only moved the stock 45%, the dilution to fund it was "already priced
  in" — the post-announcement dip is the entry. For hypergrowth hardware names,
  do not rely on generic screeners or stale online forward-P/E fields; June 1
  AAOI/SNDK replies emphasize calculating your own forward earnings/ARR from the
  ramp assumptions and call transcripts.
- **Example:** NBIS after the $17B MSFT contract (2025-09): "before $50 NBIS was
  speculation… now it's pure scaling," projecting $5-6B 2026 revenue at ~70%
  margins vs. ~$24-26B market cap.

## 4. Mag7 customer-concentration filter

- **What:** His highest-conviction qualifier early on: "who are the customers?"
  Mag7 presence as a moat/demand signal.
- **Signal:** A small-cap with systemic exposure to multiple Mag7 buyers.
- **Apply:** Use Mag7-customer presence as a *positive* concentration signal for
  demand durability — but pair it with #8 (counterparty quality) and watch the
  flip side: single-customer concentration is a *risk* (see POET losing MRVL).
- **Example:** ALAB launched as "the only small cap with systemic exposure to 5
  of the Mag7" (2025-07-28).

## 5. The GAAP-margin war

- **What:** Compare companies on GAAP gross margin, never cherry-picked non-GAAP
  or single-line margins. A market inefficiency thesis: if most investors
  compare non-GAAP, the honest discloser is systematically undervalued.
- **Signal:** A margin disclosure that strips SBC, depreciation, or restricts to
  one revenue line = uninformative for cross-company ranking.
- **Apply:** Re-rank peers on true GAAP margins before deciding who is "best in
  class." Software/orchestration ownership is the margin wedge in neoclouds.
- **Example:** IREN's "92% gross margins" flagged as hardware-specific non-GAAP
  vs. NBIS's 71.2% GAAP (Nov 2025) — "NBIS's quality is disguised because its
  disclosure is more honest."

## 6. Qualification cycle vs. TTM revenue

- **What:** Don't judge a pre-volume-ramp company by current financials. Enter
  during *qualification* (design wins, foundry partnerships, guidance language),
  before volume shows in reported revenue.
- **Signal:** Conference design wins, foundry qualification, earnings-call
  guidance — TAM expansion at an architectural inflection, not current burn.
- **Apply:** For frontier names, model forward TAM at the inflection, not
  trailing revenue. "Modeling on current revenue is the equivalent of modeling
  Celestial at $50m because of no CPO revenue in 2025."
- **Example:** SIVE, AEHR, LPK, AXTI all entered pre-ramp on qualification
  evidence. "Nobody cares about current earnings unless there's something
  extremely bad" (April 30, re: LPK miss). For SIVE's May 2026 earnings, he
  says the only thing that matters is forward growth: pre-development contract
  revenue and last-quarter results are weak signals for qualification-cycle
  optical suppliers unless they reveal a major flaw.

## 7. Dilution / ATM calendar as a disqualifier

- **What:** Large active ATMs (at-the-market share offerings), especially paired
  with executive SBC awards, are treated as structurally disqualifying — retail
  equity gets diluted to fund the buildout.
- **Signal:** ATM size vs. market cap; SBC running alongside; management track
  record of prior dilution. He reads SEC EDGAR for lockup/dilution terms.
- **Apply:** Treat a big active ATM as a ceiling on the stock. Distinguish
  *destructive* dilution (open-market ATM dumping) from *acceptable* (small
  one-time strategic listing dilution; a strategic investor retiring debt).
- **Example:** IREN $6B ATM at ~$11.7B MC = ~51% dilution overhang → "AMC of
  datacenters," explicit bear (March 2026). Contrast: SIVE's 2.5% NASDAQ-listing
  dilution viewed positively; IQE's MTSI $45M deal positive (retired debt).

## 8. Counterparty / financing-quality spectrum

- **What:** Within one sub-sector, the *tenant's creditworthiness* and the
  *financing structure* determine the equity path, not just the operations.
- **Signal:** Who backstops the contracts? AAA hyperscaler vs. a cash-burning AI
  lab. How is the buildout funded? NVDA funding + convertibles > colo model >
  ATM > credit-card debt.
- **Apply:** Rank neoclouds by financing quality:
  `NBIS (NVDA + convertibles) > CIFR/WULF (colo, GOOGL/AMZN backstop) > IREN
  (ATM) > CRWV (heavy debt interest)`. Flag OpenAI-counterparty exposure
  (ORCL/CRWV) as a risk because OpenAI's FCF can't cover its commitments.
- **Example:** Dec 2025 ORCL/CRWV "OpenAI contagion" selloff called a buying
  opportunity for MSFT/META-backstopped names (NBIS, IREN) while avoiding the
  OpenAI-dependent ones.

## 9. Short-squeeze setup (profitable-grower variant)

- **What:** High short interest on a *profitable, growing* company is an
  anomaly that resolves upward; high SI on a *zombie* is dangerous.
- **Signal:** 35%+ float short with borrow utilization near limits, against
  improving fundamentals and a near-term catalyst. Tracks SI as a squeeze timer,
  not a standalone direction.
- **Apply:** Pair SI with fundamentals. Profitable + growing + trapped shorts =
  asymmetric upside; unprofitable + high SI = avoid.
- **Example:** HIMS at 42% SI on an "11B, profitable, fast-growing company…
  potential to make history on a short squeeze" (2025-09-12). Re-flagged on the
  2026-03 NVO-partnership flip.

## 10. Tariff/macro-shock-as-buy

- **What:** Algorithmic risk-off selloffs on macro headlines are entries when
  the fundamental thesis is committed multi-year capex that doesn't respond to
  the shock within ~12 months.
- **Signal:** A broad -8% to -15% sector flush on a tariff/geopolitical
  headline, with the underlying demand contracted years out.
- **Apply:** Separate "algorithmic risk-off" from "fundamental re-rating." Buy
  the former; respect the latter. He overlays macro as a *tilt* (rate cuts →
  small-cap/growth; war → pre-position oil/defense, then rotate profits into the
  high-beta selloff), not a reason to abandon theses.
- **Example:** Oct 10 2025 tariff escalation — added NBIS leaps at $98.8 into the
  flush, called it "the best entry point of 2025." Caveat: by March 2026 he
  admitted the Iran conflict genuinely hurt his rate-cut-dependent XLU/EWY longs
  — macro can break a thesis when it changes the rate path.

## 11. Institutional lag / dark-pool & flow reading

- **What:** Retail can discover supply-chain chokepoints 4-6 weeks before
  institutions accumulate; X commentary lags fundamentals 1-3 days, institutional
  research 2-4 weeks. The window between data release and narrative absorption is
  the edge.
- **Signal:** Sustained block/dark-pool buying at discounted levels; later
  13F/holdings disclosures confirming the thesis after his public post.
- **Apply:** Treat his (or your) early supply-chain map as the lead; treat later
  analyst upgrades and fund accumulation as *lagging validation*, not new info.
- **Example:** Morgan Stanley ended up a 6.5% holder of SOI, Point72/MTSI bought
  IQE float — all *after* his public theses (April-May 2026). Also reads option
  open-interest/MM flushes as short-term timing.

## 12. Vega / IV mispricing (options structure)

- **What:** Find ETFs/indexes where market makers price implied volatility on
  stale long-run historical averages that no longer reflect new structural
  volatility — then buy long-dated leaps for vega expansion.
- **Signal:** Cheap IV on a name whose realized vol or constituent exposure has
  structurally changed; OTM long-dated leaps for convex leverage.
- **Apply:** Look for "boring" wrappers with hidden new volatility. Rule of
  thumb on entry: prefers low IV (he cites buying calls mainly at ~10-35% IV);
  for XLU he warned "if IV is elevated above 17.5%, probably stay away."
- **Example:** EWY 2028 leaps bought at 32% IV (priced on a decade of flat
  Korean returns) while EWY is effectively 50%+ Samsung/SK Hynix; IV expanded to
  44-47% in a week. May 26 update: EWY calls were up 300%+ / over 4x, with IV
  holding and Samsung/SK Hynix memory exposure still printing. May 28 update:
  EWY 2028 leaps were up 428%+ / 5.2x in three months as IV rose and underlying
  Samsung / SK Hynix memory assets appreciated. June 1 update put the EWY LEAPS
  at +485%, explicitly attributing the move to both IV expansion and directional
  Samsung/SK Hynix memory longs. XLU OTM 2-year leaps at 14-16% IV on the
  AI-power thesis.
  **High-risk, advanced — note this is leveraged options, not appropriate to
  copy without understanding the structure.**

## 13. Conviction tiering, sizing, and timing

- **What:** Explicit tiering (S/A/B/C/D/F lists) and conviction-scaled sizing;
  smaller size on binary microcaps; calls instead of shares when a name could go
  to zero (e.g. China export-ban risk).
- **Signal:** "Fundamentally de-risked" (Mag7 counterparty + locked take-or-pay
  contract) = top tier and bigger size; execution/dilution/binary risk = small
  size or defined-risk options. Explicit "no position" or "for fun" idea posts
  sit below owned thesis posts and should be used mainly to study his process.
- **Apply:** Size to conviction *and* to how binary the outcome is. He repeatedly
  warns: these names move 20%+ a day, "build conviction yourself before you
  enter," "don't have high concentration in small caps." Holds for LTCG when
  catalysts are ≥12 months out. Goes off margin during macro uncertainty.
  Jun 25 2026 update: after a recent "massive drawdown," he called the strategy
  "Diversified Losses" and said CPO exposure was hit the hardest across Foci,
  Msscorp, and adjacent names. Treat this as a live reminder that many
  individually different optical/CPO chokepoint names can still share the same
  factor exposure; diversify by driver, not just ticker count. Later the same
  day he noted memory, indexes, and large-cap semis such as Intel were among the
  only areas not yet crashing, while photonics, space, popular AI, and software
  baskets were down roughly 35-40%; use that as a market-regime filter before
  adding to high-beta AI-adjacent small caps. Jun 26 2026 follow-up framed this
  as a global correction, with Korea/Japan/Taiwan indexes down and $SOI / $RKLB
  examples off 30-40%; when he says he has "no clue when it stops," treat fresh
  high-beta adds as timing-sensitive rather than thesis-confirming.
- **Example:** "Calls are actually safer than shares" on AXTI given China export
  risk (2025-12-30); SIVE flagged "wouldn't put too much concentration into
  them" for average accounts.

## 14. Anti-patterns he calls out

- **Standalone technical analysis** — "TA is snake oil without fundamentals,
  catalysts, macro." "Float and fundamentals > lines on a chart."
- **Credentialed certainty without supply-chain fluency** — May 2026 media
  critique: credentials or background matter less than whether the person can
  reason correctly about CW laser nuances, valuation, InP substrate moats, and
  crucible-processing constraints. Treat confident commentary that conflates
  these layers as noise even when it comes from polished media voices. Jun 23
  example: Bloomberg framing Taiwan's $TSM multiple and $NVDA upstream supply
  chain as a bubble was treated as a repeat of BofA's failed KOSPI bubble call.
- **Insider sales as a bear signal** — explicitly "the dumbest metric" / noise.
- **Conflating supply-chain layers** — substrate ≠ epiwafer ≠ feedstock; foundry
  ≠ module. He corrects these constantly.
- **Reddit/X sentiment** — "IGNORE the sentiment since it's usually wrong."
- **Replying to disinformation campaigns** — May 30 SIVE follow-up: when an
  account spreads apparent disinformation, report it for spam and block it;
  replying only adds engagement.
- **Chasing the already-frontrun event** — buying oil/defense at ATHs *after* a
  war headline instead of pre-positioning.
- **Cult/financial-engineering valuations** — PLTR ("large part of profit is
  just interest income"); SNAP (SBC-funded buybacks masking negative true FCF).

---

## 15. The checklist (run this on any new name)

Score a candidate against his lens. The more "yes", the more it fits his style —
none of this is a buy signal on its own.

1. **Bottleneck?** Is it a sole/near-sole-source chokepoint in a growing chain,
   with no near-term qualified substitute and real pricing power?
2. **Upstream & cheap?** Is it upstream of the obvious "shovel seller," and is
   its component a small % of downstream BOM (so buyers pay through price hikes)?
3. **Chain fluency?** Can you map the exact chain from raw/input layer to module
   or finished-system maker without conflating substrate, epiwafer, foundry,
   laser, transceiver, and module/packaging roles?
4. **Demand driver?** Is the TAM expanding on hyperscaler AI capex (the master
   leading indicator) or physical-AI/robotics capex rather than a legacy/cyclical
   market? May 2026 framing: Jensen Huang's projected "$3-4T annually" AI capex
   by 2030 is the top-down reason tiny upstream chokepoints can re-rate. June 3
   physical-AI framing: Serenity expects the buildout to start scaling over the
   next 3-4 years, with broader labor displacement on a roughly 10-year horizon;
   use this as a long-cycle demand screen, not as a near-term ticker signal. June
   27 update: robotics/humanoid deal count and investment dollars are rising,
   and AI datacenter exposures can have second-order humanoid-ramp overlap
   through memory (DRAM/NAND for inference/storage) and DFB lasers.
5. **Contracts & counterparty?** Are there signed multi-year contracts, and is
   the tenant creditworthy (AAA hyperscaler, not a cash-burning lab)?
6. **Real margins?** Do the GAAP margins (not cherry-picked non-GAAP) support
   the quality claim?
7. **Financing quality?** Any large active ATM + SBC overhang, or worrying debt
   interest? (Disqualifier.) Or is dilution small/strategic/debt-retiring?
8. **Stage?** Is it pre-volume-ramp (qualification design wins) and therefore
   mispriced on TTM revenue, or already crowded/frontrun?
9. **Catalyst & timing?** Is there a dated catalyst (earnings, conference, MSCI
   inclusion, policy/EO) within a tradable window?
10. **Market cap headroom?** Small enough (<~$3B at call for his moonshots) that
   institutional re-rating is still ahead?
11. **Validation lag?** Is institutional/analyst coverage still behind the
    supply-chain evidence (an edge), or already in (priced)?
12. **Risk & sizing fit?** How binary is it (dilution, single-customer, China
    export, restructuring)? Size accordingly; consider defined-risk options.
13. **Disclosure weight?** Did he say he owns it, sized it, avoided it, or has no
    position? Treat no-position / exploratory posts as lower-conviction process
    examples.
14. **Macro overlay?** Does the current rate path / tariff / war regime help or
    hurt this specific thesis right now?

16. [Bottleneck vs. Chokepoint — formal distinction](#16-bottleneck-vs-chokepoint--formal-distinction)
17. [Architecture moat identification](#17-architecture-moat-identification)
18. [News second-order effects](#18-news-second-order-effects)
19. [Vertical-integration roadmap prediction](#19-vertical-integration-roadmap-prediction)
20. [Cross-exposure / dual-theme screening](#20-cross-exposure--dual-theme-screening)
21. [Structured macro filter](#21-structured-macro-filter)
22. [IPO anchor + starter-position scaling](#22-ipo-anchor--starter-position-scaling)

Then: confirm current price and fundamentals, weight using
`track-record.md`, and present as analysis — never as an order.

---

## 16. Bottleneck vs. Chokepoint — formal distinction

- **What:** The word "bottleneck" is used loosely. Serenity distinguishes two
  fundamentally different types of supply-chain constraint. Only one creates true
  pricing power.
- **Signal:**
  - **瓶颈 (capacity bottleneck):** Production capacity limits industry expansion,
    but multiple suppliers exist. Example: Win Semi is a capacity bottleneck for
    laser foundry, but GFS and TSEM also offer SiPh foundry services. The
    constraint is *volume*, not *exclusivity*.
  - **卡脖子 (strategic chokepoint) ✓:** Sole or primary source; remove it and the
    downstream product literally cannot be built. Example: $SIVE CW DFB laser
    arrays — "remove Sivers and you literally cannot build their product, delaying
    roadmaps by years." The constraint is *architecture*.
- **Apply:** For every candidate, ask: "Is this a capacity problem (bottleneck) or
  a structural dependency problem (chokepoint)?" A chokepoint + capacity scarcity
  = simultaneous pricing power. A bottleneck alone is just a cyclical supply
  shortage.
- **Example:** $SNDK doesn't manufacture all NAND but controls Kioxia allocation —
  chokepoint via allocation control, not via production volume.

## 17. Architecture moat identification

- **What:** Distinguish architecture binding from commodity interchangeability. A
  component is a true moat only if replacing it requires redesigning the
  downstream system, not just swapping a part number.
- **Signal:** CW DFB lasers are **not interchangeable** with EML lasers — different
  architecture, different thermal profile, different array configuration. $SIVE's
  lasers are chosen by Ayar, Celestial, and Lightmatter **for architectural
  reasons**, not because they're 10% cheaper. Competitors ($LITE, Furukawa) make
  different architectural choices that don't slot into the same design.
- **Apply:** For any candidate, ask "can the customer swap this out without
  redesigning their product?" If yes → commodity risk. If no → architecture moat.
  Architecture moat → customer stickiness → pricing power → ~60%+ gross margins.
- **Example:** "$LITE has higher power but different architecture — it's not a
  substitute. If you think CW lasers are interchangeable with Furukawa, I don't
  know how to explain this to you."

## 18. News second-order effects

- **What:** A specific mental model: when news breaks, the first-order trade is
  already priced in. The edge is asking "who benefits *second*?" before the market
  connects the dots.
- **Signal:** A headline event → trace the supply chain one or two hops upstream
  from the obvious beneficiary → find the hidden bottleneck that enables the
  obvious beneficiary.
- **Apply:** For every major AI/tech headline, run the table:

  | Event | Second-Order Derivation | Target |
  |-------|------------------------|--------|
  | SpaceX acquires Mesh optical networking | Needs CW DFB laser source | $SIVE |
  | Marvell acquires Celestial | SIVE already mapped to Celestial | $SIVE |
  | OpenAI launches model on Cerebras | Technical validation + endorsement premium | $CBRS |
  | Google compute limits Meta | External neocloud demand rises | $NBIS |
  | MRVL earnings highlight scale-up optical interconnect | CPO theme ascends | $SIVE, $AAOI |

- **Example:** MRVL earnings call mentions scale-up optical interconnect revenue
  doubling → Serenity reads it as CPO volume-ramp confirmation for $SIVE lasers,
  *not* as a primary MRVL trade.

## 19. Vertical-integration roadmap prediction

- **What:** Don't just analyze a company's current product. Predict its 3-5 year
  full-stack evolution using a comparable company's historical path as the
  template.
- **Signal:** Use $LITE's history as the reference path:
  `Laser die → acquire Cloud Lite → vertically integrate → $75B market cap`.
  Then map the candidate's likely path:
  `CW lasers → M&A optical engines → pluggable transceivers → TAM ×N`.
- **Apply:** Current revenue severely understates the candidate if it doesn't
  price in downstream integration value. The laser business alone might be worth
  $X, but M&A into optical engines and pluggables multiplies the TAM.
- **Example:** $SIVE's current laser revenue "severely undervalues" the company
  because it doesn't account for post-M&A downstream integration value. The
  entire optical engine / pluggable TAM is the real prize.

## 20. Cross-exposure / dual-theme screening

- **What:** Intentionally seek companies benefiting from **two megatrends
  simultaneously**. This doubles the probability of a catalyst hitting and
  provides a second chance if one theme temporarily cools.
- **Signal:** A company whose product serves AI datacenter **and** humanoid
  robotics, or automotive **and** humanoid BOM, or memory **and** LiDAR sensing.
- **Apply:** Screen candidates against two independent demand drivers:

  | Ticker | Theme A | Theme B |
  |--------|---------|---------|
  | $SIVE | AI DC optical interconnect | Humanoid LiDAR (via AEVA → Boston Dynamics) |
  | DRAM/NAND | AI training/inference | Humanoid robot storage/inference |
  | Schaeffler | Automotive components | Humanoid robot BOM (~50%) |
  | $JBL | AI DC transceivers | Manufacturing outsourcing |
  | $AEVA | LiDAR sensing | Boston Dynamics humanoid |

- **Example:** "Automotive suppliers are being undervalued because of EV drag, but
  they have humanoid BOM exposure — that's the opportunity." The auto business
  pays the bills; humanoid exposure is a free call option the market ignores.

## 21. Structured macro filter

- **What:** A systematic checklist of macro conditions that tilt the portfolio
  between risk-on and risk-off, rather than treating macro as an afterthought.
- **Signal:**

  **顺风 / Bullish (risk-on, add to high-beta names):**
  - Fed not hiking rates
  - Hyperscaler CapEx continuing to expand
  - Compute supply severely insufficient
  - Robotics investment dollars rising sharply

  **逆风 / Bearish (reduce high-beta, rotate to large-cap/defensive):**
  - Fed rate hike expectations rising
  - China AI distilling US models (regulatory/competitive risk)
  - Chinese humanoid robots entering US market (supply-chain disruption risk)
  - OpenAI's position being challenged (ecosystem risk)

- **Apply:** Overlay this filter before sizing any new position. In a bullish
  macro regime, high-beta small-cap chokepoint names get full size. In a bearish
  regime, reduce small-cap exposure, rotate to large-cap compounders ($TSM,
  memory), or hold cash. Don't fight the macro when it genuinely changes the rate
  path.
- **Example:** March 2026 Iran conflict genuinely hurt rate-cut-dependent XLU/EWY
  longs — macro broke the thesis when the rate path changed.

## 22. IPO anchor + starter-position scaling

- **What:** A concrete position-building method: use the IPO price as a valuation
  floor, enter a small "starter position," and scale up only as information
  confirms the thesis.
- **Signal:**
  - **IPO price anchor:** For newly public companies, the IPO price represents the
    underwriter's fair-value assessment. Buying below or near IPO = built-in
    margin of safety. $CBRS IPO $185, bought at ~$170.
  - **Starter position:** Enter small initially. Don't go full size on a thesis
    that still has unknown unknowns.
  - **Scale with confirmation:** Add to the position only as OSINT discoveries,
    contract announcements, earnings calls, or supply-chain evidence confirms the
    original thesis. Each confirmation = one step up in sizing.
  - **Catalyst required:** Never enter without a dated, identifiable catalyst
    (earnings, conference, MSCI inclusion, policy announcement) within a tradable
    window.
- **Apply:** The sequence: 1) Identify chokepoint → 2) Build OSINT supply-chain
  map → 3) Find a dated catalyst → 4) Enter starter position → 5) Wait for
  confirmation → 6) Scale up → 7) Wait for next confirmation → repeat. Never skip
  from step 1 to full size.
- **Anti-pattern:** "Don't post new positions during trading hours" — compliance
  protection for himself and his followers. Treat as a reminder that position
  disclosure ≠ immediate entry signal for followers.

---

## 15. The checklist (run this on any new name)

Score a candidate against his lens. The more "yes", the more it fits his style —
none of this is a buy signal on its own.

1. **Bottleneck or Chokepoint?** Distinguish: is this a capacity bottleneck
   (multiple suppliers, volume constraint) or a strategic chokepoint
   (sole/primary source, architectural dependency)? Only chokepoints have true
   pricing power. (§16)
2. **Architecture moat?** Can the customer swap this out without redesigning
   their product? If yes → commodity risk. If no → genuine moat with customer
   stickiness. (§17)
3. **Upstream & cheap?** Is it upstream of the obvious "shovel seller," and is
   its component a small % of downstream BOM (so buyers pay through price hikes)?
4. **Chain fluency?** Can you map the exact chain from raw/input layer to module
   or finished-system maker without conflating substrate, epiwafer, foundry,
   laser, transceiver, and module/packaging roles?
5. **Demand driver?** Is the TAM expanding on hyperscaler AI capex (the master
   leading indicator) or physical-AI/robotics capex rather than a legacy/cyclical
   market?
6. **Second-order exposure?** If a major headline hits tomorrow, would this
   company benefit as the hidden upstream enabler of the obvious winner? (§18)
7. **Vertical-integration optionality?** What does this company look like in 3-5
   years if it follows a LITE-style integration path? Does current valuation
   ignore downstream TAM? (§19)
8. **Cross-exposure / dual theme?** Does it benefit from TWO independent
   megatrends simultaneously? This doubles catalyst probability. (§20)
9. **Contracts & counterparty?** Are there signed multi-year contracts, and is
   the tenant creditworthy (AAA hyperscaler, not a cash-burning lab)?
10. **Real margins?** Do the GAAP margins (not cherry-picked non-GAAP) support
    the quality claim?
11. **Financing quality?** Any large active ATM + SBC overhang, or worrying debt
    interest? (Disqualifier.) Or is dilution small/strategic/debt-retiring?
12. **Stage?** Is it pre-volume-ramp (qualification design wins) and therefore
    mispriced on TTM revenue, or already crowded/frontrun? (§6)
13. **Catalyst & timing?** Is there a dated catalyst (earnings, conference, MSCI
    inclusion, policy/EO) within a tradable window?
14. **IPO anchor?** If recently public, does the current price provide margin of
    safety relative to the IPO price? (§22)
15. **Sizing discipline?** Start with a starter position. Scale only on
    confirmation. Never go from discovery to full size in one step. (§22)
16. **Market cap headroom?** Small enough (<~$3B at call for his moonshots) that
    institutional re-rating is still ahead?
17. **Validation lag?** Is institutional/analyst coverage still behind the
    supply-chain evidence (an edge), or already in (priced)?
18. **Risk & sizing fit?** How binary is it (dilution, single-customer, China
    export, restructuring)? Size accordingly; consider defined-risk options.
19. **Disclosure weight?** Did he say he owns it, sized it, avoided it, or has no
    position? Treat no-position / exploratory posts as lower-conviction process
    examples.
20. **Macro overlay?** Rate path bullish or bearish? Hyperscaler CapEx expanding?
    China AI / robotics entering US? Adjust sizing to macro regime. (§21)

Then: confirm current price and fundamentals, weight using
`track-record.md`, and present as analysis — never as an order.
