#!/usr/bin/env python3
"""一键生成小红书文案：图片路径 → 压缩 → 识图 → 3套文案 → 写入文件.

用法:
    python generate_copy.py "C:/path/to/image.jpg"
    python generate_copy.py "C:/path/to/image.jpg" --no-compress
    python generate_copy.py "C:/path/to/image.jpg" --output-dir ./my_output

输出:
    - copy_style1.txt / copy_style2.txt / copy_style3.txt  (三套文案)
    - styles_summary.md  (全部文案汇总，便于展示)
    - image_path.txt  (原始图片绝对路径)
"""

import argparse
import os
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent.parent
XHS_CONTENT = SKILL_ROOT / "xhs-content-generator"
sys.path.insert(0, str(XHS_CONTENT / "scripts"))

from image_utils import compress_and_encode, encode_image
from doubao_api import recognize_image


def parse_copy_styles(raw: str) -> list[dict]:
    """解析豆包返回的3套文案，返回 [{style, title, body, tags}, ...]."""
    styles = [
        {"style": "温柔种草风", "title": "", "body": "", "tags": ""},
        {"style": "简约高级质感风", "title": "", "body": "", "tags": ""},
        {"style": "活泼接地气闺蜜风", "title": "", "body": "", "tags": ""},
    ]

    import re
    # 按风格名称或编号分割
    parts = re.split(r"###\s*[①②③]|\-\-\-", raw)

    if len(parts) < 4:
        # 如果分割失败，原始输出保存
        for i in range(3):
            styles[i]["raw"] = raw
        return styles

    for i in range(1, min(len(parts), 4)):
        block = parts[i].strip()
        lines = block.split("\n")
        style_idx = i - 1

        title = ""
        body_lines = []
        tags = ""

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#") and not line.startswith("##"):
                tags = line
            elif line.startswith("🔹") or line.startswith("标题"):
                title = line.lstrip("🔹").lstrip("标题").strip("：:").strip()
            elif title and not line.startswith("正文"):
                body_lines.append(line)
            elif line.startswith("正文"):
                continue

        if not title:
            # fallback: 第一行非#号行作为标题
            for line in lines:
                stripped = line.strip()
                if stripped and not stripped.startswith("#") and "标签" not in stripped:
                    title = stripped.lstrip("🔹").strip("：:").strip()
                    break

        styles[style_idx]["title"] = title
        styles[style_idx]["body"] = "\n".join(body_lines) if body_lines else block
        styles[style_idx]["tags"] = tags if tags else "#小红书 #日常分享 #种草 #好物推荐"

    return styles


def generate(image_path: str, compress: bool = True, output_dir: str = ".") -> str:
    """主流程：处理图片 → 调用 API → 写入文件."""
    abs_img = str(Path(image_path).resolve())
    if not os.path.exists(abs_img):
        print(f"[ERROR] 图片不存在: {abs_img}")
        sys.exit(1)

    print(f"[1/4] 图片编码...")
    file_size_mb = os.path.getsize(abs_img) / (1024 * 1024)
    if compress and file_size_mb > 9.5:
        print(f"  文件 {file_size_mb:.1f}MB，需要压缩...")
        b64 = compress_and_encode(abs_img, max_size_mb=9.5)
    else:
        b64 = encode_image(abs_img)
    print(f"  Base64: {len(b64):,} 字符")

    print(f"[2/4] 调用豆包多模态识图 API...")
    raw_copy = recognize_image(b64)
    print(f"  返回 {len(raw_copy)} 字符")

    print(f"[3/4] 解析文案...")
    styles = parse_copy_styles(raw_copy)

    od = Path(output_dir)
    od.mkdir(parents=True, exist_ok=True)
    image_path_file = od / "image_path.txt"
    image_path_file.write_text(abs_img, encoding="utf-8")

    # 写入单独文件
    for i, s in enumerate(styles):
        fpath = od / f"copy_style{i+1}.txt"
        text = f"{s['title']}\n\n{s['body']}\n\n{s['tags']}"
        fpath.write_text(text, encoding="utf-8")
        print(f"  → copy_style{i+1}.txt")

    # 写入汇总
    summary = []
    style_emojis = ["🌷", "✨", "👯"]
    for i, s in enumerate(styles):
        summary.append(f"### {style_emojis[i]} 风格{i+1}：{s['style']}")
        summary.append(f"**标题：** {s['title']}")
        summary.append("")
        summary.append(s["body"])
        summary.append("")
        summary.append(s["tags"])
        summary.append("")
        summary.append("---")
        summary.append("")
    summary_path = od / "styles_summary.md"
    summary_path.write_text("\n".join(summary), encoding="utf-8")
    print(f"  → styles_summary.md")

    print(f"[4/4] 完成！输出目录: {od.resolve()}")
    return str(od.resolve())


def main():
    parser = argparse.ArgumentParser(description="图片 → 小红书3套文案")
    parser.add_argument("image", help="本地图片路径")
    parser.add_argument("--no-compress", action="store_true", help="跳过压缩")
    parser.add_argument("--output-dir", "-o", default=".", help="输出目录")
    args = parser.parse_args()
    generate(args.image, compress=not args.no_compress, output_dir=args.output_dir)


if __name__ == "__main__":
    main()
