#!/usr/bin/env python3
"""豆包（Doubao）开放平台 API 封装：多模态识图 + 文生图."""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "doubao_config.json"
RETRY_COUNT = 2
RETRY_BACKOFF = 1.5
TIMEOUT = (15, 90)


def _load_config():
    if not CONFIG_PATH.exists():
        print(f"[ERROR] 配置文件不存在: {CONFIG_PATH}")
        print("[提示] 请创建 config/doubao_config.json，格式参考 references/doubao_api.md")
        sys.exit(1)

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        raw = f.read()
    raw = os.path.expandvars(raw)
    cfg = json.loads(raw)

    for key in ("api_key", "base_url"):
        if key not in cfg or not cfg[key]:
            print(f"[ERROR] 配置缺少必填字段: {key}")
            sys.exit(1)
    return cfg


def _check_config():
    try:
        cfg = _load_config()
        print(f"[OK] base_url: {cfg['base_url']}")
        print(f"[OK] api_key: {'*' * 8}{cfg['api_key'][-4:] if len(cfg['api_key']) >= 4 else '****'}")
        print(f"[OK] multimodal_endpoint_id: {cfg.get('multimodal_endpoint_id') or cfg.get('multimodal_model', 'N/A')}")
        print(f"[OK] image_gen_endpoint_id: {cfg.get('image_gen_endpoint_id') or cfg.get('image_gen_model', 'N/A')}")
    except SystemExit:
        pass


def _post(endpoint: str, payload: dict, cfg: dict, timeout: tuple = TIMEOUT):
    """通用 POST 请求，含重试逻辑."""
    url = f"{cfg['base_url'].rstrip('/')}/{endpoint.lstrip('/')}"
    headers = {
        "Authorization": f"Bearer {cfg['api_key']}",
        "Content-Type": "application/json",
    }
    last_err = None
    for attempt in range(RETRY_COUNT + 1):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
            if resp.status_code == 200:
                return resp.json()
            err_msg = resp.text[:300] if resp.text else f"HTTP {resp.status_code}"
            print(f"[WARN] API 返回异常 (attempt {attempt+1}/{RETRY_COUNT+1}): {err_msg}")
            last_err = err_msg
        except requests.Timeout:
            print(f"[WARN] API 超时 (attempt {attempt+1}/{RETRY_COUNT+1})")
            last_err = "timeout"
        except requests.ConnectionError as e:
            print(f"[WARN] API 连接错误 (attempt {attempt+1}/{RETRY_COUNT+1}): {e}")
            last_err = str(e)
        if attempt < RETRY_COUNT:
            time.sleep(RETRY_BACKOFF * (attempt + 1))
    print(f"[ERROR] API 调用最终失败: {last_err}")
    return None


def recognize_image(image_base64: str, style_prompt: str | None = None):
    """调用豆包多模态识图 API，根据图片生成小红书文案."""
    cfg = _load_config()
    model = cfg.get("multimodal_endpoint_id") or cfg.get("multimodal_model", "doubao-vision-pro-32k")

    if style_prompt is None:
        style_prompt = (
            "你是一名小红书资深内容运营专家。请根据图片内容，生成 3 套不同风格的小红书文案。\n"
            "要求：\n"
            "- 每套文案包含：带 emoji 的标题 + 分段正文（2-3 段）+ 10 个话题标签\n"
            "- 正文使用短句，口语化，有网感，能引发评论互动\n"
            "- 正文中自然融入个人体验视角（'我个人觉得''姐妹们谁懂啊'等口语表达）\n"
            "- 3 套风格分别为：\n"
            "  ① 温柔种草风：亲切柔和，娓娓道来，适合美妆护肤/家居/美食\n"
            "  ② 简约高级质感风：冷静克制，突出品质感，适合穿搭/设计/生活方式\n"
            "  ③ 活泼接地气闺蜜风：语气像跟好姐妹分享，用流行梗和夸张语气，适合好物推荐/日常分享"
        )

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
                    {"type": "text", "text": style_prompt},
                ],
            }
        ],
        "temperature": 0.9,
        "max_tokens": 4096,
    }

    result = _post(cfg.get("multimodal_endpoint", "chat/completions"), payload, cfg)
    if result is None:
        sys.exit(1)
    try:
        content = result["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        print("[WARN] API 返回结构异常，输出原始内容")
        content = json.dumps(result, ensure_ascii=False, indent=2)
    return content


def generate_image(prompt: str, size: str = "768x1024", style: str = "写实"):
    """调用豆包文生图 API，返回图片 URL 列表."""
    cfg = _load_config()
    model = cfg.get("image_gen_endpoint_id") or cfg.get("image_gen_model", "doubao-seedream-4.0")

    width, _, height = size.partition("x")
    payload = {
        "model": model,
        "prompt": prompt,
        "n": 1,
        "size": f"{width}x{height}" if width and height else size,
        "response_format": "url",
        "style": style,
    }

    result = _post(cfg.get("image_gen_endpoint", "images/generations"), payload, cfg, timeout=(30, 180))
    if result is None:
        sys.exit(1)
    urls = []
    try:
        for item in result.get("data", []):
            if "url" in item:
                urls.append(item["url"])
    except Exception:
        print("[WARN] API 返回结构异常，输出原始内容")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return []
    if not urls:
        print("[ERROR] API 未返回图片 URL")
        sys.exit(1)
    return urls


def main():
    parser = argparse.ArgumentParser(description="豆包 API 工具")
    sub = parser.add_subparsers(dest="cmd")

    check = sub.add_parser("check-config", help="检查配置")

    recog = sub.add_parser("recognize", help="多模态识图 → 生成文案")
    recog.add_argument("--image-base64", required=True, help="图片 Base64 字符串")
    recog.add_argument("--prompt", default=None, help="自定义识图提示词（可选）")

    gen = sub.add_parser("generate", help="文生图")
    gen.add_argument("--prompt", required=True, help="生图描述")
    gen.add_argument("--size", default="768x1024", help="图片尺寸 (宽x高)")
    gen.add_argument("--style", default="写实", help="图片风格")

    args = parser.parse_args()

    if args.cmd == "check-config":
        _check_config()
    elif args.cmd == "recognize":
        content = recognize_image(args.image_base64, args.prompt)
        print(content)
    elif args.cmd == "generate":
        urls = generate_image(args.prompt, args.size, args.style)
        for u in urls:
            print(u)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
