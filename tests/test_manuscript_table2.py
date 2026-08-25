"""Table 2 is transcribed into prose, so a test reads it back against the counts.

Every other figure in the manuscript comes from `data/results.json` through a
script that draws it. Table 2 does not: it is a markdown table typed by hand,
added on 2026-08-25 with the counts already known, which is the worst combination
of properties a number in this paper can have. This test parses the table out of
`manuscript.md` and compares every cell against the block `aggregate.py` writes,
so that the two cannot drift apart in either direction.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
MANUSCRIPT = ROOT / "manuscript.md"
RESULTS = ROOT / "data" / "results.json"

# Row label in the manuscript -> key in results.json. "Works" is the denominator
# and is checked separately, because a wrong denominator is the failure that
# would make every other cell look consistent.
ROWS = {
    "C1, named as one instrument": "c1_identity",
    "C2, given the MBTI's provenance": "c2_provenance",
    "C3, claimed the standing of a published instrument": "c3_authority",
    "C1 or C2": "c1_or_c2",
    "Any of C1–C3": "any_conflation",
    "C0, no conflating statement": "c0_no_conflating_statement",
    "`states_distinction`, drew the distinction": "states_distinction",
}


def transcribed() -> dict[str, list[int]]:
    """The cells of Table 2, keyed by their row label, in column order (a), (b), (c)."""
    text = MANUSCRIPT.read_text(encoding="utf-8")
    start = text.index("**Table 2.** Conflation flags")
    block = text[start : text.index("\n\n", text.index("| **Works**", start))]
    cells: dict[str, list[int]] = {}
    for line in block.splitlines():
        if not line.startswith("|"):
            continue
        parts = [c.strip().strip("*") for c in line.strip("|").split("|")]
        label, values = parts[0], parts[1:]
        if not all(re.fullmatch(r"\d+", v) for v in values) or len(values) != 3:
            continue
        cells[label] = [int(v) for v in values]
    return cells


@pytest.fixture(scope="module")
def computed() -> dict:
    return json.loads(RESULTS.read_text(encoding="utf-8"))["post_hoc_counts_not_planned"]


def test_the_table_was_found_and_has_every_row(computed):
    cells = transcribed()
    assert set(cells) == {"Works", *ROWS}, "Table 2's rows have been renamed or renumbered"


def test_every_denominator_matches(computed):
    codes = computed["by_instrument_code"]
    assert transcribed()["Works"] == [codes[c]["works"] for c in ("a", "b", "c")]


@pytest.mark.parametrize("label, key", ROWS.items())
def test_every_cell_matches_the_computed_counts(computed, label, key):
    codes = computed["by_instrument_code"]
    assert transcribed()[label] == [codes[c][key] for c in ("a", "b", "c")]


WORDS = {"one": 1, "two": 2, "three": 3, "fifteen": 15, "sixteen": 16, "seventeen": 17}


@pytest.mark.parametrize("section", ["abstract", "results", "discussion"])
def test_the_prose_figure_matches_the_table(computed, section):
    """Three sections state the headline count, each in its own wording.

    The wordings differ on purpose — one is a numeral, one is spelled out, one is
    inverted — so each is pinned separately. Reading them back through the same
    computed values is the only thing stopping a later edit from changing one and
    leaving the other two behind, which is precisely what a first run of this
    test caught.
    """
    a = computed["by_instrument_code"]["a"]
    text = MANUSCRIPT.read_text(encoding="utf-8")
    patterns = {
        "abstract": rf"{a['any_conflation']} of the {a['works']} described the vendor's test "
                    rf"in terms its operator disclaims",
        "results": r"(\w+) of the (\w+) works that administered the vendor's test carried at "
                   r"least one conflating statement, and (\w+) of those identified it",
        "discussion": rf"of the {a['works']} works that administered the vendor's test, "
                      rf"{a['any_conflation']} described it in terms the vendor disclaims — "
                      rf"{a['c1_or_c2']} of them",
    }
    match = re.search(patterns[section], text)
    assert match, f"the {section} no longer states the count in its expected wording"
    if section == "results":
        assert [WORDS[g.lower()] for g in match.groups()] == [
            a["any_conflation"], a["works"], a["c1_or_c2"]
        ]


def test_the_states_distinction_count_is_stated_consistently(computed):
    a = computed["by_instrument_code"]["a"]
    text = MANUSCRIPT.read_text(encoding="utf-8")
    assert f"{a['states_distinction']} stated the distinction" in text
    assert f"{a['states_distinction']} marked the distinction somewhere in the text" in text
    assert f"{a['states_distinction']} of the {a['works']} works coded (a) state the distinction" in text


def test_every_file_the_manuscript_points_at_is_published():
    """A reader told to check a file must be able to reach it.

    `PLAN.md` and `PLAN-DEVIATIONS.md` are excluded from version control, so a
    manuscript sentence citing them sends the reader somewhere that does not
    exist. One such sentence was written and caught on 2026-08-25; this keeps the
    next one from surviving.
    """
    import subprocess

    text = MANUSCRIPT.read_text(encoding="utf-8")
    cited = set(re.findall(r"`((?:data|src|tests|figures|output|provenance)/[\w./-]+)`", text))
    tracked = set(
        subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    )
    assert cited, "no repository paths found — the extraction pattern has gone stale"
    assert not (cited - tracked), f"cited but not published: {sorted(cited - tracked)}"
    assert not re.search(r"`(PLAN|PLAN-DEVIATIONS)\.md`", text), "cites an unpublished file"


def test_the_table_carries_no_rate():
    """§12 fixed that nothing outside M1, M2 and the arms gets a proportion."""
    text = MANUSCRIPT.read_text(encoding="utf-8")
    start = text.index("**Table 2.** Conflation flags")
    block = text[start : text.index("\n\n", text.index("| **Works**", start))]
    assert "%" not in block and "CI" not in block


# --- quotations ------------------------------------------------------------


def test_every_quotation_is_accounted_for():
    """Run the quotation check, and refuse to pass when it had nothing to check.

    `sources/` is not in version control, so on a fresh clone the checker finds
    no archived text and every quotation "matches nothing". Letting that pass
    silently would turn an absent corpus into a green test, which is the same
    mistake as reading a checksum and calling the file non-empty. The test skips
    loudly instead, and only asserts where there is something to assert.
    """
    import subprocess
    import sys

    if not (ROOT / "sources").is_dir():
        pytest.skip("sources/ is not redistributed; the quotation check needs the archived texts")
    run = subprocess.run(
        [sys.executable, "src/verify_manuscript_quotes.py"],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert "not checked, file absent" not in run.stdout, run.stdout
    assert "MISS" not in run.stdout, run.stdout
    assert run.returncode == 0, run.stdout + run.stderr
