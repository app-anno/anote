# タスク005：予約失敗エラーの修正（referralCodeフィールド削除）

**プロジェクト:** ShipFront
**ステータス:** ✅ 完了
**完了日:** 2026-01-20
**ブランチ:** feature/reservation-referral-code

---

## 概要

予約確認画面で「予約に失敗しました」エラーが発生する問題を修正。原因は予約リクエストに不要な `referralCode` フィールドを含めていたこと。

---

## 実装前 → 実装後

```mermaid
graph LR
    subgraph Before["😕 実装前"]
        A[予約リクエストに<br>referralCodeを含める]
        B[GraphQLエラー発生<br>Field is not defined]
        C[予約失敗]
    end

    subgraph After["✅ 実装後"]
        D[予約リクエストから<br>referralCode削除]
        E[execSendShareKeysで<br>別途送信]
        F[予約成功]
    end

    A --> D
    B --> E
    C --> F
```

---

## 原因分析

### GraphQLエラー内容

```json
{
  "message": "Variable $input ... was provided invalid value for params.referralCode
              (Field is not defined on Types_Inputs__ShipReservationType)",
  "problems": [{
    "path": ["params", "referralCode"],
    "explanation": "Field is not defined on Types_Inputs__ShipReservationType"
  }]
}
```

### 紹介コードの正しい送信フロー

```mermaid
flowchart TD
    A[URLパラメータ ?sk=XXXXX] --> B[Cookieに保存]
    B --> C[予約確認画面で入力/表示]
    C --> D{予約ボタン押下}
    D --> E[execSendShareKeys<br>createAmbassadorEventReferralClicks mutation]
    D --> F[createShipReservation<br>予約リクエスト]
    E --> G[紹介コード送信完了]
    F --> H[予約作成完了]

    style F fill:#90EE90
    style E fill:#90EE90
```

**ポイント**:
- 紹介コードは `execSendShareKeys` で別途送信される
- 予約API (`createShipReservation`) には紹介コードを含めてはいけない
- バックエンドで日次バッチにより account_id ベースで照合・スコア付与される

---

## 実装内容

### 1. transformers/index.ts から referralCode を削除

**変更前:**
```typescript
return {
  // ...
  inquiry: createStorageResult.inquiry ?? null,
  consumePoints: createStorageResult.consumePoints ?? null,
  referralCode: createStorageResult.referralCode ?? null, // ❌ 不要
};
```

**変更後:**
```typescript
return {
  // ...
  inquiry: createStorageResult.inquiry ?? null,
  consumePoints: createStorageResult.consumePoints ?? null,
  // referralCode は execSendShareKeys で別途送信するため、ここでは送信しない
};
```

### 2. types/request.ts から referralCode プロパティを削除

**変更前:**
```typescript
export type CreateReservationRequest = {
  // ...
  consumePoints: number | null;
  /** 紹介コード */
  referralCode: string | null;  // ❌ 不要
};
```

**変更後:**
```typescript
export type CreateReservationRequest = {
  // ...
  consumePoints: number | null;
  // referralCode は execSendShareKeys で別途送信するため、予約リクエストには含めない
};
```

### 3. テストファイルの修正

テストデータからも `referralCode` を削除。

---

## 変更ファイル一覧

| ファイル | 変更種別 | 変更内容 |
|---------|---------|----------|
| `src/features/reserve/hooks/use-create-ship-reservation/transformers/index.ts` | 修正 | `referralCode` フィールドを削除 |
| `src/features/reserve/hooks/use-create-ship-reservation/types/request.ts` | 修正 | `referralCode` プロパティを削除 |
| `src/features/reserve/hooks/use-create-ship-reservation/__tests__/error-handlers.test.ts` | 修正 | テストデータから `referralCode` を削除（2箇所） |

---

## 紹介コード機能の全体フロー（参考）

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant Browser as ブラウザ
    participant Frontend as フロントエンド
    participant Backend as バックエンド

    Note over User,Backend: 紹介コード入力フロー

    User->>Browser: URLアクセス (?sk=XXXXX)
    Browser->>Frontend: Cookieに保存
    User->>Frontend: 予約フォーム入力
    User->>Frontend: 予約ボタン押下

    Frontend->>Backend: createAmbassadorEventReferralClicks<br>(紹介コード送信)
    Backend-->>Frontend: 送信完了

    Frontend->>Backend: createShipReservation<br>(予約作成 ※referralCode含まない)
    Backend-->>Frontend: 予約完了

    Note over Backend: 日次バッチで<br>account_idベース照合
```

---

## 動作確認

- [x] TypeScript型チェック通過 (`npm run ts:test`)
- [ ] 紹介コードなしで予約が成功することを確認（ブラウザ確認待ち）
- [ ] 紹介コード入力ありで予約が成功することを確認（ブラウザ確認待ち）
- [ ] 予約完了画面に遷移することを確認（ブラウザ確認待ち）

---

## 学び・メモ

- GraphQLのバックエンド型定義に存在しないフィールドを送信するとエラーになる
- 紹介コードのような補助的な情報は、メインのAPIとは別のmutationで送信するアーキテクチャになっている場合がある
- 機能追加時は、既存のデータフローを十分に理解してから実装することが重要
