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
    validate_conflation,
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


def conflation(coder: str = "c1", **overrides) -> dict:
    doc = {
        "key": "w1",
        "coder": coder,
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


def flags(coder: str = "c1", **overrides) -> dict:
    """The second pass, which carries the roles and the conflation reading it replaced."""
    doc = conflation(coder) | {
        "roles": {f"r{i}": False for i in range(1, 8)} | {"r1": True},
        "role_quotes": {"r1": "the NERIS Type Explorer — Methods"},
    }
    doc.update(overrides)
    return doc


META = pd.Series(
    {"doi": "10.1/x", "title": "A work", "work_venue_class": "journal_article"}, name="w1"
)


def row_for(gate_docs=None, flag_docs=None, conf_docs=None) -> dict:
    gate_docs = gate_docs or {c: gate(c) for c in ("c1", "c2")}
    flag_docs = flag_docs or {c: flags(c) for c in ("c1", "c2")}
    conf_docs = conf_docs or {c: conflation(c) for c in ("c1", "c2")}
    return build_row("w1", META, gate_docs, flag_docs, conf_docs)


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


# --- conflation schema, the third pass ------------------------------------


def test_valid_conflation_passes():
    validate_conflation(conflation(), "w1", "c1")


def test_the_conflation_pass_carries_the_same_checks():
    doc = conflation()
    doc["conflation_narrow"]["c3"] = True
    with pytest.raises(SchemaError, match="narrow c3 set while wide c3 is not"):
        validate_conflation(doc, "w1", "c1")


def test_roles_in_the_conflation_pass_are_rejected_not_ignored():
    """A coder told not to code roles who codes them anyway must not be silently dropped."""
    doc = conflation() | {"roles": {f"r{i}": False for i in range(1, 8)}}
    with pytest.raises(SchemaError, match="must not carry"):
        validate_conflation(doc, "w1", "c1")


def test_a_conflation_file_missing_a_field_is_rejected():
    doc = conflation()
    del doc["states_distinction"]
    with pytest.raises(SchemaError, match="missing keys"):
        validate_conflation(doc, "w1", "c1")


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
    wide_only = copy.deepcopy(conflation("c1"))
    wide_only["conflation"] = {"c0": False, "c1": True, "c2": False, "c3": False}
    wide_only["conflation_quotes"] = {"c1": "the MBTI dimensions — Table 2"}
    both = copy.deepcopy(wide_only)
    both["coder"] = "c2"
    both["conflation_narrow"]["c1"] = True
    row = row_for(conf_docs={"c1": wide_only, "c2": both})
    assert row["c1_final"] is True
    assert row["narrow_c1_final"] == ""
    assert row["contested"] == "narrow_c1"


def test_third_party_conflation_is_recorded_but_never_contested():
    c2 = conflation(
        "c2", third_party_conflation=True, third_party_conflation_quote="Humanmetrics — §3.3"
    )
    row = row_for(conf_docs={"c1": conflation("c1"), "c2": c2})
    assert row["third_party_conflation_c2"] is True
    assert "third_party_conflation" not in row["contested"]
    assert "third_party_conflation_final" not in row
    assert row["needs_adjudication"] is False


def test_the_conflation_pass_supplies_the_c_flags_and_the_flag_pass_does_not():
    """The failure this exists to prevent: reading a C flag the amendments replaced.

    The second pass still holds conflation codings, made under the rules
    2026-08-20 replaced. They stay on disk as the reading they were; the row must
    come from the third pass.
    """
    stale = copy.deepcopy(flags("c1"))
    stale["conflation"] = {"c0": False, "c1": True, "c2": True, "c3": False}
    stale["conflation_quotes"] = {"c1": "under the old rule", "c2": "under the old rule"}

    row = row_for(flag_docs={"c1": stale, "c2": copy.deepcopy(stale) | {"coder": "c2"}})
    assert row["c1_final"] is False
    assert row["c2_final"] is False
    assert row["c0_final"] is True


def test_uncertainty_in_the_conflation_pass_forces_a_ruling():
    k = {
        "c1": conflation("c1"),
        "c2": conflation("c2", uncertain=True, uncertain_note="§6 chain undecided"),
    }
    row = row_for(conf_docs=k)
    assert row["contested"] == ""
    assert row["needs_adjudication"] is True
    assert "c2/conflation: §6 chain undecided" in row["uncertain_note"]


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


# --- rulings survive a rebuild --------------------------------------------


def test_a_ruling_fills_the_final_column_and_clears_the_dispute():
    """The failure this exists to prevent: a ruling erased by the next rebuild."""
    from build_classification import apply_rulings

    g = {"c1": gate("c1"), "c2": gate("c2", e_code="E2", instrument=None, instrument_quote=None)}
    row = row_for(gate_docs=g)
    assert row["needs_adjudication"] is True

    ruled = apply_rulings(row, {"e": ("E1", "Methods names the respondents")})
    assert ruled["e_final"] == "E1"
    assert ruled["adjudicated"] is True
    assert ruled["needs_adjudication"] is False
    assert "Methods names the respondents" in ruled["note"]


def test_a_partial_ruling_leaves_the_rest_contested():
    from build_classification import apply_rulings

    c2 = copy.deepcopy(flags("c2"))
    c2["roles"]["r7"] = True
    c2["role_quotes"]["r7"] = "the site is the corpus — Method"
    c2["roles"]["r2"] = True
    c2["role_quotes"]["r2"] = "cited for the dichotomies — Introduction"
    row = row_for(flag_docs={"c1": flags("c1"), "c2": c2})
    assert set(row["contested"].split(",")) == {"r2", "r7"}

    ruled = apply_rulings(row, {"r7": (True, "the vendor is the subject")})
    assert ruled["r7_final"] is True
    assert ruled["contested"] == "r2"
    assert ruled["needs_adjudication"] is True


def test_overruling_an_agreed_code_is_recorded_as_such():
    """§9 lets the author overrule a shared reading; silence would hide it."""
    from build_classification import apply_rulings

    row = row_for()
    assert row["r1_final"] is True
    ruled = apply_rulings(row, {"r1": (False, "the quote is from a neighbouring abstract")})
    assert ruled["r1_final"] is False
    assert "overruled agreement" in ruled["note"]


def test_a_ruling_on_an_unknown_item_is_rejected():
    from build_classification import apply_rulings

    with pytest.raises(SchemaError, match="no column for a ruling"):
        apply_rulings(row_for(), {"r9": (True, "typo in the item name")})


def test_every_item_the_sheet_offers_a_ruling_on_has_somewhere_to_land():
    """The failure this exists to prevent: a documented ruling that crashes the rebuild.

    The adjudication sheet lists the names the author may rule on. Two of them
    are published under a bare column name rather than `<item>_final` — §9's
    table names the settled sub-label and abstract test without a suffix — and a
    ruling on either raised SchemaError while the lookup assumed the suffix.
    """
    from build_classification import BOOLEAN_ITEMS, apply_rulings

    offered = (
        ["e", "instrument", "instrument_sublabel", "text_is_abstract", "states_distinction"]
        + [f"r{i}" for i in range(1, 8)]
        + [f"c{i}" for i in range(4)]
        + [f"narrow_c{i}" for i in range(1, 4)]
    )
    for item in offered:
        value = False if item in BOOLEAN_ITEMS else "c-translated"
        apply_rulings(row_for(), {item: (value, "the author read the text")})


def test_a_ruling_on_the_sublabel_lands_in_its_published_column():
    from build_classification import apply_rulings

    g = {
        c: gate(c, instrument="c", instrument_sublabel=sub)
        for c, sub in (("c1", "c-translated"), ("c2", "c-authormade"))
    }
    row = row_for(gate_docs=g)
    assert "instrument_sublabel" in row["contested"]

    ruled = apply_rulings(row, {"instrument_sublabel": ("c-translated", "a rendering, not a rewrite")})
    assert ruled["instrument_sublabel"] == "c-translated"
    assert "instrument_sublabel" not in ruled["contested"]


def test_a_ruling_on_the_abstract_test_lands_in_its_published_column():
    from build_classification import apply_rulings

    g = {
        "c1": gate("c1"),
        "c2": gate("c2", text_is_abstract=True, text_is_abstract_evidence="one page — Proceedings"),
    }
    row = row_for(gate_docs=g)
    assert "text_is_abstract" in row["contested"]

    ruled = apply_rulings(row, {"text_is_abstract": (False, "the retrieved file is the full article")})
    assert ruled["text_is_abstract"] is False
    assert ruled["needs_adjudication"] is False


def test_a_comma_in_the_reasoning_does_not_shift_the_columns(tmp_path, monkeypatch):
    """The failure this exists to prevent: prose eating the author's ruling.

    Reasoning is hand-typed free text and will contain commas. Read as a plain
    four-column CSV, the extra fields shifted the columns and the run died several
    steps later complaining about a ruling on a work that does not exist — a
    message that names neither the line nor the comma.
    """
    import build_classification as bc

    path = tmp_path / "adjudications.csv"
    path.write_text(
        "key,item,ruling,reasoning\n"
        "w1,r3,true,the note names Mind, Energy, Nature and Tactics, but cites nobody\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(bc, "RULINGS", path)

    rulings = bc.load_rulings()
    value, reasoning = rulings["w1"]["r3"]
    assert value is True
    assert reasoning == "the note names Mind, Energy, Nature and Tactics, but cites nobody"


def test_a_quoted_reasoning_field_is_read_the_same_way(tmp_path, monkeypatch):
    import build_classification as bc

    path = tmp_path / "adjudications.csv"
    path.write_text(
        'key,item,ruling,reasoning\nw1,c2,false,"names the MBTI\'s standing, not the vendor\'s"\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(bc, "RULINGS", path)
    assert bc.load_rulings()["w1"]["c2"][1] == "names the MBTI's standing, not the vendor's"


def test_a_short_ruling_row_is_named_by_line_number(tmp_path, monkeypatch):
    import build_classification as bc

    path = tmp_path / "adjudications.csv"
    path.write_text("key,item,ruling,reasoning\nw1,r3,true\n", encoding="utf-8")
    monkeypatch.setattr(bc, "RULINGS", path)
    with pytest.raises(SchemaError, match="line 2: needs four fields"):
        bc.load_rulings()


def test_a_wrong_ruling_header_says_what_it_wanted(tmp_path, monkeypatch):
    import build_classification as bc

    path = tmp_path / "adjudications.csv"
    path.write_text("work,flag,value,why\nw1,r3,true,because\n", encoding="utf-8")
    monkeypatch.setattr(bc, "RULINGS", path)
    with pytest.raises(SchemaError, match="must be exactly"):
        bc.load_rulings()


def test_boolean_rulings_are_parsed_and_bad_ones_rejected():
    from build_classification import parse_ruling

    assert parse_ruling("r4", "true") is True
    assert parse_ruling("c2", "FALSE") is False
    assert parse_ruling("e", "E1") == "E1"
    with pytest.raises(SchemaError, match="must be true or false"):
        parse_ruling("r4", "maybe")
