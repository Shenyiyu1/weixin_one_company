# LaTeX Formula Rendering for WeChat Articles

WeChat Official Account does not support MathJax/KaTeX. When publishing technical articles with math formulas, you must render LaTeX formulas as images before uploading.

## Prerequisites

- **LaTeX distribution**: TeX Live (provides `latex` and `dvipng`)
  - Windows: `D:\Latex\texlive\2024\bin\windows\`
  - macOS: `brew install texlive`
  - Linux: `apt install texlive texlive-latex-extra dvipng`
- **Python 3** with standard library (no extra packages needed)
- **Standalone LaTeX class**: usually included with TeX Live (`texlive-latex-extra`)

## Quick Check

```bash
which latex dvipng    # Both must be found
kpsewhich standalone.cls  # Must return a path
```

## Workflow

### Step 1: Prepare HTML with LaTeX formulas

Keep `$...$` (inline) and `$$...$$` (display) delimiters in the HTML. The render script finds and replaces them:

```html
<p>In typical config (context length $L_c = 512$), the Encoder consumes 97.66% FLOPs.</p>

$$K_l = \text{RMSNorm}(W_l^K \cdot C_{idx}), \quad V_l = \text{RMSNorm}(W_l^V \cdot C_{idx})$$
```

### Step 2: Run formula rendering

```bash
python render_formulas.py --input article.html --output article_rendered.html --formulas-dir formulas/
```

This script:
1. Extracts all `$...$` and `$$...$$` formulas from the HTML
2. Creates individual `.tex` files for each unique formula
3. Compiles each with `latex` → DVI
4. Converts DVI to PNG with `dvipng` (150 DPI, transparent background)
5. Replaces formula delimiters with `<img>` tags pointing to local PNGs

### Step 3: Publish normally

The rendered HTML now references local PNG files. Use `wechat-api.ts` as usual — it will upload the formula PNGs alongside other images:

```bash
npx tsx scripts/wechat-api.ts article_rendered.html --title "..." --cover cover.png
```

## How It Works

```
LaTeX formula ($...$ or $$...$)
  → standalone .tex file
    → latex → .dvi
      → dvipng → .png (transparent background, 150 DPI)
        → <img src="formulas/formula_xxx.png">
```

### Supported LaTeX

The `standalone` class with `amsmath`, `amssymb`, `amsfonts` packages supports:

| Feature | Example |
|---------|---------|
| Subscripts/superscripts | `x_i^2` |
| Fractions | `\frac{a}{b}` |
| Sums, products, integrals | `\sum_{i=1}^n` |
| Greek letters | `\alpha, \beta, \pi_\theta` |
| Calligraphic | `\mathcal{L}, \mathcal{H}` |
| Text in math | `\text{RMSNorm}` |
| Cases (piecewise) | `\begin{cases} ... \end{cases}` |
| Floor/ceil | `\lfloor x \rfloor, \lceil x \rceil` |
| Bold/symbols | `\mathbf{x}, \cdot, \quad` |

### Limitations

- `\begin{align}`, `\begin{equation}` etc. are not needed — `standalone` already centers display formulas
- TikZ/PGF plots are NOT supported by this pipeline (use separate rendering for diagrams)
- `\includegraphics` won't work (no external files in formula context)

## Script Reference

The render script lives at `scripts/render-formulas.py` in this skill directory.

```
Usage:
  python render-formulas.py --input <html_file> [--output <html_file>] [--formulas-dir <dir>]

Options:
  --input         Input HTML file with $...$ / $$...$$ formulas
  --output        Output HTML file (default: overwrite input)
  --formulas-dir  Directory for PNG output (default: ./formulas)
  --dpi           DPI for rendered PNG (default: 150)
  --work-dir      Temporary directory for .tex/.dvi files (default: ./_latex_work)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `latex` not found | Install TeX Live and add `bin/windows` (or equivalent) to PATH |
| `standalone.cls` not found | `tlmgr install standalone` or install `texlive-latex-extra` |
| `dvipng` not found | `tlmgr install dvipng` |
| Formula renders but looks wrong | Check for unsupported commands; try simplifying the LaTeX |
| Transparent background looks bad in dark mode | Add `-bg White` to dvipng args in the script |
| PNG too small/blurry | Increase `--dpi` (default 150, try 200 or 300) |
