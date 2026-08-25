"""Check every quotation in the manuscript against the text it is taken from.

This study measures works that attribute to a source something the source does
not say. The obvious way for it to fail is to do that itself, and a reference
check does not catch it: `verify_manuscript_refs.py` confirms that a DOI resolves
to the work named, not that the sentence in quotation marks appears in it. That
gap has already cost this manuscript once, when a cited paper was quoted for the
opposite of its conclusion and only a human reader noticed.

So every quoted span of twenty characters or more is pulled out of the manuscript
and has to be accounted for. Three accounts are possible:

- it is quoted from an archived primary source, and the string is found there;
- it is quoted from a coded work, and the string is found in that work's located
  quotation in `data/classification.csv`;
- it is not a quotation from a source at all — a phrase being mentioned rather
  than used, or the manuscript quoting an earlier draft of itself — in which case
  it is listed below with the reason.

**A span that fits none of the three fails the run.** That is the property worth
having: a quotation added later cannot pass by being absent from this file, only
by being classified in it.

`sources/` is not redistributed, so a reader cannot run the first check. The
report this writes is published instead, and records for each quotation which
file it was found in and how many characters matched.

Outputs
    output/quote_verification.md   the record, published
    exit 1                         if any span is unaccounted for or not found
"""

from __future__ import annotations

import csv
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANUSCRIPT = ROOT / "manuscript.md"
SOURCES = ROOT / "sources"
CLASSIFICATION = ROOT / "data" / "classification.csv"
OUT = ROOT / "output" / "quote_verification.md"

MIN_LENGTH = 20

# Spans that are not quotations from a source. Each needs a reason, because
# "it is not really a quote" is exactly what someone would say about a quote they
# could not find.
NOT_A_SOURCE_QUOTATION = {
    "administered the MBTI":
        "a phrase mentioned as the kind of claim this study checks, not quoted from any work",
    "we administered the MBTI":
        "same; a constructed example of the claim, not attributed to a work",
    "we used 16Personalities, which is not the MBTI":
        "a constructed counterexample, explicitly hypothetical in the sentence that carries it",
    "the author looked and changed nothing":
        "the manuscript naming a state of affairs, not quoting a document",
    "the range of underlying rates compatible with these counts":
        "the manuscript quoting its own earlier draft, in the passage that withdraws it",
}

# Nothing is verified "by hand" here. A quotation from a document this study does
# not hold cannot be checked by anyone later, so the document is fetched and
# archived instead, and the check becomes mechanical like the others.
EXTERNAL: dict[str, tuple[str, str]] = {}

# The archived texts the manuscript quotes from, grouped by document.
ARCHIVED = {
    "for-ai": ("16p-for-ai_2026-08-17.md", "16p-for-ai_2026-08-17.txt", "16p-for-ai_2026-08-17.json"),
    "our-framework": ("16personalities-our-framework_2026-08-25.pdf",),
    # Retrieved 2026-08-25 from journals.plos.org (CC BY). This is the reference a
    # reviewer previously caught being quoted for the opposite of its conclusion,
    # which is the reason it is archived rather than trusted.
    "bennett-2011": ("Bennett2011_PLoSMed_2026-08-25.pdf",),
    # Elsevier's Scopus source list, July 2026. The workbook is 20 MB; the rows
    # for the one journal this paper names are extracted verbatim beside it so
    # the quotations can be matched without loading the spreadsheet.
    "scopus-source-list": ("scopus-ext-list_Jul2026_IJM-extract.txt",),
}


def normalise(text: str) -> str:
    """Fold the differences that are typography rather than wording.

    Ordinal suffixes are dropped after a digit because a PDF sets them as
    superscripts and text extraction moves them elsewhere: `our-framework` reads
    "early 20th century" on the page and "early 20 century" through pdfminer.
    Applying the same fold to both sides compares the words and not the layout.
    """
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("­", "")                        # soft hyphen
    text = re.sub(r"[‘’‛]", "'", text)
    text = re.sub(r"[“”‟]", '"', text)
    text = re.sub(r"[‐-―−]", "-", text)
    text = re.sub(r"(?<=\d)(st|nd|rd|th)\b", "", text, flags=re.I)
    text = re.sub(r"[^\w\s'\".,;:%+-]", " ", text)           # ® and friends
    return re.sub(r"\s+", " ", text).strip().lower()


def read_source(name: str) -> str:
    path = SOURCES / name
    if not path.exists():
        return ""
    if path.suffix == ".pdf":
        from pdfminer.high_level import extract_text
        return extract_text(str(path))
    return path.read_text(encoding="utf-8", errors="replace")


def haystacks() -> dict[str, str]:
    stacks = {
        key: normalise(" ".join(read_source(n) for n in names))
        for key, names in ARCHIVED.items()
    }
    # The protocol is published with the manuscript and the manuscript quotes it,
    # including sentences it quotes in order to withdraw them.
    stacks["protocol"] = normalise((ROOT / "data" / "coding_protocol.md").read_text(encoding="utf-8"))
    quotes = []
    with CLASSIFICATION.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            quotes += [v for k, v in row.items() if k.startswith("quote_") or k == "free_text"]
    stacks["coded-work"] = normalise(" ".join(quotes))
    return stacks


def quoted_spans(text: str) -> list[str]:
    """Quotation marks paired in the order they appear, then filtered by length.

    Not `re.findall(r'"([^"\\n]{20,})"')`. That pattern fails on a short quoted
    word: `reported "MBTI" results ... looking for "the MBTI" online` gives a
    four-character span the length bound rejects, whereupon the engine restarts
    at the *closing* mark and returns everything from there to the next opening
    one. The span it invents is real prose, so it looks like a quotation nobody
    can source — which is the wrong alarm to raise in a tool whose whole job is
    raising that alarm. Pairing first and filtering second cannot do it.
    """
    body = text[: text.index("## References")]
    body = re.sub(r"[“”‟]", '"', body)
    marks = [m.start() for m in re.finditer(r'"', body)]
    spans = []
    for opening, closing in zip(marks[::2], marks[1::2]):
        span = body[opening + 1 : closing]
        if "\n" not in span and len(span) >= MIN_LENGTH:
            spans.append(span)
    return spans


def main() -> int:
    text = MANUSCRIPT.read_text(encoding="utf-8")
    stacks = haystacks()
    missing_sources = [n for names in ARCHIVED.values() for n in names if not (SOURCES / n).exists()]

    rows, failures = [], []
    for span in dict.fromkeys(quoted_spans(text)):
        needle = normalise(span)
        if span in NOT_A_SOURCE_QUOTATION:
            rows.append(("—", "not a source quotation", span, NOT_A_SOURCE_QUOTATION[span]))
            continue
        if span in EXTERNAL:
            source, note = EXTERNAL[span]
            rows.append(("hand", source, span, note))
            continue
        found = [key for key, stack in stacks.items() if needle and needle in stack]
        if found:
            rows.append(("OK", " + ".join(found), span, f"{len(needle)} characters matched"))
        else:
            rows.append(("MISS", "not found", span, "no archived text contains this string"))
            failures.append(span)

    unclassified = [
        s for s in quoted_spans(text)
        if s not in NOT_A_SOURCE_QUOTATION and s not in EXTERNAL
        and not any(normalise(s) in stack for stack in stacks.values())
    ]

    OUT.parent.mkdir(exist_ok=True)
    lines = [
        "# Quotation verification",
        "",
        f"Every quoted span of {MIN_LENGTH} characters or more in `manuscript.md`, checked against "
        "the text it is taken from. Generated by `src/verify_manuscript_quotes.py`.",
        "",
        "`sources/` holds third-party captures and is not redistributed, so the vendor checks "
        "cannot be re-run from the public repository; this record is published in their place. "
        "The coded-work checks run against `data/classification.csv`, which is published.",
        "",
        "| Result | Found in | Quotation | Note |",
        "|---|---|---|---|",
    ]
    for result, where, span, note in rows:
        shown = span if len(span) <= 90 else span[:87] + "…"
        lines.append(f"| {result} | {where} | {shown.replace('|', '\\|')} | {note} |")
    lines += ["", f"{len(rows)} spans: "
              f"{sum(1 for r in rows if r[0] == 'OK')} found in an archived source, "
              f"{sum(1 for r in rows if r[0] == 'hand')} verified by hand against an external source, "
              f"{sum(1 for r in rows if r[0] == '—')} not source quotations, "
              f"{len(failures)} unaccounted for.", ""]
    if missing_sources:
        lines += [f"⚠️ absent from `sources/` at run time: {', '.join(missing_sources)}", ""]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    for result, where, span, note in rows:
        print(f"  {result:<4} {where:<28} {span[:60]}")
    print(f"\nwrote {OUT.relative_to(ROOT)}")
    if missing_sources:
        print(f"⚠️  not checked, file absent: {missing_sources}")
    if unclassified:
        print(f"\n{len(unclassified)} span(s) unaccounted for:")
        for span in unclassified:
            print(f"  {span}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
