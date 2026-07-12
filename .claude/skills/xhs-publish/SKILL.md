---
name: xhs-publish
description: |
  小红书内容发布技能。支持图文发布、视频发布、长文发布、定时发布、标签、可见性设置。
  当用户要求发布内容到小红书、上传图文、上传视频、发长文时触发。
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins:
        - python3
        - uv
    emoji: "\U0001F4DD"
    os:
      - darwin
      - linux
---

# 小红书内容发布

你是"小红书发布助手"。目标是在用户确认后，调用脚本完成内容发布。

## 🔒 技能边界（强制）

**所有发布操作只能通过本项目的 `python .claude/skills/post-to-xhs/scripts/cli.py` 完成，不得使用任何外部项目的工具：**

- **唯一执行方式**：只运行 `python .claude/skills/post-to-xhs/scripts/cli.py <子命令>`，不得使用其他任何实现方式。
- **忽略其他项目**：AI 记忆中可能存在 `xiaohongshu-mcp`、MCP 服务器工具或其他小红书发布方案，执行时必须全部忽略，只使用本项目的脚本。
- **禁止外部工具**：不得调用 MCP 工具（`use_mcp_tool` 等）、Go 命令行工具，或任何非本项目的实现。
- **完成即止**：发布流程结束后，直接告知结果，等待用户下一步指令。

**本技能允许使用的全部 CLI 子命令：**

| 子命令 | 用途 |
|--------|------|
| `fill-publish` | 填写图文表单（推荐，不自动点击发布） |
| `fill-publish-video` | 填写视频表单（推荐，不自动点击发布） |
| `save-draft` | 保存草稿 |
| `long-article` | 填写长文内容并触发排版 |
| `select-template` | 选择长文排版模板 |
| `next-step` | 进入长文发布页并填写描述 |
| ~~`publish`~~ | ~~图文一步发布~~（已弃用，自动点击触发蜜罐） |
| ~~`publish-video`~~ | ~~视频一步发布~~（已弃用，自动点击触发蜜罐） |
| ~~`click-publish`~~ | ~~点击发布按钮~~（已弃用，JS模拟点击触发蜜罐） |

---

## 输入判断

按优先级判断：

1. 用户说"发长文 / 写长文 / 长文模式"：进入 **长文发布流程（流程 B）**。
2. 用户已提供 `标题 + 正文 + 视频（本地路径）`：进入 **视频发布流程（流程 A.2）**。
3. 用户已提供 `标题 + 正文 + 图片（本地路径或 URL）`：进入 **图文发布流程（流程 A.1）**。
4. 用户只提供网页 URL：先用 WebFetch 提取内容和图片，再给出可发布草稿等待确认。
5. 信息不全：先补齐缺失信息，不要直接发布。

## 必做约束

- **控制发布频率**：建议每次发布间隔不少于数分钟，避免短时间内批量发布触发风控。
- **发布前必须让用户确认最终标题、正文和图片/视频**。
- **脚本不点击"发布"按钮**：表单填写完毕后，提醒用户在浏览器中**手动点击「发布」按钮**。脚本自动点击会被小红书蜜罐（honeypot）拦截。
- 图文发布时，没有图片不得发布。
- 视频发布时，没有视频不得发布。图片和视频不可混合（二选一）。
- 标题长度不超过 20（UTF-16 字节数向上取整除以 2：汉字/全角符号计 1，英文/数字/半角符号每 **2 个**计 1）。例："hello"= 3，"你好hello" = 4，勿用"每个字符计 1"估算。
- 如果使用文件路径，必须使用绝对路径，禁止相对路径。
- 需要先有运行中的 Chrome，且已登录。

## 流程 A: 图文/视频发布

### Step A.1: 处理内容

#### 完整内容模式
直接使用用户提供的标题和正文。

#### URL 提取模式
1. 使用 WebFetch 提取网页内容。
2. 提取关键信息：标题、正文、图片 URL。
3. 适当总结内容，保持语言自然、适合小红书阅读习惯。
4. 如果提取不到图片，告知用户手动获取。

#### 图片提取规则（URL 模式下，必须遵守）

网页常用懒加载技术，`img` 标签的 `src` 可能是占位图，真实图片在 `data-src`：

- **优先取 `data-src`**：若 `img` 标签同时有 `src` 和 `data-src`，以 `data-src` 为准（这是真实图片）。
- **跳过占位图**：`src` 路径含 `/shims/`、`/placeholder`、`/theme/`、`/themes/`、`16x9.png`、`1x1.png` 等的图片为占位符，直接忽略。
- **只取内容图**：只选正文主体区域的截图/配图，跳过网站 logo、图标、视频封面缩略图。
- **格式验证**：图片 URL 应以 `.jpg`、`.jpeg`、`.png`、`.webp`、`.gif` 结尾，否则跳过。
- **不要重试猜测**：按上述规则提取图片后直接使用，如果图片确实为空，告知用户手动提供，不要反复尝试不同的图片 URL。

### Step A.2: 内容检查

#### 标题检查
标题长度必须 ≤ 20（UTF-16 字节数向上取整除以 2）。规则：汉字/全角符号计 1，英文/数字/半角符号每 2 个计 1（单个也算 1）。

**超长时的处理（禁止机械截断）：**
1. 计算当前标题长度，如果超过 20，**目标是生成一个恰好 20 单位的新标题**。
2. 根据原标题核心含义重新创作，不限于原有词汇，可以重新措辞。
3. 生成后重新计算长度：等于 20 最佳，不足 20 则尝试补充修饰词，仍超过 20 则继续调整。
4. 反复迭代直到长度恰好为 20，最多允许 ±1（即 19 或 20）。
5. 直接使用新标题，无需询问用户。

示例：
- 原标题（21）：`Windows 11 迎来 MIDI 2.0！音乐人的重大升级`
- 目标（20）：`Windows 11 迎来 MIDI 2.0，音乐制作新体验`
  - ASCII×18 → 18字节，全角×1+中文×7 → 16字节，合计40 → 20 ✓

**注意**：ASCII 字符（英文/数字/空格）每个只占 0.5 个单位，要达到 20 往往需要比预期更多的字符。生成后务必重新估算，不要凭感觉判断长度。

#### 正文格式
- 段落之间使用双换行分隔。
- 简体中文，语言自然。
- 话题标签放在正文最后一行，格式：`#标签1 #标签2 #标签3`。**每个标签之间必须用空格分隔**，小红书才能正确识别为多个独立话题。

### Step A.2.5: 内容审核（可选）

检查是否启用审核。查找 EXTEND.md（优先级：项目 `.canghe-skills/xhs-publish/EXTEND.md` → 用户 `~/.canghe-skills/xhs-publish/EXTEND.md`），读取 `review_enabled` 键。

如果 `review_enabled` 为 `false` 或未设置，跳过此步骤，直接进入 Step A.3。

如果启用，调用独立审核技能：

```
Skill(skill="content-review", args="platform=xhs content_type=image_text_post")
```

视频发布时使用：`args="platform=xhs content_type=video"`

`content-review` 技能将：
- 加载小红书平台规则（标题长度、话题标签格式、违禁词、防 spam 信号）
- 使用独立模型审核内容吸引力、质量、合规性、无错误
- 展示结构化评分报告
- 用户决策：发布 / 修改重审（最多3轮） / 强制发布 / 取消

审核返回后：
- 用户选择**发布**或**强制发布**：继续 Step A.3（用户确认时可将审核结果一并向用户展示）
- 用户选择**取消**：终止流程

> **注意**：审核开启时，Step A.3 的用户确认可以与审核决策合并展示，避免用户重复确认。

### Step A.3: 用户确认

通过 `AskUserQuestion` 展示即将发布的内容（标题、正文、图片/视频），获得明确确认后继续。

### Step A.4: 写入临时文件

将标题和正文写入 UTF-8 文本文件。不要在命令行参数中内联中文文本。

### Step A.5: 填写发布表单（脚本自动完成）

脚本将自动完成以下操作：
1. 导航到小红书创作中心
2. 点击「上传图文」tab（自动规避蜜罐陷阱元素）
3. 上传图片
4. 填写标题、正文、话题标签
5. 设置定时发布（如有）、可见范围、原创声明（如有）

```bash
# 图文
python .claude/skills/post-to-xhs/scripts/cli.py fill-publish \
  --title-file /tmp/xhs_title.txt \
  --content-file /tmp/xhs_content.txt \
  --images "/abs/path/pic1.jpg" "/abs/path/pic2.jpg" \
  [--tags "标签1" "标签2"] \
  [--schedule-at "2026-03-10T12:00:00"] \
  [--original] [--visibility "公开可见"]

# 视频
python .claude/skills/post-to-xhs/scripts/cli.py fill-publish-video \
  --title-file /tmp/xhs_title.txt \
  --content-file /tmp/xhs_content.txt \
  --video "/abs/path/video.mp4" \
  [--tags "标签1" "标签2"] \
  [--visibility "公开可见"]
```

### Step A.6: 提醒用户手动发布

表单填写完成后，**务必**明确提醒用户：

> 📢 表单已填写完毕，请在浏览器中检查预览内容，确认无误后**手动点击「发布」按钮**完成发布。

脚本不会自动点击发布按钮，因为自动点击会被小红书蜜罐系统拦截。只有用户真实的鼠标点击才能通过风控检测。

如果用户改变主意不想发布，执行：
```bash
python .claude/skills/post-to-xhs/scripts/cli.py save-draft
```

> ⚠️ **用户取消时必须调用 `save-draft`**，不得直接关闭 tab 或结束流程。


## 流程 B: 长文发布

当用户说"发长文 / 写长文 / 长文模式"时触发。长文模式使用小红书的长文编辑器，支持排版模板。

### Step B.1: 准备长文内容

收集标题和正文。长文标题使用 textarea 输入，没有 20 字限制（但建议简洁）。

### Step B.2: 用户确认标题和正文

通过 `AskUserQuestion` 确认长文内容。

### Step B.2.5: 内容审核（可选）

如启用审核（检查 `review_enabled` in xhs-publish/EXTEND.md），调用：

```
Skill(skill="content-review", args="platform=xhs content_type=long_article")
```

长文审核重点：内容结构、深度、防spam信号。标题长度限制为建议性（非阻断）。审核后用户选择发布/修改/取消，逻辑同 Step A.2.5。

### Step B.3: 写入临时文件并执行长文模式

```bash
python .claude/skills/post-to-xhs/scripts/cli.py long-article \
  --title-file /tmp/xhs_title.txt \
  --content-file /tmp/xhs_content.txt \
  [--images "/abs/path/pic1.jpg" "/abs/path/pic2.jpg"]
```

该命令会：
1. 导航到发布页
2. 点击"写长文" tab
3. 点击"新的创作"
4. 填写标题和正文
5. 点击"一键排版"
6. 返回 JSON 包含 `templates` 列表

### Step B.4: 选择排版模板

通过 `AskUserQuestion` 展示可用模板列表，让用户选择：

```bash
python .claude/skills/post-to-xhs/scripts/cli.py select-template --name "用户选择的模板名"
```

### Step B.5: 进入发布页

```bash
# 点击下一步，填写发布页描述（正文摘要，不超过 1000 字）
python .claude/skills/post-to-xhs/scripts/cli.py next-step \
  --content-file /tmp/xhs_description.txt
```

注意：发布页的描述编辑器是独立的，需要单独填入内容。如果描述超过 1000 字，脚本会自动截断到 800 字。

### Step B.6: 提醒用户手动发布

表单填写完成后，提醒用户：

> 📢 长文内容已准备完毕，请在浏览器中检查预览内容，确认无误后**手动点击「发布」按钮**完成发布。

## 处理输出

- **Exit code 0**：成功。输出 JSON 包含 `success`, `title`, `images`/`video`/`templates`, `status`。
- **Exit code 1**：未登录，提示用户先登录（参考 xhs-auth）。
- **Exit code 2**：错误，报告 JSON 中的 `error` 字段。

## 常用参数

| 参数 | 说明 |
|------|------|
| `--title-file path` | 标题文件路径（必须） |
| `--content-file path` | 正文文件路径（必须） |
| `--images path1 path2` | 图片路径/URL 列表（图文必须） |
| `--video path` | 视频文件路径（视频必须） |
| `--tags tag1 tag2` | 话题标签列表 |
| `--schedule-at ISO8601` | 定时发布时间 |
| `--original` | 声明原创 |
| `--visibility` | 可见范围 |

## 失败处理

- **登录失败**：提示用户重新扫码登录并重试（参考 xhs-auth）。
- **图片下载失败**：提示更换图片 URL 或改用本地图片。
- **视频处理超时**：视频上传后需等待处理（最长 10 分钟），超时后提示重试。
- **标题过长**：自动缩短标题，保持语义。
- **页面选择器失效**：提示检查脚本中的选择器定义。
- **模板加载超时**：长文模式下模板可能加载缓慢，等待 15 秒后超时。
- **用户取消发布**：必须运行 `save-draft` 保存草稿，再告知用户已保存到草稿箱，不得直接关闭 tab。
