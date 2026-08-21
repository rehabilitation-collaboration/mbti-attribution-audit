"""Put the pending works on one page the author can rule from.

`adjudication.md` is the record; this is the desk. It follows the audit sheet
the ninth paper used: what the object is, what has been decided about it so
far, and one place to write. The difference that matters is the CSV — a ruling
is one line of `data/adjudications.csv`, the file is read line by line, and a
newline typed into a reason splits one ruling into two rows of which the second
is not a ruling — so the reason is a single-line field and the line is
assembled by the page rather than by hand.

Nothing on the page decides anything. The proposal sits beside the two codings
as a third reading, and taking it is a button the author presses, because §9
reserves the ruling for the author. Nothing is aggregated either: §10 fixes the
analysis before the codes are counted, so the page shows the works and not
their distribution.

Every verbatim is written whole and then checked: each string handed to the
page is looked for in what it wrote, and a miss is an error rather than a
shorter file. The first version of the markdown sheet cut its quotes
mid-sentence without saying so, which is the failure this check exists to make
impossible.

Output
    coding_raw/proposed-rulings.html   git-ignored: it quotes the same
                                       third-party text the raw codings do
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

import pandas as pd

from build_classification import normalise_quote
from item_wording import ASKED, VALUE_JA, WATCH
from make_adjudication_sheet import LABELS, coder_value

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "coding_raw"
ASSETS = Path(__file__).resolve().parent / "ruling_assets"
CLASSIFICATION = ROOT / "data" / "classification.csv"
PROPOSALS = RAW / "proposals"
OUT = RAW / "proposed-rulings.html"

PASSES = ("gate", "flags", "conflation")

def esc(value) -> str:
    """Show a quote as `classification.csv` stores it.

    Coders supplied located quotes in three shapes — a string, a
    `{"quote": …, "section": …}` object, or a list of either — and printing the
    object shape as JSON puts punctuation from the file format in front of the
    sentence the author has to read. The normalisation the published table uses
    joins them instead, and loses nothing: the check below looks for each part.
    """
    return html.escape(normalise_quote(value))


def esc_quote(value, gloss: dict | None = None) -> str:
    """The paper's own words, with a Japanese reading kept underneath.

    The other blocks on this page put the Japanese first, because the argument
    they carry was written to be read. A quote is not that: it is the sentence
    the code rests on, and the ruling is made against it rather than against
    anyone's rendering of it. So the original leads and the gloss is folded
    away — help for reading, not a thing to rule from.
    """
    text = esc(value)
    if not text:
        return "<i>引用なし — このフラグは立っていない</i>"
    ja = (gloss or {}).get(normalise_quote(value))
    if not ja:
        return f'<div class="text">{text}</div>'
    return (
        f'<div class="text">{text}</div>'
        f'<details class="orig"><summary>参考訳（日本語）— 判断は上の原文で</summary>'
        f'<div class="text ja">{html.escape(ja)}</div></details>'
    )


def leaves(value) -> list[str]:
    """Every string a coder wrote inside a quote, whatever shape it came in."""
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, dict):
        return [leaf for part in value.values() for leaf in leaves(part)]
    if isinstance(value, list):
        return [leaf for part in value for leaf in leaves(part)]
    return []


def shown(value) -> str:
    """The code, and what it means, because the code alone is not readable."""
    text = "" if value is None else str(value)
    if not text:
        return '<span class="val">空欄</span>'
    meaning = VALUE_JA.get(text)
    said = html.escape(text)
    return (
        f'<span class="val">{said}</span>'
        + (f" {html.escape(meaning)}" if meaning else "")
    )


def bilingual(ja: str | None, en, label: str = "原文（英語）") -> str:
    """The Japanese first, the English kept underneath.

    The author reads Japanese; the argument was written in English. Showing
    only the translation would put a rendering between the author and the
    evidence, so the original stays on the page, one click away, and the
    verbatim check below still finds it.
    """
    english = esc(en)
    if not ja:
        return f'<div class="text">{english}</div>'
    return (
        f'<div class="text">{html.escape(ja)}</div>'
        f'<details class="orig"><summary>{label}</summary>'
        f'<div class="text en">{english}</div></details>'
    )


NAMED = re.compile(r"16\s?personalities|16personalities\.com|NERIS", re.I)


def check_headings_are_plain() -> None:
    """A tag in `ASKED` reaches the page as visible characters.

    The questions are escaped into an `<h3>`, so `<b>` written in one shows up
    as `&lt;b&gt;` — which is what happened, in the sheet, while it was being
    read. Catching it here costs one comparison and saves the author from
    reading markup.
    """
    for name, text in ASKED.items():
        if html.escape(text) != text:
            raise SystemExit(
                f"ASKED[{name!r}] contains markup or an escapable character: "
                f"headings are escaped, so it would be shown literally"
            )


def names_the_vendor(key: str) -> bool:
    """Whether the work names the vendor's test or site anywhere (§6, §11 S7).

    §6 assesses naming per work and counts prose, a footnote, a reference entry
    or a bare URL, so a match anywhere in the retrieved text settles it. The
    narrow items are not a second judgement: where the vendor is named they take
    the wide item's value, and only a work that never names it drops to False.
    """
    path = ROOT / "fulltext" / f"{key}.txt"
    return bool(path.exists() and NAMED.search(path.read_text(errors="ignore")))


def take(key: str, item: str, value, label: str = "これに決める", own: bool = False) -> str:
    attr = html.escape("" if value is None else str(value))
    return (
        f'<button data-key="{html.escape(key)}" data-item="{html.escape(item)}" '
        f'data-value="{attr}"{" data-own=\"1\"" if own else ""}>{label}</button>'
    )


def reading(css: str, who: str, body: str, button: str = "") -> str:
    return f'<div class="said {css}"><div class="body">{who}{body}</div>{button}</div>'


def render_item(key: str, item: str, v1, q1, v2, q2, ruling: dict | None,
                tr: dict | None = None, gloss: dict | None = None) -> str:
    """One contested item: three readings and one place to write."""
    ja = (tr or {}).get("rulings", {}).get(item)
    parts = [
        f'<div class="item" data-key="{html.escape(key)}" data-item="{html.escape(item)}">',
        f"<h3>{html.escape(ASKED.get(item, item))}"
        f'<span class="key"><code>{html.escape(item)}</code> · '
        f"{html.escape(LABELS.get(item, item))}</span></h3>"
        + (f'<p class="watch">{WATCH[item]}</p>' if item in WATCH else ""),
        reading(
            "c1",
            f'<span class="who">AI-1 (sonnet) の答え — {shown(v1)}</span>',
            f'<div class="lab">根拠にした英文</div>{esc_quote(q1, gloss)}',
            take(key, item, v1),
        ),
        reading(
            "c2",
            f'<span class="who">AI-2 (opus) の答え — {shown(v2)}</span>',
            f'<div class="lab">根拠にした英文</div>{esc_quote(q2, gloss)}',
            take(key, item, v2),
        ),
    ]

    if ruling:
        # `matches` names a coder, and the coder names collide with the C flag
        # names, so it is spelt out rather than printed bare.
        whose = (
            "どちらの AI も間違い、という提案"
            if ruling["matches"] == "neither"
            else f"AI-{'1' if ruling['matches'] == 'c1' else '2'} と同じ"
        )
        confidence = {"high": "自信あり", "medium": "自信は中くらい"}.get(
            str(ruling["confidence"]), str(ruling["confidence"])
        )
        parts.append(
            reading(
                "p",
                f'<span class="who">3 体目の AI の提案 — {shown(ruling["proposed"])}'
                f"（{html.escape(whose)}・{html.escape(confidence)}）</span>",
                f'<div class="lab">根拠にした英文</div>{esc_quote(ruling["quote"], gloss)}'
                f'<div class="lab">なぜそう読むか</div>{bilingual(ja, ruling["reasoning"])}',
                take(key, item, ruling["proposed"]),
            )
        )

    own = [
        '<div class="own">どれも採らんとき、自分で書く値 ',
        '<input class="ownval" size="16" placeholder="true / false / a / E1 …">',
        take(key, item, None, "この値に決める", own=True),
    ]
    if item == "instrument_sublabel":
        own.append(take(key, item, "", "空欄に決める（§3.4）"))
    own.append("</div>")

    # A narrow item is the wide one's value unless the work never names the
    # vendor, so where it does, the wide item's ruling can simply be carried
    # over rather than decided twice.
    if item.startswith("narrow_") and names_the_vendor(key):
        wide = item.removeprefix("narrow_")
        own.append(
            f'<div class="mirror" data-wide="{html.escape(wide)}">'
            f'この作品は 16Personalities を名指ししている。'
            f'<code>{html.escape(wide)}</code> を決めると、その値をここにも入れられる '
            f'<button class="same" data-key="{html.escape(key)}" data-item="{html.escape(item)}" '
            f'data-wide="{html.escape(wide)}">同じ値にする</button></div>'
        )

    parts += [
        '<div class="ruling">',
        "<label>決めた理由 — 1 行で書いてから、採る答えのボタンを押す（日本語でよい）</label>",
        '<input placeholder="例: 業者の系譜やなく MBTI の格の話をしてるだけやから C2 ではない">',
        "".join(own),
        '<div class="decided" hidden></div>',
        '<div class="after"><button class="undo">この決定を取り消す</button>'
        '<span class="hint">決めた内容はブラウザに残る。ページを作り直しても消えない</span></div>',
        "</div>",
        "</div>",
    ]
    return "\n".join(parts)


def render_work(index: int, row: pd.Series, codings: dict, proposal: dict | None,
                tr: dict | None = None, gloss: dict | None = None) -> tuple[str, list]:
    """One work, and every string that must survive into the page verbatim."""
    key = row["key"]
    contested = [c for c in str(row["contested"]).split(",") if c] if pd.notna(row["contested"]) else []
    uncertain = [u for u in str(row["uncertain_by"]).split(",") if u] if pd.notna(row["uncertain_by"]) else []
    proposals = {r["item"]: r for r in (proposal or {}).get("rulings", [])}
    tr = tr or {}
    verbatim: list[tuple[str, str]] = []

    parts = [
        f'<h2 id="w{index}">{index}. <code>{html.escape(key)}</code></h2>',
        f'<p class="meta">{html.escape(str(row["title"]))}<br>'
        f'{html.escape(str(row["doi"]))} — <code>{html.escape(str(row["work_venue_class"]))}</code></p>',
    ]

    if proposal and proposal.get("protocol_gap"):
        verbatim.append((f"{key} protocol_gap", proposal["protocol_gap"]))
        parts.append(
            '<div class="gap"><b>🔴 ここは規則が決めていない — だから人が決めるしかない</b>'
            + bilingual(tr.get("protocol_gap"), proposal["protocol_gap"])
            + "</div>"
        )

    for item in contested:
        v1, q1 = coder_value(*[codings["c1"][p] for p in PASSES], item)
        v2, q2 = coder_value(*[codings["c2"][p] for p in PASSES], item)
        if q1:
            verbatim.append((f"{key} {item} c1 quote", q1))
        if q2:
            verbatim.append((f"{key} {item} c2 quote", q2))
        ruling = proposals.get(item)
        if ruling:
            verbatim.append((f"{key} {item} proposal quote", ruling["quote"]))
            verbatim.append((f"{key} {item} proposal reasoning", ruling["reasoning"]))
        parts.append(render_item(key, item, v1, q1, v2, q2, ruling, tr, gloss))

    if not contested:
        parts.append('<p class="readonly">2 体の答えは全項目で一致してる。下の申告を読むだけでよい。読んだ時点で片付く。変えたいときだけ行を書く。</p>')

    for who in uncertain:
        coder, _, which = who.partition(":")
        note = codings[coder][which]["uncertain_note"]
        if note:
            verbatim.append((f"{key} {who} uncertain_note", note))
        parts.append(
            f'<div class="note"><b>AI-{"1" if coder == "c1" else "2"} が「規則がこの場合を決めてない」と手を挙げた</b>'
            + (
                bilingual(tr.get("uncertain_notes", {}).get(who), note)
                if note
                else '<div class="text">（注記なし）</div>'
            )
            + "</div>"
        )

    free = []
    for coder in ("c1", "c2"):
        for which in PASSES:
            text = codings[coder][which]["free_text"]
            if text:
                verbatim.append((f"{key} {coder}/{which} free_text", text))
                free.append(
                    f'<div class="freeitem"><b>{coder}/{which}</b>'
                    + bilingual(tr.get("free_text", {}).get(f"{coder}/{which}"), text)
                    + "</div>"
                )
    if free:
        parts.append(
            f"<details><summary>AI が残したメモ（{len(free)} 件・読まんでもよい）</summary>{''.join(free)}</details>"
        )

    if proposal and proposal.get("notes"):
        verbatim.append((f"{key} notes", proposal["notes"]))
        parts.append(
            "<details><summary>提案した AI のメモ</summary>"
            + bilingual(tr.get("notes"), proposal["notes"])
            + "</details>"
        )

    return "\n".join(parts), verbatim


def check_nothing_was_cut(page: str, verbatim: list[tuple[str, str]]) -> int:
    """Fail rather than publish an argument that stops without ending.

    The failure this catches is silent by construction: a truncated page is a
    well-formed page, and the reader cannot tell a severed argument from a
    finished one.
    """
    checked = 0
    for name, value in verbatim:
        for leaf in leaves(value):
            checked += 1
            if html.escape(leaf) not in page:
                raise SystemExit(
                    f"{name} did not survive into the page whole ({len(leaf)} characters). "
                    "Nothing may be abridged here."
                )
    return checked


def read_glosses() -> dict[str, str]:
    """Japanese readings for the quotes, keyed by the quote itself."""
    out = {}
    for path in sorted((RAW / "quote_ja").glob("*.json")):
        for row in json.loads(path.read_text(encoding="utf-8")):
            out[normalise_quote(row["quote"])] = row["ja"]
    return out


def read_translation(key: str) -> dict:
    """The Japanese rendering, where one has been made. Absent is not an error:
    the page falls back to the English, which is the source of record."""
    path = RAW / "translations" / f"{key}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def read_codings(key: str) -> dict[str, dict[str, dict]]:
    def load(folder: str) -> dict:
        return json.loads((RAW / folder / f"{key}.json").read_text(encoding="utf-8"))

    return {
        coder: {"gate": load(coder), "flags": load(f"flags_{coder}"), "conflation": load(f"conflation_{coder}")}
        for coder in ("c1", "c2")
    }


def order(pending: pd.DataFrame) -> list[tuple[pd.Series, dict | None]]:
    """Works needing a ruling first, and among those the ones the protocol
    does not decide, because those are the ones only the author can settle."""
    rows = []
    for _, row in pending.iterrows():
        path = PROPOSALS / f"{row['key']}.json"
        proposal = json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
        split = pd.notna(row["contested"]) and str(row["contested"])
        gap = bool(proposal and proposal.get("protocol_gap"))
        rows.append(((0 if split else 1, 0 if gap else 1, str(row["key"])), row, proposal))
    return [(row, proposal) for _, row, proposal in sorted(rows, key=lambda r: r[0])]


def main() -> None:
    check_headings_are_plain()
    frame = pd.read_csv(CLASSIFICATION)
    pending = frame[frame["needs_adjudication"]]
    ordered = order(pending)

    glosses = read_glosses()
    bodies, verbatim, links, untranslated = [], [], [], 0
    for index, (row, proposal) in enumerate(ordered, start=1):
        translation = read_translation(row["key"])
        if not translation:
            untranslated += 1
        body, strings = render_work(
            index, row, read_codings(row["key"]), proposal, translation, glosses
        )
        bodies.append(body)
        verbatim += strings
        split = bool(pd.notna(row["contested"]) and str(row["contested"]))
        gap = bool(proposal and proposal.get("protocol_gap"))
        links.append((index, row["key"], row["title"], split, gap))

    items = sum(
        len([c for c in str(row["contested"]).split(",") if c])
        for row, _ in ordered
        if pd.notna(row["contested"])
    )
    toc = ['<div class="toc">']
    for heading, wanted in (
        ("🔴 規則が決めていない項目がある — 裁定が要る", lambda s, g: s and g),
        ("割れている — 裁定が要る", lambda s, g: s and not g),
        ("読むだけ — コーダーが uncertain を挙げただけ（変えるときだけ行を書く）", lambda s, g: not s),
    ):
        chosen = [link for link in links if wanted(link[3], link[4])]
        toc.append(f"<b>{heading} — {len(chosen)} 作品</b><ol>")
        for index, key, title, _, _ in chosen:
            toc.append(
                f'<li value="{index}"><a href="#w{index}"><code>{html.escape(key)}</code></a> '
                f"{html.escape(str(title))}</li>"
            )
        toc.append("</ol>")
    toc.append("</div>")

    page = (ASSETS / "page.html").read_text(encoding="utf-8")
    for marker, value in (
        ("<!--CSS-->", (ASSETS / "ruling.css").read_text(encoding="utf-8")),
        ("<!--JS-->", (ASSETS / "ruling.js").read_text(encoding="utf-8")),
        ("<!--ITEMS-->", str(items)),
        ("<!--CORPUS-->", str(len(frame))),
        ("<!--READONLY-->", str(sum(1 for link in links if not link[3]))),
        ("<!--TOC-->", "".join(toc)),
        ("<!--BODY-->", "".join(bodies)),
    ):
        if marker not in page:
            raise SystemExit(f"{marker} is missing from page.html")
        page = page.replace(marker, value)

    checked = check_nothing_was_cut(page, verbatim)
    OUT.write_text(page, encoding="utf-8")

    gaps = sum(1 for link in links if link[4])
    print(
        f"wrote {OUT.relative_to(ROOT)} — {len(pending)} works, {items} split items, "
        f"{gaps} with a protocol gap, {checked} strings verified whole, "
        f"{OUT.stat().st_size:,} bytes"
    )
    if untranslated:
        print(f"  ⚠️  {untranslated} of {len(pending)} works have no Japanese yet")
    print(f"  {len(glosses)} quotes carry a Japanese gloss")


if __name__ == "__main__":
    main()
