"""Build the frozen corpus of papers that report MBTI results and mention 16Personalities.

Two sources are queried with a single shared definition:

  denominator : title or abstract mentions MBTI / Myers-Briggs / Myers Briggs
  intersection: denominator AND full text mentions any 16Personalities word form
  window      : published 2015-01-01 onwards

The window is fixed at 2015: widening it to 2011 adds two intersecting works
(108 -> 110) while the denominator grows by a quarter (3,104 -> 3,890), which is
inside the pre-set rule of keeping 2015 when the gain is two or three works or
fewer. The word forms are likewise fixed: "Type Explorer" on its own is generic
enough to match thousands of unrelated works while adding at most one work to
the intersection, so it sits outside the shared definition and is carried as a
widening variant. Both decisions are re-measured on every run and land in
query_log.json, so they can be re-checked rather than taken on trust.

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
OA_DENOMINATOR = 'title_and_abstract.search:MBTI OR "Myers-Briggs" OR "Myers Briggs"'
OA_VARIANTS = (
    'fulltext.search:16personalities OR "16 Personalities" '
    'OR "16personalities.com" OR "NERIS Type Explorer"'
)
OA_VARIANTS_WIDE = OA_VARIANTS + ' OR "Type Explorer"'
OA_WINDOW = f"from_publication_date:{FROM_DATE}"

# Europe PMC is queried with the same four word forms, so one definition spans
# both sources rather than each source carrying its own. "Type Explorer" on its
# own sits outside that definition and is carried as a widening variant on both
# sides: it is a generic phrase that matches 2,423 works in OpenAlex while
# adding one work to the intersection there, and adds none here. Those figures
# are re-measured into variant_sensitivity on every run, so the exclusion can be
# re-checked rather than taken on trust.
EPMC_DENOMINATOR = '(TITLE_ABS:"MBTI" OR TITLE_ABS:"Myers-Briggs" OR TITLE_ABS:"Myers Briggs")'
EPMC_VARIANTS = (
    '("16personalities" OR "16 Personalities" OR "16personalities.com" '
    'OR "NERIS Type Explorer")'
)
EPMC_VARIANTS_WIDE = EPMC_VARIANTS[:-1] + ' OR "Type Explorer")'
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


def count_openalex(filter_expr: str) -> int:
    response = requests.get(
        OPENALEX, params={"filter": filter_expr, "per_page": 1, "mailto": MAILTO}, timeout=60
    )
    response.raise_for_status()
    return response.json()["meta"]["count"]


def count_europepmc(query: str) -> int:
    response = requests.get(
        EUROPEPMC,
        params={"query": query, "format": "json", "pageSize": 1, "resultType": "idlist"},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["hitCount"]


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

    # Denominators are reported in the manuscript, so they are measured here
    # rather than typed in from a shell session.
    denominators = {
        "openalex_from_2015": count_openalex(f"{OA_DENOMINATOR},{OA_WINDOW}"),
        "europepmc_from_2015": count_europepmc(f"{EPMC_DENOMINATOR} AND {EPMC_WINDOW}"),
    }

    # The 2015 window is a decision, so the numbers that decided it are measured
    # under the production definition. An earlier note recorded 2,498 -> 3,110
    # with no change in the intersection; those came from the pilot's
    # single-token query and do not reproduce here.
    from_2011 = "from_publication_date:2011-01-01"
    window_sensitivity = {
        "intersection_from_2015": count_openalex(f"{OA_DENOMINATOR},{OA_VARIANTS},{OA_WINDOW}"),
        "intersection_from_2011": count_openalex(f"{OA_DENOMINATOR},{OA_VARIANTS},{from_2011}"),
        "denominator_from_2011": count_openalex(f"{OA_DENOMINATOR},{from_2011}"),
    }
    window_sensitivity["intersection_gained_by_2011"] = (
        window_sensitivity["intersection_from_2011"] - window_sensitivity["intersection_from_2015"]
    )

    # Leaving "Type Explorer" out of the shared definition is the other standing
    # decision, so it is measured the same way rather than argued for in prose.
    variant_sensitivity = {
        "openalex_primary": window_sensitivity["intersection_from_2015"],
        "openalex_with_type_explorer": count_openalex(
            f"{OA_DENOMINATOR},{OA_VARIANTS_WIDE},{OA_WINDOW}"
        ),
        "openalex_type_explorer_alone": count_openalex(
            f'fulltext.search:"Type Explorer",{OA_WINDOW}'
        ),
        "europepmc_primary": len(epmc_records),
        "europepmc_with_type_explorer": count_europepmc(
            f"{EPMC_DENOMINATOR} AND {EPMC_VARIANTS_WIDE} AND {EPMC_WINDOW}"
        ),
    }

    unique = frame.drop_duplicates("dup_group")
    log = {
        "retrieved_on": date.today().isoformat(),
        "window": {"from": FROM_DATE, "to": TO_DATE},
        "openalex": {"filter": oa_filter, "records": len(oa_works)},
        "europepmc": {"query": epmc_query, "records": len(epmc_records)},
        "denominators": denominators,
        "window_sensitivity": window_sensitivity,
        "variant_sensitivity": variant_sensitivity,
        "rows": len(frame),
        "unique_works": int(frame["dup_group"].nunique()),
        # Two counts because they differ: a work retrieved from both sources
        # occupies two rows. Reported figures use the unique-work count.
        "venue_class_counts_unique_works": unique["venue_class"].value_counts().to_dict(),
        "venue_class_counts_all_rows": frame["venue_class"].value_counts().to_dict(),
        "validation_found": found,
        "validation_missing": missing,
    }
    (data / "query_log.json").write_text(json.dumps(log, indent=2, ensure_ascii=False))

    print(json.dumps(log, indent=2, ensure_ascii=False))
    if missing:
        raise SystemExit(f"validation records missing from corpus: {sorted(missing)}")


if __name__ == "__main__":
    main()
