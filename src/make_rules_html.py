"""Print every item's question beside the protocol text it was made from.

The ruling sheet asks each contested item as a Japanese question. Those
questions are a translation, and in one place a compression — `r4`'s heading
carries a parenthesis that is not in §5's table but in a paragraph below it. A
reader who cannot see which is which has to take the sheet's word for the rule.
So this page puts the four things side by side for all eighteen items: the
question as the sheet asks it, the protocol's own words verbatim, the provisos
that decide the awkward cases, and — marked as such — anything the sheet added.

Every quotation is checked against `data/coding_protocol.md` before the page is
written. A proviso that has drifted from the protocol is an error rather than a
page, because a summary nobody can check is what this page exists to replace.

Output
    coding_raw/rules.html   git-ignored with the rest of coding_raw, though it
                            quotes only the published protocol
"""

from __future__ import annotations

import html
import re
from pathlib import Path

from make_adjudication_sheet import LABELS
from item_wording import ASKED
from rules_ja import GROUPS

ROOT = Path(__file__).resolve().parent.parent
ASSETS = Path(__file__).resolve().parent / "ruling_assets"
PROTOCOL = ROOT / "data" / "coding_protocol.md"
OUT = ROOT / "coding_raw" / "rules.html"


def bold(text: str) -> str:
    """`**…**` is markdown; the Japanese is rendered as HTML."""
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)


def plain(text: str) -> str:
    """The protocol's words without the markdown that decorates them."""
    text = text.replace("**", "").replace("`", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def check_against_protocol(quotes: list[tuple[str, str]]) -> int:
    """Fail rather than publish a paraphrase that has drifted from the rule.

    An ellipsis joins two stretches of the protocol and an em dash often stands
    where a table cell boundary was, so each side of both is looked for
    separately. Matching is on the words: the protocol is markdown, and this
    page renders the same sentences as HTML.
    """
    source = plain(PROTOCOL.read_text(encoding="utf-8"))
    checked, adrift = 0, []
    for name, english in quotes:
        for fragment in (f.strip() for f in re.split(r"…|—", english)):
            if len(fragment) < 15:
                continue
            checked += 1
            if plain(fragment) not in source:
                adrift.append(f"{name}: {fragment[:100]}")
    if adrift:
        raise SystemExit(
            "these are not what the protocol says:\n  "
            + "\n  ".join(adrift)
            + f"\n({len(adrift)} of {checked} quotations)"
        )
    return checked


def render_item(item: dict) -> tuple[str, list[tuple[str, str]]]:
    quotes = []
    parts = [
        '<section class="rule-item">',
        f'<h3><code>{html.escape(item["name"])}</code> '
        f'{html.escape(ASKED.get(item["name"], item["question"]))}</h3>',
        f'<p class="src">{html.escape(item["label"])} — 出典 {html.escape(item["source"])}</p>',
    ]

    if item["verbatim"]:
        parts.append('<table class="codes">')
        for code, english, japanese in item["verbatim"]:
            quotes.append((f'{item["name"]} {code}', english))
            parts.append(
                f"<tr><td><code>{html.escape(code)}</code></td>"
                f'<td><div class="en">{html.escape(english)}</div>'
                f'<div class="ja">{html.escape(japanese)}</div></td></tr>'
            )
        parts.append("</table>")

    for english, japanese in item["provisos"]:
        quotes.append((f'{item["name"]} proviso', english))
        parts.append(
            f'<div class="proviso"><div class="ja">{bold(japanese)}</div>'
            f"<details><summary>原文（§ の逐語）</summary>"
            f'<div class="en">{html.escape(plain(english))}</div></details></div>'
        )

    for note in item["ours"]:
        parts.append(f'<div class="ours"><b>★画面の問いは、ここを 1 行にまとめてある</b><div>{bold(note)}</div></div>')

    parts.append("</section>")
    return "\n".join(parts), quotes


def main() -> None:
    body, quotes, toc = [], [], []
    for group in GROUPS:
        toc.append(f'<li>{html.escape(group["heading"])}</li>')
        body.append(f'<h2>{html.escape(group["heading"])}</h2>')
        body.append(f'<p class="note">{html.escape(group["note"])}</p>')
        for item in group["items"]:
            rendered, found = render_item(item)
            body.append(rendered)
            quotes += found
        for english, japanese in group.get("shared", []):
            quotes.append((f'{group["heading"]} shared', english))
            body.append(
                f'<div class="proviso shared"><div class="ja">{bold(japanese)}</div>'
                f"<details><summary>原文（§ の逐語）</summary>"
                f'<div class="en">{html.escape(plain(english))}</div></details></div>'
            )

    checked = check_against_protocol(quotes)
    items = sum(len(g["items"]) for g in GROUPS)
    # The count comes from the codebook rather than from a number typed here,
    # which is how this page came to say eighteen when there are nineteen.
    missing = set(LABELS) - {i["name"] for g in GROUPS for i in g["items"]}
    if missing:
        raise SystemExit(f"these items have no entry: {sorted(missing)}")

    page = f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>判定項目の全一覧 — MBTI attribution audit</title>
<style>
{(ASSETS / "ruling.css").read_text(encoding="utf-8")}
{(ASSETS / "rules.css").read_text(encoding="utf-8")}
</style>
</head>
<body>

<h1>判定項目の全一覧 — {items} 項目</h1>

<div class="lead">
<p>裁定シートが出している<b>日本語の問い</b>と、それが作られた<b>規則の原文</b>を並べたもの。</p>
<ul>
  <li><b>日本語はすべてうちの訳</b>。原文と食い違って見えたら<b>原文が正</b>。各項目に §番号を書いてあるので
      <code>data/coding_protocol.md</code> で前後ごと読める</li>
  <li><b>★ 印はうちが足したもの</b>。規則の原文にはその形では書かれていない</li>
  <li>ここに載せた原文の引用は、ページを書く前に <code>coding_protocol.md</code> と
      <b>{checked} 箇所すべて突き合わせて</b>いる。1 つでもずれていたら、このページは書かれずに落ちる</li>
</ul>
<ol class="toc-inline">{"".join(toc)}</ol>
</div>

{"".join(body)}

</body>
</html>"""

    OUT.write_text(page, encoding="utf-8")
    print(
        f"wrote {OUT.relative_to(ROOT)} — {items} items, {checked} quotations "
        f"checked against the protocol, {OUT.stat().st_size:,} bytes"
    )


if __name__ == "__main__":
    main()
