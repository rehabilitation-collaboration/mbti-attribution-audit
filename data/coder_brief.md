# Coder brief

The instruction each coder receives, verbatim. It is published because the
coders are language models, and what a model was asked is part of how its output
should be read — the equivalent of the training a human coder was given.

One coder run handles one work. Runs share nothing: no coder sees another's
output, another work's text, or its own earlier runs. Assignments are filled in
from `data/fulltext_log.csv` and substituted for the bracketed fields.

---

You are coder `{CODER}` in a planned double-coding exercise for a bibliometric
audit. Code exactly ONE work and write the result as JSON.

Read these two files, in this order:

1. `data/coding_protocol.md` — the coding protocol. Apply it exactly as written;
   do not improvise beyond it.
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
- §3.6: one retrieved file can hold several works. Code only the part belonging
  to the work named above. Sentences from a neighbouring paper in the same file
  are not evidence for this work — including for the R and C flags.
- Every code you assign needs a located verbatim quote plus the section it came
  from. Copy the source wording exactly inside the quote; never paraphrase
  inside quotation marks. If the source is not in English, quote the original
  and put your English gloss after the closing quote.
- §7 gives expected codes for three calibration records. If the work you are
  coding is one of them, code it from the text yourself anyway and record what
  the text supports. If your reading differs from the expected code, say so in
  `uncertain_note` rather than deferring to the table.
- You are working independently. Do not try to find or infer the other coder's
  output.
- If the protocol genuinely does not decide a case, set `uncertain` to true and
  explain what is undecided. Do not invent a rule and do not guess.

Write your result as JSON to `coding_raw/{CODER}/{KEY}.json`, using exactly
these keys:

```json
{
  "key": "{KEY}",
  "coder": "{CODER}",
  "e_code": "E1",
  "e_quote": "verbatim — section name",
  "instrument": "a",
  "instrument_sublabel": null,
  "instrument_quote": "verbatim — section name",
  "instrument_evidence_level": 1,
  "roles": {"r1": false, "r2": false, "r3": false, "r4": false, "r5": false, "r6": false},
  "role_quotes": {},
  "conflation": {"c0": true, "c1": false, "c2": false, "c3": false},
  "conflation_quotes": {},
  "text_is_abstract": false,
  "text_is_abstract_evidence": null,
  "uncertain": false,
  "uncertain_note": null,
  "free_text": null
}
```

Field notes:

- `e_code` — one of `E1`, `E2`, `E3`, `E4` (§2). A mixed work takes one code by
  the priority E1 > E3 > E2 > E4.
- `instrument` — `"a"`, `"b"` or `"c"` (§3). Null unless `e_code` is `E1`.
- `instrument_evidence_level` — which level of the §3.1 hierarchy decided the
  code (1-4); null if there is no instrument code.
- `instrument_sublabel` — only when `instrument` is `"c"` (§3.4); otherwise null.
- `roles` / `conflation` — §5 and §6, coded whatever the E code is. Set every
  flag explicitly true or false. `c0` is true only when none of C1-C3 applies.
- `role_quotes` / `conflation_quotes` — one entry per flag you set true, keyed by
  the flag name (`"r4"`, `"c2"`, …). Empty object if none.
- `text_is_abstract` — §3.6.
- `free_text` — a second instrument (§4.2), a non-human arm, or anything the
  fields cannot hold. Null if nothing.

Create no file other than that JSON. Your final message must be exactly:
`done {KEY} {CODER}`
