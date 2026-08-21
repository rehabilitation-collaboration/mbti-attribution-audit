"""How each item is asked on the ruling sheet, in words the author can use.

The first wording of these questions was a translation of the protocol's own
headings — "16Personalities に、業者が否定している系譜を与えているか" for `c2` —
and the author could not tell from it what he was being asked. The protocol is
written for a coder who has just read §6; the sheet is read by the person who
has to decide, once per item, and who has not read it.

So each item carries two strings. `ASKED` is the question, written so that it can
be answered without the section in front of you. `WATCH` is the boundary the
protocol draws around it — the case that looks like a yes and is not, and why the
flag exists at all — because the ruling turns on that more often than on the
question.

`ASKED` is escaped into an `<h3>`, so it must be plain text: a `<b>` written here
reaches the page as four visible characters. `WATCH` is written in as-is and may
carry `<b>` and `<br>`.

Both are ours. `LABELS` keeps the protocol's own name beside each so a ruling can
still be checked against §2, §3, §5 and §6, and `coding_raw/rules.html` prints
those sections verbatim.
"""

from __future__ import annotations

# Plain text only — this goes through html.escape.
ASKED = {
    "e": "この論文に出てくる性格タイプは、どこから来たものか。"
         "著者が自分で誰かに検査を受けさせたのか、よそから持ってきたのか、"
         "そもそも誰のタイプも載っていないのか",

    "instrument": "回答者が実際に受けたのは、どのテストか。"
                  "16Personalities（無料サイト）か、本物の MBTI（有料の検査用紙）か、"
                  "それとも論文を読んでも分からないか",

    "instrument_sublabel": "「どのテストか分からない」と判定した論文について、"
                           "その分からなさが下のどの形に当てはまるか。"
                           "当てはまるものが無ければ空欄のままでよい",

    "text_is_abstract": "手に入った文章は、論文まるごとか。"
                        "それとも学会発表の要旨（数百語しかない短いもの）だけか",

    "r1": "この論文は「16Personalities を使って測りました」と書いているか。"
          "測った相手は人間でも AI でもよい",

    "r2": "この論文は、MBTI がどういう考え方のものかを説明するときに、"
          "16Personalities を情報源にしているか。"
          "たとえば「性格は 4 つの軸で決まる」「INTJ とはこういう人だ」と書くのに、"
          "16Personalities のページを引いている場合",

    "r3": "この論文は「INTJ は全体の 2% しかいない」のような割合や人数を、"
          "16Personalities から持ってきているか",

    "r4": "この論文は「このテストは信用できる」と言うために、"
          "16Personalities が公表している数値を根拠にしているか。"
          "数値というのは、信頼性係数のような具体的な数字のこと",

    "r5": "この論文が分析したデータそのもの（誰が何型か、という一覧やプロフィール）は、"
          "16Personalities から取ってきたものか",

    "r6": "16Personalities は名前が出てくるだけか。"
          "つまり、この論文から 16Personalities の話を全部消しても、"
          "論文の中身は何も変わらないか",

    "r7": "この論文が調べている相手そのものが 16Personalities か。"
          "「16Personalities を道具に使って人を調べた」のではなく、"
          "「16Personalities というサイトやテスト自体を調べた」場合",

    "c0": "16Personalities と MBTI を混同している文が、この論文に一つも無いか",

    "c1": "この論文は、16Personalities と MBTI を「同じ一つのテスト」として書いているか",

    "c2": "16Personalities は自分で「うちのテストは MBTI ではありません」と言っている。"
          "それなのにこの論文は、16Personalities のことを"
          "「ユングの理論から作られた」「マイヤーズとブリッグスが開発した」「MBTI から派生した」"
          "のように、MBTI の血筋を引いているかのように書いているか",

    "c3": "この論文は 16Personalities を「公式の」「標準の」「検証済みの」「正確な」「信頼できる」"
          "のように、ちゃんとした検査として扱っているか",

    "narrow_c1": "これは新しい質問ではない。"
                 "すぐ上の「同じ一つのテストとして書いているか」で決めた答えを、"
                 "そのままここにも書き写すだけ。"
                 "例外は一つで、その論文が 16Personalities という名前を一度も出していない場合、"
                 "ここは False になる",

    "narrow_c2": "これは新しい質問ではない。"
                 "すぐ上の「MBTI の血筋を引いているように書いているか」で決めた答えを、"
                 "そのままここにも書き写すだけ。"
                 "例外は一つで、その論文が 16Personalities という名前を一度も出していない場合、"
                 "ここは False になる",

    "narrow_c3": "これは新しい質問ではない。"
                 "すぐ上の「ちゃんとした検査として扱っているか」で決めた答えを、"
                 "そのままここにも書き写すだけ。"
                 "例外は一つで、その論文が 16Personalities という名前を一度も出していない場合、"
                 "ここは False になる",

    "states_distinction": "この論文は「16Personalities と MBTI は別のものです」とも書いているか",
}

# May carry <b> and <br> — written into the page as-is.
WATCH = {
    "e": "★見るのは「タイプそのものを持っているか」。"
         "他の研究が出した「INTJ が何％」という結果を引用して論じているだけの論文は、"
         "タイプのデータ自体は持っていないので <b>E4</b>。<br>"
         "★いくつも当てはまる論文は <b>E1 &gt; E3 &gt; E2 &gt; E4</b> の順で 1 つに決める。"
         "この順番は先に決めてあり、論文ごとに決め直さない（§2）",

    "instrument": "★決め手は<b>「著者が何を読んだか」ではなく「回答者が何を受けたか」</b>。"
                  "MBTI の教科書を引用していても、それだけでは「本物の MBTI を受けさせた」ことにならない。"
                  "本文に何も書かず、参考文献に 16Personalities の URL があるだけなら"
                  "「分からない」扱いにする（§3・§4.1）",

    "instrument_sublabel": "★<b>当てはまるものが無ければ空欄でよい。</b>無理に選ばない。"
                           "原語で 2 つの意味に取れる言葉（ウクライナ語の адаптований は"
                           "「翻訳した」とも「作り変えた」とも読める）も、空欄のまま（§3.4）",

    "r1": "★見るのは<b>「使ったのがこの論文自身か」</b>。"
          "「別の研究が 16Personalities を使った」と紹介しているだけなら、"
          "これは R1 ではなく <b>R6</b>（§5）",

    "r4": "★<b>16Personalities が出した数値が要る。</b>"
          "「検証済みの検査です」「信頼できます」と書いてあるだけで数字が一つも無いなら、"
          "それは R4 ではなく <b>C3</b> の方で記録する（§5）",

    "r6": "★これは <b>R1〜R5 と R7 が全部ハズレのときの箱</b>。"
          "ただの紹介、他の検査と並べて名前を挙げただけ、"
          "参考文献に載っているが本文から一度も参照していない —— こういうのが R6。<br>"
          "★<b>「別の研究が 16Personalities を使った」と紹介しているだけなら R6。</b>"
          "使ったのはその別の研究であって、この論文ではないから。"
          "ここを間違えると、誰にも検査していないレビュー論文が、"
          "自分の参考文献から「実施した」「データを取った」を吸い上げてしまい、"
          "<b>他人がやったことがこの論文の記録に混ざる</b>（§5）",

    "r7": "★<b>道具として使ったのか、調べる相手だったのか。</b>"
          "16Personalities のサイトの文章を分析した研究、16Personalities への意識調査、"
          "それを受けた人たちを追いかけた研究 —— こういうのが R7（§5）",

    "c0": "★C1・C2・C3 のどれも立たないときだけ立てる（§6）",

    "c1": "★<b>「the test」のような言葉が、順番に両方を指しただけでは足りない。</b>"
          "たとえば「the test を受けてもらった（＝16Personalities のこと）」と書いた数行あとに"
          "「the test は 1962 年に作られた（＝MBTI のこと）」と書いてあっても、"
          "この論文が両者を同じ一つのものだと言ったことにはならない。"
          "はっきり同じものとして名指しする必要がある（§6）",

    "c2": "★<b>「〜から作られた」と述べる言葉が要る。</b>"
          "「MBTI」を「Myers-Briggs Type Indicator」と正式名称に書き直しただけでは、"
          "血筋を主張したことにならない。"
          "そこまで認めると、正式名称を書いた論文がすべてこの項目に該当してしまい、"
          "「同じ一つのテスト扱い」との区別がつかなくなるから（§6）",

    "c3": "★<b>品質の話か、人気の話か</b>で分かれる。"
          "「公式」「標準」「検証済み」「正確」「信頼できる」は品質の話＝<b>該当する</b>。"
          "「人気がある」「広く使われている」「よく知られている」は人気の話＝<b>該当しない</b>。"
          "実際 16Personalities は世界一使われている性格診断サイトなので、"
          "「広く使われている」と書いても嘘ではない。"
          "嘘ではないことを混同として数えない、という線引き（§6）",

    "narrow_c1": "",  # replaced below
    "narrow_c2": "",
    "narrow_c3": "",

    "states_distinction": "★<b>混同していても、これが立つことはある。</b>"
                          "「混同に気づかなかった論文」と「気づいた上で混同した論文」は"
                          "同じではないので、分けて数えるための項目（§6）",
}

_NARROW = (
    "★<b>これが何のためにあるか。</b>"
    "この研究は「MBTI と名乗る論文のうち、16Personalities と混同しているものが何％か」を出す。"
    "ところが混同の判定は、論文が 16Personalities という名前を一度も出していなくても成立する。"
    "たとえば「Assertive / Turbulent」という軸は 16Personalities にしか無いのに、"
    "それを「MBTI の軸」と書いている論文がある。名前は出ていないが、中身は混ざっている。<br>"
    "そういう論文まで数えると率は高く出る。<b>それは自分に都合のいい数え方かもしれない。</b>"
    "だから「16Personalities という名前をちゃんと出している論文だけ」に絞った、"
    "厳しい方の数字も一緒に報告する（§11 の感度分析 S7）。この項目はその厳しい方の記録。<br>"
    "★<b>だから独立に悩む項目ではない。</b>"
    "名前を出している論文なら ↑ と同じ値、出していない論文だけ False。"
    "<b>この作品は名前を出している</b>（出していなければこの注意そのものが表示されない）ので、"
    "↑ と同じ値をそのまま入れればよい"
)
WATCH["narrow_c1"] = _NARROW
WATCH["narrow_c2"] = _NARROW
WATCH["narrow_c3"] = _NARROW

VALUE_JA = {
    "True": "はい",
    "False": "いいえ",
    "E1": "この研究で受けさせた",
    "E2": "既存データ・他の研究から",
    "E3": "相手は AI",
    "E4": "誰のタイプも載っていない",
    "a": "16Personalities を実施",
    "b": "本物の MBTI を実施",
    "c": "何を実施したか特定できない",
    "c-unnamed": "「MBTI を実施」とだけ書いてある",
    "c-online": "名前のない無料/オンラインの MBTI テスト",
    "c-authormade": "著者が自作した項目",
    "c-vendor-cited-only": "本文に記載なし・参考文献に業者 URL だけ",
    "c-translated": "翻訳版・ライセンスも出典も無い",
    "c-named-unsourced": "名前は挙がるが用紙・出版社・版・URL がどこにも無い",
}
