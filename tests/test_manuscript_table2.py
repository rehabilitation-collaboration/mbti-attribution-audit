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
    "C0, none of C1–C3": "c0_no_conflating_statement",
    "`states_distinction`, noted some difference between the two": "states_distinction",
}


def transcribed() -> dict[str, list[int]]:
    """The cells of Table 2, keyed by their row label, in column order (a), (b), (c)."""
    text = MANUSCRIPT.read_text(encoding="utf-8")
    start = text.index("**Table 2.** Pre-defined C flags")
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

QUOTED = re.compile(r'"[^"]*"|“[^”]*”')


def unquoted(text: str) -> str:
    """The manuscript with every quoted span removed.

    A retracted phrasing may still appear inside quotation marks — the departures
    table quotes what the protocol promised, and the withdrawal passages quote
    what they withdraw. Those are the paper reporting its own corrections, not
    committing them again, so the bans below are checked against prose only.
    """
    return QUOTED.sub(" ", text)


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
        "abstract": rf"{a['c1_or_c2']} of the {a['works']} describing it as the MBTI "
                    rf"or as descended from it",
        "results": rf"\*\*{a['c1_or_c2']} of the {a['works']} either did that or gave the "
                   rf"vendor's test the MBTI's provenance\*\*",
        "discussion": r"\*\*(\w+) of seventeen described the vendor-hosted test as the "
                      r"MBTI or as descended from it",
    }
    match = re.search(patterns[section], text)
    assert match, f"the {section} no longer states the count in its expected wording"
    if section == "discussion":
        assert WORDS[match.group(1).lower()] == a["c1_or_c2"]
    # The C3-only work must not be folded into the attribution figure anywhere.
    spelled = {v: k.capitalize() for k, v in WORDS.items()}[a["any_conflation"]]
    assert f"{spelled} of seventeen described the vendor-hosted test" not in text
    assert f"{a['any_conflation']} of the {a['works']} describing it as the MBTI" not in text


def test_states_distinction_is_never_described_as_drawing_the_distinction(computed):
    """The field records that a work noted a difference, not that it got it right.

    One of the three works it flags writes "16 types identical to the Myers-Briggs
    test" and carries C1. Reporting the field under the name "drew the
    distinction" made the manuscript contradict its own next paragraph, so the
    label is gone and must not come back.
    """
    a = computed["by_instrument_code"]["a"]
    text = MANUSCRIPT.read_text(encoding="utf-8")
    spelled = {1: "One", 2: "Two", 3: "Three"}[a["states_distinction"]]
    assert f"{spelled} carry the protocol's `states_distinction` field" in text
    for banned in ("drew the distinction", "stated the distinction", "state the distinction",
                   "states the distinction", "drew it correctly"):
        assert banned not in text, f"{banned!r} overstates what the field records"
    assert "the count is two, not three" in text


def test_no_sentence_asserts_a_non_identity_this_study_did_not_establish():
    """Both vendor pages were retrieved in 2026, so (a) reaches no further than that.

    An (a) code records that a vendor-hosted test was administered and that no
    published MBTI form is identifiable from the work. Whether the product was
    distinct from the MBTI on the date any coded paper was written is not
    established here. The Discussion says so; a third round of external review
    found five sentences elsewhere that said the opposite, each of them left
    behind when the limit was written into one section only. This pins them shut.
    """
    # Quoted spans are exempt: the departures table quotes §10's promise in order
    # to report the departure from it, and the withdrawal passages quote the
    # wording they withdraw. Scanning those would ban the paper from saying what
    # it stopped saying.
    text = MANUSCRIPT.read_text(encoding="utf-8")
    for banned in ("rather than the MBTI",
                   "an instrument that is not the MBTI",
                   "administered something else",
                   "instrument different from the one named",
                   "is the misattribution"):
        assert banned not in unquoted(text), (
            f"{banned!r} asserts a non-identity this study did not establish"
        )
    # And the limit itself must still be stated, or the bans above pass vacuously
    # on a manuscript that simply stopped mentioning the question.
    assert "no published MBTI form identifiable from the work" in text
    assert "the only evidence offered is dated 2026" in text


def test_the_union_of_the_c_flags_is_never_called_a_conflation_rate():
    """C3 alone is a claim of standing, and this study judges no claim of standing.

    C1 and C2 are conflations of the two instruments; C3 is not. The union of the
    three is a flag count, so naming it "a conflating statement" reads a verdict
    into a work the coding never reached — the same over-reading the study audits.
    """
    prose = unquoted(MANUSCRIPT.read_text(encoding="utf-8"))
    for banned in ("(a conflating statement)",
                   "no conflating statement",
                   "carried a conflating statement",
                   "reproduced the conflation in prose"):
        assert banned not in prose, f"{banned!r} calls the C1-C3 union a conflation"
    assert "any pre-defined C1–C3 flag" in prose


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


def test_the_table_prints_no_percentage_and_no_interval():
    """The block is exploratory, so it carries no model-based interval.

    The defence that it "carries counts and no rate" was withdrawn — "sixteen of
    seventeen" is a proportion however it is printed — and the block is now
    described as exploratory, post hoc descriptive proportions. What must stay
    true of the table itself is that no percentage and no interval is printed
    beside a figure the protocol never planned.
    """
    text = MANUSCRIPT.read_text(encoding="utf-8")
    start = text.index("**Table 2.** Pre-defined C flags")
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
