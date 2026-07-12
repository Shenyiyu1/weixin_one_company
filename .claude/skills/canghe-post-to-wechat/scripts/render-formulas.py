#!/usr/bin/env python3
"""Render LaTeX formulas ($...$ and $$...$$) in HTML to PNG images using local LaTeX + dvipng.

Usage:
  python render-formulas.py --input article.html
  python render-formulas.py --input article.html --output rendered.html --formulas-dir imgs/formulas --dpi 200
"""

import re
import subprocess
import os
import hashlib
import shutil
import argparse
import sys
from pathlib import Path

PREAMBLE = r"""\documentclass[preview,border=4pt]{standalone}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsfonts}
\begin{document}
"""


def sanitize_filename(formula: str) -> str:
    h = hashlib.md5(formula.encode()).hexdigest()[:8]
    return f'formula_{h}'


def render_formula(formula: str, *, formulas_dir: Path, work_dir: Path, dpi: int = 150, display: bool = False) -> str | None:
    """Render a single LaTeX formula to PNG. Returns relative path to PNG or None on failure."""
    safe_name = sanitize_filename(formula)
    png_path = formulas_dir / f'{safe_name}.png'

    if png_path.exists():
        return str(png_path)

    body = rf'$\displaystyle {formula}$' if display else f'${formula}$'
    tex_content = PREAMBLE + body + '\n\\end{document}'

    tex_file = work_dir / f'{safe_name}.tex'
    tex_file.write_text(tex_content, encoding='utf-8')

    result = subprocess.run(
        ['latex', '-interaction=nonstopmode', '-halt-on-error',
         '-output-directory', str(work_dir), str(tex_file)],
        capture_output=True, text=True, cwd=str(work_dir), timeout=30
    )

    dvi_file = work_dir / f'{safe_name}.dvi'
    if not dvi_file.exists():
        print(f'  [FAIL] latex: {formula[:70]}', file=sys.stderr)
        return None

    subprocess.run(
        ['dvipng', '-D', str(dpi), '-T', 'tight', '-bg', 'Transparent',
         '-o', str(png_path), str(dvi_file)],
        capture_output=True, text=True, timeout=30
    )

    if png_path.exists():
        print(f'  [OK] {formula[:70]} -> {png_path.name} ({png_path.stat().st_size}B)', file=sys.stderr)
        return str(png_path)
    else:
        print(f'  [FAIL] dvipng: {formula[:70]}', file=sys.stderr)
        return None


def process_html(html_path: str, *, formulas_dir: Path, work_dir: Path, dpi: int = 150) -> tuple[str, int]:
    """Replace $...$ and $$...$$ in HTML with <img> tags pointing to rendered PNGs."""
    content = Path(html_path).read_text(encoding='utf-8')
    formulas = {}

    def process_display(m):
        latex = m.group(1).strip()
        if latex not in formulas:
            formulas[latex] = render_formula(latex, formulas_dir=formulas_dir, work_dir=work_dir, dpi=dpi, display=True)
        png_path = formulas[latex]
        if png_path:
            png_rel = str(Path(png_path).relative_to(Path(html_path).parent).as_posix()) if png_path else ''
            return f'<img src="{png_rel}" alt="{latex}" style="display:block;margin:12px auto;max-width:100%;height:auto;">'
        return f'<p style="font-size:14px;color:#555;text-align:center;background:#f9fafb;padding:8px;border-radius:6px;">{latex}</p>'

    content = re.sub(r'\$\$\s*(.+?)\s*\$\$', process_display, content, flags=re.DOTALL)

    def process_inline(m):
        latex = m.group(1).strip()
        if latex not in formulas:
            formulas[latex] = render_formula(latex, formulas_dir=formulas_dir, work_dir=work_dir, dpi=dpi, display=False)
        png_path = formulas[latex]
        if png_path:
            png_rel = str(Path(png_path).relative_to(Path(html_path).parent).as_posix()) if png_path else ''
            return f'<img src="{png_rel}" alt="{latex}" style="vertical-align:middle;max-width:100%;height:auto;">'
        return f'<code style="font-family:monospace;font-size:0.9em;">{latex}</code>'

    content = re.sub(r'\$(.+?)\$', process_inline, content)

    return content, len(formulas)


def main():
    parser = argparse.ArgumentParser(description='Render LaTeX formulas in HTML to PNG images')
    parser.add_argument('--input', required=True, help='Input HTML file with $...$ / $$...$$ formulas')
    parser.add_argument('--output', default=None, help='Output HTML file (default: overwrite input)')
    parser.add_argument('--formulas-dir', default='formulas', help='Directory for PNG files (default: ./formulas)')
    parser.add_argument('--work-dir', default='_latex_work', help='Temp directory for .tex/.dvi (default: ./_latex_work)')
    parser.add_argument('--dpi', type=int, default=150, help='DPI for PNG output (default: 150)')
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        print(f'Error: input file not found: {input_path}', file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output).resolve() if args.output else input_path
    formulas_dir = (input_path.parent / args.formulas_dir).resolve()
    work_dir = (input_path.parent / args.work_dir).resolve()

    formulas_dir.mkdir(exist_ok=True)
    work_dir.mkdir(exist_ok=True)

    print(f'Input:  {input_path}', file=sys.stderr)
    print(f'Output: {output_path}', file=sys.stderr)
    print(f'Images: {formulas_dir}', file=sys.stderr)

    content, count = process_html(str(input_path), formulas_dir=formulas_dir, work_dir=work_dir, dpi=args.dpi)

    output_path.write_text(content, encoding='utf-8')
    print(f'\nDone: {count} unique formulas rendered', file=sys.stderr)

    shutil.rmtree(work_dir, ignore_errors=True)


if __name__ == '__main__':
    main()
