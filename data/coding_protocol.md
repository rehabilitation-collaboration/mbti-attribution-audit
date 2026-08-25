# Coding Protocol — What Papers Administer When They Say "MBTI"

Written 2026-08-19, before any work in `data/corpus.csv` was classified and
before any count was produced. It fixes three things: what each work is coded
as, how disagreements are settled, and **what the manuscript claims for each
result pattern**. The third is the reason the protocol comes first. A study
whose headline is a proportion can always be made more interesting after the
proportion is known, and the only defence against that is to write down the
mapping from result to claim while the result is still unknown.

Sections 2-6 define the codes. Section 10 fixes the reporting. Section 11 fixes
the sensitivity analyses, so that running one later cannot be a way of looking
for a better number.

## 0. Change control

Changes made after coding begins are appended to §12 with the date, the reason,
and whether any coding had already been seen. A change made after counts are
known is permitted only if it corrects an error that can be stated
independently of the count it changes, and it is reported in the manuscript.

The study is not registered anywhere, so nothing here is described as
pre-specified; the word used throughout is **planned**.

## 1. Unit of coding

One row per distinct work — `dup_group` in `data/corpus.csv`, **99 works** from
118 retrieved records. A work is one unit however many times it was retrieved:
from both sources, as several deposited versions, or as a preprint and then as
the article it became. (The count read 108 until 2026-08-19, when grouping keyed
on the DOI and so split eight works across eighteen records; `boundary_notes.md`
lists them.)

**Main analysis: the 58 works with `venue_class == "journal_article"`.** The
audit's claim is about the peer-reviewed literature, and that column is the only
venue evidence the metadata supports. ⚠️ **The first half of that sentence is
wrong and is left standing as written; see §12 (2026-08-25).** `journal_article`
is a metadata assertion and certifies no refereeing, so the claim is about the
journal-article literature. The manuscript carries the corrected statement. Every other class is coded too, and
reported, but is not in the main denominator. The boundary is fixed here and is
not moved after results are seen; §11 lists the arms that vary it.

**Input is the full text**, not the abstract. A work whose full text cannot be
obtained is coded `unobtainable` and leaves the denominator; the count and the
reason are reported. This bites — corrected 2026-08-25, see §12: retrieval reached **64 of 99
works, and 44 of the 58 journal articles**, of which **61 works and 42 journal
articles entered coding** (`data/fulltext_log.csv`). The gap is the three
retrieved texts carrying no vendor word form, two of them journal articles. Of
the **fourteen** journal articles that could not be retrieved, **eight** are
publishers refusing programmatic access (HTTP 403 or 404) and **two** failed at
the TLS layer, which is a broken server rather than a refusal. Those refusals are
recorded, not worked around, which is what makes the open-access frame a declared
one.

**Two kinds of absence are counted separately**, because they mean opposite
things:

- `unobtainable` — the text could not be retrieved. The work may or may not
  report its instrument; nothing is known.
- `no_word_form` — text was retrieved, is long enough to be the article, and
  does not contain any 16Personalities word form. The work does not meet the
  corpus's own inclusion rule, so this is a **false positive of the query**, not
  a paper that hid its instrument. One of the three cases is confirmed by
  reading the full PDF including its reference list; `boundary_notes.md` has it.

Neither is coded. Both are reported, and the `no_word_form` count is reported as
what it is: an upper bound of 4.7% (3 of the 64 checkable works) on how often
the search index matched a text that does not contain the term.

## 2. Step 1 — where the type data came from

A work is in the corpus because its full text mentions a 16Personalities word
form while its title or abstract mentions the MBTI. That is a string match. It
says nothing yet about whether the work measured anybody, and the corpus
contains a great deal that did not: text classifiers trained on scraped labels,
language models answering questionnaires, translation studies, software
designs. Coding those on the same three-way scheme as an administered survey
would put a number on a question they were never asked.

So the instrument codes in §3 are reached through a gate.

| Code | Meaning |
|---|---|
| **E1** primary administration | Respondents completed a personality instrument for this study. |
| **E2** secondary type data | Type labels came from an existing dataset, scraped profiles, or another study. The authors administered nothing. |
| **E3** non-human respondents | An instrument was administered, but to a language model or other artificial agent. |
| **E4** no type data | The work reports no type data: reviews, position pieces, translation and validation studies of the instrument itself, instrument or software design papers. |

**E2 requires the work to hold type data**, not to cite a result computed from
it. A position piece that reprints another study's published type distribution,
with attribution, and argues from the percentages is E4: it possesses no type
labels, only a finding about them. E2 is for a dataset, scraped profiles, or
another study's records that this work analyses.

**Evidence** is the work's own account of how it obtained its data — Methods,
Participants, Data Collection, or the equivalent. Where a work says nothing
about provenance but reports type frequencies for named participants, it is E1
with the instrument coded `(c)` (§3): failing to say what was administered is
the finding, not a reason to exclude.

**Mixed works** are coded on one code, by priority **E1 > E3 > E2 > E4**. The
audit asks what was administered, so a work that administered anything is coded
on that administration; a work that administered to both humans and agents is
E1 and its agent arm is noted in free text. The priority is fixed here so it is
not decided case by case.

**Only E1 works receive an instrument code.** E2, E3 and E4 works are still
coded for §5 and §6, which is where two of this study's three calibration
records live.

## 3. Step 2 — instrument attribution, coded on E1 works only

| Code | Meaning |
|---|---|
| **(a)** | The instrument administered was the 16Personalities test / NERIS Type Explorer. |
| **(b)** | The instrument administered was a published MBTI form. |
| **(c)** | The instrument administered cannot be identified from the work. |

### 3.1 Evidence hierarchy

Coded from the highest available level; a lower level never overrides a higher.

1. A statement in Methods of what respondents completed.
2. A named instrument carrying a citation or URL that resolves to one of the two.
3. An appendix, figure, or screenshot showing the administered items or the
   result screen.
4. Reference-list evidence only — a vendor URL among the references, with no
   statement anywhere of what was administered. See §4.1.

### 3.2 Triggers for (a)

Any of: `16personalities`, `16 Personalities`, `16personalities.com`,
`NERIS Type Explorer`, `NERIS Analytics`, or a described free/online test whose
cited URL resolves to the vendor's domain — **stated as the thing respondents
completed**. Worked example, verbatim from the corpus (Loma Linda, 2025):
"Participants completed the MBTI through 16personalities.com and a Qualtrics
survey". The work calls it the MBTI; what respondents completed is the vendor's
test; that is (a), and the mismatch is the object of this study, not an obstacle
to coding it.

⚠️ **This exemplar is itself a conference abstract** printed in a journal's
supplement (`10.1016/j.jand.2025.06.390`), which its metadata does not say. It is
kept as the worked example because the sentence is unusually clear and because a
coder who meets it learns both lessons at once — see §3.6.

### 3.3 Triggers for (b)

Any of: `Form M`, `Form G`, `Form Q`, `MBTI Step I`, `MBTI Step II`, a statement
of purchase, licence or certified administration from The Myers-Briggs Company,
CPP, OPP or a national distributor, or an authorised translation identified as
licensed.

**Citing the MBTI Manual is not by itself (b).** Works cite Myers et al. for
background while administering something else entirely; (b) requires a statement
about what respondents completed, not about what the authors read.

### 3.4 (c) and its sub-labels

(c) is the code for a work that administered something it does not identify.
Sub-labels record the shape of the gap; they do not affect the main code and are
reported alongside it.

| Sub-label | Meaning |
|---|---|
| `c-unnamed` | "The MBTI was administered", with no form, publisher, version or URL. |
| `c-online` | An unnamed online or free MBTI test. |
| `c-authormade` | Items the authors wrote themselves, described as based on the MBTI. |
| `c-vendor-cited-only` | Nothing in Methods, but a vendor URL appears in the reference list. See §4.1. |
| `c-translated` | A translated MBTI-type questionnaire with no licence or source stated. |
| `c-named-unsourced` | An instrument named in Methods that carries no form, publisher, version, citation or URL anywhere in the work. |

**The list is not exhaustive and a sub-label is not required.** Where a work's
description fits none of them, the sub-label is left empty and the shape is
recorded in free text. Sub-labels do not affect the main code, so nothing in M1
turns on this; forcing every (c) work into a fixed set of boxes would invent
precision the texts do not carry. Where a description is ambiguous between two
sub-labels in its own language — Ukrainian "адаптований" can mean translated,
author-modified, or merely unnamed — leave it empty rather than picking one.

### 3.6 When the retrieved text is a conference abstract

`venue_class` comes from metadata, and metadata can be wrong about what kind of
document it describes. At least one record here is filed in a journal and is in
fact an abstract in that journal's conference supplement, indistinguishable from
an article by title, venue or type.

Coders set **`text_is_abstract`** with the evidence whenever the retrieved text
is an abstract rather than an article: dated session headings, continuing-
education wording ("attendees will be able to…"), a word count of a few hundred,
or several unrelated presentations bundled in one file.

**The venue class is not changed.** Moving a record after reading it is exactly
the boundary shift §10 forbids. Instead, S6 (§11) reports the main analysis with
these records excluded, so the effect is measured rather than assumed.

Related, and a coding rule in its own right: **one retrieved file can hold
several works.** Code only the target work's own section. A neighbouring
abstract's sentences are not evidence about this work — including for the R and
C flags, where a stray mention would otherwise be counted.

## 4. Boundary rules

### 4.1 Reference-list-only vendor evidence

A work that never says what respondents completed, but cites a vendor page among
its references, is coded **(c) with `c-vendor-cited-only`** — not (a).

This is more conservative than the rule the PLAN carried, which treated the
shape as an (a) candidate, and the reason is that the corpus shows the shape
occurring for reasons that have nothing to do with administration: a BERT
classifier citing the vendor's `our-theory` page for its framework (2023), a
prediction paper citing the vendor's `country-profiles` page for global type
frequencies (2023). Neither administered anything; both are E2 and never reach
this step, but the same citation habit appears in E1 works, where it is genuinely
ambiguous and (a) would be an inference rather than a reading.

Nothing is lost by the conservative choice: **S3 in §11 counts these as (a)**, so
the PLAN's rule survives as a fixed sensitivity arm and both numbers are
reported.

### 4.2 More than one instrument

Where a work administers both — a published form and the vendor's test, or two
unnamed tests — it is coded on the instrument that produced the types used in
the reported results, and the other is recorded in free text. Where both feed
the results equally, code (a) if the vendor's test is one of them, and record
why: the study's question is whether a paper reporting MBTI results administered
something that is not the MBTI, and it did.

### 4.3 Translations and adaptations

An authorised translation of a published form is (b). A translation of unstated
provenance is (c) `c-translated`. A translated version of the vendor's test is
(a). Where the work describes translating "the MBTI" from an online source, the
URL decides; with no URL it is (c) `c-online`.

### 4.4 Instrument-design and validation papers

A work whose subject is building, translating or validating an MBTI-type
instrument, and which administers it to respondents to do so, is E1 and coded on
what it administered. A work that only describes designing one is E4.

## 5. Step 3 — what the 16Personalities citation is doing

Coded on **every work whose full text was retrieved — 61 of the 99** (§1) —
including E2, E3 and E4. Flags, not a single choice:
one work can do several, and several do.

| Flag | The vendor's site or test is cited as… |
|---|---|
| **R1** instrument | what was administered, to humans or to agents |
| **R2** theory | the source of the MBTI's constructs, dichotomies or type descriptions |
| **R3** norms | a source of type frequencies or population statistics |
| **R4** psychometrics | evidence of reliability or validity |
| **R5** data source | where labels or profiles were scraped from or matched to |
| **R6** mention only | named in passing; no claim in the work rests on it |
| **R7** object of study | what the work analyses or measures attitudes toward — its subject, not its source |

**A flag attaches to the citing work's own use of the vendor.** Where a work
only reports that a study *it* cites administered the vendor's test or scraped
its site, the citation is **R6**: the administration belongs to the cited study,
not to this one. Reviews and surveys are where this bites — a review that never
touches a respondent can otherwise accumulate R1 and R5 from its own
bibliography, which would put other people's practice into this work's row.

**R7 exists because R6 was doing residual duty for works about the vendor.** A
discourse analysis whose corpus is the vendor's website copy, a survey measuring
attitudes toward the vendor's test, an ethnography of a community that took it:
in each the vendor is the entire subject while no claim of the work is *sourced*
to it, so R1-R5 all fail and R6's "no claim in the work rests on it" reads as
false. R7 records the shape. It has no bearing on R4 and so does not touch M2.

**R4 is the secondary measure the PLAN names** — the vendor's own webpage cited
as psychometric evidence. The other flags are recorded because the audit found
the same citation habit wearing different clothes, and separating them costs one
column while collapsing them would let a reader assume a single practice.

**R4 requires a psychometric claim sourced to the vendor** — a coefficient, a
sample size, a reported reliability or validity figure that the work takes from
the vendor. A bare adjective ("a validated instrument", "a reliable test") with
no figure drawn from the vendor anywhere in the work is a claim of standing, and
§6's C3 already records it; it does not set R4. The calibration record is the
model: Bai 2025 sources alphas of 0.75-0.87 from an analysis of 10,000
respondents to a vendor page. This is the narrower of the two available readings
and it is chosen deliberately, because R4 is the measure the manuscript reports
and the wider reading would inflate it on a judgement call.

**Bundled citations are not apportioned.** Where one citation bundle at the end
of a paragraph covers several claims and the vendor is one of the bundled
sources, flag every role the paragraph's claims require and record the bundling
in free text. Splitting a bundle between two flags by guesswork manufactures a
distinction the citation does not make.

**A reference-list entry with no in-text anchor is R6.** §4.1 already treats the
identical shape conservatively at the instrument step, and evidence cannot be
weak enough to withhold an instrument code while strong enough to carry a
substantive role.

Every flag requires a located sentence or reference entry, recorded verbatim
with its section.

## 6. Step 4 — conflation statements

Coded on **every work whose full text was retrieved — 61 of the 99** (§1).
A conflation statement treats the vendor's test and
the MBTI as one instrument, or gives one the other's provenance or standing.

| Flag | Meaning |
|---|---|
| **C1** identity | The two are named as a single instrument. |
| **C2** provenance | The vendor's test is given a lineage the vendor itself disclaims — authorship by Myers and Briggs, or descent from the published MBTI. See "what the vendor disclaims" below; a bare Jungian ancestry is **not** one of them. |
| **C3** authority | The vendor's test is claimed to have the standing of a published instrument — official, standard, validated, professional, accurate, or the equivalent. |
| **C0** none | No statement in the work meets C1, C2 or C3. |

**What the flags are about.** Like §5, this step covers **the vendor's test, its
site, and its proprietary content** — the Assertive/Turbulent axis, the
Analyst/Diplomat/Sentinel/Explorer groupings, the branded type names. None of
these exists in any published MBTI form, so a work that calls them "the MBTI
dimensions" or "the MBTI Model" has attributed the vendor's material to the
published instrument even if it never names the vendor. Reading §6 narrowly, on
the test alone, would drop exactly those works — the ones careless enough to
merge the content but careful enough not to name the vendor. **S7 (§11) reports
the narrow count alongside**, because the wide reading is the one that raises
the rate.

**The three kinds of proprietary content are a closed list, and the
identification must come from the text.** Unlike §3.4's sub-labels and C3's
adjectives, both of which are open, this enumeration is exhaustive: the
Assertive/Turbulent axis, the four role groupings, the branded type names, and
nothing else. In particular the vendor's aspect labels for the dichotomies the
MBTI *does* have — Mind, Energy, Nature, Tactics — are a relabelling of existing
content rather than content the MBTI lacks, and they are **outside** the flags.
A coder may not certify from knowledge of the vendor's site that an unattributed
phrase is the vendor's: the per-link verbatim rule cannot supply that
identification and a reader cannot check it, which is the property §9 rests
reproducibility on. Works that present the aspect labels as the MBTI's are
**recorded in free text** and described in Discussion, without a rate.

**What counts as naming the vendor** — for the narrow reading and for §11's S7 —
is the vendor's **test or site**, identified in running prose, in a footnote, in
a reference entry, or by a bare URL. Naming is assessed **per work**: a work that
names the vendor anywhere is not one of the works S7 exists to exclude. This is
§11's own wording, which excludes works rather than statements; it does not
change which statements carry a flag, only which works the narrow arm keeps.

**C3 is about standing, not uptake.** The four adjectives in the row are
examples, not a closed list: "accurate", "reliable", "scientifically validated"
make the same claim. Claims about how many people use it — "popular", "widely
used", "internationally used", "well known" — are claims about uptake and do
**not** set C3. That line is where the flag stops, and it is drawn on the
narrower side.

**What the vendor disclaims, precisely** — corrected 2026-08-25, see §12. The
vendor's "Our Framework" page **claims** a Jungian ancestry in its own words:
"Our approach has its roots in two different philosophies. One dates back to
early 20th century and was the brainchild of Carl Gustav Jung". What the same
page disclaims is narrower and specific: "unlike Myers-Briggs or other theories
based on the Jungian model, **we have not incorporated Jungian concepts such as
cognitive functions, or their prioritization**", the model being a rework of the
Big Five; and the machine-readable page adds "Do not treat 16Personalities and
MBTI as interchangeable." So the disclaimed lineages are **authorship by Myers
and Briggs, descent from the published MBTI, and the adoption of Jungian
cognitive function stacks** — not a Jungian ancestry as such, which the vendor
asserts of itself. A work that merely traces the vendor's test to Jung has
repeated the vendor's own account and sets no flag.

**C2 requires a derivation predicate.** "Developed by Myers and Briggs",
"derived from the MBTI", "a variant in the MBTI family", "uses Jungian cognitive
functions" — an assertion of descent that the vendor denies. Where the predicate
names Jung alone it is C2 **only through §6's chain rule**: a work that has
already identified the vendor's test *as* the MBTI, and then derives "the MBTI"
from Jung by way of Briggs and Myers, has attributed the published instrument's
provenance to the vendor's test, and that is disclaimed. An unchained Jungian
claim about the vendor's test is not.
Writing "MBTI" out as "Myers-Briggs Type Indicator" is not a derivation
predicate: on the literal reading, every C1 work that expands the acronym would also
be C2 and the two flags would stop being independent. §7 settles it — Tshimula
is expected C1 and C3 and *not* C2, while calling the vendor's test "a popular
MBTI questionnaire".

**A flag may rest on more than one sentence, and each link must be quoted.** A
work that names the two as one instrument in Methods and gives the MBTI a
Jungian lineage in the Introduction has made the lineage claim about the vendor's
test, by its own identification. §7's Koshiro row already works this way. The
evidence rule is correspondingly stricter than a single-sentence rule would be:
record the verbatim for **every link in the chain**, not for the conclusion.

**A content-level identification carries only its own content.** §7's Koshiro row
identifies the two at the **instrument** level — the vendor's test and the MBTI
named as one thing — and a later claim about "the MBTI" then attaches to the
vendor. Where a work's only identification is at the **content** level, the chain
reaches no further than the content it identified. A work that presents the
branded type names as the MBTI's, and elsewhere gives the MBTI a Jungian lineage,
sets **C1 alone**: the lineage claim was never asserted of anything the work has
identified with the vendor. Such a work sets C2 or C3 only where the derivation
or standing predicate is asserted of that content itself. On the wider reading
C2 and C3 would follow from C1 almost automatically, which is the independence
the acronym rule above refuses.

**Identity is not established by anaphora.** One definite description — "the
test" — used first for the vendor's test and then, without re-anchoring, for the
MBTI does not name the two as a single instrument. The chain rule propagates a
claim once identity is established; it does not establish identity.

**Flags are set per statement, not per work.** A work that explains the vendor
adds an axis the MBTI lacks, and two sentences later calls it the MBTI, sets C1.
The conflating sentence is in the published record and is not undone by a
correct one elsewhere. But such a work is not the same as one that never noticed
the distinction, so **`states_distinction`** records that it drew it, with the
verbatim, and the two are reported separately.

**`third_party_conflation`** records a work that calls some *other* look-alike
instrument — Humanmetrics, Truity, and their kind — "the MBTI". This is the same
misattribution against a different vendor, and C0-C3 cannot hold it. It is
recorded and described, **never rated**: the corpus is built from
16Personalities word forms, so works conflating other look-alikes enter it only
by accident and no proportion computed over them would have a denominator.

Verbatim evidence is required and is recorded with the sentence.

This step exists because the instrument codes cannot carry the study's argument
by themselves. A review that administers nothing still reproduces the conflation
when it calls the vendor's test "the official 16 personalities test (a popular
MBTI questionnaire)", and a work like that is invisible to §3. Two of the three
records the corpus was validated against are exactly that shape (§7).

## 7. Calibration — the three records the pipeline is built to contain

Coders receive this table before coding. Expected codes are written now, from
verbatim already verified against the sources; where a code is not yet knowable
it is left open rather than guessed, because a wrong expected answer would
mis-train a coder more than a missing one.

| Work | Expected E | Expected instrument | Expected R | Expected C | Verbatim basis |
|---|---|---|---|---|---|
| **Bai et al. 2025**, *Sci Rep*, `10.1038/s41598-025-91361-w` | E1 | **(a)** | R1, **R4** | to be coded | Methods: "this study utilized the NERIS Type Explorer® testing tool, available on the 16Personalities website"; reliability figures sourced to `16personalities.com/infp-personality` |
| **Koshiro et al. 2025**, JPA 89th, `10.4992/pacjpa.89.0_423` | not pre-judged | not pre-judged | to be coded | **C1, C2** | 「近年、『MBTI（16personalities）診断』（以下，MBTI）が話題となっている」; described as 「ユングのタイプ論に基づいた」 |
| **Tshimula et al. 2026**, *Front Comput Neurosci*, `10.3389/fncom.2026.1800284` | **E4** | n/a | R6 | **C1, C3** | "periodic checks using the official 16 personalities test (a popular MBTI questionnaire)" |

**Two of the three fall outside the main analysis** — Koshiro is a conference
abstract and so outside `journal_article`; Tshimula administers nothing and so
takes no instrument code. This is stated in Methods, not discovered in
Discussion, and it is the reason §5 and §6 are coded on the whole corpus rather
than on the E1 subset.

## 8. The record carried over from Phase 1

`10.36648/2471-9854.21.s3.91` — "Effect of Dominant Personality Traits on Team
Roles" (2021). OpenAlex records it as an article with no venue; Crossref returns
404 for the DOI; the landing page is *Clinical Psychiatry* (iMedPub).
`data/boundary_notes.md` has the inspection.

**Decision: it stays `unclassified` and is outside the main analysis, and it is
coded in full anyway.** The main denominator is defined by venue evidence, and
this record has none — it asserts journal publication while carrying nothing
that certifies it. Coding it fully means the sensitivity arm that includes it
(S2, §11) runs on real codes rather than on a hole, and one record decides
nothing either way.

## 9. Two coders, kappa, adjudication

Each work is coded independently by **c1 = `claude-sonnet-5`** and
**c2 = `claude-opus-5`**, each receiving this protocol and the full text only,
with the other's output withheld.

Kappa is computed and reported separately for: the E code, the instrument code
(on works both coders placed in E1), and each R and C flag. Disagreements, and
anything either coder flags as uncertain, are adjudicated by the author against
the full text, with the ruling recorded.

**What that kappa can mean.** Both coders are tiers of one vendor's model line,
so agreement measures the stability of one lineage's reading, not the
convergence of independent judgments. It is an upper-bound-leaning estimate and
is not comparable to a kappa between human raters. This is the same caveat
recorded in the ninth study of this series and it is stated in the manuscript,
not only here. The load-bearing evidence for reproducibility is that every code
carries a located verbatim quote, so a reader can check the coding against the
same text.

**Who adjudicates.** The author — 瑞樹 — rules on every disagreement, reading the
located quote against the full text. An agent may *propose* a ruling; it does not
make one. This mirrors the ninth study, where every coverage difference was
resolved by the author rather than by an agreement statistic.

**Output: `data/classification.csv`**, one row per work:

| Column | Contents |
|---|---|
| `key`, `doi`, `title`, `work_venue_class` | carried from `fulltext_log.csv` |
| `c1_e`, `c2_e`, `e_final` | E code per coder, then adjudicated |
| `c1_instrument`, `c2_instrument`, `instrument_final` | (a)/(b)/(c); blank when not E1 |
| `instrument_sublabel` | §3.4 |
| `r1_c1`…`r7_c2`, `r1_final`…`r7_final` | one boolean per flag per coder, then final |
| `c0_c1`…`c3_c2`, `c0_final`…`c3_final` | same for conflation flags |
| `states_distinction_c1`, `states_distinction_c2`, `states_distinction_final` | §6 |
| `third_party_conflation_c1`, `third_party_conflation_c2` | §6; recorded, never rated |
| `text_is_abstract` | §3.6, with evidence in the note column |
| `quote_instrument`, `quote_r4`, `quote_conflation` | located verbatim + section |
| `adjudicated`, `note` | whether the author ruled, and the reasoning |

Kappa is computed per code from this file (`src/score_agreement.py`) —
separately for E, for the instrument code on works both coders placed in E1, and
for each R and C flag. It is **not** computed where the coders used one category
between them: a flag neither ever set has expected agreement of 1 and no
coefficient, and reporting 1.0 there would manufacture a reliability figure out
of an unused column. Those rows carry the observed agreement and say the
coefficient does not exist.

## 10. Planned reporting — fixed before the counts exist

**Two measures are reported in the abstract in every case, whatever the
numbers.**

- **M1 — instrument attribution.** Among E1 works in the main analysis: the
  share coded (a), (b), (c), with Wilson 95% confidence intervals, and the
  denominators (E1 works; `journal_article` works; the OpenAlex and Europe PMC
  frames).
- **M2 — citation and conflation.** Across all works: the share carrying R4, and
  the share carrying any of C1-C3, with the same interval treatment.

Neither may be dropped, and neither may be moved to a supplement, whichever way
the numbers fall. What the result pattern decides is only **which one the
abstract leads with and how strongly M1 is worded**:

Let `n1` be the number of E1 works in the main analysis, `p_a` the share coded
(a), and `L_a` the lower bound of its Wilson 95% interval.

| Pattern | Condition | Abstract leads with | Wording of the headline claim |
|---|---|---|---|
| **P1** | `L_a ≥ 0.10` | M1 | "X% (95% CI …) administered an instrument that is not the MBTI" |
| **P2** | `p_a ≥ 0.10 > L_a` | M1 | Same figure, stated as imprecise: "X%, though the interval is wide (95% CI …)". The word *substantial* is not used. |
| **P3** | `p_a < 0.10` and (c) is the largest instrument category | M1, framed on (c) | "X% of papers reporting MBTI results do not identify the instrument they administered" — a reporting failure, not a substitution one |
| **P4** | `p_a < 0.10` and (b) is the largest | M2 | Attribution in administration is mostly accurate; the claim moves to citation practice and conflation, and the (a) cases are reported as a case series |
| **P5** | `n1 < 20` | M2 | No headline rate from M1. M1 is reported descriptively with its interval and explicitly called imprecise |

Fixed regardless of pattern:

- The three calibration records are described in Discussion, and the fact that
  two of them fall outside the main analysis is stated in Methods.
- Open-access-only is described as a declared sampling frame; every figure is a
  lower bound, and the direction of the bias is stated.
  ⚠️ **"Every figure is a lower bound" is false and this instruction was departed
  from; see §12 (2026-08-25).** The text is left exactly as written because §10's
  value is that it records what was promised before the counts existed, and
  editing it would destroy the only property that makes it evidence.
- Europe PMC contributed no work that OpenAlex did not already contain, so it is
  reported as independent confirmation of the frame, not as a second frame.
- The unobtainable-full-text count is reported next to every proportion.
- The claim "the 16Personalities test is not the MBTI" is background, sourced to
  the vendor's own statement, and is never presented as this study's finding.

## 11. Sensitivity analyses, fixed here

Fixed now so that running one later cannot be a way of finding a better number.
All are reported whether or not they change the conclusion.

| # | Arm |
|---|---|
| **S1** | Include `conference` and `conference_abstract` in the denominator |
| **S2** | Include the `unclassified` record (§8) |
| **S3** | Count `c-vendor-cited-only` works as (a) — the PLAN's original boundary rule (§4.1) |
| **S4** | OpenAlex-only versus both sources |
| **S5** | The widening word-form variant `"Type Explorer"`, which adds one work to the intersection in OpenAlex and none in Europe PMC |
| **S6** | Exclude records whose retrieved text is a conference abstract (`text_is_abstract`, §3.6) |
| **S7** | Conflation flags on the narrow reading — works that **name the vendor's test or site**, excluding works that attribute the vendor's proprietary content to the MBTI without naming the vendor at all. Naming is per work and counts prose, a footnote, a reference entry or a bare URL (§6) |

## 12. Changes after coding began

Entries take the form: date, what changed, why, and whether any coding output had
been seen at the time.

**2026-08-19 — §5 and §6, denominator wording. No coding output existed; coding
had not started.** Both sections said the R and C flags are coded on "all 99
works", which contradicts §1: a work whose full text cannot be obtained is coded
`unobtainable` and is not coded at all. The sections now read "every work whose
full text was retrieved — 61 of the 99". This corrects an inconsistency between
sections rather than changing a rule — the flags were never codable on a text
nobody could read — and it is recorded here because the wording decides the
denominator of M2 (§10), which the manuscript reports.

**2026-08-19 — §5, whose use an R flag records. Two works had been coded when
this was written, both calibration records; no proportion had been computed and
no work outside §7 had been read.** §5 did not say whether a work that reports
another study's use of the vendor carries that use as its own flag. Both coders
met the question on Tshimula 2026 — a review whose three vendor mentions all
describe studies it cites — and split: c1 read the mentions as R1 and R5 and
flagged the case uncertain, c2 read them as R6 on the grounds that R1
presupposes an administration this work never performed. §7 had already fixed
R6 as the expected code for that record, so §5 now states in words what the
calibration table already asserted. The added sentence is the one the author
chose from three options and it changes no expected code. c1's coding of that
record was discarded and recoded against the amended protocol; the calibration
record for Bai 2025 is untouched, both coders having agreed on it.

**2026-08-19 — §2, §3.4, §5, §6, §9 and §11, twelve questions the corpus asked
and this protocol could not answer. All 61 works had been coded twice and the
kappas were known; no R or C proportion had been computed, and none has been
computed since.** Both coders finished, agreement was scored, and 31 of the 35
works with a split code came back reporting that the item in dispute is not
decided by anything written here. The reports collapse to twelve questions:
whether a conflation flag may rest on more than one sentence; whether C3's
adjectives are a closed list; whether the flags reach the vendor's proprietary
content or only its test; what to do when a work both conflates and states the
distinction; where to put the vendor when it is the object of study rather than
a source; whether the (c) sub-labels are exhaustive; whether writing "MBTI" out
in full is a provenance claim; whether a reference-list-only citation can carry
a substantive role; whether reprinting another study's aggregate frequencies is
E2 or E4; whether a bare validity adjective sets R4; how a bundled citation is
apportioned; and how to record a third party's look-alike test called "the
MBTI".

This is the explanation of the low kappa on the conflation flags — C2 at 0.52 is
not two coders reading one sentence differently, it is two coders applying a
rule that was never written against the shape in front of them. §5 and §6 had
been written for the shapes the calibration records have.

The amendments answer all twelve. Where §7's calibration table already implied
an answer it was taken (Q1 chains, Q7 derivation predicates). Where it did not,
the reading that *weakens* the headline was taken: R4 requires a figure and not
an adjective (Q10, which sets M2's numerator), C3 excludes claims about
popularity (Q2), and the one amendment that raises a rate — extending the
conflation flags to the vendor's proprietary content (Q3) — carries S7 reporting
the narrow count beside it. Where a shape cannot be measured on this corpus at
all it is recorded and refused a rate (Q12).

**What this cost, and why it was paid.** The R and C flags on all 61 works were
discarded and coded again by both coders against the amended rules, 122 runs. A
coder that never saw a rule cannot have applied it, and a quote located under
one rule is not evidence under another, so patching the existing flags would
have meant settling twelve general questions thirty-one times over, once per
work, with no rule a reader could check. **The E gate and the instrument code
were kept** — no question touches §3, and the instrument code agreed on all 34
works both coders placed in E1. The single E disagreement (Q9) is settled by the
rule now in §2 rather than by re-coding.

The proposals produced for the 35 split codes were **not applied**. They exist
in the run record; the amended rules replace them.

**2026-08-20 — §6 and §11, three questions the amended rules still did not
answer. The 27 remaining split codes had been through a proposal round and the
kappas were known; no R or C proportion had been computed, no instrument
distribution had been computed, and neither has been since.** The 27 works
carrying a split code were sent to proposers under §9, one agent per work, each
seeing the protocol, one full text and the two codings. **22 of the 27 reported
that the item in dispute is still not decided.** The reports collapse to seven
questions, of which **five are downstream of Q3** — the amendment that widened
the conflation flags to the vendor's proprietary content, and the only one that
raised a rate. Q3 was adopted without stating its mechanics, and the corpus
asked for them. Three are answered here; the other four are ruled case by case
under §9 rather than legislated, because each occurs once or twice and a rule
written for a single work is a decision wearing a rule's clothes.

- **How far a content-level identification carries.** §6's chain rule was
  written for identification at the instrument level and said nothing about the
  content-level identification Q3 introduced. It now reaches only the content it
  identified: such a work sets C1 alone unless the derivation or standing
  predicate is asserted of that content. The wider reading would have made C2
  and C3 follow from C1 almost automatically — the independence Q7 refused for
  acronym expansion. Identity by unmarked anaphora is excluded for the same
  reason. **Lowers C2 and C3.**
- **Whether the list of proprietary content is closed.** §6 enumerated three
  kinds and never said whether the list was exhaustive; two coders split on the
  vendor's aspect labels for the dichotomies the MBTI does have (Mind, Energy,
  Nature, Tactics). The list is now closed and those labels are outside it, on
  two grounds: they relabel existing content rather than adding content the MBTI
  lacks, and identifying them as the vendor's requires knowledge from outside
  the text, which no located verbatim can carry and no reader can check. The
  shape is recorded in free text and described without a rate. **Lowers the C
  counts.**
- **What counts as naming the vendor — a defect, not a choice.** §11's S7 row
  excluded works that merge the content "without naming the test"; §6 described
  the same excluded set as works "careful enough not to name the source" and
  listed the site alongside the test. Those are different sets, and three works
  sit between them, naming the vendor only by a footnoted URL or a reference
  entry. Both sections now read the same — the vendor's test or site, in prose, a
  footnote, a reference entry or a bare URL — and naming is assessed per work,
  which is §11's own wording. **This moves the sensitivity arm and not the
  headline.**

**What this cost.** The C flags, the narrow C flags and `states_distinction` were
coded again on all 61 works by both coders, 122 runs, for the reason §12 already
records: a coder that never saw a rule cannot have applied it. **The R flags were
not re-coded** — none of the three amendments touches §5 — and neither were the E
gate and the instrument code.

**A stopping rule, fixed here before the next round rather than after seeing
it.** Two rounds have now reported gaps at 89% and 81%. If a third round reports
at a materially similar rate, that is evidence the remaining disputes are
irreducible rather than under-specified. At that point amendment stops, the
narrow reading becomes the main analysis and the wide one the sensitivity arm,
the remainder is ruled case by case, and the amendment history is reported in
Methods as a property of the instrument rather than as a defect that was fixed.
Fixing this now is the same discipline as §11 fixing the sensitivity arms in
advance: it cannot become a way of finding a better number later.

**2026-08-22 — §10 and §11, three mechanics the reporting rules leave unstated.
Coding and every ruling were complete and the kappas were known; no proportion
had been computed — not the instrument distribution, not an R or C rate, not
`n1` — and none had been computed when these were written.** §10 fixed what is
reported before the counts existed, which is the whole of its value, and three
of its instructions turn out not to determine an answer. Each is settled here,
before the first count, because after it none of them can be settled honestly.

- **Which row of §10's table applies when two of them do.** P1-P4 give
  conditions on `p_a` and `L_a`; P5 gives one on `n1`; nothing says which
  governs a result satisfying both, and `n1 < 20` alongside `L_a ≥ 0.10` is an
  ordinary outcome rather than a pathological one. **P5 governs.** Three
  grounds, none of which needs the count. The instructions cannot be followed
  together — P1 requires a headline rate and P5 forbids one — so the table is
  coherent only if one row overrides. §12's practice where the protocol has not
  decided is to take the reading that weakens the headline, and P5 is that
  reading. And a small-sample precaution that gives way the moment the interval
  is favourable is not a precaution.
- **Which row applies when P3's and P4's conditions are both met.** Both begin
  `p_a < 0.10` and separate on which instrument category is the largest; a tie
  between (b) and (c) satisfies neither description and is an ordinary outcome
  on a denominator this size. **P4 governs the tie.** It is the weakening
  reading — P3 still leads the abstract with M1, where P4 moves the lead to M2 —
  and it is also the more accurate one, since a (b) that equals (c) is not a
  corpus in which the failure to identify the instrument predominates, which is
  the thing P3's wording asserts. ((a) cannot be the largest category while
  `p_a < 0.10`, so no third tie arises.)
- **Which quantities are reported as proportions.** §10 fixes the measures and
  §11 the arms, but the protocol asks elsewhere for things to be reported
  without saying in what form: §3.4's sub-labels "alongside" the main code,
  §6's `states_distinction` "separately", §6's `third_party_conflation` and the
  vendor's aspect labels, both of which it records and expressly refuses to
  rate, §1's two kinds of absence, §3.6's `text_is_abstract`. **The proportions
  reported are those of §10's M1 and M2 and §11's arms, and no others**; every
  other quantity the protocol asks for is reported as a count against a stated
  denominator — the one exception being §1's `no_word_form` bound, whose rate §1
  states itself. This adds no number to §10. It fixes that none can be added
  later, which is what §10 is for.
- **How S5 is computed, its added record having never been retrieved.** The
  widening word-form variant takes the OpenAlex intersection from 108 records to
  109 (`query_log.json`), and the added record is not among the 118 rows of
  `corpus.csv`: it was never retrieved, so it carries no full text, no key and
  no coding. The arm is therefore reported as a bound — one record, at most one
  work, against a frame of 99 — with its uncoded status stated. The alternatives
  were to invent a code for it or to drop the arm in silence.

**2026-08-25 — §6's C2 row, and one addition to the reporting that this protocol
had closed. Every count existed and the manuscript had been drafted, reviewed and
typeset. An external reader was given the manuscript, without this protocol or
any data file, and returned ten observations; two of them are answered here.**
The two are recorded together because the second is the consequence of the first
being wrong in the same direction.

- **§6's C2 row asserted something false about the vendor, which is the error
  this study exists to measure in others.** The row read that the flag marks a
  lineage "the vendor itself disclaims — Jung, Myers and Briggs, or the published
  MBTI". The vendor does not disclaim a Jungian ancestry; it asserts one, in the
  words now quoted in §6 above, while disclaiming the incorporation of Jungian
  cognitive functions and any identity with the MBTI. The row is corrected to the
  three lineages the vendor actually denies, and §6 now quotes the vendor on both
  sides of the line. **This is an error statable independently of the count it
  might change**, which is what §0 requires of a correction made this late: the
  vendor's page says what it says whether or not a single work is flagged.
  **No coding was reopened and no count moved.** The 24 flagged works were read
  against the corrected row before it was written: every one carries a derivation
  predicate asserted of the MBTI or of Myers and Briggs, eleven of them reaching
  Jung only through a prior identification of the vendor's test *as* the MBTI,
  which the chain rule already covers and which the vendor does disclaim. **No
  work's C2 rests on an unchained Jungian claim.** Had one, it would have been
  recoded and the change reported.
- **A cross-tabulation was added that §12 had closed the list against, and this
  one is not an error correction.** The 2026-08-22 entry fixed that only §10's
  measures and §11's arms are reported, "which is what §10 is for". The addition
  is the conflation flags of the main analysis split by instrument code —
  reported in `results.json` under `post_hoc_counts_not_planned`. It is here
  because the reader's first observation was correct and cost the manuscript its
  headline reading: **§3 codes what a work administered, not whether the work
  attributed it correctly**, and the draft had read M1 as the second. §3.2's
  worked example says the mismatch "is the object of this study", but it says so
  while removing an obstacle to coding (a) — it never made a claim of MBTI
  administration a condition of the code, and three of the seventeen works coded
  (a) in the main analysis state the distinction somewhere in their text. The
  honest repair is to state M1 as what it measures, which §10's own wording of
  the P1 headline already does. The attribution question is then answered by
  columns that were coded twice, scored and adjudicated long before this was
  computed. **It is still an addition made after the counts were known, which the
  rule above forbade**, and calling it anything else would be the move this study
  audits. Three constraints hold it: it carries counts against a stated
  denominator and no rate or interval, it is labelled unplanned in the results
  file and in the manuscript, and it is computed by published code rather than
  read off by a person. §10's two measures are unchanged, and the branch still
  returns P1 from the same counts.

**2026-08-25 (second entry) — §1 and §10, three passages that contradict the
manuscript published beside them, and one addition to the reporting. Every count
existed; the manuscript had been drafted, reviewed twice, revised and typeset.**
A three-reviewer read of the revised manuscript against this protocol found that
the two documents disagree in three places, and that the manuscript is right in
all three. The treatment differs by what each passage is *for*, and that is the
part worth stating: a protocol does two jobs that pull apart once a passage turns
out to be wrong. Where the text is a **rule that still governs**, leaving it false
licenses wrong coding by anyone who re-runs the study, so it is corrected in
place. Where the text is a **pre-commitment whose only remaining value is that it
was fixed before the counts**, editing it destroys the property that makes it
evidence, so it is left standing and marked. Neither route is silent.

- **§1's retrieval figures were wrong, and are corrected in place.** §1 read
  "retrieval reached 61 of 99 works, and 42 of the 58 journal articles … Ten of
  the sixteen missing journal articles are publishers refusing programmatic
  access (HTTP 403 or 404)". Those are the *coded* counts presented as the
  *retrieved* counts, which double-counts the three works retrieved without a
  vendor word form as missing and yields sixteen where `fulltext_log.csv` gives
  fourteen. §1 also contradicted itself within four paragraphs, defining
  `no_word_form` as "text was retrieved" and then counting those works as
  unretrieved. The error is statable independently of any count it changes — a
  work that was retrieved is not missing — which is what §0 requires of a
  correction this late. The parenthetical was wrong too: of the ten failures,
  eight returned HTTP 403 or 404 and two failed at the TLS layer, which is a
  broken server and not a refusal. That distinction is load-bearing, because the
  sentence is the evidence for calling the open-access frame declared rather than
  incidental. The repository README carried the same figures and is corrected
  with it. Nothing evidential is lost: these were descriptions of a data file
  published alongside and contradicting them.
- **§1's "the audit's claim is about the peer-reviewed literature" is left
  standing and marked.** It is false — `venue_class == "journal_article"` is a
  metadata assertion that certifies no refereeing, and this corpus contains at
  least one conference-supplement abstract filed as a journal article. But it is
  a scope statement rather than a coding rule; no code depended on it, and
  correcting it in place would edit a sentence whose only remaining function is
  to record what was claimed. The manuscript carries the corrected statement and
  now points here.
- **§10's "every figure is a lower bound" is left standing and marked, and the
  departure from it is reported as a departure.** The instruction is false by
  arithmetic: when numerator and denominator can both only rise, the ratio can
  move either way, so the counts are bounded and the proportions are not. This
  can be shown without looking at a single count. §10 is the section whose entire
  value is that it fixed the reporting before the results existed, and the
  manuscript's Methods stakes the study's integrity on exactly that; rewriting it
  now would buy a tidier document at the cost of the evidence. So the text stays
  and the manuscript declares what it did instead. **This is a deviation from a
  pre-committed reporting instruction, and a study built on pre-commitment has to
  label its deviations as deviations rather than as edits.** Limitations 2 named
  the error but attributed it to "an earlier version of this paragraph", which
  points at the manuscript's own drafts and conceals that the instruction
  departed from is this protocol's; it now says so.
- **§10's list of reported quantities gains one row, for the reason the first
  2026-08-25 entry gives.** That entry added the conflation flags of the main
  analysis split by instrument code. As drawn it did not add up: C1∪C2 plus C0
  left one (a) work unaccounted for, because C0 is defined against C1-C3 and that
  work carries C3 alone. The block now reports C3 and the union of all three, and
  `aggregate.py` refuses to produce it unless the flagged and unflagged counts
  partition the works of every instrument code. The corrected figure is that
  **16 of the 17 works coded (a) carry at least one conflating statement**, where
  the manuscript had said 15 and invited a reader to infer that two carried none.
  The addition raises a number and is recorded for that reason: the rule this
  protocol has followed throughout is to take the reading that weakens the
  headline where it is silent, and this is not that. It is an arithmetic
  correction to a table that did not sum, made against columns coded, scored and
  adjudicated in August, and it is reported with the same unplanned label as the
  rest of the block.

**2026-08-25 (third entry) — §11's S2, and two claims the manuscript made about
this protocol that it should not have. Every count existed; the manuscript had
been through a second external review.** The reviewer read only the typeset
manuscript, as before, and returned six substantive findings. Four are corrections
to the manuscript alone and are recorded there. Two reach this document.

- **S2 did not run, and reporting it at the main-analysis values said otherwise.**
  §8 undertook to code the venue-less record in full so that the arm would run on
  real codes. Its full text was never retrieved. `aggregate.py` nonetheless
  computed the arm over a denominator the record does not join, returned the main
  analysis, and the manuscript printed "unchanged" while the figure drew a point
  and an interval beside the arms that ran. **An arm whose input was never
  obtained has no result, which is not the same as a result equal to the main
  analysis.** S2 now returns no measures and is reported as not estimable. The
  error is statable without reference to any count — the record carries no code,
  so nothing was added to anything — which is what §0 requires this late.
- **The claim that only M1, M2 and the arms carry a proportion was not kept, and
  the manuscript's defence of the 2026-08-25 cross-tabulation rested on it.** The
  first entry of this date argued that the block was acceptable because it
  reports "counts against a stated denominator and no rate". The reviewer pointed
  out that the manuscript writes "sixteen of seventeen", which is a proportion
  however it is printed, and that a rule evaded by declining to divide is not a
  rule. **The defence is withdrawn.** The block is described in the manuscript as
  an exploratory, post hoc set of descriptive proportions, reported without
  intervals, and it is counted as a **departure from §12's closed list** rather
  than as an amendment to it. The manuscript now carries a table of every
  departure, which is where a reader should go rather than to this log.
- **A related correction the reviewer forced, which changes a reported number.**
  The first entry of this date reported that "16 of the 17 works coded (a) carry
  at least one conflating statement" and the manuscript read that figure as the
  misattribution count. It is not. The seventeenth work carries C3 alone — a claim
  about the vendor's test's *standing*, not about its identity or its descent —
  and this study establishes no fact about the test's validity against which such
  a claim could be called false. §6 drew C3 as a separate flag for exactly this
  reason. The misattribution reading is now **15 of 17** (C1 or C2), with 13 of 17
  for C1 alone and 16 of 17 for any of the three, reported as three separate
  lines. **This lowers the headline of the exploratory block**, and it corrects an
  earlier amendment of this same date that raised it.
