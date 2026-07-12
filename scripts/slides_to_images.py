"""Convert HTML slides to individual mobile-aspect-ratio PNG images."""
import sys, os, json, http.server, socketserver, threading, time
from pathlib import Path
from playwright.sync_api import sync_playwright

HTML_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/t3_presentation.html")
OUTPUT_DIR = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("output/slides")
MOBILE_W = int(sys.argv[3]) if len(sys.argv) > 3 else 390
MOBILE_H = int(sys.argv[4]) if len(sys.argv) > 4 else 844

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Start local HTTP server for the presentation directory
HTML_DIR = HTML_PATH.resolve().parent
PORT = 8765

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(HTML_DIR), **kwargs)
    def log_message(self, format, *args):
        pass

httpd = socketserver.TCPServer(("", PORT), QuietHandler)
thread = threading.Thread(target=httpd.serve_forever, daemon=True)
thread.start()
print(f"Serving {HTML_DIR} on http://localhost:{PORT}")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": MOBILE_W, "height": MOBILE_H}, device_scale_factor=2)

    url = f"http://localhost:{PORT}/{HTML_PATH.name}"
    print(f"Loading {url}")
    page.goto(url, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(2000)  # let fonts and animations settle

    # Count slides
    slide_count = page.evaluate("() => document.querySelectorAll('.slide').length")
    print(f"Found {slide_count} slides")

    for i in range(slide_count):
        # Scroll to slide
        page.evaluate(f"""
            const slide = document.querySelectorAll('.slide')[{i}];
            slide.scrollIntoView({{ behavior: 'instant', block: 'start' }});
        """)
        page.wait_for_timeout(500)

        # Force .visible class on this slide so reveals trigger
        page.evaluate(f"""
            document.querySelectorAll('.slide').forEach((s, idx) => {{
                if (idx === {i}) s.classList.add('visible');
            }});
        """)
        page.wait_for_timeout(300)

        # Screenshot just the slide element
        element = page.query_selector(f".slide:nth-of-type({i+1})")
        if element:
            filename = f"slide_{i+1:02d}.png"
            filepath = OUTPUT_DIR / filename
            element.screenshot(path=str(filepath))
            print(f"  [{i+1}/{slide_count}] {filename}")

    browser.close()

httpd.shutdown()
print(f"\nDone! {slide_count} images saved to {OUTPUT_DIR}")
