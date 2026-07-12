---
name: content-review
description: AI content review before publishing to social platforms. Supports WeChat Official Account and XHS (小红书). Checks platform compliance, content attractiveness, quality, and errors. Uses a separate model from the calling workflow. Invoke before any publish action when review is enabled.
---

# Content Review

## Language

**Match user's language**: Respond in the same language the user uses.

## Calling Convention

This skill is invoked by publishing workflows:

```
Skill(skill="content-review", args="platform=<platform> content_type=<content_type>")
```

| Parameter | Values | Required |
|-----------|--------|----------|
| `platform` | `wechat`, `xhs` | Yes |
| `content_type` | `html_article`, `image_text_post`, `video`, `long_article` | Yes |
| `model` | `haiku`, `sonnet`, `opus` | No (override EXTEND.md) |
| `strictness` | `strict`, `moderate`, `relaxed` | No (override EXTEND.md) |

Content (HTML, title, body text, image info) is extracted from the conversation context — the calling workflow has already prepared it.

## Workflow

```
Review Progress:
- [ ] Step 0: Load preferences (EXTEND.md)
- [ ] Step 1: Parse invocation context
- [ ] Step 2: Check skip conditions
- [ ] Step 3: Load platform rules
- [ ] Step 4: Prepare review input
- [ ] Step 5: Build review prompt
- [ ] Step 6: Invoke review agent (separate model)
- [ ] Step 7: Parse and present results
- [ ] Step 8: User decision
- [ ] Step 9: Handle decision & return
```

### Step 0: Load Preferences

Check EXTEND.md existence (priority order):

```bash
test -f .canghe-skills/content-review/EXTEND.md && echo "project"
test -f "$HOME/.canghe-skills/content-review/EXTEND.md" && echo "user"
```

Resolve these defaults:

| Key | Default | Description |
|-----|---------|-------------|
| `review_model` | `haiku` | Model for review sub-agent |
| `review_strictness` | `moderate` | `strict` / `moderate` / `relaxed` |
| `max_review_rounds` | `3` | Max total review rounds (initial + re-reviews) |
| `skip_content_types` | `[]` | Content types to skip review for |

If EXTEND.md not found, use defaults. No blocking setup — the skill works with defaults out of the box.

**Override priority**: args from Skill() call > EXTEND.md > skill defaults.

### Step 1: Parse Invocation Context

From the `args` string, extract:
- `platform` — `wechat` or `xhs`
- `content_type` — `html_article`, `image_text_post`, `video`, `long_article`
- `model` (optional) — override EXTEND.md
- `strictness` (optional) — override EXTEND.md

From conversation context, identify:
- Article title
- Content body (HTML for wechat html_article, plain text for xhs posts)
- Image count / paths
- Video path (if video)

### Step 2: Check Skip Conditions

Skip review (return immediately with `{decision: "skip"}`) if:
- `content_type` is in `skip_content_types` from EXTEND.md
- Content is empty or effectively empty (< 10 words)
- `platform` is not `wechat` or `xhs`

If skip, output: "Content review skipped ([reason])." and return control to the calling workflow.

### Step 3: Load Platform Rules

Read `${SKILL_DIR}/references/<platform>.md`. This file contains:
1. Review configuration (scoring weights, verdict thresholds)
2. Platform-specific rules (format requirements, banned items, best practices)
3. Per-dimension review criteria

If the reference file is missing, warn and use wechat rules as fallback.

### Step 4: Prepare Review Input

1. Detect primary language from body text: `zh`, `en`, `mixed`, `other`
2. Count media items (images for image_text_post, inline `<img>` tags for html_article)
3. Estimate word count
4. For HTML articles: strip tags to extract plain text for word count estimation

**Truncation**: If body text exceeds 2000 words, truncate to first 8000 characters. Append: `[Content truncated. Total: ~{N} words. Focus on structural review, sample-check details on the provided portion.]`

### Step 5: Build Review Prompt

Construct a self-contained prompt by inlining platform rules and content. The prompt structure follows this exact template — replace `{{PLACEHOLDERS}}` with actual values:

---

**Review Agent Prompt** (send verbatim to the sub-agent):

```
You are a {{PLATFORM_NAME}} content reviewer. Review the following content and produce a structured assessment.

## Input
- Platform: {{PLATFORM}}
- Content Type: {{CONTENT_TYPE}}
- Title: {{TITLE}}
- Language: {{LANGUAGE}}
- Review Strictness: {{STRICTNESS}} (strict/moderate/relaxed)
- Media Count: {{MEDIA_COUNT}}
{{TRUNCATION_NOTE}}

## Platform Rules
{{PLATFORM_RULES_CONTENT}}

## Content to Review
Title: {{TITLE}}
Body:
{{CONTENT_BODY}}

## Output Format
Return ONLY a JSON object (no markdown, no code fences) with this structure:

{
  "overall_score": <float 1-10>,
  "verdict": "<pass|warn|fail>",
  "platform_compliance": {
    "score": <float 1-10>,
    "issues": [
      {
        "severity": "<error|warning|info>",
        "category": "<string>",
        "description": "<specific issue>",
        "suggestion": "<how to fix>"
      }
    ]
  },
  "content_attractiveness": {
    "score": <float 1-10>,
    "strengths": ["<string>"],
    "weaknesses": ["<string>"],
    "suggestions": ["<string>"]
  },
  "content_quality": {
    "score": <float 1-10>,
    "strengths": ["<string>"],
    "weaknesses": ["<string>"],
    "suggestions": ["<string>"]
  },
  "error_free": {
    "score": <float 1-10>,
    "typos": [{"location": "<string>", "current": "<string>", "correction": "<string>"}],
    "grammar": ["<string>"],
    "broken_links": ["<string>"],
    "formatting": ["<string>"]
  },
  "summary": "<2-3 sentence overall assessment in the content's language>",
  "critical_blockers": ["<string, only issues that MUST be fixed before publishing>"]
}

## Scoring Guidelines

**Verdict determination** (from the platform rules reference):
- **pass**: overall_score meets threshold AND critical_blockers is empty → Ready to publish
- **warn**: borderline score OR minor issues only → Publishable with caveats
- **fail**: below threshold OR has critical_blockers → Should not publish without fixes

**Strictness impact**:
- **strict**: Lower tolerance. Flag minor deviations. Apply all checks strictly.
- **moderate** (default): Balanced judgment. Focus on clear issues that affect readability or compliance.
- **relaxed**: Higher tolerance. Only flag clear errors and platform violations.

**Overall score**: Weighted average using the weights defined in the platform rules reference.

**Edge cases**:
- Very long content (>2000 words): Focus on structural issues, sample-check details (~30%), prioritize platform compliance
- Image-heavy posts (>20 images): Focus review primarily on image/media compliance
- Non-Chinese content: Adapt readability norms and typo/grammar checking to the detected language
- Technical/code-heavy content: Verify code blocks/formulas are properly rendered for the platform

Write the summary in the content's language ({{LANGUAGE}}).
```

---

### Step 6: Invoke Review Agent

Use the Agent tool with a **different model** than the calling workflow:

```
Agent(
  subagent_type: "general-purpose",
  model: <resolved_review_model>,
  description: "Content review for <platform>",
  prompt: <the constructed prompt from Step 5>
)
```

The `model` parameter is the resolved value from: args > EXTEND.md > default (`haiku`).

### Step 7: Parse and Present Results

Parse the review agent's JSON output. If JSON parsing fails, inform the user:
"Review agent returned unparseable output. Retry / Skip review / Cancel?"

On success, present the report in this format:

```
┌─────────────────────────────────────────────────────────┐
│                  Content Review Report                   │
│                                                          │
│  Overall: X.X/10  ●  VERDICT                             │
│                                                          │
│  Platform Compliance    ████████████  XX/10  Label       │
│  Content Attractiveness ██████░░░░░░   X/10  Label      │
│  Content Quality        ████████░░░░   X/10  Label      │
│  Error-Free             ██████████░░   X/10  Label      │
│                                                          │
│  Issues: N critical, N warnings                          │
│                                                          │
│  ▸ [Category] Issue description                          │
│    → Fix suggestion                                      │
│                                                          │
│  Suggestions:                                            │
│  + Suggestion 1                                          │
│  + Suggestion 2                                          │
│                                                          │
│  "Summary text"                                          │
└─────────────────────────────────────────────────────────┘
```

Score bar: `█` for filled (1 per point), `░` for empty. Label: 9-10=Excellent, 7-8=Good, 5-6=Fair, 1-4=Poor.

List all issues ordered by severity (error > warning > info). Show max 5 suggestions.

### Step 8: User Decision

Use AskUserQuestion to present the decision:

```yaml
header: "Review"
question: "How would you like to proceed?"
options:
  - label: "Publish"
    description: "Accept review and proceed to publish"
  - label: "Fix & Re-review"
    description: "Make corrections based on review, then re-run review"
  - label: "Override & Publish"
    description: "Ignore warnings and publish anyway"
  - label: "Cancel"
    description: "Stop the workflow"
```

**Override restrictions**:
- If `critical_blockers` is not empty, remove the "Override" option
- If `review_strictness` is `strict`, keep Override but add a note: "Strict mode — override at your own risk"

### Step 9: Handle Decision & Return

**Track review count**: Start at 1, increment per re-review. If count reaches `max_review_rounds`, remove the "Fix & Re-review" option and show: "Maximum re-reviews reached (N)."

| User Choice | Action |
|---|---|
| **Publish** | Return `{decision: "publish", review_result: {...}}` to calling workflow |
| **Fix & Re-review** | User corrects the content, then go back to Step 4 with updated content. Increment review count. |
| **Override** | Return `{decision: "override", review_result: {...}}` to calling workflow |
| **Cancel** | Return `{decision: "cancel", review_result: {...}}` to calling workflow. Do NOT proceed to publish. |

**Agent failure recovery**: If the Agent call fails (timeout, error), show:
"Review agent failed: [error]. Retry / Skip review / Cancel?"

After returning, the calling workflow resumes. It should check the decision:
- `publish` or `override` → continue to publishing step
- `cancel` → stop the workflow

## Platform Reference File Format

Each `references/<platform>.md` follows this structure:

```markdown
# <Platform> Review Rules

## Review Configuration
- pass_threshold: <float>
- warn_threshold: <float>
- scoring_weights:
  - platform_compliance: <0-100>%
  - content_attractiveness: <0-100>%
  - content_quality: <0-100>%
  - error_free: <0-100>%

## Platform Rules
<platform-specific formatting rules, banned items, best practices>

## Per-Dimension Criteria
### Platform Compliance
<specific checks for this platform>

### Content Attractiveness
<platform-specific attractiveness criteria>

### Content Quality
<platform-specific quality criteria>

### Error-Free
<error checking guidance>

## Strictness Impact
<how strict/moderate/relaxed affects scoring for this platform>
```
