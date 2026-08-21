"""Tests for the page the author rules from.

Four properties matter. The page must print every verbatim whole, for the same
reason the markdown sheet must: a severed argument reads exactly like a finished
one, and the author cannot tell them apart. It must not carry a ruling of its
own, because §9 reserves the ruling for the author — the proposal is a third
reading beside the two codings, and taking it is something the author does. It
must not offer a field a newline can be typed into, because the CSV is read
line by line and a broken line becomes a row that is not a ruling. And it must
escape what it quotes, since the verbatim comes from third-party text that the
page has no reason to trust as markup.
"""

from __future__ import annotations

import pandas as pd
import pytest

from make_ruling_html import check_nothing_was_cut, render_work
from test_classification import conflation, flags, gate

# Stripped, because a quote is stored without its surrounding whitespace.
LONG = ("The protocol decides this at §6, and the passage runs on. " * 40).strip()


def row(**overrides) -> pd.Series:
    doc = {
        "key": "w1",
        "doi": "10.1/x",
        "title": "A work",
        "work_venue_class": "journal_article",
        "contested": "c2",
        "uncertain_by": None,
    }
    doc.update(overrides)
    return pd.Series(doc)


def codings(gate_docs=None, flag_docs=None, conf_docs=None) -> dict:
    gate_docs = gate_docs or {c: gate(c) for c in ("c1", "c2")}
    flag_docs = flag_docs or {c: flags(c) for c in ("c1", "c2")}
    conf_docs = conf_docs or {c: conflation(c) for c in ("c1", "c2")}
    return {
        c: {"gate": gate_docs[c], "flags": flag_docs[c], "conflation": conf_docs[c]}
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


def page(work_row=None, docs=None, doc=None) -> str:
    html, _ = render_work(
        1,
        row() if work_row is None else work_row,
        codings() if docs is None else docs,
        proposal() if doc is None else doc,
    )
    return html


def quoted(value) -> dict:
    return codings(
        conf_docs={c: conflation(c, conflation_quotes={"c2": value}) for c in ("c1", "c2")}
    )


# --- nothing is abridged --------------------------------------------------


def test_a_long_argument_is_printed_whole():
    doc = proposal(rulings=[proposal()["rulings"][0] | {"reasoning": LONG}])
    assert LONG in page(doc=doc)


def test_a_long_proposal_quote_is_printed_whole():
    doc = proposal(rulings=[proposal()["rulings"][0] | {"quote": LONG}])
    assert LONG in page(doc=doc)


def test_a_long_protocol_gap_is_printed_whole():
    assert LONG in page(doc=proposal(protocol_gap=LONG))


def test_a_long_uncertain_note_is_printed_whole():
    docs = codings(conf_docs={c: conflation(c, uncertain_note=LONG) for c in ("c1", "c2")})
    assert LONG in page(work_row=row(uncertain_by="c2:conflation"), docs=docs)


def test_long_free_text_is_printed_whole():
    docs = codings(gate_docs={c: gate(c, free_text=LONG) for c in ("c1", "c2")})
    assert LONG in page(docs=docs)


def test_an_abridged_page_is_refused_rather_than_written():
    doc = proposal(rulings=[proposal()["rulings"][0] | {"reasoning": LONG}])
    html, verbatim = render_work(1, row(), codings(), doc)
    with pytest.raises(SystemExit, match="did not survive into the page whole"):
        check_nothing_was_cut(html.replace(LONG, LONG[:600]), verbatim)


def test_an_unabridged_page_passes_and_counts_what_it_checked():
    doc = proposal(protocol_gap=LONG, notes=LONG)
    html, verbatim = render_work(1, row(), quoted(LONG), doc)
    # both coders' quotes, the proposal's quote and argument, the gap, the notes
    assert check_nothing_was_cut(html, verbatim) == 6


# --- the three shapes a quote came in read as one -------------------------


def test_a_quote_given_as_an_object_reads_as_a_sentence_rather_than_as_json():
    html = page(docs=quoted({"quote": "based on the MBTI", "section": "Methods 2.1"}))
    assert "based on the MBTI — Methods 2.1" in html
    assert '{"quote"' not in html


def test_both_halves_of_an_object_quote_must_survive():
    html, verbatim = render_work(1, row(), quoted({"quote": LONG, "section": "Methods"}), proposal())
    with pytest.raises(SystemExit, match="did not survive into the page whole"):
        check_nothing_was_cut(html.replace(LONG, LONG[:600]), verbatim)


def test_a_chain_of_quotes_is_shown_whole():
    """§6 asks for every link of a cross-sentence chain."""
    html = page(docs=quoted(["named as one — Methods", {"quote": "based on Jung", "section": "Intro"}]))
    assert "named as one — Methods || based on Jung — Intro" in html


def test_an_unset_flag_says_so_rather_than_showing_an_empty_line():
    assert "引用なし" in page(docs=quoted(None))


# --- §9: the page offers readings and holds no ruling ---------------------


def test_the_page_carries_no_ruling_of_its_own():
    """Taking a reading is a button press, not a state the page arrives in."""
    html = page()
    assert "checked" not in html
    assert 'value="' not in html.replace('data-value="', "")


def test_each_of_the_three_readings_can_be_taken():
    html = page()
    assert html.count(">これに決める</button>") == 3  # c1, c2, proposal


def test_an_item_with_no_proposal_offers_only_the_two_codings():
    html = page(doc=proposal(rulings=[]))
    assert html.count(">これに決める</button>") == 2
    assert "提案 —" not in html


def test_the_empty_sub_label_can_be_taken_where_the_protocol_wants_one():
    """§3.4 wants the sub-label empty, which an author cannot type."""
    doc = proposal(rulings=[proposal()["rulings"][0] | {"item": "instrument_sublabel"}])
    assert "空欄に決める" in page(work_row=row(contested="instrument_sublabel"), doc=doc)
    assert "空欄に決める" not in page()


# --- the CSV cannot be corrupted from here --------------------------------


def test_the_reason_is_a_single_line_field():
    """A newline in a reason splits one ruling into two rows in the CSV."""
    assert "<textarea" not in page()


def test_a_work_whose_codes_all_agree_asks_for_no_ruling():
    html = page(work_row=row(contested=None, uncertain_by="c2:flags"))
    assert ">これに決める</button>" not in html
    assert "変えたいときだけ行を書く" in html


# --- third-party text is escaped ------------------------------------------


def test_markup_in_a_quote_does_not_reach_the_page_as_markup():
    hostile = '<script>alert("x")</script>'
    html = page(docs=quoted(hostile))
    assert hostile not in html
    assert "&lt;script&gt;" in html


# --- each value comes from the pass that settled it -----------------------


def test_a_c_flag_is_read_from_the_conflation_pass_not_the_flag_pass():
    """The flag pass's conflation codings predate the amendments (§12)."""
    superseded = {
        c: flags(c, conflation={"c0": True, "c1": False, "c2": False, "c3": False})
        for c in ("c1", "c2")
    }
    current = {
        c: conflation(c, conflation={"c0": False, "c1": False, "c2": True, "c3": False})
        for c in ("c1", "c2")
    }
    html = page(docs=codings(flag_docs=superseded, conf_docs=current))
    assert 'data-value="True"' in html
    assert 'data-value="False"' not in html


def test_an_r_flag_is_read_from_the_flag_pass():
    split = {"c1": flags("c1"), "c2": flags("c2", roles={f"r{i}": False for i in range(1, 8)})}
    doc = proposal(rulings=[proposal()["rulings"][0] | {"item": "r1"}])
    html = page(work_row=row(contested="r1"), docs=codings(flag_docs=split), doc=doc)
    assert 'data-value="True"' in html and 'data-value="False"' in html


def test_the_coder_a_proposal_matches_is_named_apart_from_the_flag_names():
    """`c1`/`c2` name both a coder and a C flag; the page has to say which."""
    assert "AI-2 と同じ" in page()


def test_a_proposal_against_both_coders_says_so():
    doc = proposal(rulings=[proposal()["rulings"][0] | {"matches": "neither"}])
    assert "どちらの AI も間違い" in page(doc=doc)
