"""Compute §10's planned reporting and §11's sensitivity arms from the coded corpus.

§10 of `data/coding_protocol.md` fixed what this study reports before any count
existed, and §11 fixed the arms so that running one later could not be a way of
looking for a better number. This script is where those commitments are cashed.
Everything it prints was named in the protocol; nothing it prints was chosen
after a figure was seen.

Three properties of the design decide how it is written.

**The branch is code, not a judgement.** §10's table maps a result to a claim,
and the mapping is evaluated here by `pattern()` rather than by a person reading
the output. §12's amendment of 2026-08-22 supplies the two precedences the table
omits — P5 over P1-P4 on a small `n1`, P4 over P3 on a (b)/(c) tie — both of
which were written and tested before the first count was computed, because after
it neither could have been settled honestly.

**Only §10's measures and §11's arms carry a rate.** The protocol asks elsewhere
for quantities to be reported without saying in what form — §3.4's sub-labels,
§6's `states_distinction`, §1's two kinds of absence — and §6 expressly refuses a
rate to two of them. Those are counted here against a stated denominator and are
kept out of `proportions`, so that no figure §10 did not name can acquire a
confidence interval later. §12 records the rule.

**The finals are the one thing a person edited.** `build_classification.py`
validates the coders' JSON; nothing until now has validated the columns the
author's rulings write to. `check()` does it, because a blank or contradictory
final would not raise here — it would quietly leave a work out of a numerator.

Wilson intervals are computed in this file from the normal quantile rather than
taken from scipy or statsmodels. Both are installed and neither is in
`requirements.txt`, so a reader who installed what the repository declares could
not reproduce a figure that depended on them; the formula is four lines and
`tests/test_aggregate.py` checks it against published values and, where the
library is present, against statsmodels itself.

Outputs
    data/results.json  every figure the manuscript reports, published
    stdout             the same, laid out to be read
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CLASSIFICATION = ROOT / "data" / "classification.csv"
CORPUS = ROOT / "data" / "corpus.csv"
LOG = ROOT / "data" / "fulltext_log.csv"
QUERY_LOG = ROOT / "data" / "query_log.json"
OUT = ROOT / "data" / "results.json"

# The 0.975 quantile of the standard normal. Written out rather than imported so
# that the interval depends on nothing outside requirements.txt.
Z95 = 1.959963984540054

MAIN_VENUES = ("journal_article",)
INSTRUMENTS = ("a", "b", "c")
R_FLAGS = ("r1", "r2", "r3", "r4", "r5", "r6", "r7")
C_FLAGS = ("c1", "c2", "c3")
NARROW_C_FLAGS = ("narrow_c1", "narrow_c2", "narrow_c3")

# §7's three calibration records and the codes it expected of them, written
# before coding from verbatim already verified against the sources. Where §7 left
# a cell open — "not pre-judged", "to be coded" — nothing is expected and the
# coded value is reported without a verdict. §10 fixes that the manuscript states
# in Methods how many of the three fall outside the main analysis, so it is
# computed rather than repeated from §7's prose.
CALIBRATION = {
    "10.1038/s41598-025-91361-w": {
        "name": "Bai et al. 2025",
        "e": "E1",
        "instrument": "a",
        "r": ("r1", "r4"),
    },
    "10.4992/pacjpa.89.0_423": {
        "name": "Koshiro et al. 2025",
        "c": ("c1", "c2"),
    },
    "10.3389/fncom.2026.1800284": {
        "name": "Tshimula et al. 2026",
        "e": "E4",
        "instrument": "",
        "r": ("r6",),
        "c": ("c1", "c3"),
    },
}

PATTERNS = {
    # §10's promised wording, quoted character for character from the table in
    # `data/coding_protocol.md`; `tests/test_aggregate.py` compares them raw and fails
    # on a single changed character. An earlier version paraphrased three of the five,
    # which made the pre-commitment read better than it was: P3 lost "of papers
    # reporting MBTI results", the population claim this study retracted.
    # The manuscript departs from P1 — only 2026 vendor pages were ever retrieved, so
    # non-identity at the date each coded paper was written is not established. The
    # departure is carried in `pattern.headline_departed_from` below, not by editing this.
    'P1': ('M1', '"X% (95% CI …) administered an instrument that is not the MBTI"'),
    'P2': ('M1', 'Same figure, stated as imprecise: "X%, though the interval is wide (95% CI …)". The word *substantial* is not used.'),
    'P3': ('M1, framed on (c)', '"X% of papers reporting MBTI results do not identify the instrument they administered" — a reporting failure, not a substitution one'),
    'P4': ('M2', 'Attribution in administration is mostly accurate; the claim moves to citation practice and conflation, and the (a) cases are reported as a case series'),
    'P5': ('M2', 'No headline rate from M1. M1 is reported descriptively with its interval and explicitly called imprecise'),
}


class ResultsError(ValueError):
    """The coded corpus does not carry what the reporting rules require of it."""


def wilson(k: int, n: int, z: float = Z95) -> tuple[float, float]:
    """The Wilson score interval for k successes in n trials.

    Wilson rather than Wald because several of these proportions sit near 0 or 1
    on denominators in the tens, where Wald returns bounds outside [0, 1] and
    covers below its nominal rate. §10 names the interval and not the method;
    this is the standard choice for that shape and it is fixed here.
    """
    if n <= 0:
        raise ResultsError("a proportion needs a denominator")
    if not 0 <= k <= n:
        raise ResultsError(f"{k} successes in {n} trials")
    p = k / n
    denominator = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denominator
    half = z / denominator * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return max(0.0, centre - half), min(1.0, centre + half)


def proportion(k: int, n: int) -> dict:
    low, high = wilson(k, n)
    return {
        "k": int(k),
        "n": int(n),
        "p": round(k / n, 4),
        "ci_low": round(low, 4),
        "ci_high": round(high, 4),
    }


def booleans(frame: pd.DataFrame, column: str) -> pd.Series:
    """Read a final flag column, refusing anything that is not a settled boolean.

    A blank final is the failure this guards: it means the coders split and no
    ruling landed, and read as false it would leave the work out of a numerator
    while keeping it in the denominator — a disagreement counted as an absence.
    """

    def one(value):
        if isinstance(value, bool):
            return value
        text = str(value).strip().lower()
        if text in {"true", "false"}:
            return text == "true"
        raise ResultsError(
            f"{column}: {value!r} is neither true nor false — the column is "
            "unsettled and cannot be counted"
        )

    return frame[column].map(one)


def any_of(frame: pd.DataFrame, flags: tuple[str, ...]) -> pd.Series:
    """True where any of the named flags is set, read from their final columns."""
    combined = booleans(frame, f"{flags[0]}_final")
    for flag in flags[1:]:
        combined = combined | booleans(frame, f"{flag}_final")
    return combined


def work_key(base: str) -> str:
    """`fetch_fulltext.work_key`, repeated so a work can be traced to its records."""
    return re.sub(r"[^a-z0-9]+", "_", str(base).lower()).strip("_")[:100]


def sources_by_key(corpus: pd.DataFrame, keys: set[str]) -> dict[str, tuple[str, ...]]:
    """Which databases returned each work, for S4.

    `corpus.csv` keys works by `dup_group` and the coded files key them by the
    slug of a DOI, so the join runs through the keys a group's records would
    produce. Twelve records carry no DOI and are keyed on their source id, which
    a DOI-only join would drop.
    """
    found: dict[str, tuple[str, ...]] = {}
    for _, group in corpus.groupby("dup_group"):
        candidates = {work_key(row["doi"] or row["source_id"]) for _, row in group.iterrows()}
        matched = candidates & keys
        if not matched:
            continue
        if len(matched) > 1:
            raise ResultsError(f"one work matched several coded keys: {sorted(matched)}")
        found[matched.pop()] = tuple(sorted(set(group["source_db"])))
    missing = keys - set(found)
    if missing:
        raise ResultsError(f"coded works absent from the corpus: {sorted(missing)}")
    return found


def check(coded: pd.DataFrame, log: pd.DataFrame) -> None:
    """Refuse to count a corpus whose settled columns contradict the protocol."""
    expected = int((log["status"] == "ok").sum())
    if len(coded) != expected:
        raise ResultsError(f"{len(coded)} coded works against {expected} with status ok")

    pending = booleans(coded, "needs_adjudication")
    if pending.any():
        raise ResultsError(
            f"{int(pending.sum())} works still await a ruling; §9 reserves it for the author"
        )

    if (coded["e_final"] == "").any():
        raise ResultsError("a work carries no settled E code")
    unknown = set(coded["e_final"]) - {"E1", "E2", "E3", "E4"}
    if unknown:
        raise ResultsError(f"unknown E codes: {sorted(unknown)}")

    is_e1 = coded["e_final"] == "E1"
    coded_instrument = coded["instrument_final"] != ""
    # §2: only E1 works receive an instrument code, and every E1 work has one.
    # Compared elementwise rather than with Series.equals, which also weighs the
    # name and the dtype and would pass or fail for reasons unrelated to the codes.
    if (is_e1 != coded_instrument).any():
        raise ResultsError("instrument codes and the E1 gate disagree about which works carry one")
    bad = set(coded.loc[is_e1, "instrument_final"]) - set(INSTRUMENTS)
    if bad:
        raise ResultsError(f"unknown instrument codes: {sorted(bad)}")

    # §3.4: a sub-label records the shape of a (c), and nothing else takes one.
    stray = coded[(coded["instrument_sublabel"] != "") & (coded["instrument_final"] != "c")]
    if len(stray):
        raise ResultsError(f"sub-labels on non-(c) works: {stray['key'].tolist()}")

    # §6: C0 is true exactly when C1-C3 are all false, and the narrow reading is
    # a subset of the wide one. Either failing would let S7 report more
    # conflation than the main analysis does.
    if (booleans(coded, "c0_final") != ~any_of(coded, C_FLAGS)).any():
        raise ResultsError("c0_final is not the complement of C1-C3")
    for wide, narrow in zip(C_FLAGS, NARROW_C_FLAGS):
        broken = booleans(coded, f"{narrow}_final") & ~booleans(coded, f"{wide}_final")
        if broken.any():
            raise ResultsError(f"{narrow} set where {wide} is not: {coded.loc[broken, 'key'].tolist()}")


def measures(coded: pd.DataFrame, main_venues: tuple[str, ...], instrument: pd.Series,
             c_flags: tuple[str, ...]) -> dict:
    """M1 over the E1 works of the main analysis, M2 over every coded work.

    The arms of §11 vary exactly three things — which works are in scope, which
    venue classes the main analysis holds, and how a code reads — so all three
    are arguments and the two measures are computed once.
    """
    main = coded[coded["work_venue_class"].isin(main_venues)]
    e1 = main[main["e_final"] == "E1"]
    n1 = len(e1)

    m1: dict = {
        "n1": n1,
        "denominators": {
            "e1_works_in_main_analysis": n1,
            "works_in_main_analysis": len(main),
            "coded_works": len(coded),
        },
    }
    if n1:
        codes = instrument.loc[e1.index]
        m1["distribution"] = {c: proportion(int((codes == c).sum()), n1) for c in INSTRUMENTS}
    else:
        m1["distribution"] = None
        m1["note"] = "no E1 work in the main analysis; M1 is not computable on this arm"

    n2 = len(coded)
    m2 = {
        "n": n2,
        "r4": proportion(int(booleans(coded, "r4_final").sum()), n2),
        # Schema key, not a claim: the manuscript reports this union as "the share
        # carrying any pre-defined C1-C3 flag" and states plainly that it is not a
        # rate of conflation, because C3 alone is a claim of standing this study
        # does not adjudicate. The key is left unrenamed so that a reader's saved
        # path keeps working; `any_conflation_note` says what it counts.
        "any_conflation": proportion(int(any_of(coded, c_flags).sum()), n2),
        "any_conflation_note": (
            "share carrying at least one pre-defined C1-C3 flag; not a rate of "
            "conflation - C2 and C3 are counted and not adjudicated"
        ),
        "conflation_flags": list(c_flags),
    }
    return {"m1": m1, "m2": m2}


def pattern(m1: dict) -> dict:
    """§10's table, with the two precedences §12 settled on 2026-08-22.

    Evaluated from the numbers rather than chosen after reading them, which is
    the single commitment §10 exists to enforce.
    """
    n1 = m1["n1"]
    if n1 < 20:
        return _pattern("P5", f"n1 = {n1} < 20; §12 (2026-08-22) gives P5 precedence over P1-P4")

    distribution = m1["distribution"]
    # Recomputed from the counts rather than read from `p` and `ci_low`, which are
    # rounded to four places for reporting. A bound of 0.09996 reads as 0.1000
    # rounded and would take P1 on a threshold it does not actually clear; the
    # branch is the one place in this study where that must not happen.
    k_a, n_a = distribution["a"]["k"], distribution["a"]["n"]
    p_a = k_a / n_a
    l_a = wilson(k_a, n_a)[0]
    if l_a >= 0.10:
        return _pattern("P1", f"L_a = {l_a:.4f} >= 0.10")
    if p_a >= 0.10:
        return _pattern("P2", f"p_a = {p_a:.4f} >= 0.10 > L_a = {l_a:.4f}")

    largest = max(("b", "c"), key=lambda code: distribution[code]["k"])
    if distribution["b"]["k"] == distribution["c"]["k"]:
        return _pattern("P4", f"p_a = {p_a:.4f} < 0.10 and (b) ties (c) as the largest category; §12 (2026-08-22) gives P4 the tie")
    return _pattern(
        "P3" if largest == "c" else "P4",
        f"p_a = {p_a:.4f} < 0.10 and ({largest}) is the largest instrument category",
    )


def _pattern(name: str, reason: str) -> dict:
    leads_with, wording = PATTERNS[name]
    return {
        "pattern": name,
        "reason": reason,
        "abstract_leads_with": leads_with,
        "headline_wording": wording,
        # §10 promised the wording above before any count existed, so it is kept
        # verbatim: editing a pre-commitment destroys the only property that makes
        # it evidence. The manuscript does not make that claim. Both vendor pages
        # were retrieved in 2026, so non-identity at the date each coded paper was
        # written is not established, and P1's wording asserts it. A reader who
        # opens this file rather than the paper needs to be told that here.
        "headline_departed_from": name == "P1",
        "headline_as_reported": (
            "X% (model-based Wilson 95% interval ...) administered a vendor-hosted test "
            "from which no published MBTI form was identifiable"
        ) if name == "P1" else None,
    }


def sensitivity(coded: pd.DataFrame, instrument: pd.Series, sources: dict[str, tuple[str, ...]],
                query_log: dict, venue_counts: dict[str, int]) -> dict:
    """§11's seven arms, all reported whether or not they change the conclusion."""
    arms: dict[str, dict] = {}

    arms["S1"] = {
        "arm": "include conference and conference_abstract in the denominator",
        **measures(coded, MAIN_VENUES + ("conference", "conference_abstract"), instrument, C_FLAGS),
        "note": (
            "denominator re-counted from corpus.csv, not from query_log.json, whose "
            "venue_class_counts_all_rows was left behind by the 2026-08-19 duplicate fix: "
            f"{venue_counts.get('journal_article', 0)} journal_article, "
            f"{venue_counts.get('conference', 0)} conference, "
            f"{venue_counts.get('conference_abstract', 0)} conference_abstract among the 99 works"
        ),
    }

    unclassified = coded[coded["work_venue_class"] == "unclassified"]
    # S2 only *ran* if the record it adds carries a code. It does not: §8 undertook
    # to code the venue-less work in full, and its full text was never retrieved.
    # Reporting the arm at the main-analysis values said "including it changed
    # nothing", which asserts a result the arm never produced — and the figure drew
    # it beside the arms that did run, with a point and an interval. An arm whose
    # input was never obtained is not estimable, and is now reported as such.
    arms["S2"] = (
        {
            "arm": "include the unclassified record (§8)",
            "m1": None,
            "m2": None,
            "note": "not estimable: §8 planned to code the record in full, but its full "
                    "text was never retrieved (status no_url in fulltext_log.csv), so §1 "
                    "leaves it unobtainable and it carries no code to add. The arm has no "
                    "result — not a result equal to the main analysis",
        }
        if unclassified.empty
        else {
            "arm": "include the unclassified record (§8)",
            **measures(coded, MAIN_VENUES + ("unclassified",), instrument, C_FLAGS),
            "note": f"{len(unclassified)} unclassified work(s) added",
        }
    )

    vendor_only = (instrument == "c") & (coded["instrument_sublabel"] == "c-vendor-cited-only")
    arms["S3"] = {
        "arm": "count c-vendor-cited-only works as (a) — the PLAN's original boundary rule (§4.1)",
        **measures(coded, MAIN_VENUES, instrument.mask(vendor_only, "a"), C_FLAGS),
        "note": (
            f"{int(vendor_only.sum())} coded work(s) re-read as (a), of which "
            f"{int((vendor_only & coded['work_venue_class'].isin(MAIN_VENUES)).sum())} "
            "sit in the main analysis — an arm that moves M1 by fewer works than it "
            "re-reads has found the shape outside the denominator, not failed to run"
        ),
    }

    openalex = coded[coded["key"].map(lambda k: "openalex" in sources[k])]
    arms["S4"] = {
        "arm": "OpenAlex-only versus both sources",
        **measures(openalex, MAIN_VENUES, instrument.loc[openalex.index], C_FLAGS),
        "note": (
            f"{len(openalex)} of {len(coded)} coded works are in OpenAlex; Europe PMC "
            "contributed no work OpenAlex did not already hold, so §10 reports it as "
            "independent confirmation of the frame rather than as a second frame"
        ),
    }

    variants = query_log["variant_sensitivity"]
    arms["S5"] = {
        "arm": 'the widening word-form variant "Type Explorer"',
        "m1": None,
        "m2": None,
        "note": (
            f"reported as a bound, not a recount: the variant takes the OpenAlex "
            f"intersection from {variants['openalex_primary']} records to "
            f"{variants['openalex_with_type_explorer']} and Europe PMC from "
            f"{variants['europepmc_primary']} to {variants['europepmc_with_type_explorer']}. "
            "The added record is not among corpus.csv's 118 rows, so it was never retrieved "
            "and carries no code; the arm bounds the effect at one record, at most one work, "
            "against a frame of 99 (§12, 2026-08-22)"
        ),
    }

    article = coded[~booleans(coded, "text_is_abstract")]
    arms["S6"] = {
        "arm": "exclude records whose retrieved text is a conference abstract (§3.6)",
        **measures(article, MAIN_VENUES, instrument.loc[article.index], C_FLAGS),
        "note": f"{len(coded) - len(article)} of {len(coded)} coded works excluded",
    }

    arms["S7"] = {
        "arm": "pre-defined C flags on the narrow reading — works that name the vendor's test or site",
        **measures(coded, MAIN_VENUES, instrument, NARROW_C_FLAGS),
        "note": (
            "M1 is untouched: the narrow reading is a rule about §6's flags. The stopping "
            "rule of §12 did not fire at the third round, so the wide reading remains the "
            "main analysis and this is the arm"
        ),
    }
    return arms


def descriptive(coded: pd.DataFrame, log: pd.DataFrame, venue_counts: dict[str, int]) -> dict:
    """Everything the protocol asks to be reported without a rate (§12, 2026-08-22)."""
    statuses = log["status"].value_counts().to_dict()
    unobtainable = {k: int(v) for k, v in statuses.items() if k not in {"ok", "no_word_form"}}
    is_c = coded["instrument_final"] == "c"

    # The main-analysis frame separately, because "not coded" and "not retrieved"
    # differ there too and the flow figure annotates that step.
    journal = log[log["work_venue_class"] == "journal_article"]
    journal_statuses = journal["status"].value_counts().to_dict()
    journal_unobtainable = {k: int(v) for k, v in journal_statuses.items()
                            if k not in {"ok", "no_word_form"}}

    return {
        "retrieval": {
            "works": len(log),
            "coded": int(statuses.get("ok", 0)),
            "unobtainable": {"total": sum(unobtainable.values()), "by_reason": unobtainable},
            "no_word_form": {
                "count": int(statuses.get("no_word_form", 0)),
                "checkable_works": int(statuses.get("ok", 0)) + int(statuses.get("no_word_form", 0)),
                "note": "§1 reports this as an upper bound on how often the search index "
                        "matched a text not containing the term; the rate is §1's own",
            },
            "journal_articles": {
                "in_frame": len(journal),
                "coded": int(journal_statuses.get("ok", 0)),
                "no_word_form": int(journal_statuses.get("no_word_form", 0)),
                "unobtainable": sum(journal_unobtainable.values()),
            },
        },
        "venue_class_of_the_99_works": venue_counts,
        "venue_class_of_the_coded_works": coded["work_venue_class"].value_counts().to_dict(),
        "e_gate": coded["e_final"].value_counts().to_dict(),
        "instrument_sublabels_among_c": coded.loc[is_c, "instrument_sublabel"].replace("", "(none)").value_counts().to_dict(),
        "role_flags": {flag.upper(): int(booleans(coded, f"{flag}_final").sum()) for flag in R_FLAGS},
        "conflation_flags": {
            **{flag.upper(): int(booleans(coded, f"{flag}_final").sum()) for flag in ("c0",) + C_FLAGS},
            **{flag: int(booleans(coded, f"{flag}_final").sum()) for flag in NARROW_C_FLAGS},
        },
        "states_distinction": int(booleans(coded, "states_distinction_final").sum()),
        "third_party_conflation": {
            "count": int((booleans(coded, "third_party_conflation_c1") | booleans(coded, "third_party_conflation_c2")).sum()),
            "note": "§6 records this shape and refuses it a rate: the corpus is built from "
                    "16Personalities word forms, so a proportion over it would have no denominator",
        },
        "text_is_abstract": int(booleans(coded, "text_is_abstract").sum()),
    }


def post_hoc(coded: pd.DataFrame, instrument: pd.Series) -> dict:
    """The pre-defined C flags of the main analysis, cross-tabulated by instrument code.

    **Nothing here was planned.** §10 named M1 and M2 and §12 closed the list on
    2026-08-22; this block was added on 2026-08-25, after every count existed, and
    §12 records it as an amendment with the reason. It answers a question M1 does
    not: M1 reports which instrument each work administered, and says nothing
    about whether the work attributed that instrument correctly. The C flags do,
    and they were coded twice, scored and adjudicated before any of this was
    computed — so the cross-tabulation reads columns that were already settled
    rather than coding anything again.

    It is reported as counts against a stated denominator and carries no interval,
    which is the form §12 fixed for every quantity outside M1, M2 and the arms.
    The distinction matters more here than elsewhere precisely because this is the
    figure a reader is most likely to want promoted to a rate.
    """
    main = coded[coded["work_venue_class"].isin(MAIN_VENUES) & (coded["e_final"] == "E1")]
    by_code: dict[str, dict] = {}
    for code in INSTRUMENTS:
        rows = main[instrument.loc[main.index] == code]
        if rows.empty:
            by_code[code] = {"works": 0}
            continue
        c1 = booleans(rows, "c1_final")
        c2 = booleans(rows, "c2_final")
        c3 = booleans(rows, "c3_final")
        by_code[code] = {
            "works": len(rows),
            "c1_identity": int(c1.sum()),
            "c2_provenance": int(c2.sum()),
            "c3_authority": int(c3.sum()),
            "c1_or_c2": int((c1 | c2).sum()),
            # The union over all three, which is what M2 rates across the whole
            # corpus. Without it the block did not add up: C1∪C2 plus C0 left one
            # (a) work unaccounted for, because C0 is defined against C1-C3 and
            # that work carries C3 alone. Reported here so the column closes.
            "any_conflation": int((c1 | c2 | c3).sum()),
            "c0_no_conflating_statement": int(booleans(rows, "c0_final").sum()),
            "states_distinction": int(booleans(rows, "states_distinction_final").sum()),
        }
        counted = by_code[code]["any_conflation"] + by_code[code]["c0_no_conflating_statement"]
        if counted != len(rows):
            raise ResultsError(
                f"the C flags of instrument code ({code}) do not partition its "
                f"{len(rows)} works: {by_code[code]['any_conflation']} carry a flag and "
                f"{by_code[code]['c0_no_conflating_statement']} carry C0, totalling {counted}"
            )
    return {
        "planned": False,
        "added": "2026-08-25",
        "form": "exploratory, post hoc descriptive proportions; no model-based interval",
        "form_note": "an earlier value of this field read 'counts against a stated "
                     "denominator; no proportion, no interval'. That defence was withdrawn on "
                     "2026-08-25: 'sixteen of seventeen' is a proportion however it is printed. "
                     "See the manuscript's departures table and the protocol at §12.",
        "why": "M1 measures what was administered, not whether the work attributed it "
               "correctly. The manuscript had read M1 as the second quantity; it is not. "
               "These columns carry the attribution and were settled before this was computed.",
        "denominator": "E1 works in the main analysis, split by instrument code",
        "by_instrument_code": by_code,
    }


def calibration(coded: pd.DataFrame) -> dict:
    """Where §7's three records sit, and whether the pipeline reproduced them.

    "Outside the main analysis" is read as §7 reads it — the record contributes
    nothing to M1 — and not as venue class alone. Tshimula is a `journal_article`
    and still outside, because it administers nothing and so takes no instrument
    code; counting on venue would report one record outside where §7, and §10's
    Methods statement after it, say two.
    """
    records: dict[str, dict] = {}
    for doi, expected in CALIBRATION.items():
        name = expected["name"]
        row = coded[coded["doi"].str.lower() == doi.lower()]
        if row.empty:
            records[name] = {"doi": doi, "coded": False, "contributes_to_m1": False}
            continue
        record = row.iloc[0]
        actual = {
            "e": record["e_final"],
            "instrument": record["instrument_final"],
            "r": tuple(f for f in R_FLAGS if booleans(row, f"{f}_final").iloc[0]),
            "c": tuple(f for f in C_FLAGS if booleans(row, f"{f}_final").iloc[0]),
        }
        checks = {
            field: {"expected": expected[field], "actual": actual[field],
                    "reproduced": expected[field] == actual[field]}
            for field in ("e", "instrument", "r", "c")
            if field in expected
        }
        records[name] = {
            "doi": doi,
            "coded": True,
            "venue_class": record["work_venue_class"],
            "contributes_to_m1": record["work_venue_class"] in MAIN_VENUES and record["e_final"] == "E1",
            "coded_as": actual,
            "expected_by_section_7": checks,
            "reproduced": all(c["reproduced"] for c in checks.values()),
        }
    return {
        "records": records,
        "outside_main_analysis": sum(1 for r in records.values() if not r["contributes_to_m1"]),
        "all_reproduced": all(r.get("reproduced", False) for r in records.values()),
    }


def build() -> dict:
    coded = pd.read_csv(CLASSIFICATION, keep_default_na=False, dtype=str)
    log = pd.read_csv(LOG, keep_default_na=False)
    corpus = pd.read_csv(CORPUS, keep_default_na=False)
    query_log = json.loads(QUERY_LOG.read_text(encoding="utf-8"))

    check(coded, log)

    venue_counts = (
        corpus.drop_duplicates("dup_group")["work_venue_class"].value_counts().to_dict()
    )
    declared = query_log["venue_class_counts_unique_works"]
    if {k: int(v) for k, v in venue_counts.items()} != {k: int(v) for k, v in declared.items()}:
        raise ResultsError(
            f"corpus.csv and query_log.json disagree about the venue classes of the 99 works: "
            f"{venue_counts} against {declared}"
        )

    instrument = coded["instrument_final"]
    sources = sources_by_key(corpus, set(coded["key"]))
    base = measures(coded, MAIN_VENUES, instrument, C_FLAGS)

    return {
        "protocol": "data/coding_protocol.md §10 (planned reporting) and §11 (sensitivity arms)",
        "frames": {
            "retrieved_on": query_log["retrieved_on"],
            "window": query_log["window"],
            "openalex_from_2015": query_log["denominators"]["openalex_from_2015"],
            "europepmc_from_2015": query_log["denominators"]["europepmc_from_2015"],
            "note": "the frames move with the databases; every figure is reported with the "
                    "retrieval date and the values come from query_log.json",
        },
        "main_analysis": {
            "venue_classes": list(MAIN_VENUES),
            "works_in_frame": venue_counts.get("journal_article", 0),
            "works_retrieved": int((coded["work_venue_class"] == "journal_article").sum()),
        },
        "m1": base["m1"],
        "m2": base["m2"],
        "pattern": pattern(base["m1"]),
        "sensitivity": sensitivity(coded, instrument, sources, query_log, venue_counts),
        "calibration": calibration(coded),
        "descriptive_counts_no_rate": descriptive(coded, log, venue_counts),
        "post_hoc_counts_not_planned": post_hoc(coded, instrument),
    }


def show(results: dict) -> None:
    def line(label: str, p: dict) -> str:
        return f"  {label:<34} {p['k']:>3}/{p['n']:<3} {p['p']:>7.1%}  95% CI [{p['ci_low']:.1%}, {p['ci_high']:.1%}]"

    frames = results["frames"]
    print(f"Frames ({frames['retrieved_on']}): OpenAlex {frames['openalex_from_2015']:,} / "
          f"Europe PMC {frames['europepmc_from_2015']:,}")
    main = results["main_analysis"]
    print(f"Main analysis: {main['works_retrieved']} of {main['works_in_frame']} journal_article works retrieved")

    m1 = results["m1"]
    print(f"\nM1 — instrument attribution (E1 works in the main analysis, n1 = {m1['n1']})")
    if m1["distribution"]:
        for code in INSTRUMENTS:
            print(line(f"({code})", m1["distribution"][code]))
    else:
        print(f"  {m1['note']}")

    m2 = results["m2"]
    print(f"\nM2 — citation and conflation (all {m2['n']} coded works)")
    print(line("R4 vendor as psychometrics", m2["r4"]))
    print(line("any of C1-C3", m2["any_conflation"]))

    p = results["pattern"]
    print(f"\n§10 pattern: {p['pattern']} — {p['reason']}")
    print(f"  abstract leads with {p['abstract_leads_with']}")
    print(f"  headline as §10 promised it: {p['headline_wording']}")
    if p.get("headline_departed_from"):
        print(f"  DEPARTED FROM — as reported: {p['headline_as_reported']}")

    print("\n§11 sensitivity arms")
    for name, arm in results["sensitivity"].items():
        print(f"\n  {name}: {arm['arm']}")
        if arm["m1"] and arm["m1"]["distribution"]:
            codes = "  ".join(
                f"({c}) {arm['m1']['distribution'][c]['k']}/{arm['m1']['distribution'][c]['n']}"
                f" {arm['m1']['distribution'][c]['p']:.1%}" for c in INSTRUMENTS
            )
            print(f"    M1 (n1={arm['m1']['n1']}): {codes}")
        if arm["m2"]:
            a = arm["m2"]
            print(f"    M2 (n={a['n']}): R4 {a['r4']['k']}/{a['r4']['n']} {a['r4']['p']:.1%}"
                  f"   any C {a['any_conflation']['k']}/{a['any_conflation']['n']} {a['any_conflation']['p']:.1%}")
        print(f"    {arm['note']}")

    d = results["descriptive_counts_no_rate"]
    print("\nCounts the protocol asks for without a rate (§12, 2026-08-22)")
    print(f"  E gate: {d['e_gate']}")
    print(f"  role flags: {d['role_flags']}")
    print(f"  conflation flags: {d['conflation_flags']}")
    print(f"  (c) sub-labels: {d['instrument_sublabels_among_c']}")
    print(f"  states_distinction: {d['states_distinction']}   "
          f"third-party conflation: {d['third_party_conflation']['count']} (never rated)   "
          f"text_is_abstract: {d['text_is_abstract']}")
    r = d["retrieval"]
    print(f"  retrieval: {r['coded']} coded, {r['unobtainable']['total']} unobtainable "
          f"{r['unobtainable']['by_reason']}, {r['no_word_form']['count']} no_word_form "
          f"of {r['no_word_form']['checkable_works']} checkable")

    ph = results["post_hoc_counts_not_planned"]
    print(f"\nUNPLANNED, added {ph['added']} — conflation flags by instrument code "
          f"({ph['form']})")
    for code, counts in ph["by_instrument_code"].items():
        if not counts["works"]:
            continue
        print(f"  ({code}) n={counts['works']:<3} C1 {counts['c1_identity']}"
              f"  C2 {counts['c2_provenance']}"
              f"  C3 {counts['c3_authority']}"
              f"  C1-or-C2 {counts['c1_or_c2']}"
              f"  any C1-C3 {counts['any_conflation']}"
              f"  C0 {counts['c0_no_conflating_statement']}"
              f"  states_distinction {counts['states_distinction']}")

    c = results["calibration"]
    print(f"\n§7 calibration records: {c['outside_main_analysis']} of {len(CALIBRATION)} contribute "
          f"nothing to M1; every pre-judged code reproduced = {c['all_reproduced']}")
    for name, record in c["records"].items():
        if not record["coded"]:
            print(f"  {name}: not retrieved")
            continue
        coded_as = record["coded_as"]
        print(f"  {name}: {record['venue_class']}, {coded_as['e']}"
              f"{', (' + coded_as['instrument'] + ')' if coded_as['instrument'] else ''}"
              f", R {'+'.join(f.upper() for f in coded_as['r']) or '-'}"
              f", C {'+'.join(f.upper() for f in coded_as['c']) or '-'}"
              f" | in M1 = {record['contributes_to_m1']}, §7 reproduced = {record['reproduced']}")
        for field, verdict in record["expected_by_section_7"].items():
            if not verdict["reproduced"]:
                print(f"    ⚠ {field}: §7 expected {verdict['expected']!r}, coded {verdict['actual']!r}")


def main() -> None:
    results = build()
    OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    show(results)
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
