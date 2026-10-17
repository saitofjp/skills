【T0 ユーザー】
個人開発のクイズアプリ（React の SPA、DB と認証は Supabase、ホスティングは Vercel）に、2人が同じ問題を同時に解いて競う「リアルタイム対戦」を入れたい。実現方法を調査して

【T0 AI】
Supabase Realtime の最新仕様と、Vercel の WebSocket 制約、他の選択肢を並行して調べます。

（ツール実行: [WebFetch] {"url": "https://supabase.com/docs/guides/realtime", "prompt": "Summarize Supabase Realtime features: Broadcast, Presenc）

（ツール実行: [WebFetch] {"url": "https://supabase.com/docs/guides/realtime/limits", "prompt": "List the Realtime limits per plan (concurrent con）

（ツール実行: [WebFetch] {"url": "https://supabase.com/docs/guides/realtime/authorization", "prompt": "How does Realtime Authorization work (priv）

（ツール実行: [WebSearch] {"query": "Vercel functions WebSocket support 2026", "mode": "standard"}）

supabase.com への直接取得がプロキシで拒否されたので、検索で補います。

（ツール実行: [WebSearch] {"query": "Supabase Realtime limits concurrent connections messages per second free plan pro plan", "mode": "extended"}）

（ツール実行: [WebSearch] {"query": "Supabase Realtime Broadcast Presence private channel authorization realtime.messages RLS broadcast from datab）

（ツール実行: [WebSearch] {"query": "multiplayer quiz game server authoritative timing anti-cheat Supabase edge function answer validation", "mode）

# リアルタイム対戦の実現方法（Supabase + Vercel 構成）

## 結論

**今の構成のまま、Supabase Realtime を使うのがおすすめです。** サーバーを新しく立てる必要はありません。

- **通知の配信**: Supabase Realtime の Broadcast（部屋内へのイベント送信）と Presence（相手がオンラインかの検知）を使います。
- **正誤判定・時間判定・スコア**: Postgres の RPC（`SECURITY DEFINER` 関数）で行います。クライアントの申告は信用しません。
- **Vercel**: 今まで通り SPA の配信だけに使います。

Vercel Functions の WebSocket 対応は 2026年6月に公開ベータになったばかりです。接続は関数の最大実行時間で切れ、約5分で切断されたという検証報告もあります。また、部屋内への一斉配信や在席管理は自分で作る必要があります。このため、今回の用途では選ぶ理由が薄いです。

## 全体の流れ

```
[A] ──RPC: submit_answer──▶ Postgres (正誤・締切判定, 記録)
                               │ realtime.send()
                               ▼
[A][B] ◀──Broadcast "match:{id}"── Supabase Realtime
[A][B] ◀──Presence (在席/切断検知)──
```

1. **マッチング**
   - 最初は「合言葉／招待リンクで部屋に入る」形が一番簡単です。
   - ランダムマッチにする場合は、`join_match()` RPC 内で `SELECT ... FOR UPDATE SKIP LOCKED` を使い、待機中の部屋を1つ確保します。こうすると同時に参加しても競合しません。
2. **部屋のチャンネル**: `match:{match_id}` を private channel にします。参加者以外が購読・送信できないよう、RLS で制限します（SQL は後述）。
3. **出題**: 問題の開始時刻と締切は DB の `now()` で決めて `matches` テーブルに保存し、Broadcast で両者に知らせます。クライアントはその時刻を基準にカウントダウンを表示します。リロードしても残り時間は延びません。
4. **回答**
   - `submit_answer(match_id, q_index, choice)` RPC で回答します。この中で次の処理を行います。
     - 締切を過ぎていないかを `now()` で判定する
     - 正誤を判定する
     - 回答を記録する。`(match_id, user_id, q_index)` にユニーク制約を付けて、二重回答を防ぐ
   - 記録したら `realtime.send()` で「相手が回答した」ことを部屋に通知します。
5. **次の問題へ進む**
   - 常駐するゲームサーバーがないため、どちらのクライアントからでも `advance(match_id)` RPC を呼べるようにします。
   - RPC 内で「両者が回答済み」または「締切を過ぎた」場合だけ、条件付き UPDATE で状態を進めます。
   - 2人が同時に呼んでも1回しか進まないので、重複は問題になりません。
6. **切断**
   - Presence の leave イベントで「相手が切断」と表示します。
   - 戻ってこない場合も、上の締切判定で試合は自動的に進みます。

### 正解をクライアントに渡さない

正解は別テーブル（例: `question_answers`）に分け、クライアント向けの RLS ポリシーを作りません。正解を読めるのは `SECURITY DEFINER` の RPC だけになります。

`questions` テーブルに正解の列を残す場合は、RLS ではなく列単位の権限（`REVOKE SELECT (correct_answer) ...`）で隠します。RLS は行単位の制御なので、列は隠せません。

## 設定例（要点のみ）

```sql
-- 参加者だけが部屋チャンネルを受信できる
create policy "match members receive"
on realtime.messages for select to authenticated
using (
  realtime.messages.extension in ('broadcast', 'presence')
  and exists (
    select 1 from match_players mp
    where mp.user_id = auth.uid()
      and 'match:' || mp.match_id::text = (select realtime.topic())
  )
);
-- Presence の送信にも同じ条件で INSERT ポリシーが必要
-- Broadcast の送信は RPC 内の realtime.send() に限定すると改ざんしにくい
```

```ts
await supabase.realtime.setAuth()
const ch = supabase.channel(`match:${matchId}`, { config: { private: true } })
  .on('broadcast', { event: 'answered' }, ({ payload }) => { /* 相手の回答を表示 */ })
  .on('presence', { event: 'leave' }, () => { /* 相手が切断 */ })
  .subscribe(async (s) => { if (s === 'SUBSCRIBED') await ch.track({ userId }) })
```

## 制限とコスト

- **Free プラン**: 同時接続 200、メッセージ 100件/秒。
- **Pro プラン**: 同時接続 500、メッセージ 500件/秒。
- 上限を超えると切断されます（`tenant_events` エラー）。ただし supabase-js が自動で再接続します。
- 1試合は2接続で、メッセージも数件/秒程度なので、個人開発の規模なら Free で十分です。
- Free プランのプロジェクトは、しばらく使われないと一時停止されます。公開を続けるなら注意してください。

## 公平性について

- 「どちらが先に答えたか」は、サーバーが受け取った時刻（`now()`）で決めます。クライアントの時計は使いません。
- この時刻には通信の遅延が含まれますが、一般的なクイズアプリなら許容範囲です。
- 遅延による不公平が気になる場合は、「正解数で勝敗を決め、同点のときだけ回答時間を比べる」ルールにすると目立ちにくくなります。

## 他の選択肢

| 選択肢 | 向いているケース |
|---|---|
| **Supabase Realtime + RPC（推奨）** | 今の構成のまま追加できる。ターン制のクイズに十分 |
| Cloudflare Durable Objects / PartyKit | サーバー側で毎秒ゲームを進める厳密なタイマーや、大人数の部屋が必要な場合 |
| Ably / Pusher | 大規模配信。今回の用途には過剰 |
| Vercel Functions の WebSocket | ベータ版で、接続が切れる・一斉配信を自作する必要がある。今回は非推奨 |

## 進め方の提案

1. 招待リンクで部屋を作り、Broadcast で同期するところまでを作る
2. RPC による回答判定と `advance` を作る
3. Presence で切断を扱う
4. 必要ならランダムマッチを追加する

supabase.com のドキュメントはこの環境から直接取得できず、検索結果で確認しました。そのため `realtime.topic()` を使う RLS の正確な書き方と、`realtime.send()` の引数は、実装前に公式ドキュメントで確認してください。

ご希望であれば、テーブル定義と RPC の SQL 一式を作ります。

Sources:
- [Realtime Limits (Supabase)](https://supabase.com/docs/guides/realtime/limits)
- [Realtime Reports (Supabase)](https://supabase.com/docs/guides/realtime/reports)
- [Supabase Realtime: Broadcast and Presence Authorization](https://supabase.com/blog/supabase-realtime-broadcast-and-presence-authorization)
- [Realtime: Broadcast from Database](https://supabase.com/blog/realtime-broadcast-from-database)
- [Getting Started with Realtime](https://supabase.com/docs/guides/realtime/getting_started)
- [Supabase Realtimeの実装|3方式の使い分け](https://www.issoh.co.jp/tech/details/17058/)
- [Do Vercel serverless functions support WebSocket connections?](https://vercel.com/support/articles/do-vercel-serverless-functions-support-websocket-connections)
- [WebSocket support is now available for Python Functions](https://vercel.com/changelog/websocket-support-is-now-available-for-python-functions)
- [Vercel launches WebSocket support in public beta](https://releases.sh/release/rel_yNUn74KGsQqbJOSpgMBnY-vercel-launches-websocket-support-in-public-beta-for-functions)
- [Vercel Functions が WebSocket に対応したので試してみた（DevelopersIO）](https://dev.classmethod.jp/articles/vercel-functions-websocket-public-beta-verification/)
- [Vercel websockets vs Ably](https://ably.com/vercel/vercel-websockets-vs-ably)
- [How to Add a Knowledge Quiz to Your App](https://www.rapidevelopers.com/md/app-features/interactive-knowledge-quiz)

【T1 ユーザー】
WebRTC で P2P にすればサーバー代かからないよね？そっちのほうがよくない？

【T1 AI】
# WebRTC の P2P にするべきか

**このアプリではおすすめしません。** サーバー代はほとんど減らず、実装の手間と不正対策の難しさが増えるためです。

## サーバー代は減らない

- **今の案も 0 円で動く見込み**: 1試合で使うのは2接続、メッセージは数件/秒です。Supabase Free プランの同時接続 200・100件/秒に十分収まるので、P2P にしても節約できる金額がありません。
- **P2P でも中継役のサーバーは必要**
  - **シグナリング**: 接続を始めるときに、お互いの接続情報を交換する仕組みが要ります。結局 Supabase Realtime などを使うことになります。
  - **TURN（通信を中継するサーバー）**: スマホのキャリア回線や会社・学校のネットワークでは、直接つながらないことがよくあります。その場合は TURN で中継するしかなく、ここは通信量に応じた従量課金になります。TURN を用意しないと、一部のユーザーは対戦できません。

## 対戦ゲームとして困る点

- **不正を防げない**: 正誤判定やスコア計算をどちらかのブラウザで行うことになります。正解をクライアントに渡すことになり、開発者ツールで見られます。回答時刻やスコアも書き換えられます。
- **戦績やランキングを信用できない**: 結果をDBに保存しても、それはクライアントの自己申告です。前回の案では、サーバー（Postgres の RPC）が締切と正誤を判定するので、この問題がありません。
- **切断時の扱いが難しい**: どちらが正しい状態を持つかの調停役がいません。片方が落ちたときや再接続したときの処理を自分で設計する必要があります。
- **低遅延の利点がほぼない**: P2P は速いのが強みですが、クイズなら数百ミリ秒の遅延は問題になりません。

## P2P が向いているケース

- 対戦中に**ボイスチャットやビデオ**を付けたいとき。その場合も、試合の進行は今の案のままにして、通話だけを WebRTC にし、シグナリングに Supabase Realtime を使う構成が素直です。
- 友達同士で遊ぶだけで、**戦績やランキングを残さない**カジュアルなモード。

まずは前回の Supabase Realtime + RPC の構成で作り、通話などが必要になったときに WebRTC を足すのがいいと思います。

【T2 ユーザー】
ちなみに、マッチングってどうやるのが普通？レーティングとかも付けたい

【T2 AI】
# マッチングとレーティングの一般的な作り方

## マッチング

よく使われるのは次の3つで、多くのゲームは組み合わせて使っています。

| 方式 | 内容 | 向いている場面 |
|---|---|---|
| **フレンド対戦** | 招待コードやリンクで部屋に入る | 最初に作るならこれ。レートは変動させない |
| **ランダムマッチ（キュー方式）** | 待機列に入り、レートが近い相手と組む | レート戦 |
| **ゴースト対戦**（相手がいないときの代わり） | 他の人が過去に遊んだ回答記録と非同期で戦う | 同時にオンラインの人が少ないとき |

### 個人開発で一番困るのは人の少なさ

同時に待っている人が少ないと、いくらマッチングを工夫しても相手が見つかりません。そのため、次の2つがほぼ必須です。

- **待ち時間に応じて許容するレート差を広げる**: 例えば最初は ±100 にして、5秒ごとに ±50 ずつ広げます。
- **一定時間（20〜30秒など）見つからなければ、ゴースト対戦か Bot 対戦に切り替える**: 回答記録はすでに DB に保存しているので、ゴースト対戦は比較的作りやすいです。

### Supabase での実装例

`find_match()` という RPC を1つ用意すれば、常駐サーバーは要りません。

```sql
create function find_match() returns uuid
language plpgsql security definer as $$
declare
  my_rating int;
  opp record;
  new_match uuid;
begin
  select rating into my_rating from profiles where id = auth.uid();

  -- 相手の待ち時間が長いほど、許容するレート差を広げる
  select * into opp from match_queue
  where user_id <> auth.uid()
    and abs(rating - my_rating)
        <= 100 + 50 * floor(extract(epoch from now() - enqueued_at) / 5)
  order by enqueued_at
  limit 1
  for update skip locked;          -- 同時に呼ばれても同じ相手を取り合わない

  if found then
    delete from match_queue where user_id in (opp.user_id, auth.uid());
    insert into matches (status) values ('ready') returning id into new_match;
    insert into match_players (match_id, user_id)
      values (new_match, auth.uid()), (new_match, opp.user_id);
    -- 待っていた側に個人チャンネルで通知する
    perform realtime.send(
      jsonb_build_object('match_id', new_match), 'matched',
      'user:' || opp.user_id, true);
    return new_match;
  end if;

  insert into match_queue (user_id, rating) values (auth.uid(), my_rating)
    on conflict (user_id) do nothing;
  return null;  -- 見つからなければ待機列に入る
end $$;
```

- クライアントは数秒おきに `find_match()` を呼び直します。こうすると、待っている人同士も、広がったレート差の範囲でマッチします。
- 待っている側は private channel `user:{自分のID}` を購読して、`matched` の通知を受け取ります。前回と同じように、このチャンネルにも RLS が必要です。
- 待機列には古いエントリが残ることがあります。`enqueued_at` が古いものは除外または削除し、画面を閉じたときにも列から抜けるようにします。

## レーティング

| 方式 | 特徴 | 向いている場面 |
|---|---|---|
| **Elo** | 計算式が1行で済み、SQL だけで書ける | **最初はこれがおすすめ** |
| Glicko-2 | 「レートの確からしさ」も持つので、新規の人や久しぶりに遊ぶ人の評価が早く落ち着く | 精度を上げたくなったら移行する |
| TrueSkill / OpenSkill | 3人以上やチーム戦に対応する | 1対1なら不要 |

### Elo の計算

```
期待勝率 E_A = 1 / (1 + 10^((R_B - R_A) / 400))
新レート R_A' = R_A + K × (結果 - E_A)    ※結果: 勝ち=1、引き分け=0.5、負け=0
```

- 初期レートは 1500 にするのが一般的です。
- K は 32 程度にします。最初の10戦ほどは K を大きく（40〜60）して、本来の実力に早く近づけるのがよく使われる工夫です。

### 実装で気をつけること

- **レートの更新はサーバー側で、試合確定と同じトランザクションの中で行います。** 前回の `advance` RPC で試合を `finished` に変えるときに、一緒に計算するのがいいです。状態が変わったときだけ更新するので、2回呼ばれても二重に加算されません。
- **レートが変動するのはランダムマッチだけにします。** フレンド対戦も対象にすると、サブアカウントと組んでわざと負けてレートを稼ぐことができてしまいます。
- **途中で切断したら負けとして扱います。** そうしないと、負けそうなときに切断すれば済んでしまいます。
- 同じ相手と短時間に何度も当たったときは、レートの変動を減らすか、変動しないようにします。
- 表示はレートの数値そのものより、ブロンズ・シルバーのような**ランク帯**にすると、ユーザーにとって分かりやすいです。

## 作る順番の提案

1. フレンド対戦（ここまでは前回の内容）
2. 待機列 + `find_match()` によるランダムマッチ
3. Elo レート（ランダムマッチのみ）
4. 人が少ない時間帯への対策として、ゴースト対戦か Bot 対戦

必要なら、`profiles` / `match_queue` / `matches` / `match_players` のテーブル定義、RLS、`advance` 内での Elo 更新までをまとめた SQL を書きます。

【T3 ユーザー】
Supabase Realtime って無料枠だと同時接続どれくらいまでいける？

【T3 AI】
# Supabase Realtime 無料枠の同時接続数

公式の制限ページでは、Free プランの上限は次の通りです。

| 項目 | Free | Pro（参考） |
|---|---|---|
| 同時接続数 | **200** | 500（支出上限を外すと 10,000） |
| メッセージ数 / 秒 | **100** | 500 |
| Presence メッセージ数 / 秒 | 20 | 50 |
| 月間メッセージ数 | 200万件 | 500万件 |

月間メッセージ数は公式ページを直接見られず、複数のブログ記事で確認した値です。

## 対戦アプリに当てはめると

- **1接続はブラウザ1タブ**と考えてください。1つのタブで部屋や個人用の通知など複数のチャンネルを購読しても、接続は1本です。同じ人が2タブ開くと2接続になります。
- 全員が対戦中なら、**最大でおよそ100試合を同時に行えます**。ただし、ランダムマッチの待機中の人やロビーにいる人も、接続していれば数に入ります。
- **メッセージ数 / 秒**はクイズならまず問題になりません。1問ごとに出題・回答通知・判定の数件が送られるだけです。注意が必要なのは Presence の 20件/秒で、多くの人が同時に入退室すると先にこちらが上限に達する可能性があります。
- **月間メッセージ数**は、1試合（10問程度）で数十〜100件と見積もると、**月に数万試合**までは収まる計算です。1件の配信が受信者ごとに数えられるかどうかで実際の数は変わるので、運用を始めたらダッシュボードの Realtime Reports で実際の値を確認してください。

## 上限を超えたらどうなるか

- 接続が切断されます（`tenant_events` エラー）。supabase-js は、流量が上限を下回ると自動で再接続します。
- 長くつながったままのタブで枠を使い切らないように、Realtime には**対戦中とマッチング待ちのときだけ接続**し、終わったら `supabase.removeChannel()` で切断するようにしておくと安全です。

個人開発の初期なら、Free プランで足りなくなることはまずないと思います。同時にプレイする人が数百人規模になったら、Pro（月額 $25〜）に移行するのが目安です。

Sources:
- [Realtime Limits (Supabase)](https://supabase.com/docs/guides/realtime/limits)
- [Realtime Reports (Supabase)](https://supabase.com/docs/guides/realtime/reports)
- [Supabase Free Tier Limits: What You Actually Get In 2026](https://aiagencyplus.com/supabase-free-tier-limits/)

【T4 ユーザー】
あ、言ってなかったけど一番気にしてるのは不正対策。相手の答えが見えたり、タイマーをいじられたりするのは絶対に避けたい

【T4 AI】
# 不正対策の設計

基本の考え方は「**クライアントには、今の時点で見えてよい情報しか渡さない。判定はすべてサーバーで行う**」です。今の構成（Supabase の RPC と RLS）で、ご心配の2点は防げます。

## 1. 相手の答えが見えないようにする

相手の答えが漏れる経路は主に4つあり、それぞれ塞ぎます。

| 漏れる経路 | 対策 |
|---|---|
| 回答テーブルを直接 SELECT する | RLS で「自分の回答」と「締切を過ぎた問題の相手の回答」だけ読めるようにする |
| Realtime の通知 | 回答時に送るのは「答えた」という事実だけにして、選んだ選択肢は含めない |
| Postgres Changes（テーブルの変更をそのまま配信する機能） | 回答テーブルや試合テーブルを `supabase_realtime` publication に**追加しない** |
| クライアントからの Broadcast 送信 | `realtime.messages` に broadcast の INSERT ポリシーを作らない。送信は RPC 内の `realtime.send()` だけにする |

```sql
alter table match_answers enable row level security;

create policy "own answers, or opponent's after close"
on match_answers for select to authenticated
using (
  user_id = auth.uid()
  or exists (
    select 1 from matches m
    join match_players mp on mp.match_id = m.id and mp.user_id = auth.uid()
    where m.id = match_answers.match_id
      and (match_answers.q_index < m.current_q or now() > m.q_deadline)
  )
);
-- INSERT / UPDATE / DELETE のポリシーは作らない（書き込みは RPC だけに限定）
```

**選択肢の並び順を、プレイヤーごとにシャッフルします。** こうすると「Bだよ」のように Discord などで答えを教え合っても役に立ちません。そのため、回答は表示上の番号ではなく選択肢の ID で受け取ります。

## 2. 正解と問題文を先に見られないようにする

- 正解は `question_answers` などの別テーブルに分け、クライアント向けのポリシーは作りません。
- **問題文は、出題時刻になるまで渡しません。** 全問をまとめて先に取得すると、開発者ツールで読まれて事前に調べられてしまいます。

```sql
create function get_current_question(p_match uuid) returns jsonb
language plpgsql security definer set search_path = '' as $$
declare m public.matches;
begin
  select * into m from public.matches where id = p_match;
  if not exists (select 1 from public.match_players
                 where match_id = p_match and user_id = auth.uid()) then
    raise exception 'not a player';
  end if;
  if now() < m.q_started_at then
    raise exception 'not started';   -- 出題時刻より前は返さない
  end if;
  -- 問題文と、このプレイヤー用にシャッフルした選択肢（ID とテキスト）だけを返す。正解は含めない
  ...
end $$;
```

## 3. タイマーをいじられないようにする

**クライアントのタイマーは表示用にすぎず、判定には一切使いません。**

- `advance` RPC で次の問題に進むときに、`q_started_at = now() + interval '3 seconds'` と `q_deadline = q_started_at + 制限時間` を DB に保存します。3秒は出題前のカウントダウンです。
- `submit_answer` RPC では、DB の `now()` が `q_started_at` から `q_deadline` の間にあるときだけ回答を受け付けます。ブラウザの時計を変えても、JS を書き換えても、結果は変わりません。
- 回答時間は `now() - q_started_at` でサーバーが計算します。クライアントから送られた経過時間は使いません。
- `(match_id, user_id, q_index)` にユニーク制約を付けて、二重回答や回答の変更を防ぎます。
- 正誤は、その問題が締切を迎えるまで両者に返しません。

```sql
create function submit_answer(p_match uuid, p_q int, p_choice uuid) returns void
language plpgsql security definer set search_path = '' as $$
declare m public.matches;
begin
  select * into m from public.matches where id = p_match for update;
  if not exists (select 1 from public.match_players
                 where match_id = p_match and user_id = auth.uid()) then
    raise exception 'not a player';
  end if;
  if m.status <> 'playing' or m.current_q <> p_q then
    raise exception 'invalid question';
  end if;
  if now() < m.q_started_at or now() > m.q_deadline then
    raise exception 'out of time';
  end if;

  insert into public.match_answers (match_id, user_id, q_index, choice_id, is_correct, elapsed_ms)
  select p_match, auth.uid(), p_q, p_choice, (qa.correct_choice_id = p_choice),
         (extract(epoch from now() - m.q_started_at) * 1000)::int
  from public.question_answers qa
  where qa.question_id = m.current_question_id;   -- 二重回答はユニーク制約でエラーになる

  -- 通知は「答えた」という事実だけ。選択肢は含めない
  perform realtime.send(jsonb_build_object('user_id', auth.uid(), 'q', p_q),
                        'answered', 'match:' || p_match, true);
end $$;
```

## 4. 全体で押さえておくこと

- **すべてのテーブルで RLS を有効にし、クライアントからの書き込みポリシーは作りません。** 書き込みは RPC 経由だけにします。
- RPC は誰でも直接呼べるという前提で書きます。どの RPC も、最初に「`auth.uid()` がこの試合の参加者か」と「今の試合の状態でその操作をしてよいか」を確認します。
- `security definer` の関数には `set search_path = ''` を付けます。付けないと、別のスキーマに置かれた同名のテーブルや関数にすり替えられる危険があります。
- 未ログインのユーザーに RPC を使わせないよう、`revoke execute on function ... from anon` も実行しておきます。
- **スコアとレートはサーバーだけが計算します。** クライアントから送られた結果は保存しません。

## 防ぎきれない不正

ここは、どんな構成を選んでも完全には防げない部分です。

- **別の画面で検索する、他の人に聞く**: 制限時間を短くし、回答の速さもスコアに加えることで影響を小さくできます。
- **Bot による自動回答**: 回答時間はすべて記録されるので、毎回極端に速い人や正答率が不自然に高い人を後から検出し、ランク戦から外す運用で対応します。
- **通信の速さによる差**: 回線が速い人のほうが、回答時刻がわずかに早く記録されます。気になる場合は、「正解数で勝敗を決め、同点のときだけ時間を比べる」ルールにすると影響は小さくなります。

ご希望であれば、テーブル定義、RLS、RPC（`find_match` / `advance` / `get_current_question` / `submit_answer`）をまとめた SQL を一式書きます。そのときに、上のチェック項目もすべて盛り込みます。

【T5 ユーザー】
それなら Cloudflare Durable Objects ってどう？対戦ルームに向いてるって聞いた

【T5 AI】
Durable Objects の最新の料金と制約を確認します。

（ツール実行: [WebSearch] {"query": "Cloudflare Durable Objects pricing free plan WebSocket hibernation limits 2026", "mode": "standard"}）

（ツール実行: [WebSearch] {"query": "Cloudflare Durable Objects verify Supabase JWT authentication WebSocket game room alarms", "mode": "standard"）

# Cloudflare Durable Objects は使うべきか

**使う価値は十分あります。** ただし理由ははっきりさせておきます。DO にしたから不正対策が強くなるわけではありません。Supabase の RPC で判定する案も、サーバーが判定する（サーバー権威型の）設計なので、相手の答えやタイマーを守る強さは同じです。DO の利点は、**同じ守りを、ミスが起きにくい形で実装できる**ことです。

## Durable Objects が対戦ルームに向いている理由

- **1試合を1つのオブジェクトにできる**: 問題・正解・回答・タイマーを、その部屋のサーバー側のメモリやストレージだけに持てます。クライアントが直接読める DB に置かないので、RLS の設定ミスで漏れるという心配がなくなります。Supabase 案での一番のリスクはここでした。
- **処理が順番に1つずつ実行される**: 1つのオブジェクトは同時に1つの処理しか実行しません。「同時に回答した」「2人が同時に次の問題へ進めようとした」といった競合を、`FOR UPDATE` などで考える必要がありません。
- **サーバーが自分でタイマーを動かせる**: Alarms 機能で締切の時刻にオブジェクトが起動し、自分で次の問題に進めます。Supabase 案のように、クライアントに `advance` を呼んでもらう必要がなくなります。
- **ロジックを TypeScript で書ける**: SQL の RPC と RLS ポリシーに分散していたロジックを、1つのクラスにまとめられます。
- **料金**: Free プランでも使えます。上限はリクエスト 10万件/日と実行時間 13,000 GB-s/日です。WebSocket は1接続で1リクエスト、クライアントからのメッセージは20件で1リクエストとして数えられます。Hibernation API を使えば、待っている間の実行時間は課金されません。クイズの対戦なら、個人開発の規模では無料枠に収まります。

## 増える手間

- **管理するサービスが1つ増える**: Vercel（SPA）、Supabase（認証・DB）、Cloudflare（対戦）の3つになります。
- **認証をつなぐ処理が必要**: Worker で Supabase の JWT を検証してから、DO に接続を渡します。Supabase の非対称鍵を使っているなら、JWKS（`/auth/v1/.well-known/jwks.json`）と `jose` ライブラリで検証できます。
- **結果を Supabase に書き戻す必要がある**: 試合が終わったら、DO から service role キーで戦績とレートを書き込みます。service role キーは Cloudflare の Secret に保存します。
- **自分で作る部分が増える**: 在席の管理（Presence に当たるもの）や再接続の処理です。ただし対戦ルームなら、「WebSocket が切れた」というイベントと猶予時間のタイマーで足ります。
- **Cloudflare 特有の注意点**: `setTimeout` は使わず Alarms を使います。また、オブジェクトは休止すると起き直すので、メモリの状態だけに頼らず `ctx.storage` に保存しておきます。

## 構成案

```
[SPA on Vercel] ──Supabase Auth でログイン──▶ JWT
      │
      └─ wss://game.example.com/match?token=... ──▶ [Worker] JWT 検証
                                                       │
                     ┌─────────────────────────────────┤
                     ▼                                 ▼
             [Matchmaker DO] (1個)              [MatchRoom DO] (1試合1個)
             待機列とレート差の拡大              出題・締切 Alarm・判定・スコア
                     │ マッチ成立                      │ 試合終了
                     └──── 試合ID を両者に通知          └─▶ Supabase に戦績とレートを保存
```

```ts
export class MatchRoom extends DurableObject {
  async fetch(req: Request) {
    const userId = req.headers.get('x-user-id')!   // Worker が JWT を検証済み
    if (!(await this.isPlayer(userId))) return new Response('forbidden', { status: 403 })
    const [client, server] = Object.values(new WebSocketPair())
    this.ctx.acceptWebSocket(server, [userId])     // Hibernation API
    return new Response(null, { status: 101, webSocket: client })
  }

  async webSocketMessage(ws: WebSocket, msg: string) {
    const [userId] = this.ctx.getTags(ws)
    const { type, choiceId } = JSON.parse(msg)
    if (type !== 'answer') return
    const s = await this.load()
    if (Date.now() < s.startedAt || Date.now() > s.deadline) return  // 時刻はサーバーの時計だけで判定
    if (s.answers[userId]) return                                     // 二重回答を防ぐ
    s.answers[userId] = { choiceId, ms: Date.now() - s.startedAt }
    await this.save(s)
    this.broadcast({ type: 'answered', userId })   // 選んだ選択肢は送らない
    if (Object.keys(s.answers).length === 2) await this.closeQuestion(s)
  }

  async alarm() { await this.closeQuestion(await this.load()) }  // 締切になったら自動で次へ
}
```

前回まとめた不正対策は、そのまま DO 側で実現できます。問題文は出題時刻に送る、正解は締切後に送る、選択肢は人ごとにシャッフルする、回答時間はサーバーの時計で測る、という点です。

## どちらを選ぶか

| | Supabase RPC + Realtime | Durable Objects |
|---|---|---|
| 不正対策の強さ | 同じ（サーバー権威型） | 同じ（サーバー権威型） |
| 設定ミスによる漏洩のリスク | RLS や RPC の設定ミスで漏れうる | 判定に使うデータがクライアントから届かない場所にある |
| タイマーの進行 | クライアントが RPC を呼ぶ | サーバーが Alarm で進める |
| 構成の数 | 2つのまま | 3つになる |
| 書く言語 | SQL / PL/pgSQL | TypeScript |

**不正対策を最優先にするなら、DO で対戦ルームとマッチングを作り、Supabase は認証と戦績・レートの保存だけに使う構成をおすすめします。** 守るべきデータを置く場所を DO の中だけに限定できるので、「どこか1つ RLS を間違えたら漏れる」という状態を避けられるからです。SQL のほうが書き慣れていて、サービスを増やしたくない場合は、前回の Supabase 案でも同じ水準で守れます。

## 確認できなかった点

- 1オブジェクトあたりのストレージ上限は、Free プランについて資料によって 1GB と 10GB の2通りの記載がありました。1試合のデータは数KB なので、今回の用途では影響しません。
- Supabase の JWT を Worker で検証する方法は、公式の組み合わせ例を見つけられませんでした。上で書いた JWKS を使う方法は一般的な手順ですが、実装前に Supabase のドキュメントで、お使いのプロジェクトの鍵の方式（非対称鍵か共有シークレットか）を確認してください。

DO 案で進める場合は、Worker、Matchmaker DO、MatchRoom DO、Supabase への書き戻しまでをまとめた雛形を書けます。

Sources:
- [Durable Objects Pricing (Cloudflare Docs)](https://developers.cloudflare.com/durable-objects/platform/pricing)
- [Durable Objects FAQ (Cloudflare Docs)](https://developers.cloudflare.com/durable-objects/reference/faq)
- [Durable Objects Release Notes](https://2b20f69b.previews.developers.cloudflare.com/durable-objects/release-notes/index.md)
- [Durable Objects API (Cloudflare Docs)](https://developers.cloudflare.com:2053/durable-objects/api)
- [Cloudflare WebSockets: CDN, Workers & Durable Objects](https://websocket.org/guides/infrastructure/cloudflare/)
- [FlareCalc: Durable Objects calculator](https://flarecalc.com/calculators/durable-objects)
- [cloudflare/skills durable-objects (playbooks)](https://playbooks.com/skills/cloudflare/skills/durable-objects)
- [jezweb cloudflare-durable-objects skill](https://tessl.io/skills/github/jezweb/claude-skills/cloudflare-durable-objects)

【T6 ユーザー】
でも Durable Objects を入れると Vercel・Supabase・Cloudflare の3つになるのが嫌だな。Supabase だけでできない？

【T6 AI】
# Supabase だけで作れるか

**作れます。不正対策の強さも DO 案と同じ水準にできます。** 前回挙げた DO の利点は3つでしたが、どれも Supabase の機能で代わりが用意できます。

| DO の利点 | Supabase での代わり |
|---|---|
| 守るべきデータがクライアントから届かない場所にある | ゲーム用のテーブルを、**API に公開しないスキーマ**に置く |
| 処理が1つずつ順番に実行される | 各 RPC の最初で、試合の行を `select ... for update` でロックする |
| サーバーが Alarm で問題を進める | 締切の判定は `now()` で行い、進行は「誰が呼んでも安全な RPC」と pg_cron で補う |

## 1. ゲームデータを非公開スキーマに置く

DO 案の一番の利点は、問題・正解・回答をクライアントから届かない場所に置けることでした。Supabase でも同じことができます。

```sql
create schema game;   -- Dashboard の API 設定で「公開するスキーマ」に追加しない
revoke all on schema game from anon, authenticated;

create table game.matches (...);
create table game.match_players (...);
create table game.match_answers (...);
create table game.questions (...);
create table game.question_answers (...);
```

- `game` スキーマを公開しなければ、REST API（PostgREST）からは**テーブルの存在すら見えません**。RLS のポリシーを1つ書き忘れても、そこから漏れることはありません。
- クライアントが触れられるのは、`public` スキーマに置いた少数の RPC だけになります。例えば `find_match`、`leave_queue`、`get_current_question`、`submit_answer`、`advance` です。
- RPC は `security definer set search_path = ''` で定義し、中では `game.matches` のようにスキーマ名付きでテーブルを参照します。
- 「入口が RPC だけ」という構造は、DO の WebSocket で受けるメッセージを処理する部分と同じ役割になります。

## 2. 同時実行をロックで1つずつにする

```sql
select * into m from game.matches where id = p_match for update;
```

すべての RPC の最初でこの行をロックすれば、同じ試合への処理は1つずつ順番に実行されます。DO と同じく、同時に回答が来ても状態が壊れません。

## 3. タイマーの進行

ここは、DO の Alarm と考え方が違う部分です。

- **不正対策の上では、締切を `now()` で判定していれば十分です。** 誰も `advance` を呼ばなくても、締切を過ぎた回答は受け付けません。クライアントが `advance` を早く呼んでも、「両者が回答済み」か「締切を過ぎた」のどちらかでなければ何も起きません。つまり、**呼ぶタイミングをいじられても得をする方法がありません。**
- 通常は、両方のクライアントが締切の時刻に `advance` を呼びます。呼ばれるのが2回でも、進むのは1回だけです。
- 2人とも切断して試合が止まった場合に備え、**pg_cron**（Supabase Cron）で数十秒〜1分ごとに締切切れの試合をまとめて進めるか、放棄された試合として終了させます。pg_cron は秒単位の間隔も指定できます。ただ、これは後片付けだけが目的なので、1分ごとでも問題ありません。

## 4. Realtime の設定

前回と同じ内容です。

- Broadcast は、RPC の中の `realtime.send()` からだけ送ります。`realtime.messages` には、broadcast の INSERT ポリシーを作りません。
- クライアントからの送信は、Presence だけを許可します。
- `game` スキーマのテーブルは `supabase_realtime` publication に入れません。

## 5. 設定ミスを防ぐ確認

DO なら確認するのは TypeScript のコード1か所ですが、Supabase では次の手順で確認します。

- Dashboard の **Security Advisor** を実行し、RLS が無効なテーブルや `search_path` が指定されていない関数がないかを見ます。
- **別のユーザーで試します**。他人のトークンを使い、`supabase-js` から「他人の試合の `get_current_question`」「締切後の `submit_answer`」「`game` スキーマのテーブルへの直接アクセス」を実行して、すべて拒否されることを確かめます。これを簡単なスクリプトにしておき、RPC を変更するたびに流します。

## DO 案と比べて残る違い

- **ロジックを PL/pgSQL で書くことになります。** TypeScript に比べると、書きやすさやテストのしやすさでは劣ります。
- **問題を進めるタイミングは、主にクライアントからの呼び出しに頼ります。** 不正には影響しませんが、片方の通信が遅いと、画面が次の問題に切り替わるのが少し遅れることはあります。

この2点を受け入れられるなら、**Vercel と Supabase だけの構成で十分です。** 全体の構成は、Supabase Realtime（Broadcast と Presence）、非公開の `game` スキーマ、少数の RPC、片付け用の pg_cron になります。

必要なら、`game` スキーマのテーブル定義、公開する RPC 一式（マッチング・出題・回答・進行・Elo 更新）、Realtime の RLS、pg_cron の設定、確認用スクリプトまでをまとめて書きます。

【T7 ユーザー】
結局、最初の一歩としてどこから作るのがいい？

【T7 AI】
# 最初に作るもの

**招待リンクで2人が1試合を最後まで遊べるところまで**を最初に作るのがおすすめです。ランダムマッチやレートは後回しにします。

ただし、不正対策の仕組み（非公開の `game` スキーマ、判定は RPC だけで行う、締切は `now()` で判定する）は**最初から入れてください**。後から入れようとすると、クライアントが DB を直接読み書きするコードを書き直すことになり、遠回りになります。

## ステップ1でやること

1. **DB**
   - `game` スキーマを作ります（API には公開しません）。
   - テーブルは `matches`、`match_players`、`questions`、`question_answers`、`match_answers` の5つです。
   - 問題は既存のものから10問程度をコピーしておけば十分です。
2. **RPC**（5つ）
   - `create_match()`: 部屋を作り、招待コードを返します。
   - `join_match(code)`: 2人目として参加します。2人そろったら最初の問題の出題時刻（`q_started_at`）を決めます。
   - `get_current_question(match_id)`: 出題時刻を過ぎていれば、正解を含まない問題文と選択肢を返します。
   - `submit_answer(match_id, q, choice_id)`: 締切内かどうかと二重回答を確認し、回答を記録します。
   - `advance(match_id)`: 両者が回答済みか締切を過ぎていれば、次の問題に進むか試合を終了させます。
3. **Realtime**
   - private channel `match:{id}` を使い、参加者だけが受信できるように RLS を設定します。
   - RPC 内の `realtime.send()` で `started`、`answered`、`question_closed`、`finished` の4種類を通知します。
4. **画面**
   - 部屋を作る、リンクで参加する、対戦する、結果を見る、の4画面です。タイマーは表示用だけです。

## ステップ1で作らないもの

ランダムマッチ、レート、Presence による切断表示、pg_cron による後片付け、ゴースト対戦は作りません。

切断への対応も今は不要です。締切を `now()` で判定しているので、相手が落ちても試合は止まらず進みます。

## 完了の目安

- 2つのブラウザ（別アカウント）で、10問の試合を最後まで遊べる。
- 確認用スクリプトで、次の操作がすべて拒否される。
  - `game` スキーマのテーブルを直接 SELECT する
  - 他人の試合の `get_current_question` を呼ぶ
  - 締切を過ぎてから `submit_answer` を呼ぶ
  - 同じ問題に2回回答する
  - 出題時刻より前に問題を取得する

この2つを満たせば、不正対策の土台は完成です。

## その後の順番

1. Presence で「相手が切断」を表示し、pg_cron で放棄された試合を片付ける
2. ランダムマッチ（`find_match`）
3. Elo レート
4. 人が少ない時間帯のためのゴースト対戦

ステップ1の SQL（スキーマ、テーブル、RPC 5つ、Realtime の RLS）と確認用スクリプトを書きましょうか？既存のテーブル構成（問題テーブルの列など）を教えてもらえれば、それに合わせて作ります。

