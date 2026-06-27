# Loop 范例库 / Example Library

这些是各场景的真实 loop 范例，用来给用户举例、或作为骨架起点。注意每个范例都体现了「可观察目标 + 可跑的验证 + 明确停止 + 一次一个有界动作」。

---

## 编程 / Engineering

### Ship PR Until Green（CI 跑到绿）

```
Start the "Ship PR Until Green" loop.
Goal: PR is open with all CI checks passing
Max iterations: 10
Between iterations run: gh pr checks
Exit when: all PR checks are success
Each iteration: implement the change, test locally, push, and fix CI until green.
Ask before: nothing (working on a feature branch)

Self-pace this loop. After each iteration, run the check command, read the output,
and only continue if the exit condition is not met. Stop when checks pass, max
iterations is reached, or there's no measurable progress. Give a short status update
each pass. Never report a failing build as success.
```

设计理由：CI 的通过/失败是天然的客观验证，状态由 `gh pr checks` 输出提供，10 轮上限防止在同一个错误上空转。

---

## 测试 / Testing & Quality

### Quality Streak（质量连胜）

```
启动「质量连胜」循环。
目标：最近 [N] 个真实场景连续通过质量门槛
最多迭代：直到连续 [N] 次通过
每轮之间运行：在一致条件下跑下一个真实场景，保留结果
满足以下条件时退出：连续 [N] 个场景达到既定质量门槛
每轮动作：跑一个场景；若失败，记录它、补回归和 benchmark 覆盖、修复、验证修复，然后把连胜计数清零
需要批准：无

自定步调运行。开跑前先定好 [N] 和质量门槛，场景分布要有代表性。
绝不为了维持连胜而降低门槛或回避难题。连续无进展时停止求助。
```

设计理由：失败清零的机制保证 loop 真的在学习而不是碰运气；明确"不许降低门槛"防止 AI 用作弊方式满足退出条件。

---

## 安全 / Security

### npm Audit Fix（依赖漏洞修复）

```
Start the "npm Audit Fix" loop.
Goal: no high or critical npm audit vulnerabilities
Max iterations: 10
Between iterations run: npm audit --audit-level=high && npm test
Exit when: npm audit reports no high/critical issues and tests pass
Each iteration: pick ONE high/critical advisory, apply the safest fix, run tests, repeat.
Ask before: nothing (changes are in a branch, reviewed via PR later)

Self-pace this loop. Fix findings one at a time with test verification — NOT a blind
`npm audit fix --force`. Stop when audit is clean, max iterations is reached, or a fix
can't pass tests. Never report remaining vulnerabilities as success.
```

设计理由：一次只修一个 + 每次跑测试，避免破坏性批量操作；把"修复"和"不破坏现有功能"两个信号绑在一起验证。

---

## 文档 / Docs

### Docs Sweep（文档核对）

```
启动「文档核对」循环。
目标：文档与当前实现一致，并产出一个可评审的 PR
最多迭代：无固定上限，连续无进展时停止
每轮之间运行：对照代码、配置、命令、实际行为，检查文档是否还准确
满足以下条件时退出：所有过时文档已更新，命令/链接/示例已对照仓库验证，PR 已开
每轮动作：找出一处文档漂移，只更新过时内容，验证改动
需要批准：开 PR 前确认范围（不要为了制造活动去重写本来正确的文档）

自定步调运行。把范围严格绑定在真实的实现变更上。每轮给简短状态。
```

设计理由：把文档绑定到实现而非记忆；要求产出 PR 创造了可见 diff 和评审点；明确"不要重写正确的文档"防止无意义改动。

---

## 运维 / Maintenance

### Flaky Test Hunter（不稳定测试排查）

```
Start the "Flaky Test Hunter" loop.
Goal: identify and fix the flaky test causing intermittent CI failures
Max iterations: 8
Between iterations run: run the suspect test 20 times and count failures
Exit when: the test passes 20/20 runs across two consecutive iterations
Each iteration: form ONE hypothesis about the flake source, apply a targeted fix, re-run.
Ask before: nothing

Self-pace this loop. Record each hypothesis and its result so you don't repeat a
ruled-out cause. Stop when stable, max iterations is reached, or hypotheses are
exhausted with no progress. Never report a still-flaky test as fixed.
```

设计理由：重复运行 20 次是把"偶发"变成可观察信号的关键；记录已排除的假设是状态记忆的典型用法。

---

## 反例：这不该做成 Loop

用户："帮我写个 loop，每天读一篇行业新闻然后总结给我。"

这不是 loop，因为**新一轮的反馈无法改变下一步动作**——每天的总结是独立的一次性任务，没有"上一轮失败→这一轮改进"的迭代结构。它更适合：一段固定的总结 prompt + 一个定时触发器（这是自动化调度，不是 loop）。

正确回应：诚实指出它是"定时执行的一次性 workflow"，给出那段总结 prompt 和设定定时任务的建议，而不是硬包装成循环。

---

## 反例：混合请求 —— 拆开，只循环该循环的部分

用户："我要做个 Agent infra 项目（记忆、上下文等模块）。先从产品和架构出一份设计方案。第一阶段只实现底座 + 记忆模块，用 Python + LanceDB，支持向量/BM25/混合检索 + rerank。"

这条请求**捆了两件性质不同的事**，不能整体判定：

- **出设计方案** —— 不是 loop。设计好不好是人的主观评审，没有能跑的客观检查在每轮告诉 AI"达标了"。新一轮反馈不构成"客观信号驱动下一步"。→ 用一次性 prompt 产出，人来评审迭代。
- **实现第一阶段** —— 是 loop 候选。记忆检索能力（向量/BM25/混合/rerank）可以用**固定的召回 eval** 客观验证（如 20 条"存入→检索"场景，混合检索 recall@5 ≥ 阈值、rerank 后 top-1 命中），每轮按失败原因改进。这才有迭代内核。

关键点：**同一个项目，不同阶段 loop 性质会变**。用户当下只要设计方案，就别急着设计实现 loop——先交付那段一次性的设计 prompt，并告诉他等方案定稿、进入实现阶段时，再回来把"记忆检索跑到 eval 达标"做成 loop。

正确回应：先分诊拆开，对"设计方案"给一次性 prompt，对"实现阶段"说明它将来适合做成 loop 及验证标准长什么样——而不是把整个项目硬塞进一个循环。

