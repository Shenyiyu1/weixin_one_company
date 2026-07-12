#!/usr/bin/env python3
"""Capture a WeChat cover image from a paper presentation or analysis HTML.

Usage:
  python scripts/capture_cover.py output/paper/presentation.html output/paper/cover.png
  python scripts/capture_cover.py output/paper/paper_analysis.html output/paper/cover.png --size 900x500
"""

import sys
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright

WECHAT_COVER_RATIO = 1.91  # 900:500
COVER_WIDTH = 900
COVER_HEIGHT = 470
MAX_SIZE_MB = 2


def capture_from_presentation(html_path: str, output_path: str, width: int, height: int):
    """Capture the cover slide from a frontend-slides presentation.html."""
    html_dir = Path(html_path).resolve().parent
    html_name = Path(html_path).name

    import http.server
    import socketserver
    import threading

    PORT = 8766

    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(html_dir), **kwargs)

        def log_message(self, fmt, *args):
            pass

    httpd = socketserver.TCPServer(("", PORT), QuietHandler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=2)
            page.goto(f"http://localhost:{PORT}/{html_name}", wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(2000)

            slides = page.query_selector_all(".slide")
            if slides:
                slide = slides[0]
                slide.evaluate("el => el.classList.add('visible')")
                page.wait_for_timeout(500)
                slide.screenshot(path=output_path)
                print(f"Cover captured from first slide: {output_path}", file=sys.stderr)
            else:
                print("No .slide elements found, falling back to full page screenshot", file=sys.stderr)
                page.screenshot(path=output_path, full_page=True)

            browser.close()
    finally:
        httpd.shutdown()

    _post_process(output_path, width, height)


def capture_from_analysis(html_path: str, output_path: str, width: int, height: int):
    """Capture the title area from a paper analysis HTML."""
    html_dir = Path(html_path).resolve().parent
    html_name = Path(html_path).name

    import http.server
    import socketserver
    import threading

    PORT = 8767

    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(html_dir), **kwargs)

        def log_message(self, fmt, *args):
            pass

    httpd = socketserver.TCPServer(("", PORT), QuietHandler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1280, "height": 900}, device_scale_factor=2)
            page.goto(f"http://localhost:{PORT}/{html_name}", wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(2000)

            h1 = page.query_selector("h1")
            if h1:
                box = h1.bounding_box()
                if box:
                    clip = {
                        "x": max(0, box["x"] - 40),
                        "y": max(0, box["y"] - 40),
                        "width": min(1280, box["width"] + 80),
                        "height": min(900, box["height"] + 400),
                    }
                    page.screenshot(path=output_path, clip=clip)
                    print(f"Cover captured from h1 area: {output_path}", file=sys.stderr)
                else:
                    page.screenshot(path=output_path, full_page=True)
            else:
                page.screenshot(path=output_path, full_page=True)

            browser.close()
    finally:
        httpd.shutdown()

    _post_process(output_path, width, height)


def _post_process(output_path: str, width: int, height: int):
    """Resize and compress the cover image."""
    try:
        from PIL import Image
    except ImportError:
        print("Pillow not installed, skipping resize/compress", file=sys.stderr)
        return

    img = Image.open(output_path)
    original_size = img.size

    # Resize to cover dimensions (maintain aspect ratio, crop excess)
    target_ratio = width / height
    current_ratio = img.width / img.height

    if current_ratio > target_ratio:
        new_w = int(img.height * target_ratio)
        offset = (img.width - new_w) // 2
        img = img.crop((offset, 0, offset + new_w, img.height))
    else:
        new_h = int(img.width / target_ratio)
        offset = (img.height - new_h) // 2
        img = img.crop((0, offset, img.width, offset + new_h))

    img.thumbnail((width, height), Image.LANCZOS)

    # Compress to <2MB
    quality = 85
    img.save(output_path, "JPEG", quality=quality, optimize=True)
    while Path(output_path).stat().st_size > MAX_SIZE_MB * 1024 * 1024 and quality > 20:
        quality -= 10
        img.save(output_path, "JPEG", quality=quality, optimize=True)

    print(f"Cover processed: {original_size} -> {img.size}, {Path(output_path).stat().st_size}B", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Capture WeChat cover from presentation or analysis HTML")
    parser.add_argument("input", help="Path to presentation.html or paper_analysis.html")
    parser.add_argument("output", help="Output PNG path (e.g. cover.png)")
    parser.add_argument("--size", default="900x470", help="Target size WxH (default: 900x470)")
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    w, h = map(int, args.size.split("x"))
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if "presentation" in input_path.name.lower() or "slide" in input_path.name.lower():
        capture_from_presentation(str(input_path), str(output_path), w, h)
    else:
        capture_from_analysis(str(input_path), str(output_path), w, h)

    print(f"Done: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
