"""Assemble the coders' per-work JSON into data/classification.csv.

Each work in `data/fulltext_log.csv` with `status == "ok"` is coded twice and
independently — c1 by `claude-sonnet-5`, c2 by `claude-opus-5` — against
`data/coding_protocol.md`, each coder seeing the protocol and one full text and
nothing else.

The codings arrive in three passes, and this script reads all three. The **gate
pass** (`coding_raw/<coder>/`) carries the E code, the instrument code and
`text_is_abstract`. The **flag pass** (`coding_raw/flags_<coder>/`) carries the R
flags, re-coded after §12's first set of amendments. The **conflation pass**
(`coding_raw/conflation_<coder>/`) carries the C flags, the narrow C flags and
`states_distinction`, re-coded after the second set, made on 2026-08-20.

Each pass is read only for what it settles. The flag pass also holds conflation
codings, made under the rules the second amendment replaced; they stay on disk as
the reading they were and are not read here. A coder that never saw a rule cannot
have applied it, and no amendment has ever touched §3, so the gate pass stands.

Where the coders agree, the agreed value is written to the `*_final` column and
the row is not adjudicated: there is nothing for the author to rule on. Where
they disagree, or where either coder set `uncertain` in either pass, the final
columns are left empty and `needs_adjudication` marks the row. §9 reserves that
ruling for the author, so this script never breaks a tie — not by majority, not
by seniority of model, not by any rule that would let an agent decide a code.

`third_party_conflation` has no final column by design. §6 records that shape
and refuses to rate it: the corpus is built from 16Personalities word forms, so
works conflating other look-alikes enter it only by accident and no proportion
over them would have a denominator.

**Rulings live in `data/adjudications.csv`, not in this script's output.** This
script rebuilds `classification.csv` from the codings every time it runs, so a
ruling typed into that file would be erased by the next run. The author writes
one row per ruling — key, item, ruling, reasoning — and the ruling is applied
here, which keeps it through every rebuild and keeps the reasoning next to the
code it settles. The file may not exist yet; then nothing is adjudicated.

Outputs
    data/classification.csv  one row per coded work, published
    stdout                   the disagreement list, for the adjudication pass

Inputs beyond the codings
    data/adjudications.csv   the author's rulings (optional), columns:
                             key, item, ruling, reasoning
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "coding_raw"
LOG = ROOT / "data" / "fulltext_log.csv"
OUT = ROOT / "data" / "classification.csv"
RULINGS = ROOT / "data" / "adjudications.csv"
DISCHARGED = ROOT / "data" / "discharged.csv"

CODERS = ("c1", "c2")
E_CODES = {"E1", "E2", "E3", "E4"}
INSTRUMENTS = {"a", "b", "c"}
SUBLABELS = {
    "c-unnamed",
    "c-online",
    "c-authormade",
    "c-vendor-cited-only",
    "c-translated",
    "c-named-unsourced",
}
R_FLAGS = ("r1", "r2", "r3", "r4", "r5", "r6", "r7")
C_FLAGS = ("c0", "c1", "c2", "c3")
NARROW_FLAGS = ("c1", "c2", "c3")

GATE_KEYS = {
    "key",
    "coder",
    "e_code",
    "e_quote",
    "instrument",
    "instrument_sublabel",
    "instrument_quote",
    "instrument_evidence_level",
    "text_is_abstract",
    "text_is_abstract_evidence",
    "uncertain",
    "uncertain_note",
    "free_text",
}

CONFLATION_KEYS = {
    "key",
    "coder",
    "conflation",
    "conflation_quotes",
    "conflation_narrow",
    "states_distinction",
    "states_distinction_quote",
    "third_party_conflation",
    "third_party_conflation_quote",
    "uncertain",
    "uncertain_note",
    "free_text",
}

FLAG_KEYS = CONFLATION_KEYS | {"roles", "role_quotes"}


class SchemaError(ValueError):
    """A coder's JSON does not carry what the protocol requires of it."""


def normalise_quote(value) -> str:
    """Read a located quote in any of the three shapes the coders supplied.

    §9 asks for a located verbatim *and* its section, and §6 asks for every link
    of a cross-sentence chain. Coders met those requirements three ways: one
    string, a `{"quote": …, "section": …}` object, or a list of either when a
    flag rests on several passages. All three carry the same information, and
    none is a violation of the protocol — the brief simply did not fix a shape.
    Everything is stored as "verbatim — section", chained with " || ".
    """
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        quote = str(value.get("quote", "")).strip()
        section = str(value.get("section", "")).strip()
        if quote and section:
            return f"{quote} — {section}"
        return quote or section
    if isinstance(value, list):
        return " || ".join(part for item in value if (part := normalise_quote(item)))
    raise SchemaError(
        f"a quote must be a string, a quote/section object, or a list of those, "
        f"got {type(value).__name__}"
    )


def _check_identity(doc: dict, key: str, coder: str, required: set[str]) -> str:
    where = f"{coder}/{key}"
    missing = required - set(doc)
    if missing:
        raise SchemaError(f"{where}: missing keys {sorted(missing)}")
    if doc["key"] != key or doc["coder"] != coder:
        raise SchemaError(f"{where}: file names {doc['key']}/{doc['coder']}")
    return where


def validate_gate(doc: dict, key: str, coder: str) -> None:
    """Reject a gate coding that cannot be read as the protocol defines it."""
    where = _check_identity(doc, key, coder, GATE_KEYS)
    if doc["e_code"] not in E_CODES:
        raise SchemaError(f"{where}: e_code {doc['e_code']!r}")

    instrument = doc["instrument"]
    if doc["e_code"] == "E1":
        if instrument not in INSTRUMENTS:
            raise SchemaError(f"{where}: E1 needs an instrument code, got {instrument!r}")
    elif instrument is not None:
        raise SchemaError(f"{where}: {doc['e_code']} must not carry an instrument code")

    sub = doc["instrument_sublabel"]
    if sub is not None:
        if instrument != "c":
            raise SchemaError(f"{where}: sublabel {sub!r} on instrument {instrument!r}")
        if sub not in SUBLABELS:
            raise SchemaError(f"{where}: unknown sublabel {sub!r}")


def validate_flags(doc: dict, key: str, coder: str) -> None:
    """Reject a flag coding that cannot be read as the protocol defines it.

    Silent acceptance is the failure mode that matters: a missing flag that
    defaults to false would enter the counts as a coded absence rather than as
    the omission it is.
    """
    where = _check_identity(doc, key, coder, FLAG_KEYS)
    _check_boolean_map(doc, where, "roles", R_FLAGS)
    _check_quotes(doc, where, "role_quotes", "roles", R_FLAGS)
    _check_conflation_fields(doc, where)


def _check_boolean_map(doc: dict, where: str, field: str, flags: tuple[str, ...]) -> None:
    got = doc[field]
    if not isinstance(got, dict) or set(got) != set(flags):
        raise SchemaError(f"{where}: {field} must set exactly {list(flags)}")
    if not all(isinstance(v, bool) for v in got.values()):
        raise SchemaError(f"{where}: {field} values must be booleans")


def _check_quotes(doc: dict, where: str, field: str, source: str, flags: tuple[str, ...]) -> None:
    for flag in flags:
        if flag == "c0" or not doc[source][flag]:
            continue
        if not normalise_quote(doc[field].get(flag)):
            raise SchemaError(f"{where}: {flag} set without a quote in {field}")


def _check_conflation_fields(doc: dict, where: str) -> None:
    """The checks the conflation fields carry, in whichever pass produced them."""
    for field, flags in (("conflation", C_FLAGS), ("conflation_narrow", NARROW_FLAGS)):
        _check_boolean_map(doc, where, field, flags)

    conf = doc["conflation"]
    if conf["c0"] == any(conf[f] for f in ("c1", "c2", "c3")):
        raise SchemaError(f"{where}: c0 must be true exactly when C1-C3 are all false")

    # The narrow reading is a subset of the wide one: a work that never names the
    # vendor cannot conflate more under the narrow arm than under the wide one.
    for flag in NARROW_FLAGS:
        if doc["conflation_narrow"][flag] and not conf[flag]:
            raise SchemaError(f"{where}: narrow {flag} set while wide {flag} is not")

    _check_quotes(doc, where, "conflation_quotes", "conflation", C_FLAGS)

    for field in ("states_distinction", "third_party_conflation"):
        if doc[field] and not normalise_quote(doc[f"{field}_quote"]):
            raise SchemaError(f"{where}: {field} set without a quote")


def validate_conflation(doc: dict, key: str, coder: str) -> None:
    """Reject a conflation coding that carries roles it was told not to code.

    A stray `roles` map would be silently dropped, which would hide a reading a
    coder actually made rather than record it — the same failure a missing flag
    would be, in the other direction.
    """
    where = _check_identity(doc, key, coder, CONFLATION_KEYS)
    if stray := {"roles", "role_quotes"} & set(doc):
        raise SchemaError(f"{where}: the conflation pass must not carry {sorted(stray)}")
    _check_conflation_fields(doc, where)


PASSES = {
    "gate": (lambda coder: coder, validate_gate),
    "flags": (lambda coder: f"flags_{coder}", validate_flags),
    "conflation": (lambda coder: f"conflation_{coder}", validate_conflation),
}


def load(key: str, coder: str, pass_: str) -> dict:
    directory, validate = PASSES[pass_]
    path = RAW / directory(coder) / f"{key}.json"
    if not path.exists():
        raise FileNotFoundError(f"no {pass_} coding for {coder}/{key}")
    doc = json.loads(path.read_text(encoding="utf-8"))
    validate(doc, key, coder)
    return doc


def agree(a, b):
    """Return the agreed value, or None when the coders differ."""
    return a if a == b else None


BOOLEAN_ITEMS = set(R_FLAGS) | set(C_FLAGS) | {
    f"narrow_{f}" for f in NARROW_FLAGS
} | {"states_distinction", "text_is_abstract"}

# Most items carry each coder's reading beside an adjudicated `<item>_final`.
# Two do not: §9's published table names the settled value of the sub-label and
# of the abstract test without a suffix, so a ruling on either lands there.
BARE_FINAL = {"instrument_sublabel", "text_is_abstract"}


def final_column(item: str) -> str:
    """The column a ruling on this item writes to."""
    return item if item in BARE_FINAL else f"{item}_final"


def parse_ruling(item: str, ruling: str):
    """Read a ruling as the type its column holds."""
    text = str(ruling).strip()
    if item in BOOLEAN_ITEMS:
        lowered = text.lower()
        if lowered in {"true", "yes", "1"}:
            return True
        if lowered in {"false", "no", "0"}:
            return False
        raise SchemaError(f"ruling on {item} must be true or false, got {ruling!r}")
    return text


def load_discharged() -> dict[str, str]:
    """Works the author has read and left exactly as the coders had them.

    §9 hands every uncertainty to the author, and the adjudication sheet settles
    what that costs: a work flagged uncertain with no split code needs a row only
    if something is changing, and otherwise "the flag is discharged by your
    having read it". Reading leaves no trace in the codings, so it is recorded
    here. Without a file saying which works were read, "the author looked and
    changed nothing" cannot be told apart from "nobody looked", and the second is
    the state this study spent three coding passes trying not to be in.

    A work with a split code is never discharged this way — that would let a
    disagreement pass as settled without anyone settling it — so `apply_rulings`
    ignores the entry and the row stays contested.
    """
    if not DISCHARGED.exists():
        return {}
    out = {}
    with DISCHARGED.open(encoding="utf-8") as handle:
        reader = csv.reader(handle)
        header = next(reader, None)
        if header != ["key", "reasoning"]:
            raise SchemaError(
                f"{DISCHARGED.name} must start with key,reasoning — got {header}"
            )
        for line, row in enumerate(reader, start=2):
            if not row:
                continue
            if len(row) < 2:
                raise SchemaError(f"{DISCHARGED.name} line {line}: needs key,reasoning")
            out[row[0].strip()] = ",".join(row[1:]).strip()
    return out


def load_rulings() -> dict[str, dict[str, tuple[object, str]]]:
    """The author's rulings, keyed by work and then by contested item.

    Absent file means nothing has been adjudicated yet, which is a state this
    study passes through rather than an error.
    """
    if not RULINGS.exists():
        return {}

    rows = list(csv.reader(RULINGS.read_text(encoding="utf-8").splitlines()))
    rows = [r for r in rows if any(field.strip() for field in r)]
    if not rows:
        return {}

    header = [h.strip().lower() for h in rows[0]]
    required = ["key", "item", "ruling", "reasoning"]
    if header[:4] != required:
        raise SchemaError(
            f"{RULINGS.name}: the first line must be exactly "
            f"'key,item,ruling,reasoning' — got {','.join(header) or '(empty)'}"
        )

    rulings: dict[str, dict[str, tuple[object, str]]] = {}
    for n, row in enumerate(rows[1:], start=2):
        if len(row) < 4:
            raise SchemaError(
                f"{RULINGS.name} line {n}: needs four fields "
                f"(key, item, ruling, reasoning), found {len(row)}: {','.join(row)!r}"
            )
        # Reasoning is prose and will contain commas. Anything after the third
        # comma belongs to it, whether or not the author remembered to quote it —
        # unquoted commas used to shift the columns and surface far downstream as
        # a ruling on a work that does not exist.
        key, item, ruling = (field.strip() for field in row[:3])
        reasoning = ",".join(row[3:]).strip()
        if not key or not item:
            continue
        rulings.setdefault(key, {})[item] = (parse_ruling(item, ruling), reasoning)
    return rulings


def discharge(row: dict, reasoning: str) -> dict:
    """Record that the author read a work and left the coders' values alone.

    Only an uncertainty can be discharged this way. A split code is a
    disagreement between two readings and needs someone to choose between them;
    letting a "read it" entry clear one would put an unsettled tie into the
    counts as though it were settled.
    """
    if [c for c in str(row["contested"]).split(",") if c]:
        return row
    row["needs_adjudication"] = False
    note = f"read by the author, unchanged: {reasoning}"
    row["note"] = f"{row['note']} || {note}" if row["note"] else note
    return row


def apply_rulings(row: dict, rulings: dict[str, tuple[object, str]]) -> dict:
    """Fill the final columns the author has ruled on, and say who ruled.

    A ruling on an item the coders agreed about is applied too and reported:
    §9 lets the author overrule a shared reading, and silently ignoring such a
    row would hide a decision rather than record it.
    """
    if not rulings:
        return row

    contested = [c for c in str(row["contested"]).split(",") if c]
    notes = []
    for item, (value, reasoning) in sorted(rulings.items()):
        column = final_column(item)
        if column not in row:
            raise SchemaError(f"{row['key']}: no column for a ruling on {item!r}")
        overruled = item not in contested and row[column] != "" and row[column] != value
        row[column] = value
        if item in contested:
            contested.remove(item)
        notes.append(f"{item} -> {value}" + (" (overruled agreement)" if overruled else "") + f": {reasoning}")

    row["contested"] = ",".join(contested)
    row["adjudicated"] = True
    row["note"] = " || ".join(notes)
    # Uncertainty flagged by a coder is discharged by the author having looked.
    row["needs_adjudication"] = bool(contested)
    return row


def build_row(
    key: str,
    meta: pd.Series,
    gate: dict[str, dict],
    flag: dict[str, dict],
    conf: dict[str, dict],
) -> dict:
    g1, g2 = gate["c1"], gate["c2"]
    f1, f2 = flag["c1"], flag["c2"]
    k1, k2 = conf["c1"], conf["c2"]
    contested: list[str] = []

    row: dict[str, object] = {
        "key": key,
        "doi": meta["doi"],
        "title": meta["title"],
        "work_venue_class": meta["work_venue_class"],
        "c1_e": g1["e_code"],
        "c2_e": g2["e_code"],
    }

    e_final = agree(g1["e_code"], g2["e_code"])
    row["e_final"] = e_final or ""
    if e_final is None:
        contested.append("e")

    row["c1_instrument"] = g1["instrument"] or ""
    row["c2_instrument"] = g2["instrument"] or ""
    instrument_final = agree(g1["instrument"], g2["instrument"])
    # An instrument code is only meaningful once both coders have placed the work
    # in E1; §9 computes its kappa on exactly that subset.
    if e_final != "E1":
        instrument_final = None
    row["instrument_final"] = instrument_final or ""
    if e_final == "E1" and instrument_final is None:
        contested.append("instrument")

    sub_final = agree(g1["instrument_sublabel"], g2["instrument_sublabel"])
    row["c1_instrument_sublabel"] = g1["instrument_sublabel"] or ""
    row["c2_instrument_sublabel"] = g2["instrument_sublabel"] or ""
    row["instrument_sublabel"] = (sub_final or "") if instrument_final == "c" else ""
    # §3.4: the sub-labels are neither exhaustive nor required, so a difference
    # between an empty one and a filled one is not a disagreement to rule on.
    if instrument_final == "c" and sub_final is None and all(
        g[k] for g, k in ((g1, "instrument_sublabel"), (g2, "instrument_sublabel"))
    ):
        contested.append("instrument_sublabel")

    for flag_name in R_FLAGS:
        row[f"{flag_name}_c1"] = f1["roles"][flag_name]
        row[f"{flag_name}_c2"] = f2["roles"][flag_name]
        final = agree(f1["roles"][flag_name], f2["roles"][flag_name])
        row[f"{flag_name}_final"] = "" if final is None else final
        if final is None:
            contested.append(flag_name)

    for flag_name in C_FLAGS:
        row[f"{flag_name}_c1"] = k1["conflation"][flag_name]
        row[f"{flag_name}_c2"] = k2["conflation"][flag_name]
        final = agree(k1["conflation"][flag_name], k2["conflation"][flag_name])
        row[f"{flag_name}_final"] = "" if final is None else final
        if final is None:
            contested.append(flag_name)

    for flag_name in NARROW_FLAGS:
        col = f"narrow_{flag_name}"
        row[f"{col}_c1"] = k1["conflation_narrow"][flag_name]
        row[f"{col}_c2"] = k2["conflation_narrow"][flag_name]
        final = agree(k1["conflation_narrow"][flag_name], k2["conflation_narrow"][flag_name])
        row[f"{col}_final"] = "" if final is None else final
        if final is None:
            contested.append(col)

    for field in ("states_distinction",):
        row[f"{field}_c1"] = k1[field]
        row[f"{field}_c2"] = k2[field]
        final = agree(k1[field], k2[field])
        row[f"{field}_final"] = "" if final is None else final
        if final is None:
            contested.append(field)

    # Recorded, never rated (§6): no final column, no contested entry.
    row["third_party_conflation_c1"] = k1["third_party_conflation"]
    row["third_party_conflation_c2"] = k2["third_party_conflation"]
    row["third_party_conflation_quote"] = " || ".join(
        q for k in (k1, k2) if (q := normalise_quote(k["third_party_conflation_quote"]))
    )

    abstract_final = agree(g1["text_is_abstract"], g2["text_is_abstract"])
    row["text_is_abstract_c1"] = g1["text_is_abstract"]
    row["text_is_abstract_c2"] = g2["text_is_abstract"]
    row["text_is_abstract"] = "" if abstract_final is None else abstract_final
    if abstract_final is None:
        contested.append("text_is_abstract")

    row["quote_e"] = g1["e_quote"] if e_final else ""
    row["quote_instrument"] = (g1["instrument_quote"] or "") if instrument_final else ""
    row["quote_r4"] = normalise_quote(f1["role_quotes"].get("r4")) if row["r4_final"] is True else ""
    row["quote_conflation"] = " || ".join(
        q
        for f in ("c1", "c2", "c3")
        if row[f"{f}_final"] is True and (q := normalise_quote(k1["conflation_quotes"].get(f)))
    )
    row["quote_states_distinction"] = (
        normalise_quote(k1["states_distinction_quote"])
        if row["states_distinction_final"] is True
        else ""
    )

    def passes(coder: str):
        return ("gate", gate[coder]), ("flags", flag[coder]), ("conflation", conf[coder])

    uncertain = sorted(
        {f"{c}:{p}" for c in CODERS for p, d in passes(c) if d["uncertain"]}
    )
    row["uncertain_by"] = ",".join(uncertain)
    row["uncertain_note"] = " || ".join(
        f"{c}/{p}: {d['uncertain_note']}"
        for c in CODERS
        for p, d in passes(c)
        if d["uncertain"] and d["uncertain_note"]
    )
    row["free_text"] = " || ".join(
        f"{c}/{p}: {d['free_text']}"
        for c in CODERS
        for p, d in passes(c)
        if d["free_text"]
    )
    row["contested"] = ",".join(contested)
    row["needs_adjudication"] = bool(contested) or bool(uncertain)
    row["adjudicated"] = False
    row["note"] = ""
    return row


def main() -> None:
    log = pd.read_csv(LOG).set_index("key")
    keys = log.index[log["status"] == "ok"].tolist()
    rulings = load_rulings()
    discharged = load_discharged()

    rows, missing = [], []
    for key in keys:
        try:
            gate = {c: load(key, c, "gate") for c in CODERS}
            flag = {c: load(key, c, "flags") for c in CODERS}
            conf = {c: load(key, c, "conflation") for c in CODERS}
        except FileNotFoundError as exc:
            missing.append(str(exc))
            continue
        row = apply_rulings(
            build_row(key, log.loc[key], gate, flag, conf), rulings.get(key, {})
        )
        if key in discharged:
            row = discharge(row, discharged[key])
        rows.append(row)

    unknown = set(rulings) - set(keys)
    if unknown:
        raise SchemaError(f"{RULINGS.name} rules on works not in the corpus: {sorted(unknown)}")

    astray = set(discharged) - set(keys)
    if astray:
        raise SchemaError(f"{DISCHARGED.name} names works not in the corpus: {sorted(astray)}")

    if missing:
        print(f"not yet coded ({len(missing)}):")
        for m in missing:
            print(f"  {m}")

    if not rows:
        # Mid-pass this is the normal state, and writing would replace a good
        # file with an empty one — the loss would look like a successful run.
        raise SchemaError(
            f"no work could be assembled from all three passes; {OUT.name} left as it was"
        )

    frame = pd.DataFrame(rows)
    frame.to_csv(OUT, index=False)
    print(f"\nwrote {OUT.relative_to(ROOT)} — {len(frame)} of {len(keys)} works")
    if rulings:
        print(f"applied rulings from {RULINGS.name}: {len(rulings)} works")
    else:
        print(f"no {RULINGS.name} yet — nothing adjudicated")

    if frame.empty:
        return
    pending = frame[frame["needs_adjudication"]]
    print(f"awaiting the author's ruling: {len(pending)} of {len(frame)}")
    for _, row in pending.iterrows():
        reason = row["contested"] or "flagged uncertain"
        print(f"  {row['key']}: {reason}")


if __name__ == "__main__":
    main()
