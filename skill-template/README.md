# Skill Template

新建一个 Kairos Skill 的最小骨架。复制本目录，改 4 处，即可拥有完整的基础设施。

---

## 为什么有这个模板

每个 Kairos Skill 都需要相同的脚手架：确定性渲染入口、字体校验、CDN 离线校验、字体 CSS 生成。这些脚本是通用的（用 `Path(__file__).resolve().parents[1]` 自动定位技能根，不绑定技能名），所以提取成模板，避免每次手写。

---

## 用法（5 步）

1. **复制目录**

   ```bash
   cp -r skill-template kairos-<你的技能名>
   ```

2. **改 SKILL.md** — 替换 `<skill-name>`、触发词、工作流。

3. **加字体** — 把 woff2 文件放进 `assets/fonts/`，编辑 `assets/fonts/fonts.json` 注册每款字体。

4. **生成字体 CSS** — 运行 `python3 scripts/build_font_css.py`，它会读 `fonts.json` 生成 `fonts.css`。

5. **跑校验** —

   ```bash
   cd kairos-<你的技能名>
   python3 scripts/verify_fonts.py     # 字体完整性
   python3 scripts/verify_assets.py    # CDN 离线校验
   ```

   两项都通过后，在根 `skills.json` 注册新技能（见根 `CONTRIBUTING.md` 第 3 节）。

---

## 目录说明

```
skill-template/
├── SKILL.md                  # 技能指令骨架（YAML frontmatter + 管线）
├── scripts/
│   ├── render.py             # 确定性渲染入口模板（TODO 标记待实现）
│   ├── verify_assets.py      # CDN 引用扫描（通用，直接可用）
│   ├── verify_fonts.py       # 字体完整性校验（通用，直接可用）
│   └── build_font_css.py     # 由 fonts.json 生成 @font-face CSS（通用，直接可用）
└── assets/
    ├── fonts/
    │   └── fonts.json        # 字体注册表模板
    └── placeholders/         # 放本地 SVG 占位符
```

带 "通用" 标记的脚本无需改动即可运行——它们靠脚本自身的路径定位技能根。

---

## 设计约束

继承自根 `AGENTS.md` 的资产策略：

- 所有运行时资产（字体、图片）必须本地打包，**禁止 CDN 引用**。
- 占位符用本地 SVG，不用 `placehold.co`。
- 字体用 woff2 格式，声明在 `fonts.json` 里。
- `verify_assets.py` 是门禁：任何 CDN 引用都会让它退出码 1。
