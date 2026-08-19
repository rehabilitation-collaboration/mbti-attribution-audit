"""Tests for assembling the coders' output and scoring their agreement.

Two things here are worth more than the rest. Schema validation has to reject a
coding that omits a flag, because a missing flag silently read as false would
enter the counts as a coded absence. And kappa has to refuse to exist when the
coders used one category between them, because returning 1.0 there would hand
the study its strongest reliability figure for a flag nobody ever set.
"""

from __future__ import annotations

import copy

import pandas as pd
import pytest

from build_classification import SchemaError, build_row, validate
from score_agreement import cohen_kappa, score


def coding(coder: str = "c1", **overrides) -> dict:
    doc = {
        "key": "w1",
        "coder": coder,
        "e_code": "E1",
        "e_quote": "Participants completed the test — Methods",
        "instrument": "a",
        "instrument_sublabel": None,
        "instrument_quote": "via 16personalities.com — Methods",
        "instrument_evidence_level": 1,
        "roles": {"r1": True, "r2": False, "r3": False, "r4": False, "r5": False, "r6": False},
        "role_quotes": {"r1": "the NERIS Type Explorer — Methods"},
        "conflation": {"c0": True, "c1": False, "c2": False, "c3": False},
        "conflation_quotes": {},
        "text_is_abstract": False,
        "text_is_abstract_evidence": None,
        "uncertain": False,
        "uncertain_note": None,
        "free_text": None,
    }
    doc.update(overrides)
    return doc


META = pd.Series(
    {"doi": "10.1/x", "title": "A work", "work_venue_class": "journal_article"}, name="w1"
)


# --- schema ---------------------------------------------------------------


def test_valid_coding_passes():
    validate(coding(), "w1", "c1")


def test_missing_flag_is_rejected():
    doc = coding()
    del doc["roles"]["r5"]
    with pytest.raises(SchemaError, match="roles must set exactly"):
        validate(doc, "w1", "c1")


def test_e1_without_instrument_is_rejected():
    with pytest.raises(SchemaError, match="E1 needs an instrument"):
        validate(coding(instrument=None, instrument_quote=None), "w1", "c1")


def test_instrument_on_non_e1_is_rejected():
    with pytest.raises(SchemaError, match="must not carry an instrument"):
        validate(coding(e_code="E4"), "w1", "c1")


def test_sublabel_outside_c_is_rejected():
    with pytest.raises(SchemaError, match="sublabel"):
        validate(coding(instrument_sublabel="c-unnamed"), "w1", "c1")


def test_c0_contradicting_the_other_flags_is_rejected():
    doc = coding()
    doc["conflation"] = {"c0": True, "c1": True, "c2": False, "c3": False}
    doc["conflation_quotes"] = {"c1": "named as one — Introduction"}
    with pytest.raises(SchemaError, match="c0 must be true exactly when"):
        validate(doc, "w1", "c1")


def test_flag_without_a_quote_is_rejected():
    doc = coding()
    doc["role_quotes"] = {}
    with pytest.raises(SchemaError, match="r1 set without a quote"):
        validate(doc, "w1", "c1")


def test_file_naming_mismatch_is_rejected():
    with pytest.raises(SchemaError, match="file names"):
        validate(coding(), "other-key", "c1")


# --- assembly -------------------------------------------------------------


def test_agreement_fills_final_and_needs_no_ruling():
    row = build_row("w1", META, {"c1": coding("c1"), "c2": coding("c2")})
    assert row["e_final"] == "E1"
    assert row["instrument_final"] == "a"
    assert row["r1_final"] is True
    assert row["c0_final"] is True
    assert row["needs_adjudication"] is False
    assert row["quote_instrument"].startswith("via 16personalities.com")


def test_disagreement_leaves_final_empty_and_is_listed():
    c2 = coding("c2", e_code="E2", instrument=None, instrument_quote=None)
    row = build_row("w1", META, {"c1": coding("c1"), "c2": c2})
    assert row["e_final"] == ""
    assert row["instrument_final"] == ""
    assert "e" in row["contested"].split(",")
    assert row["needs_adjudication"] is True
    assert row["quote_instrument"] == ""


def test_instrument_is_not_scored_when_the_gate_is_not_e1():
    both_e4 = {
        c: coding(c, e_code="E4", instrument=None, instrument_quote=None) for c in ("c1", "c2")
    }
    row = build_row("w1", META, both_e4)
    assert row["e_final"] == "E4"
    assert row["instrument_final"] == ""
    assert "instrument" not in row["contested"].split(",")
    assert row["needs_adjudication"] is False


def test_a_coder_flagging_uncertainty_forces_a_ruling():
    c2 = coding("c2", uncertain=True, uncertain_note="Methods names two tests")
    row = build_row("w1", META, {"c1": coding("c1"), "c2": c2})
    assert row["contested"] == ""
    assert row["needs_adjudication"] is True
    assert "c2: Methods names two tests" in row["uncertain_note"]


def test_flag_disagreement_is_contested_per_flag():
    c2 = copy.deepcopy(coding("c2"))
    c2["roles"]["r4"] = True
    c2["role_quotes"]["r4"] = "alpha of 0.75 — Measures"
    row = build_row("w1", META, {"c1": coding("c1"), "c2": c2})
    assert row["r4_final"] == ""
    assert row["contested"] == "r4"
    assert row["quote_r4"] == ""


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
