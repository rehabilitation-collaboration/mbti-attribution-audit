"""Retrieve open-access full text for the works in the frozen corpus.

Coding reads full text rather than abstracts (`data/coding_protocol.md` §1), so
this step decides how much of the corpus can be coded at all. What it fails to
retrieve is as much a result as what it retrieves: the protocol drops
unobtainable works from the denominator and requires the count and the reason to
be reported next to every proportion.

Retrieval order per work: the open-access link OpenAlex already recorded, then
every location Unpaywall knows for the DOI. Europe PMC's full-text endpoint is
not tried — its search index is broader than its open-access subset, and all ten
of this corpus's Europe PMC records return 404 there (measured 2026-08-19).

A retrieved document is checked against the word forms the corpus was built on.
A work entered the corpus because its full text mentions 16Personalities, so a
retrieved text that does not is probably a landing page or an abstract rather
than the article, and is flagged rather than silently coded.

Outputs
    fulltext/<key>.txt     extracted text. Git-ignored: these are third-party
                           articles and this repository does not redistribute
                           them, the same decision already taken for sources/
    data/fulltext_log.csv  one row per work — which URL served it, how much text
                           came out, whether the text contains the word forms,
                           and why a failure failed
"""

from __future__ import annotations

import io
import re
import time
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text as pdf_text

from build_corpus import VENUE_PRIORITY

MAILTO = "shirai@reha3.jp"
UNPAYWALL = "https://api.unpaywall.org/v2/"
UA = (
    "mbti-attribution-audit/1.0 "
    "(+https://github.com/rehabilitation-collaboration/mbti-attribution-audit; "
    f"mailto:{MAILTO})"
)
TIMEOUT = 60
PAUSE = 0.5

# Below this a document is treated as not being the article. Even a two-page
# conference paper clears it; an abstract page or a paywall notice does not.
MIN_CHARS = 3000

VARIANT_RE = re.compile(r"16\s?personalit|NERIS|Type Explorer", re.I)
MBTI_RE = re.compile(r"MBTI|Myers[\s-]?Briggs", re.I)


def work_key(row: pd.Series) -> str:
    """A filesystem-safe identifier, preferring the DOI over the source id."""
    base = row["doi"] or row["source_id"]
    return re.sub(r"[^a-z0-9]+", "_", str(base).lower()).strip("_")[:100]


def unpaywall_locations(doi: str) -> list[str]:
    """Every open-access URL Unpaywall holds for a DOI, best location first."""
    if not doi:
        return []
    try:
        response = requests.get(
            f"{UNPAYWALL}{doi}", params={"email": MAILTO}, timeout=TIMEOUT
        )
        if response.status_code != 200:
            return []
        payload = response.json()
    except (requests.RequestException, ValueError):
        return []

    urls: list[str] = []
    best = payload.get("best_oa_location") or {}
    for location in [best, *(payload.get("oa_locations") or [])]:
        for field in ("url_for_pdf", "url"):
            candidate = location.get(field)
            if candidate and candidate not in urls:
                urls.append(candidate)
    return urls


def extract(response: requests.Response) -> str:
    """Text from a PDF or an HTML page, whitespace collapsed."""
    is_pdf = response.content[:4] == b"%PDF" or "pdf" in response.headers.get(
        "content-type", ""
    )
    if is_pdf:
        text = pdf_text(io.BytesIO(response.content))
    else:
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer"]):
            tag.decompose()
        text = soup.get_text(" ")
    return re.sub(r"\s+", " ", text).strip()


def attempt(url: str) -> tuple[str, str]:
    """Fetch one URL. Returns (text, error); exactly one of them is empty."""
    try:
        response = requests.get(
            url, headers={"User-Agent": UA}, timeout=TIMEOUT, allow_redirects=True
        )
    except requests.RequestException as exc:
        return "", type(exc).__name__
    if response.status_code != 200:
        return "", f"http_{response.status_code}"
    try:
        text = extract(response)
    except Exception as exc:  # pdfminer raises a wide range on malformed files
        return "", f"extract_{type(exc).__name__}"
    if not text:
        return "", "empty_extract"
    return text, ""


def ordered_records(records: pd.DataFrame) -> pd.DataFrame:
    """One work's records, most authoritative version first."""
    rank = {name: index for index, name in enumerate(VENUE_PRIORITY)}
    return records.assign(
        _rank=records["venue_class"].map(lambda c: rank.get(c, len(rank)))
    ).sort_values("_rank")


def retrieve(records: pd.DataFrame, out_dir: Path) -> dict:
    """Try every location known for one work and keep the best document.

    A work can have reached the corpus as a preprint and again as the article it
    became. The article is tried first — the Methods a coder reads should be the
    published one where it exists — and the version that actually served the
    text is recorded, so a coder reading a preprint knows that is what it is.
    """
    records = ordered_records(records)
    lead = records.iloc[0]

    candidates: list[tuple[str, str, str]] = []  # (url, where it came from, venue)
    for _, record in records.iterrows():
        if record["oa_url"]:
            candidates.append((record["oa_url"], "openalex", record["venue_class"]))
    for _, record in records.iterrows():
        for url in unpaywall_locations(record["doi"]):
            candidates.append((url, "unpaywall", record["venue_class"]))
    # The same URL often arrives more than once; keep the earliest mention.
    seen: set[str] = set()
    candidates = [c for c in candidates if not (c[0] in seen or seen.add(c[0]))]

    log = {
        "key": work_key(lead),
        "doi": lead["doi"],
        "title": lead["title"],
        "work_venue_class": lead["work_venue_class"],
        "records": len(records),
        "urls_tried": 0,
        "status": "no_url",
        "served_by": "",
        "url_source": "",
        "served_venue_class": "",
        "chars": 0,
        "has_16p_form": False,
        "has_mbti": False,
        "note": "",
    }
    if not candidates:
        log["note"] = "no open-access location in OpenAlex or Unpaywall"
        return log

    best: tuple[str, str, str, str] | None = None  # (text, url, source, venue)
    errors: list[str] = []
    for url, source, venue in candidates:
        log["urls_tried"] += 1
        text, error = attempt(url)
        time.sleep(PAUSE)
        if error:
            errors.append(f"{source}:{error}")
            continue
        if best is None or len(text) > len(best[0]):
            best = (text, url, source, venue)
        # Long enough and carrying the word forms means this is the article;
        # nothing later in the list can improve on it.
        if len(text) >= MIN_CHARS and VARIANT_RE.search(text):
            break

    if best is None:
        log["status"] = "fetch_failed"
        log["note"] = "; ".join(errors[:4])
        return log

    text, url, source, venue = best
    log.update(
        served_by=url,
        url_source=source,
        served_venue_class=venue,
        chars=len(text),
        has_16p_form=bool(VARIANT_RE.search(text)),
        has_mbti=bool(MBTI_RE.search(text)),
    )
    if len(text) < MIN_CHARS:
        log["status"] = "too_short"
        log["note"] = "retrieved document is shorter than an article"
    elif not log["has_16p_form"]:
        log["status"] = "no_word_form"
        log["note"] = "long enough, but lacks the form the corpus matched on"
    else:
        log["status"] = "ok"
    if errors:
        log["note"] = (log["note"] + " | " if log["note"] else "") + "; ".join(errors[:3])

    (out_dir / f"{log['key']}.txt").write_text(text)
    return log


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    out_dir = root / "fulltext"
    out_dir.mkdir(exist_ok=True)
    # Stale files would otherwise survive a change in how records group into
    # works, and the directory is meant to mirror the log exactly.
    for stale in out_dir.glob("*.txt"):
        stale.unlink()

    corpus = pd.read_csv(root / "data" / "corpus.csv", dtype=str, keep_default_na=False)
    groups = list(corpus.groupby("dup_group", sort=False))

    rows = []
    for position, (_, records) in enumerate(groups, start=1):
        entry = retrieve(records, out_dir)
        rows.append(entry)
        print(f"[{position}/{len(groups)}] {entry['status']:12} {entry['title'][:60]}")

    frame = pd.DataFrame(rows)
    frame.to_csv(root / "data" / "fulltext_log.csv", index=False)

    codeable = int((frame["status"] == "ok").sum())
    print(f"\nstatus: {frame['status'].value_counts().to_dict()}")
    print(f"codeable: {codeable}/{len(frame)} ({codeable / len(frame):.1%})")
    main_analysis = frame[frame["work_venue_class"] == "journal_article"]
    got = int((main_analysis["status"] == "ok").sum())
    print(f"journal_article: {got}/{len(main_analysis)} ({got / len(main_analysis):.1%})")
    served_elsewhere = frame[
        (frame["status"] == "ok")
        & (frame["served_venue_class"] != frame["work_venue_class"])
    ]
    print(f"served by a different version: {len(served_elsewhere)}")


if __name__ == "__main__":
    main()
