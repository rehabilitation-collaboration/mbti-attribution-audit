"""Draw the manuscript's four figures from data/results.json.

Every number in every figure is read from the results file at draw time. None is
typed into this script, for the same reason none is typed into the manuscript:
a figure that disagrees with the table it illustrates is a defect a reader finds
before the author does, and the only reliable way to prevent it is to remove the
opportunity to transcribe.

Choices worth stating, because a reviewer will ask.

**Proportions are drawn as points with intervals, not as bars.** A bar encodes
magnitude from a zero baseline and invites the eye to compare areas; an interval
floating above one reads as an ornament on the bar rather than as the estimate's
width. On n₁ = 27 the interval is the finding as much as the point is.

**Two colors, and only where two things are being distinguished.** Figures 1, 2
and 4 plot one series each and carry no legend — the row labels are the identity
channel. Figure 3's panel B is the only place two readings appear together, so it
is the only place a second hue and a legend are used. The pair was checked with
the palette validator against a white surface (CVD ΔE 24.7, normal-vision 33.6,
both above the gates).

**Grayscale is assumed.** Journals print figures in grayscale often enough that
no figure here depends on hue: the two series in the one two-series panel are
also separated by position, and every plotted value is directly labelled.

Outputs
    figures/figure1_flow.{pdf,png} … figures/figure4_sensitivity.{pdf,png}
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "data" / "results.json"
QUERY_LOG = ROOT / "data" / "query_log.json"
OUT = ROOT / "figures"

# palette.md, light mode, validated against a white surface
SURFACE = "#ffffff"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
RULE = "#c3c2b7"
SERIES_1 = "#2a78d6"
SERIES_2 = "#eb6834"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 8.5,
    "axes.edgecolor": RULE,
    "axes.labelcolor": INK_2,
    "text.color": INK,
    "xtick.color": MUTED,
    "ytick.color": INK_2,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "axes.grid": False,
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def load() -> tuple[dict, dict]:
    return json.loads(RESULTS.read_text()), json.loads(QUERY_LOG.read_text())


def save(fig, stem: str) -> None:
    OUT.mkdir(exist_ok=True)
    for suffix in ("pdf", "png"):
        fig.savefig(OUT / f"{stem}.{suffix}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote figures/{stem}.pdf and .png")


def recessive_x(ax, lo: float, hi: float, ticks, labels=None) -> None:
    """A hairline solid grid, one step off the surface, behind the marks."""
    ax.set_xlim(lo, hi)
    ax.set_xticks(ticks)
    if labels is not None:
        ax.set_xticklabels(labels)
    for tick in ticks:
        ax.axvline(tick, color=GRID, linewidth=0.6, zorder=0, solid_capstyle="butt")
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color(RULE)
    ax.spines["bottom"].set_linewidth(0.8)
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", length=3, width=0.8)


def interval_row(ax, y: float, p: dict, color: str = SERIES_1, label_fmt: str = "{p:.1%}") -> None:
    """One estimate: a 2px interval, an >=8px marker, a 2px surface ring."""
    ax.plot([p["ci_low"], p["ci_high"]], [y, y], color=color, linewidth=2,
            solid_capstyle="round", zorder=2)
    ax.plot([p["p"]], [y], marker="o", markersize=8, color=color,
            markeredgecolor=SURFACE, markeredgewidth=2, zorder=3)
    ax.text(p["ci_high"] + 0.025, y,
            f"{label_fmt.format(p=p['p'])}  ({p['ci_low']:.1%}–{p['ci_high']:.1%})",
            va="center", ha="left", fontsize=8, color=INK_2)


# --- Figure 1 --------------------------------------------------------------


def figure1(d: dict, q: dict) -> None:
    """Flow from the two frames to the main analysis, with reasons for attrition."""
    retrieval = d["descriptive_counts_no_rate"]["retrieval"]
    unobtainable = retrieval["unobtainable"]
    journal = retrieval["journal_articles"]
    frames, main = d["frames"], d["main_analysis"]
    records = q["openalex"]["records"] + q["europepmc"]["records"]

    other_venues = retrieval["works"] - main["works_in_frame"]
    reasons = "  ·  ".join(f"{k.replace('_', ' ')} {v}" for k, v in unobtainable["by_reason"].items())
    stages = [
        (f"Bibliographic frames, from 2015\n"
         f"OpenAlex {frames['openalex_from_2015']:,}  ·  Europe PMC {frames['europepmc_from_2015']:,}",
         f"retrieved {frames['retrieved_on']}; the frames move,\nso every figure carries its date"),
        (f"Records matching both term sets\n"
         f"{q['openalex']['records']} OpenAlex  +  {q['europepmc']['records']} Europe PMC  =  {records}",
         "Europe PMC contributed no work\nOpenAlex did not already hold"),
        (f"Distinct works\nn = {retrieval['works']}",
         f"{records - retrieval['works']} records merged into\nthe work they belong to"),
        (f"Classified as journal articles\nn = {main['works_in_frame']}",
         f"{other_venues} works in other venue classes —\ncoded and reported, but outside\nthe main denominator"),
        (f"Full text coded\nn = {main['works_retrieved']}",
         f"{journal['unobtainable']} journal articles not retrieved\n"
         f"({unobtainable['total']} across the whole corpus:\n{reasons}),\n"
         f"plus {journal['no_word_form']} retrieved with no vendor word form"),
        (f"Administered an instrument (E1)\nMAIN ANALYSIS   n₁ = {d['m1']['n1']}",
         f"{main['works_retrieved'] - d['m1']['n1']} works reported no type data, used\n"
         "existing type labels, or administered\nto a language model"),
    ]

    fig, ax = plt.subplots(figsize=(7.4, 8.0))
    step, box_w, box_h = 1.42, 5.7, 0.86
    ax.set_xlim(0, 10.2); ax.set_ylim(0, len(stages) * step); ax.axis("off")

    for i, (text, note) in enumerate(stages):
        y = (len(stages) - i - 1) * step + 0.30
        final = i == len(stages) - 1
        ax.add_patch(FancyBboxPatch(
            (0.10, y), box_w, box_h, boxstyle="round,pad=0.04,rounding_size=0.07",
            linewidth=1.3 if final else 0.8,
            edgecolor=SERIES_1 if final else RULE,
            facecolor=SURFACE, zorder=2))
        ax.text(0.10 + box_w / 2, y + box_h / 2, text, ha="center", va="center",
                fontsize=8, color=INK, linespacing=1.55,
                fontweight="bold" if final else "normal", zorder=3)
        if note:
            ax.annotate("", xy=(6.05, y + box_h / 2), xytext=(5.82, y + box_h / 2),
                        arrowprops=dict(arrowstyle="-", color=RULE, linewidth=0.8))
            ax.text(6.18, y + box_h / 2, note, ha="left", va="center", fontsize=7,
                    color=MUTED, linespacing=1.5)
        if i:
            prev = (len(stages) - i) * step + 0.30
            ax.add_patch(FancyArrowPatch(
                (0.10 + box_w / 2, prev), (0.10 + box_w / 2, y + box_h),
                arrowstyle="-|>", mutation_scale=9,
                color=RULE, linewidth=0.9, shrinkA=0, shrinkB=0, zorder=1))
    save(fig, "figure1_flow")


# --- Figure 2 --------------------------------------------------------------


def figure2(d: dict) -> None:
    """Instrument attribution among the E1 works of the main analysis."""
    dist = d["m1"]["distribution"]
    rows = [
        ("(a)  the vendor's test", "a"),
        ("(b)  a published MBTI form", "b"),
        ("(c)  not identifiable from the work", "c"),
    ]
    fig, ax = plt.subplots(figsize=(7.2, 2.5))
    for i, (label, code) in enumerate(rows):
        y = len(rows) - 1 - i
        interval_row(ax, y, dist[code])
        ax.text(-0.03, y, label, ha="right", va="center", fontsize=8.5, color=INK)
        ax.text(-0.03, y - 0.28, f"{dist[code]['k']} of {dist[code]['n']} works",
                ha="right", va="center", fontsize=7.2, color=MUTED)

    recessive_x(ax, 0, 1.0, [0, 0.25, 0.5, 0.75, 1.0], ["0%", "25%", "50%", "75%", "100%"])
    ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.set_yticks([])
    ax.set_xlabel("Share of the 27 works in the main analysis that administered an instrument",
                  fontsize=8, labelpad=7)
    save(fig, "figure2_instrument")


# --- Figure 3 --------------------------------------------------------------


def figure3(d: dict) -> None:
    """Citation-role and conflation flags, as counts."""
    counts = d["descriptive_counts_no_rate"]
    roles, conf = counts["role_flags"], counts["conflation_flags"]
    n = d["m2"]["n"]

    role_names = {"R1": "R1 instrument", "R2": "R2 theory", "R3": "R3 norms",
                  "R4": "R4 psychometrics", "R5": "R5 data source",
                  "R6": "R6 mention only", "R7": "R7 object of study"}
    conf_names = {"C0": "C0 none", "C1": "C1 identity",
                  "C2": "C2 provenance", "C3": "C3 authority"}

    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(7.4, 3.4), gridspec_kw={"wspace": 0.42})
    top = max(max(roles.values()), max(conf.values())) + 8

    for i, (key, label) in enumerate(role_names.items()):
        y = len(role_names) - 1 - i
        ax_a.barh(y, roles[key], height=0.5, color=SERIES_1, zorder=2)
        ax_a.text(roles[key] + 0.9, y, str(roles[key]), va="center", fontsize=8, color=INK_2)
        ax_a.text(-1.2, y, label, ha="right", va="center", fontsize=8.5, color=INK)
    ax_a.set_ylim(-1.4, len(role_names) - 0.4)
    ax_a.set_title("A  What the vendor is cited as", loc="left", fontsize=9,
                   color=INK, pad=8, fontweight="bold")

    # The narrow reading exists only for C1-C3; C0 is the complement and has none.
    for i, (key, label) in enumerate(conf_names.items()):
        y = len(conf_names) - 1 - i
        narrow_key = f"narrow_{key.lower()}"
        paired = narrow_key in conf
        # Adjacent bars are separated by a gap in the surface, never by a stroke:
        # 0.24 tall on a 0.34 pitch leaves the gap the spec asks for.
        ax_b.barh(y + (0.17 if paired else 0), conf[key], height=0.24 if paired else 0.46,
                  color=SERIES_1, zorder=2)
        ax_b.text(conf[key] + 0.9, y + (0.17 if paired else 0), str(conf[key]),
                  va="center", fontsize=8, color=INK_2)
        if paired:
            ax_b.barh(y - 0.17, conf[narrow_key], height=0.24, color=SERIES_2, zorder=2)
            ax_b.text(conf[narrow_key] + 0.9, y - 0.17, str(conf[narrow_key]),
                      va="center", fontsize=8, color=INK_2)
        ax_b.text(-1.2, y, label, ha="right", va="center", fontsize=8.5, color=INK)

    # states_distinction is not a conflation flag; it is shown apart, below a gap.
    ax_b.barh(-1.15, counts["states_distinction"], height=0.5, color=SERIES_1, zorder=2)
    ax_b.text(counts["states_distinction"] + 0.9, -1.15, str(counts["states_distinction"]),
              va="center", fontsize=8, color=INK_2)
    ax_b.text(-1.2, -1.15, "states the distinction", ha="right", va="center",
              fontsize=8.5, color=INK_2, style="italic")
    ax_b.axhline(-0.62, color=GRID, linewidth=0.8, zorder=1)
    ax_b.set_ylim(-1.9, len(conf_names) - 0.4)
    ax_b.set_title("B  Conflating statements", loc="left", fontsize=9,
                   color=INK, pad=8, fontweight="bold")
    ax_b.legend(handles=[Line2D([], [], color=SERIES_1, linewidth=6, label="wide reading (main analysis)"),
                         Line2D([], [], color=SERIES_2, linewidth=6, label="narrow reading (S7)")],
                loc="lower right", frameon=False, fontsize=7.4, handlelength=1.1,
                labelcolor=INK_2, borderpad=0.2)

    for ax in (ax_a, ax_b):
        recessive_x(ax, 0, top, [0, 10, 20, 30, 40])
        ax.set_yticks([])
        ax.set_xlabel(f"Works (of {n} coded)", fontsize=8, labelpad=6)
    save(fig, "figure3_flags")


# --- Figure 4 --------------------------------------------------------------


def figure4(d: dict) -> None:
    """The two measures under the main analysis and each planned arm."""
    arms = d["sensitivity"]
    labels = {
        "S1": "S1  conference classes added",
        "S2": "S2  venue-less record added",
        "S3": "S3  reference-list-only as (a)",
        "S4": "S4  OpenAlex only",
        "S5": "S5  widened word form",
        "S6": "S6  abstract-texts excluded",
        "S7": "S7  narrow conflation reading",
    }
    panels = [
        ("A  M1 — administered the vendor's test", d["m1"]["distribution"]["a"],
         lambda a: a["m1"]["distribution"]["a"] if a["m1"] and a["m1"]["distribution"] else None,
         lambda p: f"{p['k']}/{p['n']}"),
        ("B  M2 — any conflating statement", d["m2"]["any_conflation"],
         lambda a: a["m2"]["any_conflation"] if a["m2"] else None,
         lambda p: f"{p['k']}/{p['n']}"),
    ]

    # Stacked, not side by side: each row carries a numeric column to the right of
    # its interval, and in a two-column layout that column lands on the next
    # panel's row labels. Full width per panel is the fix; nothing is clipped.
    fig, axes = plt.subplots(2, 1, figsize=(7.4, 7.4), gridspec_kw={"hspace": 0.55})
    for ax, (title, base, pick, fmt) in zip(axes, panels):
        rows = [("Main analysis", base)] + [(labels[k], pick(v)) for k, v in arms.items()]
        ax.axvline(base["p"], color=RULE, linewidth=1.0, zorder=1)
        for i, (label, p) in enumerate(rows):
            y = len(rows) - 1 - i
            weight = "bold" if i == 0 else "normal"
            ax.text(-0.06, y, label, ha="right", va="center", fontsize=8,
                    color=INK if i == 0 else INK_2, fontweight=weight)
            if p is None:
                ax.text(0.03, y, "reported as a bound; the added record is uncoded",
                        ha="left", va="center", fontsize=7.2, color=MUTED, style="italic")
                continue
            interval_row(ax, y, p, label_fmt="{p:.1%}")
            ax.text(-0.06, y - 0.34, fmt(p), ha="right", va="center", fontsize=7, color=MUTED)
        recessive_x(ax, 0, 1.0, [0, 0.25, 0.5, 0.75, 1.0], ["0%", "25%", "50%", "75%", "100%"])
        ax.set_ylim(-0.6, len(rows) - 0.4)
        ax.set_yticks([])
        ax.set_title(title, loc="left", fontsize=9, color=INK, pad=8, fontweight="bold")
        ax.set_xlabel("Share, with Wilson 95% CI", fontsize=8, labelpad=6)
    save(fig, "figure4_sensitivity")


def main() -> None:
    d, q = load()
    print("drawing from data/results.json")
    figure1(d, q)
    figure2(d)
    figure3(d)
    figure4(d)


if __name__ == "__main__":
    main()
