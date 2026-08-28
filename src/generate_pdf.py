"""Render manuscript.md to PDF with the four figures placed under their legends.

Adapted from the ninth paper's build. Two things differ and both would corrupt
the output if carried over unchanged:

- This manuscript writes legends as `**Figure 1.** text`, with the bold closing
  after the period rather than wrapping the title. The pattern below allows an
  empty title so the whole legend lands in the body group.
- A `## Tables` section follows the legends. The ninth paper's lookahead ended
  at `---` or end-of-file only, so the last legend would swallow every section
  after it. `\n\n## ` is therefore part of the terminator.

Tables stay where they are: they are written inline in Results, which is where
a reader needs them.

Figure map — checked against the manuscript at build time, because a stale map
prints the wrong image under the right caption and nothing else catches it.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import markdown
import weasyprint

PROJECT_DIR = Path(__file__).resolve().parent.parent
FIGURES_DIR = PROJECT_DIR / "figures"
OUT_DIR = PROJECT_DIR / "output"
MANUSCRIPT = PROJECT_DIR / "manuscript.md"

MAIN_FIGURES = {
    "Figure 1": "figure1_flow.png",
    "Figure 2": "figure2_instrument.png",
    "Figure 3": "figure3_flags.png",
    "Figure 4": "figure4_sensitivity.png",
}

CSS = """
@page {
    size: A4;
    margin: 2.5cm 2cm;
    @bottom-center { content: counter(page); font-size: 10pt; color: #666; }
}
body {
    font-family: "Times New Roman", "DejaVu Serif", Georgia, serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #111;
}
h1 { font-size: 16pt; margin-top: 0; margin-bottom: 8pt; line-height: 1.3;
     page-break-after: avoid; }
h2 { font-size: 13pt; margin-top: 20pt; margin-bottom: 6pt;
     border-bottom: 1px solid #ccc; padding-bottom: 3pt;
     page-break-after: avoid; }
/* The body sets bold lead-ins on many paragraphs ("**The substitution.**"), so an
   h3 only 0.5pt larger than body bold reads as one of them rather than as a
   heading — an external reader took "Data and code" for a run-in lead-in. The
   size gap and the space above are what separate the two. */
h3 { font-size: 12.5pt; margin-top: 20pt; margin-bottom: 5pt;
     font-style: italic;
     page-break-after: avoid; }
p { margin: 6pt 0; text-align: justify; widows: 3; orphans: 3; }
ol li, ul li { margin: 6pt 0; widows: 2; orphans: 2; }
sup { font-size: 0.75em; }
code { font-family: "DejaVu Sans Mono", Menlo, monospace; font-size: 9.5pt;
       background: #f4f4f4; padding: 0 2pt; }
table {
    border-collapse: collapse; width: 100%; margin: 10pt 0;
    font-size: 9pt;
    /* Not "avoid": a table taller than a page cannot honour it, and when it
       cannot, the caption above is stranded on the previous page. */
    page-break-inside: auto;
}
thead { display: table-header-group; }
tr { page-break-inside: avoid; }
th, td { border: 1px solid #999; padding: 3pt 5pt; text-align: left; }
th { background: #e8e8e8; font-weight: bold; }
hr { border: none; border-top: 1px solid #ccc; margin: 16pt 0; }
strong { font-weight: bold; }
em { font-style: italic; }
.figure-block {
    page-break-inside: avoid;
    page-break-before: always;
    margin: 1.5em 0;
    text-align: center;
}
.figure-block img { display: block; margin: 0 auto; max-width: 96%; max-height: 76vh; }
.figure-caption { font-size: 10pt; text-align: justify; margin-top: 0.6em; }
"""

LEGEND_PATTERN = re.compile(
    r"\*\*Figure (\d+)\.\s*(.*?)\*\*\s*(.*?)(?=\n\n\*\*Figure|\n\n---|\n\n## |\Z)",
    re.DOTALL,
)


def extract_legends(md_text: str) -> dict[str, str]:
    legends = {}
    section = re.search(r"## Figure Legends\n(.*?)(?=\n## |\Z)", md_text, re.DOTALL)
    if not section:
        sys.exit("manuscript.md has no '## Figure Legends' section")
    for m in LEGEND_PATTERN.finditer(section.group(1)):
        title = m.group(2).strip()
        body = " ".join(m.group(3).split())
        legends[f"Figure {m.group(1)}"] = f"{title} {body}".strip()
    return legends


def inline_html(text: str) -> str:
    """Render a legend's inline markdown; verbatim text would print literal `**`."""
    return re.sub(r"^<p>|</p>$", "", markdown.markdown(text).strip())


def figure_block(label: str, filename: str, caption: str) -> str:
    path = FIGURES_DIR / filename
    if not path.exists():
        sys.exit(f"missing figure: {path}")
    return (
        '<div class="figure-block">'
        f'<img src="file://{path}" alt="{label}">'
        f'<p class="figure-caption"><strong>{label}.</strong> {inline_html(caption)}</p>'
        "</div>\n"
    )


def build() -> Path:
    md_text = MANUSCRIPT.read_text(encoding="utf-8")
    legends = extract_legends(md_text)

    if set(legends) != set(MAIN_FIGURES):
        sys.exit(
            "figure map is out of sync with manuscript.md\n"
            f"  legends in manuscript: {sorted(legends)}\n"
            f"  files in MAIN_FIGURES: {sorted(MAIN_FIGURES)}"
        )
    for label, caption in legends.items():
        if len(caption) < 40:
            sys.exit(f"{label} legend came out suspiciously short: {caption!r}")

    # The legends are rebuilt below with their images attached.
    # `\Z` matters: when `## Tables` was removed on 2026-08-28 this pattern stopped
    # matching, the legends section stayed in the body, and every legend printed twice —
    # once in the body and once under its figure. `extract_legends` above already had it.
    md_text = re.sub(r"## Figure Legends\n.*?(?=\n## |\Z)", "", md_text, flags=re.DOTALL)
    # Pandoc-style superscripts for the affiliation marker.
    md_text = re.sub(r"\^([^^]+?)\^", r"<sup>\1</sup>", md_text)

    body = markdown.markdown(md_text, extensions=["tables", "smarty"])
    figures = "".join(figure_block(k, v, legends[k]) for k, v in MAIN_FIGURES.items())

    html = ('<!DOCTYPE html><html><head><meta charset="utf-8">'
            f"<style>{CSS}</style></head><body>{body}{figures}</body></html>")

    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / "manuscript.pdf"
    weasyprint.HTML(string=html, base_url=str(PROJECT_DIR)).write_pdf(str(out))
    return out


if __name__ == "__main__":
    path = build()
    print(f"[OK] {path} ({path.stat().st_size / 1024:.0f} KB)")
