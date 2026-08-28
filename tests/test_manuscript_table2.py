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


def _works_row(text: str, start: int) -> int:
    """Offset of Table 2's denominator row, whatever weight its label is set in.

    This anchor located the row by the literal `| **Works**`, which pinned a
    typographic choice: when emphasis was reserved for the claims the paper
    asserts, the bold came off every row of this exploratory table and the
    anchor stopped matching. What the tests below check is the counts, and the
    counts are read cell by cell with `*` stripped, so the anchor has no reason
    to care either way.
    """
    match = re.search(r"^\|\s*\*{0,2}Works\*{0,2}\s*\|", text[start:], re.M)
    assert match, "Table 2 has no denominator row — the table has been restructured"
    return start + match.start()


def transcribed() -> dict[str, list[int]]:
    """The cells of Table 2, keyed by their row label, in column order (a), (b), (c)."""
    text = MANUSCRIPT.read_text(encoding="utf-8")
    start = text.index("**Table 2.** Pre-defined C flags")
    block = text[start : text.index("\n\n", _works_row(text, start))]
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


WORDS = {"one": 1, "two": 2, "three": 3, "thirteen": 13, "fifteen": 15,
         "sixteen": 16, "seventeen": 17}

# A permanent counter-example. The bans below are a list, and a list can only
# prove that the sentences already on it are gone — three sentences this list
# was written to catch were found later by readers, not by it. This string is
# never in the manuscript, so if `unquoted()` ever stops returning scannable
# prose (an unbalanced quote swallowing the file, a path change, an empty read)
# the canary test fails and says so, instead of every ban passing vacuously.
CANARY = "administered an instrument that is not the MBTI"

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
    # C1 is the centre: the vendor states plainly that its test is not the MBTI, so
    # a work calling it the MBTI contradicts something the vendor actually says. C2
    # records an asserted derivation the vendor neither claims nor denies, so it is
    # pinned as the broader reading and never as the headline.
    #
    # These patterns once required the surrounding `**`. That pinned a typographic
    # choice the test was never about: emphasis was later reserved for the few
    # claims the paper asserts, and three of these sentences lost their bold while
    # every count stayed put. What the test exists to catch is a count edited in
    # one section and left behind in the others, so it now reads the wording and
    # the number and says nothing about the weight of the type.
    patterns = {
        "abstract": rf"{a['c1_identity']} of the {a['works']} describing it as the MBTI"
                    rf"\*{{0,2}}, contrary to the vendor's 2026 statement",
        "results": rf"{a['c1_identity']} of the {a['works']} described the vendor's test "
                   rf"as the MBTI\*{{0,2}} \(C1\) — \*{{0,2}}the central attribution finding",
        "discussion": r"(\w+) of seventeen described the vendor-hosted test as the MBTI, "
                      r"contrary to the vendor's 2026 statement",
    }
    match = re.search(patterns[section], text)
    assert match, f"the {section} no longer states the count in its expected wording"
    if section == "discussion":
        assert WORDS[match.group(1).lower()] == a["c1_identity"]
    # The broader reading is still reported, and still as the broader reading.
    assert (f"{a['c1_or_c2']} of the {a['works']} either did that or asserted that the "
            f"vendor's test derives from the MBTI") in text
    # Neither the C1-or-C2 nor the any-flag count may be given C1's wording. Dropping
    # the trailing `**` widens these two bans rather than narrowing them: the wrong
    # count is now forbidden in that wording whether or not it is set in bold.
    spelled = {v: k.capitalize() for k, v in WORDS.items()}
    for n in (a["c1_or_c2"], a["any_conflation"]):
        assert f"{spelled[n]} of seventeen described the vendor-hosted test as the MBTI," not in text
        assert f"{n} of the {a['works']} describing it as the MBTI" not in text


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
    # The first five came from the third review's own quotations. The last two were
    # found by a later reader, in sections that review had not quoted, and they are
    # added because a known error should not be allowed back — not because the list
    # is now complete. It cannot be: a ban-list only ever proves that the sentences
    # on it are gone. What guards against the scanner itself going blind is the
    # negative control below, which is a different problem from coverage.
    for banned in ("rather than the MBTI",
                   "an instrument that is not the MBTI",
                   "administered something else",
                   "instrument different from the one named",
                   "is the misattribution",
                   # Sentence-initial: the assertive form. The paper's corrected
                   # sentence opens "Whether the distinction was discoverable …
                   # is not something this study examined", which must pass.
                   "The distinction was discoverable",
                   "why the substitution matters"):
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


def test_the_paper_never_says_the_vendor_disclaims_a_derivation_from_the_mbti():
    """The vendor denies being the MBTI. It does not deny descending from it.

    Its framework page states that it uses "the acronym format introduced by
    Myers-Briggs" and recounts the MBTI's origins approvingly; what it denies is
    identity and the incorporation of Jungian cognitive functions. C2's row twice
    claimed a denial the sources do not contain — first naming Jung, then, after
    that correction, naming descent from the published MBTI. Attributing to a
    source a position it does not hold is the error this study measures, so the
    ban is permanent and C2 carries no verdict.
    """
    prose = unquoted(MANUSCRIPT.read_text(encoding="utf-8"))
    for banned in ("a lineage the vendor disclaims",
                   "the lineages the vendor denies",
                   "the three the vendor denies",
                   "lineages C2 covers are the three",
                   "descent from the published MBTI, and the use of Jungian"):
        assert banned not in prose, f"{banned!r} attributes a denial the vendor never made"
    assert "this study does not adjudicate it" in prose


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
    block = text[start : text.index("\n\n", _works_row(text, start))]
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


def test_the_scanner_the_bans_rely_on_is_not_returning_empty_prose():
    """A negative control for the two ban tests above.

    Both bans are `assert <string> not in unquoted(text)`. That assertion passes
    for the right reason and also for several wrong ones: an unbalanced quotation
    mark that makes `QUOTED` swallow the file, a manuscript that failed to load, a
    path that moved. None of those would fail any existing test — the bans would
    simply stop looking and report success, which is the shape of failure this
    paper is about.

    So: the scanner must still be returning most of the file, and it must still be
    able to find the banned string when the string is actually there.
    """
    text = MANUSCRIPT.read_text(encoding="utf-8")
    prose = unquoted(text)
    assert len(prose) > 0.9 * len(text), (
        f"unquoted() removed {100 * (1 - len(prose) / len(text)):.1f}% of the manuscript; "
        "the quotation regex is swallowing prose and every ban below it is vacuous"
    )
    assert CANARY not in prose, "the canary is in the manuscript; it was never meant to be"
    assert CANARY in unquoted(f"x {CANARY} y"), "unquoted() cannot see a banned string at all"


def test_figure4_annotates_each_unestimated_arm_with_its_own_reason():
    """S2 and S5 both yield no estimate, and they do so for different reasons.

    Figure 4 used to print one hard-coded string for both, so S2 displayed S5's
    explanation and contradicted Table 5. The annotation is now read from each
    arm's own `note` in results.json, taking the text before the first colon.
    That parse is only safe while the notes keep leading with a short clause, so
    it is checked here rather than trusted.
    """
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    arms = results["sensitivity"]
    unestimated = {k: v for k, v in arms.items() if v["m1"] is None and v["m2"] is None}
    assert set(unestimated) == {"S2", "S5"}, "which arms yield no estimate has changed"

    leads = {}
    for key, arm in unestimated.items():
        note = arm.get("note", "")
        assert note, f"{key} has no note, so the figure would annotate it with nothing"
        lead = note.split(":", 1)[0]
        assert 0 < len(lead) <= 60, (
            f"{key}'s note does not lead with a short clause ({len(lead)} chars); "
            "figure4() would render the whole note into the plot"
        )
        leads[key] = lead
    assert leads["S2"] != leads["S5"], (
        "both arms would be annotated identically — the defect this parse replaced"
    )
    assert "estimable" in leads["S2"] and "bound" in leads["S5"], leads


# --- what the reader actually receives ---------------------------------------

SCOPE_CLAUSE = "Enriched, programmatically retrievable intersection"


def test_every_figure_legend_states_the_sample_it_describes():
    """A figure travels without its paper, so its own caption must say what it is.

    Two external rounds asked for this. The first attempt put one shared sentence
    at the head of the Figure Legends section — where `generate_pdf.py` never
    looks, because it extracts only paragraphs beginning `**Figure N.**`. The
    clause was in the markdown, was reported as done, and reached no reader.
    """
    text = MANUSCRIPT.read_text(encoding="utf-8")
    section = text[text.index("## Figure Legends") :]
    legends = re.findall(r"\*\*Figure (\d)\.\*\*(.+)", section)
    assert len(legends) == 4, f"expected four figure legends, found {len(legends)}"
    for number, body in legends:
        assert SCOPE_CLAUSE in body, (
            f"Figure {number}'s legend does not say what sample it describes; "
            "a reader meeting the figure alone could read its proportion as a population rate"
        )


def test_every_table_caption_states_the_sample_it_describes():
    """Same requirement, same reason: tables get screenshotted too."""
    text = MANUSCRIPT.read_text(encoding="utf-8")
    results = text[text.index("## Results") : text.index("## Discussion")]
    captions = re.findall(r"\*\*Table (\d)\.\*\*(.+)", results)
    assert len(captions) == 5, f"expected five table captions in Results, found {len(captions)}"
    for number, body in captions:
        assert SCOPE_CLAUSE in body, f"Table {number}'s caption does not state its sample"


def test_the_legends_are_stripped_from_the_body_so_they_print_once():
    """The generator prints each legend under its figure and must not print it twice.

    `generate_pdf.py` removes the legends section from the body before rendering.
    That substitution terminated on the next `## ` heading only. When the
    abbreviated Tables index was deleted on 2026-08-28 there was no next heading,
    the removal silently stopped matching, and all four legends printed twice —
    once in the body, once under the figure. Nothing in the markdown looked wrong.
    """
    text = MANUSCRIPT.read_text(encoding="utf-8")
    stripped = re.sub(r"## Figure Legends\n.*?(?=\n## |\Z)", "", text, flags=re.DOTALL)
    assert "## Figure Legends" not in stripped, (
        "the legends section survives the strip the PDF generator performs; "
        "every legend would print twice"
    )
    for n in range(1, 5):
        assert f"**Figure {n}.**" not in stripped, f"Figure {n}'s legend would print twice"
