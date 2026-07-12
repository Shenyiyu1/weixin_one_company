#!/usr/bin/env python3
"""Render Mermaid diagrams (<pre class="mermaid">) in HTML to PNG images using Playwright.

Usage:
  python scripts/render_mermaid.py --input output/paper/paper_analysis.html
  python scripts/render_mermaid.py --input output/paper/paper_analysis.html --output output/paper/paper_wechat.html --dir output/paper/formulas
"""

import re
import sys
import hashlib
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright

MERMAID_CDN = "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"
TEMP_HTML_TEMPLATE = """<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<script src="{mermaid_cdn}"></script>
<script>mermaid.initialize({{startOnLoad:true,theme:'default',securityLevel:'loose'}});</script>
<style>
body{{margin:0;padding:24px;background:#fff;font-family:sans-serif;}}
.mermaid-wrap{{margin-bottom:24px;}}
</style>
</head><body>
{body}
</body></html>"""


def sanitize_name(mermaid_code: str) -> str:
    h = hashlib.md5(mermaid_code.encode()).hexdigest()[:8]
    return f"mermaid_{h}"


def render_all_mermaid(html_path: str, *, output_dir: Path) -> dict[str, str]:
    """Extract all Mermaid blocks, render them in one page, screenshot each SVG. Returns {code_hash: relative_png_path}."""
    content = Path(html_path).read_text(encoding="utf-8")
    blocks = re.findall(r'<pre class="mermaid">(.*?)</pre>', content, re.DOTALL)

    if not blocks:
        print("No <pre class=\"mermaid\"> blocks found.", file=sys.stderr)
        return {}

    # Build temp HTML with all diagrams
    body_parts = []
    for i, block in enumerate(blocks):
        body_parts.append(f'<div class="mermaid-wrap"><pre class="mermaid">{block}</pre></div>')

    temp_html = TEMP_HTML_TEMPLATE.format(
        mermaid_cdn=MERMAID_CDN,
        body="\n".join(body_parts)
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    result = {}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 800})
        page.set_content(temp_html)
        page.wait_for_selector("svg", timeout=30000)
        page.wait_for_timeout(2000)

        svg_elements = page.query_selector_all("svg")
        for i, svg_el in enumerate(svg_elements):
            box = svg_el.bounding_box()
            if not box:
                print(f"  [SKIP] mermaid block {i+1}: no bounding box", file=sys.stderr)
                continue

            code = blocks[i]
            name = sanitize_name(code)
            png_path = output_dir / f"{name}.png"

            if png_path.exists():
                print(f"  [CACHE] {name}.png (already exists)", file=sys.stderr)
            else:
                svg_el.screenshot(path=str(png_path))
                print(f"  [OK] {name}.png ({png_path.stat().st_size}B)", file=sys.stderr)

            result[name] = str(png_path.relative_to(Path(html_path).parent).as_posix())

        browser.close()

    return result


def process_html(html_path: str, output_path: str, output_dir: Path) -> int:
    content = Path(html_path).read_text(encoding="utf-8")
    blocks = re.findall(r'<pre class="mermaid">(.*?)</pre>', content, re.DOTALL)
    png_map = render_all_mermaid(html_path, output_dir=output_dir)

    def replace_block(m):
        code = m.group(1)
        name = sanitize_name(code)
        if name in png_map:
            rel_path = png_map[name]
            escaped = code.strip().replace('"', '&quot;')[:80]
            return f'<p style="text-align:center;"><img src="{rel_path}" alt="mermaid: {escaped}" style="max-width:100%;height:auto;"></p>'
        return f'<p style="font-size:14px;color:#999;text-align:center;background:#f9fafb;padding:12px;border-radius:6px;">[Mermaid 图表: {code.strip()[:60]}...]</p>'

    content = re.sub(r'<pre class="mermaid">(.*?)</pre>', replace_block, content, count=0, flags=re.DOTALL)
    Path(output_path).write_text(content, encoding='utf-8')
    return len(png_map)


def main():
    parser = argparse.ArgumentParser(description='Render Mermaid diagrams in HTML to PNG')
    parser.add_argument('--input', required=True, help='Input HTML with <pre class="mermaid"> blocks')
    parser.add_argument('--output', default=None, help='Output HTML (default: overwrite input)')
    parser.add_argument('--dir', default='formulas', help='Output directory for PNGs (default: <input dir>/formulas)')
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        print(f'Error: input file not found: {input_path}', file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output).resolve() if args.output else input_path
    img_dir = (input_path.parent / args.dir).resolve()

    print(f'Input:  {input_path}', file=sys.stderr)
    print(f'Output: {output_path}', file=sys.stderr)
    print(f'Images: {img_dir}', file=sys.stderr)

    count = process_html(str(input_path), str(output_path), img_dir)
    print(f'\nDone: {count} Mermaid diagrams rendered', file=sys.stderr)


if __name__ == '__main__':
    main()
