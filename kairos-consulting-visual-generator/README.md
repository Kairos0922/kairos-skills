# kairos-consulting-visual-generator

`kairos-consulting-visual-generator` 把用户输入的商业、学术或策略主题直接转化为高端咨询风视觉图。它用于封面和信息图两类出图任务：封面强调留白、核心词、标题重构和单一主隐喻；信息图强调结构、模块、阅读路径、层级关系和结论表达。

这个 skill 的重点不是盲目默认，而是先确认需求是否足够清楚。主题、用途、画幅等关键信息不足时，agent 应先追问；信息足够后，再形成内部视觉简报并生成最终画面。

## 适用场景

| 输入 | 输出 | 适合用户 |
| --- | --- | --- |
| 主题、用途、画幅、语言、语境 | 咨询风封面或信息图生成指令 | 内容创作者、咨询顾问、产品经理、研究员、AI agent |
| 长标题或复杂商业主题 | 核心词、完整标题、标签和主隐喻 | 需要快速生成高级商业视觉的人 |

可用于 X 封面、微信公众号文章封面、小红书/小绿书封面、海报封面、PPT 封面、商业报告封面、作品集封面、信息图、咨询分析页、方法论图、流程图和矩阵图。

## 工作流

1. 读取用户主题、用途、画幅、语言和补充语境。
2. 判断信息是否足够；缺少会改变结果的字段时，先追问 1-3 个关键问题。
3. 判断是封面逻辑还是信息图逻辑。
4. 形成内部 `Visual Brief`：核心词、完整标题、标签、短结论、锚点、构图模型、禁用项。
5. 根据场景和语境选择一个主商业隐喻；脚本只能作为辅助建议。
6. 将文字和隐喻融合成咨询风画面。
7. 直接调用宿主 agent 的图像生成能力输出最终画面，并按 QA 清单检查。

该 skill 不保存图片、不配置模型、不绑定 provider，也不管理 API key。图像生成由宿主 agent 环境负责。

详细方法论见 `references/consulting_visual_methodology.md`。

## 可选辅助脚本

稳定效果的核心是 `SKILL.md` 和 `references/consulting_visual_methodology.md` 中的方法论。脚本只是辅助检查，不是主要创作方式。

先检查输入是否足够：

```bash
python3 scripts/select_metaphor.py \
  --check-intake \
  --title "增长" \
  --usage "封面"
```

如果 `ready` 为 `false`，先向用户追问 `questions`，不要生成最终画面。

查看初始隐喻建议：

```bash
python3 scripts/select_metaphor.py \
  --title "AI Agent 商业化增长路径" \
  --usage "咨询分析页" \
  --ratio "16:9" \
  --context "B2B SaaS, 产品战略"
```

JSON 输出包含：

- `metaphor`：选中的单一主隐喻。
- `reason`：选择理由。
- `matched_keywords`：命中的关键词。
- `mode`：`cover` 或 `infographic`。
- `composition_hint`：构图提示。

如果脚本建议和用户语境冲突，以视觉简报、用途和专业判断为准。

## 验证

从 skill 目录运行：

```bash
PYTHONPYCACHEPREFIX=.pycache python3 -m py_compile scripts/select_metaphor.py
python3 scripts/select_metaphor.py --check-intake --title "增长" --usage "封面"
python3 scripts/select_metaphor.py --title "风险治理体系" --usage "商业报告封面"
python3 scripts/select_metaphor.py --title "用户转化漏斗优化" --usage "信息图"
```

从仓库根目录运行：

```bash
python3 -m json.tool skills.json >/dev/null
```

## 维护说明

- `SKILL.md` 是 agent 面向的主工作流和视觉规则。
- `references/consulting_visual_methodology.md` 是视觉总监方法论、隐喻语法和 QA 清单。
- `scripts/select_metaphor.py` 保存可重复的 intake 检查和初始隐喻建议，不是最终设计裁判。
- 新增隐喻时，同步更新 `SKILL.md`、`references/consulting_visual_methodology.md`、脚本中的 `METAPHORS` 和本文档。
- 不要加入本机路径、生成缓存、外部 provider 配置或密钥。
