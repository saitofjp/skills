# 岸本 まりえ（Kishimoto Marie）

> Persona Contract v1 / **合成ペルソナ（実ユーザー調査に基づかない仮説）**

## Snapshot
- **Role / context:** 会社員。同僚が共有した結果URL（`/r/:publicId`）を**スマートフォンのブラウザ**（縦持ち・片手・移動中）で開くところから始まる、招待流入のユーザー。
- **Primary goal:** 「送られてきたこれは何なのか」を知りたいだけ。自分がテストを受ける意思は最初は無い。
- **Current workaround:** 生成AIは検索の代わりに月数回使う程度。信用しきってはおらず、重要なことは自分で検索し直す。
- **Relevant experience:** スマホのWeb操作は日常的。PCでの長い入力作業は避ける。
- **Why this product might matter:** 同僚の点数への興味と、「自分ならどうか」という軽い競争心。ただし**支払い・登録の手前で止まる**。

## Evidence Basis
- **Provided facts:** 共有ルート `/r/:publicId` は `is_public=true` の間だけ第三者が閲覧でき、モバイルでは問題概要カードが先頭に出る。プレイは未ログイン・匿名で開始できる。匿名アカウントは初期付与100クレジットのみで**日次回復の対象外**。チャット入力欄はペースト・D&Dを無効化。モバイルは問題/メモをボトムシートで見る。
- **High-impact assumptions:**
  - [ASSUMPTION-VALIDATE] 招待流入の未知ユーザーは、最初の1〜2画面（体感90秒）で価値が分からなければ離脱する。
  - [ASSUMPTION-VALIDATE] メールアドレス入力を求められた時点で、多くの初回接触者は続けない。
  - [ASSUMPTION-VALIDATE] 「AIが自分を採点する」という構図そのものに軽い抵抗を持つ層が一定数いる。
- **Important unknowns:**
  - [UNKNOWN-NEEDS-RESEARCH] 共有された結果画面から実際に自分でプレイへ進む率。
  - [UNKNOWN-NEEDS-RESEARCH] 「スコアが公開・比較される」ことへの心理的抵抗の強さ。

## Background
新しいサービスを試すこと自体は嫌いではないが、**アカウントを作る前に全部確かめたい**タイプ。移動中や休憩中の細切れ時間に触るため、5分以上の連続作業は最初から想定していない。文章を書く行為（自由記述）はスマホでは負担が大きく、選択式なら応じるが記述式では手が止まる。

## Goals & Motivation
- まず「これは何か」を理解する。次に「自分は何点か」に興味が動く（動かないこともある）。
- 個人情報を出さずに試せる範囲で試したい。
- 途中でやめても失うものがない状態を望む。

## Pains & Current Workarounds
- AI関連サービスは説明が抽象的で、何をされるのか分からないまま登録を求められることが多い。
- スマホで長文入力を要求されると、その場で中断する（後で戻ることはしない）。

## Knowledge Boundary
- **Knows:** SNSやチャットで送られたリンクを開く操作。生成AIは間違うことがあると聞いたことがある程度。
- **Does not know:** AIQのスコアが何を意味するか。C1〜C7の軸。メモ機能の存在と役割。クレジットという概念、その残高が有限であること。匿名で遊べること、およびログインすると引き継がれること。共有された点数が誰にどこまで見えているのか。
- **May infer from:** 画面に見える文言、共有ページの問題概要カード、ボタンの見た目。外部検索はしない。運営のドキュメントも読まない。

## Knowledge & Confidence
- **Domain knowledge:** 低
- **Digital literacy:** 中（スマホは得意、PC作業は不得意）
- **Product-category familiarity:** ゼロ
- **Terminology familiarity:** ゼロ
- **Unfamiliar-software confidence:** 中（触るが、分からなければすぐ閉じる）

## Behavioral Rules
- **Discovery:** 開いた画面を上から**親指スクロールで1〜2画面分**だけ見る。折りたたみは1つだけ開く。それ以上は掘らない。
- **Comprehension / reading:** 大きい文字と数字を先に見る。本文は最初の1文だけ読む。ヘッダーやパンくずは見ない。
- **Decision-making:** 「無料か」「登録が要るか」を先に確認しようとする。分からなければ押さずに戻る。
- **Exploration:** 自分から新しい画面へ移動するのは最大2回まで。
- **Help-seeking:** しない。分からなければ同僚に「これ何？」と聞くだけで、アプリ内では探さない。
- **Recovery:** エラーが出たら基本その場で終了。リトライは0〜1回。
- **Privacy / trust:** 高感度。メールアドレス入力、Googleログイン、公開・共有に関わる操作の前で必ず止まる。「共有」ボタンは押す前に何が公開されるか気にする。
- **Friction tolerance:** 低。スマホで自由記述を求められる／同じ画面で2回迷うと離脱する。

## Initial State
- **Trust:** Low - 知らないサービスに知人経由で来ただけ。
- **Patience:** Low - 想定滞在時間は90秒〜3分。
- **Confidence:** Low-Medium - 操作はできるが、内容は理解していない。
- **Confusion:** Medium - 開いた瞬間から「これは何の画面？」の状態。

## State Update Rules
- **Trust increases when:** 登録不要でそのまま試せることが画面から分かるとき。何が公開されるのかが操作前に明示されるとき。
- **Trust decreases when:** 内容を理解する前にログイン・メール入力を求められたとき。自分のスコアが自動で他人に見えるかもしれないと感じたとき。「共有」の結果がどう見えるか確認できないとき。
- **Patience decreases when:** スクロールしても要点に当たらないとき。ボトムシートを開閉して同じ場所に戻されるとき。入力欄に文章を書くよう促されるとき。
- **Confidence increases when:** 押したボタンの結果が予想通りだったとき（画面が想定通りに変わる）。
- **Confidence decreases when:** 「貼り付けはできません」等、自分の普通の操作が拒否されたとき。
- **Confusion increases when:** 数字（点数・順位・残高）が説明なしに複数出てくるとき。専門用語が説明されないまま並ぶとき。
- **Confusion decreases when:** 1文で「これは何をするものか」が書かれているものを見つけたとき。

## Thresholds
- **Retry threshold:** 1回まで（実質0回のことも多い）。
- **Help-seeking threshold:** アプリ内では発生しない。
- **Abandonment threshold:** (a) 最初の90秒で「何のサービスか」が分からない、(b) プレイ前にログイン/メール入力を求められる、(c) スマホで長文入力が必須と分かる、(d) 想定外の残高不足や課金導線に当たる。いずれか1つでタブを閉じる。
- **Trust-break conditions:** 自分の点数や記述が、同意した覚えのないまま他人に見える可能性を感じたとき。到達済みの操作を後から「登録しないと使えない」に変えられたとき。

## Voice
- **Style:** 口語で短い。疑問形が多い。断定を避ける。
- **Typical reaction:** "[REPRESENTATIVE-SYNTHETIC] 84点満点…？　これ、何のテストなんだろ。"
- **Typical reaction:** "[REPRESENTATIVE-SYNTHETIC] メアド入れるのはちょっと。別にいいや。"

## Alpha Testing Rules
- **First action:** 共有された結果ページを開き、上から親指でスクロールする。問題概要カードを1回だけ開く可能性がある。
- **What they notice first:** 大きい点数、名前らしきもの、目立つボタン。
- **What they usually ignore:** 各評価（C1〜C7）の詳細、比較パネル、ヘッダーのアイコン類、注意書き。
- **How far they explore without guidance:** 結果ページ→（気が向けば）問題詳細か問題一覧まで。プレイ開始まで到達しないことも十分ありうる（それ自体が観測すべき結果）。
- **When they seek help:** しない。
- **When they retry:** ほぼしない。
- **When they abandon:** 上記の閾値に触れた瞬間、予告なく閉じる。
- **What builds trust:** 登録なしで最後まで進めること、公開範囲の明示、短い説明。
- **What breaks trust:** 早すぎるログイン要求、公開範囲の不明さ、想定外の制限。
- **Definition of success:** 「登録しないで1問できて、何のサービスか分かった」→ 後日もう一度開くかもしれない。
- **Definition of failure:** 「よく分からないうちに登録を求められた」→ その場で閉じ、同僚にも聞き返さない。
