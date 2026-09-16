# 根拠となる文献

SKILL.md の判定のうち、**文献に当たらないと変えられないもの**だけを載せる。載っている文献を消すと、対応する判定が根拠を失う。

## 枠組み

| 文献 | SKILL.md のどこ | 何が取れるか |
|---|---|---|
| [ISO 24495-1:2023 Plain language — Part 1: Governing principles and guidelines](https://www.iso.org/standard/78907.html)（[4原則の公開版](https://www.iplfederation.org/iso-standard/)） | 冒頭の4原則、ステップ1（宣言） | relevant / findable / understandable / usable。25カ国・19言語の合意で作られた国際規格。「読み手が必要なものを得る」が第1原則 |

## ステップ2・3（意味単位と核判定）

| 文献 | 対応する箇所 | 何が取れるか |
|---|---|---|
| Mann & Thompson, Rhetorical Structure Theory（[Taboada & Mann のレビュー](https://www.sfu.ca/~mtaboada/docs/Taboada_Mann_RST_Part1.pdf)） | ステップ3の削除テスト、「判断の再現性を測る」 | 核(nucleus)と衛星(satellite)。**重要度は削除テストで操作的に定義される**：核を削るとテキストが非一貫になるが、衛星を削ってもならない（Carlson & Marcu が削除テスト＋置換テストを手順化）。同時にRST自身が「すべての判定は plausibility judgement であり複数の注釈がありうる」と認めている。**完全な客観化は文献側でも達成されていない。だから一致率を測る** |
| Horn, Information Mapping（[解説](https://ivacheung.com/2012/11/introduction-to-information-mapping/)、[Structured writing](https://en.wikipedia.org/wiki/Structured_writing)） | ステップ2の情報型6つ | procedure / process / principle / concept / structure / fact。ビジネス・技術文書の内容をほぼ覆う既成の分類。**自作の分類を使わないためにこれを借りている** |
| [Carroll, The Minimal Manual (1987)](http://swcarpentry.github.io/swc-releases/2017.02/instructor-training/files/papers/carroll-minimal-manual-1987.pdf) / [ミニマリズムのメタ分析](https://files.eric.ed.gov/fulltext/ED491708.pdf) | ステップ6の落とす候補 | 学習時間 16.4h → 10h（40%減）、完了サブタスク 2.7倍。**同時にCarrollは「エラー認識と回復の記述は残す」と明示** — 落とす候補から制約・禁止・復旧手順を外す理由 |

## ステップ6・7（QAテスト）

| 文献 | 対応する箇所 | 何が取れるか |
|---|---|---|
| [FEQA (Durmus et al., ACL 2020)](https://arxiv.org/abs/2005.03754)、QAGS、QuestEval | ステップ6・7 | 要約の忠実性をQAで測る枠組み。元文書からQAを作り、要約だけで答えられるかを見る。**skillのQAテストはこれを圧縮タスクに転用したもの。** 限界も同じで、指標は質問生成モデルと回答モデルの両方に依存する — **質問が甘いとテストは素通りする。** 質問を宣言の「行動」から機械的に作り、思いつきで作らない理由 |
| [An Empirical Study of LLM-as-a-Judge (2025)](https://arxiv.org/pdf/2506.13639) | 「判断の再現性を測る」の一致率0.6 | 客観的な基準では κ≈0.57–0.63、主観的な基準では κ<0.35 に落ちる。**κ<0.4 は「基準が曖昧」のサイン。** 一致率が低いとき文書ではなく基準を疑う根拠 |

## ステップ10（機械検査）の閾値

| 文献 | 対応する行 | 何が取れるか |
|---|---|---|
| [textlint-rule-preset-ja-technical-writing](https://github.com/textlint-ja/textlint-rule-preset-ja-technical-writing) | ステップ10の表ほぼ全部 | 1文100字 / 読点3つ / 連続漢字6字 / 二重否定禁止 / 同一助詞の連続禁止 / 弱い表現・冗長表現の語リスト。**閾値の出どころはここ。実行できるならskillで数えるより実行するほうが速く正確** |
| [Gibson, Reading-Time Evidence for Long-Distance Dependencies (Syntax, 2004)](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1368-0005.2004.00065.x) | 修飾語と被修飾語の距離 | Dependency Locality Theory。係り受け距離が伸びるほど統合コストが上がる。自己ペース読み・視線計測・ERPで確認。textlintに対応ルールが無く、この行だけ出どころが別。**40字という具体値は文献に無い運用値** |
| [Verifying Negative Sentences (Clark & Chase の追試, 2021)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8660742/) / [Do two negatives make a positive? (2023)](https://www.tandfonline.com/doi/full/10.1080/23273798.2023.2190134) | 否定辞の数、二重否定 | 否定文は肯定文より反応時間・誤答率が高い。二重否定は肯定に還元されず、追加コストが残る |

## この文書の使い方

skillの判定を変えたくなったら、次の順で確認する。

1. その判定はステップ10（機械検査）か。なら閾値を変えるだけ。文献に当たる必要はない
2. ステップ2・3（意味単位と核判定）か。なら削除テストの手続きを変えることになる。RSTの原典を読んでから変える
3. ステップ7〜10（検証）か。なら検証が弱くなる方向の変更でないか確かめる。**QAテストを外す変更はしない**
4. ステップ1（宣言）か。宣言の項目を増やす変更は、主観の集約点を増やすことになる。4項目より増やさない
