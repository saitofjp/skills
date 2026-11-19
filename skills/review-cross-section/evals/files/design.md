# 市民スポーツ施設 予約システム 設計書 v0.3

仕様書 v0.9 に対応する設計。

## 1. 構成

- Web アプリ（SPA）と API サーバー、PostgreSQL。
- 決済は外部決済サービスを使い、完了は Webhook で受け取る。
- メールは外部のメール配信サービスで送る。

## 2. データ

### reservations

| 列 | 型 | 説明 |
|---|---|---|
| id | uuid | |
| facility_id | uuid | |
| user_id | uuid | 予約した利用者（団体予約では代表者） |
| date | date | 利用日 |
| slot | int | 時間枠（0〜5） |
| status | enum | `tentative` / `paid` / `used` / `cancelled` / `waiting` |
| created_at | timestamp | |

- 一つの (facility_id, date, slot) に `tentative` または `paid` の予約は1件だけとする（アプリで確認する）。

### group_members

| 列 | 型 | 説明 |
|---|---|---|
| reservation_id | uuid | |
| name | text | メンバーの氏名 |

## 3. API

| メソッド | パス | 呼べる人 | 内容 |
|---|---|---|---|
| POST | /reservations | 利用者 | 予約を作る。枠が埋まっていれば `waiting` で作る |
| DELETE | /reservations/{id} | 利用者（本人のみ） | キャンセルする |
| POST | /reservations/{id}/payment | 利用者（本人のみ） | 決済を始める |
| POST | /webhooks/payment | 決済サービス | 決済完了の通知を受けて `paid` にする |
| GET | /facilities/{id}/reservations | 施設スタッフ | 予約一覧 |
| POST | /facilities/{id}/closures | 施設スタッフ | 臨時休館を登録する |
| POST | /reservations/{id}/members | 利用者（代表者） | メンバーを追加する |

## 4. 処理

### 4.1 予約の作成

1. 同じ枠に `tentative` か `paid` の予約があるかを SELECT で調べる。
2. 無ければ `tentative` で INSERT する。あれば `waiting` で INSERT する。

### 4.2 仮予約の失効

- 5分ごとのバッチで、`created_at` から30分を過ぎた `tentative` の予約を `cancelled` にする。

### 4.3 キャンセル

- DELETE /reservations/{id} で予約を `cancelled` にする。`paid` なら決済サービスの返金 API を呼ぶ。
- 同じ処理の中で、その枠の `waiting` のうち `created_at` が最も古いものを `tentative` にし、メールを送る。

### 4.4 臨時休館

- POST /facilities/{id}/closures の処理の中で、その日の予約を順に `cancelled` にし、`paid` のものは一件ずつ返金 API を呼び、メールを送る。

### 4.5 決済完了

- Webhook を受けたら、対象の予約を `paid` にする。
