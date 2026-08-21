"""What each item asks, in Japanese, beside the protocol text it comes from.

The ruling sheet prints a Japanese question above every contested item. Those
questions are a translation and, in a few places, a compression: `r4` is headed
"評価尺度の信頼性・妥当性の根拠として引用しているか（数値が要る）", and only the
first half of that is the row in §5's table — the parenthesis is a summary of a
paragraph further down. A reader who cannot check which is which has to take the
sheet's word for the rule, which is the thing this study asks of nobody.

So each entry carries four fields: the item's name, the question as the sheet
asks it, the protocol's own words verbatim, and the provisos that decide the
awkward cases. Anything written here that is not a quotation is marked as ours.

`SOURCE` lines give the section, so a reader can open `data/coding_protocol.md`
and read the surrounding argument rather than this summary of it.
"""

from __future__ import annotations

# Each group: (heading, note, [items])
# Each item: {name, question, source, verbatim: [(code, english, japanese)],
#             provisos: [(english, japanese)], ours: [str]}

GROUPS = [
    {
        "heading": "① まず振り分け — 型データはどこから来たか",
        "note": "全 61 作品にコードする。ここで E1 になった作品だけが ② に進む。",
        "items": [
            {
                "name": "e",
                "question": "型データはどこから来たか",
                "label": "E gate (§2)",
                "source": "§2 — Step 1: where the type data came from",
                "verbatim": [
                    ("E1", "primary administration — Respondents completed a personality instrument for this study.",
                     "この研究のために、回答者が性格検査を受けた"),
                    ("E2", "secondary type data — Type labels came from an existing dataset, scraped profiles, or another study. The authors administered nothing.",
                     "型ラベルは既存データセット・スクレイプしたプロフィール・他の研究から来た。著者は何も実施していない"),
                    ("E3", "non-human respondents — An instrument was administered, but to a language model or other artificial agent.",
                     "検査は実施されたが、相手は言語モデル等の人工エージェント"),
                    ("E4", "no type data — The work reports no type data: reviews, position pieces, translation and validation studies of the instrument itself, instrument or software design papers.",
                     "型データを報告していない。レビュー・意見文・検査自体の翻訳/検証研究・検査やソフトの設計論文"),
                ],
                "provisos": [
                    ("**E2 requires the work to hold type data**, not to cite a result computed from it. A position piece that reprints another study's published type distribution, with attribution, and argues from the percentages is E4: it possesses no type labels, only a finding about them.",
                     "E2 は「型データを持っている」ことを要求する。そこから計算された結果を引用しているだけでは足りない。他の研究の型分布を出典付きで再掲して％から論じる意見文は E4。型ラベルを持たず、それについての知見を持っているだけだから"),
                    ("**Mixed works** are coded on one code, by priority **E1 > E3 > E2 > E4**. … The priority is fixed here so it is not decided case by case.",
                     "混在する作品は 1 つのコードに決める。優先順位は E1 > E3 > E2 > E4。その場ごとに決めないよう、ここで固定してある"),
                    ("Where a work says nothing about provenance but reports type frequencies for named participants, it is E1 with the instrument coded `(c)` (§3): failing to say what was administered is the finding, not a reason to exclude.",
                     "出所を何も書いていないが、名指しされた参加者の型頻度を報告している場合は E1 +(c)。何を実施したか書いていないこと自体が発見であって、除外の理由ではない"),
                    ("**Only E1 works receive an instrument code.** E2, E3 and E4 works are still coded for §5 and §6",
                     "instrument コードが付くのは E1 の作品だけ。E2/E3/E4 も §5 と §6 はコードする"),
                ],
                "ours": [],
            },
        ],
    },
    {
        "heading": "② E1 の作品だけ — 何を実施したか",
        "note": "証拠は階層で読む。上の段が使えるなら下の段では覆せない。",
        "items": [
            {
                "name": "instrument",
                "question": "何を実施したか",
                "label": "instrument (a)/(b)/(c) (§3)",
                "source": "§3 — Step 2: instrument attribution, coded on E1 works only",
                "verbatim": [
                    ("(a)", "The instrument administered was the 16Personalities test / NERIS Type Explorer.",
                     "実施したのは 16Personalities のテスト / NERIS Type Explorer"),
                    ("(b)", "The instrument administered was a published MBTI form.",
                     "実施したのは出版された MBTI 用紙"),
                    ("(c)", "The instrument administered cannot be identified from the work.",
                     "何を実施したか、その作品からは特定できない"),
                ],
                "provisos": [
                    ("Coded from the highest available level; a lower level never overrides a higher. … A statement in Methods of what respondents completed. … A named instrument carrying a citation or URL that resolves to one of the two. … An appendix, figure, or screenshot showing the administered items or the result screen. … Reference-list evidence only — a vendor URL among the references, with no statement anywhere of what was administered.",
                     "使える一番上の段でコードする。下の段が上の段を覆すことはない。① Methods に「回答者が何を完了したか」の記載 → ② 引用や URL 付きで名指しされた検査 → ③ 実施項目や結果画面を示す付録・図・スクショ → ④ 参考文献だけ"),
                    ("Any of: `16personalities`, `16 Personalities`, `16personalities.com`, `NERIS Type Explorer`, `NERIS Analytics`, or a described free/online test whose cited URL resolves to the vendor's domain — **stated as the thing respondents completed**.",
                     "(a) の引き金: 16personalities / 16 Personalities / 16personalities.com / NERIS Type Explorer / NERIS Analytics、またはベンダーのドメインに解決する URL 付きで説明された無料・オンライン検査 —— ただし「回答者が完了したもの」として述べられている場合"),
                    ("Any of: `Form M`, `Form G`, `Form Q`, `MBTI Step I`, `MBTI Step II`, a statement of purchase, licence or certified administration from The Myers-Briggs Company, CPP, OPP or a national distributor, or an authorised translation identified as licensed. … **Citing the MBTI Manual is not by itself (b).** Works cite Myers et al. for background while administering something else entirely; (b) requires a statement about what respondents completed, not about what the authors read.",
                     "(b) の引き金: Form M / Form G / Form Q / MBTI Step I / Step II、購入・ライセンス・認定実施の記載など。★MBTI マニュアルを引用しているだけでは (b) にならない。まったく別のものを実施しながら背景として Myers らを引く作品があるから。(b) が要求するのは「回答者が何を完了したか」であって「著者が何を読んだか」ではない"),
                    ("A work that never says what respondents completed, but cites a vendor page among its references, is coded **(c) with `c-vendor-cited-only`** — not (a). … Nothing is lost by the conservative choice: **S3 in §11 counts these as (a)**, so the PLAN's rule survives as a fixed sensitivity arm and both numbers are reported.",
                     "§4.1 — 回答者が何を完了したか一度も書かず、参考文献にベンダーのページを引いている作品は (a) ではなく (c) + c-vendor-cited-only。保守的に取っても失うものはない。感度分析 S3 がこれらを (a) として数えるので、両方の数字が報告される"),
                    ("Where a work administers both — a published form and the vendor's test, or two unnamed tests — it is coded on the instrument that produced the types used in the reported results, and the other is recorded in free text. Where both feed the results equally, code (a) if the vendor's test is one of them, and record why",
                     "§4.2 — 両方実施している場合は、報告された結果に使われた型を生んだ方でコードする。両方が同等に結果に寄与しているなら、ベンダーのテストが含まれていれば (a)"),
                    ("An authorised translation of a published form is (b). A translation of unstated provenance is (c) `c-translated`. A translated version of the vendor's test is (a). Where the work describes translating \"the MBTI\" from an online source, the URL decides; with no URL it is (c) `c-online`.",
                     "§4.3 — 出版用紙の正規翻訳は (b)。出所不明の翻訳は (c) c-translated。ベンダーのテストの翻訳版は (a)。オンライン源から「MBTI」を翻訳したと書いている場合は URL が決める。URL が無ければ (c) c-online"),
                ],
                "ours": [],
            },
            {
                "name": "instrument_sublabel",
                "question": "(c) の内訳 — 特定できない書き方のどれか（空欄でよい）",
                "label": "(c) sub-label (§3.4)",
                "source": "§3.4 — (c) and its sub-labels",
                "verbatim": [
                    ("c-unnamed", '"The MBTI was administered", with no form, publisher, version or URL.',
                     "「MBTI を実施した」だけで、用紙・出版社・版・URL が無い"),
                    ("c-online", "An unnamed online or free MBTI test.",
                     "名前のないオンライン/無料の MBTI テスト"),
                    ("c-authormade", "Items the authors wrote themselves, described as based on the MBTI.",
                     "著者が自分で書いた項目。MBTI に基づくと説明されている"),
                    ("c-vendor-cited-only", "Nothing in Methods, but a vendor URL appears in the reference list.",
                     "Methods に記載なし。参考文献にベンダー URL がある"),
                    ("c-translated", "A translated MBTI-type questionnaire with no licence or source stated.",
                     "翻訳された MBTI 型質問紙。ライセンスも出典も書かれていない"),
                    ("c-named-unsourced", "An instrument named in Methods that carries no form, publisher, version, citation or URL anywhere in the work.",
                     "Methods で名前は挙がるが、用紙・出版社・版・引用・URL が作品のどこにも無い"),
                ],
                "provisos": [
                    ("**The list is not exhaustive and a sub-label is not required.** Where a work's description fits none of them, the sub-label is left empty and the shape is recorded in free text. Sub-labels do not affect the main code",
                     "★リストは網羅的ではないし、サブラベルは必須でもない。どれにも当てはまらないなら空欄にして、形は自由記述に書く。サブラベルは主コードに影響しない"),
                    ("Where a description is ambiguous between two sub-labels in its own language — Ukrainian \"адаптований\" can mean translated, author-modified, or merely unnamed — leave it empty rather than picking one.",
                     "原語のうえで 2 つのサブラベルの間で曖昧なとき（ウクライナ語の адаптований は翻訳とも著者改変とも単に無名とも取れる）は、どちらかを選ばず空欄にする"),
                ],
                "ours": [],
            },
            {
                "name": "text_is_abstract",
                "question": "取得できた本文は、論文ではなく学会抄録か",
                "label": "retrieved text is an abstract (§3.6)",
                "source": "§3.6 — When the retrieved text is a conference abstract",
                "verbatim": [],
                "provisos": [
                    ("Coders set **`text_is_abstract`** with the evidence whenever the retrieved text is an abstract rather than an article: dated session headings … a word count of a few hundred, or several unrelated presentations bundled in one file.",
                     "取得した本文が論文ではなく抄録であるときに証拠付きで立てる。日付入りのセッション見出し、継続教育の文言（\"attendees will be able to…\"）、数百語しかない、無関係な発表が 1 ファイルに束ねられている、など"),
                    ("**The venue class is not changed.** Moving a record after reading it is exactly the boundary shift §10 forbids. Instead, S6 (§11) reports the main analysis with these records excluded, so the effect is measured rather than assumed.",
                     "★venue class は変えない。読んでから記録を動かすのは §10 が禁じている境界の付け替えそのもの。代わりに感度分析 S6 がこれらを除外した数字を報告するので、影響は仮定ではなく測定される"),
                    ("Related, and a coding rule in its own right: **one retrieved file can hold several works.** Code only the target work's own section. A neighbouring abstract's sentences are not evidence about this work — including for the R and C flags, where a stray mention would otherwise be counted.",
                     "★1 つの取得ファイルに複数の作品が入っていることがある。対象の作品自身の節だけをコードする。隣の抄録の文は、この作品についての証拠ではない（R フラグ・C フラグについても同じ）"),
                ],
                "ours": [],
            },
        ],
    },
    {
        "heading": "③ 全 61 作品 — 16Personalities の引用が何の役をしているか",
        "note": "フラグなので、1 つの作品が複数該当してよい。全フラグに「場所を特定した 1 文」の逐語記録が要る。",
        "items": [
            {
                "name": "r1",
                "question": "16Personalities を「実施した道具」として引用しているか",
                "label": "R1 instrument (§5)",
                "source": "§5 — the table's R1 row",
                "verbatim": [("R1", "instrument — what was administered, to humans or to agents",
                              "実施したもの。人間相手でも AI 相手でも")],
                "provisos": [], "ours": [],
            },
            {
                "name": "r2",
                "question": "16Personalities を「理論の出どころ」として引用しているか",
                "label": "R2 theory (§5)",
                "source": "§5 — the table's R2 row",
                "verbatim": [("R2", "theory — the source of the MBTI's constructs, dichotomies or type descriptions",
                              "MBTI の構成概念・二分法・タイプ説明の出どころ")],
                "provisos": [], "ours": [],
            },
            {
                "name": "r3",
                "question": "16Personalities を「統計の出どころ」として引用しているか",
                "label": "R3 norms (§5)",
                "source": "§5 — the table's R3 row",
                "verbatim": [("R3", "norms — a source of type frequencies or population statistics",
                              "タイプ頻度や母集団統計の出どころ")],
                "provisos": [], "ours": [],
            },
            {
                "name": "r4",
                "question": "16Personalities を「信頼性・妥当性の根拠」として引用しているか（数値が要る）",
                "label": "R4 psychometrics — the PLAN's secondary measure (§5)",
                "source": "§5 — the table's R4 row, and the paragraph beginning \"R4 requires…\"",
                "verbatim": [("R4", "psychometrics — evidence of reliability or validity",
                              "信頼性または妥当性の証拠")],
                "provisos": [
                    ("**R4 requires a psychometric claim sourced to the vendor** — a coefficient, a sample size, a reported reliability or validity figure **that the work takes from the vendor**. A bare adjective (\"a validated instrument\", \"a reliable test\") with no figure drawn from the vendor anywhere in the work is a claim of standing, and **§6's C3 already records it**; it does not set R4.",
                     "★R4 は「ベンダーを出典とする心理測定上の主張」を要求する —— 係数、標本サイズ、報告された信頼性・妥当性の数値で、その作品がベンダーから取ったもの。作品のどこにもベンダー由来の数値がなく、裸の形容詞（\"a validated instrument\"、\"a reliable test\"）だけなら、それは格の主張であって §6 の C3 がすでに記録している。R4 は立たない"),
                    ("The calibration record is the model: Bai 2025 sources alphas of 0.75-0.87 from an analysis of 10,000 respondents to a vendor page.",
                     "校正記録が範型: Bai 2025 はベンダーのページにある 1 万人の分析から α 0.75〜0.87 を引いている"),
                    ("This is **the narrower of the two available readings and it is chosen deliberately**, because R4 is the measure the manuscript reports and **the wider reading would inflate it on a judgement call**.",
                     "★これは可能な 2 つの読みのうち狭い方であり、意図的にそちらを選んでいる。R4 は原稿が報告する指標であり、広い読みでは判断次第で数字が膨らむから"),
                    ("**R4 is the secondary measure the PLAN names** — the vendor's own webpage cited as psychometric evidence.",
                     "R4 は PLAN が名指す副次指標 —— ベンダー自身のウェブページが心理測定上の証拠として引用されること"),
                ],
                "ours": [
                    "画面の問いは <b>2 か所を 1 行にまとめてある</b>。前半「信頼性・妥当性の根拠として"
                    "引用しているか」は<b>表の R4 行</b>の訳、後半「（数値が要る）」は<b>その下の但し書き</b>の要約。"
                    "<b>どちらも規則の原文であって、うちが作った要件ではない。</b>"
                    "まとめたのがうち、というだけ。",
                    "<b>判定は但し書きに従う＝数値が要る。</b>但し書きが「it does not set R4」と表を"
                    "明示的に絞っており、しかも「the narrower of the two available readings and it is "
                    "chosen deliberately」と、狭く取ったのが意図的であることまで書いてあるから。"
                    "数値のない「格の主張」は C3 が拾うので、取りこぼしにはならない。",
                ],
            },
            {
                "name": "r5",
                "question": "16Personalities を「データの取得元」として引用しているか",
                "label": "R5 data source (§5)",
                "source": "§5 — the table's R5 row",
                "verbatim": [("R5", "data source — where labels or profiles were scraped from or matched to",
                              "ラベルやプロフィールをどこからスクレイプしたか、どこに照合したか")],
                "provisos": [], "ours": [],
            },
            {
                "name": "r6",
                "question": "16Personalities は名前が出るだけで、主張が何も乗っていないか",
                "label": "R6 mention only (§5)",
                "source": "§5 — the table's R6 row, and the paragraphs on citing works and reference lists",
                "verbatim": [("R6", "mention only — named in passing; no claim in the work rests on it",
                              "通りすがりに名前が出るだけ。作品のどの主張もそれに依拠していない")],
                "provisos": [
                    ("**A flag attaches to the citing work's own use of the vendor.** Where a work only reports that a study *it* cites administered the vendor's test or scraped its site, the citation is **R6**: the administration belongs to the cited study, not to this one. Reviews and surveys are where this bites — a review that never touches a respondent can otherwise accumulate R1 and R5 from its own bibliography, which would put other people's practice into this work's row.",
                     "★フラグは「引用する側の作品自身のベンダーの使い方」に付く。その作品が引用している研究がベンダーのテストを実施した／サイトをスクレイプした、と報告しているだけなら、その引用は R6。実施したのは引用先の研究であってこの作品ではない。レビューや調査でここが効く —— 回答者に一度も触れないレビューが、自分の参考文献から R1 や R5 を溜め込んでしまい、他人の実践をこの作品の行に入れることになる"),
                    ("**A reference-list entry with no in-text anchor is R6.** §4.1 already treats the identical shape conservatively at the instrument step, and evidence cannot be weak enough to withhold an instrument code while strong enough to carry a substantive role.",
                     "★本文にアンカーの無い参考文献項目は R6。§4.1 が instrument の段階で同じ形を保守的に扱っている以上、「instrument コードを与えられないほど弱い証拠が、実質的な役割を担えるほど強い」ということはあり得ない"),
                ],
                "ours": [],
            },
            {
                "name": "r7",
                "question": "16Personalities 自体が研究の対象か",
                "label": "R7 object of study (§5)",
                "source": "§5 — the table's R7 row, and the paragraph beginning \"R7 exists because…\"",
                "verbatim": [("R7", "object of study — what the work analyses or measures attitudes toward — its subject, not its source",
                              "その作品が分析する対象、あるいは態度を測る対象 —— 出どころではなく主題")],
                "provisos": [
                    ("**R7 exists because R6 was doing residual duty for works about the vendor.** A discourse analysis whose corpus is the vendor's website copy, a survey measuring attitudes toward the vendor's test, an ethnography of a community that took it: in each the vendor is the entire subject while no claim of the work is *sourced* to it, so R1-R5 all fail and R6's \"no claim in the work rests on it\" reads as false. R7 records the shape. **It has no bearing on R4 and so does not touch M2.**",
                     "★R7 があるのは、ベンダーについての作品の受け皿を R6 が兼ねてしまっていたから。ベンダーのサイト文言を資料とする言説分析、ベンダーのテストへの態度を測る調査、それを受けたコミュニティの民族誌 —— どれもベンダーが主題まるごとなのに、作品のどの主張もベンダー発ではない。だから R1-R5 が全部落ち、R6 の「どの主張も依拠していない」も偽と読める。R7 がその形を記録する。★R4 には影響しないので M2 に触れない"),
                ],
                "ours": [],
            },
        ],
        "shared": [
            ("**Bundled citations are not apportioned.** Where one citation bundle at the end of a paragraph covers several claims and the vendor is one of the bundled sources, flag every role the paragraph's claims require and record the bundling in free text. Splitting a bundle between two flags by guesswork manufactures a distinction the citation does not make.",
             "★束ねられた引用は按分しない。段落末尾の 1 つの引用の束が複数の主張をカバーし、ベンダーがその 1 つなら、その段落の主張が要求する役割を全部立てて、束ねられている事実を自由記述に書く。推測で束を 2 つのフラグに割るのは、引用がしていない区別を捏造すること"),
            ("Every flag requires a located sentence or reference entry, recorded verbatim with its section.",
             "すべてのフラグに、場所の特定された 1 文または参考文献項目が要る。節名とともに逐語で記録する"),
        ],
    },
    {
        "heading": "④ 全 61 作品 — 混同しているか",
        "note": "文ごとに立てる。作品ごとではない。",
        "items": [
            {
                "name": "c1",
                "question": "16Personalities と MBTI を 1 つの道具として名指ししているか",
                "label": "C1 identity (§6)",
                "source": "§6 — the table's C1 row",
                "verbatim": [("C1", "identity — The two are named as a single instrument.",
                              "両者が 1 つの道具として名指しされている")],
                "provisos": [
                    ("**Identity is not established by anaphora.** One definite description — \"the test\" — used first for the vendor's test and then, without re-anchoring, for the MBTI does not name the two as a single instrument. The chain rule propagates a claim once identity is established; it does not establish identity.",
                     "★同一性は照応では成立しない。「the test」という 1 つの定表現が、最初はベンダーのテストを指し、次に錨を打ち直さないまま MBTI を指したとしても、それは両者を 1 つの道具として名指ししたことにならない。鎖の規則は同一性が成立した後に主張を伝播させるものであって、同一性を成立させるものではない"),
                ],
                "ours": [],
            },
            {
                "name": "c2",
                "question": "16Personalities に、業者が否定している系譜を与えているか",
                "label": "C2 provenance (§6)",
                "source": "§6 — the table's C2 row, and the paragraph beginning \"C2 requires…\"",
                "verbatim": [("C2", "provenance — The vendor's test is given a lineage the vendor itself disclaims — Jung, Myers and Briggs, or the published MBTI.",
                              "ベンダーのテストに、ベンダー自身が否定している系譜（ユング、マイヤーズとブリッグス、出版された MBTI）が与えられている")],
                "provisos": [
                    ("**C2 requires a derivation predicate.** \"Based on Jung's theory\", \"developed by Myers and Briggs\", \"derived from the MBTI\", \"a variant in the MBTI family\" — an assertion of descent. Writing \"MBTI\" out as \"Myers-Briggs Type Indicator\" is not one: on the literal reading, every C1 work that expands the acronym would also be C2 and the two flags would stop being independent.",
                     "★C2 は「由来を述べる述語」を要求する。\"Based on Jung's theory\"、\"developed by Myers and Briggs\"、\"derived from the MBTI\"、\"a variant in the MBTI family\" —— 系統の主張。★「MBTI」を「Myers-Briggs Type Indicator」と展開して書くのはこれに当たらない。字義どおりに読むと、頭字語を展開した C1 の作品はすべて C2 にもなり、2 つのフラグが独立でなくなるから"),
                    ("§7 settles it — Tshimula is expected C1 and C3 and *not* C2, while calling the vendor's test \"a popular MBTI questionnaire\".",
                     "§7 の校正記録が決着させている —— Tshimula はベンダーのテストを \"a popular MBTI questionnaire\" と呼びながら、C1 と C3 が立ち C2 は立たない、と事前に予期されている"),
                ],
                "ours": [],
            },
            {
                "name": "c3",
                "question": "16Personalities を「ちゃんとした検査だ」と書いているか",
                "label": "C3 authority (§6)",
                "source": "§6 — the table's C3 row, and the paragraph beginning \"C3 is about standing…\"",
                "verbatim": [("C3", "authority — The vendor's test is claimed to have the standing of a published instrument — official, standard, validated, professional, accurate, or the equivalent.",
                              "ベンダーのテストが、出版された検査の格を持つと主張されている —— 公式、標準、検証済み、専門的、正確、またはそれに相当するもの")],
                "provisos": [
                    ("**C3 is about standing, not uptake.** The four adjectives in the row are examples, not a closed list: \"accurate\", \"reliable\", \"scientifically validated\" make the same claim. Claims about how many people use it — \"popular\", \"widely used\", \"internationally used\", \"well known\" — are claims about uptake and do **not** set C3. That line is where the flag stops, and it is drawn on the narrower side.",
                     "★C3 は格の話であって普及の話ではない。表の 4 つの形容詞は例であって閉じたリストではない。\"accurate\"、\"reliable\"、\"scientifically validated\" も同じ主張をする。★どれだけの人が使っているかの主張 —— \"popular\"、\"widely used\"、\"internationally used\"、\"well known\" —— は普及の話であって C3 を立てない。フラグが止まるのはこの線で、狭い側に引いてある"),
                ],
                "ours": [],
            },
            {
                "name": "c0",
                "question": "混同を示す文が 1 つも無いか",
                "label": "C0 no conflation (§6)",
                "source": "§6 — the table's C0 row",
                "verbatim": [("C0", "none — No statement in the work meets C1, C2 or C3.",
                              "その作品のどの文も C1・C2・C3 に当たらない")],
                "provisos": [], "ours": [],
            },
            {
                "name": "narrow_c1",
                "question": "「同一視」を、対象を絞って測り直す — この論文が 16Personalities の名前かサイトを挙げているか",
                "label": "C1 identity under the NARROW reading — S7 only (§6, §11)",
                "source": "§6 — the paragraphs on what the flags cover and on naming the vendor",
                "verbatim": [], "provisos": [], "ours": [],
            },
            {
                "name": "narrow_c2",
                "question": "「由来」を、対象を絞って測り直す — この論文が 16Personalities の名前かサイトを挙げているか",
                "label": "C2 provenance under the NARROW reading — S7 only (§6, §11)",
                "source": "同上",
                "verbatim": [], "provisos": [], "ours": [],
            },
            {
                "name": "narrow_c3",
                "question": "「権威」を、対象を絞って測り直す — この論文が 16Personalities の名前かサイトを挙げているか",
                "label": "C3 authority under the NARROW reading — S7 only (§6, §11)",
                "source": "同上",
                "verbatim": [], "provisos": [], "ours": [],
            },
            {
                "name": "states_distinction",
                "question": "その論文は「両者は別物だ」とも書いているか",
                "label": "the work also states the distinction (§6)",
                "source": "§6 — the paragraph beginning \"Flags are set per statement…\"",
                "verbatim": [],
                "provisos": [
                    ("**Flags are set per statement, not per work.** A work that explains the vendor adds an axis the MBTI lacks, and two sentences later calls it the MBTI, sets C1. The conflating sentence is in the published record and is not undone by a correct one elsewhere. But such a work is not the same as one that never noticed the distinction, so **`states_distinction`** records that it drew it, with the verbatim, and the two are reported separately.",
                     "★フラグは文ごとに立てる。作品ごとではない。ベンダーが MBTI に無い軸を足していると説明しておきながら、2 文あとでそれを MBTI と呼ぶ作品は C1 が立つ。混同する文は公表された記録の中に在るのであって、他の箇所の正しい 1 文で取り消されはしない。ただしそういう作品は、区別に一度も気づかなかった作品とは別物なので、states_distinction が「区別を引いた」ことを逐語つきで記録し、両者は別々に報告される"),
                ],
                "ours": [],
            },
        ],
        "shared": [
            ("**What the flags are about.** Like §5, this step covers **the vendor's test, its site, and its proprietary content** — the Assertive/Turbulent axis, the Analyst/Diplomat/Sentinel/Explorer groupings, the branded type names. None of these exists in any published MBTI form, so a work that calls them \"the MBTI dimensions\" or \"the MBTI Model\" has attributed the vendor's material to the published instrument even if it never names the vendor.",
             "★フラグの対象は、§5 と同じく「ベンダーのテスト・そのサイト・その独自コンテンツ」の 3 つ。独自コンテンツとは Assertive/Turbulent 軸、Analyst/Diplomat/Sentinel/Explorer のグループ分け、ブランド型名。これらはどの出版 MBTI 用紙にも存在しないので、これらを「MBTI の次元」「MBTI モデル」と呼ぶ作品は、ベンダーを一度も名指ししていなくても、ベンダーの素材を出版された検査に帰属させたことになる"),
            ("**The three kinds of proprietary content are a closed list, and the identification must come from the text.** … In particular the vendor's aspect labels for the dichotomies the MBTI *does* have — Mind, Energy, Nature, Tactics — are a relabelling of existing content rather than content the MBTI lacks, and they are **outside** the flags. **A coder may not certify from knowledge of the vendor's site that an unattributed phrase is the vendor's**: the per-link verbatim rule cannot supply that identification and a reader cannot check it",
             "★独自コンテンツ 3 種は閉じたリストであり、同定はテキストから来なければならない。★特に、MBTI が実際に持っている二分法に対するベンダーの呼び名 —— Mind、Energy、Nature、Tactics —— は既存コンテンツの言い換えであって MBTI に無いコンテンツではないので、フラグの対象外。★ベンダーのサイトについての知識から「この帰属のないフレーズはベンダーのものだ」と認定してはいけない。リンクごとの逐語規則ではその同定を供給できず、読者に確認できないから"),
            ("**A flag may rest on more than one sentence, and each link must be quoted.** … The evidence rule is correspondingly stricter than a single-sentence rule would be: record the verbatim for **every link in the chain**, not for the conclusion.",
             "★フラグは複数の文にまたがってよく、鎖の各リンクを引用しなければならない。証拠の規則は 1 文規則より厳しくなる。結論についてではなく、鎖のすべてのリンクについて逐語を記録すること"),
            ("**A content-level identification carries only its own content.** … A work that presents the branded type names as the MBTI's, and elsewhere gives the MBTI a Jungian lineage, sets **C1 alone**: the lineage claim was never asserted of anything the work has identified with the vendor.",
             "★コンテンツレベルの同定は、そのコンテンツにしか届かない。ブランド型名を MBTI のものとして提示し、別の箇所で MBTI にユング的系譜を与える作品は C1 だけが立つ。系譜の主張は、その作品がベンダーと同定したものについては一度も述べられていないから"),
            ("**What counts as naming the vendor** — for the narrow reading and for §11's S7 — is the vendor's **test or site**, identified in running prose, in a footnote, in a reference entry, or by a bare URL. Naming is assessed **per work**: a work that names the vendor anywhere is not one of the works S7 exists to exclude.",
             "★狭い読みと S7 における「ベンダーを名指しした」の定義は、ベンダーのテストまたはサイトが、本文・脚注・参考文献項目・裸の URL のいずれかで同定されていること。★名指しは作品単位で判定する。どこかでベンダーを名指ししている作品は、S7 が除外の対象とする作品ではない"),
            ("**`third_party_conflation`** records a work that calls some *other* look-alike instrument — Humanmetrics, Truity, and their kind — \"the MBTI\". … It is recorded and described, **never rated**: the corpus is built from 16Personalities word forms, so works conflating other look-alikes enter it only by accident and no proportion computed over them would have a denominator.",
             "★third_party_conflation は、別のそっくり検査 —— Humanmetrics、Truity など —— を「MBTI」と呼んでいる作品を記録する。記録し記述するが、率は出さない。母集団は 16Personalities の語形から作られているので、他社を混同している作品は偶然入ってきただけであり、それらで割合を計算しても分母が無い"),
        ],
    },
]
