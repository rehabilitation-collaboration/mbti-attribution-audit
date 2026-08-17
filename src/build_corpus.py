"""Build the frozen corpus of papers that report MBTI results and mention 16Personalities.

Two sources are queried with a single shared definition:

  denominator : title or abstract mentions MBTI / Myers-Briggs / Myers Briggs
  intersection: denominator AND full text mentions any 16Personalities word form
  window      : published 2015-01-01 onwards

The window is fixed at 2015 because widening it to 2011 adds no intersecting
work (measured 2026-08-18: 39 in both), while the denominator grows by a fifth.

Outputs
    data/corpus.csv     one row per retrieved record, both sources, with a
                        duplicate group id and a venue class; nothing is dropped
    data/query_log.json the exact queries, the counts they returned, and the
                        retrieval date, so every reported number can be repinned
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

import pandas as pd
import requests

MAILTO = "shirai@reha3.jp"
OPENALEX = "https://api.openalex.org/works"
EUROPEPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
FROM_DATE = "2015-01-01"
TO_DATE = "2026-12-31"

# OpenAlex accepts quoted phrases in .search filters; unquoted multi-word terms
# are treated as loose token queries and explode (16 personalities -> 200,102).
# "Type Explorer" alone is not used: it returns 2,423 works on its own and adds
# exactly one work to the intersection, so it is carried as a widening variant
# to be checked by eye rather than folded into the primary definition.
OA_DENOMINATOR = 'title_and_abstract.search:MBTI OR "Myers-Briggs" OR "Myers Briggs"'
OA_VARIANTS = (
    'fulltext.search:16personalities OR "16 Personalities" '
    'OR "16personalities.com" OR "NERIS Type Explorer"'
)
OA_VARIANTS_WIDE = OA_VARIANTS + ' OR "Type Explorer"'
OA_WINDOW = f"from_publication_date:{FROM_DATE}"

# Europe PMC's full-text index handles spaced phrases correctly, so the whole
# word-form set is used there.
EPMC_DENOMINATOR = '(TITLE_ABS:"MBTI" OR TITLE_ABS:"Myers-Briggs" OR TITLE_ABS:"Myers Briggs")'
EPMC_VARIANTS = (
    '("16personalities" OR "16 Personalities" OR "16personalities.com" '
    'OR "NERIS Type Explorer" OR "Type Explorer")'
)
EPMC_WINDOW = f"(FIRST_PDATE:[{FROM_DATE} TO {TO_DATE}])"

# Known-correct records that must survive the pipeline. If one of these goes
# missing the query is broken, not the literature.
VALIDATION_DOIS = {
    "10.1038/s41598-025-91361-w": "Bai 2025 Scientific Reports",
    "10.4992/pacjpa.89.0_423": "Koshiro 2025 Japanese Psychological Association",
    "10.3389/fncom.2026.1800284": "Tshimula 2026 Frontiers Comput Neurosci",
}

REPO_HINTS = ("zenodo", "arxiv", "ssrn", "researchsquare", "biorxiv", "psyarxiv", "osf")


def norm_doi(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", value.strip().lower())


def norm_title(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def fetch_openalex(filter_expr: str) -> list[dict]:
    """Page through an OpenAlex filter with a cursor and return every work."""
    works, cursor = [], "*"
    while cursor:
        response = requests.get(
            OPENALEX,
            params={"filter": filter_expr, "per_page": 200, "cursor": cursor, "mailto": MAILTO},
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        works.extend(payload["results"])
        cursor = payload["meta"].get("next_cursor")
    return works


def fetch_europepmc(query: str) -> list[dict]:
    """Page through a Europe PMC query with a cursor mark and return every result."""
    results, cursor = [], "*"
    while True:
        response = requests.get(
            EUROPEPMC,
            params={
                "query": query,
                "format": "json",
                "pageSize": 100,
                "cursorMark": cursor,
                "resultType": "core",
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        results.extend(payload["resultList"]["result"])
        next_cursor = payload.get("nextCursorMark")
        if not next_cursor or next_cursor == cursor:
            return results
        cursor = next_cursor


def classify_openalex(work: dict) -> str:
    """Assign a venue class used later to decide what counts as peer reviewed."""
    location = work.get("primary_location") or {}
    source = location.get("source") or {}
    source_type = (source.get("type") or "").lower()
    name = (source.get("display_name") or "").lower()
    host = (source.get("host_organization_name") or "").lower()
    work_type = (work.get("type") or "").lower()

    if work_type == "libguides":
        return "non_scholarly"
    if work_type == "preprint" or source_type == "preprint":
        return "preprint"
    if work_type == "dissertation":
        return "thesis"
    if source_type == "repository" or any(h in name or h in host for h in REPO_HINTS):
        return "repository"
    if work_type == "conference-abstract":
        return "conference_abstract"
    if source_type == "conference" or work_type in {"proceedings-article", "conference-paper"}:
        return "conference"
    if work_type == "book-chapter":
        return "book_chapter"
    if source_type == "journal" and work_type in {"article", "review"}:
        return "journal_article"
    return "unclassified"


def row_from_openalex(work: dict) -> dict:
    location = work.get("primary_location") or {}
    source = location.get("source") or {}
    best = work.get("best_oa_location") or {}
    return {
        "source_db": "openalex",
        "source_id": work.get("id", ""),
        "doi": norm_doi(work.get("doi")),
        "title": work.get("display_name") or "",
        "year": work.get("publication_year"),
        "pub_date": work.get("publication_date") or "",
        "venue": source.get("display_name") or "",
        "venue_class": classify_openalex(work),
        "work_type": work.get("type") or "",
        "is_oa": bool((work.get("open_access") or {}).get("is_oa")),
        "oa_url": best.get("pdf_url") or best.get("landing_page_url") or "",
    }


def row_from_europepmc(record: dict) -> dict:
    is_preprint = (record.get("source") or "") == "PPR"
    # Europe PMC nests these; there is no top-level journalTitle or pubType.
    journal = ((record.get("journalInfo") or {}).get("journal") or {}).get("title") or ""
    pub_types = (record.get("pubTypeList") or {}).get("pubType") or []
    if isinstance(pub_types, str):
        pub_types = [pub_types]
    return {
        "source_db": "europepmc",
        "source_id": f"{record.get('source', '')}:{record.get('id', '')}",
        "doi": norm_doi(record.get("doi")),
        "title": record.get("title") or "",
        "year": record.get("pubYear"),
        "pub_date": record.get("firstPublicationDate") or "",
        "venue": journal,
        "venue_class": "preprint" if is_preprint else "journal_article",
        "work_type": "; ".join(pub_types),
        "is_oa": (record.get("isOpenAccess") or "N") == "Y",
        "oa_url": f"https://europepmc.org/article/{record.get('source', '')}/{record.get('id', '')}",
    }


def assign_duplicate_groups(frame: pd.DataFrame) -> pd.DataFrame:
    """Group records that are the same work: same DOI, else same normalised title.

    Kept as a group id rather than a deletion so the manuscript can report how
    many records collapsed and a reader can audit each collapse.
    """
    keys, seen = [], {}
    for _, row in frame.iterrows():
        key = row["doi"] or f"title:{norm_title(row['title'])}"
        keys.append(seen.setdefault(key, len(seen)))
    frame = frame.copy()
    frame["dup_group"] = keys
    return frame


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    data = root / "data"
    data.mkdir(exist_ok=True)

    oa_filter = f"{OA_DENOMINATOR},{OA_VARIANTS},{OA_WINDOW}"
    epmc_query = f"{EPMC_DENOMINATOR} AND {EPMC_VARIANTS} AND {EPMC_WINDOW}"

    oa_works = fetch_openalex(oa_filter)
    epmc_records = fetch_europepmc(epmc_query)

    rows = [row_from_openalex(w) for w in oa_works] + [row_from_europepmc(r) for r in epmc_records]
    frame = assign_duplicate_groups(pd.DataFrame(rows).sort_values(["source_db", "year", "title"]))
    frame.to_csv(data / "corpus.csv", index=False)

    found = {d: n for d, n in VALIDATION_DOIS.items() if d in set(frame["doi"])}
    missing = {d: n for d, n in VALIDATION_DOIS.items() if d not in found}

    log = {
        "retrieved_on": date.today().isoformat(),
        "window": {"from": FROM_DATE, "to": TO_DATE},
        "openalex": {"filter": oa_filter, "records": len(oa_works)},
        "europepmc": {"query": epmc_query, "records": len(epmc_records)},
        "rows": len(frame),
        "unique_works": int(frame["dup_group"].nunique()),
        "venue_class_counts": frame["venue_class"].value_counts().to_dict(),
        "validation_found": found,
        "validation_missing": missing,
    }
    (data / "query_log.json").write_text(json.dumps(log, indent=2, ensure_ascii=False))

    print(json.dumps(log, indent=2, ensure_ascii=False))
    if missing:
        raise SystemExit(f"validation records missing from corpus: {sorted(missing)}")


if __name__ == "__main__":
    main()
