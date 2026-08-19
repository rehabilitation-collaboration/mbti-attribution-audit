"""Lay out the contested codings for the author to rule on.

§9 gives every disagreement, and anything either coder flagged as uncertain, to
the author. An agent may propose a ruling and does not make one, so this script
does no arbitration: it puts the two readings side by side with the verbatim
each rests on, and leaves the decision empty.

Only contested items are shown. A work with one split flag does not need its
other seventeen codes re-read, and printing them would bury the question being
asked. The uncertain notes are shown in full, because a coder that says the
protocol does not decide a case is describing a gap in the protocol, and that is
worth more to the author than the code it produced.

Codings come from two passes — the gate pass holds E, instrument and
`text_is_abstract`; the flag pass holds R, C, narrow C and `states_distinction`
— so each item is read from whichever pass produced it.

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
    "r4": "R4 psychometrics — the PLAN's secondary measure (§5)",
    "r5": "R5 data source (§5)",
    "r6": "R6 mention only (§5)",
    "r7": "R7 object of study (§5)",
    "c0": "C0 no conflation (§6)",
    "c1": "C1 identity (§6)",
    "c2": "C2 provenance (§6)",
    "c3": "C3 authority (§6)",
    "narrow_c1": "C1 identity under the NARROW reading — S7 only (§6, §11)",
    "narrow_c2": "C2 provenance under the NARROW reading — S7 only (§6, §11)",
    "narrow_c3": "C3 authority under the NARROW reading — S7 only (§6, §11)",
    "states_distinction": "the work also states the distinction (§6)",
}

HOW_TO = """## How to record a ruling

🔴 **Do not type rulings into `data/classification.csv`.** That file is rebuilt
from the codings every time `src/build_classification.py` runs, so anything
written into it is erased by the next run.

Write one row per ruling in **`data/adjudications.csv`**:

```
key,item,ruling,reasoning
10_3390_ijerph17062125,c2,false,names the MBTI's standing and not the vendor's lineage
```

- `item` — the name in bold under each work below: `e`, `instrument`,
  `instrument_sublabel`, `r1`-`r7`, `c0`-`c3`, `narrow_c1`-`narrow_c3`,
  `states_distinction`, `text_is_abstract`.
- `ruling` — `true`/`false` for a flag, the code itself for E and instrument.
- A work flagged uncertain with no split code needs a row only if you are
  changing something; otherwise the flag is discharged by your having read it.

Then re-run `python3 src/build_classification.py` and
`python3 src/score_agreement.py`.

Two kinds of entry appear below. A **split code** is a straight disagreement,
with each coder's verbatim beneath it. An **uncertain flag** is a coder
reporting that the protocol does not decide the case — worth reading even where
the codes match, because it points at a gap rather than at an error.

⚠️ The flag names collide with the coder names. `c1`/`c2` as a *coder* means
sonnet/opus; `c1`/`c2` as an *item* means conflation of identity/provenance
(§6). The headings spell out which is meant.

---
"""


def coder_value(gate: dict, flag: dict, item: str):
    """What this coder said about one contested item, with its quote."""
    if item == "e":
        return gate["e_code"], gate["e_quote"]
    if item == "instrument":
        return gate["instrument"], gate["instrument_quote"]
    if item == "instrument_sublabel":
        return gate["instrument_sublabel"], gate["instrument_quote"]
    if item == "text_is_abstract":
        return gate["text_is_abstract"], gate["text_is_abstract_evidence"]
    if item == "states_distinction":
        return flag["states_distinction"], flag["states_distinction_quote"]
    if item.startswith("narrow_"):
        bare = item.removeprefix("narrow_")
        return flag["conflation_narrow"][bare], flag["conflation_quotes"].get(bare)
    if item.startswith("r"):
        return flag["roles"][item], flag["role_quotes"].get(item)
    return flag["conflation"][item], flag["conflation_quotes"].get(item)


def show(value) -> str:
    if value is None or value == "":
        return "(no quote — the flag was not set)"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def render(index: int, row: pd.Series, gate: dict[str, dict], flag: dict[str, dict]) -> str:
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
            v1, q1 = coder_value(gate["c1"], flag["c1"], item)
            v2, q2 = coder_value(gate["c2"], flag["c2"], item)
            lines += [
                f"**`{item}`** — {LABELS.get(item, item)}",
                "",
                f"c1 said `{v1}`, c2 said `{v2}`",
                "",
                f"- c1: {show(q1)}",
                f"- c2: {show(q2)}",
                "",
            ]
    else:
        lines += ["### No split codes — both coders agreed on every item", ""]

    for who in uncertain:
        coder, _, which = who.partition(":")
        doc = (gate if which == "gate" else flag)[coder]
        note = doc["uncertain_note"] or "(flagged uncertain with no note)"
        lines += [f"### {coder} flagged this uncertain in the {which} pass", "", note, ""]

    free = [
        f"- {c}/{which}: {doc['free_text']}"
        for c in ("c1", "c2")
        for which, doc in (("gate", gate[c]), ("flags", flag[c]))
        if doc["free_text"]
    ]
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
        HOW_TO,
        "",
    ]

    body = []
    for i, (_, row) in enumerate(pending.iterrows(), start=1):
        gate = {
            c: json.loads((RAW / c / f"{row['key']}.json").read_text(encoding="utf-8"))
            for c in ("c1", "c2")
        }
        flag = {
            c: json.loads((RAW / f"flags_{c}" / f"{row['key']}.json").read_text(encoding="utf-8"))
            for c in ("c1", "c2")
        }
        body.append(render(i, row, gate, flag))

    OUT.write_text("\n".join(header) + "\n".join(body), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} — {len(pending)} works, {OUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
