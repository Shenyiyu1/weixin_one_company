# Scripts — 共享工具脚本

项目根 `scripts/` 集中存放**跨 skill 共享**的 Python 工具。各 skill 内部脚本（CLI、API 封装等）保留在各自的 `.claude/skills/<name>/scripts/` 目录。

| 脚本 | 用途 | 调用者 |
|------|------|--------|
| `slides_to_images.py` | HTML 幻灯片 → 逐页 PNG 截图 | paper-to-xhs, paper-to-wechat |
| `render_mermaid.py` | `<pre class="mermaid">` → PNG 图片 | paper-to-wechat |
| `capture_cover.py` | presentation.html 第一页 → 微信封面图 | paper-to-wechat |

## 运行环境

```bash
.venv/Scripts/python scripts/<script>.py <args...>
```

依赖：`.venv` 中已安装 Playwright + Chromium + Pillow。
