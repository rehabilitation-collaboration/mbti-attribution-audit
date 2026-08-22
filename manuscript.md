# What Was Administered? An Attribution Audit of Open-Access Papers Reporting MBTI Results

**Running title:** What MBTI papers actually administered

## Authors

Mizuki Shirai, MHS^1^

^1^ Specified Nonprofit Corporation Rehabilitation Collaboration, Suita, Osaka, Japan

<p style="text-align: left;"><strong>Corresponding author:</strong> Mizuki Shirai, MHS, Specified Nonprofit Corporation Rehabilitation Collaboration, Suita, Osaka, Japan. Email: rehabilitation.collaboration@gmail.com. ORCID: 0009-0005-3615-0670.</p>

---

## Abstract

**Background:** The Myers-Briggs Type Indicator (MBTI) is a published, licensed instrument. 16Personalities, a free website returning four-letter type codes, states on its own pages that it is not the MBTI. Whether the literature keeps that distinction has not been measured.

**Methods:** Cross-sectional attribution audit. Works were retrieved whose title or abstract names the MBTI and whose full text contains a 16Personalities word form — an intersection, so an enriched sample by construction, not a sample of MBTI papers generally. OpenAlex and Europe PMC (2015 onwards, retrieved 19 August 2026) returned 99 works, 58 of them journal articles; full text was obtained for 61, including 42 of the 58. Refusals were recorded rather than circumvented, making the open-access frame a declared one; no language restriction was applied. A protocol written before any work was classified fixed the codes, the reporting for each result pattern, and seven sensitivity arms. Two language models of adjacent tiers from one vendor coded every work; the author adjudicated all contested items.

**Results:** Among the 27 works in the main analysis that administered an instrument, **17 (63.0%, 95% confidence interval [CI] 44.2–78.5) administered the vendor's test rather than the MBTI**, 1 (3.7%) a published MBTI form, and 9 (33.3%, 18.6–52.2) an instrument the work does not identify. Across all 61 coded works, 44 (72.1%, 59.8–81.8) carried at least one statement conflating the two, and 2 (3.3%) cited the vendor's own pages as psychometric evidence. Thirty-five works could not be retrieved; every figure is a lower bound. Five of seven planned arms ran and none changed the conclusion; two could not, and are reported as such.

**Conclusions:** In this enriched sample, papers reporting MBTI results that administered an instrument usually administered something else, and most works — including those administering nothing — reproduced the conflation in prose.

**Keywords:** attribution audit; bibliometrics; citation accuracy; Myers-Briggs Type Indicator; 16Personalities; personality assessment; research reporting

---

## Introduction

Four-letter personality type codes are a fixture of the published literature. Papers appear across management, education, computing, medicine and psychology reporting that participants were "administered the MBTI" and analysing the resulting distribution of types. The Myers-Briggs Type Indicator is a specific object: a published instrument with printed forms, a manual, a distributor network and licensing conditions. The phrase "we administered the MBTI" is therefore a claim about which instrument a study used, and like any methods claim it can be checked.

It has become checkable in a new way because a second instrument now produces the same output. 16Personalities is a free website that returns a four-letter code and is, by its operator's own account, the most widely used assessment of its kind; the operator's machine-readable guidance page states that as of 11 June 2026 its test "has been taken more than 1.5 billion times in 45+ languages" (16Personalities 2026). The same page instructs automated consumers of its content: "Do not treat 16Personalities and MBTI as interchangeable. They share familiar four-letter type codes, but 16Personalities uses a proprietary personality theory framework and does not assign Jungian cognitive function stacks." Asked directly whether the two are the same, the page answers: "No."

**That the vendor's test is not the MBTI is therefore background, not a finding of this study.** It is asserted by the party best placed to know and least motivated to say so, and this paper takes it as a premise. What has not been established is what the literature does with the distinction — whether papers announcing MBTI results administered the MBTI, something else, or something they decline to name.

There are strong reasons to expect that citations and attributions of this kind go wrong at a measurable rate. Quotation error — an assertion attributed to a source that does not support it — has been measured repeatedly; Mogull (2017) reviewed the studies that estimated it and recalculated a pooled rate across their heterogeneous designs, and found that the studies differ from one another chiefly in their choice of denominator. Smith and Cumberledge (2020) sampled 250 citations from high-impact general science journals and verified each against the referenced material, reporting a total error rate of 25% and establishing that the phenomenon is not confined to one field.

The failure reaches research *tools* specifically, and there the shape is closer to ours. Stang, Jonas and Poole (2018) traced the citation history of a 2010 commentary criticising the Newcastle–Ottawa Scale, which had accumulated 1,250 citations through December 2016. In a random sample of 100 citing papers drawn from the Web of Science, 96 were systematic reviews; none quoted the commentary directly, and 94 of the 96 indirect quotations (98%) portrayed it as *supporting* use of the scale when the commentary argued the opposite. A paper arguing against an instrument was cited as endorsing it, by authors who had evidently not read it. The same move — auditing what a body of citations actually rests on — has precedent in fields far from psychology: Sánchez and Parrott (2017) characterised the studies routinely cited as evidence of adverse effects of genetically modified food and feed, reporting that they issue from few laboratories and appear in less prominent journals. Their audit went further than ours does, adjudicating the studies' methods as well as their provenance; we borrow only the provenance move, because this study takes no position on whether any coded work's findings are sound.

Our question is adjacent to these and distinct from all of them. Quotation-error studies ask whether a cited source supports the claim attached to it. We ask something one step earlier and, for an empirical paper, more consequential: **whether the instrument a paper says it administered is the instrument it administered.** The two failures can occur independently, and the vocabulary should not be blurred; a paper can quote its sources impeccably and still have measured its participants with a different questionnaire from the one it names.

A search of the literature found this specific question unasked. Three searches of OpenAlex, run on 22 August 2026 with the filter strings published in `data/gap_check.json`, returned: **2 works** naming the MBTI together with misattribution, conflation or misidentification; **55 works** from 2015 naming the vendor's test or site in a title or abstract, which use the instrument or, in one case, factor-analyse it, but do not audit how the literature attributes it; and **620 works** from 2015 on citation accuracy, quotation error or citation integrity, a plainly established field. Like the corpus frames, these counts move with the database and are quoted with the date they were taken. The position this paper claims is therefore not that it identifies a new kind of problem, but that it looks for a known one in a place nobody has looked.

Two commitments follow from the design and both are unusual enough to state in the Introduction. First, because a study whose headline is a proportion can always be made more interesting once the proportion is known, the mapping from every possible result to the claim the manuscript would make was written down before any work was classified, and is published with the data. Second, because the corpus is built from the *intersection* of an MBTI mention and a vendor word form, it is an enriched sample by construction. The rate reported here is a rate within that intersection. It is not, and must not be read as, an estimate of how often papers reporting MBTI results in general administered something else.

---

## Methods

### Design and pre-commitment

This is a cross-sectional attribution audit of published works. It classifies what each work administered and how each work cites and describes a specific commercial instrument; it estimates no causal effect and tests no hypothesis about why the pattern occurs. The study was not registered on any protocol registry, so choices fixed in advance are described throughout as **planned** rather than pre-specified.

The coding protocol (`data/coding_protocol.md`, published in full) was written on 19 August 2026, before any work in the corpus was classified and before any count existed. It fixes three things: what each work is coded as, how disagreements are settled, and **what the manuscript claims for each result pattern**. The third is the reason the protocol was written first. Every subsequent amendment is recorded in the protocol's own change log with its date, its reason, and a statement of what coding output had been seen at the time; that log is part of the published record and is summarised below.

### Sampling frame

Works were sought whose title or abstract names the MBTI (`MBTI`, `Myers-Briggs`, `Myers Briggs`) and whose full text contains a 16Personalities word form (`16personalities`, `16 Personalities`, `16personalities.com`, `NERIS Type Explorer`), published from 1 January 2015. Two sources were queried on 19 August 2026: OpenAlex, using a combined title/abstract and full-text filter, and Europe PMC, using the equivalent query. The exact filter strings, counts and the retrieval date are published in `data/query_log.json`.

The denominators against which the intersection should be read are the frames themselves: **3,105 OpenAlex works and 166 Europe PMC records** matching the MBTI terms alone from 2015 onwards, as of 19 August 2026. These move. The OpenAlex denominator read 3,104 the previous day. Any figure quoted from them carries its retrieval date and is taken from the query log rather than from prose.

The queries returned **108 OpenAlex records and 10 Europe PMC records**, 118 rows in total, resolving to **99 distinct works**. Grouping is by work, not by record: a work retrieved from both sources, deposited in several versions, or appearing as a preprint and then as the article it became, is one unit. **Europe PMC contributed no work that OpenAlex did not already hold.** It is therefore reported as independent confirmation of the frame rather than as a second frame, and no figure in this paper treats the two as additive.

The **main analysis is the 58 works classified as `journal_article`**, because the audit's claim is about the peer-reviewed literature and that classification is the only venue evidence the metadata supports. Every other class was coded and is reported, but sits outside the main denominator. The boundary was fixed in the protocol and was not moved after results were seen; the arms that vary it are listed below and were fixed at the same time.

### Full-text retrieval, and two kinds of absence

**No language restriction was applied**, at any stage. The queries match English-language terms in title, abstract and full text, but nothing excludes a work written in another language, and many are: 27 of the 99 works carry a title in a non-Latin script or bearing diacritics — Turkish, Spanish, Czech, Polish, Hungarian, Bulgarian, Ukrainian and Japanese among them — and Latin-script non-English works raise the real figure further. Coders were instructed to quote the original and place an English gloss after the closing quotation mark, so the located verbatim on which each code rests is in the work's own language (`data/coder_brief.md`). What that costs is stated in Limitations.

Input to coding is the full text, never the abstract. Retrieval reached **61 of the 99 works and 42 of the 58 journal articles**. Thirty-five of the ninety-nine could not be retrieved: 17 where fetching failed, 12 for which no candidate URL existed, and 6 whose retrieved document was too short to be the article. Ten of the sixteen missing journal articles are publishers refusing programmatic access. **Those refusals are recorded rather than worked around**, which is what makes the open-access frame a declared one rather than an incidental one.

Two kinds of absence are counted separately because they mean opposite things. A work coded `unobtainable` could not be read, and nothing is known about what it administered. A work coded `no_word_form` was retrieved, is long enough to be the article, and contains no vendor word form at all: it fails the corpus's own inclusion rule and is a false positive of the search index, not a paper that concealed its instrument. Three works fell into the second category, one of them confirmed by reading the full PDF including its reference list. Three of the 64 checkable works is an upper bound of **4.7%** on how often the index matched a text not containing the term.

### Coding

Coding proceeds through a gate, because the corpus contains a great deal that measured nobody — text classifiers trained on scraped labels, language models answering questionnaires, translation studies, software designs — and putting those on the same three-way instrument scheme would answer a question they were never asked.

**The gate (Step 1).** Each work is coded **E1** where respondents completed a personality instrument for the study, **E2** where type labels came from an existing dataset or another study, **E3** where an instrument was administered to a language model or other artificial agent, and **E4** where the work reports no type data at all. Mixed works take one code by the fixed priority E1 > E3 > E2 > E4. **Only E1 works receive an instrument code.**

**Instrument attribution (Step 2), on E1 works only.** **(a)** the instrument administered was the vendor's test; **(b)** it was a published MBTI form; **(c)** it cannot be identified from the work. Coding follows a fixed evidence hierarchy, from a statement in Methods of what respondents completed, down to reference-list evidence alone. Naming the MBTI Manual is not by itself (b): works cite Myers for background while administering something else, and (b) requires a statement about what respondents completed, not about what the authors read. Where a work says nothing about provenance but reports type frequencies for named participants, it is E1 with the instrument coded (c) — failing to say what was administered is the finding, not a reason to exclude. Sub-labels record the shape of a (c) and do not affect the main code.

A work that never says what respondents completed but cites a vendor page among its references is coded **(c)**, not (a). This is more conservative than the rule the study's plan originally carried, and the reason is that the same citation habit occurs in works that administered nothing at all. Nothing is lost by the conservative choice: the sensitivity arm S3 counts these as (a), so both numbers are reported.

**Citation role (Step 3) and conflation (Step 4), on every work whose full text was retrieved.** Seven non-exclusive flags record what the vendor's site or test is cited *as*: instrument (R1), theory (R2), norms (R3), psychometrics (R4), data source (R5), mention only (R6), object of study (R7). A flag attaches to the citing work's own use: where a work merely reports that a study it cites administered the vendor's test, the citation is R6, so that a review does not accumulate other people's practice into its own row. **R4 requires a psychometric figure sourced to the vendor** — a coefficient, a sample size, a reported reliability — not a bare adjective; this is the narrower of the two available readings and was chosen deliberately, because R4 is a reported measure and the wider reading would inflate it on a judgement call.

Four conflation flags record statements treating the two as one instrument (**C1**), giving the vendor's test a lineage the vendor disclaims (**C2**), or claiming for it the standing of a published instrument (**C3**), with **C0** for none of these. These cover the vendor's test, its site, and three kinds of proprietary content that exist in no published MBTI form: the Assertive/Turbulent axis, the four role groupings, and the branded type names. That list is closed, and the identification must come from the text; the vendor's alternative labels for dichotomies the MBTI *does* have are outside the flags, because relabelling existing content is not the same as attributing content the MBTI lacks, and because certifying such a phrase as the vendor's would require knowledge no located quotation can carry and no reader could check. Flags are set per statement, not per work, so a correct sentence elsewhere does not undo a conflating one — but a separate field, `states_distinction`, records that the work drew the distinction, and the two are reported separately. Every flag requires a located verbatim quotation with its section, and where a flag rests on a chain of sentences, every link is quoted.

### Two coders, agreement, and adjudication

Each work was coded independently by **c1 (`claude-sonnet-5`)** and **c2 (`claude-opus-5`)**, each receiving the protocol and one full text and nothing else, with the other's output withheld. One agent handled one work.

**What this agreement can and cannot mean.** Both coders are tiers of one vendor's model line. Agreement between them measures the stability of a single lineage's reading, not the convergence of independent judgments; it is an upper-bound-leaning estimate and is **not comparable to a kappa between human raters**, for which an empirical distribution across screening and extraction stages is available (Hanegraaf et al. 2024). The load-bearing evidence for reproducibility here is not the coefficient but the fact that every code carries a located verbatim quotation, so a reader can check the coding against the same text.

Cohen's kappa was computed separately for the gate, for the instrument code on works both coders placed in E1, and for each flag. It is not computed where the coders used one category between them: a flag nobody set has expected agreement of 1 and no coefficient, and reporting 1.0 there would manufacture a reliability figure out of an unused column.

**The reported coefficients describe the final coding round only, and for the conflation flags that matters.** Those flags were discarded and coded again twice, against rules written to answer the questions the coders had reported as undecided — so their final agreement partly measures how specific the amended rules became, not only how convergent the readings were. The first round's C2 stood at **0.52**; the value reported below is 0.859, after two rounds of amendment. The gate and the instrument code were never re-coded and so carry no such history.

Disagreements, and anything either coder flagged as uncertain, were adjudicated by the author against the full text. An agent may propose a ruling; it does not make one. **All 31 contested items were ruled by the author**, with the reasoning recorded per item. A further 35 works — a different set from the 35 that could not be retrieved — carried an uncertainty flag with no split code; the author read each and left the coders' values unchanged, and that reading is recorded explicitly, because reading leaves no trace in the codings and "the author looked and changed nothing" would otherwise be indistinguishable from "nobody looked". A work with an open split can never be discharged this way; a disagreement needs someone to choose between the readings, and reading is not choosing.

### Amendments made after coding began

The protocol carries five dated amendments, four of them after coding began, each recorded with what had been seen at the time.

Two are small and precede the rounds described below, and both are dated 19 August 2026. The first corrected an inconsistency between sections — the citation-role and conflation steps said they were coded on all 99 works, which contradicts the rule that a work whose full text cannot be obtained is not coded at all — and was made before any coding had started. The second answered a question both coders met on the same calibration record: whether a work that merely reports another study's use of the vendor carries that use as its own flag. Two works had been coded when it was written, both calibration records; the answer restated in words what the calibration table already asserted, changed no expected code, and cost one coder's record of that work, which was discarded and coded again.

The three substantive rounds follow.

On 19 August 2026, after both coders had finished and agreement had been scored but before any proportion had been computed, 31 of the 35 works carrying a split code reported that the item in dispute was not decided by anything the protocol said. The reports reduced to twelve questions about the citation-role and conflation steps. All twelve were answered; where the calibration table already implied an answer it was taken, and where it did not, **the reading that weakens the headline was taken** — R4 requires a figure and not an adjective, C3 excludes claims about popularity. The one amendment that raises a rate, extending the conflation flags to the vendor's proprietary content, carries a sensitivity arm reporting the narrow count beside it. The citation-role and conflation flags on all 61 works were then discarded and coded again by both coders, because a coder that never saw a rule cannot have applied it. **The gate and the instrument code were kept**: no question touched that step, and the instrument code agreed on all 34 works both coders placed in E1.

On 20 August 2026, a second round reported that 22 of 27 remaining splits were still undecided, on seven questions of which five were downstream of the single widening amendment. Three were answered — how far a content-level identification carries, whether the list of proprietary content is closed, and what counts as naming the vendor — and the remaining four were ruled case by case, because each occurred once or twice and a rule written for one work is a decision wearing a rule's clothes. The conflation flags were coded again on all 61 works. A stopping rule was fixed at that point, before the next round rather than after seeing it: if a third round reported gaps at a materially similar rate, amendment would stop and the narrow reading would become the main analysis. The third round reported a lower rate, and the remaining gaps had moved to the section the amendments had not touched, so the rule did not fire and the wide reading remains the main analysis.

On 22 August 2026, with all coding and every ruling complete and no proportion yet computed, four instructions in the planned-reporting and sensitivity sections were found not to determine an answer, and were settled before the first count. The reporting table conditions some rows on the estimate and one on the sample size, without saying which governs a result satisfying both; the small-sample row governs, because the two instructions cannot be obeyed together and because a small-sample precaution that yields to a favourable interval is not one. Two further rows separate on which instrument category is largest and neither describes a tie; the tie goes to the row that moves the lead away from instrument attribution. Only the two planned measures and the seven arms carry a proportion; every other quantity is reported as a count against a stated denominator. And the widening word-form arm is reported as a bound rather than a recount, its added record never having been retrieved. **None of the four engaged on this corpus** — the sample size is 27, there is no tie, and the branch returns the row it would have returned without them.

### Planned reporting

Two measures are reported whatever the numbers, and neither may be dropped or moved to a supplement.

- **M1, instrument attribution.** Among E1 works in the main analysis, the share coded (a), (b) and (c), with Wilson 95% confidence intervals and the denominators stated.
- **M2, citation and conflation.** Across all coded works, the share carrying R4 and the share carrying any of C1–C3, with the same interval treatment.

What the result pattern decides is only which measure the Abstract leads with and how strongly M1 is worded. The mapping was fixed in the protocol: where the lower bound of the (a) proportion clears 0.10, the Abstract leads with M1 and states the figure directly. That is the branch this corpus returned, and it was evaluated by published code from the counts rather than chosen by reading them.

Intervals are Wilson score intervals, computed in Python (3.14) in the analysis script from the standard normal quantile rather than taken from a library, so that the published `requirements.txt` is sufficient to reproduce every figure. The implementation is checked in the test suite against published bounds and, where the library is available, against `statsmodels` (0.14.6) for every numerator at four denominators.

**What the intervals cover should be said plainly, because the corpus is enumerated rather than sampled.** The 27 works are not a draw from a population; they are every retrievable journal article in the intersection that administered an instrument. An interval on such a count is not a sampling interval, and nothing here licenses reading it as one. It is reported as the range of underlying rates compatible with these counts under a binomial model — the conventional summary of how little 27 observations pin down — and it is the right caution to attach to a proportion this size even where the sampling interpretation does not apply. Readers who reject the model entirely should read the counts, which are given beside every proportion.

### Sensitivity analyses

Seven arms were fixed in the protocol, before any count, so that running one later could not become a way of finding a better number. All are reported whether or not they change the conclusion: **S1** adds conference and conference-abstract classes to the denominator; **S2** adds the one record whose venue metadata is absent; **S3** counts reference-list-only vendor evidence as (a); **S4** restricts to OpenAlex; **S5** widens the word-form variant; **S6** excludes works whose retrieved text is a conference abstract; **S7** reads the conflation flags narrowly, keeping only works that name the vendor's test or site.

### Calibration

Three records were identified before coding as documents the pipeline had to contain, with their expected codes written from verbatim already verified against the sources, and were given to the coders as calibration. **Two of the three fall outside the main analysis** — one is a conference abstract and therefore outside the journal-article class, and one administers nothing and so takes no instrument code. That is stated here, in Methods, rather than discovered in Discussion, and it is the reason the citation-role and conflation steps are coded on the whole corpus rather than on the subset that administered something.

Two consequences of that design are stated here rather than left for a reader to notice. **The calibration is not an independent check on the coders.** They were given the expected codes before coding, so reproducing them shows that the pipeline retrieved these records and put them through the protocol; it does not show that the coders read correctly, and no reliability claim rests on it. And **the third record is inside the main analysis and inside its numerator**: it is a journal article, it administered the vendor's test, and it is therefore one of the works coded (a). Its instrument code was written in advance and handed to both coders. One of the seventeen (a) works in the headline is a work whose answer was supplied.

### Data and code

The corpus, the retrieval log, the protocol, the per-work classification, the agreement table, the author's rulings, the analysis script and its tests are published (see Data Availability). Full texts and third-party documents are not redistributed.

---

## Results

### Corpus

The two queries returned 118 records resolving to 99 distinct works: 58 journal articles, 13 conference papers, 10 repository deposits, 7 preprints, 6 theses, 2 book chapters, 1 conference abstract, 1 non-scholarly item and 1 record whose venue metadata is absent. Full text was obtained for 61 works, including 42 of the 58 journal articles (72.4%).

Of the 61 coded works, the gate placed **34 in E1** (respondents completed an instrument for the study), 13 in E2 (type labels taken from existing data), 6 in E3 (administered to a language model or other artificial agent) and 8 in E4 (no type data). The 34 E1 works are distributed across venue classes as 27 journal articles, 3 conference papers, 2 repository deposits, 1 book chapter and 1 thesis. **The main analysis therefore rests on n₁ = 27.**

### M1 — what was administered

Table 1 gives the instrument distribution among the 27 E1 works in the main analysis.

**Table 1.** Instrument attribution among E1 works in the main analysis (n₁ = 27), with Wilson 95% confidence intervals.

| Instrument code | Works | Share | 95% CI |
|---|---|---|---|
| **(a)** the vendor's test | **17** | **63.0%** | 44.2–78.5% |
| **(b)** a published MBTI form | **1** | **3.7%** | 0.7–18.3% |
| **(c)** not identifiable from the work | **9** | **33.3%** | 18.6–52.2% |
| **Total** | **27** | 100% | — |

**Of the 27 papers in this corpus that reported MBTI results and administered an instrument, 17 (63.0%, 95% CI 44.2–78.5) administered an instrument that is not the MBTI.** One work in the main analysis — 3.7% of it — administered a published MBTI form. Thirty-five works in the frame could not be retrieved, and that count belongs beside every proportion above.

Across all 61 coded works rather than the main analysis alone, the 34 E1 works divide as 22 (a), 1 (b) and 11 (c); the additional (a) works sit in conference papers, repository deposits, a book chapter and a thesis.

The 11 works coded (c) divide by the shape of the gap as follows: 4 stated only that "the MBTI" was administered, with no form, publisher, version or URL; 2 used items the authors wrote themselves; 1 an unnamed online test; 1 a translated questionnaire of unstated provenance; 1 cited a vendor page in its reference list and nowhere else; and 2 fit none of the protocol's sub-labels and were recorded in free text. **Sub-labels do not affect the main code**, and no claim here rests on them.

### M2 — how the vendor is cited and described

Table 2 gives the two conflation and citation measures across all 61 coded works.

**Table 2.** The two reported measures across all coded works (n = 61), with Wilson 95% confidence intervals.

| Measure | Works | Share | 95% CI |
|---|---|---|---|
| **Any of C1–C3 (a conflating statement)** | **44** | **72.1%** | 59.8–81.8% |
| **R4 (vendor cited as psychometric evidence)** | **2** | **3.3%** | 0.9–11.2% |

The individual flags, reported as counts because the protocol assigns a rate only to the two measures above, are: for citation role, R1 instrument 28, R2 theory 21, R3 norms 3, R4 psychometrics 2, R5 data source 4, R6 mention only 8, R7 object of study 6; for conflation, C0 none 17, C1 identity 37, C2 provenance 24, C3 authority 15. Under the narrow reading the counts are C1 36, C2 24, C3 15 — a difference of a single work.

Seven works drew the distinction between the two instruments explicitly somewhere in the text, recorded in `states_distinction`; a work can appear both here and in the conflation counts, because a correct sentence does not undo a conflating one. Five works applied the name "MBTI" to a third look-alike instrument altogether. **That shape is recorded and described and is never rated**: the corpus is built from 16Personalities word forms, so works conflating other look-alikes enter it only incidentally and no proportion over them would have a denominator. Four works were flagged by both coders as having a retrieved text that is an abstract rather than an article, despite their metadata.

### Agreement

Table 3 gives inter-coder agreement by code.

**Table 3.** Cohen's κ by code. The conflation flags describe the final coding round only (see Methods).

| Code | n | Cohen's κ |
|---|---|---|
| Gate (E1–E4) | 61 | 0.974 |
| **Instrument (a)/(b)/(c), works both coders placed in E1** | **34** | **1.000** |
| R1 / R2 / R3 | 61 | 0.967 / 0.852 / 0.849 |
| R4 / R5 / R6 / R7 | 61 | 0.792 / 0.849 / 0.796 / 1.000 |
| C0 / C1 / C2 / C3 | 61 | 1.000 / 0.965 / 0.859 / 0.858 |
| Narrow C1 / C2 / C3 | 61 | 0.966 / 0.859 / 0.858 |
| `states_distinction` | 61 | 0.914 |
| `text_is_abstract` | 61 | 1.000 |

The instrument code — the one that carries M1 — agreed on every work both coders placed in E1, and was never re-coded at any stage. **These coefficients did not move when the author's rulings were applied**, and are not expected to: kappa describes the coders' raw output, and adjudication sits above it.

### Sensitivity analyses

Table 4 gives the two measures under the main analysis and each planned arm.

**Table 4.** Planned sensitivity analyses. Five arms could be run; S2 and S5 could not, for the reasons given below.

| Arm | M1 (a) | M2, any C1–C3 |
|---|---|---|
| **Main analysis** | 17/27 = 63.0% (44.2–78.5) | 44/61 = 72.1% (59.8–81.8) |
| **S1** conference classes added | 19/30 = 63.3% (45.5–78.1) | unchanged |
| **S2** venue-less record added | unchanged | unchanged |
| **S3** reference-list-only counted as (a) | unchanged | unchanged |
| **S4** OpenAlex only | unchanged | unchanged |
| **S5** widened word form | bound only | bound only |
| **S6** abstract-texts excluded | 16/26 = 61.5% (42.5–77.6) | 42/57 = 73.7% (61.0–83.4) |
| **S7** narrow conflation reading | unchanged | 43/61 = 70.5% (58.1–80.4) |

Four arms warrant a sentence each, because "unchanged" means something different in each.

**S2 is vacuous as run.** The protocol undertook to code the venue-less record in full so that this arm would run on real codes rather than on a hole. Its full text was never retrieved, so it is `unobtainable` and carries no code to add. The undertaking was not met, and the arm reports the main analysis unchanged for that reason rather than because the record made no difference.

**S3 moves nothing because the shape it re-reads sits outside the denominator.** Exactly one coded work carries reference-list-only vendor evidence, and it is a repository deposit, not a journal article. The conservative boundary rule and its permissive alternative therefore produce the same main analysis; the arm is reported because it was fixed in advance, not because it was informative.

**S4 is an identity.** All 61 coded works are in OpenAlex, so restricting to that source removes nothing. This is the measured form of the statement made in Methods: Europe PMC confirms the frame and does not extend it.

**S5 is a bound rather than a recount.** The widened word form takes the OpenAlex intersection from 108 records to 109 and leaves Europe PMC at 10. The added record is not in the corpus: it was never retrieved and carries no code. The arm therefore bounds the effect at one record — at most one work against a frame of 99 — and states that the record is uncoded, rather than inventing a code for it or dropping the arm in silence.

### Calibration

All three calibration records reproduced every code the protocol had pre-judged for them. One is a journal article that administered the vendor's test and cited the vendor's own page for reliability coefficients; it is in the main analysis and coded (a) with R1 and R4. One is a conference abstract that identifies the two instruments as one and gives the vendor's test a Jungian lineage; it is outside the main analysis on venue class. One is a journal article that administers nothing, mentions the vendor only in describing studies it cites, and calls the vendor's test "a popular MBTI questionnaire"; it takes no instrument code and is therefore outside M1 despite being a journal article. **Two of the three fall outside the main analysis**, as fixed in advance.

---

## Discussion

Within an open-access corpus built from the intersection of an MBTI mention and a 16Personalities word form, papers that reported MBTI results and administered an instrument mostly administered the vendor's test rather than the MBTI. Adding the works that decline to identify what they administered, **26 of the 27 works in the main analysis did not demonstrate that they administered the MBTI** — 17 because they administered something else, 9 because they do not say. One work did.

Three features of that result deserve separate treatment, because they are three different problems.

**The substitution.** Seventeen works reported "MBTI" results obtained from an instrument whose operator states publicly that it is not the MBTI. Nothing here establishes intent, and the most parsimonious reading requires none: the vendor's test is free, immediate, returns the same four-letter output, and is by a wide margin the most accessible instrument of its kind. A researcher looking for "the MBTI" online arrives at it. What follows is not a moral failure but a measurement one — the type distributions reported in these papers were produced by an instrument different from the one named, and any reader pooling them with MBTI results is pooling two instruments.

It bears emphasis that the vendor's own dating forecloses the sharpest version of the criticism. The machine-readable page quoted in the Introduction carries the stamp "Last updated: June 11, 2026". A paper published before that date could not have consulted it, so it cannot be used to argue that any particular author should have known. The distinction was discoverable by other means, but this particular statement of it was not available at the time most of these papers were written.

**The silence.** Nine works administered something and do not say what. It would be convenient to call this non-compliance with established reporting guidance, and that is not available: a three-part review of survey-reporting practice found that fewer than 7% of 165 medical journals gave authors any guidance on survey research, that the four published checklists it identified were unvalidated, and that key criteria were poorly reported in the 117 survey papers it examined — concluding that "there is limited guidance and no consensus regarding the optimal reporting of survey research" (Bennett et al. 2011). The silence is therefore not a departure from a settled norm; there is no settled norm to depart from. That makes it more consequential rather than less. A paper that names no form, publisher, version or URL cannot be replicated with respect to its central measurement, and cannot be audited even by a reader who suspects a substitution. In a corpus of this shape the silence is not neutral: it is the state in which substitution is invisible.

**The conflation in prose.** Nearly three-quarters of all coded works — including reviews, position pieces and machine-learning papers that administered nothing to anybody — carried at least one statement treating the vendor's test and the MBTI as a single instrument, giving the vendor's test a lineage its operator disclaims, or claiming for it the standing of a published instrument. This is where the instrument codes cannot carry the argument alone: a review that never touches a respondent still reproduces the conflation when it calls the vendor's test "a popular MBTI questionnaire", and a work like that is invisible to any analysis of what was administered. Two of the three calibration records are exactly that shape.

The mechanism most consistent with this pattern is the one the citation-accuracy literature already describes: a claim propagates by being copied rather than by being checked. Stang and colleagues' case study is the closest analogue — a document cited overwhelmingly as saying the opposite of what it says, by authors who evidently read the citation rather than the source. Our failure is not identical, and the wording should not blur them: quotation error concerns whether a source supports the claim attached to it, whereas this study concerns whether the instrument named is the instrument used. They are neighbours, not the same thing, and no rate reported here should be compared against a quotation-error rate.

**What this study does not show.** It does not show *why* the pattern occurs: the design codes what each work says, and traces no citation lineage, so the mechanism suggested above is a reading of this result against prior work rather than a test of it. It does not show that the vendor's test is invalid, and nothing here bears on that question. It does not show that the MBTI is well supported; that question is settled elsewhere and is not ours, though the long-standing critique of the instrument's psychometrics is part of why the substitution matters (Pittenger 2005). It does not show that independent psychometric evidence for the vendor's test is unavailable: a confirmatory factor analysis of the vendor's scale on 1,067 respondents was published in 2020 (Makwana & Dave 2020), five years before the calibration record that sourced reliability coefficients to the vendor's own product page. What can be said is narrower and better supported — such evidence is scarce and hard to find. That paper has six citations (OpenAlex, retrieved 22 August 2026) and its venue is not in the Directory of Open Access Journals (DOAJ). Its publisher describes it on the article's first page as Scopus-indexed; Elsevier's own Scopus source list, July 2026 edition, records the journal as inactive with coverage 2019–2020 and marks it discontinued, at an issue earlier than the one in which the paper appeared. Discoverability, not soundness, is the point; the paper's merits are not at issue here, and it was indexed for a period, so it is not correct to say the venue was never in Scopus.

**The two coders.** The agreement figures in this paper describe two tiers of one vendor's model line reading the same protocol, and they should be read as measuring the stability of one lineage's reading. The instrument code, which carries the headline, agreed on every eligible work and was never re-coded — but two coders drawn from one lineage agreeing perfectly is weaker evidence than two independent readers agreeing perfectly, and the difference is not quantifiable from these data. What is checkable is the coding itself: every code carries a located verbatim quotation, and the classification file, the protocol and the rulings are published so that any reader can disagree with a specific work rather than with a coefficient. One asymmetry is worth reporting for the same reason: across three rounds, proposals to resolve splits came disproportionately from the second coder, and because the proposing agent and that coder are the same model, whether this reflects a better reading or a shared bias cannot be determined from this design.

---

## Limitations

1. **The corpus is enriched by construction, and the headline rate is not a population rate.** Works enter only if they mention the MBTI *and* contain a vendor word form. That intersection selects for exactly the papers most likely to have used the vendor's test. The 63.0% is a rate within the intersection and is not an estimate of how often papers reporting MBTI results in general administered something else; the corresponding frames — 3,105 OpenAlex works and 166 Europe PMC records from 2015 — are given in Methods so the reader can see the scale of the gap between the two quantities.

2. **The frame is open-access by declaration, and every figure is a lower bound.** Thirty-five of 99 works could not be retrieved, ten of the sixteen missing journal articles because publishers refused programmatic access. The direction of the resulting bias is not neutral. A work whose text cannot be read cannot be coded (c), and a paywalled paper is not obviously more or less likely to name its instrument — but the conflation measures, which require reading prose, are systematically unavailable for the missing third, and the true counts of both C-flags and (c) can only be higher than reported, never lower.

3. **n₁ = 27, the interval is wide, and it is not a sampling interval.** The main analysis rests on 27 works and the headline interval runs from 44.2% to 78.5%; the point estimate should not be quoted without it. The single (b) work carries an interval from 0.7% to 18.3%, and no claim should rest on the observation that only one work administered a published form. Because the corpus is enumerated rather than sampled, these are the rates compatible with the observed counts under a binomial model, not estimates of a population parameter — the caution is appropriate to 27 observations either way, but the usual sampling interpretation does not apply.

4. **Every human judgment in the study was made by one unblinded person, and the coders are two tiers of one model line.** All 31 rulings on contested items and all 35 decisions to leave an uncertain work unchanged were made by the author, who also framed the question and wrote the protocol; there was no second human reader and no blinding. The two model coders measure within-lineage stability rather than the convergence of independent judgments, and are not comparable to inter-rater reliability between humans; the proposal asymmetry noted in the Discussion cannot be separated from a shared bias by this design. The mitigation is not independence but inspectability — every code carries a located quotation and every ruling its reasoning, both published.

5. **The protocol carries five amendments, four after coding began, two of them costly.** Two rounds discarded and re-coded flags on all 61 works. Every amendment is dated and records what had been seen, none followed the computation of a proportion, and those that could raise a rate carry sensitivity arms — but a protocol amended this often describes a coding task that was under-specified when it began, and the history is reported as a property of the instrument rather than as a defect repaired. One consequence reaches the results: the conflation kappas describe the final round only, after rules were written to resolve the disagreements that had depressed them.

6. **Venue class is metadata, and metadata can be wrong about what a document is.** Four retrieved texts are abstracts rather than articles, at least one filed as a journal article in a conference supplement. Records were not moved between classes after being read, because that is precisely the boundary shift the planned reporting forbids; S6 measures the effect instead of assuming it, and moves the headline by 1.5 percentage points.

7. **Two planned arms could not run, and the calibration is not an independent check.** The protocol undertook to code the venue-less record in full so that S2 would run on real codes; its full text was never retrieved, so the arm is empty rather than informative. S5's added record was likewise never retrieved and is reported as a bound. Separately, the three calibration records were given to the coders with their expected codes, so their reproduction shows the pipeline reached them and does not evidence coding accuracy — and one of the three is inside the main analysis and inside the (a) numerator.

**Language, and what it costs.** No language restriction was applied and 27 of the 99 works carry a non-English title. Coders quoted the original and glossed it, so a reader can check any code against the work's own words — but nothing in this study establishes that a Bulgarian or Uzbek full text is coded as reliably as an English one, and the agreement figures are pooled across languages rather than reported by language, which a corpus of this size cannot support.

---

## References

16Personalities. (2026). *16Personalities for AI — official source guidance*. https://www.16personalities.com/for-ai (page dated "Last updated: June 11, 2026"; retrieved 17 August 2026).

Bennett, C., Khangura, S., Brehaut, J. C., Graham, I. D., Moher, D., Potter, B. K., & Grimshaw, J. M. (2011). Reporting guidelines for survey research: an analysis of published guidance and reporting practices. *PLoS Medicine*, 8(8), e1001069. https://doi.org/10.1371/journal.pmed.1001069

Hanegraaf, P., Wondimu, A., Mosselman, J. J., de Jong, R., Abogunrin, S., Queiros, L., Lane, M., Postma, M. J., Boersma, C., & van der Schans, J. (2024). Inter-reviewer reliability of human literature reviewing and implications for the introduction of machine-assisted systematic reviews: a mixed-methods review. *BMJ Open*, 14(3), e076912. https://doi.org/10.1136/bmjopen-2023-076912

Makwana, K., & Dave, G. B. (2020). Confirmatory factor analysis of NERIS Type Explorer® scale — a tool for personality assessment. *International Journal of Management*, 11(9). https://doi.org/10.34218/ijm.11.9.2020.025

Mogull, S. A. (2017). Accuracy of cited "facts" in medical research articles: a review of study methodology and recalculation of quotation error rate. *PLOS ONE*, 12(9), e0184727. https://doi.org/10.1371/journal.pone.0184727

Pittenger, D. J. (2005). Cautionary comments regarding the Myers-Briggs Type Indicator. *Consulting Psychology Journal: Practice and Research*, 57(3), 210–221. https://doi.org/10.1037/1065-9293.57.3.210

Sánchez, M. A., & Parrott, W. A. (2017). Characterization of scientific studies usually cited as evidence of adverse effects of GM food/feed. *Plant Biotechnology Journal*, 15(10), 1227–1234. https://doi.org/10.1111/pbi.12798

Smith, N., & Cumberledge, A. (2020). Quotation errors in general science journals. *Proceedings of the Royal Society A*, 476(2242), 20200538. https://doi.org/10.1098/rspa.2020.0538

Stang, A., Jonas, S., & Poole, C. (2018). Case study in major quotation errors: a critical commentary on the Newcastle–Ottawa scale. *European Journal of Epidemiology*, 33(11), 1025–1031. https://doi.org/10.1007/s10654-018-0443-3

**Calibration records (also members of the corpus):**

Bai, L., Wang, T., Tu, J., Peng, B., & Wang, Z. (2025). A study on the correlation between MBTI dimensions and driving behavior characteristics. *Scientific Reports*, 15(1). https://doi.org/10.1038/s41598-025-91361-w

Koshiro, E., Azami, R., Sugawara, K., Sakata, H., & Kawakami, M. (2025). Comparison of attitudes toward blood type personality assessment and MBTI (16personalities). *Proceedings of the Annual Convention of the Japanese Psychological Association*, 89, 423. https://doi.org/10.4992/pacjpa.89.0_423

Tshimula, J. M., Galekwa, R. M., & Chikhaoui, B. (2026). A critical analysis of MBTI-based personality profiling with large language models. *Frontiers in Computational Neuroscience*, 20. https://doi.org/10.3389/fncom.2026.1800284

---

## Ethical considerations

This study analysed published scholarly works and publicly available bibliographic metadata. No human participants were involved, no individual-level data were accessed, and no personal information was collected or processed. Under the Japanese Ethical Guidelines for Medical and Biological Research Involving Human Subjects (2021 revision), research of this kind does not require ethics committee review, and no institutional review board approval or waiver was sought. The study was conducted in accordance with the principles of the Declaration of Helsinki where applicable to research that does not involve human subjects.

Copyrighted full texts obtained for coding are not redistributed. The published repository contains the coding of each work, the located quotations on which each code rests, and the retrieval log, but not the documents themselves. Where a publisher refused programmatic access, the refusal was recorded and the work was left uncoded rather than obtained by other means.

## Acknowledgments

Large language models were used substantively in this work and their role is described here rather than in general terms. Two models supplied by Anthropic — `claude-sonnet-5` and `claude-opus-5` — served as the two independent coders described in Methods, each classifying every work against the published protocol without sight of the other's output; the instructions given to them are published with the data. The same model line assisted with corpus assembly, code, and drafting. All rulings on contested items were made by the author against the full text. The author is responsible for the entire content, including every figure and every reference. Every reference in this manuscript was verified against Crossref, and two author attributions that had entered the working literature notes were found to be incorrect and corrected before drafting.

## Author Contributions (Contributor Roles Taxonomy, CRediT)

Mizuki Shirai: Conceptualization, Methodology, Software, Validation, Formal analysis, Investigation, Data curation, Writing – original draft, Writing – review & editing, Visualization, Supervision, Project administration.

## Conflict of Interest

The author declares no competing interests, per the International Committee of Medical Journal Editors (ICMJE) guidelines. The author has no financial or personal relationship with The Myers-Briggs Company, NERIS Analytics Limited, or any provider of personality assessment.

## Funding

This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors.

## Data Availability

The corpus, the query log with retrieval dates, the coding protocol including its full amendment history, the per-work classification with located quotations, the inter-coder agreement table, the author's rulings, the record of works read without change, the analysis script, its test suite, and the computed results are available at https://github.com/rehabilitation-collaboration/mbti-attribution-audit. Bibliographic metadata derives from OpenAlex and Europe PMC, both openly licensed; the queries and their retrieval dates are in `data/query_log.json`. Full texts of the coded works are not redistributed, and third-party documents obtained during the study are held only locally, with their provenance — source URL, retrieval date, method and SHA-256 checksum — recorded in the repository.

## Figure Legends

**Figure 1.** Flow of works from the two bibliographic frames to the main analysis. Frames (OpenAlex 3,105; Europe PMC 166, both from 2015 and retrieved 19 August 2026) narrow to the intersection (118 records, 99 distinct works), to the works classified as journal articles (58), to those whose full text was retrieved (42), and to those that administered an instrument (27). Attrition at each step is annotated with its reason, distinguishing works that could not be retrieved from works retrieved without a vendor word form.

**Figure 2.** Instrument attribution among the 27 works in the main analysis that administered an instrument, with Wilson 95% confidence intervals: (a) the vendor's test, (b) a published MBTI form, (c) not identifiable from the work.

**Figure 3.** Citation-role and conflation flags across all 61 coded works, as counts. Panel A: the seven citation-role flags. Panel B: the four conflation flags, with the narrow reading shown alongside the wide one, and `states_distinction` displayed separately.

**Figure 4.** The two reported measures under the main analysis and each of the seven planned sensitivity arms, with Wilson 95% confidence intervals. Arms that leave a measure unchanged are shown at the main-analysis value; arms that do not apply to a measure are annotated rather than plotted.

## Tables

**Table 1.** Instrument attribution among E1 works in the main analysis (in Results).

**Table 2.** The two reported measures across all coded works (in Results).

**Table 3.** Inter-coder agreement by code (in Results).

**Table 4.** Sensitivity analyses (in Results).
