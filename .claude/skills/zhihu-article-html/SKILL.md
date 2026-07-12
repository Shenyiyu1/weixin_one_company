---
name: zhihu-article-html
description: "知乎文章转 HTML：登录态浏览器抓取、图片本地化、公式 KaTeX 渲染、中译英、自包含 HTML 输出。| Zhihu article to self-contained HTML with images, formulas, and English translation."
version: "2.0.0"
user-invocable: true
argument-hint: "<知乎文章URL>"
allowed-tools: Read, Write, Edit, Bash
---

# 知乎文章 → 自包含 HTML

从知乎文章 URL 生成一个**自包含 HTML 文件**：图片下载到本地 `images/`，公式用 KaTeX 渲染，表格/代码块完整保留，支持中译英。

## 依赖

```bash
pip install playwright requests translate
playwright install chromium
```

## 用法

### 1. 抓取文章

```bash
python ${CLAUDE_SKILL_DIR}/scripts/fetch_article.py <知乎文章URL>
```

示例：
```bash
python ${CLAUDE_SKILL_DIR}/scripts/fetch_article.py https://zhuanlan.zhihu.com/p/2030970565092177542
```

输出目录：`zhihu_article_{文章ID}/`
- `article.html` — 自包含 HTML（中文原文）
- `images/` — 本地化图片

### 2. 翻译为英文

```bash
python ${CLAUDE_SKILL_DIR}/scripts/translate_article.py <zhihu_article_{id}/article.html>
```

示例：
```bash
python ${CLAUDE_SKILL_DIR}/scripts/translate_article.py zhihu_article_2030970565092177542/article.html
```

输出目录：`zhihu_article_{文章ID}_en/`
- `article.html` — 英文翻译版
- `images/` — 从原文目录复制（需手动复制或脚本自动处理）

翻译后端自动选择：
1. **DeepSeek API**（高质量）— 需设置环境变量 `DEEPSEEK_API_KEY`
2. **translate 库**（免费，无需 API key）— 自动回退

### 3. 一键抓取 + 翻译

```bash
# 抓取
python ${CLAUDE_SKILL_DIR}/scripts/fetch_article.py <URL>
# 准备英文目录
cp -r zhihu_article_{id} zhihu_article_{id}_en
# 翻译
python ${CLAUDE_SKILL_DIR}/scripts/translate_article.py zhihu_article_{id}/article.html
```

## 工作流程

### fetch_article.py（抓取）

1. **打开浏览器**（`launch_persistent_context`，复用 `~/.openclaw/workspace/chrome_user_data/` 中的登录态）
2. **检测登录**：若无 `z_c0` cookie，等待用户扫码登录（最长 3 分钟）
3. **访问文章页**，等待 DOM 加载，滚动触发懒加载
4. **DOM 提取**：`document.querySelector('.Post-RichText, .RichText.ztext')` 的 `innerHTML`
5. **公式转换**：
   - `<script type="math/tex;mode=display">` → `$$...$$`
   - `<span class="ztext-math" data-eeimg="2" data-tex="...">` → `$$...$$`
   - `<span class="ztext-math" data-eeimg="1" data-tex="...">` → `$...$`
   - `<span class="math-holder">` → 移除（重复内容）
6. **图片下载**：带 Referer 请求头下载到 `images/`，替换 src 为本地路径
7. **生成 HTML**：KaTeX CDN 渲染公式，响应式布局

### translate_article.py（翻译）

1. **检测后端**：DeepSeek API（`DEEPSEEK_API_KEY`）或 translate 库
2. **提取保护块**：`<pre><code>`、KaTeX/MathJax 公式、`<img>`、`<a>`、`<svg>`、`<code>` → 占位符
3. **翻译结构元素**：`<title>`、`<h1>`~`<h4>`、meta 标签
4. **翻译正文**：`<p>`、`<li>`、`<blockquote>`、`<th>`、`<td>` 中的中文文本
5. **恢复保护块**：占位符还原为原始 HTML
6. **输出**：`lang="en"` 的完整 HTML

## 翻译规则

| 保留不动 | 翻译 |
|----------|------|
| KaTeX/MathJax 公式 | 标题 `<title>` |
| `<pre><code>` 代码块 | 各级标题 `<h1>`~`<h4>` |
| `<img>` 标签及路径 | 段落 `<p>` |
| `<a>` 链接及 href | 列表项 `<li>` |
| `<svg>` 标签 | 引用块 `<blockquote>` |
| CSS 样式、JS 脚本 | 表格表头 `<th>` |
| 技术术语（CSA, HCA, mHC, Muon, RoPE, KV Cache, FP8, FP4 等） | 表格单元格 `<td>` |
| 所有数字、JSON 配置值 | Meta 标签（作者→Author, 原文→Source） |

## 已知限制

### 抓取
- 需要手动登录一次（登录态保存在 `chrome_user_data/`，后续可复用）
- `__INITIAL_DATA__` 不再嵌入页面，改用 DOM 提取（内容完整性依赖页面 JS 执行）
- 首次登录后浏览器窗口会保持打开约 10 秒（等待页面完全渲染）
- 若文章需要登录才能查看，必须先在浏览器中登录知乎

### 翻译
- translate 库（免费后端）对超长文本可能截断，长段落建议用 DeepSeek API
- 公式内的中文标注（如 `\text{旋转}`）不会被翻译（属于公式渲染的一部分）
- 代码块内的中文注释不会被翻译（保留原样）

## Agent 检查清单

### 抓取
```
□ 确认 playwright + requests 已安装，chromium 已下载
□ 确认 ~/.openclaw/workspace/chrome_user_data/ 存在（自动创建）
□ 运行 fetch_article.py <URL>，等待浏览器窗口
□ 如需登录，提示用户扫码；已有登录态则自动继续
□ 输出在 zhihu_article_{id}/ 目录下
□ 用浏览器打开 article.html 验证效果
```

### 翻译
```
□ 确认 translate 包已安装（pip install translate）
□ （可选）设置 DEEPSEEK_API_KEY 以使用高质量翻译
□ cp -r zhihu_article_{id} zhihu_article_{id}_en  # 复制图片
□ 运行 translate_article.py zhihu_article_{id}/article.html
□ 输出在 zhihu_article_{id}_en/article.html
□ 用浏览器打开验证翻译效果
```
