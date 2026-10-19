> **改善後** 同じ時点で「ここまでの調査を、主目的に沿って構成を組み直してまとめて」と頼んだもの。
> この行より下は、AIが書いたままの本文である。

---

# #1588 Vercel 移行検討：調査まとめ

## 0. 結論

- **主目的は「Vercel Hobby プランの商用利用問題の解消（＝Vercel をやめる／払う）」**。Supabase Edge Functions への移行はその手段の 1 案にすぎない
- **Supabase 案では主目的を達成できない**。Supabase には静的ホスティングもホスト全体のルーティングも無いため、移行してもフロント＋ rewrite のために Vercel が残る
- しかも Supabase 案はセキュリティ（Bedrock 認証が恒久キーに後退）と機能（`/api/og` `/api/meta`）の両面で後退する
- 選択肢は実質 3 つ：
  1. **Vercel Pro を払う** — 作業ゼロ。最も確実
  2. **Cloudflare Pages + Workers（フロント）＋ AWS Lambda（API）** — 脱 Vercel の中で最も工数が小さい見込み。PR プレビューを維持できる
  3. **AWS 完結（S3 + CloudFront + Lambda）** — 技術的には最もきれい（実行ロール認証、UA 判定のキャッシュ問題も解ける）が、PR プレビュー喪失が痛い
- **推奨：まず 1 で商用利用問題を即解消。脱 Vercel が別途必要になったら 2 を第一候補に PoC**

---

## 1. 前提の訂正

- AIQ は **Vercel Edge Functions を使っていない**。`api/*.ts` 全 9 本に `runtime: 'edge'` 指定はなく、すべて `(req: IncomingMessage, res: ServerResponse)` の **Node.js Serverless Functions**
- よって「Edge → Edge」の横移動ではなく、Supabase 案は「**Node Serverless → Deno Edge**」の移植になる
- Function 数 9 本はどのプランでも余裕（Pro の上限は 500。1000 は Team）

## 2. 判断軸

| 軸 | 何を見るか |
| --- | --- |
| 主目的の達成 | Vercel をやめられるか／商用利用条件を満たせるか |
| Bedrock 認証 | 恒久アクセスキーを持たずに済むか（`docs/tech-notes/vercel-aws-oidc連携.md` で意図的に選んだ方針） |
| ルーティング | `vercel.json` の rewrite（プリレンダ優先・UA 判定・catch-all → `spa.html`）を移植できるか |
| 実行制約 | タイムアウト（`/api/score` 実測 42 秒）、CPU、パッケージサイズ |
| 開発体験 | PR プレビュー、ローカル／E2E（`vercel dev`）、Analytics |
| 運用コスト | プラットフォーム数、デプロイ系統 |

## 3. 選択肢比較

| | A. Vercel Pro | B. Supabase に寄せる | C. AWS 完結 | D. Cloudflare Pages + Lambda |
| --- | --- | --- | --- | --- |
| **Vercel をやめられるか** | ×（払って継続） | **×（Vercel が残る）** | ○ | ○ |
| Bedrock 認証 | OIDC（現状） | **恒久キーに後退** | 実行ロール（最良） | 実行ロール（Lambda 側） |
| `/api/og` | 現状維持 | **難所 3 つ** | 素直（Node のまま） | 素直（Lambda） |
| `/api/meta` | 現状維持 | **難所 2 つ** | 素直 | Workers or Lambda |
| タイムアウト上限 | 800 秒 | **150 秒** | 15 分 | 15 分（Lambda） |
| UA 判定ルーティング | 現状（`crawler` モード） | **不可** | CloudFront Function で可、キャッシュ問題も解ける | Workers で自明 |
| PR プレビュー | あり | あり（Vercel 残存） | **喪失**（自作が必要） | あり（Pages 標準） |
| プラットフォーム数 | 2 | 2（Vercel 残存） | 2（AWS + Supabase DB） | 3 |
| 作業量 | ゼロ | 大 | 大 | 中〜大 |

---

## 4. B. Supabase 案の問題点（不採用理由）

### 4-1. 主目的を満たさない
- OGP は `/problem/:id` の URL のまま UA 判定 rewrite する設計。Supabase にはホスト全体のルーティングが無く、**Vercel（または他の CDN）が残る**

### 4-2. Bedrock 認証の後退（最大の難所）
- Supabase にワークロード ID フェデレーションが無く、Vercel OIDC → **恒久アクセスキーを Secrets に保存**へ巻き戻しになる
- 署名自体は問題ない（`@ai-sdk/amazon-bedrock` は `aws4fetch` で SigV4 を自前署名するので Deno で動く）。難所は資格情報の出所

### 4-3. `/api/og`：難所 3 つ
- resvg native → WASM（tech-note で意図的に避けた判断の巻き戻し）
- CPU 2 秒制限との勝負（現状の実 CPU 時間は未計測）
- フォント 9.2MB の同梱（Docker 必須、パッケージ上限 20MB）

### 4-4. `/api/meta`：難所 2 つ
- 公式 Limits：HTML は**カスタムドメインでのみ配信可**（それ以外は `text/plain` に書き換え）
- ビルド成果物 `dist/spa.html` の同梱が必要

### 4-5. その他
- ログ上限 10,000 文字。`[chat-log]` `[score] request:` が超える
- `/api/chat` `/api/score` は Bedrock 待ちが I/O なので CPU 2 秒には当たらない（issue 本文の見立ては正しい）

---

## 5. 脱 Vercel する場合の設計（C / D 共通の API 層：AWS Lambda）

### 5-1. Bedrock 認証が一番きれいになる
- Lambda 実行ロールに `bedrock:InvokeModel` を付けるだけ。**恒久キー不要**、一時クレデンシャルは自動ローテーション
- Bedrock と同一アカウント・同一リージョン（us-east-1）
- タイムアウト 15 分で `/api/score` の余裕も減らない

### 5-2. `/api/og` `/api/meta` は Lambda だと素直
- `/api/og` は最も独立したエンドポイント（Bedrock なし、認証・クレジットなし、env は `SUPABASE_URL` / `SUPABASE_ANON_KEY` のみ）
- resvg は native のまま（`@resvg/resvg-js-linux-x64-gnu` が Amazon Linux の glibc と一致）、zip 250MB で フォント同梱も問題なし
- 描画ロジックは無変更。書き換えは末尾のレスポンス生成（`{ statusCode, headers, body, isBase64Encoded }`）30 行程度
- `/api/meta` も Function URL なら Content-Type 自由、`dist/spa.html` は zip に入れればよい
- **og だけを AWS に出すのは非推奨**（meta が厄介なまま残る＋プラットフォームが 3 系統になる）

### 5-3. デプロイ経路
- GitHub Actions → AWS の OIDC は既に稼働中（`.github/workflows/db-backup.yml`）。ロールを足すだけ

---

## 6. C. AWS 完結案のフロント（S3 + CloudFront）

### 6-1. ホスティング自体は素直
- `dist/` をそのまま S3（OAC で private）。ACM 証明書は us-east-1 に作成

### 6-2. 難所はルーティングの移植
1. **プリレンダ済みルートの静的優先**
   - Vercel は「静的ファイル > rewrite」を自動でやっているが CloudFront には無い
   - CloudFront Function に `/` → `/index.html`、`/explore` → `/explore/index.html` を明示する必要があり、`scripts/prerender.mjs` の `ROUTES` と二重管理になる
   - ズレると「LP の DOM が全 SPA ルートに配られる」事故（アーキテクチャ仕様が警告済み）が**見た目上動いたまま**起きる
   - 対策：`prerender.mjs` に `dist/prerendered-routes.json` を出力させ、デプロイ時に Function / KeyValueStore に流し込む
2. **UA 判定**
   - 罠：viewer-request で URI を書き換えても**キャッシュビヘイビア（オリジン）は変わらない**。「crawler なら `/__og/*` に書き換えて別オリジン」は動かない
   - 推奨：オリジンを 1 つにし、CloudFront Function で UA を `x-aiq-crawler: 0|1` に正規化してキャッシュポリシーに含める
   - これにより tech-note §6 が `all` モードを諦めた理由（`Vary: User-Agent` でキャッシュヒット率ほぼゼロ）が**解消する**
   - `all` モードの懸念「meta 障害＝サイト全体障害」はオリジングループ（Lambda → S3 `/spa.html` にフェイルオーバー）で緩和できる見込み
   - 保守的に行くなら、デフォルトを S3 にして crawler のみ origin-request の Lambda@Edge でオリジン差し替え（現状の `crawler` モードの完全な写し。デプロイは重くなる）
3. **catch-all → `spa.html`**

### 6-3. ビヘイビア構成案

| パスパターン | オリジン | キャッシュ |
| --- | --- | --- |
| `/assets/*` | S3 | `max-age=31536000, immutable` |
| `/api/*` | Lambda | エンドポイント側の `Cache-Control` |
| `/sitemap.xml` | Lambda | 1 時間 |
| `/favicon*` `/robots.txt` `/site.webmanifest` `/*.png` `/icons.svg` | S3 | 中 TTL |
| `*`（デフォルト） | meta Lambda | キャッシュキーに `x-aiq-crawler` |

### 6-4. デプロイの非原子性
Vercel はデプロイ単位でキャッシュが分離されるが、`aws s3 sync` は原子的でない。順序を固定する：
1. `assets/` を先にアップロード（immutable）
2. HTML を後でアップロード（`max-age=0, must-revalidate`）
3. 旧アセットは即削除しない（1〜2 デプロイ分残す）
4. HTML のみ invalidation（`/`、`/index.html`、`/explore/*`、`/spa.html`）

### 6-5. 失うもの

| 項目 | 影響 |
| --- | --- |
| **PR プレビュー環境** | `sync-deploy-preview-branch.yml` で利用中。PR ごとに prefix + distribution を自作する必要があり、**実務上最大の損失** |
| `@vercel/analytics` / `@vercel/speed-insights` | `src/App.tsx:3-4`。CloudWatch RUM / Plausible 等に置き換え |
| `process.env.VERCEL_ENV` | `vite.config.ts:12` の `__APP_ENV__` の供給元を変更 |
| `vercel dev` | `npm start` と `playwright.config.ts:57`。ローカル／E2E 起動を作り直し |

---

## 7. D. Cloudflare Pages + Lambda 案

- Pages は **PR プレビュー標準装備**、UA 判定は Workers で素直に書ける
- Bedrock を叩く API は Lambda に置けば実行ロール認証を維持できる
- C の最大の損失（PR プレビュー）を回避でき、**脱 Vercel の中では工数が最小になる可能性が高い**
- 代償はプラットフォームが 3 つ（Cloudflare + AWS + Supabase DB）になること
- 参考：AWS Amplify Hosting は PR プレビューはあるが rewrite 条件が country ベースで **UA 判定不可**（`all` モード一択）

---

## 8. 推奨する進め方

1. **短期**：Vercel Pro に切り替えて商用利用問題を解消（作業ゼロ、リスクゼロ）
2. **Supabase Edge Functions 移行は見送り**（主目的を満たさず、認証・og・meta が後退）
3. **脱 Vercel が必要になった場合**：
   - 第一候補 D（Cloudflare Pages + Lambda）、次点 C（AWS 完結）
   - 着手順は依存の少ない順：`/api/og` + `/api/meta` → `/api/stripe-webhook` 等 → `/api/chat` `/api/score`（ストリーミング検証後）→ フロント切り替え

## 9. 要 PoC・未確認事項

| 項目 | 内容 |
| --- | --- |
| `/api/og` の CPU 時間 | 現状 Vercel でも未計測。Supabase 案の可否はこれ次第（Lambda 案では無関係） |
| `/api/og` の PNG サイズ | Lambda BUFFERED は 6MB 上限、base64 で 1.33 倍。`?debug` の `pngBytes` で確認 |
| `/api/chat` のストリーミング | AI SDK の `pipeUIMessageStreamToResponse`（Node `ServerResponse` 前提）と `awslambda.streamifyResponse` の噛み合わせ。最初 6MB 以降は 2MBps 制限 |
| CloudFront の URI 書き換えとキャッシュキー | 公式ドキュメントの記述が曖昧。推奨構成（ヘッダー正規化）はこれに依存しないが実測すべき |
| オリジングループのフェイルオーバー | Lambda 5xx → S3 `/spa.html` が意図どおり動くか |
| コールドスタート | フォント 9.2MB 読み込みの実測値なし（現状より悪化はしない見込み） |

## Sources

- [Vercel Functions Limits](https://vercel.com/docs/functions/limitations)
- [Supabase Edge Functions Limits](https://supabase.com/docs/guides/functions/limits)
- [Lambda response streaming](https://docs.aws.amazon.com/lambda/latest/dg/configuration-response-streaming.html)
- [Lambda Function URL streaming](https://docs.aws.amazon.com/lambda/latest/dg/config-rs-invoke-furls.html)
- [CloudFront Functions event structure](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/functions-event-structure.html)
- [CloudFront: Understand the cache key](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/understanding-the-cache-key.html)
- [CloudFront: Cache content based on request headers](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/header-caching.html)
- [@resvg/resvg-js-linux-x64-gnu](https://www.npmjs.com/package/@resvg/resvg-js-linux-x64-gnu)
