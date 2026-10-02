---
name: semantic-model-viewer
description: Semantic Model（semantic-model-builderが作るノート）を、原文と並べて、1枚で完結するアニメーション付きのHTMLページ（トランスフォームビュー）として表示する。2つの軸で動く。フォーカスアウト／インは、原文から塊へ、塊からモデルへと昇り、また降りる。トランスフォームは、モデルを構造・線形のノート・表・一言の要約に変える。どの要素も元の位置から行き先へ飛ぶので、読み手は迷わない。原文とノートはカーソルの位置で糸のようにつながる。ストーリーモードでは、原文、カットイン付きで塊を巻く、ノート、構造、つながり、一言、の順に昇る過程全体を再生する。Semantic Modelや文章のノートを見たい・探りたい・発表したい・可視化したいとき、原文とノートを並べて読みたいとき、文章が構造になる様子を見たいときに使う。「Semantic Modelを表示して」「原文とノートを並べて見せて」「構造になっていく様子を見せて」「トランスフォームビューで見せて」などで使う。
---

# Semantic Model Viewer

> 英語版 [SKILL.md](SKILL.md) と同じ内容の日本語版。

1枚のページで1つのモデルを見せる。動きは2つある。

- **フォーカスアウト／イン：** 原文（L0）から、塊に巻いた原文（L1）へ、さらにモデル（L2）へと昇り、また降りる。昇ると抽象度が上がり、降りると言葉に戻る。L2では原文とノートが左右に並び、カーソル位置が連動する。これがTwo Paneである。
- **トランスフォーム：** L2で、同じノートを構造・線形のノート・表・一言に変える。

変化はすべてアニメーションで見せ、読み手が自分の位置を見失わないようにする。見出しの札がカードに育ち、カードは要約の中の自分の語句へ飛び込み、要点は表のセルへ移る。逆向きも同じように動く。▶ は、昇る過程全体をストーリーとして再生する（Formation）。原文、カットインとともに巻かれていく各塊、ノート、構造、結論から外側へ広がるつながり、一言、の順に進む。

ページは固定のテンプレート [`assets/viewer.html`](assets/viewer.html) である。契約（[`references/semantic-model.md`](references/semantic-model.md)）に従うモデルなら何でも表示でき、ネットワークは要らない。原文から意味を取り出すことはせず、表示するものはすべてモデルから来る。

## 入力

- Semantic Modelのファイル（`semantic-model/1`）。原文しか無いときは、先に [`semantic-model-builder`](../semantic-model-builder/SKILL.ja.md) でノートを作る。ここで構造を考え出さない。
- ユーザーが望むなら、層・表現・ストーリーを再生するかどうか。

## 手順

ツールは、このスキルのフォルダにある `scripts/build_viewer.py`（Python 3、標準ライブラリのみ）。

1. **ページの開き方を決める。** これは見せ方の選択であり、モデルは変えない。
   - 読んで探るなら、モデル層で線形のノートを開く（既定）。
   - 発表するとき、または文章が構造になる様子を見せたいときは `--play`。物語や手順のように、原文に出てくる順番に意味があるなら `--order reading`。
   - 特定の状態から開くなら `--stop`、`--rep`、`--focus <node-id>`。
2. **ビルドする。**
   `python3 scripts/build_viewer.py model.json -o view.html [--play] [--stop text|chunks|model] [--rep structure|linear|table|summary] [--order notes|reading] [--focus ID] [--theme dark|light|auto]`
   builderと同じ検査器でモデルを検証し、エラーがある間は何も書き出さない。保存先はユーザーの指定があればそこ、無ければモデルと同じ場所の `.semantic/<YYYYMMDD>-<slug>/view.html`。コミットはユーザーに求められたときだけ行う。
3. **ブラウザで確認する**（NodeとPlaywrightが使える場合）。
   `NODE_PATH="$(npm root -g)" node scripts/check_viewer.cjs view.html`
   次を確かめる。
   - エラーなく開く。
   - 言葉にカーソルを重ねるとモデルに焦点が移る。
   - 固定すると詳細カードが開き、Escで解除される。
   - すべての層と表現が描ける。
   - ストーリーが両方の順序で最後まで進む。
   - スマホ幅ではみ出さない。

   そのうえで自分の目でも見る。見出しを順に読んで話になっているか。要約がきちんと着地しているか。
4. **渡す。** パスと使い方を伝える。
   - カーソルを重ねると原文とノートがつながる。クリックで固定、Escで解除。
   - 「フォーカス」と「表現」のボタンで切り替える（↑↓、1〜4）。
   - ▶／Spaceでストーリーを再生し、←→で1コマずつ進める。

   ユーザーがローカルのファイルを開けない環境（リモート実行など）では、Artifactとして公開する。公開前に `artifact-design` スキルを読み込む。

## ビューオプション

フラグで渡すか、JSONファイルにして `--view` で渡す。ページ内のモデルとは別のブロックに入り、モデルには入らない。

```json
{ "stop": "model", "rep": "linear", "play": false, "order": "notes", "focus": "node-id", "theme": "dark", "follow": true, "lang": "ja" }
```

## しないこと

- **見た目のためにモデルを直さない。** ノートが分かりにくいなら、builderでノートを直す。見せ方だけの問題なら、ビューオプションを変える。
- **ページに原文の解析を足さない。** ページが表示するものはすべてモデルから来る。
- **原文ごとにページを書き起こさない。** テンプレートが実装である。テンプレートを改良したときは、[`references/transform-view.md`](references/transform-view.md) もテンプレートに合わせる。

## 参照

- [references/semantic-model.md](references/semantic-model.md)：入力の契約（builderと共通）。英語。
- [references/transform-view.md](references/transform-view.md)：層、表現、ストーリー、動きの規則、背景の構図、原文 ↔ モデルの対応、操作。英語。
- [assets/viewer.html](assets/viewer.html)：テンプレート。そのまま開くと短い作例（駅前商店街を3つの塊にしたもの）を表示する。
