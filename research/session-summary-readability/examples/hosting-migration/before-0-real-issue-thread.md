> **改善前（実物）** 調査結果を Issue に2回に分けて追記したもの。1本目は最初の依頼（Supabase へ移した場合の影響）への回答、2本目は「代替案系も含めて、書いてみて」への回答。
> この行より下は、AIが書いたままの本文である。

---

--- issue #1588 コメント 1 ---

Supabase Edge Functions への移行インパクトを、実際のコード（`api/*.ts` 全9本）と公式ドキュメントを突き合わせて調べました。結論から言うと、**issue本文の「AIQならほぼ問題ない」という見立ては `/api/chat` `/api/score` については正しい**です。ただし、issueの表に載っていない項目に**移行コストの本体**があります。

---

## 0. 前提の訂正：AIQは今 Vercel Edge Functions を使っていない

タイトルは「Vercel Edge Functions → Supabase Edge Functions」ですが、実際には**AIQに Edge Functions は1本もありません**。

- `api/*.ts` 全9本に `export const config = { runtime: 'edge' }` が無い → 全部 **Node.js Serverless Functions**
- ハンドラのシグネチャが全部 `(req: IncomingMessage, res: ServerResponse)`（9ファイル全部）
- `api/og.ts:2` `api/meta.ts:2` が `node:fs` を直接使っている
- `process.env` 参照が12箇所

つまり実際に検討するのは **「Node Serverless → Deno Edge」** です。ランタイムが Node → Deno に変わるので、移行の重さがだいぶ違ってきます。

---

## 1. 現状の棚卸し

| エンドポイント | 役割 | Vercel固有 / Node固有依存 | 移行難易度 |
| --- | --- | --- | --- |
| `api/chat.ts` | Bedrock ストリーミング | Vercel OIDC、`pipeUIMessageStreamToResponse` | **中** |
| `api/score.ts` | Bedrock 採点（非ストリーミング） | Vercel OIDC | **中** |
| `api/og.ts` | OGP画像PNG生成（467行） | `@resvg/resvg-js`（native addon）、`node:fs`、フォント9.2MB同梱 | **最難** |
| `api/meta.ts` | OGP meta注入HTML返却 | `dist/spa.html` 読み込み、HTML返却、vercel.json rewrite | **最難** |
| `api/stripe-webhook.ts` | 決済Webhook | `constructEvent`（同期・Node crypto） | **易** |
| `api/checkout.ts` | Stripe Checkout作成 | なし | 易 |
| `api/sitemap.ts` | sitemap.xml | vercel.json rewrite（`/sitemap.xml`） | 易 |
| `api/claim-anon-sessions.ts` | 匿名→本会員のデータ移管 | なし | 易 |
| `api/debug-credits.ts` | デバッグ用 | なし | 易 |

---

## 2. issue本文の制限表に対する当たり判定

### ✅ CPU 2秒 — チャット/採点は問題なし。ただし `/api/og` は別

issue本文の「Bedrockの待ち時間はI/OなのでCPUを食わない」は**その通り**です。`api/chat.ts` `api/score.ts` はどちらもプロンプト組み立て（`JSON.stringify`）＋ `fetch` 待ちなので、CPU 2秒には全く当たりません。

**唯一の実質リスクが `/api/og`** です。ここは純粋なCPU処理です：

```
SVG文字列を組む → resvg で 2400×1260 にラスタライズ → PNGエンコード
```

しかも後述（3-4）の通り native → WASM になるので、**今より遅くなる方向**です。ここが2秒に収まるかは実測しないと分かりません（Vercel側でも現状 `/api/og` の所要時間は計測していない）。

### ⚠️ 150秒 idle timeout — 現状は余裕あり、ただし天井は下がる

`/api/score` は `generateText`（非ストリーミング）なので、**採点が終わるまで1バイトも返しません**。実測値は E2E の記録に残っていて、

> `scenario-with-api.spec.ts` | 1 | 1分18秒（うち **`/api/score` が42秒**）
> — `plans/archive/20260819-001-CI-E2Eの実行時間短縮.md`

42秒なので150秒には収まります。ただし比較対象として、**現在のVercel（Fluid compute）は Pro で最大800秒**（[Vercel Functions Limits](https://vercel.com/docs/functions/limitations)）なので、**天井は 800秒 → 150秒 に下がります**。

`maxReasoningEffort` を `medium` → `high` に戻す（#1536 で下げた経緯がある）、問題文が長文化する、といった変化で余裕が削られる方向なので、移行するなら **`/api/score` をストリーミング化して150秒制約から外す**のがセットになると思います。

### ⚠️ メモリ 256MB — `/api/og` は要実測

`/api/og` の内訳がけっこう重いです：

- Noto Serif JP（**8.0MB**）+ Inter 876KB + Newsreader 452KB + JetBrains Mono 187KB = **フォント計 9.2MB**
- logo-big.png **516KB**（base64 data URI 化するので実効 ~690KB）
- 2400×1260 RGBA ビットマップ ≒ **12MB**
- resvg WASM のヒープ

256MBには収まりそうですが、余裕がどれくらいかは実測待ちです。

### ✅ Function数 — 全く問題なし（9本）

issue本文の通りです。1点だけ訂正すると、[公式Limits](https://supabase.com/docs/guides/functions/limits)では **Pro は 500**（1000 は Team プラン）です。いずれにせよ9本なので誤差です。

### ⚠️ Functionサイズ 20MB — `/api/og` だけ注意

`/api/og` 1本で フォント9.2MB + ロゴ516KB + resvg WASM。20MBには収まりそうですが余裕は少ないです。

さらに地味に効くのが、公式Limitsのこの一文：

> Static files cannot be deployed using the API flag. You need to build them with **Docker on the CLI**.

フォントを `static_files` で同梱する以上、**`--use-api` でのデプロイが使えず Docker 必須**になります。CI/CDの構成に影響します。

---

## 3. issueの表に載っていない項目（← ここが移行コストの本体）

### 3-1. 【最大】Vercel OIDC → AWS恒久アクセスキーへの後退

`api/_lib/aws-credentials.ts` はこれだけのファイルです：

```ts
import { awsCredentialsProvider } from '@vercel/oidc-aws-credentials-provider'
export function getBedrockCredentialProvider() {
  return awsCredentialsProvider({ roleArn: process.env.AWS_ROLE_ARN! })
}
```

VercelがOIDCトークンを発行 → `AssumeRoleWithWebIdentity` で `aiq-bedrock-vercel` ロールの**一時クレデンシャル**を得る、という構成です。そしてこれは `docs/tech-notes/vercel-aws-oidc連携.md` に、

> issue #15 では当初「Bedrock専用IAMユーザー＋アクセスキー」を想定していたが、**長期キーをVercel環境変数に保存するリスクを避けるため**、VercelのOIDC Federationを使う方式に変更した

と、**意図的にキー方式を捨てて選んだ**設計です。

Supabase Edge Functions には同等のワークロードIDフェデレーションがありません。したがって移行すると **IAMユーザーの恒久アクセスキーを Supabase Secrets に置く**しかなく、**#15 で一度捨てた案に戻ります**。

> 補足：「SupabaseのJWKSをAWSのOIDC IdPとして登録する」手は使えません。Supabaseが発行するJWTの `sub` は**エンドユーザーのID**なので、それでRoleをAssumeできるようにすると任意のユーザーがBedrockを叩けてしまいます。ワークロードIDではないので代替になりません。

技術的な救いとして、**Bedrock呼び出しそのものはDenoで問題なく動きます**。`@ai-sdk/amazon-bedrock@4.0.111` の依存を見ると SigV4署名を `aws4fetch` で自前実装していて、AWS SDKは不要です：

```
@ai-sdk/amazon-bedrock -> @smithy/eventstream-codec, @smithy/util-utf8, aws4fetch
```

AWS SDK（`@aws-sdk/credential-providers`）を引きずり込んでいるのは**認証情報の取得経路だけ**です。つまり難所は署名ではなく「クレデンシャルの出所をどうするか」という**セキュリティ設計の判断**です。

### 3-2. `/api/meta` のHTML返却は「カスタムドメイン必須」

[公式Limits](https://supabase.com/docs/guides/functions/limits) にこう書かれています：

> Serving of HTML content is only supported with **custom domains** (Otherwise `GET` requests that return `text/html` will be rewritten to `text/plain`).

`api/meta.ts` は `dist/spa.html` を読んで `<head>` にOGP metaを注入して `Content-Type: text/html` で返す、まさにHTML配信です。**Supabaseのカスタムドメイン（有料アドオン）が前提条件**になります。

さらに厄介なのが、`dist/spa.html` が **Viteのビルド成果物**だという点です。今は `vercel.json` の `"api/meta.ts": { "includeFiles": "dist/spa.html" }` でlambdaに同梱していますが、Supabaseの `static_files` は「リポジトリ内の静的ファイル」を想定した仕組みなので、**ビルド → 関数ディレクトリへコピー → deploy** という工程を自前で組む必要があります（`api/_lib/meta-html.ts:22-23` のパス解決も書き直し）。

### 3-3. vercel.json の rewrite に相当する機能が無い ← 移行の動機に直結

これが**一番効く**と思います。現在の `vercel.json` は：

- `/sitemap.xml` → `/api/sitemap`
- クローラーUA（facebookexternalhit / twitterbot / slackbot / …）または `?__og=1` のとき → `/api/meta?path=/$1`
- それ以外の全SPAルート → `/spa.html`

OGPは **`/problem/:id` `/r/:publicId` というSPAのURLそのまま**でクローラーに叩かれ、UA条件で内部rewriteして `/api/meta` に流す設計です。

Supabase Edge Functions のエンドポイントは `https://<ref>.supabase.co/functions/v1/<name>` に固定で、**こういうホスト全体のルーティング層を持ちません**。しかも Supabase は静的サイトホスティングを提供していません。

つまり：

> **バックエンドを全部Supabaseに寄せても、フロントのホスティング＋ルーティング層は Vercel（か Cloudflare Pages 等）に残ります。**

[1つ目のコメント](https://github.com/saitofjp/aiq/issues/1588#issuecomment-5577558691)の Hobby商用利用の話が移行の動機だとすると、**Supabase Edge Functions への移行だけでは解決しません**（Vercelが残る＝Proが必要）。ここは分けて考える必要があります。

（なお Vercel の rewrite は destination に外部URLを書けるので、Vercelに残したルーティング層から Supabase へプロキシする形は可能です。ただし1ホップ増えます。）

### 3-4. `/api/og` の resvg：native → WASM への差し戻し

公式Limitsに：

> **Node Libraries that require multithreading are not supported.** Examples: libvips, sharp

`@resvg/resvg-js` は napi-rs の native addon（`.node`）で、そもそもDeno/edge-runtimeでは読み込めません。**`@resvg/resvg-wasm` への差し替えが必須**です。

これが厄介なのは、`docs/tech-notes/共有カードOG画像生成-描画基盤.md §1` で**わざわざWASM版を避けてnativeを選んだ経緯がある**ことです：

> **採用**: Node Serverless Function ＋ 純SVG文字列 ＋ `@resvg/resvg-js`
> Edge Runtime の resvg は **WASM版**で、Vercelのfunction builderと噛み合わずローカル `vercel dev` でも落ちやすい。
> **Node にする利点**: native版 resvg が使え、`fs` でフォントを読める。

つまり**この設計判断を巻き戻す**ことになります。加えて：

- WASM版は `fontFiles`（パス配列）APIを持たず、`initWasm()` ＋ フォントを ArrayBuffer で渡す形なので、`api/og.ts:65-80` の `fontDirCandidates()` / `resolveFontFiles()` は全面書き直し
- 上記の CPU 2秒 / メモリ 256MB とのせめぎ合いになる

現実解は Supabase公式が OG画像生成で推奨している **Storage への cache-first パターン**（生成済みPNGをStorageに置いてCDNで配る）ですが、AIQは `is_public` が事後にトグルされうる（`api/og.ts:445` のコメントに明記）ので、**キャッシュ無効化の設計が新たに必要**になります。

### 3-5. `verify_jwt` の設計（`supabase/config.toml` が現状リポジトリに無い）

Supabase Edge Functions は既定でJWT必須です。エンドポイントごとに分かれます：

**JWT必須のままでOK**（`Authorization: Bearer <supabase access token>` を既に送っているのでそのまま通る。匿名ユーザーも `signInAnonymously()` でJWTを持つので問題なし）：
`/api/chat` `/api/score` `/api/checkout` `/api/claim-anon-sessions` `/api/debug-credits`

**`verify_jwt = false` が必須**（SNSクローラー・Stripeはトークンを持たない）：
`/api/og` `/api/meta` `/api/sitemap` `/api/stripe-webhook`

`supabase/config.toml` が今リポジトリに存在しない（`supabase/` は schema / migrations / seed のみ）ので新規作成になります。

### 3-6. Node API 依存の書き換え（全ファイル）

全ハンドラが `(req: IncomingMessage, res: ServerResponse)`。Denoは Fetch API の `Request`/`Response` なので、全部書き換えです：

| 現状 | Deno |
| --- | --- |
| `res.statusCode` / `res.setHeader` / `res.end` | `new Response(body, { status, headers })` |
| `readRequestBody`（`req.on('data')`、`request-helpers.ts:9-19`） | `await req.text()` |
| `withAccessLog` の `res.once('finish')`（`request-helpers.ts:64`） | Responseベースに再実装（ストリーミング完了の検知方法が変わる） |
| `result.pipeUIMessageStreamToResponse(res)`（`chat.ts:133`） | `result.toUIMessageStreamResponse()` |
| `process.env`（12箇所） | `Deno.env.get()` |
| `node:fs` / `process.cwd()`（`og.ts` `meta.ts`） | `static_files` ＋ `Deno.readFile` / `import.meta.url` |
| `stripe.webhooks.constructEvent`（`stripe-webhook.ts:36`、同期・Node crypto） | **`constructEventAsync`**（Web Crypto、Supabase公式サンプルもこちら） |

`PhaseTimer`（`request-helpers.ts:87-105`）は `Date.now()` だけなのでそのまま使えます。

**ストリーミングは追加の注意点あり**。Supabaseのトラブルシュートに「SSE/AIストリームが完了前に切れる」ケースが明記されていて、`EdgeRuntime.waitUntil()` で isolate を生かす対応が必要です（EarlyDrop対策）。`/api/chat` は直撃するので移行時の必須対応になります。

### 3-7. CORS（全エンドポイント）

今は同一オリジンの `/api/*` ですが、Supabaseは `*.supabase.co` の別オリジンになります。全エンドポイントに `OPTIONS` プリフライト対応 + `Access-Control-Allow-*` が必要です。

フロント側のURLも差し替え：
- `src/hooks/useChatSession.ts:36` `api: '/api/chat'`
- `src/hooks/useScoringSubmission.ts:41` `authFetch('/api/score')`
- `src/hooks/useCreditPurchase.ts:12` `postJson('/api/checkout')`
- `src/lib/anonTakeover.ts:66` `fetch('/api/claim-anon-sessions')`
- `src/pages/DebugSettingsPage.tsx:40` `postJson('/api/debug-credits')`

（Vercel rewriteでプロキシすれば同一オリジンのままCORS不要にできますが、それはVercelを残す前提です）

### 3-8. 開発 / CI / 監視

- **ローカル開発**：`npm start` = `vercel dev`、`playwright.config.ts:57` の `webServer.command` も `vercel dev`。→ `supabase functions serve` + Vite の2プロセス構成に変わり、E2Eのwebserver設定も書き換え
- **環境変数**：`vercel env pull` 前提の運用（`docs/tech-notes/vercel-dev-環境変数の読み込み.md`）→ `supabase secrets set`。副次的なメリットとして、**OIDCトークンが12時間で失効してローカルのBedrock呼び出しが死ぬ問題**（同tech-noteのトラブルシューティング項）は消えます
- **ログ**：Vercel Observability → Supabase Functions Logs。ここに**具体的な地雷**があります。公式Limitsに

  > Maximum log message length: **10,000 characters** / Log event threshold: **100 events per 10 seconds**

  `api/chat.ts:117-131` の `[chat-log]` は systemプロンプト（~2-3KB）＋全メッセージ＋assistant応答をJSONで1行に出しており、会話が伸びれば10,000文字を普通に超えます。`api/score.ts:216-225` の `[score] request:` も `chatMessages` / `memos` / `groundTruth` を丸ごと出すので同様です。**ログ設計の見直しがセット**になります
- `@vercel/analytics` / `@vercel/speed-insights`（`src/App.tsx:3-4`）はフロント側なので、Vercelホスティングを残す限り影響なし

---

## 4. まとめ：判断材料

issue本文の結論、

> 「Vercel Functionsを使うかSupabase Edge Functionsを使うか」より、**Supabase側にバックエンドを寄せるかどうか**で決めていい

には賛成です。その上で、調べた結果として言えることは：

**① 全面移行はコスパが悪い。** 3-3の通り静的ホスティング＋rewriteがSupabaseに無いので、**Vercel（か代替）は結局消えません**。Hobby商用利用問題（1つ目のコメント）が動機なら、これでは解決せず Vercel Pro は依然必要です。「Vercelをやめたい」なら、フロントを Cloudflare Pages 等へ移す話とセットで考える必要があります。

**② 性能面の旨みはほぼ無い。** 「DBと同居してレイテンシ削減」が期待できそうですが、AIQのボトルネックは Bedrock（`/api/score` で42秒）であって Supabase往復（数十ms）ではありません。`PhaseTimer` の内訳を見ても効果は誤差です。

**③ 部分移行なら意味がある。やるならこの順番。**

1. **`/api/stripe-webhook`** — 外部Webhook受け口、Vercel固有依存ゼロ、`verify_jwt = false` だけ。公式サンプルもある。**単独で移せてリスク最小**。`constructEvent` → `constructEventAsync` の1点だけ注意
2. **`/api/checkout` `/api/claim-anon-sessions` `/api/debug-credits`** — Supabaseを叩くだけ。CORSの手当てが要る程度
3. **`/api/chat` `/api/score`** — 3-1（OIDCを捨ててキー方式に戻す判断）が決まれば移せる。`/api/score` は150秒制約に対してストリーミング化を検討
4. **`/api/og` `/api/meta`** — **最後**。resvg WASM化・カスタムドメイン必須・ビルド成果物の同梱、と独立した難所が3つある
5. **`/api/sitemap`** — 移せるが `aiqtry.com/sitemap.xml` である必要があるので、rewrite（＝Vercelが残る）が前提

---

## 5. 未確認 / 要実測

判断を確定させるには以下が必要です：

- **`/api/og` の実CPU時間**（2秒に収まるか）— 現状Vercelでも未計測。`api/og.ts` に `PhaseTimer` を入れれば今のVercel上でも当たりが付く
- **WASM resvg でのメモリピーク**（256MBに対する余裕）
- **`/api/score` の本番 p95**（150秒に対する余裕）— `PhaseTimer` 導入は `plans/active/20260906-001-AI採点処理の高速化.md` に含まれているので、それが入れば分かる
- **Supabaseカスタムドメインの料金**（`/api/meta` を移す場合の前提コスト）

---
_Generated by [Claude Code](https://claude.ai/code)_


--- issue #1588 コメント 2 ---

「og だけAWSに出す」を調べていて、それより大きい話が見えたので追記します。**「Vercelをやめる」が目的なら、フロントも含めてAWSに寄せる案のほうが筋が良いかもしれません。** 代替案も含めて検討結果を残します。

---

## 1. なぜ「og だけ」ではなく「フロントごと」を検討する価値があるか

前回指摘した**最大の難所（3-1: Vercel OIDC → 恒久アクセスキーへの後退）が、AWS Lambdaなら逆に解決します**。

Lambdaは実行ロールに `bedrock:InvokeModel` を付けるだけで、**恒久キーが1本も要りません**。Lambdaが自動注入・自動ローテーションする一時クレデンシャルを使うので、Vercel OIDCと同等以上、Supabase案（恒久キーをSecretsに置く）より明確に安全です。同一アカウント・同一リージョン（us-east-1）なので Bedrock との往復も短くなります。

`/api/og` 単体で見ても、Supabase案の3つの難所がそのまま消えます：

| 難所（Supabase Edge Functions案） | AWS Lambda（Node.js）|
| --- | --- |
| resvg native → WASM 差し戻し | **native のまま**。`@resvg/resvg-js-linux-x64-gnu` が Amazon Linux の glibc と一致 |
| CPU 2秒 | **消える**。Lambdaはメモリ最大10GB・タイムアウト15分 |
| フォント9.2MB同梱（Docker必須） | **消える**。zip 250MBまで許容 |

コード変更も小さく済みます。`api/og.ts` は Bedrock・認証・クレジット消費を一切触っていない（`aws-credentials` を import しているのは `chat.ts` / `score.ts` のみ、`getAccessToken` / `consumeCredits` はヒット0件）ので、必要な環境変数は `SUPABASE_URL` / `SUPABASE_ANON_KEY` の2つだけ。描画ロジック400行以上は無変更で、書き換わるのは `res.setHeader` / `res.end` を Lambda proxy レスポンス形式に直す末尾30行程度です。

デプロイ経路もゼロからではありません。**GitHub Actions → AWS の OIDC federationは `.github/workflows/db-backup.yml` で既に動いています**（`aws-actions/configure-aws-credentials@v4` + `BACKUP_AWS_ROLE_ARN`）。ロールを1つ足すだけです。

`/api/meta` も一緒に持っていくべきです。Supabase案の2大難所（HTML返却にカスタムドメイン必須／`dist/spa.html` というビルド成果物の同梱）はLambdaだと問題になりません。og だけ出して meta をSupabaseに残すと、いちばん厄介な1本が残ります。

ここまでは「バックエンドをどこに置くか」の話です。が、この2本を動かすなら、**フロントとバックエンドを分けたまま2〜3プラットフォームを維持するコストと、フロントごとAWSに寄せて1プラットフォームにするコストを比べる価値がある**、というのが本題です。

---

## 2. フロントのホスティング：S3 + CloudFront は成立する。ただし難所はホスティングでなくルーティング

### 2-1. ファイル配置自体は素直

ビルド成果物（`npm run build` = `tsc -b && vite build && vite build --ssr ... && node scripts/prerender.mjs`）をそのまま S3 に置くだけです：

```
dist/
├── index.html          ← プリレンダ済みLP（/ 専用）
├── explore/index.html  ← プリレンダ済みexplore（/explore 専用）
├── spa.html            ← 空のSPAシェル（catch-all用）
├── assets/*            ← content-hash付き
└── favicon* robots.txt site.webmanifest logo*.png icons.svg（public/のコピー）
```

S3 は OAC（Origin Access Control）で private にし、CloudFront経由のみアクセス可にする構成が定石です。証明書はCloudFrontの制約でACMを `us-east-1` に作る必要があります。

### 2-2. 本当の難所：Vercelの「静的解決 > rewrite」という暗黙の優先順位が消える

`scripts/prerender.mjs` のコメントに、このプリレンダ機構がVercelの挙動に暗黙に依存していることが明記されています：

> プリレンダ済み静的ファイルは `api/meta.ts` を経由せず配信される（**Vercelの静的解決が rewrite より優先されるため**）

`/` と `/explore` が `/api/meta` に到達しないのは、Vercelが「静的ファイルが存在すればrewriteより優先する」を自動でやっているからです。**CloudFrontにこの優先順位はありません。** CloudFront Function（viewer-request）が「このパスはプリレンダ済み静的ファイルである」ことを明示的に知っている必要があります。つまり `prerender.mjs` の `ROUTES = ['/', '/explore']` と二重管理になります。ここがズレると、アーキテクチャ仕様書が明示的に警告している事故（「catch-all rewrite の destination を `/index.html` に戻してはいけない。全SPAルートにLPの本文が配られてしまう」）と同じ種類の問題が起きえます。しかも**見た目は動くので気づきにくい**のが厄介です。

対策としては、`prerender.mjs` が `dist/prerendered-routes.json` のようなマニフェストを吐き、デプロイ時にそれを CloudFront Function のコード（か KeyValueStore）へ機械的に反映する形にすれば、単一ソースに保てます。

### 2-3. UA判定：CloudFrontの罠と、その先にある朗報

まず罠から。AWS公式ドキュメントにこう明記されています：

> When a function changes the `uri` value, it **doesn't change the cache behavior** for the request or the origin that an origin request is sent to.

つまり「クローラーUAなら `/__og/*` にURIを書き換えて、`/__og/*` のビヘイビアをLambdaオリジンに向ける」という設計は動きません。ビヘイビア（＝どのオリジンに投げるか）はURI書き換え**前**の値で確定済みだからです。UAでオリジンを本当に振り分けたいなら origin-request の Lambda@Edge が必要になります。

ここで、**オリジンを1つに固定してUA判定をやめる**設計を考えると、tech-note（共有カードOG画像生成-OGP注入とルーティング.md §6）が抱えていた問題がむしろ解けます。tech-noteが `all` モード（全リクエストを `/api/meta` に通す）を採用できなかった理由：

> 同一URLがUAによって別のbodyを返すため `Vary: User-Agent` が必要になり、UAの種類は事実上無限なのでキャッシュヒット率はほぼゼロ

**CloudFrontならこれが解けます。** viewer-requestのCloudFront FunctionでUAを boolean に正規化し、その正規化ヘッダーをキャッシュポリシーに含める：

```js
// viewer-request CloudFront Function（イメージ）
var ua = (event.request.headers['user-agent']?.value || '').toLowerCase()
var isCrawler = /facebookexternalhit|twitterbot|slackbot|cardyb|googlebot|.../.test(ua)
event.request.headers['x-aiq-crawler'] = { value: isCrawler ? '1' : '0' }
```

これでキャッシュキーの次元が「UAの種類（事実上無限）」→「boolean 1個」に潰れます。`Vary: User-Agent` は不要、キャッシュ汚染もなし。Lambda側は生UAでなく `x-aiq-crawler` を読むだけでよく、`CRAWLER_UA` リスト（`scripts/ogp-mode.mjs` の `CRAWLER_UA`）はそのままCloudFront Function側に移植できます。**Vercelでは「正規化した値をキャッシュキーに入れる」手段が無かったので `all` を保留していましたが、CloudFrontでは素直に解けます。**

さらに、tech-noteが `all` モードの最大の懸念として挙げていた

> `/api/meta` の障害＝**サイト全体**の障害になる

も、CloudFrontのオリジングループ（プライマリ=meta Lambda、フェイルオーバー=S3の `/spa.html`、5xx検知でフェイルオーバー）で緩和できる見込みです（ここは実測・PoCが必要な部分です）。

保守的にいくなら、デフォルトをS3（`/spa.html`）にして、crawler判定時だけ origin-request の Lambda@Edge でオリジンを差し替える構成にすれば、**今のVercelの `crawler` モードをほぼそのまま再現**できます（通常ブラウザはFunctionを一切通らない）。Lambda@Edgeを使う分だけデプロイの複雑さは上がります。

### 2-4. ビヘイビア構成（案）

| パスパターン | オリジン | キャッシュ |
| --- | --- | --- |
| `/assets/*` | S3 | `max-age=31536000, immutable`（content-hash済み） |
| `/api/*` | Lambda | エンドポイント側の `Cache-Control` に従う |
| `/sitemap.xml` | Lambda | 1時間 |
| `/favicon*` `/robots.txt` `/site.webmanifest` `/*.png` `/icons.svg` | S3 | 中TTL |
| `*`（デフォルト） | meta Lambda | キャッシュキーに `x-aiq-crawler` を含める |

### 2-5. デプロイの非原子性（見落としやすい）

tech-noteはこの前提に乗っています：

> VercelのEdgeキャッシュはデプロイ単位で分離されるので、デプロイ時のCDN側の切り替えは自動

**`aws s3 sync` は原子的ではありません。** 同期中に「新しいHTML + まだ上がっていない新アセット」という不整合な組み合わせが配られる瞬間がありえます。順序を固定する必要があります：

1. `assets/` を先にアップロード（`--cache-control "max-age=31536000,immutable"`）
2. HTML を後でアップロード（`max-age=0, must-revalidate`）
3. 旧アセットは即 `--delete` しない（1〜2デプロイ分は残す）
4. HTMLパスだけ CloudFront invalidation（`/`、`/index.html`、`/explore/*`、`/spa.html`）

---

## 3. 失うもの（正直ここが一番痛い）

| | 影響 |
| --- | --- |
| **PRごとのプレビュー環境** | Vercelの目玉機能。`.github/workflows/sync-deploy-preview-branch.yml` の存在から見て今使っている。AWSで再現するにはPRごとに bucket prefix + distribution を組む自前実装が要り、**実務上いちばん重い損失** |
| `@vercel/analytics` / `@vercel/speed-insights` | `src/App.tsx:3-4`。CloudWatch RUM か Plausible 等への置き換えが必要 |
| `process.env.VERCEL_ENV` | `vite.config.ts:12` の `__APP_ENV__` の供給元を作り直し |
| `vercel dev` | `npm start` と `playwright.config.ts:57` の `webServer.command`。ローカル/E2Eの起動方法を作り直し |

---

## 4. 代替案：AWS完結より軽いかもしれない選択肢

「Vercelをやめる」が目的なら、AWS完結（S3+CloudFront+Lambda）は唯一解ではありません。2つ比較します。

### 4-1. Cloudflare Pages + Workers（フロント）＋ Lambda（AI/og/meta）

- **PRプレビューが標準装備**（Vercelと同じ体験がそのまま手に入る＝3の最大の損失が消える）
- UA判定は Workers で素直に書ける（CloudFront Functionの「URI書き換えはキャッシュキーに影響しない」という制約自体が存在しない）
- Bedrock呼び出し（`/api/chat` `/api/score`）だけ Lambda に残せば、**実行ロール方式（恒久キー不要）は維持できる**
- デメリットはプラットフォームが2つ（Cloudflare + AWS）に分かれること。ただし「Vercelをやめる」目的に対しては、**AWS完結よりトータル工数が小さくなる可能性が高い**と見ています（2-2〜2-3で挙げたルーティング移植の手間がまるごと減るため）

### 4-2. AWS Amplify Hosting

- CI/CD・PRプレビューが標準で付いてくるので魅力的に見えますが、**rewriteの条件分岐がcountryベースで、UAベースの判定ができません**。`crawler` モードに相当する構成が作れず、`all` 相当（全リクエストをFunction経由にする）一択になります
- tech-noteが `all` を保留したのはVercelでキャッシュキー正規化の手段が無かったからですが、Amplify Hostingでも同様の制約がある可能性が高く、要検証です

**現時点の見立て**: 「フロントもバックエンドも全部AWSに寄せて1プラットフォームに統一したい」なら 2章の S3+CloudFront+Lambda 案、「Vercelの開発体験（特にPRプレビュー）は手放したくないが認証基盤の恒久キー問題だけ解決したい」なら 4-1 の Cloudflare Pages + Workers + Lambda(Bedrock専用) 案、が候補になります。どちらもPoC前の机上検討である点は変わりません。

---

## 5. 未確認・要PoC（この追記分)

- **CloudFront FunctionのURI書き換えがキャッシュキーに実際どう影響するか** — 公式ドキュメントは「キャッシュビヘイビア（オリジン選択）は変わらない」としか明言しておらず、キャッシュキー自体への影響は曖昧。2-3で提案した「オリジン1つ＋ヘッダー正規化」構成はこの曖昧さに依存しない設計ですが、実際に組むなら最初に実測すべき箇所です
- **オリジングループのフェイルオーバー実効性**（meta Lambda障害時にS3へ落ちるか）
- **Cloudflare Workers から Bedrock（Lambda経由）への追加レイテンシ**（4-1案を取る場合)
- **PRプレビュー環境を自前実装するコスト**の具体的な見積もり（S3+CloudFront案を選ぶ場合、ここが工数の大半を占める可能性)

---
_Generated by [Claude Code](https://claude.ai/code)_
