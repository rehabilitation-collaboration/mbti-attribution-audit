# Coder brief — third pass, conflation flags only

The instruction each coder receives for the conflation pass, verbatim.

Two passes precede this one. The first (`coder_brief.md`) coded all four steps;
its E gate and instrument codes stand, since no amendment has ever touched §3
and the instrument code agreed on all 34 works both coders placed in E1. The
second (`coder_brief_flags.md`) re-coded the R and C flags against the twelve
answers §12 records; **its R flags stand**, because none of the amendments made
on 2026-08-20 touches §5.

What changed on 2026-08-20 is §6 and §11, on three points: how far a
content-level identification carries through a chain, whether the list of the
vendor's proprietary content is closed, and what counts as naming the vendor.
All three decide C flags and none decides an R flag, so the conflation fields
alone are coded again. A coder that never saw a rule cannot have applied it, and
a quote located under one rule is not evidence under another.

The output goes to a third directory. Nothing already on disk is overwritten:
each pass stays readable as the reading it was.

Assignments are filled in from `data/fulltext_log.csv` and substituted for the
bracketed fields.

---

You are coder `{CODER}` in a planned double-coding exercise. Code exactly ONE
work on the **conflation flags (§6) only**, and write the result as JSON.

Read these two files, in this order:

1. `data/coding_protocol.md` — the coding protocol. Apply it exactly as written;
   do not improvise beyond it. **§6 and §11 were amended on 2026-08-20; read §12
   before you code, so you know which rules are recent and what shape each was
   written for.** Three of those rules decide most contested cases: a
   content-level identification carries only its own content, the list of
   proprietary content is closed, and identity is not established by anaphora.
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
- **Do not read any file in `coding_raw/`.** Two earlier codings of this work
  exist there, including your own. Reading them would make this an edit of a
  previous answer rather than a reading of the text.
- **Do not code the E gate, the instrument code, or the R flags.** They are
  settled and are not part of this pass. Code the conflation flags on their own
  terms: §6 applies to every work whatever its E code and whatever roles its
  vendor citation plays.
- **You may not identify a phrase as the vendor's from anything but this text.**
  §6 closes the list of proprietary content to the Assertive/Turbulent axis, the
  four role groupings and the branded type names. The vendor's aspect labels for
  the dichotomies the MBTI does have — Mind, Energy, Nature, Tactics — are
  outside the flags. If a work presents those as the MBTI's, record it in
  `free_text` and do not set a flag for it.
- §3.6: one retrieved file can hold several works. Code only the part belonging
  to the work named above. Sentences from a neighbouring paper in the same file
  are not evidence for this work.
- Every flag you set needs a located verbatim quote plus the section it came
  from. Copy the source wording exactly inside the quote; never paraphrase
  inside quotation marks. If the source is not in English, quote the original
  and put your English gloss after the closing quote.
- Where a flag rests on a chain across sentences (§6), quote **every link**,
  joined by ` || ` in the one quote field. A chain must begin from an explicit
  identification; a definite description carried over from an earlier sentence
  is not one.
- §7 gives expected codes for three calibration records. If the work you are
  coding is one of them, code it from the text yourself anyway. If your reading
  differs from the expected code, say so in `uncertain_note`.
- You are working independently. Do not try to find or infer the other coder's
  output.
- If the protocol genuinely does not decide a case, set `uncertain` to true and
  explain what is undecided. Do not invent a rule and do not guess.

Write your result as JSON to `coding_raw/conflation_{CODER}/{KEY}.json`, using
exactly these keys:

```json
{
  "key": "{KEY}",
  "coder": "{CODER}",
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

- `conflation` — §6. Set every flag explicitly true or false. `c0` is true
  exactly when none of C1-C3 applies.
- `conflation_narrow` — the same three flags under the **narrow** reading, which
  feeds sensitivity arm S7 (§11). A work qualifies for the narrow arm if it
  **names the vendor's test or site anywhere** — in prose, in a footnote, in a
  reference entry, or by a bare URL. In a work that does not name the vendor
  anywhere, every narrow flag is false. The narrow flags are a subset of the
  wide ones: never set a narrow flag whose wide flag is false.
- `conflation_quotes` — one entry per flag you set true, keyed by the flag name
  (`"c1"`, `"c2"`, `"c3"`). Empty object if none. No entry for `c0`.
- `states_distinction` — §6: the work states somewhere that the vendor's test
  and the MBTI are not the same instrument, whether or not it also conflates
  them. A derivation predicate ("a variant in the MBTI family") asserts descent
  and is **not** a statement of the distinction. Quote it.
- `third_party_conflation` — §6: the work calls some *other* look-alike
  instrument (Humanmetrics, Truity, and their kind) "the MBTI". Recorded, never
  rated. Quote it.
- `free_text` — anything the fields cannot hold, including an aspect-label
  merger you were told above not to flag. Null if nothing.

Create no file other than that JSON. Your final message must be exactly:
`conflation {KEY} {CODER}`
