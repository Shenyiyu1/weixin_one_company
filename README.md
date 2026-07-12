# OneCompany

AI 内容发布工具包 —— 一套 Claude Code 技能，把论文、想法、图片变成微信公众号和小红书的精美内容。

## 安装

```bash
# 1. 克隆仓库
git clone https://github.com/Shenyiyu1/weixin_one_company.git
cd weixin_one_company

# 2. 创建 Python 虚拟环境
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt

# 3. 安装 Playwright 浏览器
.venv/Scripts/playwright install chromium

# 4. 配置 API Key
cp .claude/skills/xhs-content-generator/config/doubao_config.json.example \
   .claude/skills/xhs-content-generator/config/doubao_config.json
# 编辑 doubao_config.json 填入你的 API Key

# 5. 创建 Claude Code 本地配置（可选，用于自动授权）
# 参考下方「配置」章节创建 .claude/settings.local.json
```

## 快速开始

```
# 论文一条龙：深度解析 → PPT → 卡片 → 小红书发布
/paper-to-xhs https://arxiv.org/abs/2605.23904

# 论文 → 微信公众号文章
/paper-to-wechat https://arxiv.org/abs/2605.23904

# 论文 → 方法图解
/paper-comic https://arxiv.org/abs/2605.23904 --style sketchnote

# 本地图片 → AI 文案 → 小红书发布
/xhs-image-to-publish /path/to/photo.jpg
```

## 技能列表

### 论文流水线
| 技能 | 说明 |
|-------|------|
| `paper-analyzer-another` | MinerU API 解析 PDF → 深度分析长文 |
| `paper-to-xhs` | 全流程：解析 → PPT → 社交卡片 → 小红书发布 |
| `paper-to-wechat` | 全流程：解析 → 公众号排版 → 草稿发布 |
| `paper-comic` | 论文方法图解（温暖笔记风 / 论文框架图风） |

### 微信公众号
| 技能 | 说明 |
|-------|------|
| `gzh-design` | Markdown → 微信兼容 HTML（石墨极简主题） |
| `canghe-post-to-wechat` | 微信 API 创建草稿、CDN 图片上传 |
| `content-review` | 发布前 AI 审核（合规、吸引力、质量、错误） |
| `md2wechat` | 备用 Markdown → 微信转换器（CLI 工具） |

### 小红书
| 技能 | 说明 |
|-------|------|
| `xhs-auth` | 登录、会话管理、二维码认证 |
| `xhs-content-generator` | AI 内容生成（豆包 API） |
| `xhs-image-to-publish` | 一键：图片 → 文案 → 发布 |
| `xhs-publish` | 发布图文、视频、长文 |
| `xhs-explore` | 搜索笔记、浏览首页、查看用户主页 |
| `xhs-interact` | 评论、回复、点赞、收藏 |
| `xhs-content-ops` | 复合运营：竞品分析、热点追踪 |
| `post-to-xhs` | Chrome CDP 桥接浏览器发布 |

### 创意工具
| 技能 | 说明 |
|-------|------|
| `frontend-slides` | 动画 HTML 演示文稿 |
| `guizang-social-card-skill` | 社交卡片图片集、Live Photo 卡片 |

### 实用工具
| 技能 | 说明 |
|-------|------|
| `zhihu-article-html` | 知乎文章抓取 → 自包含 HTML |
| `zhihu-fetch-skill` | 批量抓取知乎收藏夹与文章 |
| `mcp-builder` | 构建 MCP 服务端 |
| `skill-creator` | 创建与评测 Claude Code 技能 |

## 共享脚本

| 脚本 | 用途 |
|--------|------|
| `slides_to_images.py` | HTML 幻灯片 → 逐页 PNG 截图 |
| `render_mermaid.py` | Mermaid 图表 → PNG 图片 |
| `capture_cover.py` | HTML 第一页 → 微信公众号封面（900×470） |

## 目录结构

```
.
├── .claude/skills/          # Claude Code 技能定义
│   ├── paper-*              # 论文分析与发布流水线
│   ├── xhs-*                # 小红书自动化
│   ├── *-post-to-wechat     # 公众号发布
│   ├── frontend-slides/     # 演示文稿
│   ├── gzh-design/          # 公众号排版
│   └── ...
├── scripts/                 # 共享工具脚本
├── .canghe-skills/          # 个人配置（已排除版本控制）
├── output/                  # 生成产物（已排除版本控制）
└── .venv/                   # Python 虚拟环境（已排除版本控制）
```

## 配置

### 环境变量

创建 `.claude/settings.local.json` 文件，填入你的 API Key：

```json
{
  "env": {
    "DASHSCOPE_API_KEY": "sk-xxx",
    "MINERU_TOKEN": "xxx",
    "DOUBAO_API_KEY": "ark-xxx"
  }
}
```

### 微信公众号凭证

创建 `.canghe-skills/.env`：

```
WECHAT_APP_ID=wx...
WECHAT_APP_SECRET=...
```

### API 依赖说明

| 服务 | 用途 | 注册地址 |
|------|------|----------|
| MinerU | PDF 解析（论文分析必选） | https://mineru.net |
| DashScope | 图片生成（社交卡片） | https://dashscope.aliyun.com |
| 豆包（Doubao） | 多模态识图 + 文生图 | https://www.volcengine.com |
| 微信公众号 | 文章发布 | https://mp.weixin.qq.com |

## License

MIT
