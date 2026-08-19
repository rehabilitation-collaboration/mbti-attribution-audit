"""Fill a coder brief in for every work-coder pair that still needs coding.

The brief is one document with bracketed fields; a coder run needs it with the
fields filled and nothing else in front of it. Writing the filled briefs to disk
keeps the instruction identical across runs — the wording a coder sees does not
depend on who launched it or on what was typed that time — and lets the harness
that starts a run carry a path rather than a paragraph.

Only pairs with no output yet are written, so re-running this after a coding
round leaves finished work alone. A run whose coding was deliberately discarded
is picked up again by that same rule.

Two passes exist. The default fills `coder_brief.md`, which codes a work on all
four steps. `--flags` fills `coder_brief_flags.md`, which re-codes the R and C
flags alone against the rules amended in §12; its output goes to a separate
directory so that the first pass's codings are not overwritten by a pass that
does not produce them.

Usage
    python src/make_assignments.py [--flags]

Outputs
    coding_raw/assignments[_flags]/<coder>/<key>.md   git-ignored, regenerable
    stdout                                            the launch list
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "data" / "fulltext_log.csv"
RAW = ROOT / "coding_raw"
CODERS = ("c1", "c2")

PASSES = {
    "full": {
        "brief": ROOT / "data" / "coder_brief.md",
        "assignments": RAW / "assignments",
        "output": lambda coder: RAW / coder,
    },
    "flags": {
        "brief": ROOT / "data" / "coder_brief_flags.md",
        "assignments": RAW / "assignments_flags",
        "output": lambda coder: RAW / f"flags_{coder}",
    },
}

SEPARATOR = "\n---\n"


def brief_body(brief: Path) -> str:
    """The instruction itself, without the preamble explaining why it exists."""
    text = brief.read_text(encoding="utf-8")
    _, _, body = text.partition(SEPARATOR)
    if not body.strip():
        raise ValueError(f"{brief.name} has no instruction section after the separator")
    return body.strip()


def fill(body: str, coder: str, work: pd.Series, out_dir: Path) -> str:
    filled = (
        body.replace("{CODER}", coder)
        .replace("{KEY}", str(work.name))
        .replace("{DOI}", str(work["doi"]))
        .replace("{TITLE}", str(work["title"]))
        .replace("{VENUE}", str(work["work_venue_class"]))
    )
    header = (
        f"Every relative path below is relative to `{ROOT}`.\n"
        f"Write your JSON to `{out_dir / f'{work.name}.json'}`.\n\n"
    )
    return header + filled + "\n"


def main() -> None:
    which = "flags" if "--flags" in sys.argv else "full"
    spec = PASSES[which]
    body = brief_body(spec["brief"])
    log = pd.read_csv(LOG).set_index("key")
    works = log[log["status"] == "ok"]

    pending: list[tuple[str, str]] = []
    for coder in CODERS:
        out_dir = spec["output"](coder)
        out_dir.mkdir(parents=True, exist_ok=True)
        (spec["assignments"] / coder).mkdir(parents=True, exist_ok=True)
        for key, work in works.iterrows():
            if (out_dir / f"{key}.json").exists():
                continue
            path = spec["assignments"] / coder / f"{key}.md"
            path.write_text(fill(body, coder, work, out_dir), encoding="utf-8")
            pending.append((coder, key))

    done = len(works) * len(CODERS) - len(pending)
    print(f"pass: {which} ({spec['brief'].name})")
    print(f"{done} of {len(works) * len(CODERS)} codings already on disk")
    print(f"{len(pending)} assignments written under {spec['assignments'].relative_to(ROOT)}\n")
    for coder, key in pending:
        print(f"{coder} {key}")


if __name__ == "__main__":
    main()
