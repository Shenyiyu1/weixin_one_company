#!/usr/bin/env python3
"""Translate a Chinese Zhihu article HTML to English, preserving all HTML structure.

Two backends (auto-selected):
  1. DeepSeek API — higher quality (set DEEPSEEK_API_KEY env var)
  2. translate library — free, no API key needed (fallback)

Usage: python translate_article.py <input_html> [output_html]
  input_html:  path to Chinese article.html (e.g. zhihu_article_2030970565092177542/article.html)
  output_html: path for English output (default: <input_dir>_en/article.html)

Dependencies:
  pip install translate requests
"""

import sys, os, re, json, time
from pathlib import Path

# ── Backend detection ────────────────────────────────────────────
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
API_URL = "https://api.deepseek.com/chat/completions"
USE_DEEPSEEK = bool(DEEPSEEK_KEY)


def has_chinese(s):
    """Check if string contains Chinese characters."""
    return bool(re.search(r'[一-鿿]', s))


# ═══════════════════════════════════════════════════════════════════
# Backend 1: DeepSeek API (high quality)
# ═══════════════════════════════════════════════════════════════════

def deepseek_translate(text):
    """Translate Chinese text to English using DeepSeek API."""
    if not DEEPSEEK_KEY or not has_chinese(text):
        return text

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": (
                "You are a technical translator. Translate Chinese technical content about AI/ML "
                "to precise, idiomatic English. Preserve ALL technical terms (CSA, HCA, mHC, Muon, "
                "RoPE, KV Cache, FP8, FP4, AdamW, RMSNorm, etc.), numbers, code, and formulas. "
                "Keep the tone professional and academic. Return ONLY the translated text, no explanations."
            )},
            {"role": "user", "content": f"Translate this Chinese text to English:\n\n{text}"}
        ],
        "temperature": 0.1,
        "max_tokens": 4096
    }

    try:
        import requests as req
        r = req.post(API_URL, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"  DeepSeek API error: {e}, falling back to translate library")
        return translate_lib(text)


# ═══════════════════════════════════════════════════════════════════
# Backend 2: translate library (free, no API key)
# ═══════════════════════════════════════════════════════════════════

_translator = None

def _get_translator():
    global _translator
    if _translator is None:
        from translate import Translator
        _translator = Translator(to_lang='en', from_lang='zh')
    return _translator


def translate_lib(text):
    """Translate using the free 'translate' library with retries."""
    text = text.strip()
    if not text or not has_chinese(text) or len(text) < 2:
        return text

    t = _get_translator()
    for attempt in range(3):
        try:
            result = t.translate(text)
            return result if result else text
        except Exception as e:
            if attempt == 2:
                print(f"  Translation failed: {text[:40]}... -> {e}")
                return text
            time.sleep(1)
    return text


def translate_text(text):
    """Translate text using the available backend."""
    if USE_DEEPSEEK:
        return deepseek_translate(text)
    return translate_lib(text)


# ═══════════════════════════════════════════════════════════════════
# HTML-aware translation
# ═══════════════════════════════════════════════════════════════════

def preserve_special_blocks(html):
    """Extract blocks that must NOT be translated (formulas, code, images, links, SVGs)."""
    preserved = []

    def save(m):
        preserved.append(m.group(0))
        return f'\x00PRESERVED_{len(preserved)-1}\x00'

    # Order matters: larger blocks first
    html = re.sub(r'<pre[^>]*>.*?</pre>', save, html, flags=re.DOTALL)
    html = re.sub(r'<span class="katex-(?:block|inline)">.*?</span>', save, html, flags=re.DOTALL)
    html = re.sub(r'<span[^>]*MathJax[^>]*>.*?</span>', save, html, flags=re.DOTALL)
    html = re.sub(r'<svg[^>]*>.*?</svg>', save, html, flags=re.DOTALL)
    html = re.sub(r'<img[^>]+>', save, html)
    html = re.sub(r'<a[^>]*>.*?</a>', save, html, flags=re.DOTALL)
    html = re.sub(r'<code>[^<]*</code>', save, html)

    return html, preserved


def restore_preserved(html, preserved):
    """Restore preserved blocks back into HTML."""
    for i, block in enumerate(preserved):
        html = html.replace(f'\x00PRESERVED_{i}\x00', block)
    return html


def translate_html_element(html, tag, count=0):
    """Translate content inside HTML tags like <p>, <li>, <th>, <td>, <blockquote>."""
    # Only translate if there's Chinese content
    pattern = rf'<{tag}([^>]*)>(.*?)</{tag}>'
    matches = list(re.finditer(pattern, html, re.DOTALL))

    # Process in reverse to preserve positions
    translated_count = 0
    for m in reversed(matches):
        attrs = m.group(1)
        content = m.group(2)
        if has_chinese(content):
            translated = translate_text(content)
            old = m.group(0)
            new = f'<{tag}{attrs}>{translated}</{tag}>'
            if old != new:
                # Find and replace (using string index to avoid regex issues)
                start = m.start()
                end = m.end()
                html = html[:start] + new + html[end:]
                translated_count += 1
                if count and translated_count >= count:
                    break

    return html


def translate_html(html):
    """Main pipeline: translate all Chinese text in HTML while preserving structure."""
    # 1. Extract untouchable blocks
    html, preserved = preserve_special_blocks(html)
    print(f"  Preserved {len(preserved)} special blocks")

    # 2. Structural changes
    html = html.replace('lang="zh-CN"', 'lang="en"')

    # 3. Translate <title>
    tm = re.search(r'<title>(.*?)</title>', html)
    if tm and has_chinese(tm.group(1)):
        en = translate_text(tm.group(1))
        html = html.replace(f'<title>{tm.group(1)}</title>', f'<title>{en}</title>')
        print(f"  Title: {en[:60]}...")

    # 4. Translate headings (h1, h2, h3, h4)
    for tag in ['h1', 'h2', 'h3', 'h4']:
        for m in re.finditer(rf'<{tag}>(.*?)</{tag}>', html):
            if has_chinese(m.group(1)):
                en = translate_text(m.group(1))
                html = html.replace(f'<{tag}>{m.group(1)}</{tag}>', f'<{tag}>{en}</{tag}>', 1)
                print(f"  {tag}: {en[:50]}...")

    # 5. Meta labels
    html = html.replace('作者: ', 'Author: ')
    html = html.replace('原文: ', 'Source: ')
    html = html.replace('知乎链接', 'Zhihu Link')

    # 6. Translate body text elements
    for tag in ['p', 'li', 'blockquote', 'th', 'td']:
        print(f"  Translating <{tag}> elements...")
        html = translate_html_element(html, tag)

    # 7. Restore preserved blocks
    html = restore_preserved(html, preserved)

    return html


# ═══════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════

def main():
    if len(sys.argv) < 2:
        print("Usage: python translate_article.py <input_html> [output_html]")
        print("  Backend: DeepSeek API if DEEPSEEK_API_KEY is set, else free translate library")
        sys.exit(1)

    input_path = Path(sys.argv[1])

    if len(sys.argv) > 2:
        output_path = Path(sys.argv[2])
    else:
        # Default: <parent>_en/article.html
        parent = input_path.parent
        en_parent = Path(str(parent) + '_en')
        output_path = en_parent / 'article.html'

    if not input_path.exists():
        print(f"ERROR: {input_path} not found")
        sys.exit(1)

    backend = "DeepSeek API" if USE_DEEPSEEK else "translate library (free)"
    print(f"Translating: {input_path}")
    print(f"  Backend: {backend}")
    print(f"  Input: {len(input_path.read_text(encoding='utf-8'))} chars")

    html = input_path.read_text(encoding='utf-8')
    translated = translate_html(html)

    os.makedirs(output_path.parent, exist_ok=True)
    output_path.write_text(translated, encoding='utf-8')
    print(f"  Output: {output_path} ({len(translated)} chars)")
    print("Done!")


if __name__ == "__main__":
    main()
