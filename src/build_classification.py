"""Assemble the two coders' per-work JSON into data/classification.csv.

Each work in `data/fulltext_log.csv` with `status == "ok"` is coded twice and
independently — c1 by `claude-sonnet-5`, c2 by `claude-opus-5` — against
`data/coding_protocol.md`, each coder seeing the protocol and one full text and
nothing else. Each run writes one JSON to `coding_raw/<coder>/<key>.json`. This
script checks those files against the schema the protocol implies and lays them
out as the one-row-per-work table §9 specifies.

Where the coders agree, the agreed value is written to the `*_final` column and
the row is not adjudicated: there is nothing for the author to rule on. Where
they disagree, or where either coder set `uncertain`, the final columns are left
empty and `needs_adjudication` marks the row. §9 reserves that ruling for the
author, so this script never breaks a tie — not by majority, not by seniority of
model, not by any rule that would let an agent decide a code.

Quotes follow the same principle. A `quote_*` column carries the agreed coder's
located verbatim only when the code behind it is agreed; a contested code leaves
its quote empty until the ruling supplies one.

Outputs
    data/classification.csv  one row per coded work, published
    stdout                   the disagreement list, for the adjudication pass
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "coding_raw"
LOG = ROOT / "data" / "fulltext_log.csv"
OUT = ROOT / "data" / "classification.csv"

CODERS = ("c1", "c2")
E_CODES = {"E1", "E2", "E3", "E4"}
INSTRUMENTS = {"a", "b", "c"}
SUBLABELS = {
    "c-unnamed",
    "c-online",
    "c-authormade",
    "c-vendor-cited-only",
    "c-translated",
}
R_FLAGS = ("r1", "r2", "r3", "r4", "r5", "r6")
C_FLAGS = ("c0", "c1", "c2", "c3")

REQUIRED_KEYS = {
    "key",
    "coder",
    "e_code",
    "e_quote",
    "instrument",
    "instrument_sublabel",
    "instrument_quote",
    "instrument_evidence_level",
    "roles",
    "role_quotes",
    "conflation",
    "conflation_quotes",
    "text_is_abstract",
    "text_is_abstract_evidence",
    "uncertain",
    "uncertain_note",
    "free_text",
}


class SchemaError(ValueError):
    """A coder's JSON does not carry what the protocol requires of it."""


def validate(doc: dict, key: str, coder: str) -> None:
    """Reject a coding that cannot be read as the protocol defines it.

    Silent acceptance is the failure mode that matters here: a missing flag that
    defaults to false would enter the count as a coded absence rather than as
    the omission it is.
    """
    where = f"{coder}/{key}"
    missing = REQUIRED_KEYS - set(doc)
    if missing:
        raise SchemaError(f"{where}: missing keys {sorted(missing)}")
    if doc["key"] != key or doc["coder"] != coder:
        raise SchemaError(f"{where}: file names {doc['key']}/{doc['coder']}")
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

    for field, flags in (("roles", R_FLAGS), ("conflation", C_FLAGS)):
        got = doc[field]
        if not isinstance(got, dict) or set(got) != set(flags):
            raise SchemaError(f"{where}: {field} must set exactly {list(flags)}")
        if not all(isinstance(v, bool) for v in got.values()):
            raise SchemaError(f"{where}: {field} values must be booleans")

    conf = doc["conflation"]
    if conf["c0"] == any(conf[f] for f in ("c1", "c2", "c3")):
        raise SchemaError(f"{where}: c0 must be true exactly when C1-C3 are all false")

    for field, flags in (("role_quotes", R_FLAGS), ("conflation_quotes", C_FLAGS)):
        source = "roles" if field == "role_quotes" else "conflation"
        for flag in flags:
            if flag == "c0":
                continue
            if doc[source][flag] and not (doc[field].get(flag) or "").strip():
                raise SchemaError(f"{where}: {flag} set without a quote in {field}")


def load(key: str, coder: str) -> dict:
    path = RAW / coder / f"{key}.json"
    if not path.exists():
        raise FileNotFoundError(f"no coding for {coder}/{key}")
    doc = json.loads(path.read_text(encoding="utf-8"))
    validate(doc, key, coder)
    return doc


def agree(a, b):
    """Return the agreed value, or None when the coders differ."""
    return a if a == b else None


def build_row(key: str, meta: pd.Series, docs: dict[str, dict]) -> dict:
    c1, c2 = docs["c1"], docs["c2"]
    contested: list[str] = []

    row: dict[str, object] = {
        "key": key,
        "doi": meta["doi"],
        "title": meta["title"],
        "work_venue_class": meta["work_venue_class"],
        "c1_e": c1["e_code"],
        "c2_e": c2["e_code"],
    }

    e_final = agree(c1["e_code"], c2["e_code"])
    row["e_final"] = e_final or ""
    if e_final is None:
        contested.append("e")

    row["c1_instrument"] = c1["instrument"] or ""
    row["c2_instrument"] = c2["instrument"] or ""
    instrument_final = agree(c1["instrument"], c2["instrument"])
    # An instrument code is only meaningful once both coders have placed the work
    # in E1; §9 computes its kappa on exactly that subset.
    if e_final != "E1":
        instrument_final = None
    row["instrument_final"] = instrument_final or ""
    if e_final == "E1" and instrument_final is None:
        contested.append("instrument")

    sub_final = agree(c1["instrument_sublabel"], c2["instrument_sublabel"])
    row["c1_instrument_sublabel"] = c1["instrument_sublabel"] or ""
    row["c2_instrument_sublabel"] = c2["instrument_sublabel"] or ""
    row["instrument_sublabel"] = (sub_final or "") if instrument_final == "c" else ""
    if instrument_final == "c" and sub_final is None:
        contested.append("instrument_sublabel")

    for flag in R_FLAGS:
        row[f"{flag}_c1"] = c1["roles"][flag]
        row[f"{flag}_c2"] = c2["roles"][flag]
        final = agree(c1["roles"][flag], c2["roles"][flag])
        row[f"{flag}_final"] = "" if final is None else final
        if final is None:
            contested.append(flag)

    for flag in C_FLAGS:
        row[f"{flag}_c1"] = c1["conflation"][flag]
        row[f"{flag}_c2"] = c2["conflation"][flag]
        final = agree(c1["conflation"][flag], c2["conflation"][flag])
        row[f"{flag}_final"] = "" if final is None else final
        if final is None:
            contested.append(flag)

    abstract_final = agree(c1["text_is_abstract"], c2["text_is_abstract"])
    row["text_is_abstract_c1"] = c1["text_is_abstract"]
    row["text_is_abstract_c2"] = c2["text_is_abstract"]
    row["text_is_abstract"] = "" if abstract_final is None else abstract_final
    if abstract_final is None:
        contested.append("text_is_abstract")

    row["quote_instrument"] = (c1["instrument_quote"] or "") if instrument_final else ""
    row["quote_r4"] = c1["role_quotes"].get("r4", "") if row["r4_final"] is True else ""
    conflation_quote = ""
    if any(row[f"{f}_final"] is True for f in ("c1", "c2", "c3")):
        conflation_quote = " | ".join(
            q for f in ("c1", "c2", "c3") if (q := c1["conflation_quotes"].get(f))
        )
    row["quote_conflation"] = conflation_quote
    row["quote_e"] = c1["e_quote"] if e_final else ""

    uncertain = [c for c in CODERS if docs[c]["uncertain"]]
    row["uncertain_by"] = ",".join(uncertain)
    row["uncertain_note"] = " || ".join(
        f"{c}: {docs[c]['uncertain_note']}" for c in uncertain if docs[c]["uncertain_note"]
    )
    row["free_text"] = " || ".join(
        f"{c}: {docs[c]['free_text']}" for c in CODERS if docs[c]["free_text"]
    )
    row["contested"] = ",".join(contested)
    row["needs_adjudication"] = bool(contested) or bool(uncertain)
    row["adjudicated"] = False
    row["note"] = ""
    return row


def main() -> None:
    log = pd.read_csv(LOG).set_index("key")
    keys = log.index[log["status"] == "ok"].tolist()

    rows, missing = [], []
    for key in keys:
        try:
            docs = {c: load(key, c) for c in CODERS}
        except FileNotFoundError as exc:
            missing.append(str(exc))
            continue
        rows.append(build_row(key, log.loc[key], docs))

    if missing:
        print(f"not yet coded ({len(missing)}):")
        for m in missing:
            print(f"  {m}")

    frame = pd.DataFrame(rows)
    frame.to_csv(OUT, index=False)
    print(f"\nwrote {OUT.relative_to(ROOT)} — {len(frame)} of {len(keys)} works")

    if frame.empty:
        return
    pending = frame[frame["needs_adjudication"]]
    print(f"awaiting the author's ruling: {len(pending)} of {len(frame)}")
    for _, row in pending.iterrows():
        reason = row["contested"] or "flagged uncertain"
        print(f"  {row['key']}: {reason}")


if __name__ == "__main__":
    main()
