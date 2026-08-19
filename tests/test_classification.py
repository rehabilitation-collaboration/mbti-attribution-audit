"""Tests for assembling the coders' output and scoring their agreement.

Three things here are worth more than the rest. Schema validation has to reject
a coding that omits a flag, because a missing flag silently read as false would
enter the counts as a coded absence. The narrow conflation reading has to be a
subset of the wide one, or S7 could report more conflation than the main
analysis. And kappa has to refuse to exist when the coders used one category
between them, because returning 1.0 there would hand the study its strongest
reliability figure for a flag nobody ever set.
"""

from __future__ import annotations

import copy

import pandas as pd
import pytest

from build_classification import (
    SchemaError,
    build_row,
    normalise_quote,
    validate_flags,
    validate_gate,
)
from score_agreement import cohen_kappa, score


def gate(coder: str = "c1", **overrides) -> dict:
    doc = {
        "key": "w1",
        "coder": coder,
        "e_code": "E1",
        "e_quote": "Participants completed the test — Methods",
        "instrument": "a",
        "instrument_sublabel": None,
        "instrument_quote": "via 16personalities.com — Methods",
        "instrument_evidence_level": 1,
        "text_is_abstract": False,
        "text_is_abstract_evidence": None,
        "uncertain": False,
        "uncertain_note": None,
        "free_text": None,
    }
    doc.update(overrides)
    return doc


def flags(coder: str = "c1", **overrides) -> dict:
    doc = {
        "key": "w1",
        "coder": coder,
        "roles": {f"r{i}": False for i in range(1, 8)} | {"r1": True},
        "role_quotes": {"r1": "the NERIS Type Explorer — Methods"},
        "conflation": {"c0": True, "c1": False, "c2": False, "c3": False},
        "conflation_quotes": {},
        "conflation_narrow": {"c1": False, "c2": False, "c3": False},
        "states_distinction": False,
        "states_distinction_quote": None,
        "third_party_conflation": False,
        "third_party_conflation_quote": None,
        "uncertain": False,
        "uncertain_note": None,
        "free_text": None,
    }
    doc.update(overrides)
    return doc


META = pd.Series(
    {"doi": "10.1/x", "title": "A work", "work_venue_class": "journal_article"}, name="w1"
)


def row_for(gate_docs=None, flag_docs=None) -> dict:
    gate_docs = gate_docs or {c: gate(c) for c in ("c1", "c2")}
    flag_docs = flag_docs or {c: flags(c) for c in ("c1", "c2")}
    return build_row("w1", META, gate_docs, flag_docs)


# --- quote shapes ---------------------------------------------------------


def test_a_plain_string_quote_is_kept():
    assert normalise_quote("  the MBTI was administered — Methods  ") == (
        "the MBTI was administered — Methods"
    )


def test_a_quote_section_object_is_joined():
    got = normalise_quote({"quote": "via 16personalities.com", "section": "Methods 2.1"})
    assert got == "via 16personalities.com — Methods 2.1"


def test_a_partial_object_does_not_gain_a_dangling_dash():
    assert normalise_quote({"quote": "no section given", "section": ""}) == "no section given"
    assert normalise_quote({"section": "Methods"}) == "Methods"


def test_a_list_of_quotes_becomes_a_chain():
    """§6 asks for every link of a cross-sentence chain."""
    got = normalise_quote(
        ["named as one — Methods", {"quote": "based on Jung", "section": "Introduction"}]
    )
    assert got == "named as one — Methods || based on Jung — Introduction"


def test_absent_and_empty_quotes_read_as_missing():
    assert normalise_quote(None) == ""
    assert normalise_quote("   ") == ""
    assert normalise_quote([]) == ""


def test_an_unusable_quote_shape_is_rejected():
    with pytest.raises(SchemaError, match="must be a string"):
        normalise_quote(42)


# --- gate schema ----------------------------------------------------------


def test_valid_gate_passes():
    validate_gate(gate(), "w1", "c1")


def test_e1_without_instrument_is_rejected():
    with pytest.raises(SchemaError, match="E1 needs an instrument"):
        validate_gate(gate(instrument=None, instrument_quote=None), "w1", "c1")


def test_instrument_on_non_e1_is_rejected():
    with pytest.raises(SchemaError, match="must not carry an instrument"):
        validate_gate(gate(e_code="E4"), "w1", "c1")


def test_new_sublabel_is_accepted():
    validate_gate(gate(instrument="c", instrument_sublabel="c-named-unsourced"), "w1", "c1")


def test_unknown_sublabel_is_rejected():
    with pytest.raises(SchemaError, match="unknown sublabel"):
        validate_gate(gate(instrument="c", instrument_sublabel="c-invented"), "w1", "c1")


def test_file_naming_mismatch_is_rejected():
    with pytest.raises(SchemaError, match="file names"):
        validate_gate(gate(), "other-key", "c1")


# --- flag schema ----------------------------------------------------------


def test_valid_flags_pass():
    validate_flags(flags(), "w1", "c1")


def test_missing_flag_is_rejected():
    doc = flags()
    del doc["roles"]["r7"]
    with pytest.raises(SchemaError, match="roles must set exactly"):
        validate_flags(doc, "w1", "c1")


def test_c0_contradicting_the_other_flags_is_rejected():
    doc = flags()
    doc["conflation"] = {"c0": True, "c1": True, "c2": False, "c3": False}
    doc["conflation_quotes"] = {"c1": "named as one — Introduction"}
    with pytest.raises(SchemaError, match="c0 must be true exactly when"):
        validate_flags(doc, "w1", "c1")


def test_narrow_flag_without_the_wide_one_is_rejected():
    """S7 must be a subset: the narrow reading cannot exceed the main analysis."""
    doc = flags()
    doc["conflation_narrow"]["c2"] = True
    with pytest.raises(SchemaError, match="narrow c2 set while wide c2 is not"):
        validate_flags(doc, "w1", "c1")


def test_flag_without_a_quote_is_rejected():
    doc = flags()
    doc["role_quotes"] = {}
    with pytest.raises(SchemaError, match="r1 set without a quote"):
        validate_flags(doc, "w1", "c1")


def test_states_distinction_without_a_quote_is_rejected():
    with pytest.raises(SchemaError, match="states_distinction set without a quote"):
        validate_flags(flags(states_distinction=True), "w1", "c1")


def test_third_party_conflation_without_a_quote_is_rejected():
    with pytest.raises(SchemaError, match="third_party_conflation set without a quote"):
        validate_flags(flags(third_party_conflation=True), "w1", "c1")


# --- assembly -------------------------------------------------------------


def test_agreement_fills_final_and_needs_no_ruling():
    row = row_for()
    assert row["e_final"] == "E1"
    assert row["instrument_final"] == "a"
    assert row["r1_final"] is True
    assert row["r7_final"] is False
    assert row["c0_final"] is True
    assert row["needs_adjudication"] is False
    assert row["quote_instrument"].startswith("via 16personalities.com")


def test_disagreement_leaves_final_empty_and_is_listed():
    g = {"c1": gate("c1"), "c2": gate("c2", e_code="E2", instrument=None, instrument_quote=None)}
    row = row_for(gate_docs=g)
    assert row["e_final"] == ""
    assert row["instrument_final"] == ""
    assert "e" in row["contested"].split(",")
    assert row["needs_adjudication"] is True


def test_uncertainty_in_either_pass_forces_a_ruling():
    f = {"c1": flags("c1"), "c2": flags("c2", uncertain=True, uncertain_note="§6 undecided")}
    row = row_for(flag_docs=f)
    assert row["contested"] == ""
    assert row["needs_adjudication"] is True
    assert "c2/flags: §6 undecided" in row["uncertain_note"]


def test_r7_disagreement_is_contested():
    c2 = copy.deepcopy(flags("c2"))
    c2["roles"]["r7"] = True
    c2["role_quotes"]["r7"] = "the site is the corpus — Method"
    row = row_for(flag_docs={"c1": flags("c1"), "c2": c2})
    assert row["r7_final"] == ""
    assert row["contested"] == "r7"


def test_narrow_and_wide_are_scored_separately():
    wide_only = copy.deepcopy(flags("c1"))
    wide_only["conflation"] = {"c0": False, "c1": True, "c2": False, "c3": False}
    wide_only["conflation_quotes"] = {"c1": "the MBTI dimensions — Table 2"}
    both = copy.deepcopy(wide_only)
    both["coder"] = "c2"
    both["conflation_narrow"]["c1"] = True
    row = row_for(flag_docs={"c1": wide_only, "c2": both})
    assert row["c1_final"] is True
    assert row["narrow_c1_final"] == ""
    assert row["contested"] == "narrow_c1"


def test_third_party_conflation_is_recorded_but_never_contested():
    c2 = flags("c2", third_party_conflation=True, third_party_conflation_quote="Humanmetrics — §3.3")
    row = row_for(flag_docs={"c1": flags("c1"), "c2": c2})
    assert row["third_party_conflation_c2"] is True
    assert "third_party_conflation" not in row["contested"]
    assert "third_party_conflation_final" not in row
    assert row["needs_adjudication"] is False


def test_empty_sublabels_are_not_a_disagreement():
    """§3.4: a sub-label is optional, so absent-vs-absent is agreement."""
    g = {c: gate(c, instrument="c", instrument_sublabel=None) for c in ("c1", "c2")}
    row = row_for(gate_docs=g)
    assert "instrument_sublabel" not in row["contested"]
    assert row["needs_adjudication"] is False


# --- kappa ----------------------------------------------------------------


def test_perfect_agreement_with_variation_is_one():
    kappa, observed, _ = cohen_kappa([1, 1, 0, 0], [1, 1, 0, 0])
    assert kappa == pytest.approx(1.0)
    assert observed == pytest.approx(1.0)


def test_chance_level_agreement_is_zero():
    kappa, observed, expected = cohen_kappa([1, 1, 0, 0], [1, 0, 1, 0])
    assert observed == pytest.approx(0.5)
    assert expected == pytest.approx(0.5)
    assert kappa == pytest.approx(0.0)


def test_known_three_case_value():
    kappa, _, _ = cohen_kappa(["E1", "E1", "E2"], ["E1", "E2", "E2"])
    assert kappa == pytest.approx(0.4)


def test_kappa_is_undefined_when_no_one_ever_set_the_flag():
    """The failure this file exists to prevent: 1.0 from an unused flag."""
    kappa, observed, expected = cohen_kappa([False] * 8, [False] * 8)
    assert kappa is None
    assert observed == pytest.approx(1.0)
    assert expected == pytest.approx(1.0)


def test_score_reports_the_undefined_case_rather_than_a_number():
    frame = pd.DataFrame({"r5_c1": [False, False], "r5_c2": [False, False]})
    row = score(frame, "R5", "r5_c1", "r5_c2")
    assert row["kappa"] == ""
    assert "undefined" in row["note"]
    assert row["observed_agreement"] == pytest.approx(1.0)


def test_empty_input_raises_rather_than_returning_a_figure():
    with pytest.raises(ValueError, match="no works"):
        cohen_kappa([], [])
