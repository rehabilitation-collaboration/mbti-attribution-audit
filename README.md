# What Do Papers Administer When They Say "MBTI"?

An attribution audit of the journal-article literature. When a paper reports MBTI
results, it may have administered the published instrument, or a free web test
that shares its four-letter codes but not its theory or its publisher, or
something it never names. This study measures how often each is the case.

The audit is prompted by cases like Bai et al. 2025 in *Scientific Reports*,
whose title reports "MBTI dimensions" while its methods state the NERIS Type
Explorer on the 16Personalities website, and whose reliability figures are
sourced to a page on the vendor's own site rather than to an independent study.
The vendor itself states that the two should not be treated as interchangeable.

This is not a claim that the MBTI is invalid; evidence syntheses on that
question already exist. The question here is narrower and, as far as we can
find, unasked: **what was actually administered.**

## Method (overview)

- **Corpus.** Works whose title or abstract mentions MBTI, Myers-Briggs or Myers
  Briggs, published 2015 onwards, whose full text also mentions any of five
  16Personalities word forms. Queried from OpenAlex and Europe PMC under one
  shared definition (`src/build_corpus.py`); every count and the exact query is
  written to `data/query_log.json` on each run.
- **Frame and corpus.** The sampling frame is the 99 works the searches returned.
  The analytic corpus of 61 is that frame conditioned on programmatic
  retrievability — not on open access: no work's licence was checked, an openly
  licensed paper can still refuse an automated request, and a document that was
  retrieved need carry no open licence. The condition is declared, not a
  workaround: observed positive counts are stated as lower bounds, and the
  direction of the bias in the proportions is stated to be unknown. Retrieval
  reached 64 of the 99 works and 44 of the 58 journal articles, of which 61 works
  and 42 journal articles entered coding; the difference is three retrieved texts
  carrying no vendor word form. Of the fourteen journal articles that could not
  be retrieved, eight are publishers refusing programmatic access and two failed
  at the TLS layer, and those refusals are recorded rather than worked around.
- **Classification (planned).** Works are first coded by where their type data
  came from, because a good deal of the corpus administered nothing to anybody:
  classifiers trained on scraped labels, language models answering the
  questionnaire, studies *of* the instrument rather than *with* it. Works whose
  authors did administer something are then coded (a) a vendor-hosted test with no
  published MBTI form identifiable from the work, (b) a published MBTI form, or
  (c) other or insufficiently identified. Both vendor pages this study quotes were retrieved in
  2026, so (a) carries no claim about the product's specification at any earlier
  date. Two independent coders,
  kappa reported, disagreements adjudicated.
- **Secondary measures (planned).** What the vendor's site is cited *as* — the
  instrument, the theory, population norms, reliability evidence, a scraping
  target, or a passing mention — and whether the work states outright that the
  vendor's test and the MBTI are the same instrument.
- **Rules before results.** `data/coding_protocol.md` fixes the codes, the
  boundary cases, the sensitivity analyses, and what the manuscript claims under
  each result pattern. It was written before any work was classified, and it
  requires both measures to be reported whichever way the numbers fall.

## Layout

```
src/build_corpus.py          corpus construction; re-measures every reported count
src/fetch_fulltext.py        programmatic retrieval, one document per work
tests/                       regression tests for the normalisation and grouping rules
data/corpus.csv              retrieved records, both sources, nothing dropped
data/query_log.json          queries, counts, window and word-form sensitivity, validation
data/coding_protocol.md      how each work is coded, and what is claimed for each result
data/fulltext_log.csv        what was retrieved, from where, and why a failure failed
data/boundary_notes.md       records inspected by hand: duplicates, false positives, edge venues
provenance/                  where each primary source came from, and its hash
```

### What is frozen, and what is not

`corpus.csv` fixes the *set of works*, not the metadata saying where to read
them. Re-running the build the day after the freeze left every record, DOI and
venue class untouched, and moved three columns that only describe where a copy
can be found: one `venue`, four `oa_url` values, and one `is_oa` flag — a thesis
that had stopped being reachable overnight. Those columns feed retrieval, not
any reported count, and they are a snapshot of their retrieval date.

The count of distinct works is a different matter, and it was corrected: it read
108 until the grouping rule was found to split a work across its own versions,
and it is 99. That is a change to a rule rather than drift in the data — the 118
retrieved records never changed — and it is recorded in `data/boundary_notes.md`
and held by a test. The repository history is the record of both kinds of change.

Primary sources themselves are not redistributed: they include a third-party
thesis in full and captures of a commercial website. `provenance/` records the
retrieval URL, date, method and SHA-256 for each, so a reader can obtain and
verify the same files. See `provenance/sources-provenance.md`.

## Run

```
pip install -r requirements.txt
python src/build_corpus.py     # corpus and query log; re-measures every count
python src/fetch_fulltext.py   # one document per work into fulltext/ (git-ignored)
pytest                         # regression tests
```

`build_corpus.py` fails if any of the three records the corpus is known to
require goes missing, so a broken query cannot pass silently.

The tests hold faults that actually occurred rather than hypothetical ones: a
title normaliser that emptied every non-Latin title, and a grouping rule that
counted a work once per DOI and so split Zenodo versions and preprint/article
pairs. Both were found after the corpus had been published, and both moved a
reported count. Each test fails if its fault is reintroduced.
