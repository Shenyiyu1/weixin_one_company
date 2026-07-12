# 微信文章 HTML 规则

微信公众平台对 HTML 有严格的白名单过滤机制，生成文章内容时务必遵守以下规则。

## 样式规则

### 仅内联样式
- **必须使用 `style="..."` 属性**，`<style>` 块和外部 CSS 会被过滤
- 禁止 `<link>` 引入外部样式表
- 使用 `class` 属性无效（样式会被剥离），只能靠内联样式

### 常用内联 CSS 属性（基本都支持）
- 文本：`color`, `font-size`, `font-weight`, `font-style`, `text-align`, `line-height`, `text-decoration`, `letter-spacing`, `word-spacing`, `white-space`
- 背景：`background-color`, `background`, `background-image`（需上传到微信 CDN）
- 边框：`border`, `border-radius`, `border-left`, `border-bottom` 等
- 间距：`margin`, `padding`（不支持负值）
- 尺寸：`width`, `max-width`（百分比和 px 均支持）
- 显示：`display`（仅 `inline`, `block`, `inline-block`, `none`）
- 其他：`opacity`, `box-shadow`, `text-shadow`, `vertical-align`

### 不支持的 CSS
- `position`（`fixed`, `absolute`, `sticky` 均无效）
- `float` 无效
- `animation`, `transition` 动画/过渡
- `transform` 变换
- `flexbox`, `grid` 布局（`display: flex` 会被移除）
- 伪类和伪元素：`:hover`, `::before`, `::after` 等
- `@font-face` 自定义字体
- `@media` 媒体查询（但移动端自适应预览本身可用）
- CSS 变量 `var(--xxx)`

## HTML 标签白名单

### 可用标签
`div`, `p`, `span`, `section`, `h1`-`h6`, `img`, `a`, `strong`, `b`, `em`, `i`, `u`, `s`, `del`, `br`, `hr`, `ul`, `ol`, `li`, `blockquote`, `pre`, `code`, `table`, `thead`, `tbody`, `tr`, `th`, `td`, `caption`, `sub`, `sup`, `abbr`, `fieldset`, `legend`

### 禁止标签（会被过滤）
`script`, `iframe`, `form`, `input`, `button`, `select`, `textarea`, `object`, `embed`, `video`, `audio`, `canvas`, `svg`, `link`, `meta`, `style`, `header`, `footer`, `nav`, `article`, `aside`, `main`

## 图片规则

- **图片必须上传到微信 CDN**（`mmbiz.qpic.cn` 域名），外链图片（非微信域名）会被屏蔽
- 格式：JPG、PNG、GIF（不支持 WebP、SVG）
- 大小：单张不超过 10MB（建议控制 2MB 以内）
- 支持 `data-src` 属性用于懒加载
- `alt` 属性可选，用于图片描述
- GIF 动图在微信中可播放，但过大可能被压缩/截断

## 链接规则

- `<a href="...">` 可用，但必须是完整的 `https://` 链接
- 不可嵌套在图片外层（`<a><img/></a>`）——在部分场景下会失效
- `target="_blank"` 无效，微信统一处理跳转

## 公式与特殊内容

- MathJax / KaTeX **完全不可用**
- LaTeX 公式必须预先渲染为 PNG 图片后嵌入
- 代码高亮需用内联样式实现（`<span style="color:#...">`），不可依赖 highlight.js 等 JS 库

## 其他限制

- **不支持 JavaScript**，所有 `<script>` 及相关事件属性（`onclick`, `onload` 等）都会被过滤
- 不支持 `<iframe>` 嵌入外部内容
- 不支持视频/音频标签，视频需通过微信后台单独上传
- 不支持表单元素
- 每篇文章总长度有限制（约 20000 字），图片过多也可能导致保存失败

## 最佳实践

1. **粘贴测试**：生成 HTML 后，在微信编辑器「源代码」模式下粘贴，切回「所见即所得」预览检查
2. **图片本地化**：所有图片先上传到微信素材库，再用返回的 `mmbiz.qpic.cn` 链接替换
3. **字号参考**：正文 15px，标题 18px，二级标题 16px，注释 13px
4. **颜色参考**：正文 `#1a1a1a` 或 `#333`，链接 `#2563eb`，注释 `#888`
5. **间距统一**：段落间距用 `margin:10px 0`，标题上间距 30-35px，下间距 10-15px
6. **移动优先**：文章主要在手机上阅读，`max-width:100%` 对图片至关重要
