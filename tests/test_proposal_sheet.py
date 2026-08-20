"""Tests for the sheet the author rules from.

Two properties matter here and nothing else does. The sheet must print the
proposers' arguments whole, because the first version cut them at a fixed length
with no mark where the cut fell and a severed argument reads exactly like a
finished one. And each coder's value must be read from the pass that settled the
item, because the C flags were coded twice — once under rules the 2026-08-20
amendments replaced — and showing the superseded reading beside the current one
would put two protocols in a single line.
"""

from __future__ import annotations

import pandas as pd
import pytest

from make_proposal_sheet import check_nothing_was_cut, render
from test_classification import conflation, flags, gate

ROW = pd.Series(
    {
        "key": "w1",
        "doi": "10.1/x",
        "title": "A work",
        "work_venue_class": "journal_article",
    }
)

LONG = "The protocol decides this at §6, and the passage runs on. " * 40


def coders(flag_docs=None, conf_docs=None) -> dict[str, dict[str, dict]]:
    flag_docs = flag_docs or {c: flags(c) for c in ("c1", "c2")}
    conf_docs = conf_docs or {c: conflation(c) for c in ("c1", "c2")}
    return {
        c: {"gate": gate(c), "flags": flag_docs[c], "conf": conf_docs[c]}
        for c in ("c1", "c2")
    }


def proposal(**overrides) -> dict:
    doc = {
        "key": "w1",
        "protocol_gap": None,
        "notes": None,
        "rulings": [
            {
                "item": "c2",
                "proposed": True,
                "matches": "c2",
                "confidence": "high",
                "quote": "based on the MBTI — Methods",
                "reasoning": "the derivation predicate is asserted of the vendor's test",
            }
        ],
    }
    doc.update(overrides)
    return doc


# --- nothing is abridged --------------------------------------------------


def test_a_long_argument_is_printed_whole():
    doc = proposal(rulings=[proposal()["rulings"][0] | {"reasoning": LONG}])
    assert LONG in render(ROW, doc, coders())


def test_a_long_quote_is_printed_whole():
    doc = proposal(rulings=[proposal()["rulings"][0] | {"quote": LONG}])
    assert LONG in render(ROW, doc, coders())


def test_long_notes_are_printed_whole():
    assert LONG in render(ROW, proposal(notes=LONG), coders())


def test_a_long_protocol_gap_is_printed_whole():
    assert LONG in render(ROW, proposal(protocol_gap=LONG), coders())


def test_an_abridged_sheet_is_refused_rather_than_written():
    doc = proposal(rulings=[proposal()["rulings"][0] | {"reasoning": LONG}])
    abridged = render(ROW, doc, coders()).replace(LONG, LONG[:900])
    with pytest.raises(SystemExit, match="did not survive into the sheet whole"):
        check_nothing_was_cut(abridged, [doc])


def test_an_unabridged_sheet_passes_and_counts_what_it_checked():
    doc = proposal(protocol_gap=LONG, notes=LONG)
    assert check_nothing_was_cut(render(ROW, doc, coders()), [doc]) == 4


# --- the value shown is the one the settling pass holds --------------------


def test_a_c_flag_is_read_from_the_conflation_pass_not_the_flag_pass():
    """The flag pass's conflation codings predate the amendments (§12)."""
    superseded = {
        c: flags(c, conflation={"c0": True, "c1": False, "c2": False, "c3": False})
        for c in ("c1", "c2")
    }
    current = {
        c: conflation(c, conflation={"c0": False, "c1": True, "c2": True, "c3": False})
        for c in ("c1", "c2")
    }
    sheet = render(ROW, proposal(), coders(flag_docs=superseded, conf_docs=current))
    assert "c1 said `True`, c2 said `True`" in sheet


def test_an_r_flag_is_read_from_the_flag_pass():
    doc = proposal(rulings=[proposal()["rulings"][0] | {"item": "r1"}])
    split = {"c1": flags("c1"), "c2": flags("c2", roles={f"r{i}": False for i in range(1, 8)})}
    sheet = render(ROW, doc, coders(flag_docs=split))
    assert "c1 said `True`, c2 said `False`" in sheet


def test_the_coder_a_proposal_matches_is_named_apart_from_the_flag_names():
    """`c1`/`c2` name both a coder and a C flag; the sheet has to say which."""
    sheet = render(ROW, proposal(), coders())
    assert "matches **coder c2**" in sheet


def test_a_proposal_against_both_coders_says_so():
    sheet = render(ROW, proposal(rulings=[proposal()["rulings"][0] | {"matches": "neither"}]), coders())
    assert "matches **neither coder**" in sheet
