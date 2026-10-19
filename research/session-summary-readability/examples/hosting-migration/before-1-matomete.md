> **改善前（再現）** 同じセッションを最後の依頼の手前まで再開し、「ここまでの調査をまとめて」と頼んだもの。
> この行より下は、AIが書いたままの本文である。

---

# #1588 Vercel 脱却の調査まとめ

## 0. 前提の訂正

- AIQ は **Vercel Edge Functions を使っていない**。`api/*.ts` の9本はすべて Node.js Serverless Functions（`runtime: 'edge'` 指定なし、`(req: IncomingMessage, res: ServerResponse)`）
- 実際の論点は「Node Serverless → 別プラットフォーム」。また Supabase に移しても**ルーティング層（rewrite / 静的ホスティング）が残るため Vercel は消えない**

## 1. 3つの選択肢の比較

| | A. Vercel Pro を払う | B. Supabase Edge Functions | C. AWS（S3+CloudFront+Lambda） |
| --- | --- | --- | --- |
| Bedrock 認証 | Vercel OIDC（現状維持） | **恒久アクセスキーに後退** | **Lambda 実行ロール（最良・恒久キー不要）** |
| `/api/chat` `/api/score` | 現状維持 | 動く（CPU 2秒は I/O 待ちなので当たらない） | 動く（chat のストリーミングは要確認） |
| `/api/og` | 現状維持 | **難所3つ**（resvg WASM化・CPU 2秒・フォント9.2MB同梱） | 素直（native resvg のまま、zip 250MB） |
| `/api/meta` | 現状維持 | **難所2つ**（HTML返却にカスタムドメイン必須・`dist/spa.html` 同梱） | 素直 |
| タイムアウト上限 | 800秒 | **150秒** | 15分 |
| ログ上限 | — | **10,000文字**（`[chat-log]` `[score]` が超える） | CloudWatch（実質問題なし） |
| ルーティング層 | Vercel | **無い → Vercel が残る** | CloudFront で組める |
| PR プレビュー | あり | あり（Vercel 側に残るので） | **失う** |
| 作業量 | ゼロ | 大 | 大 |

**結論**: 「Vercel をやめる」が目的なら B（Supabase）は目的を達成しない。やるなら C（AWS）か、後述の Cloudflare 案。単にコストの問題なら A が最も安い。

## 2. Supabase 移行の主な難所（issue コメント済み）

1. **Vercel OIDC → 恒久アクセスキーへの後退（最大）**: `docs/tech-notes/vercel-aws-oidc連携.md` で意図的に避けた方式を巻き戻すことになる。署名自体は `@ai-sdk/amazon-bedrock`（aws4fetch で SigV4）が Deno でも動くので、問題は資格情報の出所
2. **rewrite の代替が無い**: `/problem/:id` の UA 判定 rewrite（OGP）を移せない → Vercel が残る
3. **`/api/meta`**: HTML はカスタムドメインでないと `text/plain` に書き換えられる
4. **`/api/og`**: resvg native→WASM（tech-note で避けた判断の巻き戻し）、CPU 2秒、フォント 9.2MB 同梱（Docker 必須）
5. **ログ 10,000 文字上限**
- 部分移行するなら `/api/stripe-webhook` から

## 3. `/api/og` だけ AWS Lambda に出す案

- og は全エンドポイントで最も独立している（Bedrock なし・認証/クレジットなし・env は `SUPABASE_URL` / `SUPABASE_ANON_KEY` のみ）
- Lambda なら Supabase での難所3つがすべて消える。描画ロジックは無変更で、末尾のレスポンス処理（約30行）を Lambda proxy 形式に直すだけ
- GitHub Actions → AWS の OIDC は `db-backup.yml` で既に動いている
- `vercel.json` の rewrite の destination を Function URL に向ければ URL も `og:image` も変わらない
- **ただし「og だけ」は筋が悪い**: meta も同様に Lambda で素直に動くので一緒に出すべき。og 1本のために3プラットフォーム運用（Vercel+Supabase+AWS）になるのは重い

## 4. AWS 完結案（S3 + CloudFront + Lambda）

### ホスティング
- `dist/` をそのまま S3（OAC で private）、ACM 証明書は us-east-1
- **難所はホスティングではなくルーティング（`vercel.json` の移植）**

### 移植すべき3点
1. **プリレンダ済みルートの静的優先**: Vercel は「静的ファイル > rewrite」を自動でやっているが CloudFront には無い。`/` → `index.html`、`/explore` → `explore/index.html` を明示する必要があり、`prerender.mjs` の `ROUTES` と二重管理になる。間違えると空シェル or 全ルートに LP の DOM が配られる（気づきにくい）
   - 対策: `prerender.mjs` が `dist/prerendered-routes.json` を出力し、デプロイ時に CloudFront Function / KeyValueStore へ流し込む
2. **UA 判定**: CloudFront Function で URI を書き換えても**オリジン（ビヘイビア）は変わらない**ため、「crawler なら Lambda へ」は viewer-request だけでは組めない
   - 推奨: オリジンを1つにし、viewer-request で UA を `x-aiq-crawler: 0/1` に正規化してキャッシュキーに入れる → キャッシュキーの次元が ∞→2。tech-note §6 で `all` モードを諦めた理由（`Vary: User-Agent` でヒット率ゼロ）が解消される
   - meta Lambda 障害＝サイト全体障害の懸念は、オリジングループ（5xx で S3 の `spa.html` にフェイルオーバー）で緩和できる見込み
   - 保守的な代替: デフォルトは S3、crawler のときだけ Lambda@Edge（origin-request）でオリジン差し替え（現行 `crawler` モードの忠実な再現、デプロイは重くなる）
3. **catch-all → `spa.html`**

### ビヘイビア構成案
| パス | オリジン | キャッシュ |
| --- | --- | --- |
| `/assets/*` | S3 | 1年 immutable |
| `/api/*` | Lambda | エンドポイントの `Cache-Control` |
| `/sitemap.xml` | Lambda | 1時間 |
| favicon / robots.txt / webmanifest / png / svg | S3 | 中 TTL |
| `*`（デフォルト） | meta Lambda | キーに `x-aiq-crawler` |

### デプロイ
`s3 sync` は原子的でないので順序を固定: ① `assets/` を先に ② HTML を後で（`max-age=0`）③ 旧アセットは即削除しない ④ HTML だけ invalidation

### 失うもの
| | 影響 |
| --- | --- |
| **PR プレビュー環境** | 実務上いちばん重い損失（`sync-deploy-preview-branch.yml` で使用中） |
| `@vercel/analytics` / `speed-insights` | `src/App.tsx:3-4`、置き換えが必要 |
| `VERCEL_ENV` | `vite.config.ts:12` の `__APP_ENV__` の供給元 |
| `vercel dev` | `npm start` と `playwright.config.ts:57` の起動方法を作り直し |

## 5. その他の代替案

- **Cloudflare Pages + Workers（フロント）＋ Lambda（Bedrock 系）**: PR プレビュー標準装備、UA 判定は Workers で簡単、Bedrock は実行ロールのまま。「Vercel をやめる」目的なら AWS 完結より工数が小さい可能性が高い（プラットフォームは2つ）
- **AWS Amplify Hosting**: PR プレビューありだが rewrite で UA 判定ができず、`all` モードしか選べない

## 6. 未検証（PoC が必要な点）

- `/api/og` の実 CPU 時間（Supabase の 2秒制限に収まるか。現状 Vercel でも未計測）
- `/api/og` の PNG サイズ（Lambda BUFFERED は 6MB 上限、base64 で 1.33 倍）
- `/api/chat` のストリーミング: AI SDK の `pipeUIMessageStreamToResponse` と `awslambda.streamifyResponse` の組み合わせ
- CloudFront Function の URI 書き換えがキャッシュキーに入るか（公式ドキュメントの記述があいまい。推奨構成はこれに依存しない）
- オリジングループによる meta Lambda のフェイルオーバー
- コールドスタート時間（フォント 9.2MB の読み込み）

## 7. 推奨

1. **目的の確認が先**: Hobby 商用利用（規約）やコストの問題なら、A（Pro）が最も安い。B（Supabase）は Vercel が残るので解決にならない
2. Vercel 脱却が必須なら **Cloudflare Pages + Lambda** か **AWS 完結**。どちらでも Bedrock は Lambda 実行ロールになり、セキュリティは現状と同等以上
3. 着手するなら、独立性が高くリスクの小さい `/api/og` + `/api/meta` の Lambda 化 PoC から（rewrite 先を変えるだけで Vercel 上で試せる）

## 出典
- [Vercel Functions Limits](https://vercel.com/docs/functions/limitations)
- [Supabase Edge Functions Limits](https://supabase.com/docs/guides/functions/limits)
- [Lambda response streaming](https://docs.aws.amazon.com/lambda/latest/dg/configuration-response-streaming.html)
- [CloudFront Functions event structure](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/functions-event-structure.html)
- [CloudFront cache key](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/understanding-the-cache-key.html)
