"""Fill data/coder_brief.md in for every work-coder pair that still needs coding.

The brief is one document with bracketed fields; a coder run needs it with the
fields filled and nothing else in front of it. Writing the filled briefs to disk
keeps the instruction identical across runs — the wording a coder sees does not
depend on who launched it or on what was typed that time — and lets the harness
that starts a run carry a path rather than a paragraph.

Only pairs with no output yet are written, so re-running this after a coding
round leaves finished work alone. A run whose coding was deliberately discarded
is picked up again by that same rule.

Outputs
    coding_raw/assignments/<coder>/<key>.md   git-ignored, regenerable
    stdout                                    the launch list
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
BRIEF = ROOT / "data" / "coder_brief.md"
LOG = ROOT / "data" / "fulltext_log.csv"
RAW = ROOT / "coding_raw"
CODERS = ("c1", "c2")

SEPARATOR = "\n---\n"


def brief_body() -> str:
    """The instruction itself, without the preamble explaining why it exists."""
    text = BRIEF.read_text(encoding="utf-8")
    _, _, body = text.partition(SEPARATOR)
    if not body.strip():
        raise ValueError("coder_brief.md has no instruction section after the separator")
    return body.strip()


def fill(body: str, coder: str, work: pd.Series) -> str:
    filled = (
        body.replace("{CODER}", coder)
        .replace("{KEY}", str(work.name))
        .replace("{DOI}", str(work["doi"]))
        .replace("{TITLE}", str(work["title"]))
        .replace("{VENUE}", str(work["work_venue_class"]))
    )
    header = (
        f"Every relative path below is relative to `{ROOT}`.\n"
        f"Write your JSON to `{RAW / coder / f'{work.name}.json'}`.\n\n"
    )
    return header + filled + "\n"


def main() -> None:
    body = brief_body()
    log = pd.read_csv(LOG).set_index("key")
    works = log[log["status"] == "ok"]

    pending: list[tuple[str, str]] = []
    for coder in CODERS:
        (RAW / "assignments" / coder).mkdir(parents=True, exist_ok=True)
        for key, work in works.iterrows():
            if (RAW / coder / f"{key}.json").exists():
                continue
            path = RAW / "assignments" / coder / f"{key}.md"
            path.write_text(fill(body, coder, work), encoding="utf-8")
            pending.append((coder, key))

    done = len(works) * len(CODERS) - len(pending)
    print(f"{done} of {len(works) * len(CODERS)} codings already on disk")
    print(f"{len(pending)} assignments written under {(RAW / 'assignments').relative_to(ROOT)}\n")
    for coder, key in pending:
        print(f"{coder} {key}")


if __name__ == "__main__":
    main()
