# OneCompany

AI-powered content publishing toolkit — Claude Code skills for turning papers, ideas, and images into polished content across WeChat, XHS, and more.

## Installation

```bash
# 1. Clone this repo
git clone https://github.com/Shenyiyu1/weixin_one_company.git
cd weixin_one_company

# 2. Create Python virtual environment
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt

# 3. Install Playwright browsers
.venv/Scripts/playwright install chromium

# 4. Configure API keys
cp .claude/skills/xhs-content-generator/config/doubao_config.json.example \
   .claude/skills/xhs-content-generator/config/doubao_config.json
# Edit doubao_config.json with your API key

# 5. Create Claude Code settings (optional, for auto-allow permissions)
# Copy .claude/settings.local.json.example → .claude/settings.local.json
```

## Quick Start

```
# Paper → Deep Analysis → WeChat + XHS publishing
/paper-to-xhs https://arxiv.org/abs/2605.23904

# Paper → WeChat Official Account article
/paper-to-wechat https://arxiv.org/abs/2605.23904

# Paper → Visual diagrams
/paper-comic https://arxiv.org/abs/2605.23904 --style sketchnote

# Upload local image → AI caption → publish to XHS
/xhs-image-to-publish /path/to/photo.jpg
```

## Skills

### Paper Pipeline
| Skill | Description |
|-------|-------------|
| `paper-analyzer-another` | PDF parsing via MinerU API → deep analysis article |
| `paper-to-xhs` | Full pipeline: analysis → slides → social cards → XHS publish |
| `paper-to-wechat` | Full pipeline: analysis → WeChat formatting → draft publish |
| `paper-comic` | Visual method diagrams (sketchnote or paper-figure style) |

### WeChat Official Account (微信公众号)
| Skill | Description |
|-------|-------------|
| `gzh-design` | Markdown → WeChat-compatible HTML with graphite-minimal theme |
| `canghe-post-to-wechat` | WeChat API draft creation, CDN image upload |
| `content-review` | AI pre-publish review (compliance, quality, errors) |
| `md2wechat` | Alternative markdown-to-WeChat converter (CLI tool) |

### XHS (小红书)
| Skill | Description |
|-------|-------------|
| `xhs-auth` | Login, session management, QR code auth |
| `xhs-content-generator` | AI-powered content generation (Doubao API) |
| `xhs-image-to-publish` | One-click: image → caption → publish |
| `xhs-publish` | Publish images, videos, long articles |
| `xhs-explore` | Search feeds, browse homepage, view user profiles |
| `xhs-interact` | Comment, reply, like, favorite |
| `xhs-content-ops` | Composite workflows: competitor analysis, trend tracking |
| `post-to-xhs` | Chrome CDP bridge for browser-based publishing |

### Creative
| Skill | Description |
|-------|-------------|
| `frontend-slides` | HTML presentation slides with animations |
| `guizang-social-card-skill` | Social card image sets, Live Photo cards |

### Utilities
| Skill | Description |
|-------|-------------|
| `zhihu-article-html` | Fetch Zhihu articles → self-contained HTML |
| `zhihu-fetch-skill` | Batch fetch Zhihu collections and articles |
| `mcp-builder` | Build MCP (Model Context Protocol) servers |
| `skill-creator` | Create and benchmark new Claude Code skills |

## Scripts

| Script | Purpose |
|--------|---------|
| `slides_to_images.py` | HTML slides → PNG screenshots |
| `render_mermaid.py` | Mermaid diagrams → PNG images |
| `capture_cover.py` | HTML first page → WeChat cover image (900×470) |

## Directory Structure

```
.
├── .claude/skills/          # Claude Code skill definitions
│   ├── paper-*              # Paper analysis & publishing pipeline
│   ├── xhs-*                # XHS (小红书) automation
│   ├── *-post-to-wechat     # WeChat publishing
│   ├── frontend-slides/     # Presentation slides
│   ├── gzh-design/          # WeChat article formatting
│   └── ...
├── scripts/                 # Shared utility scripts
├── .canghe-skills/          # Personal config (gitignored)
├── output/                  # Generated content (gitignored)
└── .venv/                   # Python virtual environment (gitignored)
```

## Configuration

### Environment Variables

Create a `.claude/settings.local.json` file with your API keys:

```json
{
  "env": {
    "DASHSCOPE_API_KEY": "sk-xxx",
    "MINERU_TOKEN": "xxx",
    "DOUBAO_API_KEY": "ark-xxx"
  }
}
```

### WeChat Credentials

Create `.canghe-skills/.env`:

```
WECHAT_APP_ID=wx...
WECHAT_APP_SECRET=...
```

## License

MIT
