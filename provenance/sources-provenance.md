# Provenance of primary sources

This study cites a small number of documents that are not redistributed with the
repository: one third-party master's thesis and several captures of a commercial
vendor's website. This file records where each file came from, when and how it was
retrieved, and how a reader can confirm that a re-retrieved copy is identical to
the copy the analysis used.

## Policy

The files themselves live in `sources/`, which is excluded from version control.

- `LeeSeongbin2024_MA-thesis_GNU_*.pdf` is another author's master's thesis in
  full (131 pp). The licence statement printed inside the PDF reads
  저작자표시 (attribution) / 비영리 (non-commercial) / 변경금지 (no derivatives),
  i.e. CC BY-NC-ND. Redistribution would add nothing to reproducibility.
- The 16Personalities captures are pages from a commercial website. The passages
  this study relies on are quoted verbatim in the manuscript; the full captures
  are kept locally only.

Publishing provenance rather than the files preserves verifiability without
redistributing third-party content.

## Integrity verification

`provenance/CHECKSUMS.txt` lists the SHA-256 of all nine files. To check a local
copy of `sources/`:

```bash
cd sources && shasum -a 256 -c ../provenance/CHECKSUMS.txt
```

Verification log:

- 2026-08-17: hashes first recorded at retrieval time.
- 2026-08-18: all nine files re-hashed and matched the 2026-08-17 record (9/9).
  On the same date the five vendor URLs were re-requested and returned HTTP 200
  with byte counts identical to the stored captures (16130 / 15805 / 14548 /
  1941 / 38087), so the live pages had not changed since retrieval.
- 2026-08-25: `16personalities-our-framework_2026-08-25.pdf` added and hashed.
  Recorded together with the finding that a byte-identical capture can still be
  empty of content: `our-theory` passes its checksum and carries 628 characters
  of text. A checksum certifies that a file has not changed, not that it says
  anything, and the two vendor pages this study quotes are now held in a form
  that carries the text.

## Files

| File | Source URL | Retrieved | Method |
|---|---|---|---|
| `16p-for-ai_2026-08-17.md` | `https://www.16personalities.com/for-ai.md` | 2026-08-17 | `curl -s -L` |
| `16p-for-ai_2026-08-17.txt` | `https://www.16personalities.com/for-ai.txt` | 2026-08-17 | `curl -s -L` |
| `16p-for-ai_2026-08-17.json` | `https://www.16personalities.com/for-ai.json` | 2026-08-17 | `curl -s -L` |
| `16p-llms_2026-08-17.txt` | `https://www.16personalities.com/llms.txt` | 2026-08-17 | `curl -s -L` |
| `16personalities-our-theory_2026-08-17.html` | `https://www.16personalities.com/articles/our-theory` | 2026-08-17 | `curl -s -L` |
| `16personalities-our-framework_2026-08-25.pdf` | `https://www.16personalities.com/articles/our-framework` | 2026-08-25 | browser print-to-PDF (see note) |
| `LeeKim2024_KCI-preview-p1_2026-08-17.pdf` / `.txt` | `https://www.kci.go.kr/kciportal/ci/sereArticleSearch/artiPreView.kci?sereArticleSearchBean.artiId=ART003137485&v=2019` | 2026-08-17 | `curl -s -L` |
| `LeeSeongbin2024_MA-thesis_GNU_2026-08-17.pdf` / `.txt` | see "Korean thesis" below | 2026-08-17 | cookie session |

`.txt` files are text extracted from the corresponding PDF; they are not separate
downloads.

### Notes that affect how these files may be used

- **`for-ai` pages carry a visible date stamp, `Last updated: June 11, 2026`.**
  Any paper published before that date could not have consulted them, so this
  page cannot be used to argue that a given author "should have known".
- **`16personalities-our-theory_*.html` contains no article text.** The page is a
  client-rendered single-page application; the retrieved HTML is 38,087 bytes but
  yields only 628 characters of text, and the terms `jungian`, `Myers-Briggs` and
  `acronym` each occur zero times. It is retained as a record of retrieval only
  and is not usable as evidence. The rendered text was read separately through a
  JavaScript-capable fetch on 2026-08-17.
- **`16personalities-our-framework_2026-08-25.pdf` is the load-bearing source for
  what the vendor claims and denies about its own lineage**, and it exists as a
  PDF for a reason. The page is client-rendered like `our-theory`: a plain `curl`
  returns navigation only, which is why two earlier attempts to check the point
  found no mention of Jung and could neither confirm nor refute it. The capture
  was therefore taken by opening the URL in a browser and printing to PDF. It is
  10 pages and carries the full article text, including the two passages the
  manuscript quotes — "Our approach has its roots in two different philosophies …
  Carl Gustav Jung" and "unlike Myers-Briggs or other theories based on the
  Jungian model, we have not incorporated Jungian concepts such as cognitive
  functions". Unlike a `curl` capture its bytes are not reproducible by
  re-running a command, so the checksum records this copy rather than certifying
  the live page; the URL and retrieval date are given so a reader can repeat the
  reading.
- **`LeeKim2024_KCI-preview-p1_*` is the first page only** (cover, abstract and
  footnotes), not the full article. The publisher releases only a one-page
  preview through KCI.
- **`16personalities.com` cannot be archived at the Internet Archive.** Its
  `robots.txt` begins `User-agent: ia_archiver` / `Disallow: /`, so no Wayback
  snapshot exists for any URL on the domain and none can be created. The
  date-stamped `for-ai` capture above is the substitute record. As of 2026-08-17
  the same `robots.txt` contained no `Disallow` directive for AI-agent user
  agents, and the retrievals above were plain `curl` requests.

### Korean thesis: retrieval procedure

The peer-reviewed article (Lee & Kim 2024, DOI `10.31008/MV.51.3`) is available in
full only behind a login. The thesis it was derived from is openly available, and
is the copy this study read.

1. RISS record: `https://www.riss.kr/link?id=T17080890`
   (UCI `I804:48003-000000035136`). Note that this record is not reachable
   through US-facing web search; the Korean database has to be queried directly.
2. Gyeongsang National University dCollection:
   `https://dcollection.gnu.ac.kr/common/orgView/000000035136`, requested with a
   persistent cookie jar (`curl -c jar -b jar`).
3. The returned HTML contains a `location.href` pointing at a generated PDF path
   under `/public_resource/pdf/`. The path embeds a timestamp and changes on every
   request, so it cannot be hard-coded; it must be fetched within the same
   session. Requesting it without the cookie returns HTML instead of a PDF.

Bibliographic details: 이성빈, master's thesis, Department of Sociology,
Gyeongsang National University, August 2024, 118 pp of body text (131 pp
including front matter); supervisor 김명희, who is the corresponding author of the
peer-reviewed article.
