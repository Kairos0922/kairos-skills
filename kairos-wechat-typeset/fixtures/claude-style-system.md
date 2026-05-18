---
title: 把 Claude 接入你正在使用的工具
---

:::lead
2026 年 5 月 18 日　·　连接器指南
:::

# 把 Claude 接入你正在使用的工具

连接器把团队已经在使用的工具、文档和数据带入 Claude，让一次对话可以基于真实上下文展开。

:::figure
![雾中的山湖](https://placehold.co/1280x720/e8e3da/7f7a72.png?text=Claude+Landscape)
安静的图像只承担氛围和语境，不喧宾夺主。
:::

Claude 最适合处理那些需要上下文的任务。通过连接器，你可以把内部知识库、项目管理工具、数据仓库和文档系统安全地接入 Claude。

> [!NOTE]
> 连接器遵循 Model Context Protocol（MCP）。它是一套开放标准，用来帮助 AI 系统安全地访问外部数据。

:::pullquote
好的 AI 系统不是替代工具，而是把工具之间的上下文重新组织起来。
:::

## 01 几分钟内开始使用

第一次接入不需要设计复杂流程。先选一个高频工具，确认权限边界，再让 Claude 基于真实数据回答问题。

1. 选择一个工具或服务
2. 授权访问所需范围
3. 在 Claude 中开始使用上下文

```bash
curl -X POST https://api.example.com/v1/connectors \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "knowledge-base",
    "type": "oauth",
    "scope": "read:docs"
  }'
```

## 02 适合接入哪些内容

:::soft-list
- 产品知识库
- 项目管理系统
- 内部技术文档
- 数据库与数据仓库
- 客服工单和用户反馈
:::

### 接入前的检查清单

- [x] 从一个连接器开始验证价值
- [x] 只开放任务所需的最小权限
- [x] 明确凭证保存和轮换方式
- [ ] 定期复查访问范围

## 03 常见授权方式

| 授权方式 | 说明 | 适用场景 | 状态 |
| --- | --- | --- | --- |
| OAuth 2.0 | 用户级安全授权 | SaaS 工具 | 推荐 |
| API Key | 简单的令牌访问 | 内部服务 | 可用 |
| 自定义鉴权 | 自定义请求头或流程 | 高级集成 | 评估中 |

:::figure
![柔和光线下的沙丘](https://placehold.co/1280x360/ede9e1/817b73.png?text=Claude+Image+Band)
横向图像应该服务于节奏，而不是成为页面的装饰中心。
:::

:::insight
连接器真正释放的不是某个工具的能力，而是组织内部上下文的可用性。
:::

---

:::closing-note
先为清晰而设计：用结构、间距和克制的对比，让复杂系统变得容易理解。
:::
