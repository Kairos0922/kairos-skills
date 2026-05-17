---
title: Connect Claude to the tools you use
---

:::lead
May 20, 2024　·　Connectors
:::

# Connect Claude to the tools you use

Connectors bring the tools and data you rely on into Claude, so you can work with context that matters.

:::figure
![Mountain lake in mist](https://placehold.co/1280x720/e8e3da/7f7a72.png?text=Claude+Landscape)
A quiet landscape image supports context without becoming decoration.
:::

Claude works best when it has the right context. Connectors let you securely connect Claude to external systems-like your internal tools, documentation, and data sources.

> [!NOTE]
> Connectors follow the Model Context Protocol (MCP), an open standard that helps AI systems securely access external data.

:::pullquote
The best AI systems don't replace your tools — they integrate with them.
:::

## 01 Get started in minutes

You can set up a connector in just a few steps.

1. Choose a tool or service
2. Authorize the connection
3. Start using it in Claude

```bash
curl -X POST https://api.anthropic.com/v1/connectors \
  -H "Authorization: Bearer $ANTHROPIC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "notion",
    "type": "oauth",
    "config": { ... }
  }'
```

## 02 What you can connect

:::soft-list
- Knowledge bases
- Project management tools
- Internal documentation
- Databases and warehouses
- And more
:::

### Best practices

- [x] Start with one connector
- [x] Use least-privilege permissions
- [x] Keep credentials secure
- [ ] Review and refine access

## 03 Supported auth types

| Auth type | Description | Best for | Status |
| --- | --- | --- | --- |
| OAuth 2.0 | Secure user authorization | SaaS tools | Supported |
| API Key | Simple token-based auth | Internal APIs | Supported |
| Custom | Custom headers or flows | Advanced use cases | Beta |

:::figure
![Sand dunes in soft light](https://placehold.co/1280x360/ede9e1/817b73.png?text=Claude+Image+Band)
Wide imagery should feel quiet, tonal, and supportive.
:::

:::insight
Connectors unlock Claude's full potential by bringing your world into the conversation.
:::

---

:::closing-note
Design for clarity first: use structure, spacing, and quiet contrast to make complex systems understandable.
:::
