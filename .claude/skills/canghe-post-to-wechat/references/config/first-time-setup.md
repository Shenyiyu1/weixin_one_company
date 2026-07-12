---
name: first-time-setup
description: First-time setup flow for canghe-post-to-wechat preferences
---

# First-Time Setup

## Overview

When no EXTEND.md is found, guide user through preference setup.

**BLOCKING OPERATION**: This setup MUST complete before ANY other workflow steps. Do NOT:
- Ask about content or files to publish
- Ask about themes or publishing methods
- Proceed to content conversion or publishing

ONLY ask the questions in this setup flow, save EXTEND.md, then continue.

## Setup Flow

```
No EXTEND.md found
        |
        v
+---------------------+
| AskUserQuestion     |
| (all questions)     |
+---------------------+
        |
        v
+---------------------+
| Create EXTEND.md    |
+---------------------+
        |
        v
    Continue to Step 1
```

## Questions

**Language**: Use user's input language or saved language preference.

Use AskUserQuestion with up to 4 questions per call. Ask questions in batches (max 4 per batch):

### Question 1: Default Theme

```yaml
header: "Theme"
question: "Default theme for article conversion?"
options:
  - label: "default (Recommended)"
    description: "Classic layout - centered title with border, white-on-color H2"
  - label: "grace"
    description: "Elegant - text shadows, rounded cards, refined blockquotes"
  - label: "simple"
    description: "Minimal modern - asymmetric rounded corners, clean whitespace"
```

### Question 2: Default Publishing Method

```yaml
header: "Method"
question: "Default publishing method?"
options:
  - label: "api (Recommended)"
    description: "Fast, requires API credentials (AppID + AppSecret)"
  - label: "browser"
    description: "Slow, requires Chrome and login session"
```

### Question 3: Default Author

```yaml
header: "Author"
question: "Default author name for articles?"
options:
  - label: "No default"
    description: "Leave empty, specify per article"
```

Note: User will likely choose "Other" to type their author name.

### Question 4: Open Comments

```yaml
header: "Comments"
question: "Enable comments on articles by default?"
options:
  - label: "Yes (Recommended)"
    description: "Allow readers to comment on articles"
  - label: "No"
    description: "Disable comments by default"
```

### Question 5: Fans-Only Comments

```yaml
header: "Fans only"
question: "Restrict comments to followers only?"
options:
  - label: "No (Recommended)"
    description: "All readers can comment"
  - label: "Yes"
    description: "Only followers can comment"
```

### Question 6: Save Location

```yaml
header: "Save"
question: "Where to save preferences?"
options:
  - label: "Project (Recommended)"
    description: ".canghe-skills/ (this project only)"
  - label: "User"
    description: "~/.canghe-skills/ (all projects)"
```

### Question 7: Content Review

```yaml
header: "Review"
question: "Enable AI content review before publishing?"
options:
  - label: "Yes (Recommended)"
    description: "AI reviews content for platform compliance, quality, and errors before publishing"
  - label: "No"
    description: "Skip review, publish directly (faster)"
```

### Question 8: Review Model (only if Question 7 = Yes)

```yaml
header: "Review Model"
question: "Which AI model should review your content?"
options:
  - label: "Haiku (Recommended)"
    description: "Fast, affordable, good for basic compliance + quality checks"
  - label: "Sonnet"
    description: "More thorough review for important articles"
  - label: "Opus"
    description: "Maximum review quality (slowest, most expensive)"
```

### Question 9: Review Strictness (only if Question 7 = Yes)

```yaml
header: "Strictness"
question: "How strict should the content review be?"
options:
  - label: "Moderate (Recommended)"
    description: "Balanced — flag clear issues, ignore minor style preferences"
  - label: "Strict"
    description: "Flag everything — ideal for brand content and client work"
  - label: "Relaxed"
    description: "Only flag clear errors and platform violations"
```

## Save Locations

| Choice | Path | Scope |
|--------|------|-------|
| Project | `.canghe-skills/canghe-post-to-wechat/EXTEND.md` | Current project |
| User | `~/.canghe-skills/canghe-post-to-wechat/EXTEND.md` | All projects |

## After Setup

1. Create directory if needed
2. Write EXTEND.md
3. Confirm: "Preferences saved to [path]"
4. Continue to Step 0 (load the saved preferences)

## EXTEND.md Template

```md
default_theme: [default/grace/simple]
default_publish_method: [api/browser]
default_author: [author name or empty]
need_open_comment: [1/0]
only_fans_can_comment: [1/0]
chrome_profile_path:
review_enabled: [true/false]
review_model: [haiku/sonnet/opus]
review_strictness: [strict/moderate/relaxed]
```

## Modifying Preferences Later

Users can edit EXTEND.md directly or delete it to trigger setup again.
