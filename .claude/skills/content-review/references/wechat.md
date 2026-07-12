# WeChat Official Account Review Rules

## Review Configuration

- pass_threshold: 7.0
- warn_threshold: 5.0
- scoring_weights:
  - platform_compliance: 35%
  - content_quality: 25%
  - content_attractiveness: 25%
  - error_free: 15%

## Platform Rules

### HTML Tag Rules
**Allowed tags**: `div`, `p`, `span`, `section`, `h1`-`h6`, `img`, `a`, `strong`, `b`, `em`, `i`, `u`, `s`, `del`, `br`, `hr`, `ul`, `ol`, `li`, `blockquote`, `pre`, `code`, `table`, `thead`, `tbody`, `tr`, `th`, `td`, `caption`, `sub`, `sup`, `abbr`, `fieldset`, `legend`

**Banned tags** (will be stripped by WeChat): `script`, `iframe`, `form`, `input`, `button`, `select`, `textarea`, `object`, `embed`, `video`, `audio`, `canvas`, `svg`, `link`, `meta`, `style`, `header`, `footer`, `nav`, `article`, `aside`, `main`

### CSS Rules
- **Only inline styles** (`style="..."` attribute) are allowed. `<style>` blocks and external CSS are filtered.
- `class` attributes are stripped — styles applied via classes will be lost.
- **Unsupported CSS**:
  - `position` (fixed, absolute, sticky) — all stripped
  - `float` — stripped
  - `animation`, `transition` — stripped
  - `transform` — stripped
  - `display: flex`, `display: grid` — stripped (use `display: inline-block` or `display: block`)
  - `@font-face` — custom fonts not supported
  - `@media` queries — stripped
  - CSS variables `var(--xxx)` — stripped
  - Pseudo-classes/elements (`:hover`, `::before`, `::after`) — stripped
- **Supported CSS**: `color`, `font-size`, `font-weight`, `font-style`, `text-align`, `line-height`, `text-decoration`, `letter-spacing`, `background-color`, `background`, `border`, `border-radius`, `border-left`, `border-bottom`, `margin`, `padding` (no negative values), `width`, `max-width`, `opacity`, `box-shadow`, `text-shadow`, `vertical-align`, `display` (inline, block, inline-block, none only)

### Image Rules
- Images **must** be on WeChat CDN (`mmbiz.qpic.cn` domain). External URLs are blocked.
- Formats: JPG, PNG, GIF only. **No WebP, no SVG**.
- Max 10MB per image (recommend < 2MB).
- `alt` attribute: optional but recommended for accessibility.
- GIF animations work but large GIFs may be truncated.
- `data-src` attribute supported for lazy loading.

### Link Rules
- `<a href="...">` must use full `https://` URLs.
- `<a><img/></a>` nesting may fail on WeChat — avoid wrapping images in links.
- `target="_blank"` is ignored (WeChat handles link opens).

### Content Rules
- No JavaScript event handlers (`onclick`, `onload`, etc.).
- Content length: approximately 20,000 characters max.
- No `<iframe>` embeds.
- No video/audio tags (videos must be uploaded separately via WeChat backend).
- No form elements.

### Formula / Code Rules
- MathJax / KaTeX **completely unavailable**.
- LaTeX formulas MUST be pre-rendered as PNG images.
- Code syntax highlighting must use inline `<span style="color:#...">` — cannot rely on highlight.js or similar JS libraries.

### Best Practices
- Body text: 15px, `#1a1a1a` or `#333`
- Titles: 18px
- H2 headings: 16px
- Captions/notes: 13px, `#888`
- Links: `#2563eb`
- Paragraph spacing: `margin: 10px 0`
- Heading top margin: 30-35px, bottom margin: 10-15px
- Mobile-first: `max-width: 100%` on all images

## Per-Dimension Criteria

### Platform Compliance (35%)
Check the HTML content against all rules above:
1. **Tag check**: Scan for any banned tags. Report with line/context.
2. **CSS check**: Report any `<style>` blocks, `class` attribute usage, unsupported CSS properties.
3. **Image check**: Report non-CDN images, unsupported formats (WebP/SVG), images over 10MB.
4. **Link check**: Report non-HTTPS links, `<a><img/></a>` nesting.
5. **JS/Event check**: Report any `onclick`, `onload`, or other event handler attributes.
6. **Formula check**: Report any raw `$...$` or `$$...$$` LaTeX that wasn't rendered to images.
7. **Content length**: Warn if near or over 20,000 characters.

### Content Attractiveness (25%)
1. **Title quality**: Is the title compelling and click-worthy? Does it communicate value?
2. **Opening hook**: Does the first paragraph grab attention? Start with a question, statistic, story, or bold claim?
3. **Scannability**: Good use of headings, subheadings, bullet lists, breaks? Can a reader skim and get the gist?
4. **Engaging elements**: Quotes, comparisons, examples, analogies, data points?
5. **Flow**: Does content flow logically from section to section? Are transitions smooth?
6. **Mobile readability**: Are paragraphs short enough (3-5 sentences max)? Is text broken up visually?

### Content Quality (25%)
1. **Accuracy and depth**: Is the information correct and sufficiently detailed?
2. **Readability**: Appropriate language level for the target audience.
3. **Mobile-first design**: Font sizes correct (15px body, 18px titles, 16px H2, 13px captions). Spacing appropriate. Images have max-width: 100%.
4. **Heading hierarchy**: No skipped levels (e.g., H1 → H3 without H2). Logical nesting.
5. **Code blocks**: Use inline styles for syntax highlighting (not JS-dependent).
6. **Image quality**: Proper resolution, not blurry, correct aspect ratio.
7. **Structure**: Clear introduction, body, conclusion. Logical organization.

### Error-Free (15%)
1. **Typos & spelling**: Adapt to content language. For Chinese: wrong characters (错别字), pinyin input errors. For English: standard spell-check.
2. **Grammar**: Sentence structure issues, subject-verb agreement (English), 语病 (Chinese).
3. **Links**: Broken or suspicious URLs, placeholder links.
4. **Formatting**: Inconsistent spacing, mixed punctuation styles (Chinese vs English punctuation), inconsistent heading styles.

## Strictness Impact

| Dimension | Strict | Moderate | Relaxed |
|-----------|--------|----------|---------|
| Tag check | Flag any non-whitelist tag | Flag only banned tags | Flag only banned tags |
| CSS check | Flag class usage, unsupported properties | Flag `<style>` blocks, flex/grid, position | Flag only `<style>` blocks |
| Image alt text | Required on all images | Suggested | Ignored |
| Font sizes | Must match best practices | Warn if wildly off | Ignored |
| Paragraph length | Flag >3 sentences | Flag >5 sentences | Flag only >10 sentences |
| Typos | Comprehensive check | Clear errors only | Obvious errors only |

## Edge Cases

### Long Articles (>2000 words)
Focus on structural issues and platform compliance. Sample-check ~30% for typos and formatting. Prioritize catching banned tags and CSS violations.

### Image-Heavy Articles (>20 images)
Focus primarily on image compliance: CDN URLs, supported formats, size limits, alt text (per strictness). Text quality review is lightweight.

### Non-Chinese Content
Adapt typo/grammar checking to the detected language. Check for mixed-language formatting issues (e.g., Chinese punctuation in English text).

### Technical/Code-Heavy Articles
Verify code blocks use inline styles. Check formulas are rendered as images (not raw LaTeX). Verify code font-size >= 12px for mobile readability.
