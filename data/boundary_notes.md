# Boundary cases inspected by hand

`build_corpus.py` assigns a `venue_class` from metadata alone. Records it cannot
place, and records whose automatic class would misrepresent them, are inspected
individually and recorded here. Nothing is deleted from `corpus.csv`; this file
explains what a reader is looking at.

Inspected 2026-08-18, after the corpus was frozen at 118 records / 108 distinct
works.

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
