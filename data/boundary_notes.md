# Boundary cases inspected by hand

`build_corpus.py` assigns a `venue_class` from metadata alone. Records it cannot
place, and records whose automatic class would misrepresent them, are inspected
individually and recorded here. Nothing is deleted from `corpus.csv`; this file
explains what a reader is looking at.

First inspected 2026-08-18, when the corpus held 118 records and was read as 108
distinct works. The distinct-work count became **99** on 2026-08-19, when
full-text retrieval surfaced the same article arriving twice under different
DOIs; the last section explains what collapsed and why. The record count, 118,
has not changed.

## Not scholarly literature (1)

**"LibGuides: MBA 750 Organizational Behavior KM: Related materials - MBTI"**
(2019, no DOI, OpenAlex type `libguides`). A university library research guide,
not a publication reporting results. Classed `non_scholarly` and excluded from
every analysis. It is retained in `corpus.csv` so the count of retrieved records
matches what the query returns.

## Journal article with no venue metadata (1)

**"Effect of Dominant Personality Traits on Team Roles"** (2021,
`10.36648/2471-9854.21.s3.91`). OpenAlex records `type: article` but
`primary_location.source` is `None`, so no venue name is available and the
automatic class falls through to `unclassified`. Checked by hand:

- Crossref returns HTTP 404 for the DOI, i.e. it is not registered there.
- The landing page is `clinical-psychiatry.imedpub.com`, identifying the venue
  as *Clinical Psychiatry* (iMedPub), a publisher widely listed as predatory.

It is left as `unclassified` rather than promoted to `journal_article`: the
record asserts journal publication but carries none of the metadata that the
class is meant to certify. Phase 2's coding protocol decides whether it enters
the main analysis; either way the decision is one record and will be reported.

## Venues registered as journals that are effectively proceedings

Not individually annotated, but noted here because it affects how the
peer-reviewed boundary should be read. Several `journal_article` records sit in
venues that publish conference output under a journal ISSN — *Proceedings of the
ACM on Human-Computer Interaction*, *Proceedings of the Design Society*, *GBP
Proceedings Series* — and several others are in series that publish conference
papers in journal form (*Highlights in Science Engineering and Technology*,
*Advances in Economics Management and Political Sciences*, *Applied and
Computational Engineering*, *Communications in Humanities Research*). The first
group is peer reviewed by the usual standards of its field; the second is
weaker. Phase 4 reports the main analysis on `journal_article` and a sensitivity
analysis that varies this boundary, rather than asserting a single answer.

## A retrieved work whose text does not contain the word form

`fetch_fulltext.py` checks every retrieved document against the word forms the
corpus was built on. Three works cleared the length test without carrying one,
and one of the three is not a retrieval problem at all.

**"The Relationship between Carl Jung's Eight Cognitive Functions and Social
Entrepreneurial Intention"** (2026, `10.25236/fsst.2026.080105`) retrieves in
full — 37,970 characters of published PDF, title page through reference list. It
names the MBTI 29 times and Myers 5 times. It contains no `16personalities`, no
`NERIS` and no `Type Explorer`; the digits "16" appear only in the ISSN, the
volume line, and "16 groups of the same 100 people". Its reference list is
complete and cites none of the vendor's pages.

The corpus includes a work when its full text mentions a 16Personalities word
form. This work does not, and OpenAlex's `fulltext.search` returned it anyway.
It is a false positive of the query — not a paper that failed to report its
instrument, which is a different thing and would be a finding.

The other two are unsettled rather than settled: a 3,705-character OhioLink
record page for "Personality Types Among Athletic Trainers", and a
6,495-character Hungarian document that does not mention the MBTI either. Both
are short enough that what came back may not be the article.

**What this measures.** Of the 64 works whose retrieved text was long enough to
check, 61 carry a word form and 3 do not. That is an upper bound of 4.7% on the
query's false-positive rate, with one case confirmed by reading. The 35 works
whose text could not be retrieved cannot be checked either way, so the true rate
is unknown and the bound is what gets reported. Nothing is deleted: the record
stays in `corpus.csv`, and it is left out of the coding because its text cannot
carry a code, which the log states as `no_word_form`.

The negative control run in Phase 1 cannot catch this. Searching a typo and
getting zero results shows the query does not match noise; it says nothing about
whether the index behind the query is accurate for the terms that do match.

## The same work under more than one identifier

Until 2026-08-19 records were grouped into works by DOI where one existed, and
by normalised title otherwise. That is wrong for this corpus. Zenodo and OSF
mint a DOI per deposited version, and a preprint carries a different DOI from
the article it becomes, so eight works were being counted as eighteen records
and the distinct-work count read 108 where it is **99**. Full-text retrieval
exposed it: the same article came back twice under two keys.

Records are now joined transitively on DOI **or** normalised title, and each
group takes a single venue class by the priority in `build_corpus.py` — a work
that reached us as both a preprint and an article is an article.

**The main analysis is unaffected.** All 58 journal articles were already
distinct works: in every mixed group the published record is the one the
priority keeps, so the collapse removed preprint and repository copies (14 → 7
and 12 → 10) and no journal article.

- **Can ChatGPT Assess Human Personalities? A General Evaluation Framework** — kept as `conference`
  - `10.18653/v1/2023.findings-emnlp.84` · 2023 · conference
  - `10.48550/arxiv.2303.01248` · 2023 · preprint · arXiv
- **Evidence-Based Frameworks for University Major Selection…** — kept as `preprint`
  - `10.5281/zenodo.20131632` and `10.5281/zenodo.20131633` · 2026 · two Zenodo versions
- **Open Models, Closed Minds? On Agents Capabilities in Mimicking Human Personalities…** — kept as `conference`
  - `10.1609/aaai.v39i2.32125` · 2025 · conference · AAAI
  - `10.48550/arxiv.2401.07115` · 2024 · preprint · arXiv
- **Personality Types of Medical Students in Terms of Their Choice of Medical Specialty** — kept as `journal_article`
  - `10.2196/60223` · 2024 · retrieved from both sources
  - `10.2196/preprints.60223` · 2024 · preprint
- **Persönlichkeitstests im beruflichen Kontext** — kept as `repository`
  - `10.5281/zenodo.21517801` and `10.5281/zenodo.21517802` · 2026 · two Zenodo versions
- **Study Future Compass - Volume 2…** — kept as `repository`
  - `10.5281/zenodo.20521076` and `10.5281/zenodo.20521077` · 2026 · two Zenodo versions
- **The MBTI, cultural creation and self-conceptions…** — kept as `preprint`
  - `10.31235/osf.io/c9raf`, `_v2`, `_v3` · 2024-2025 · three OSF versions
- **The Self-Perception and Political Biases of ChatGPT** — kept as `journal_article`
  - `10.1155/2024/7115633` · 2024 · Human Behavior and Emerging Technologies
  - `10.48550/arxiv.2304.07333` · 2023 · preprint · arXiv

### One pair that is not a duplicate

Two Cyrillic titles were briefly grouped together, and they are different
studies: "Идентифициране на личностните типове на кметовете в местното
самоуправление в България по типологията на Майерс – Бригс" (2024, Bulgarian
Portal for Open Science) and "ПСИХОЛОГІЧНІ ТИПИ ЯК ІНСТРУМЕНТ ПІДВИЩЕННЯ
МОТИВАЦІЇ ТА КОМАНДНОЇ ЕФЕКТИВНОСТІ" (2025, a Ukrainian university's economic
sciences series). They stay separate.

They matched because the title normaliser stripped everything outside
`[a-z0-9]`, which empties a title written entirely in a non-Latin script — and
two empty keys are equal. The same fault ran the other way: such a work could
never be recognised as a duplicate of its own other version, because an empty
key carries no information to match on.

**Measured, so the size of the fault is not overstated.** Applying the old
normaliser to all 99 titles empties exactly **two** (the Bulgarian and Ukrainian
titles above), so the works actually at risk were 2%, not the 27% of titles that
merely contain a non-ASCII character — a Turkish or Czech title keeps enough
Latin letters to survive. Normalisation is now Unicode-aware regardless.

Titles are also stored as the work states them rather than as the API encodes
them: two carried a literal `&amp;` ("Personality Type &amp; Fruit and Vegetable
Consumption", "Bleed in Dungeons &amp; Dragons").


## A record whose metadata says journal, and whose text is a conference abstract

**"Exploring Associations Between Personality Type & Fruit and Vegetable
Consumption"** (2025, `10.1016/j.jand.2025.06.390`) carries `venue_class =
journal_article`: OpenAlex records it in the *Journal of the Academy of
Nutrition and Dietetics*, which is a journal. Its retrieved text is not an
article. It opens "TUESDAY, OCTOBER 14, 2025", bundles several unrelated
presentations in one PDF, and states its objective as "reviewing the abstract
content, attendees will be able to describe…" — the continuing-education wording
of a conference abstract supplement.

This matters in two ways, and both are handled in `coding_protocol.md` rather
than by editing the corpus:

1. **Consistency.** Koshiro 2025 is excluded from the main analysis because its
   metadata says `conference_abstract`. This record is the same kind of document
   and its metadata does not say so, so venue metadata alone cannot enforce the
   peer-reviewed boundary. §3.6 now has coders record the evidence when a
   retrieved text is an abstract, and S6 varies the boundary on that evidence.
2. **Contamination.** One retrieved file can hold several works' text. The
   word-form and MBTI checks in `fetch_fulltext.py` run over the whole file, so
   in principle a neighbouring abstract could satisfy them for a record that
   does not mention the vendor at all. Here it does not — the matching sentences
   are inside the target abstract — but the risk is real and coders are told to
   read only the target work's own section.

Nothing is deleted. The record keeps `journal_article` because that is what its
metadata says, and moving it after seeing it would be exactly the boundary-shift
the protocol forbids.
