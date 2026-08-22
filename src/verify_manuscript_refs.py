"""Check every reference in manuscript.md against Crossref, by DOI.

The shared tool `internal/tools/verify_refs.py` resolves DOIs correctly but
compares fields on a Vancouver-style template — authors, then title, then
journal, separated by ". " — and this manuscript's references are author-date,
so its field comparison reads an author's initials as the title and reports a
mismatch on every line. Its DOI resolution is sound; its field verdicts are not
applicable here. This script does the comparison the reference style this
manuscript actually uses allows.

It exists as a script rather than as a one-off check because the reference list
has to be verified again immediately before submission, against the manuscript
rather than against the working notes. That distinction is not pedantic: two
entries in the working notes carried a fabricated first author — real
researchers in the right field, attached to the wrong DOI — and were caught only
because the DOIs were resolved rather than the names read.

What it checks, per reference: that the DOI resolves; that Crossref's first
author surname appears in the manuscript's line; that Crossref's year appears;
that a distinctive fragment of Crossref's title appears; and that the author
count the manuscript lists is not fewer than Crossref's. It reports what it
finds rather than guessing at a fix.

Outputs
    output/reference_verification_by_doi.md   the table, for review and submission
    stdout                                    the same, plus a pass/fail summary
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANUSCRIPT = ROOT / "manuscript.md"
OUT = ROOT / "output" / "reference_verification_by_doi.md"
MAILTO = "rehabilitation.collaboration@gmail.com"

STOPWORDS = {"the", "a", "an", "of", "and", "in", "on", "for", "to", "with", "at", "is"}


def references() -> list[str]:
    """Every entry in the References section, one string each."""
    text = MANUSCRIPT.read_text(encoding="utf-8")
    match = re.search(r"^## References\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not match:
        sys.exit("manuscript.md has no '## References' section")
    entries = []
    for block in re.split(r"\n\s*\n", match.group(1)):
        block = " ".join(block.split())
        # Sub-headings and rules carry no reference.
        if not block or block.startswith("---") or re.fullmatch(r"\*\*.*:\*\*", block):
            continue
        entries.append(block)
    return entries


def crossref(doi: str) -> dict | None:
    request = urllib.request.Request(
        f"https://api.crossref.org/works/{doi}",
        headers={"User-Agent": f"mbti-attribution-audit/1.0 (mailto:{MAILTO})"},
    )
    try:
        return json.load(urllib.request.urlopen(request, timeout=30))["message"]
    except Exception:
        return None


def year_of(record: dict) -> str:
    for field in ("published-print", "published-online", "issued", "created"):
        parts = (record.get(field) or {}).get("date-parts") or []
        if parts and parts[0] and parts[0][0]:
            return str(parts[0][0])
    return ""


def title_fragment(record: dict) -> str:
    """The longest distinctive word in Crossref's title, for a presence check."""
    title = (record.get("title") or [""])[0]
    words = [w for w in re.findall(r"[A-Za-z][A-Za-z-]{4,}", title) if w.lower() not in STOPWORDS]
    return max(words, key=len) if words else ""


def check(entry: str) -> dict:
    doi_match = re.search(r"https?://doi\.org/(10\.\S+?)(?:\s|$)", entry)
    if not doi_match:
        return {"entry": entry, "doi": "", "verdict": "NO DOI",
                "notes": "not a DOI-bearing source; verify by hand against its own record"}
    doi = doi_match.group(1).rstrip(".")
    record = crossref(doi)
    if record is None:
        return {"entry": entry, "doi": doi, "verdict": "UNRESOLVED",
                "notes": "Crossref returned nothing for this DOI"}

    authors = record.get("author") or []
    first = (authors[0].get("family") or "") if authors else ""
    year = year_of(record)
    fragment = title_fragment(record)
    listed = len(re.findall(r"\b[A-Z]\.", entry.split("(")[0])) if "(" in entry else 0

    problems = []
    if first and first.lower() not in entry.lower():
        problems.append(f"Crossref's first author '{first}' does not appear in the entry")
    if year and year not in entry:
        problems.append(f"Crossref's year {year} does not appear in the entry")
    if fragment and fragment.lower() not in entry.lower():
        problems.append(f"no trace of Crossref's title (looked for '{fragment}')")
    if authors and listed and listed < len(authors):
        problems.append(f"entry lists ~{listed} authors, Crossref has {len(authors)}")

    return {
        "entry": entry, "doi": doi,
        "verdict": "OK" if not problems else "CHECK",
        "crossref_first_author": first,
        "crossref_authors": len(authors),
        "crossref_year": year,
        "crossref_title": (record.get("title") or [""])[0],
        "crossref_venue": (record.get("container-title") or [""])[0],
        "notes": "; ".join(problems),
    }


def main() -> None:
    entries = references()
    print(f"checking {len(entries)} references in manuscript.md against Crossref\n")
    results = []
    for entry in entries:
        result = check(entry)
        results.append(result)
        flag = {"OK": "  OK   ", "CHECK": "  CHECK", "NO DOI": "  NODOI", "UNRESOLVED": "  FAIL "}[result["verdict"]]
        print(f"{flag} {result['doi'] or '(no doi)'}  {result.get('crossref_first_author', '')}")
        if result["notes"]:
            print(f"         {result['notes']}")
        time.sleep(0.3)

    OUT.parent.mkdir(exist_ok=True)
    lines = [
        "# Reference verification by DOI",
        "",
        "Generated by `src/verify_manuscript_refs.py` from `manuscript.md`.",
        "",
        "Each DOI in the reference list was resolved against Crossref and the record",
        "compared with what the manuscript's entry says. The shared Vancouver-style",
        "checker is not applicable to this manuscript's author-date references; its DOI",
        "resolution is sound but its field verdicts read an initial as a title.",
        "",
        "| # | DOI | Verdict | Crossref first author | Authors | Year | Venue | Notes |",
        "|---|-----|---------|----------------------|---------|------|-------|-------|",
    ]
    for i, r in enumerate(results, 1):
        lines.append(
            f"| {i} | `{r['doi'] or '—'}` | **{r['verdict']}** | {r.get('crossref_first_author', '—') or '—'} "
            f"| {r.get('crossref_authors', '—')} | {r.get('crossref_year', '—') or '—'} "
            f"| {r.get('crossref_venue', '—') or '—'} | {r['notes'] or '—'} |"
        )
    counts = {v: sum(1 for r in results if r["verdict"] == v) for v in ("OK", "CHECK", "NO DOI", "UNRESOLVED")}
    lines += ["", f"**Summary**: {counts['OK']} OK · {counts['CHECK']} need a look · "
                  f"{counts['NO DOI']} without a DOI · {counts['UNRESOLVED']} unresolved."]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\n{counts['OK']} OK · {counts['CHECK']} CHECK · {counts['NO DOI']} no DOI · {counts['UNRESOLVED']} unresolved")
    print(f"wrote {OUT.relative_to(ROOT)}")
    if counts["UNRESOLVED"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
