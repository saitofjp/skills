# 根拠となる文献

SKILL.md の各判定の出どころ。**判定基準を変えるときは、対応する文献に当たってから変える。**

## 全体の枠組み

| 文献 | SKILL.md のどこ | 何が取れるか |
|---|---|---|
| [ISO 24495-1:2023 Plain language — Part 1: Governing principles and guidelines](https://www.iso.org/standard/78907.html)（[4原則の公開版](https://www.iplfederation.org/iso-standard/)） | 冒頭の4原則、層0 | relevant / findable / understandable / usable。25カ国・19言語の合意で作られた国際規格。「読み手が必要なものを得る」が第1原則 |
| [文化審議会建議「公用文作成の考え方」(令和4年)](https://www.bunka.go.jp/seisaku/bunkashingikai/kokugo/hokoku/pdf/93651301_01.pdf) | 層1の閾値 | 日本語文書の公的な規範。**未確認** — PDFからテキストを抽出できていない。層1の閾値を見直す際は、この原典に当たること |
| [Kimble, *Writing for Dollars, Writing to Please* (2nd ed., 2023)](https://www.nngroup.com/articles/cloze-test-reading-comprehension/) | 全体 | プレーンランゲージの効果を時間・エラー率・コストで実測した事例集 |

## 層1（機械判定）の閾値

| 文献 | 対応する行 | 何が取れるか |
|---|---|---|
| [textlint-rule-preset-ja-technical-writing](https://github.com/textlint-ja/textlint-rule-preset-ja-technical-writing) | 層1の表ほぼ全部 | 1文100字 / 読点3つ / 連続漢字6字 / 二重否定禁止 / 同一助詞の連続禁止 / 弱い表現・冗長表現の語リスト。**閾値の出どころはここ。実行できるならskillで数えるより実行するほうが速く正確** |
| [Gibson, Reading-Time Evidence for Long-Distance Dependencies (Syntax, 2004)](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1368-0005.2004.00065.x) | 修飾語と被修飾語の距離 | Dependency Locality Theory。係り受け距離が伸びるほど統合コストが上がる。自己ペース読み・視線計測・ERPで確認。**40字という具体値は文献に無い運用値** |
| [Verifying Negative Sentences (Clark & Chase の追試, 2021)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8660742/) | 否定辞の数 | 否定文は肯定文より反応時間・誤答率が高い |
| [Do two negatives make a positive? (2023)](https://www.tandfonline.com/doi/full/10.1080/23273798.2023.2190134) | 二重否定 | 二重否定は肯定に還元されず、追加コストが残る |
| [jReadability](https://jreadability.net/) / [リーダビリティ測定ツール（長岡技科大）](http://readability.nagaokaut.ac.jp/readability) | （未使用） | 日本語文章の難易度を6段階判定。李・長谷部・柴崎の公式（BCCWJ+読売新聞1,949サンプル）。圧縮前後の補助指標として使える |

## 層2（構造と核判定）

| 文献 | 対応する箇所 | 何が取れるか |
|---|---|---|
| Mann & Thompson, Rhetorical Structure Theory（[Taboada & Mann のレビュー](https://www.sfu.ca/~mtaboada/docs/Taboada_Mann_RST_Part1.pdf)） | ステップ4の削除テスト | 核(nucleus)と衛星(satellite)。**重要度は削除テストで操作的に定義される**：核を削るとテキストが非一貫になるが、衛星を削ってもならない。Carlson & Marcu が削除テスト＋置換テストを手順化 |
| 同上 | ステップ8の一致率 | **RST自身が「すべての判定は plausibility judgement であり複数の注釈がありうる」と認めている。** 完全な客観化は文献側でも達成されていない。だから一致率を測る |
| Horn, Information Mapping（[解説](https://ivacheung.com/2012/11/introduction-to-information-mapping/)、[Structured writing](https://en.wikipedia.org/wiki/Structured_writing)） | ステップ3の情報型6つ | procedure / process / principle / concept / structure / fact。ビジネス・技術文書の内容をほぼ覆う既成の分類。**自作の分類を使わないためにこれを借りている** |
| [Carroll, The Minimal Manual (1987)](http://swcarpentry.github.io/swc-releases/2017.02/instructor-training/files/papers/carroll-minimal-manual-1987.pdf) / [ミニマリズムのメタ分析](https://files.eric.ed.gov/fulltext/ED491708.pdf) | 「削ると良くなる」の根拠 | 学習時間 16.4h → 10h（40%減）、完了サブタスク 2.7倍。**同時にCarrollは「エラー認識と回復の記述は残す」と明示** — 落とす候補から制約・禁止・復旧手順を外す理由 |
| [Mayer, Coherence Principle](https://resolve.cambridge.org/core/services/aop-cambridge-core/content/view/4C1367F7716D91DE196CA8D319DF5FAD/9781139164603c7_p113-133_CBO.pdf/coherence_principle.pdf) / [Cromley & Chen のメタ分析 (2025)](https://www.sciencedirect.com/science/article/pii/S1747938X25000673) | 同上 | 余計な素材を除くと学習が深まる（23/23の実験で支持、効果量中央値0.86）。ただし2025年の包括的メタ分析では全体 g=0.37 と控えめ。**効果はあるが誇張しない** |

## 層3（検証）

| 文献 | 対応する箇所 | 何が取れるか |
|---|---|---|
| [FEQA (Durmus et al., ACL 2020)](https://arxiv.org/abs/2005.03754)、QAGS、QuestEval | ステップ6・8のQAテスト | 要約の忠実性をQAで測る枠組み。元文書からQAを作り、要約だけで答えられるかを見る。**skillのQAテストはこれを圧縮タスクに転用したもの** |
| 同上（限界） | ステップ8 | これらの指標は質問生成モデルと回答モデルの両方に依存する。**質問が甘いとテストは素通りする。** 質問は宣言の「行動」から機械的に作り、思いつきで作らない |
| [Cloze Test for Reading Comprehension (NN/g)](https://www.nngroup.com/articles/cloze-test-reading-comprehension/) / [HyTeC-cloze (Kleijn et al., 2019)](https://journals.sagepub.com/doi/10.1177/0265532219840382) | （未使用） | 人間の読み手で検証する場合の標準手法。1950年代から使われる。QAテストより強いが、人手が要る |
| [An Empirical Study of LLM-as-a-Judge (2025)](https://arxiv.org/pdf/2506.13639) | ステップ8の一致率0.6 | 客観的な基準では κ≈0.57–0.63、主観的な基準では κ<0.35 に落ちる。**κ<0.4 は「基準が曖昧」のサイン。** 一致率が低いとき文書ではなく基準を疑う根拠 |

## この文書の使い方

skillの判定を変えたくなったら、次の順で確認する。

1. その判定は層1か。なら閾値を変えるだけ。文献に当たる必要はない
2. 層2か。なら削除テストの手続きを変えることになる。RSTの原典を読んでから変える
3. 層3か。なら検証が弱くなる方向の変更でないか確かめる。**QAテストを外す変更はしない**
4. 層0か。宣言の項目を増やす変更は、主観の集約点を増やすことになる。4項目より増やさない
