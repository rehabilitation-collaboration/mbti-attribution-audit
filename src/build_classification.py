"""Assemble the coders' per-work JSON into data/classification.csv.

Each work in `data/fulltext_log.csv` with `status == "ok"` is coded twice and
independently — c1 by `claude-sonnet-5`, c2 by `claude-opus-5` — against
`data/coding_protocol.md`, each coder seeing the protocol and one full text and
nothing else.

The codings arrive in two passes, and this script reads both. The **gate pass**
(`coding_raw/<coder>/`) carries the E code, the instrument code and
`text_is_abstract`. The **flag pass** (`coding_raw/flags_<coder>/`) carries the R
and C flags, re-coded after §12's amendments; a coder that never saw a rule
cannot have applied it, so the flags were read again rather than patched. No
amendment touches §3, so the gate pass stands as it is.

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

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "coding_raw"
LOG = ROOT / "data" / "fulltext_log.csv"
OUT = ROOT / "data" / "classification.csv"
RULINGS = ROOT / "data" / "adjudications.csv"

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

FLAG_KEYS = {
    "key",
    "coder",
    "roles",
    "role_quotes",
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

    for field, flags in (
        ("roles", R_FLAGS),
        ("conflation", C_FLAGS),
        ("conflation_narrow", NARROW_FLAGS),
    ):
        got = doc[field]
        if not isinstance(got, dict) or set(got) != set(flags):
            raise SchemaError(f"{where}: {field} must set exactly {list(flags)}")
        if not all(isinstance(v, bool) for v in got.values()):
            raise SchemaError(f"{where}: {field} values must be booleans")

    conf = doc["conflation"]
    if conf["c0"] == any(conf[f] for f in ("c1", "c2", "c3")):
        raise SchemaError(f"{where}: c0 must be true exactly when C1-C3 are all false")

    # The narrow reading is a subset of the wide one: a statement that names the
    # vendor's test is also a statement about the vendor.
    for flag in NARROW_FLAGS:
        if doc["conflation_narrow"][flag] and not conf[flag]:
            raise SchemaError(f"{where}: narrow {flag} set while wide {flag} is not")

    for field, source, flags in (
        ("role_quotes", "roles", R_FLAGS),
        ("conflation_quotes", "conflation", C_FLAGS),
    ):
        for flag in flags:
            if flag == "c0" or not doc[source][flag]:
                continue
            if not normalise_quote(doc[field].get(flag)):
                raise SchemaError(f"{where}: {flag} set without a quote in {field}")

    for field in ("states_distinction", "third_party_conflation"):
        if doc[field] and not normalise_quote(doc[f"{field}_quote"]):
            raise SchemaError(f"{where}: {field} set without a quote")


def load(key: str, coder: str, *, flags: bool) -> dict:
    directory = RAW / (f"flags_{coder}" if flags else coder)
    path = directory / f"{key}.json"
    if not path.exists():
        raise FileNotFoundError(f"no {'flag' if flags else 'gate'} coding for {coder}/{key}")
    doc = json.loads(path.read_text(encoding="utf-8"))
    (validate_flags if flags else validate_gate)(doc, key, coder)
    return doc


def agree(a, b):
    """Return the agreed value, or None when the coders differ."""
    return a if a == b else None


BOOLEAN_ITEMS = set(R_FLAGS) | set(C_FLAGS) | {
    f"narrow_{f}" for f in NARROW_FLAGS
} | {"states_distinction", "text_is_abstract"}


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


def load_rulings() -> dict[str, dict[str, tuple[object, str]]]:
    """The author's rulings, keyed by work and then by contested item.

    Absent file means nothing has been adjudicated yet, which is a state this
    study passes through rather than an error.
    """
    if not RULINGS.exists():
        return {}
    frame = pd.read_csv(RULINGS).fillna("")
    required = {"key", "item", "ruling", "reasoning"}
    if not required.issubset(frame.columns):
        raise SchemaError(f"{RULINGS.name} needs columns {sorted(required)}")

    rulings: dict[str, dict[str, tuple[object, str]]] = {}
    for _, row in frame.iterrows():
        key, item = str(row["key"]).strip(), str(row["item"]).strip()
        if not key or not item:
            continue
        rulings.setdefault(key, {})[item] = (
            parse_ruling(item, row["ruling"]),
            str(row["reasoning"]).strip(),
        )
    return rulings


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
        column = f"{item}_final"
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


def build_row(key: str, meta: pd.Series, gate: dict[str, dict], flag: dict[str, dict]) -> dict:
    g1, g2 = gate["c1"], gate["c2"]
    f1, f2 = flag["c1"], flag["c2"]
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
        row[f"{flag_name}_c1"] = f1["conflation"][flag_name]
        row[f"{flag_name}_c2"] = f2["conflation"][flag_name]
        final = agree(f1["conflation"][flag_name], f2["conflation"][flag_name])
        row[f"{flag_name}_final"] = "" if final is None else final
        if final is None:
            contested.append(flag_name)

    for flag_name in NARROW_FLAGS:
        col = f"narrow_{flag_name}"
        row[f"{col}_c1"] = f1["conflation_narrow"][flag_name]
        row[f"{col}_c2"] = f2["conflation_narrow"][flag_name]
        final = agree(f1["conflation_narrow"][flag_name], f2["conflation_narrow"][flag_name])
        row[f"{col}_final"] = "" if final is None else final
        if final is None:
            contested.append(col)

    for field in ("states_distinction",):
        row[f"{field}_c1"] = f1[field]
        row[f"{field}_c2"] = f2[field]
        final = agree(f1[field], f2[field])
        row[f"{field}_final"] = "" if final is None else final
        if final is None:
            contested.append(field)

    # Recorded, never rated (§6): no final column, no contested entry.
    row["third_party_conflation_c1"] = f1["third_party_conflation"]
    row["third_party_conflation_c2"] = f2["third_party_conflation"]
    row["third_party_conflation_quote"] = " || ".join(
        q for f in (f1, f2) if (q := normalise_quote(f["third_party_conflation_quote"]))
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
        if row[f"{f}_final"] is True and (q := normalise_quote(f1["conflation_quotes"].get(f)))
    )
    row["quote_states_distinction"] = (
        normalise_quote(f1["states_distinction_quote"])
        if row["states_distinction_final"] is True
        else ""
    )

    uncertain = sorted(
        {f"{c}:{pass_}" for c in CODERS for pass_, d in (("gate", gate[c]), ("flags", flag[c])) if d["uncertain"]}
    )
    row["uncertain_by"] = ",".join(uncertain)
    row["uncertain_note"] = " || ".join(
        f"{c}/{pass_}: {d['uncertain_note']}"
        for c in CODERS
        for pass_, d in (("gate", gate[c]), ("flags", flag[c]))
        if d["uncertain"] and d["uncertain_note"]
    )
    row["free_text"] = " || ".join(
        f"{c}/{pass_}: {d['free_text']}"
        for c in CODERS
        for pass_, d in (("gate", gate[c]), ("flags", flag[c]))
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

    rows, missing = [], []
    for key in keys:
        try:
            gate = {c: load(key, c, flags=False) for c in CODERS}
            flag = {c: load(key, c, flags=True) for c in CODERS}
        except FileNotFoundError as exc:
            missing.append(str(exc))
            continue
        rows.append(apply_rulings(build_row(key, log.loc[key], gate, flag), rulings.get(key, {})))

    unknown = set(rulings) - set(keys)
    if unknown:
        raise SchemaError(f"{RULINGS.name} rules on works not in the corpus: {sorted(unknown)}")

    if missing:
        print(f"not yet coded ({len(missing)}):")
        for m in missing:
            print(f"  {m}")

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
