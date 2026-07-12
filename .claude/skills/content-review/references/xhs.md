# XHS (小红书) Review Rules

## Review Configuration

- pass_threshold: 7.0
- warn_threshold: 5.0
- scoring_weights:
  - platform_compliance: 30%
  - content_attractiveness: 30%
  - content_quality: 25%
  - error_free: 15%

## Platform Rules

### Title Rules
- **Max 20 units** (UTF-16 code unit algorithm):
  - Chinese characters, emoji, full-width characters = weight 2
  - ASCII letters, digits, half-width punctuation = weight 1
  - Formula: `(sum of weights + 1) // 2` must be <= 20
  - Examples: "你好" = 2 units, "hello你好" = 4 units, "你好hello" = 4 units
- Title should be engaging, keyword-rich, and accurately reflect content
- Emoji in titles is encouraged (increases click-through)
- Must not be misleading or clickbait (标题党)

### Body Content Rules
- Short sentences (15-25 characters preferred), conversational tone
- Paragraph breaks every 2-3 sentences, separated by double newline
- **Banned words (违禁词)** — flag these:
  - Absolute terms: 最好, 第一, 唯一, 绝对, 国家级, 世界级, 顶级, 最高级
  - Exaggerated claims: 100%, 永不, 永久, 万能, 神效, 立即见效
  - Unverified comparisons: 比XX好, 超越所有
  - Medical claims without disclaimer
  - Financial promises (稳赚, 保证收益, 零风险)
- **Anti-spam signals** — flag these:
  - Aggressive sales language (快买, 限时抢购, 马上行动, 不要错过)
  - External contact info (WeChat ID, QQ number, phone number, email)
  - Excessive emoji density (>1 emoji per 5 characters on average)
  - ALL CAPS or excessive punctuation (!!!, ？？？)
- Content should NOT be generic AI-generated text (no personality, overly formal)
- Include personal perspective phrases (我觉得, 我个人, 说实话, 讲真)
- Encourage interaction: end with a question or call-to-action

### Hashtag Rules
- Must be placed at the **END** of the body text
- **Space-separated**: `#标签1 #标签2 #标签3` — NEVER concatenate as `#标签1#标签2#标签3`
- Each tag must start with `#`
- Recommended: 5-10 tags, relevant to content
- Tags should include: topic tags (主题标签), category tags (分类标签), and trending/event tags where appropriate
- Do NOT use irrelevant popular tags just for reach (tag stuffing)

### Image Rules
- Required for image-text posts (图文) — at least 1 image
- Formats: JPG, PNG, WebP (NOT GIF for cover)
- Max size: ~10MB per image (recommend < 2MB)
- Preferred aspect ratio: 3:4 (portrait) or 1:1 (square)
- Max 18 images per post
- Avoid:
  - QR codes (will be flagged as引流/导流)
  - Other platform watermarks (抖音, 快手, etc.)
  - Blurry or low-resolution images
  - Images with excessive text overlay

### Video Rules
- Video is a separate publishing mode (cannot mix with images)
- Processing can take up to 10 minutes
- Review focuses on title and description only (not video content itself)

### Long Article (长文) Rules
- Title: no 20-unit limit (uses textarea), but should still be concise
- Description on publish page: max 1000 characters (auto-truncated to 800)
- Content quality expectations are higher for long articles

### Anti-Spam / Frequency Rules
- No identical duplicate posts
- Recommend >5 minutes between publishes
- Daily limit: ~20 posts to avoid triggering anti-fraud
- Peak posting hours: 12:00-13:00, 18:00-21:00 (for best engagement)
- Sensitive topics: flag political,宗教, adult content — these risk post removal

## Per-Dimension Criteria

### Platform Compliance (30%)
1. **Title length**: Check title is within 20 units (UTF-16 algorithm). Flag if over.
2. **Hashtag format**: Check tags are space-separated, at end of body, each starts with `#`.
3. **Banned words**: Scan body for违禁词 and report each instance.
4. **Anti-spam signals**: Flag aggressive marketing language, contact info, excessive emoji/punctuation.
5. **Image requirements**: Check at least 1 image for image-text posts. Flag QR codes, watermarks.
6. **Sensitive topics**: Flag any content that risks platform moderation.

### Content Attractiveness (30%)
1. **Title click-worthiness**: Is the title engaging? Does it create curiosity or promise value? Use of emoji?
2. **Opening hook**: First 2-3 sentences — do they grab attention immediately?
3. **Sentence rhythm**: Short, punchy sentences. Conversational flow. Not robotic or stiff.
4. **Conversational tone (网感)**: Does it sound like a real person sharing, not a marketing script? Use of natural phrases (讲真, 说实话, 姐妹们, 家人们).
5. **Emoji usage**: Appropriate emoji placement. Enhances readability without overwhelming.
6. **Call-to-action / engagement bait**: Ends with a question, poll, or invitation to comment.
7. **Originality**: Does NOT read like generic AI-generated content. Has personality and unique perspective.
8. **Emotional resonance**: Does it connect emotionally (inspiration, curiosity, humor, empathy)?

### Content Quality (25%)
1. **Information value**: Does the content provide practical value, useful information, or genuine insight?
2. **Structure**: Clear progression. Scannable format with visual breaks (emoji as section markers, line breaks).
3. **Detail level**: Enough specifics to be credible — not vague generalities.
4. **Image-text balance**: Images support and enhance the text. Cover image is compelling.
5. **Targeting**: Content matches XHS audience expectations (lifestyle, knowledge sharing, authentic reviews).
6. **Trend awareness**: Does it connect to current XHS trends or conversations where relevant?

### Error-Free (15%)
1. **Chinese typos**: Pinyin input errors (e.g., 在/再, 的/地/得, 做/作), wrong characters.
2. **Grammar**: Sentence structure issues (语病), subject-verb agreement.
3. **Punctuation**: Consistent use of Chinese punctuation (，。) vs English punctuation (, .). No mixing within sentences.
4. **Facts**: Verify any claims, statistics, or references if possible. Flag doubtful factual claims.
5. **Formatting**: Consistent line spacing, emoji style, heading markers.

## Strictness Impact

| Dimension | Strict | Moderate | Relaxed |
|-----------|--------|----------|---------|
| Title length | Must be <= 20 units | Warn if 21-22 units | Flag only if >22 units |
| Banned words | Flag borderline cases | Flag clear违禁词 only | Flag only obvious violations |
| Hashtag format | Require 5+ tags, space check | Space check only | Warn on missing spaces |
| Anti-spam | Flag any sales-like language | Flag aggressive sales only | Flag extreme cases only |
| Conversational tone | Require网感, flag formal text | Suggest improvements | Ignored |
| Emoji usage | Flag no-emoji posts | Suggest adding emoji | Ignored |
| Typos | Comprehensive check | Clear errors only | Obvious errors only |
| Factual claims | Verify and flag | Flag suspicious claims | Ignored |

## Edge Cases

### Image-Heavy Posts
Focus review on image compliance (format, watermarks, QR codes) and hashtag correctness. Text quality review is lightweight. Verify image-text ratio is balanced.

### Video Posts
Review limited to title and description. No video content review. Focus on title attractiveness and hashtag correctness.

### Long Articles
Apply full quality review. Title length advisory only (not blocking). Content structure and depth are weighted more heavily than for short posts.

### AI-Generated Content
If content shows signs of being AI-generated (overly formal, generic structure, lack of personality), flag as a quality issue and suggest adding personal voice. This is a common XHS quality problem.

### Non-Chinese Content
XHS is primarily a Chinese platform. Non-Chinese content is unusual — flag for user confirmation. Adapt typo/grammar checking to the detected language.
