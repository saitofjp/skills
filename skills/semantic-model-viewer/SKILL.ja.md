---
name: semantic-model-viewer
description: Semantic Model（semantic-model-builderの出力）を、1枚で完結するインタラクティブなHTMLとして表示する。同じモデルを2つの見方で見せる。Two Paneは原文とモデルを左右に並べて双方向に同期させ、意味的距離に応じて強調し、推論を原文の根拠までたどれる。Formationはモデルが形成されていく過程を、中心から、または読む順に、各要素が原文の言葉から立ち上がる形で見せる。粒度の切り替えで概観と詳細を行き来できる。Semantic Modelや文章の構造を見たい・探りたい・可視化したい・発表したいとき、原文と構造を並べて読みたいとき、構造が形成される様子を見たいときに使う。「Semantic Modelを表示して」「原文とモデルを並べて見せて」「意味構造の形成過程を見せて」「Two Pane / Formationで見せて」などで使う。
---

# Semantic Model Viewer

> 英語版 [SKILL.md](SKILL.md) と同じ内容の日本語版。

1枚のページで、1つのSemantic Modelを2つの見方で見せる。

- **Two Pane：** 原文と構造を同時に見る。言葉にカーソルを重ねると構造の中の位置が、ノードに重ねるとその言葉が分かる。強調は現在の焦点からの意味的距離に応じて薄くなり、推論は原文の根拠までたどれる。
- **Formation：** 構造ができていく様子を見る。焦点から外へ（焦点 → 直接の関係 → 関係するノード → 二次の関係 → 全体構造）、または読む順に育つ。各ノードは、それが来た原文の言葉から立ち上がる。

2つの見方は同じ埋め込みモデルを読み、各ノードを同じ位置に置く。切り替えても読み手の頭の中の地図が崩れない。

ページは固定のテンプレート [`assets/viewer.html`](assets/viewer.html) である。契約（[`references/semantic-model.md`](references/semantic-model.md)）に従うモデルなら何でも表示でき、ネットワークは要らない。ページは原文から意味を取り出さない。構造の出どころはモデルだけである。

## 入力

- Semantic Modelのファイル（`semantic-model/1`）。原文しか無いときは、先に [`semantic-model-builder`](../semantic-model-builder/SKILL.ja.md) でモデルを作る。ここで構造を考え出さない。
- ユーザーが望むなら、見方・粒度・出発点。

## 手順

ツールはこのスキルのフォルダにある `scripts/build_viewer.py`（Python 3、標準ライブラリのみ）。

1. **ページの開き方を決める。** これらは見せ方の選択である。モデルから決め、モデルは変えない。
   - **見方：** 読んで探るなら `two-pane`。発表などで構造ができる様子を見せるなら `formation`。
   - **形成の順序：** 論証や説明のように中心があるなら `focus`。物語や手順のように、出てくる順番に意味があるなら `reading`。
   - **焦点ノード：** その文章が何についてのものかを表すノード。既定では、モデルの結論（`role: "conclusion"`）から始めるので、論証が組み立てられる順に構造ができる。結論が無いときは、ほかが支えている主張や、説明の対象を選ぶ。どちらも無ければ最もつながりの多いノードを使うが、それが意味の中心とは限らない。
   - **粒度：** `parent` を使うモデルは概観（level `0`）で開く。読み手はそこから詳細を開く。
   - **独自の順序（任意）：** どちらの順序でもうまく伝わらないときは、手順を自分で書く（ビューオプション参照）。
2. **ビルドする。**
   `python3 scripts/build_viewer.py model.json -o view.html --focus <node-id> [--mode formation] [--strategy reading] [--level 0]`
   builderと同じ検査器でモデルを検証し、エラーがある間は何も書き出さない。保存先はユーザー指定があればそこ、無ければモデルと同じ場所の `.semantic/<YYYYMMDD>-<slug>/view.html`。コミットはユーザーに求められたときだけ行う。
3. **ブラウザで確認する**（NodeとPlaywrightが使える場合）。
   `NODE_PATH="$(npm root -g)" node scripts/check_viewer.cjs view.html`
   コンソールエラーなく開くこと、言葉にカーソルを重ねるとグラフに焦点が移ること、クリックで固定されて詳細カードが開きEscで解除されること、Formationが両方の順序で最後まで進むことを確かめる。そのうえで自分の目でも見る。概観で話の筋が分かるか、結論が結論として読めるか。
4. **渡す。** パスと使い方を伝える。カーソルを重ねる、クリックで固定、Escで解除、粒度ボタン、「本文に追従」、Formationでは Space / ← → / Home / End。ユーザーがローカルのファイルを開けない環境（リモート実行など）では、Artifactとして公開する。公開前に `artifact-design` スキルを読み込む。

## ビューオプション

フラグで渡すか、JSONファイルにして `--view` で渡す。ページ内のモデルとは別のブロックに入り、モデルには入らない。

```json
{
  "mode": "two-pane",
  "level": 0,
  "follow": true,
  "lang": "ja",
  "formation": {
    "strategy": "focus",
    "focus": "node-id",
    "steps": [{ "add": ["node-or-relation-id"], "caption": "…", "phase": "focus" }]
  }
}
```

`steps` は `strategy` が `"custom"` のときに使う。`lang` の既定は `metadata.language`、無ければ原文の文字種から決める。

## しないこと

- **見た目のためにモデルを直さない。** 表示が誤解を招くなら、builderでモデルを直す。見せ方だけの問題ならビューオプションを変える。
- **ページに原文の解析を足さない。** ページが表示するものはすべてモデルから来る。
- **原文ごとにページを書き起こさない。** テンプレートが実装である。改良したときは [`references/two-pane.md`](references/two-pane.md) と [`references/formation.md`](references/formation.md) をテンプレートに合わせる。

## 参照

- [references/semantic-model.md](references/semantic-model.md)：入力の契約（builderと共通）。英語。
- [references/two-pane.md](references/two-pane.md)：UI、操作、強調、原文 ↔ モデルの対応。英語。
- [references/formation.md](references/formation.md)：形成の順序、アニメーションの規則、焦点と展開、操作。英語。
- [assets/viewer.html](assets/viewer.html)：テンプレート。そのまま開くと最小例「AはBを使ってCした。DはCに影響した。」を表示する。
