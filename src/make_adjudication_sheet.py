"""Lay out the contested codings for the author to rule on.

§9 gives every disagreement, and anything either coder flagged as uncertain, to
the author. An agent may propose a ruling and does not make one, so this script
does no arbitration: it puts the two readings side by side with the verbatim
each rests on, and leaves the decision empty.

Only contested items are shown. A work with one split flag does not need its
other twelve codes re-read, and printing them would bury the question being
asked. The uncertain notes are shown in full, because a coder that says the
protocol does not decide a case is describing a gap in the protocol, and that is
worth more to the author than the code it produced.

Output
    coding_raw/adjudication.md   git-ignored: the coders' raw notes quote more
                                 third-party text than the published table does
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "coding_raw"
CLASSIFICATION = ROOT / "data" / "classification.csv"
OUT = RAW / "adjudication.md"

LABELS = {
    "e": "E gate (§2)",
    "instrument": "instrument (a)/(b)/(c) (§3)",
    "instrument_sublabel": "(c) sub-label (§3.4)",
    "text_is_abstract": "retrieved text is an abstract (§3.6)",
    "r1": "R1 instrument (§5)",
    "r2": "R2 theory (§5)",
    "r3": "R3 norms (§5)",
    "r4": "R4 psychometrics (§5)",
    "r5": "R5 data source (§5)",
    "r6": "R6 mention only (§5)",
    "c0": "C0 no conflation (§6)",
    "c1": "C1 identity (§6)",
    "c2": "C2 provenance (§6)",
    "c3": "C3 authority (§6)",
}


def coder_value(doc: dict, item: str):
    """What this coder said about one contested item, with its quote."""
    if item == "e":
        return doc["e_code"], doc["e_quote"]
    if item == "instrument":
        return doc["instrument"], doc["instrument_quote"]
    if item == "instrument_sublabel":
        return doc["instrument_sublabel"], doc["instrument_quote"]
    if item == "text_is_abstract":
        return doc["text_is_abstract"], doc["text_is_abstract_evidence"]
    if item.startswith("r"):
        return doc["roles"][item], doc["role_quotes"].get(item)
    return doc["conflation"][item], doc["conflation_quotes"].get(item)


def render(index: int, row: pd.Series, docs: dict[str, dict]) -> str:
    contested = [c for c in str(row["contested"]).split(",") if c] if pd.notna(row["contested"]) else []
    uncertain = str(row["uncertain_by"]).split(",") if pd.notna(row["uncertain_by"]) else []
    uncertain = [u for u in uncertain if u]

    lines = [
        f"## {index}. `{row['key']}`",
        "",
        f"**{row['title']}**  ",
        f"{row['doi']} — venue class `{row['work_venue_class']}`",
        "",
    ]

    if contested:
        lines += ["### Split codes", ""]
        for item in contested:
            v1, q1 = coder_value(docs["c1"], item)
            v2, q2 = coder_value(docs["c2"], item)
            lines += [
                f"**{LABELS.get(item, item)}** — c1 said `{v1}`, c2 said `{v2}`",
                "",
                f"- c1: {q1 or '(no quote — the flag was not set)'}",
                f"- c2: {q2 or '(no quote — the flag was not set)'}",
                "",
            ]
    else:
        lines += ["### No split codes — both coders agreed on every item", ""]

    for coder in uncertain:
        note = docs[coder]["uncertain_note"] or "(flagged uncertain with no note)"
        lines += [f"### {coder} flagged this uncertain", "", note, ""]

    free = [f"- {c}: {docs[c]['free_text']}" for c in ("c1", "c2") if docs[c]["free_text"]]
    if free:
        lines += ["### Coders' notes", "", *free, ""]

    lines += ["**Ruling:** _______", "", "---", ""]
    return "\n".join(lines)


def main() -> None:
    frame = pd.read_csv(CLASSIFICATION)
    pending = frame[frame["needs_adjudication"]]

    header = [
        "# Adjudication sheet",
        "",
        f"{len(pending)} of {len(frame)} works need a ruling. Only the contested items are",
        "shown; everything else the two coders agreed on and is already final in",
        "`data/classification.csv`.",
        "",
        "Two kinds of entry appear. A **split code** is a straight disagreement, with each",
        "coder's verbatim beneath it. An **uncertain flag** is a coder reporting that the",
        "protocol does not decide the case — those are worth reading even where the codes",
        "happen to match, because they point at gaps rather than at errors.",
        "",
        "⚠️ The flag names collide with the coder names. `c1`/`c2` as a *coder* means",
        "sonnet/opus; `C1`/`C2` as a *code* means conflation of identity/provenance (§6).",
        "The headings below spell out which is meant.",
        "",
        "---",
        "",
    ]

    body = []
    for i, (_, row) in enumerate(pending.iterrows(), start=1):
        docs = {
            c: json.loads((RAW / c / f"{row['key']}.json").read_text(encoding="utf-8"))
            for c in ("c1", "c2")
        }
        body.append(render(i, row, docs))

    OUT.write_text("\n".join(header) + "\n".join(body), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} — {len(pending)} works, {OUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
