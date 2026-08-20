"""Lay the proposers' rulings out for the author, whole.

§9 reserves the ruling for the author, so what this sheet has to carry is the
proposer's evidence rather than its verdict: the located verbatim, the argument
from the protocol, and — where the proposer reports that the protocol does not
decide the item — the gap itself.

The first version of this sheet was assembled by hand and cut the quote at 600
characters, the argument at 900 and the per-work notes at 500, with no mark
where the cut fell: 17 of 31 quotes, 14 of 31 arguments and 17 of 18 notes ended
mid-sentence. One of the two proposals that say both coders are wrong lost the
whole of its enumeration of the sub-labels it had considered and rejected, which
was the entire ground for proposing neither. A severed argument that does not
say it has been severed is worse than a short one, because the author cannot
tell it from a finished one. So this script writes the proposals out in full and
then checks that it did: every string it was handed is looked for, verbatim, in
what it wrote, and a miss is an error rather than a shorter file.

Coder values are not read from the proposal. They come from the pass that
settles each item, through the same `coder_value` the adjudication sheet uses —
routing an item to the wrong pass is the failure that file has already had
twice, and there is no reason to write a second copy of it here.

Output
    coding_raw/proposed-rulings.md   git-ignored: the proposals quote the same
                                     third-party text the raw codings do
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from make_adjudication_sheet import LABELS, coder_value

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "coding_raw"
CLASSIFICATION = ROOT / "data" / "classification.csv"
PROPOSALS = RAW / "proposals"
OUT = RAW / "proposed-rulings.md"

HEADER = """# Proposed rulings — the works with a split code

One agent per work read the full text and both codings under the amended
protocol and proposed a ruling. **§9 reserves the ruling for the author**: these
are advice, and `neither` means the proposer thinks both coders are wrong.

To accept a row, copy it into `data/adjudications.csv` as
`key,item,ruling,reasoning`. To reject one, write your own value instead, or
leave the item out and rule it from `coding_raw/adjudication.md`.

🔴 **Where a work carries a `protocol gap` note, the proposer is saying the
protocol does not decide the item and its value is a reading, not a derivation.**
Those are the rows worth your attention first.

Quotes, arguments and notes are printed in full. Nothing on this sheet is
abridged, so an argument that stops has ended.
"""


def read_proposal(key: str) -> dict:
    path = PROPOSALS / f"{key}.json"
    if not path.exists():
        raise SystemExit(f"no proposal for {key}: run the proposers first")
    return json.loads(path.read_text(encoding="utf-8"))


def render(row: pd.Series, proposal: dict, coders: dict[str, dict[str, dict]]) -> str:
    lines = [
        f"## `{row['key']}`",
        "",
        f"**{row['title']}**  ",
        f"{row['doi']} — `{row['work_venue_class']}`",
        "",
    ]

    if proposal.get("protocol_gap"):
        lines += [f"🔴 **protocol gap**: {proposal['protocol_gap']}", ""]

    for ruling in proposal["rulings"]:
        item = ruling["item"]
        v1, _ = coder_value(coders["c1"]["gate"], coders["c1"]["flags"], coders["c1"]["conf"], item)
        v2, _ = coder_value(coders["c2"]["gate"], coders["c2"]["flags"], coders["c2"]["conf"], item)
        # `matches` names a coder, and the two coder names collide with the C
        # flag names, so it is spelt out rather than printed as `c1`.
        matches = ruling["matches"]
        whose = "neither coder" if matches == "neither" else f"coder {matches}"
        lines += [
            f"### `{item}` — {LABELS.get(item, item)}",
            "",
            f"c1 said `{v1}`, c2 said `{v2}`",
            "",
            f"**proposed `{ruling['proposed']}`** (matches **{whose}**, "
            f"confidence {ruling['confidence']})",
            "",
            f"- quote: {ruling['quote']}",
            f"- why: {ruling['reasoning']}",
            "",
        ]

    if proposal.get("notes"):
        lines += [f"_notes_: {proposal['notes']}", ""]

    lines += ["---", ""]
    return "\n".join(lines)


def check_nothing_was_cut(text: str, proposals: list[dict]) -> int:
    """Fail rather than publish an argument that stops without ending.

    Every string the proposers wrote is looked for verbatim. The check is worth
    having because the failure it catches is silent by construction: a truncated
    sheet is a well-formed sheet, and the reader has no way to know.
    """
    checked = 0
    for proposal in proposals:
        fields = [("notes", proposal.get("notes")), ("protocol_gap", proposal.get("protocol_gap"))]
        for ruling in proposal["rulings"]:
            fields += [
                (f"{ruling['item']} quote", ruling["quote"]),
                (f"{ruling['item']} reasoning", ruling["reasoning"]),
            ]
        for name, value in fields:
            if not value:
                continue
            checked += 1
            if value not in text:
                raise SystemExit(
                    f"{proposal['key']}: {name} did not survive into the sheet whole "
                    f"({len(value)} characters). Nothing may be abridged here."
                )
    return checked


def main() -> None:
    frame = pd.read_csv(CLASSIFICATION)
    split = frame[frame["contested"].notna() & (frame["contested"] != "")]

    body, proposals = [], []
    for _, row in split.sort_values("key").iterrows():
        key = row["key"]
        proposal = read_proposal(key)
        coders = {
            c: {
                "gate": json.loads((RAW / c / f"{key}.json").read_text(encoding="utf-8")),
                "flags": json.loads(
                    (RAW / f"flags_{c}" / f"{key}.json").read_text(encoding="utf-8")
                ),
                "conf": json.loads(
                    (RAW / f"conflation_{c}" / f"{key}.json").read_text(encoding="utf-8")
                ),
            }
            for c in ("c1", "c2")
        }
        proposals.append(proposal)
        body.append(render(row, proposal, coders))

    text = HEADER + "\n---\n\n" + "\n".join(body)
    checked = check_nothing_was_cut(text, proposals)
    OUT.write_text(text, encoding="utf-8")

    items = sum(len(p["rulings"]) for p in proposals)
    gaps = sum(1 for p in proposals if p.get("protocol_gap"))
    print(
        f"wrote {OUT.relative_to(ROOT)} — {len(proposals)} works, {items} items, "
        f"{gaps} with a protocol gap, {checked} strings verified whole, "
        f"{OUT.stat().st_size:,} bytes"
    )


if __name__ == "__main__":
    main()
