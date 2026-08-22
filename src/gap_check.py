"""Run the three prior-work searches the Introduction's novelty claim rests on.

These counts were originally taken on 2026-08-19 and quoted in prose without
being logged anywhere — the one place in the study where a figure was not
traceable to a file. Review caught it, and re-running the queries did not
reproduce the quoted values: two of the three had moved *down*, which retrieval
drift does not explain, so the original filter strings can no longer be
recovered. They are therefore re-measured here, with the exact filters written
down, so that the claim rests on something a reader can re-run.

This is not the corpus query. `build_corpus.py` writes `data/query_log.json` and
re-measures the window and word-form decisions every run; these searches feed no
part of the analysis and are context for the Introduction alone, so they are kept
in their own file rather than folded into a log that another script owns.

The counts move with the databases, as the corpus frames do. Every figure this
writes carries the date it was taken, and the manuscript quotes it with that date.

Outputs
    data/gap_check.json  the three searches, their filters, and their counts
    stdout               the same
"""

from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "gap_check.json"
MAILTO = "rehabilitation.collaboration@gmail.com"
WINDOW = "from_publication_date:2015-01-01"

SEARCHES = {
    "mbti_x_misattribution": {
        "asks": "Has anyone treated the misattribution of the MBTI as a subject?",
        "filter": 'title_and_abstract.search:(MBTI OR "Myers-Briggs" OR "Myers Briggs") '
                  'AND (misattribution OR conflation OR misidentification)',
    },
    "vendor_word_forms": {
        "asks": "How much work names the vendor's test in its title or abstract?",
        "filter": 'title_and_abstract.search:"16Personalities" OR "16 Personalities" '
                  'OR "NERIS Type Explorer"',
    },
    "citation_accuracy_family": {
        "asks": "How established is the family of questions this one belongs to?",
        "filter": 'title_and_abstract.search:"citation accuracy" OR "quotation error" '
                  'OR "citation integrity"',
    },
}


def count(filter_expr: str) -> int:
    url = ("https://api.openalex.org/works?mailto=" + MAILTO + "&filter="
           + urllib.parse.quote(filter_expr, safe='=,:|"()'))
    with urllib.request.urlopen(url, timeout=40) as response:
        return json.load(response)["meta"]["count"]


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("usage: gap_check.py YYYY-MM-DD   (the date of this run, recorded with the counts)")
    retrieved_on = sys.argv[1]

    results = {"source": "OpenAlex", "retrieved_on": retrieved_on, "window": WINDOW, "searches": {}}
    for name, spec in SEARCHES.items():
        unwindowed = count(spec["filter"])
        windowed = count(f"{spec['filter']},{WINDOW}")
        results["searches"][name] = {
            "asks": spec["asks"],
            "filter": spec["filter"],
            "count_all_years": unwindowed,
            "count_from_2015": windowed,
        }
        print(f"  {name}\n    {spec['filter']}\n    all years {unwindowed}  ·  from 2015 {windowed}")

    results["note"] = (
        "These searches are context for the Introduction's claim that the specific question "
        "is unasked. They feed no measure. Counts move with the database, so each is quoted "
        "in the manuscript with the retrieval date above."
    )
    OUT.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
