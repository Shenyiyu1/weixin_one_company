# Changelog

## 2026-06-06

### OpenClaw-RL 文章 v2 发布 + content-review 全流程验证

**背景**：重新用 paper-analyzer 分析论文，保留关键论文图片，生成 v2 版微信文章和小红书文案，并完整跑通 content-review 审核流程。

**新建文件**：

| 文件 | 说明 |
|------|------|
| `post-to-wechat/2026-06-06/openclaw-rl-v2.html` | v2 微信文章（含 3 张论文原图、数据表格、内联样式） |
| `output/openclaw-rl/paper_images/page-01~33.png` | 33 页 PDF 截图 |
| `output/openclaw-rl/xhs_title_v2.txt` | v2 小红书标题 |
| `output/openclaw-rl/xhs_caption_v2.txt` | v2 小红书文案 |

**发布结果**：

| 平台 | 方式 | 审核 | 状态 |
|------|------|------|------|
| 微信公众号 | API | 8.8/10 PASS | 草稿已保存 |
| 小红书 | Browser fill-publish | 8.4/10 PASS | 表单已填写，等待手动发布 |

**content-review 验证**：
- 微信文章（Haiku 模型）：8.8/10 PASS，0 critical blockers，1 warning（border-collapse），2 info
- 小红书文案（Haiku 模型）：8.4/10 PASS，0 critical blockers，2 info（标题缺 emoji、明文 GitHub URL）
- 两次审核均在 moderate 严格度下独立模型执行，验证了 content-review 技能的正确性

---

## 2026-05-30

### 微信文章改用 API 发布 + 经验沉淀

**背景**：前一天 Browser 方式发布的微信文章丢失了 HTML 格式（表格、样式变成纯文本），改用 API 方式重新发布。

**操作**：
- 用 `wechat-api.ts` + `--cover slide_01.png` 重新发布 `openclaw-rl.html`，media_id: `xnbRy2l7Vz2VCNkuXK_zNPIUrJitkvZAqRYout9-ZSNplOmdzfMwjyUETBzhbJEF`
- 保存 5 条经验到 memory：微信 API vs Browser 选择、Windows npm 缓存问题、paper-analyzer 使用规范、微信 API IP 白名单、arXiv ID 格式

**经验教训**：
- 有表格/样式的文章必须用 API 方式，Browser 剪贴板粘贴会丢失格式
- Windows 上 `npx -y bun` 报 EPERM 时直接用 `bun run`

---

## 2026-05-29

### 独立 content-review 审核技能 + OpenClaw-RL 论文全流程发布

**背景**：将微信发布流程中的内联审核逻辑（~200行）抽取为独立 `content-review` skill，同时支持微信和小红书两个平台。然后以 OpenClaw-RL 论文为测试用例，跑通「论文分析→写文章→审核→发布」完整流水线。

**新建文件**：

| 文件 | 说明 |
|------|------|
| `.claude/skills/content-review/SKILL.md` | 审核技能主文件（325行），10步平台无关工作流 |
| `.claude/skills/content-review/references/wechat.md` | 微信平台规则（合规35%/质量25%/吸引力25%/错误15%） |
| `.claude/skills/content-review/references/xhs.md` | 小红书平台规则（合规30%/吸引力30%/质量25%/错误15%） |
| `.canghe-skills/content-review/EXTEND.md` | 审核全局配置（模型haiku、严格度moderate、最多3轮） |
| `post-to-wechat/2026-05-29/openclaw-rl.html` | 微信文章 HTML（内联样式、表格、微信合规） |
| `output/openclaw-rl/paper_analysis.html` | paper-analyzer 学术型解析（34KB、71公式、2表格） |
| `output/openclaw-rl/presentation.html` | 20页 Electric Studio 组会 PPT |
| `output/openclaw-rl/mobile_cards.html` | 8页暖色卡片风手机版 |
| `output/openclaw-rl/mobile_slides/slide_01~08.png` | 手机卡片截图（390×844, 2x） |
| `output/openclaw-rl/xhs_title.txt` + `xhs_caption.txt` | 小红书标题和文案 |

**修改文件**：

| 文件 | 改动 |
|------|------|
| `.claude/skills/canghe-post-to-wechat/SKILL.md` | Step 4.5 从 ~200行审核逻辑替换为 `Skill(content-review)` 调用 |
| `.canghe-skills/canghe-post-to-wechat/EXTEND.md` | `review_model`/`review_strictness` 标记废弃，指向 content-review |
| `.claude/skills/xhs-publish/SKILL.md` | 新增 Step A.2.5/B.2.5 内容审核 |
| `.claude/skills/xhs-image-to-publish/SKILL.md` | Phase 2 用户选完文案后插入审核 |

**发布结果**：

| 平台 | 方式 | 状态 |
|------|------|------|
| 微信公众号 | Browser CDP | 草稿已保存（但格式丢失，次日用 API 重发） |
| 小红书 | Browser CDP (fill-publish) | 表单已填写，8张图片已上传，等待手动点击发布 |

**审核结果**：
- 微信文章：8.9/10 PASS，发现多余 `</section>` 标签已修复
- 小红书文案：8.4/10 PASS，0 严重问题，建议加 emoji 和互动引导

**经验教训**：
- paper-analyzer 应该第一步调用，不应手动读 PDF 写文章
- 微信 API 需要 IP 白名单（错误 40164），当天未解决，次日确认已加入
- Browser 方式发布微信文章会丢失 HTML 格式
