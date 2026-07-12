---
name: paper-to-xhs
description: 论文一条龙：从读论文 → 深度解析 → PPT演示文稿 → 手机卡片 → 小红书发布。当用户说"把这篇论文做成PPT发小红书""论文一条龙""从论文到发布"时触发。
---

# Paper to XHS — 论文到小红书一条龙

将一篇学术论文从阅读到发布小红书的完整自动化流程。

## 流程总览

> **输出约定**：每篇论文在 `output/` 下创建独立子文件夹，以论文简称（paper_slug）命名。
> 例如一篇论文简称 `my-paper` → `output/my-paper/`，所有产物都在该目录下。

```
论文 PDF → 深度解析(HTML) → 组会PPT(HTML) → 社交卡片(HTML) → 图片导出 → 小红书发布
  │              │                │                   │              │            │
  │ paper-analyzer│ frontend-slides│ A: guizang-card   │ Playwright │ post-to-xhs │
  │  (academic)   │  (Electric Studio)│ B: frontend-slides │  截图     │  fill-publish│
  │  [MinerU API] │                │                   │              │            │
```

## 并行执行策略

Step 2（组会 PPT）和 Step 3（社交卡片）互不依赖——两者都只需要 Step 1 的论文解析结果。Step 3 提供**两种卡片方案**，可二选一或都跑：

- **Step 3A: guizang 社交卡片** — Editorial Magazine × E-ink，1080×1440，杂志质感
- **Step 3B: frontend-slides 手机卡片** — 暖色卡片风，390×844，轻量快速

```
论文 PDF → 深度解析(HTML) ─┬→ 组会PPT(HTML) ───────────→ 图片导出 → 小红书发布
                           │    (Agent: ppt-generator)
                           │
                           ├→ guizang社交卡片(HTML) ────→ 图片导出
                           │    (Agent: guizang-card-generator)
                           │
                           └→ 手机卡片(HTML) ────────────→ 图片导出
                                (Agent: mobile-card-generator)
```

### 执行方式

Step 1 完成后，最多三个 Agent 并行启动：

```
Agent(subagent_type="general-purpose", description="Generate PPT HTML",
  prompt="基于 {paper_analysis_path} 生成 19 页组会 PPT...")
Agent(subagent_type="general-purpose", description="Generate guizang social cards HTML",
  prompt="基于 {paper_analysis_path} 生成 8 页 guizang 社交卡片...")
Agent(subagent_type="general-purpose", description="Generate mobile cards HTML",
  prompt="基于 {paper_analysis_path} 生成 8 页手机卡片...")
```

### Subagent Prompt 要点

每个 subagent 的 prompt 必须**自包含**，包含以下内容：

1. **论文解析文件路径**（`output/<paper_slug>/paper_analysis.html`）
2. **完整风格参数**（见 Step 2/3 的关键决策表）
3. **幻灯片结构**（19 页 / 8 页的详细结构）
4. **必要的技术约束**（viewport-base.css、clamp()、overflow:hidden 等）
5. **输出文件路径**

> 具体 prompt 模板见下方各 Step 的 "Subagent Prompt" 折叠区。

---

## 前置条件

- Python venv: `.venv`
- Playwright 已安装且 Chromium 已就绪
- 小红书已登录（`post-to-xhs` skill）
- 输出根目录: `output\`
- **每篇论文创建独立子文件夹**，以论文简称命名（如 `onerec-v2`、`lora`、`transformer`），方便多篇论文管理
- 输出目录示例: `output/<paper_slug>/`（该论文所有产物都在此目录下）

---

## Step 1: 论文解析（paper-analyzer-another）

paper-analyzer-another 使用 **MinerU Cloud API** 高精度解析 PDF（文本+公式+表格+图片一步到位），无需额外抓取 arxiv 网页。

### 调用方式

直接在当前会话中 invoke paper-analyzer 技能：

```
Skill(skill="paper-analyzer", args="<arxiv_url 或 PDF 路径>")
```

paper-analyzer（即 paper-analyzer-another，name 注册为 `paper-analyzer`）会自动完成：
1. PDF 下载 → MinerU API 解析 → 输出 `full.md` + `images/`
2. MinerU 图片分类（架构图/实验结果→必须嵌入，公式片段→LaTeX优先，表格→可选）
3. 论文信息提取 → `paper_info.json`
4. 风格询问（默认 academic）
5. HTML 输出 → `output/<paper_slug>/paper_analysis.html`

> 不要手动用 Agent prompt 重新描述 paper-analyzer 工作流——这样会导致过时的 arxiv HTML 抓取流程被重复执行。直接 `Skill` 调用即可，paper-analyzer-another 的 SKILL.md 已有完整的工作流定义。

### 输出产物（paper-analyzer-another 产出）
- `output/<paper_slug>/paper_analysis.html` — 论文深度解析 HTML（后续步骤的输入）
- `output/<paper_slug>/full.md` — MinerU 提取的完整 markdown
- `output/<paper_slug>/images/` — MinerU 提取的论文配图

### academic 学术型硬标准（paper-analyzer-another 自动遵循）
- 字数 ≥ 4000
- 段落 ≥ 20
- 论文公式引用 ≥ 5 处（KaTeX 渲染：$$...$$）
- 论文配图嵌入 ≥ 3 张（架构图 + 实验结果 + 消融对比）
- 论文图/表引用 ≥ 3 处（标注 Figure/Table 编号）
- 实验数据表格 ≥ 2 张
- 指出局限 ≥ 2 处（至少 1 处作者自述）
- 代码分析 ≥ 2 段（如有代码）

### 文章结构（9 段式，paper-analyzer-another 自动遵循）
1. 论文元信息（标题·作者·链接·代码状态）
2. 一句话总结（<100字）
3. 研究背景与动机（4-5段）
4. 预备知识（2-3段，如需要）
5. 方法详解（8-10段，每个创新点含：问题→方法→为什么有效→公式）
6. 实验分析（4-6段，配≥2张表格+深入解读）
7. 讨论（2-3段，适用边界+未解决问题）
8. 局限分析（2-3段，作者自述≥1处+独立判断≥1处）
9. 结论（1-2段，凝练贡献+展望）

### 写法要求（paper-analyzer-another 自动遵循）
- 每个公式后跟"人话"解释
- 引用论文 Figure/Table/Section 编号
- 表格数据要有解读，不只贴数据
- 数学符号首次出现要解释含义
- 禁止 AI 套话："深入探讨""至关重要""值得注意的是"

### 注意事项
- 如果论文来自 arXiv 且 PDF 有密码保护，优先用 HTML 版本：`curl -sL "https://arxiv.org/html/<paper_id>"`（MinerU 无法解析加密 PDF 时的降级方案）
- 代码克隆：`git clone --depth 1 <repo_url> /tmp/paper_code`
- Agent 已指定 academic 风格，不需要再询问用户
- 输出路径中的 `<paper_slug>` 需替换为实际论文简称
- **配图目录**：MinerU 提取的图片在 `output/<paper_slug>/images/`，重命名后拷贝到 `figures/` 目录引用

---

## Step 2: 组会 PPT（frontend-slides）

### 调用方式

使用 `Agent` 工具调用 frontend-slides 生成 PPT。prompt 必须自包含，见下方 Subagent Prompt 模板。

### 关键决策（Phase 1 询问）
| 选项 | 组会场景推荐值 |
|------|---------------|
| 用途 Purpose | **组会汇报** |
| 页数 Length | **详细 15-20 页** |
| 内容 Content | 内容已准备好（已有论文解析结果） |
| 编辑 Editing | **Yes (Recommended)** 可在浏览器改文字 |

### 关键决策（Phase 2 风格选择）
| 选项 | 组会场景推荐值 |
|------|---------------|
| 感觉 Vibe | **专业/可信** (Impressed/Confident) |
| 预设 Preset | **Electric Studio**（深色+蓝色强调+分栏布局） |

### Electric Studio 风格特征
- 字体：Manrope（Google Fonts）
- 配色：深色背景 `#0a0a0f` + 蓝色强调 `#4361ee`
- 布局：封面分栏（左暗右蓝），内容页左侧强调竖线
- 适合：学术汇报、技术分享

### Subagent Prompt 模板

```
你需要基于论文解析 HTML 创建一份组会 PPT。请先读取论文解析文件，根据论文内容设计幻灯片结构，再生成 HTML。

## 输入
- 论文解析: output\<paper_slug>\paper_analysis.html
- 论文配图: output\<paper_slug>\figures\ （如有，用 Read 查看）
- 用 Read 工具读取论文解析文件获取内容；配图可直接查看

## 幻灯片结构设计原则（先设计再生成）
根据论文内容自行设计 18-20 页的结构。必须覆盖以下模块：
- 封面（标题+作者+会议/机构）
- 问题背景（1-2页：领域问题 + 现有方法局限）
- 核心方法（5-7页：每个创新点 1-2 页，含问题→方法→公式→为什么有效）
- 实验分析（3-4页：实验设置 + 主要结果表 + 消融/对比分析）
- 讨论与局限（2-3页）
- 总结（1页）

⚠️ 不要照搬下方模板的具体内容——那个只是格式示意。实际内容必须来自论文解析文件。

## 风格参数
- 用途: 组会汇报
- 页数: 18-20 页（根据论文复杂度调整）
- Vibe: 专业/可信 (Impressed/Confident)
- 预设: Electric Studio（深色背景 #0a0a0f + 蓝色强调 #4361ee + Manrope 字体 + 分栏布局）
- 编辑: Yes，内嵌 inline editing
- 必须读取 viewport-base.css、html-template.md、animation-patterns.md（路径: ~/.claude/skills/frontend-slides/）

## 技术约束
- 每页 height: 100vh; overflow: hidden;
- 字体用 clamp()，图片 max-height: min(50vh, 400px)
- 如有论文配图（figures/ 目录），可 base64 嵌入关键图表到幻灯片中
- 输出: output\<paper_slug>\presentation.html
```

### 注意事项
- **必须**先读取 `viewport-base.css`、`html-template.md`、`animation-patterns.md`
- 每页必须 `height: 100vh; overflow: hidden;`
- 字体必须用 `clamp()`，图片 `max-height: min(50vh, 400px)`
- **Agent 必须先读论文解析，根据内容自定结构，不要用任何预设的论文专属页面**
- 可从 `figures/` 目录读取配图嵌入关键幻灯片

---

## Step 3: guizang 社交卡片（guizang-social-card-skill）

### 调用方式

使用 `Agent` 工具调用 guizang-social-card-skill 生成 8 页社交卡片。prompt 必须自包含，见下方 Subagent Prompt 模板。

### 关键参数
| 参数 | 值 |
|------|-----|
| 页数 | **8 页** |
| 尺寸 | 1080×1440（3:4 小红书竖版） |
| 风格模式 | **Editorial Magazine × E-ink** |
| 主题 | **Indigo Porcelain（靛蓝瓷）** |
| 种子模板 | `assets/template-editorial-card.html` |
| 布局配方 | M01-M16（Editorial 系列） |

### 设计要点
- 封面用 M01 Magazine Issue Cover，营造杂志创刊号氛围
- 内容页每页一个核心观点，使用 ledger / pipeline / pull-quote / before-after 等配方
- 底色为暖纸白 + 靛蓝墨色文字 + 纸纹/墨染氛围层
- 可嵌入论文配图（从 `figures/` 目录读取）到 image-well 区域
- 字体自动加载（Google Fonts：Noto Serif SC + Inter），无需手动处理

### 8 页内容结构（通用模板）

⚠️ **以下为格式示意，Agent 必须根据论文实际内容自行设计每页的具体内容和布局配方。**

```
1. 封面（M01 Magazine Issue Cover）— 论文标题 + 机构/会议 + 核心标签
2. 问题/动机（M03 Editorial Essay Split 或 M14 Vertical Pipeline）— 领域痛点
3. 核心概念/理论（M08 Tall Ledger 或 M14 Vertical Pipeline）— 关键概念图解
4. 方法流程（M14 Vertical Pipeline）— 方法步骤/阶段
5. 关键创新细节（M15 Before/After 或 M08 Tall Ledger）— 创新点对比
6. 实验/结果数据（M08 Tall Ledger）— 关键数字 + 对比表格
7. 洞察/金句（M04 Pull Quote）— 提炼最有价值的洞察
8. 总结 + 链接（M07 Closing Note）— 贡献总结 + 论文/代码链接
```

### Subagent Prompt 模板

```
你需要基于论文解析 HTML，用 guizang-social-card-skill 生成 8 页小红书社交卡片。

## 输入
- 论文解析: output\<paper_slug>\paper_analysis.html
- 论文配图: output\<paper_slug>\figures\ （如有，用 Read 查看）
- 用 Read 工具读取论文解析文件获取内容；配图可直接查看

## 第一步：读取 guizang 参考文件
在生成前，先读取以下参考文件（路径: .claude/skills/guizang-social-card-skill/references/）：
- layout-recipes.md（选择 M01-M16 配方）
- theme-presets.md（Indigo Porcelain 的 CSS token）
- components.md（字体、字号、间距规范）
- background-systems.md（纸纹/墨染氛围层）
- portrait-fill.md（3:4 画布填充规则）

## 第二步：生成 HTML
1. 复制种子模板 `.claude/skills/guizang-social-card-skill/assets/template-editorial-card.html`
   到 `output\<paper_slug>\guizang_cards\index.html`
2. 设置 `<html data-theme="indigo-porcelain">`
3. 根据论文内容自行设计 8 页卡片，每页从 M01-M16 中选择合适的布局配方
4. 替换 `<!-- POSTERS_HERE -->` 区域，每个 `<section class="poster xhs">` 对应一页
5. 如有论文配图，放到 `output\<paper_slug>\guizang_cards\assets\` 目录并在 HTML 中引用

## 页面内容设计原则
- 封面（Page 01）：M01 Magazine Issue Cover，论文标题 + 机构 + 标签
- 问题/动机（Page 02）：M03 或 M14，展示领域痛点
- 核心概念（Page 03）：M08 或 M14，图解关键概念
- 方法流程（Page 04）：M14 Vertical Pipeline，展示方法步骤
- 创新细节（Page 05）：M15 Before/After 或 M08，对比分析
- 实验数据（Page 06）：M08 Tall Ledger，关键数字+对比表
- 洞察金句（Page 07）：M04 Pull Quote，提炼核心洞察
- 总结（Page 08）：M07 Closing Note，贡献总结+链接

⚠️ 以上为格式示意，Agent 必须根据论文实际内容自行设计每页，不要用任何预设的论文专属内容。

## 关键约束
- 所有 .poster.xhs 必须是 1080×1440，内容覆盖 ≥75% 画布高度
- 不要混合 Swiss 和 Editorial 的 class 体系
- 不要添加无意义的装饰元素（CSS blob、随机圆圈等）
- 文字不能溢出、不能贴边
- 如果嵌入配图，设置正确的 object-position
- 禁止在图片上使用默认的全画布蒙版

## 输出
- HTML: output\<paper_slug>\guizang_cards\index.html
- 配图: output\<paper_slug>\guizang_cards\assets\ （如有）
```


---

## Step 3B: frontend-slides 手机卡片（备选，暖色卡片风）

如果你不需要 guizang 的杂志质感，可以用 frontend-slides 快速生成 8 页暖色手机卡片。两种方案可**二选一**，也可**都跑**（两套图片都发小红书）。

### 关键参数
| 参数 | 值 |
|------|-----|
| 页数 | **8 页** |
| 布局 | 手机竖版卡片（max-width: 380px），截图 390×844 |
| 风格 | 暖色卡片风（#f5f0eb 底色 + #fefcf8 卡片） |
| 4色点缀 | 橙 #e07b5a, 绿 #5b8c7a, 紫 #8b6faa, 金 #c9a040 |
| 字体 | Plus Jakarta Sans (Google Fonts) |
| 编辑 | No（手机版不需要 inline editing） |

### 设计要点
- **内容占比优先**：卡片有效内容需占 viewport ≥70%。减少外层 padding/margin，字要大、图要满、留白克制
- 每页一张卡片：顶部 4px 色条（四色轮换）+ 内容区 + 页码
- 使用 scroll-snap 实现滑动翻页，触摸优先（touchstart/touchend）
- CSS 图解元素：流程图、步骤行、迷你卡片网格
- 不包含 inline editing

### 8 页内容结构（通用模板）

```
1. 封面卡片（论文标题 + 机构/会议 + arXiv链接 + 核心标签）
2. 问题卡片（用迷你卡片网格展示 3-4 个核心痛点/挑战）
3. 理论/概念卡片（用图解展示核心理论框架）
4. 方法卡片（用流程图展示方法步骤/阶段）
5. 创新细节卡片（用步骤卡片展示关键创新点细节）
6. 结果卡片（关键数字统计 + 迷你数据卡）
7. 洞察卡片（关键洞察 + 金句）
8. 总结 + 链接卡片
```

### Subagent Prompt 模板

```
你需要基于论文解析 HTML 创建一份 8 页手机卡片版 HTML。请先读取论文解析，提取关键信息，再生成 HTML。

## 输入
- 论文解析: output\<paper_slug>\paper_analysis.html
- 用 Read 工具读取该文件获取论文内容

## 幻灯片结构设计原则
根据论文内容自行设计 8 页卡片。必须覆盖：
1. 封面（标题+机构+标签+链接）
2. 痛点/动机（用迷你卡片网格展示 3-4 个核心问题）
3. 核心概念/理论（图解/示意图，让人秒懂）
4. 方法流程（步骤图/流程图，展示方法怎么做）
5. 关键创新细节（分步骤卡片）
6. 结果数据（数字+迷你数据卡）
7. 洞察+金句（提炼最有价值的洞察）
8. 总结+链接

⚠️ 每页具体内容从论文解析中提取，不要用任何预设的论文专属内容。

## 风格参数
- 页数: 精确 8 页
- 布局: 手机竖版卡片（max-width: 380px）
- 风格: 暖色卡片风（#f5f0eb 底色 + #fefcf8 卡片）
- 4色点缀: 橙 #e07b5a, 绿 #5b8c7a, 紫 #8b6faa, 金 #c9a040
- 字体: Plus Jakarta Sans (Google Fonts)
- 编辑: No（手机版不需要 inline editing）
- 必须读取 viewport-base.css、html-template.md（路径: .claude/skills/frontend-slides/）

## 设计要点
- 每页一张卡片，卡片内有：顶部 4px 色条（四色轮换）+ 内容区 + 页码
- 使用 scroll-snap 实现滑动翻页
- 触摸优先（touchstart/touchend 滑动检测）
- CSS 图解元素：流程图、步骤行、迷你卡片网格
- 不包含 inline editing
- **内容占比优先**：卡片有效内容需占 viewport ≥70%。减少外层 padding/margin（margin 8-12px, padding 16-20px），字要大、图要满、留白要克制

## 技术约束
- 每页 height: 100vh; height: 100dvh; overflow: hidden;
- 字体用 clamp()，下限不低于 14px
- 卡片 margin 控制在 8-12px，padding 控制在 16-20px
- 有 viewport-base.css 完整内容
- 单文件 HTML，所有 CSS/JS inline
- 无需图片，所有视觉用 CSS 生成
- 输出: output\<paper_slug>\mobile_cards.html
```

---

## Step 4: HTML 转图片（Playwright 截图）

guizang 社交卡片为单文件 HTML，通过 Playwright 对每个 `.poster.xhs` 元素截图导出 PNG。

### 用法

```python
# 在 .venv 环境中运行
from playwright.sync_api import sync_playwright

html_path = r"output\<paper_slug>\guizang_cards\index.html"
output_dir = r"output\<paper_slug>\guizang_cards\output"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1080, "height": 1440})
    page.goto(f"file:///{html_path}", wait_until="commit")
    page.wait_for_timeout(8000)  # 等待 Google Fonts 加载
    posters = page.query_selector_all(".poster.xhs")
    for i, poster in enumerate(posters):
        poster.screenshot(path=f"{output_dir}/xhs-{i+1:02d}.png")
    browser.close()
```

### 参数说明

| 参数 | 值 | 说明 |
|------|-----|------|
| viewport | 1080×1440 | 匹配 `.poster.xhs` 的 3:4 比例 |
| wait_until | `commit` | 不用 `networkidle`（Google Fonts CDN 在国内可能超时） |
| wait_for_timeout | 8000ms | 给字体和 WebGL 背景足够的渲染时间 |
| 输出命名 | `xhs-01.png` ~ `xhs-08.png` | 符合小红书 fill-publish 的图片顺序 |

### 注意事项
- Google Fonts CDN 在国内较慢，`wait_until='commit'` + 8s 等待可规避超时
- 截图前确认 `.poster.xhs` 元素数量正确（应为 8 个）
- 输出目录 `output/<paper_slug>/guizang_cards/output/` 需提前创建
- 每张 PNG 约 150-300KB，总量约 1.5-2.5MB

### 手机卡片截图（Step 3B 产出）

如果选择了 Step 3B，用 `slides_to_images.py` 脚本截图：

```bash
.venv/Scripts/python scripts/slides_to_images.py \
  "output/<paper_slug>/mobile_cards.html" \
  "output/<paper_slug>/mobile_slides" \
  390 844
```

| 参数 | 值 | 说明 |
|------|-----|------|
| viewport | 390×844 | 手机竖版比例 |
| 输出命名 | `slide_01.png` ~ `slide_08.png` | 截图后按需重命名 |

---

## Step 5: 小红书文案

### 文案结构（小红书风格）
```
[吸引眼球的标题式开头]

[背景铺垫 1-2 句]

[核心内容分点展开]
- 关键发现 1
- 关键发现 2
- ...

[金句收尾]

[话题标签 用空格分隔]
```

### 文案示例与要点
- 示例见各论文子文件夹下的 `xhs_caption.txt`
- 开头用提问或热点切入引发共鸣
- 分点讲清楚：问题 → 方法 → 效果
- 金句收尾
- 标签用空格分隔：`#AI论文 #推荐系统 #生成式AI`
- 根据论文主题调整标签，不要照搬

### 注意事项
- ⚠️ 标题 ≤ 20 字（小红书限制）
- ⚠️ 话题标签之间**必须用空格分隔**，不能连写（例如 `#AI #论文` 而非 `#AI#论文`）
- 内容不用太长，300-500 字即可
- 文案保存到 `output/<paper_slug>/xhs_caption.txt`
- 标题单独保存到 `output/<paper_slug>/xhs_title.txt`

---

## Step 6: 小红书发布（post-to-xhs）

### 调用方式
```
/post-to-xhs 发布图文
```
或直接运行：
```bash
.venv/Scripts/python .claude/skills/post-to-xhs/scripts/cli.py fill-publish \
  --title-file "output/<paper_slug>/xhs_title.txt" \
  --content-file "output/<paper_slug>/xhs_caption.txt" \
  --images "output/<paper_slug>/guizang_cards/output/xhs-01.png" ... "output/<paper_slug>/guizang_cards/output/xhs-08.png"
```

### 发布流程
1. 先 `check-login` 确认登录状态
2. 用 `fill-publish` 填写表单（**不自动点击发布**，最后一步用户手动点）
3. 图片自动上传（每张约 1-2 秒）
4. 标题和正文自动填写

### 注意事项
- ⚠️ Chrome 扩展 Bridge Server 必须在 `ws://localhost:9333` 可用
- ⚠️ 如果 Bridge 超时：检查 Chrome 扩展是否已连接
- ⚠️ 如果标题过长：`TitleTooLongError`，缩短到 ≤20 字
- ⚠️ `fill-publish` 只填表单不发布，用户需手动在浏览器中点击"发布"

---

## 完整文件清单

```
output/
└── <paper_slug>/              # 每篇论文独立子文件夹
    ├── paper_analysis.html    # Step 1: 论文深度解析（含配图）
    ├── full.md                #        MinerU 提取的完整 markdown
    ├── images/                #        MinerU 提取的论文配图（原始文件名）
    ├── figures/               #        重命名后的论文配图（figure_01_xxx.jpg）
    ├── presentation.html      # Step 2: 组会 PPT
    ├── slides/                # Step 4a: PPT 图片
    ├── guizang_cards/         # Step 3A: guizang 社交卡片
    │   ├── index.html         #   卡片 HTML（Editorial × E-ink）
    │   ├── assets/            #   卡片中引用的图片/配图
    │   └── output/            #   Step 4b: 卡片截图（1080×1440）
    │       ├── xhs-01.png     #   封面
    │       ├── xhs-02.png     #   问题/动机
    │       ├── ...
    │       └── xhs-08.png     #   总结+链接
    ├── mobile_cards.html      # Step 3B: frontend-slides 手机卡片（备选）
    ├── mobile_slides/         # Step 4c: 手机卡片截图（390×844）
    │   ├── slide_01.png
    │   ├── slide_02.png
    │   ├── ...
    │   └── slide_08.png
    ├── xhs_title.txt          # Step 5: 小红书标题
    └── xhs_caption.txt        # Step 5: 小红书文案
```

---

## 快速命令速查

```bash
# Step 4a: 组会 PPT → 图片（16:9 桌面比例）
.venv/Scripts/python scripts/slides_to_images.py \
  "output/<paper_slug>/presentation.html" "output/<paper_slug>/slides" 1280 720

# Step 4b: guizang 卡片 → 图片（Playwright 截图 .poster.xhs → PNG）
# 使用 .venv 中 Playwright 直接截图，详见 Step 4 说明

# Step 5: 检查小红书登录
.venv/Scripts/python .claude/skills/post-to-xhs/scripts/cli.py check-login

# Step 6: 填写发布表单
.venv/Scripts/python .claude/skills/post-to-xhs/scripts/cli.py fill-publish \
  --title-file "output/<paper_slug>/xhs_title.txt" \
  --content-file "output/<paper_slug>/xhs_caption.txt" \
  --images "output/<paper_slug>/guizang_cards/output/xhs-01.png" \
           ... \
           "output/<paper_slug>/guizang_cards/output/xhs-08.png"
```

---

## 默认风格配置

> 以下为 paper-to-xhs 全流程的默认配置。每篇论文的幻灯片结构（页数、内容）需根据论文主题自行设计，详见 Step 2/3 的"结构生成原则"。

| 阶段 | 决策 | 默认值 |
|------|------|--------|
| 论文解析 | 风格 | academic 学术型 |
| 组会 PPT | 感觉 | 专业/可信 (Impressed/Confident) |
| 组会 PPT | 预设 | Electric Studio |
| 组会 PPT | 页数 | 18-20 页 |
| 组会 PPT | 编辑 | Yes (inline editing) |
| 社交卡片 | 风格模式 | Editorial Magazine × E-ink |
| 社交卡片 | 主题 | Indigo Porcelain（靛蓝瓷） |
| 社交卡片 | 页数 | 8 页 |
| 社交卡片 | 布局 | 1080×1440（3:4） |
| 小红书 | 标题 | ≤20 字 |
| 小红书 | 发布 | fill-publish（手动点发布） |
