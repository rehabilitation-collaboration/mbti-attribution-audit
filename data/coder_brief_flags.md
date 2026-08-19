# Coder brief — second pass, R and C flags only

The instruction each coder receives for the flag pass, verbatim.

The first pass (`coder_brief.md`) coded every work on all four steps. Its E gate
and instrument codes stand — no amendment touches §3, and the instrument code
agreed on all 34 works both coders placed in E1. What the first pass could not
do is apply rules that were not yet written: §12 records twelve questions the
corpus raised and the protocol did not answer, and the amendments that followed
change how the R and C flags are assigned.

So the flags are coded again, from the text, by both coders, against the amended
protocol. A coder that never saw a rule cannot have applied it. This pass does
not ask for the E gate or the instrument code and coders are told not to supply
them, so that a second reading cannot quietly move a code the amendments do not
touch.

Assignments are filled in from `data/fulltext_log.csv` and substituted for the
bracketed fields.

---

You are coder `{CODER}` in a planned double-coding exercise. Code exactly ONE
work on the **R flags (§5) and the C flags (§6) only**, and write the result as
JSON.

Read these two files, in this order:

1. `data/coding_protocol.md` — the coding protocol. Apply it exactly as written;
   do not improvise beyond it. §5, §6 and §12 have been amended; read §12 so you
   know which rules are recent and why.
2. `fulltext/{KEY}.txt` — the full text of the work you are coding. Read the
   whole file, including the reference list.

The work you are coding:

- key: `{KEY}`
- doi: `{DOI}`
- title: {TITLE}
- work_venue_class: `{VENUE}`

Rules you must not break:

- The full text file above is your ONLY source of evidence. Do not search the
  web, do not fetch the DOI, do not open any other file in `fulltext/`, and do
  not rely on prior knowledge of this paper. If the retrieved text does not
  contain it, it is not evidence.
- **Do not read any file in `coding_raw/`.** Earlier codings of this work exist
  there, including your own from the first pass and the other coder's. Reading
  them would make this an edit of a previous answer rather than a reading of the
  text.
- **Do not code the E gate or the instrument code.** They are settled and are
  not part of this pass. Code the flags on their own terms: §5 and §6 apply to
  every work whatever its E code.
- §3.6: one retrieved file can hold several works. Code only the part belonging
  to the work named above. Sentences from a neighbouring paper in the same file
  are not evidence for this work.
- Every flag you set needs a located verbatim quote plus the section it came
  from. Copy the source wording exactly inside the quote; never paraphrase
  inside quotation marks. If the source is not in English, quote the original
  and put your English gloss after the closing quote.
- Where a C flag rests on a chain across sentences (§6), quote **every link**,
  joined by ` || ` in the one quote field.
- §7 gives expected codes for three calibration records. If the work you are
  coding is one of them, code it from the text yourself anyway. If your reading
  differs from the expected code, say so in `uncertain_note`.
- You are working independently. Do not try to find or infer the other coder's
  output.
- If the protocol genuinely does not decide a case, set `uncertain` to true and
  explain what is undecided. Do not invent a rule and do not guess.

Write your result as JSON to `coding_raw/flags_{CODER}/{KEY}.json`, using
exactly these keys:

```json
{
  "key": "{KEY}",
  "coder": "{CODER}",
  "roles": {"r1": false, "r2": false, "r3": false, "r4": false, "r5": false, "r6": false, "r7": false},
  "role_quotes": {},
  "conflation": {"c0": true, "c1": false, "c2": false, "c3": false},
  "conflation_quotes": {},
  "conflation_narrow": {"c1": false, "c2": false, "c3": false},
  "states_distinction": false,
  "states_distinction_quote": null,
  "third_party_conflation": false,
  "third_party_conflation_quote": null,
  "uncertain": false,
  "uncertain_note": null,
  "free_text": null
}
```

Field notes:

- `roles` — §5, including the new **R7** (the vendor as the object of study, not
  a source). Set every flag explicitly true or false.
- `conflation` — §6. `c0` is true exactly when none of C1-C3 applies.
- `conflation_narrow` — the same three flags under the **narrow** reading:
  counting only statements about the vendor's **test or site by name**, and
  excluding statements that attribute the vendor's *proprietary content* (the
  -A/-T axis, the Analyst/Diplomat groupings, the branded type names) to the
  MBTI without naming the test. This feeds sensitivity arm S7 (§11). Where a
  work sets a flag under both readings, both are true.
- `role_quotes` / `conflation_quotes` — one entry per flag you set true, keyed
  by the flag name (`"r4"`, `"c2"`, …). Empty object if none.
- `states_distinction` — §6: the work states somewhere that the vendor's test
  and the MBTI are not the same instrument, whether or not it also conflates
  them. Quote it.
- `third_party_conflation` — §6: the work calls some *other* look-alike
  instrument (Humanmetrics, Truity, and their kind) "the MBTI". Recorded, never
  rated. Quote it.
- `free_text` — anything the fields cannot hold, including a bundled citation
  you flagged on more than one role (§5). Null if nothing.

Create no file other than that JSON. Your final message must be exactly:
`flags {KEY} {CODER}`
