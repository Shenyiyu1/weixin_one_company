#!/usr/bin/env python3
"""图片工具：Base64 编解码、下载、本地存储、压缩."""

import argparse
import base64
import io
import os
import random
import string
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

try:
    from PIL import Image

    HAS_PIL = True
except ImportError:
    HAS_PIL = False

DEFAULT_OUTPUT_DIR = Path.cwd() / "xhs_auto_images"
TIMEOUT = (15, 120)


def _rand_suffix(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def _generate_filename(ext: str = "png") -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"xhs_{ts}_{_rand_suffix()}.{ext}"


def encode_image(filepath: str) -> str:
    """将本地图片文件转为 Base64 字符串."""
    path = Path(filepath)
    if not path.exists():
        print(f"[ERROR] 图片文件不存在: {filepath}")
        sys.exit(1)
    ext = path.suffix.lower()
    mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
    if ext not in mime_map:
        print(f"[WARN] 未识别的图片格式: {ext}，将按 JPEG 处理")

    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def compress_image(
    filepath: str,
    max_size_mb: float = 10.0,
    max_dimension: int = 2048,
    quality_start: int = 85,
    quality_min: int = 30,
) -> tuple[bytes, str]:
    """压缩图片至目标大小以内，返回 (二进制数据, 格式扩展名).

    策略：先调 JPEG 质量，若仍超标则等比缩小尺寸.
    """
    if not HAS_PIL:
        print("[ERROR] 图片压缩需要 Pillow，请执行: pip install Pillow")
        sys.exit(1)

    path = Path(filepath)
    if not path.exists():
        print(f"[ERROR] 图片文件不存在: {filepath}")
        sys.exit(1)

    raw = path.read_bytes()
    original_mb = len(raw) / (1024 * 1024)
    print(f"[压缩] 原始大小: {original_mb:.1f} MB")

    if original_mb <= max_size_mb:
        print(f"[压缩] 已在 {max_size_mb}MB 以内，跳过")
        ext = path.suffix.lower().lstrip(".")
        return raw, ext if ext else "jpg"

    max_bytes = int(max_size_mb * 1024 * 1024)
    img = Image.open(io.BytesIO(raw))

    # 先限制尺寸上限
    w, h = img.size
    if max(w, h) > max_dimension:
        ratio = max_dimension / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
        w, h = img.size
        print(f"[压缩] 缩放至: {w}x{h}")

    # RGB
    if img.mode in ("RGBA", "P", "CMYK"):
        img = img.convert("RGB")

    # quality
    for quality in range(quality_start, quality_min - 1, -5):
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        size_mb = buf.tell() / (1024 * 1024)
        print(f"[压缩] quality={quality}: {size_mb:.1f} MB")
        if size_mb <= max_size_mb:
            print(f"[压缩] 完成 → {size_mb:.1f} MB")
            return buf.getvalue(), "jpg"

    # resize
    for scale in range(90, 30, -10):
        ratio = scale / 100
        new_size = (int(w * ratio), int(h * ratio))
        resized = img.resize(new_size, Image.LANCZOS)
        for quality in (75, 60, 45):
            buf = io.BytesIO()
            resized.save(buf, format="JPEG", quality=quality, optimize=True)
            size_mb = buf.tell() / (1024 * 1024)
            print(f"[压缩] {new_size[0]}x{new_size[1]} quality={quality}: {size_mb:.1f} MB")
            if size_mb <= max_size_mb:
                print(f"[压缩] 完成 → {size_mb:.1f} MB")
                return buf.getvalue(), "jpg"

    print("[WARN] 无法压缩到目标大小，返回最小压缩版本")
    buf = io.BytesIO()
    resized.save(buf, format="JPEG", quality=20, optimize=True)
    return buf.getvalue(), "jpg"


def compress_and_encode(filepath: str, max_size_mb: float = 10.0) -> str:
    """压缩并返回 Base64 字符串."""
    data, _ext = compress_image(filepath, max_size_mb)
    return base64.b64encode(data).decode("utf-8")


def download_image(url: str, output_dir: str | None = None, filename: str | None = None) -> str:
    """从 URL 下载图片并保存到本地目录，返回绝对路径."""
    dest = Path(output_dir) if output_dir else DEFAULT_OUTPUT_DIR
    dest.mkdir(parents=True, exist_ok=True)

    if filename is None:
        parsed = urlparse(url)
        path_part = parsed.path
        if path_part and path_part.rfind(".") > path_part.rfind("/"):
            ext = path_part.rsplit(".", 1)[-1].split("?")[0]
            ext = ext if ext.lower() in ("png", "jpg", "jpeg", "webp") else "png"
        else:
            ext = "png"
        filename = _generate_filename(ext)

    filepath = dest / filename

    for attempt in range(3):
        try:
            resp = requests.get(url, timeout=TIMEOUT, stream=True)
            resp.raise_for_status()
            with open(filepath, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"[OK] 图片已保存: {filepath}")
            return str(filepath.resolve())
        except requests.Timeout:
            print(f"[WARN] 下载超时 (attempt {attempt+1}/3)")
        except requests.RequestException as e:
            print(f"[WARN] 下载错误 (attempt {attempt+1}/3): {e}")
        if attempt < 2:
            time.sleep(2)
    print(f"[ERROR] 图片下载最终失败: {url}")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="图片工具")
    sub = parser.add_subparsers(dest="cmd")

    enc = sub.add_parser("encode", help="图片文件 → Base64")
    enc.add_argument("filepath", help="图片文件路径")

    dl = sub.add_parser("download", help="下载图片到本地")
    dl.add_argument("--url", required=True, help="图片 URL")
    dl.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="输出目录")
    dl.add_argument("--filename", default=None, help="自定义文件名（可选）")

    comp = sub.add_parser("compress", help="压缩图片到目标大小")
    comp.add_argument("filepath", help="图片文件路径")
    comp.add_argument("--max-size-mb", type=float, default=10.0, help="最大文件大小 (MB)")
    comp.add_argument("--max-dimension", type=int, default=2048, help="最大边长")
    comp.add_argument("--output", default=None, help="输出文件路径（可选）")

    cenc = sub.add_parser("compress-encode", help="压缩图片并输出 Base64")
    cenc.add_argument("filepath", help="图片文件路径")
    cenc.add_argument("--max-size-mb", type=float, default=10.0, help="最大文件大小 (MB)")

    args = parser.parse_args()

    if args.cmd == "encode":
        b64 = encode_image(args.filepath)
        print(b64)
    elif args.cmd == "download":
        path = download_image(args.url, args.output_dir, args.filename)
        print(path)
    elif args.cmd == "compress":
        data, ext = compress_image(args.filepath, args.max_size_mb, args.max_dimension)
        out_path = args.output or f"{Path(args.filepath).stem}_compressed.{ext}"
        Path(out_path).write_bytes(data)
        print(f"[OK] 已保存: {out_path}")
    elif args.cmd == "compress-encode":
        b64 = compress_and_encode(args.filepath, args.max_size_mb)
        print(b64)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
