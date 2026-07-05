---
name: token-audit
description: 审计并优化当前工作目录的 Claude Code token 开销。当用户要求 review token 使用、优化 CLAUDE.md、精简项目配置以节省 token 时使用。
---

# Token 开销审计与优化

## 流程

### 第 1 步：测量基线

优先询问用户是否愿意运行 /context 并粘贴结果（最精确）。
若用户不提供，则改用静态估算：派 sub-agent 用 wc -c 统计所有
自动加载文件（各级 CLAUDE.md、@import 文件）的字节数，
按 3.5 字符/token 估算；MCP server 按每个 2k token 估算。
在报告中注明数据是实测还是估算。

### 第 2 步：派 sub-agent 扫描（不要在主上下文直接读所有文件）

用 Task 工具派一个 general-purpose sub-agent，让它收集并只返回摘要：

- 所有 CLAUDE.md 的路径、行数、内容分类（命令/规范/文档/历史信息）
- 所有 @import 引用及被引文件大小
- .claude/ 下的 settings、agents、skills、hooks 清单
- .mcp.json 中配置的 MCP servers
sub-agent 返回结构化摘要，禁止返回文件全文。

### 第 3 步：逐项诊断

对 CLAUDE.md 每部分内容按此标准分类：

- [保留] 命令、硬约束、Claude 无法推断且高频需要的信息
- [下沉] 详细规范/流程 → 建议改为项目级 skill 按需加载
- [删除] 可从代码推断的内容、过时信息、解释性文档
其他检查：
- @import 的大文件 → 改为 skill 或在 CLAUDE.md 用一句话指路（"部署规范见 docs/deploy.md，需要时再读"）
- 低频 MCP server → 建议移除或改用 CLI
- hooks 输出是否冗长

### 第 4 步：输出报告

格式：

1. 基线 token 分布
2. 问题清单（按预估节省量降序）
3. 每项给出具体修改建议（含改写后的文本）
4. 预估总节省

### 第 5 步：执行

经用户确认后执行修改。修改 CLAUDE.md 时保持指令简洁、祈使句、无解释性废话。
完成后提示用户重启会话并再次 /context 验证效果。

## 红线（保证质量不下降）

- 不删除构建/测试/lint 命令
- 不删除会导致错误行为的硬约束（如"禁止直接改 generated/ 目录"）
- 拿不准的内容标记为"待确认"而非直接删
