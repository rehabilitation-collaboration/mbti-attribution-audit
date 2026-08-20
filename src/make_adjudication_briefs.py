"""Write one brief per contested work for an agent to propose a ruling on.

§9 lets an agent propose a ruling and reserves the making of one for the author.
A proposal is worth having because the author rules against the full text, and
an agent that has already gone back to the full text can put the relevant
passage in front of them; it is worth nothing if it merely counts votes.

So the brief tells the proposer to decide from the text and forbids the three
shortcuts that would make the proposal an echo: siding with a majority that does
not exist in a two-coder design, preferring a coder because of which model it
is, and preferring the reading that makes the study more interesting. It is also
told in as many words that both coders may be wrong, because a proposal that can
only pick one of two offered answers cannot report that neither is right.

Only works with a split code get a brief. Where the coders agreed and one merely
flagged the case uncertain, there is nothing to arbitrate — that is a report of
a gap in the protocol, and it goes to the author as itself.

The brief sends the proposer to all three coding passes and says which items each
one settles. Getting that wrong is the failure this file has already had twice: a
proposer sent only to the gate pass is asked about a flag its files do not
contain, and a proposer sent to the flag pass for a C item is handed a reading
the 2026-08-20 amendments replaced — worse than a missing file, because it looks
like an answer.

Outputs
    coding_raw/adjudication_briefs/<key>.md   git-ignored, regenerable
    stdout                                    the launch list
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CLASSIFICATION = ROOT / "data" / "classification.csv"
RAW = ROOT / "coding_raw"
BRIEFS = RAW / "adjudication_briefs"

LABELS = {
    "e": "the E gate code (§2)",
    "instrument": "the instrument code (a)/(b)/(c) (§3)",
    "instrument_sublabel": "the (c) sub-label (§3.4)",
    "text_is_abstract": "whether the retrieved text is a conference abstract (§3.6)",
    "r1": "flag R1, the vendor cited as the instrument administered (§5)",
    "r2": "flag R2, the vendor cited as the source of the theory (§5)",
    "r3": "flag R3, the vendor cited for norms or type frequencies (§5)",
    "r4": "flag R4, the vendor cited as evidence of reliability or validity (§5)",
    "r5": "flag R5, the vendor cited as where labels were scraped or matched (§5)",
    "r6": "flag R6, the vendor named in passing with no claim resting on it (§5)",
    "r7": "flag R7, the vendor as the object of study rather than a source (§5)",
    "c0": "flag C0, no conflation statement (§6)",
    "c1": "flag C1, conflation of identity (§6)",
    "c2": "flag C2, conflation of provenance (§6)",
    "c3": "flag C3, conflation of authority (§6)",
    "narrow_c1": "flag C1 under the narrow reading — the vendor's test only, "
    "excluding its proprietary content; reported as sensitivity arm S7 (§6, §11)",
    "narrow_c2": "flag C2 under the narrow reading — the vendor's test only, "
    "excluding its proprietary content; reported as sensitivity arm S7 (§6, §11)",
    "narrow_c3": "flag C3 under the narrow reading — the vendor's test only, "
    "excluding its proprietary content; reported as sensitivity arm S7 (§6, §11)",
    "states_distinction": "whether the work also states the distinction between "
    "the vendor's test and the MBTI (§6)",
}

TEMPLATE = """Every relative path below is relative to `{root}`.

You are proposing rulings on contested codings in a double-coding exercise. The
author makes the ruling; you propose one and give the evidence it rests on
(§9 of the protocol). Your proposal will be accepted, rejected or changed.

Read, in this order:

1. `data/coding_protocol.md` — the coding protocol. §12 lists the rules amended
   after coding began; the amendments are already written into §2, §3.4, §5, §6,
   §9 and §11, and §12 says which shape each one was written for.
2. `fulltext/{key}.txt` — the full text of the work. Read the whole file,
   including the reference list.
3. The two codings, which arrived in three passes. Each pass settles some items
   and is read only for those:
   - `coding_raw/c1/{key}.json`, `coding_raw/c2/{key}.json` — the **gate pass**:
     the E code, the instrument code and `text_is_abstract`.
   - `coding_raw/flags_c1/{key}.json`, `coding_raw/flags_c2/{key}.json` — the
     **flag pass**: the **R flags**. 🔴 This file also holds conflation codings
     made under rules the 2026-08-20 amendments replaced. **Do not read them for
     a C item.** They stay on disk as the reading they were.
   - `coding_raw/conflation_c1/{key}.json`, `coding_raw/conflation_c2/{key}.json`
     — the **conflation pass**: the **C flags, the narrow C flags and
     `states_distinction`**, coded against §6 and §11 as amended. For those items
     this pass is the coding.

The work:

- key: `{key}`
- doi: `{doi}`
- title: {title}
- work_venue_class: `{venue}`

**The contested items, and only these:**

{items}

How to decide each one:

- Decide from the full text and the protocol. Go back to the passage; do not
  arbitrate between two summaries.
- **Both coders may be wrong.** If neither reading is what the protocol
  requires, propose the third answer and say so. A proposal that can only pick
  one of the two offered is not worth having.
- Do not decide by majority — there is no majority in a two-coder design.
- Do not prefer a coder because of which model it is. c1 and c2 are two tiers of
  one model line and neither has standing over the other.
- Do not prefer the reading that makes the study's finding stronger or more
  interesting. If the conservative reading is what the text supports, propose it.
- The full text is the only evidence. No web search, no other work's text, no
  prior knowledge of this paper.
- §3.6: one retrieved file can hold several works. Only the target work's own
  section is evidence.

Where either coder flagged the case `uncertain`, read the note. If the protocol
genuinely does not decide the item, say that in `protocol_gap` rather than
forcing a code — a gap the author needs to see is more useful than a guess.

Write your result as JSON to `coding_raw/proposals/{key}.json`:

```json
{{
  "key": "{key}",
  "rulings": [
    {{
      "item": "c2",
      "proposed": true,
      "matches": "c2",
      "confidence": "high",
      "quote": "the located verbatim the ruling rests on — section name",
      "reasoning": "why the protocol requires this, in two or three sentences"
    }}
  ],
  "protocol_gap": null,
  "notes": null
}}
```

Field notes:

- one entry in `rulings` per contested item, using the item names exactly as
  listed above.
- `proposed` — the value you propose: `"E1"`-`"E4"`, `"a"`/`"b"`/`"c"`, a
  sub-label string, or `true`/`false` for a flag.
- `matches` — `"c1"`, `"c2"`, or `"neither"` when you propose a third answer.
- `confidence` — `"high"`, `"medium"` or `"low"`. Use `"low"` honestly; a
  low-confidence proposal tells the author where to spend their attention.
- `quote` — verbatim from the text, exactly as written, with the section. Quote
  the original language and gloss it in English afterwards if not in English.
- `protocol_gap` — a sentence naming what the protocol does not decide, or null.
- `notes` — anything the fields cannot hold, or null.

Create no file other than that JSON. Your final message must be exactly:
`proposed {key}`
"""


def main() -> None:
    frame = pd.read_csv(CLASSIFICATION)
    contested = frame[
        frame["contested"].notna() & (frame["contested"].astype(str).str.strip() != "")
    ]
    BRIEFS.mkdir(parents=True, exist_ok=True)
    (RAW / "proposals").mkdir(parents=True, exist_ok=True)

    written = []
    for _, row in contested.iterrows():
        key = row["key"]
        if (RAW / "proposals" / f"{key}.json").exists():
            continue
        items = "\n".join(
            f"- **{item}** — {LABELS.get(item, item)}. c1 proposed one value, c2 another; "
            "both are in the JSON files."
            for item in str(row["contested"]).split(",")
            if item
        )
        (BRIEFS / f"{key}.md").write_text(
            TEMPLATE.format(
                root=ROOT,
                key=key,
                doi=row["doi"],
                title=row["title"],
                venue=row["work_venue_class"],
                items=items,
            ),
            encoding="utf-8",
        )
        written.append(key)

    print(f"{len(contested)} works have a split code; {len(written)} briefs written\n")
    for key in written:
        print(key)


if __name__ == "__main__":
    main()
