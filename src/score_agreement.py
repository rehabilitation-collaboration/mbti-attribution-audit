"""Compute inter-coder agreement from data/classification.csv.

§9 of `data/coding_protocol.md` asks for kappa separately per code rather than
as one headline: the E gate over every coded work, the instrument code over the
works both coders placed in E1, and each R and C flag on its own. A single
pooled figure would average a four-way judgment together with ten binary flags
that are mostly false, and would read higher than any of them deserves.

Two properties of this design decide how the output is written.

Cohen's kappa is undefined when the coders' marginals leave no room for chance
disagreement — a flag neither coder ever sets gives expected agreement of 1 and
a zero denominator. That is not perfect reliability and is not reported as
kappa; the row carries the observed agreement and says the coefficient does not
exist. Reporting 1.0 there would manufacture the study's strongest reliability
figure out of a flag nobody used.

And both coders are tiers of one vendor's model line, so every figure here
measures the stability of one lineage's reading rather than the convergence of
independent judgments. §9 requires that caveat in the manuscript. It is repeated
in this file's output so the number is never read without it.

Outputs
    data/agreement.csv  one row per code, published
    stdout              the same table, plus the caveat
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CLASSIFICATION = ROOT / "data" / "classification.csv"
OUT = ROOT / "data" / "agreement.csv"

R_FLAGS = ("r1", "r2", "r3", "r4", "r5", "r6", "r7")
C_FLAGS = ("c0", "c1", "c2", "c3")
NARROW_FLAGS = ("narrow_c1", "narrow_c2", "narrow_c3")
EXTRA_FLAGS = ("states_distinction", "text_is_abstract")

CAVEAT = (
    "Both coders are tiers of one vendor's model line (c1 claude-sonnet-5, "
    "c2 claude-opus-5). These figures measure the stability of one lineage's "
    "reading, not agreement between independent raters, and are not comparable "
    "to a kappa between humans."
)


def cohen_kappa(a: list, b: list) -> tuple[float | None, float, float]:
    """Return (kappa, observed agreement, expected agreement).

    Kappa is None when expected agreement is 1 — the coders used one category
    between them, so chance alone predicts every match and the coefficient has a
    zero denominator. The caller reports the observed agreement instead of
    substituting a value.
    """
    if len(a) != len(b):
        raise ValueError("coder vectors differ in length")
    n = len(a)
    if n == 0:
        raise ValueError("no works to score")

    observed = sum(x == y for x, y in zip(a, b)) / n
    count_a, count_b = Counter(a), Counter(b)
    expected = sum(count_a[k] * count_b.get(k, 0) for k in count_a) / (n * n)

    if expected >= 1.0:
        return None, observed, expected
    return (observed - expected) / (1 - expected), observed, expected


def score(frame: pd.DataFrame, name: str, col_a: str, col_b: str) -> dict:
    a, b = frame[col_a].tolist(), frame[col_b].tolist()
    kappa, observed, expected = cohen_kappa(a, b)
    categories = sorted({str(v) for v in a + b})
    return {
        "code": name,
        "n": len(a),
        "categories_used": "/".join(categories),
        "observed_agreement": round(observed, 4),
        "expected_agreement": round(expected, 4),
        "kappa": "" if kappa is None else round(kappa, 4),
        "note": "" if kappa is not None else "undefined: one category between both coders",
    }


def main() -> None:
    frame = pd.read_csv(CLASSIFICATION)
    rows = [score(frame, "E gate", "c1_e", "c2_e")]

    both_e1 = frame[(frame["c1_e"] == "E1") & (frame["c2_e"] == "E1")]
    if len(both_e1):
        rows.append(score(both_e1, "instrument (both coders E1)", "c1_instrument", "c2_instrument"))
    else:
        rows.append(
            {
                "code": "instrument (both coders E1)",
                "n": 0,
                "categories_used": "",
                "observed_agreement": "",
                "expected_agreement": "",
                "kappa": "",
                "note": "no work placed in E1 by both coders",
            }
        )

    for flag in R_FLAGS + C_FLAGS + NARROW_FLAGS + EXTRA_FLAGS:
        label = flag.upper() if len(flag) == 2 else flag
        rows.append(score(frame, label, f"{flag}_c1", f"{flag}_c2"))

    table = pd.DataFrame(rows)
    table.to_csv(OUT, index=False)

    print(table.to_string(index=False))
    print(f"\nwrote {OUT.relative_to(ROOT)}")
    print(f"\n{CAVEAT}")

    pending = frame["needs_adjudication"].sum() if "needs_adjudication" in frame else 0
    if pending:
        print(
            f"\n{pending} of {len(frame)} works still await the author's ruling; "
            "these figures describe the coders' raw output, which is what kappa "
            "is meant to describe, and do not change once the rulings land."
        )


if __name__ == "__main__":
    main()
