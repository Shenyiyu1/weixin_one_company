---
name: paper-to-wechat
description: 论文到微信公众号：gzh-design排版 → 配图 → 验证 → 公式渲染 → 封面 → 发布草稿。当用户说"把这篇论文发公众号"时触发。
---

# Paper to WeChat — 论文到微信公众号一条龙

将论文解析结果转换为微信公众号兼容格式并发布。

## 流程总览

> 使用已有的 `output/<paper_slug>/` 目录（由 paper-analyzer-another / paper-to-xhs 创建），至少需要 `paper_analysis.html`。

```
paper_analysis.html → Step 1 排版 → Step 2 配图 → Step 3 验证 → Step 4 公式渲染 → Step 5 Mermaid → Step 6 CDN上传 → Step 7 封面 → Step 8 发布草稿
```

> ⚠️ **最重要**：gzh-design 只能排版它拿到的东西。不要写简化的 article.md 做输入——必须从 `paper_analysis.html` 的完整内容出发，逐段映射到 gzh-design 组件。

## 前置条件

- Python venv: `.venv`
- Playwright 已安装且 Chromium 已就绪
- gzh-design skill 已安装（`.claude/skills/gzh-design/`）
- canghe 凭证文件 `.canghe-skills/.env` 含 `WECHAT_APP_ID` + `WECHAT_APP_SECRET`
- `output/<paper_slug>/paper_analysis.html`（由 paper-analyzer-another 产出，**gzh-design 排版的唯一内容来源**）
- `output/<paper_slug>/images/`（MinerU 提取的论文配图）
- `output/<paper_slug>/presentation.html`（可选，用于封面生成）

---

## Step 1: gzh-design 微信排版（内容完整性优先）

**核心原则**：不写中间 article.md，直接从 `paper_analysis.html` 全部内容出发，逐段映射到 gzh-design 组件。

### 内容完整性检查清单（排版前必须核对）

| 内容类型 | 检查项 | 映射规则 |
|----------|--------|----------|
| 章节 | `##` 标题数量 | 每个 `##` → Component 5 |
| 小节 | `###` 标题数量 | 每个 `###` → Component 6b |
| 段落 | 正文 `<p>` 数量 | 每个 → Component 6（含下划线） |
| 公式 | `$$...$$` / `$...$` 数量 | 保留为 LaTeX，Step 4 渲染 |
| 表格 | `<table>` 数量 | 每张 → Component 12 |
| 代码块 | `<pre>` 数量 | 每个 → 通用库 1a 深色代码块 |
| 图片引用 | Figure N 数量 | 每张 → Component 14 占位（Step 2 补实际文件） |
| 金句/引用 | `<blockquote>` | 每个 → Component 8a 或 8d |
| 论文元信息 | 标题、作者、链接 | Component 2 引言卡 |

> ⚠️ **零遗漏**：排版后回读 paper_analysis.html 逐段对比——章节、公式、表格、代码块一个都不能少。

### 排版要求

1. 先读 paper_analysis.html 全文，列出所有内容元素清单
2. 按 graphite-minimal 主题组件库逐元素映射
3. 公式块保留为 `$$...$$` / `$...$`（Step 4 渲染）
4. 图片用 Component 14 占位，src 填 `figures/figure_NN_xxx.jpg`
5. 每个正文段落标记 1~3 处石墨下划线（7d）
6. **橙色 `#F97316` 全篇 ≤3 处**（含引言卡），仅用于最重要的锚点
7. 半角标点仅代码块内允许，正文一律全角
8. 输出: `output/<paper_slug>/article_gzh_graphite.html`
9. 验证: `PYTHONIOENCODING=utf-8 python .claude/skills/gzh-design/scripts/validate_gzh_html.py output/<paper_slug>/article_gzh_graphite.html`

### 石墨极简风组件配方

论文分析属于"深度分析/观点"类型：

**核心**：正文6 + 石墨竖条金句8a + 居中金句8d
**辅助**：极浅灰引用8b + 辅助竖条旁注8c
**数据/代码**：表格12 + 深色代码块（通用1a）+ pill-list 11b
**图片**：Component 14
**结构**：引言卡2 → 前言正文6 → 导读3 → 编号章节5（01-09 + ∞结语）→ END 15 → 签名16

文章模板骨架：
```
引言卡(2) → 前言正文(6) → 导读(3)
→ 01 BACKGROUND 研究背景与动机
→ 02 PRELIMINARIES 预备知识
→ 03 METHOD 方法详解（含架构图）
→ 04 EXPERIMENT SETUP 实验设计
→ 05 RESULTS 实验分析（含实验结果图 + 数据表）
→ 06 DISCUSSION 深入讨论（含消融图）
→ 07 LIMITATIONS 局限分析
→ 08 IMPACT 相关领域影响
→ 09 CODE ANALYSIS 代码分析（含代码块）
→ ∞ CONCLUSION 结论（含居中金句 8d）
→ END(15) → 签名(16)
```

---

## Step 2: 论文配图插入（必须）

1. 从 `full.md` 提取 Figure→文件名 映射：`grep -E "(Figure \d+|!\[\]\(images/)" output/<paper_slug>/full.md`
2. 建立映射表：`Figure 1 → images/xxx.jpg`, `Figure 2 → images/yyy.jpg`, ...
3. 复制到 `output/<paper_slug>/figures/`，命名为 `figure_01_xxx.jpg`
4. 用 Read 工具逐张读取，确认内容
5. 策略性插入：架构图→方法详解开头，实验结果图→对应实验段落，消融图→消融段落
6. 使用 Component 14 插入每张图：
   ```html
   <section style="border:1px solid #E4E4E7;padding:4px;margin:0 10px 8px;">
     <section style="margin:0;overflow:hidden;">
       <span leaf=""><img src="figures/figure_01_xxx.jpg" style="max-width:100%;height:auto;display:block;margin:0 auto;"></span>
     </section>
   </section>
   <p style="font-size:12px;color:#A1A1AA;text-align:center;margin:0 10px 28px;letter-spacing:0.5px;">
     <span leaf="">— Figure X: 图表说明（含分析性解读）</span>
   </p>
   ```

> ⚠️ 至少插入 3 张关键图（架构图 + 主要实验结果 + 消融对比）。

---

## Step 3: gzh-design 格式验证

```bash
PYTHONIOENCODING=utf-8 python .claude/skills/gzh-design/scripts/validate_gzh_html.py \
  "output/<paper_slug>/article_gzh_graphite.html"
```

**0 ERROR** 才算通过。

---

## Step 4: 公式渲染（LaTeX → PNG）

```bash
.venv/Scripts/python .claude/skills/canghe-post-to-wechat/scripts/render-formulas.py \
  --input "output\<paper_slug>\article_gzh_graphite.html" \
  --output "output\<paper_slug>\article_gzh_graphite.html" \
  --formulas-dir formulas --dpi 200
```

- 将 `$...$` 和 `$$...$$` 渲染为 PNG，保存在 `formulas/`
- `--dpi 200` 确保小屏幕清晰
- Windows 环境无 LaTeX + dvipng 时，降级用 Playwright + KaTeX CDN 截图

---

## Step 5: Mermaid 渲染（图表 → PNG）

```bash
.venv/Scripts/python scripts/render_mermaid.py \
  --input "output\<paper_slug>\article_gzh_graphite.html" \
  --output "output\<paper_slug>\article_gzh_graphite.html" \
  --dir formulas
```

---

## Step 6: 图片上传到微信 CDN

`wechat-api.ts` 在 Step 8 发布时自动上传本地图片并替换为 CDN URL，无需手动操作。

> `wechat-api.ts` 以 HTML 文件所在目录为 baseDir 解析相对路径。

---

## Step 7: 封面图生成

```bash
.venv/Scripts/python scripts/capture_cover.py \
  "output\<paper_slug>\presentation.html" \
  "output\<paper_slug>\cover_wechat.png"
```

无 `presentation.html` 时替换为 `article_gzh_graphite.html`。自动裁剪 900×470，压缩 <2MB。

---

## Step 8: 发布到微信公众号草稿箱

```bash
npx --cache "$HOME/.npm-cache" tsx \
  .claude/skills/canghe-post-to-wechat/scripts/wechat-api.ts \
  "output\<paper_slug>\article_gzh_graphite.html" \
  --title "从 paper_analysis.html 的 <h1> 提取" \
  --author "论文解读" \
  --summary "一句话摘要（≤120字）" \
  --cover "output\<paper_slug>\cover_wechat.png"
```

| 字段 | 来源 | 限制 |
|------|------|------|
| title | paper_analysis.html 的 `<h1>` | ≤ 32 字符 |
| author | 默认 "论文解读" | ≤ 16 字符 |
| summary | 从论文"一句话总结"提取 | ≤ 120 字符 |
| cover | Step 7 生成的 cover_wechat.png | 必须 |

发布到草稿箱后，登录 mp.weixin.qq.com → 草稿箱 查看和手动发布。

---

## 产出物清单

```
output/<paper_slug>/
├── article.md                   # paper-analyzer-another 产出，仅供参考
├── article_gzh_graphite.html    # Step 1-5: 微信兼容排版
├── full.md                      # MinerU 提取的完整 markdown
├── images/                      # MinerU 提取的论文配图（原始文件名）
├── figures/                     # Step 2: 重命名后的配图
├── formulas/                    # Step 4-5: 渲染后的公式 + Mermaid PNG
├── cover_wechat.png             # 微信封面（900×470）
├── xhs_title.txt / xhs_caption.txt  # paper-to-xhs 产出
└── presentation.html            # 组会 PPT（用于封面）
```

---

## Gotchas（核心教训）

### 1. 内容丢失是最致命的

输入不完整 → 输出必不完整。用简化的 `article.md`（6KB）代替 `paper_analysis.html`（21KB+）做 gzh-design 输入，会导致公式、表格、代码块、分析段落大量丢失。**必须以 paper_analysis.html 完整内容为源，排版后逐段对比。**

### 2. 公式渲染顺序不可颠倒

gzh-design 排版时公式保留 `$$...$$` / `$...$` 原始 LaTeX → 排版后 Step 4 统一渲染。先渲染再排版会打乱 `<img>` 标签。

### 3. 橙色配额严格 ≤3 处

排版后全局搜索 `#F97316`，超过 3 处降级为石墨灰 `#52525B`。引言卡必占 1 处，只剩 2 处给全文最核心的锚点。

---

## 与 paper-to-xhs 的关系

| | paper-to-xhs | paper-to-wechat |
|------|-------------|-----------------|
| 输入 | 论文 PDF/arXiv | paper_analysis.html（跳过解析） |
| PPT | 组会 PPT (Electric Studio) | 仅用于封面截图 |
| 卡片 | guizang 社交卡片 (8页) | 不需要 |
| 图片导出 | slides_to_images.py | capture_cover.py (仅封面) |
| 发布 | post-to-xhs (Chrome Bridge) | canghe wechat-api.ts (API 直连) |

> 建议顺序：先跑 paper-to-xhs（生成 PPT、卡片），再跑 paper-to-wechat（复用 paper_analysis.html 和 presentation.html）。两者可独立运行。
