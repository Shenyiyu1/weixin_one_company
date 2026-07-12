#!/usr/bin/env python3
"""Fetch a Zhihu article and generate a self-contained HTML with images and formulas.

Usage: python fetch_article.py <zhihu_article_url>
Example: python fetch_article.py https://zhuanlan.zhihu.com/p/2030970565092177542

Output: zhihu_article_{article_id}/article.html + images/
"""
import asyncio, sys, os, re, hashlib, random
from pathlib import Path
from playwright.async_api import async_playwright
import requests

STEALTH_SCRIPT = """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en'] });
delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
window.chrome = { runtime: {}, loadTimes: function() {}, csi: function() {}, app: {} };
"""

USER_DATA_DIR = os.path.join(os.path.expanduser("~"), ".openclaw", "workspace", "chrome_user_data")
TIMEOUT_LOGIN = 180  # seconds to wait for user login


def download_image(url, img_dir):
    """Download a single image with Zhihu referer, return local path."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://zhuanlan.zhihu.com/"
        }
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        ct = r.headers.get("content-type", "")
        ext = ".jpg"
        if "png" in ct: ext = ".png"
        elif "gif" in ct: ext = ".gif"
        elif "svg" in ct: ext = ".svg"
        elif "webp" in ct: ext = ".webp"
        h = hashlib.md5(url.encode()).hexdigest()[:12]
        fname = f"{h}{ext}"
        with open(img_dir / fname, "wb") as f:
            f.write(r.content)
        return f"images/{fname}"
    except Exception as e:
        print(f"  Warning: {url[:60]} -> {e}")
        return url


def convert_math(html):
    """Convert Zhihu math formats to KaTeX delimiters.

    Zhihu uses multiple overlapping renderers:
    1. <script type="math/tex;mode=display"> - MathJax block
    2. <script type="math/tex"> - MathJax inline
    3. <span class="ztext-math" data-eeimg="2" data-tex="..."> - custom block
    4. <span class="ztext-math" data-eeimg="1" data-tex="..."> - custom inline
    5. <span class="math-holder"> - hidden fallback text (duplicate, remove)
    """
    # Primary: MathJax script tags
    html = re.sub(
        r'<script[^>]*type="math/tex;mode=display"[^>]*>\s*(.*?)\s*</script>',
        lambda m: f'<span class="katex-block">$${m.group(1).strip()}$$</span>',
        html, flags=re.DOTALL
    )
    html = re.sub(
        r'<script[^>]*type="math/tex"[^>]*>\s*(.*?)\s*</script>',
        lambda m: f'<span class="katex-inline">${m.group(1).strip()}$</span>',
        html, flags=re.DOTALL
    )
    # Remove duplicate renderers
    html = re.sub(
        r'<span[^>]*class="[^"]*ztext-math[^"]*"[^>]*>.*?</span>',
        '', html, flags=re.DOTALL
    )
    html = re.sub(
        r'<span[^>]*class="[^"]*math-holder[^"]*"[^>]*>.*?</span>',
        '', html, flags=re.DOTALL
    )
    # Deduplicate adjacent identical blocks
    html = re.sub(
        r'(<span class="katex-block">\$\$.*?\$\$</span>)\s*\1',
        r'\1', html, flags=re.DOTALL
    )
    return html


def clean_html(html):
    """Strip Zhihu-specific wrappers without losing content."""
    html = re.sub(r'<noscript[^>]*>.*?</noscript>', '', html, flags=re.DOTALL)
    html = re.sub(
        r'<span[^>]*class="[^"]*RichText-EasyImgLoading[^"]*"[^>]*>.*?</span>',
        '', html, flags=re.DOTALL
    )
    html = re.sub(r'\s*class="(?!katex-block|katex-inline)[^"]*"', '', html)
    html = re.sub(r'\s*data-[a-z-]+="[^"]*"', '', html)
    return html


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/katex.min.css">
<style>
  :root {{
    --bg: #fff; --text: #1a1a1a; --text-secondary: #666;
    --border: #e8e8e8; --code-bg: #f5f5f5; --link: #0066cc;
    --table-header: #f0f4f8; --table-stripe: #fafbfc;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
      "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
    background: #f7f8fa; color: var(--text); line-height: 1.8; font-size: 16px;
  }}
  .container {{ max-width: 780px; margin: 0 auto; padding: 40px 24px 80px; }}
  article {{
    background: var(--bg); border-radius: 12px; padding: 48px 56px;
    box-shadow: 0 1px 3px rgba(0,0,0,.08);
  }}
  h1 {{ font-size: 2em; font-weight: 700; line-height: 1.4; margin-bottom: 16px; color: #111; }}
  .meta {{ color: var(--text-secondary); font-size: 14px; margin-bottom: 36px; padding-bottom: 24px; border-bottom: 1px solid var(--border); }}
  .meta a {{ color: var(--link); text-decoration: none; }}
  .meta a:hover {{ text-decoration: underline; }}
  h2 {{ font-size: 1.5em; font-weight: 600; margin: 40px 0 16px; padding-bottom: 8px; border-bottom: 2px solid #0066cc; color: #111; }}
  h3 {{ font-size: 1.25em; font-weight: 600; margin: 32px 0 12px; color: #222; }}
  h4 {{ font-size: 1.1em; font-weight: 600; margin: 24px 0 8px; color: #333; }}
  p {{ margin: 12px 0; }}
  strong, b {{ font-weight: 600; color: #111; }}
  ul, ol {{ margin: 12px 0; padding-left: 24px; }}
  li {{ margin: 6px 0; }}
  blockquote {{
    margin: 16px 0; padding: 12px 20px; border-left: 4px solid #0066cc;
    background: #f0f5ff; border-radius: 0 6px 6px 0; color: #333;
  }}
  code {{
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
    font-size: 0.9em; background: var(--code-bg); padding: 2px 6px;
    border-radius: 3px; border: 1px solid #eee;
  }}
  pre {{
    margin: 16px 0; padding: 20px 24px; background: #282c34; color: #abb2bf;
    border-radius: 8px; overflow-x: auto; font-size: 14px; line-height: 1.6;
  }}
  pre code {{ background: none; padding: 0; border: none; color: inherit; }}
  table {{
    width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px;
  }}
  thead th {{
    background: var(--table-header); font-weight: 600; text-align: left;
    padding: 10px 14px; border: 1px solid var(--border); white-space: nowrap;
  }}
  tbody td {{ padding: 8px 14px; border: 1px solid var(--border); vertical-align: top; }}
  tbody tr:nth-child(even) {{ background: var(--table-stripe); }}
  tbody tr:hover {{ background: #eef4ff; }}
  figure {{ margin: 24px 0; text-align: center; }}
  figure img, img {{ max-width: 100%; height: auto; border-radius: 6px; box-shadow: 0 2px 8px rgba(0,0,0,.1); }}
  .katex-display {{ margin: 16px 0; overflow-x: auto; overflow-y: hidden; }}
  .katex-inline .katex, .katex-block .katex {{ font-size: 1.05em; }}
  hr {{ border: none; border-top: 1px solid var(--border); margin: 32px 0; }}
  @media (max-width: 768px) {{
    article {{ padding: 24px 20px; }}
    h1 {{ font-size: 1.5em; }}
    .container {{ padding: 16px 8px 40px; }}
    table {{ font-size: 12px; }}
    thead th, tbody td {{ padding: 6px 8px; }}
  }}
  @media print {{
    body {{ background: white; }}
    article {{ box-shadow: none; }}
  }}
</style>
</head>
<body>
<div class="container">
<article>
<h1>{title}</h1>
<div class="meta">
  作者: <strong>{author}</strong> &nbsp;|&nbsp;
  原文: <a href="{url}" target="_blank" rel="noopener">知乎链接</a>
</div>
{content}
</article>
</div>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/contrib/auto-render.min.js"></script>
<script>
document.addEventListener("DOMContentLoaded", function() {{
  renderMathInElement(document.body, {{
    delimiters: [
      {{left: "$$", right: "$$", display: true}},
      {{left: "$", right: "$", display: false}},
      {{left: "\\\\[", right: "\\\\]", display: true}},
      {{left: "\\\\(", right: "\\\\)", display: false}},
      {{left: "\\\\begin{{equation}}", right: "\\\\end{{equation}}", display: true}},
      {{left: "\\\\begin{{align}}", right: "\\\\end{{align}}", display: true}},
    ],
    throwOnError: false, trust: true, strict: false
  }});
}});
</script>
</body>
</html>"""


async def fetch_article(url):
    """Main pipeline: login -> fetch -> extract -> download images -> generate HTML."""
    article_id = re.search(r'/p/(\d+)', url)
    article_id = article_id.group(1) if article_id else 'unknown'
    output_dir = Path(f"zhihu_article_{article_id}")
    output_dir.mkdir(exist_ok=True)
    img_dir = output_dir / "images"
    img_dir.mkdir(exist_ok=True)
    os.makedirs(USER_DATA_DIR, exist_ok=True)

    print(f"[1/5] 启动浏览器...")
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            USER_DATA_DIR, headless=False,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1440, 'height': 900},
            locale='zh-CN', timezone_id='Asia/Shanghai',
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        await context.add_init_script(STEALTH_SCRIPT)
        page = context.pages[0] if context.pages else await context.new_page()

        # Login check
        await page.goto('https://www.zhihu.com/', wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(2)
        cookies = await context.cookies('https://www.zhihu.com')
        if 'z_c0' not in [c['name'] for c in cookies]:
            print(f"[2/5] 需要登录！请在浏览器中扫码或手机号登录...")
            for i in range(TIMEOUT_LOGIN // 2):
                await asyncio.sleep(2)
                cookies = await context.cookies('https://www.zhihu.com')
                if 'z_c0' in [c['name'] for c in cookies]:
                    print("\n      登录成功！")
                    break
                print(f"      等待... ({i*2//60}分{i*2%60}秒)", end='\r')
            else:
                print("\nERROR: 登录超时")
                await context.close()
                sys.exit(1)
        else:
            print(f"[2/5] 登录态有效，跳过登录")

        # Fetch article
        print(f"[3/5] 加载文章: {url}")
        await page.goto(url, wait_until='domcontentloaded', timeout=60000)
        await page.wait_for_timeout(2000)

        try:
            await page.wait_for_selector('.Post-RichText, .RichText.ztext', timeout=15000)
        except Exception:
            print("ERROR: 未找到文章内容区域，可能需要登录或页面结构已变化")
            await context.close()
            sys.exit(1)

        await page.wait_for_timeout(3000)

        # Scroll to trigger lazy loading
        for _ in range(8):
            await page.evaluate(f'window.scrollBy(0, {random.randint(400, 800)})')
            await page.wait_for_timeout(random.randint(800, 1200))

        await page.evaluate('window.scrollTo(0, 0)')
        await page.wait_for_timeout(1000)

        # Extract from DOM
        print(f"[4/5] 提取内容...")
        data = await page.evaluate('''() => {
            const title = document.querySelector('h1.Post-Title, h1[class*="Title"]')?.innerText?.trim() || '';
            const author = document.querySelector('.AuthorInfo-name, a[class*="Author"]')?.innerText?.trim() || '';
            const content = document.querySelector('.Post-RichText, .RichText.ztext, article .RichText');
            return { title, author, html: content ? content.innerHTML : '' };
        }''')

        title = data['title']
        author = data['author']
        content = data['html']
        await context.close()

    if not content:
        print("ERROR: 未能提取文章内容")
        sys.exit(1)

    print(f"      标题: {title}")
    print(f"      作者: {author}")
    print(f"      内容: {len(content)} 字符")

    # Process content
    content = convert_math(content)
    content = clean_html(content)

    # Download images
    img_urls = re.findall(r'<img[^>]+src="([^"]+)"', content)
    img_urls += re.findall(r"<img[^>]+src='([^']+)'", content)
    img_urls = [u for u in img_urls if u.startswith('http')]

    print(f"[5/5] 下载图片 ({len(img_urls)} 张)...")
    for i, url in enumerate(img_urls):
        print(f"      [{i+1}/{len(img_urls)}] {url[:70]}...")
        local = download_image(url, img_dir)
        content = content.replace(url, local)

    content = re.sub(r'srcset="[^"]*"', '', content)
    content = re.sub(r'sizes="[^"]*"', '', content)

    # Escape HTML entities in title/author for safe embedding
    def escape(s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    html_out = HTML_TEMPLATE.format(
        title=escape(title), author=escape(author), url=url, content=content
    )

    output_path = output_dir / "article.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_out)

    img_count = len(list(img_dir.glob('*')))
    print(f"\n完成! {output_path}")
    print(f"  图片: {img_dir} ({img_count} 张)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python fetch_article.py <知乎文章URL>")
        print("示例: python fetch_article.py https://zhuanlan.zhihu.com/p/2030970565092177542")
        sys.exit(1)
    asyncio.run(fetch_article(sys.argv[1]))
