"""Tests for the planned reporting.

Two things here carry more weight than the rest.

§10's branch from result to claim is the study's central commitment, and the
only way it can be kept is for the branch to be evaluated by code that was
written and tested before the first count existed. So `pattern()` is exercised
on every row of §10's table using synthetic distributions, including the two
cases §10 left undetermined and §12 settled on 2026-08-22: a small `n1` that
also satisfies P1, and a tie between (b) and (c).

And the interval is computed in the repository rather than imported, because
scipy and statsmodels are installed here but absent from `requirements.txt`.
That is only safe if the formula is checked, so it is checked twice — against
published Wilson bounds, and against statsmodels where statsmodels is present.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import pytest

from aggregate import (
    C_FLAGS,
    MAIN_VENUES,
    NARROW_C_FLAGS,
    PATTERNS,
    R_FLAGS,
    ResultsError,
    any_of,
    booleans,
    check,
    measures,
    pattern,
    post_hoc,
    proportion,
    wilson,
)


def work(key: str = "w1", **overrides) -> dict:
    row = {
        "key": key,
        "doi": f"10.0000/{key}",
        "title": key,
        "work_venue_class": "journal_article",
        "e_final": "E1",
        "instrument_final": "a",
        "instrument_sublabel": "",
        "states_distinction_final": False,
        "third_party_conflation_c1": False,
        "third_party_conflation_c2": False,
        "text_is_abstract": False,
        "needs_adjudication": False,
    }
    row.update({f"{flag}_final": False for flag in R_FLAGS})
    row.update({f"{flag}_final": False for flag in ("c0",) + C_FLAGS})
    row.update({f"{flag}_final": False for flag in NARROW_C_FLAGS})
    row["c0_final"] = True
    row.update(overrides)
    return row


def frame(*rows: dict) -> pd.DataFrame:
    return pd.DataFrame(list(rows) or [work()])


def log_for(frame_: pd.DataFrame, **extra: int) -> pd.DataFrame:
    rows = [{"key": k, "status": "ok"} for k in frame_["key"]]
    for status, count in extra.items():
        rows += [{"key": f"{status}{i}", "status": status} for i in range(count)]
    return pd.DataFrame(rows)


def m1_of(a: int, b: int, c: int) -> dict:
    n1 = a + b + c
    return {
        "n1": n1,
        "distribution": None
        if not n1
        else {code: proportion(k, n1) for code, k in (("a", a), ("b", b), ("c", c))},
    }


# --- the interval ----------------------------------------------------------


@pytest.mark.parametrize(
    "k, n, low, high",
    [
        (0, 10, 0.0000, 0.2775),
        (5, 10, 0.2366, 0.7634),
        (10, 10, 0.7225, 1.0000),
        (1, 100, 0.0018, 0.0545),
    ],
)
def test_wilson_matches_published_bounds(k, n, low, high):
    assert wilson(k, n) == pytest.approx((low, high), abs=1e-4)


def test_wilson_agrees_with_statsmodels_where_it_is_installed():
    statsmodels = pytest.importorskip("statsmodels.stats.proportion")
    for n in (7, 20, 42, 61):
        for k in range(n + 1):
            assert wilson(k, n) == pytest.approx(
                tuple(statsmodels.proportion_confint(k, n, method="wilson")), abs=1e-9
            )


def test_wilson_refuses_an_empty_denominator():
    with pytest.raises(ResultsError):
        wilson(0, 0)


def test_wilson_refuses_more_successes_than_trials():
    with pytest.raises(ResultsError):
        wilson(5, 4)


# --- §10's branch ----------------------------------------------------------


def test_p1_when_the_lower_bound_clears_ten_percent():
    assert pattern(m1_of(10, 15, 15))["pattern"] == "P1"


def test_p2_when_the_point_estimate_clears_it_but_the_bound_does_not():
    m1 = m1_of(3, 8, 9)
    assert m1["distribution"]["a"]["p"] >= 0.10 > m1["distribution"]["a"]["ci_low"]
    result = pattern(m1)
    assert result["pattern"] == "P2"
    assert "substantial" in result["headline_wording"]


def test_p3_when_a_is_rare_and_c_is_the_largest():
    assert pattern(m1_of(2, 10, 28))["pattern"] == "P3"


def test_p4_when_a_is_rare_and_b_is_the_largest():
    assert pattern(m1_of(2, 28, 10))["pattern"] == "P4"


def test_p4_takes_the_tie_between_b_and_c():
    """§12, 2026-08-22. A tie satisfies neither P3's nor P4's description."""
    result = pattern(m1_of(2, 19, 19))
    assert result["pattern"] == "P4"
    assert "ties" in result["reason"]


def test_p5_governs_a_small_n1_even_when_p1_would_also_apply():
    """§12, 2026-08-22. The precedence §10's table omits.

    19 works all coded (a) satisfies P1 — the lower bound is far above 0.10 —
    and a precaution that gives way to a favourable interval is not one.
    """
    high = m1_of(19, 0, 0)
    assert high["distribution"]["a"]["ci_low"] >= 0.10
    assert pattern(high)["pattern"] == "P5"


def test_pattern_ignores_the_rounded_fields_and_recomputes_from_the_counts():
    """The reported bound is rounded to four places; the branch must not read it.

    3/20 has a Wilson lower bound near 0.05, so P2 is the row. A `ci_low` of
    0.9999 injected into the reported field would take P1 if the branch trusted
    it — which is how a bound of 0.09996, reported as 0.1000, could clear a
    threshold it does not actually clear.
    """
    m1 = m1_of(3, 8, 9)
    m1["distribution"]["a"]["ci_low"] = 0.9999
    m1["distribution"]["a"]["p"] = 0.9999
    assert pattern(m1)["pattern"] == "P2"


def test_pattern_reports_no_headline_rate_under_p5():
    assert pattern(m1_of(5, 5, 5))["abstract_leads_with"] == "M2"


# --- reading the settled columns -------------------------------------------


def test_booleans_refuses_a_blank_final():
    """A split with no ruling would otherwise count as a coded absence."""
    with pytest.raises(ResultsError, match="unsettled"):
        booleans(frame(work(r4_final="")), "r4_final")


def test_booleans_reads_the_strings_a_csv_round_trip_produces():
    read_back = frame(work(r4_final="True"), work("w2", r4_final="False"))
    assert booleans(read_back, "r4_final").tolist() == [True, False]


def test_any_of_is_the_union_of_the_flags():
    rows = frame(
        work("w1", c0_final=False, c2_final=True),
        work("w2"),
        work("w3", c0_final=False, c3_final=True),
    )
    assert any_of(rows, C_FLAGS).tolist() == [True, False, True]


# --- the integrity gate ----------------------------------------------------


def test_check_passes_a_settled_corpus():
    rows = frame(work())
    check(rows, log_for(rows))


def test_check_refuses_a_work_still_awaiting_a_ruling():
    rows = frame(work(needs_adjudication=True))
    with pytest.raises(ResultsError, match="await"):
        check(rows, log_for(rows))


def test_check_refuses_an_e1_work_with_no_instrument_code():
    rows = frame(work(instrument_final=""))
    with pytest.raises(ResultsError, match="E1 gate"):
        check(rows, log_for(rows))


def test_check_refuses_an_instrument_code_on_a_work_outside_e1():
    rows = frame(work(e_final="E4", instrument_final="c"))
    with pytest.raises(ResultsError, match="E1 gate"):
        check(rows, log_for(rows))


def test_check_refuses_a_sublabel_on_a_work_that_is_not_c():
    rows = frame(work(instrument_final="b", instrument_sublabel="c-online"))
    with pytest.raises(ResultsError, match="sub-labels"):
        check(rows, log_for(rows))


def test_check_refuses_narrow_conflation_wider_than_the_wide_reading():
    """S7 could otherwise report more conflation than the main analysis."""
    rows = frame(work(narrow_c1_final=True))
    with pytest.raises(ResultsError, match="narrow_c1"):
        check(rows, log_for(rows))


def test_check_refuses_c0_that_is_not_the_complement_of_c1_to_c3():
    rows = frame(work(c0_final=True, c1_final=True))
    with pytest.raises(ResultsError, match="c0_final"):
        check(rows, log_for(rows))


def test_check_refuses_a_row_count_that_does_not_match_the_retrieval_log():
    rows = frame(work())
    extra = pd.concat([log_for(rows), pd.DataFrame([{"key": "w9", "status": "ok"}])])
    with pytest.raises(ResultsError, match="status ok"):
        check(rows, extra)


# --- the measures ----------------------------------------------------------


def test_m1_counts_only_e1_works_inside_the_main_analysis():
    rows = frame(
        work("in", work_venue_class="journal_article", instrument_final="a"),
        work("out_venue", work_venue_class="preprint", instrument_final="a"),
        work("out_gate", e_final="E4", instrument_final="", c0_final=True),
    )
    result = measures(rows, MAIN_VENUES, rows["instrument_final"], C_FLAGS)
    assert result["m1"]["n1"] == 1
    assert result["m1"]["distribution"]["a"]["k"] == 1
    # M2 is coded on every retrieved work, whatever its venue or gate (§5, §6).
    assert result["m2"]["n"] == 3


def test_m1_is_not_computable_without_an_e1_work():
    rows = frame(work(e_final="E2", instrument_final=""))
    result = measures(rows, MAIN_VENUES, rows["instrument_final"], C_FLAGS)
    assert result["m1"]["distribution"] is None
    assert "not computable" in result["m1"]["note"]


def test_s3_rereads_vendor_cited_only_works_as_a():
    """§4.1's conservative call, restored as §11's fixed arm."""
    rows = frame(
        work("w1", instrument_final="c", instrument_sublabel="c-vendor-cited-only"),
        work("w2", instrument_final="c", instrument_sublabel="c-online"),
    )
    instrument = rows["instrument_final"]
    base = measures(rows, MAIN_VENUES, instrument, C_FLAGS)
    assert base["m1"]["distribution"]["a"]["k"] == 0
    assert base["m1"]["distribution"]["c"]["k"] == 2

    remapped = instrument.mask(
        (instrument == "c") & (rows["instrument_sublabel"] == "c-vendor-cited-only"), "a"
    )
    arm = measures(rows, MAIN_VENUES, remapped, C_FLAGS)
    assert arm["m1"]["distribution"]["a"]["k"] == 1
    assert arm["m1"]["distribution"]["c"]["k"] == 1


def test_s7_reads_the_narrow_flags_and_leaves_m1_alone():
    rows = frame(work(c0_final=False, c1_final=True, narrow_c1_final=False))
    wide = measures(rows, MAIN_VENUES, rows["instrument_final"], C_FLAGS)
    narrow = measures(rows, MAIN_VENUES, rows["instrument_final"], NARROW_C_FLAGS)
    assert wide["m2"]["any_conflation"]["k"] == 1
    assert narrow["m2"]["any_conflation"]["k"] == 0
    assert wide["m1"] == narrow["m1"]


# --- the unplanned cross-tabulation ----------------------------------------


def test_post_hoc_splits_the_conflation_flags_by_instrument_code():
    rows = frame(
        work("a1", instrument_final="a", c0_final=False, c1_final=True),
        work("a2", instrument_final="a", c0_final=False, c2_final=True),
        work("a3", instrument_final="a", c0_final=False, c1_final=True, c2_final=True),
        work("a4", instrument_final="a"),
        work("c1w", instrument_final="c", instrument_sublabel="c-unnamed",
             c0_final=False, c3_final=True),
    )
    block = post_hoc(rows, rows["instrument_final"])["by_instrument_code"]
    assert block["a"] == {
        "works": 4,
        "c1_identity": 2,
        "c2_provenance": 2,
        "c3_authority": 0,
        "c1_or_c2": 3,
        "any_conflation": 3,
        "c0_no_conflating_statement": 1,
        "states_distinction": 0,
    }
    # C3 alone is neither an identity nor a provenance claim, so the (c) work
    # counts as neither — the union must not quietly become "any C flag".
    assert block["c"]["c1_or_c2"] == 0
    assert block["b"] == {"works": 0}


def test_post_hoc_counts_only_e1_works_inside_the_main_analysis():
    rows = frame(
        work("in", instrument_final="a", c0_final=False, c1_final=True),
        work("venue", work_venue_class="preprint", instrument_final="a",
             c0_final=False, c1_final=True),
        work("gate", e_final="E2", instrument_final="", c0_final=False, c1_final=True),
    )
    block = post_hoc(rows, rows["instrument_final"])["by_instrument_code"]
    assert block["a"]["works"] == 1
    assert block["a"]["c1_identity"] == 1


def test_post_hoc_refuses_a_column_that_does_not_close():
    """The guard that would have caught the bug this block shipped with.

    Table 2 was first drawn with C1, C2 and C0 and no C3 row, so the (a) column
    accounted for 16 of its 17 works: C0 is defined against C1-C3, and the
    seventeenth work carried C3 alone. Nothing failed, because nothing was
    checking that the flagged and unflagged counts partition the works.
    """
    rows = frame(work("orphan", instrument_final="a", c0_final=False, c3_final=True))
    assert post_hoc(rows, rows["instrument_final"])["by_instrument_code"]["a"] == {
        "works": 1, "c1_identity": 0, "c2_provenance": 0, "c3_authority": 1,
        "c1_or_c2": 0, "any_conflation": 1, "c0_no_conflating_statement": 0,
        "states_distinction": 0,
    }
    # A work carrying neither C0 nor any C flag cannot exist under the protocol,
    # and if the coding ever produced one the block must refuse to report it.
    broken = frame(work("impossible", instrument_final="a", c0_final=False))
    with pytest.raises(ResultsError, match="do not partition"):
        post_hoc(broken, broken["instrument_final"])


def test_post_hoc_declares_itself_unplanned_and_rateless():
    block = post_hoc(frame(), frame()["instrument_final"])
    assert block["planned"] is False
    # No key may carry a proportion or an interval: §12 fixed that only M1, M2
    # and the arms do, and this block was added after every count existed.
    assert not {"p", "ci_low", "ci_high"} & set(block["by_instrument_code"]["a"])


# --- §10's promised wording is a quotation, so it is pinned as one -------------

PROTOCOL = Path(__file__).resolve().parent.parent / "data" / "coding_protocol.md"


def _protocol_patterns() -> dict[str, tuple[str, str]]:
    """P1-P5 as they stand in §10's table: (what the abstract leads with, wording)."""
    rows = re.findall(
        r"^\|\s*\*\*(P[1-5])\*\*\s*\|(.*?)\|(.*?)\|(.*?)\|\s*$",
        PROTOCOL.read_text(encoding="utf-8"),
        re.M,
    )
    return {name: (leads.strip(), wording.strip()) for name, _cond, leads, wording in rows}


def test_the_protocol_table_is_still_parseable():
    """A negative control for the two tests below.

    Both compare `PATTERNS` against rows extracted from the protocol. If the
    table is reformatted and the pattern stops matching, the extraction returns
    nothing and every comparison below passes over an empty set — the shape of
    failure this repository keeps finding in itself. So the count is asserted
    first, and it is asserted against the names, not just the length.
    """
    found = _protocol_patterns()
    assert set(found) == {"P1", "P2", "P3", "P4", "P5"}, (
        "§10's table no longer yields five patterns; the tests below would pass vacuously"
    )
    assert all(w for _, w in found.values()), "a pattern row parsed to an empty wording"


@pytest.mark.parametrize("name", ["P1", "P2", "P3", "P4", "P5"])
def test_the_promised_wording_is_quoted_character_for_character(name):
    """`PATTERNS` quotes §10; a quotation that has been tidied is not evidence.

    Three of these were paraphrases until 2026-08-28, under a comment saying all
    five were verbatim. P3 had lost "of papers reporting MBTI results" — the
    population claim this study spent Limitation 1 and two departure rows
    retracting — which made the pre-commitment read better than it was.

    Compared raw. Normalising would fold exactly the differences that mattered:
    an ASCII ellipsis for U+2026, a dropped pair of quotation marks, a full stop
    changed to a semicolon.
    """
    promised_leads, promised_wording = _protocol_patterns()[name]
    assert PATTERNS[name][1] == promised_wording
    assert PATTERNS[name][0] == promised_leads


# --- the rules are read as rules, not as a record -----------------------------

# Phrases the change log has retracted. Each may still stand in §§1-11 — a rule
# rewritten after the fact is no longer evidence of what the coders were given —
# but only with its correction marked where a reader meets it.
RETRACTED_IN_THE_RULES = [
    "the vendor itself disclaims",
    "an assertion of descent that the vendor denies",
    "and that is disclaimed",
    "descent from the published MBTI, and the adoption of Jungian",
]


@pytest.mark.parametrize("phrase", RETRACTED_IN_THE_RULES)
def test_a_retracted_rule_stands_only_with_its_correction_marked(phrase):
    """§§1-11 are what the coders were given; §12 is the record of what changed.

    Every guard in this repository reads `manuscript.md`. None read the protocol
    as rules, and on 2026-08-28 that gap surfaced: four sentences in §6 still
    defined C2 by a denial the vendor never made — the error this study exists to
    measure — while §12 recorded that the correction had reached them. It had not.
    The manuscript meanwhile called the row "an earlier version" of itself.

    The sentences stay. What must never again be absent is the mark beside them.
    """
    text = PROTOCOL.read_text(encoding="utf-8")
    rules = text[: text.index("## 12. Changes after coding began")]
    assert len(rules) > 0.2 * len(text), "the rules/log split has moved; this test is scanning nothing"
    if phrase not in rules:
        return  # the sentence was removed outright, which is also fine
    start = 0
    while (idx := rules.find(phrase, start)) != -1:
        window = rules[max(0, idx - 400) : idx + 700]
        assert "\u26a0" in window, (
            f"{phrase!r} stands in the rules with no correction mark beside it; "
            "the log retracted it, so a reader of §§1-11 is being given a rule the study disowns"
        )
        start = idx + 1
