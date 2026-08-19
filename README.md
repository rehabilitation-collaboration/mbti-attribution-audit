# What Do Papers Administer When They Say "MBTI"?

An attribution audit of the peer-reviewed literature. When a paper reports MBTI
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
- **Frame.** Open-access full text only. This is a declared sampling frame, not
  a workaround: figures are stated as lower bounds and the direction of the bias
  is reported.
- **Classification (planned).** Works are first coded by where their type data
  came from, because a good deal of the corpus administered nothing to anybody:
  classifiers trained on scraped labels, language models answering the
  questionnaire, studies *of* the instrument rather than *with* it. Works whose
  authors did administer something are then coded (a) the 16Personalities test,
  (b) a published MBTI form, or (c) not identifiable. Two independent coders,
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
data/corpus.csv              retrieved records, both sources, nothing dropped
data/query_log.json          queries, counts, window and word-form sensitivity, validation
data/coding_protocol.md      how each work is coded, and what is claimed for each result
data/boundary_notes.md       records the classifier could not place, inspected by hand
provenance/                  where each primary source came from, and its hash
```

### What is frozen, and what is not

`corpus.csv` fixes the *set of works*. Re-running the build a day after the
freeze left all 108 works, every DOI, every duplicate grouping and every venue
class untouched. What moved were three columns describing where a copy could be
read: one `venue`, four `oa_url` values, and one `is_oa` flag — a thesis that
had stopped being reachable overnight. Those columns are inputs to full-text
retrieval, not to any reported count, and they are a snapshot of the retrieval
date rather than a fixed value. The repository history is the record of each
move.

Primary sources themselves are not redistributed: they include a third-party
thesis in full and captures of a commercial website. `provenance/` records the
retrieval URL, date, method and SHA-256 for each, so a reader can obtain and
verify the same files. See `provenance/sources-provenance.md`.

## Run

```
pip install -r requirements.txt
python src/build_corpus.py
```

The script fails if any of the three records the corpus is known to require
goes missing, so a broken query cannot pass silently.
