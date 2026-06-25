---
name: <skill-name>
description: |
  在此处写触发描述：当用户需要……时加载。触发词包括："……"、"……"。
  不适用于……。
metadata:
  version: "0.1.0"
---

# <skill-name>

## Purpose / 目的

一句话说明这个 skill 解决什么问题。核心原则：**确定性优先**——AI 只做编辑判断，视觉/样式决策由代码和契约锁定。

## Core Principle / 核心原则

- **LLM 做**：编辑判断（结构、层级、重点、选主题/风格）。
- **代码做**：渲染、字号、颜色、间距、验证。
- **LLM 不许做**：直接输出 HTML/CSS/`style`/`class`。

## Pipeline / 管线

```
用户输入 → LLM 编辑判断 → render.py 渲染（确定）→ verify 验证（确定）→ 输出
```

TODO: 在此描述你技能的具体管线阶段。

## Themes / 主题（如有）

如果有主题系统，在此列出，并把主题 JSON 放进 `themes/`。每个主题是一份视觉哲学，不是颜色包。

## Validation / 验证

```bash
python3 scripts/verify_fonts.py      # 字体完整性
python3 scripts/verify_assets.py     # CDN 离线校验
# TODO: 加入你技能的渲染验证脚本
```

## Output Contract / 输出契约

TODO: 描述输出格式、版本化目录约定（如 `~/.<skill-name>/<slug>/vNNN/`）。
