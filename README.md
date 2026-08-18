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
- **Classification (planned).** Each work is coded as (a) administered
  16Personalities, (b) administered a published MBTI form, or (c) instrument not
  identifiable. Coding rules are written before coding begins; two independent
  coders, kappa reported, disagreements adjudicated.
- **Secondary measure (planned).** Papers citing the vendor's own web pages as
  psychometric evidence.

## Layout

```
src/build_corpus.py          corpus construction; re-measures every reported count
data/corpus.csv              retrieved records, both sources, nothing dropped
data/query_log.json          queries, counts, window sensitivity, validation
data/boundary_notes.md       records the classifier could not place, inspected by hand
provenance/                  where each primary source came from, and its hash
```

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
