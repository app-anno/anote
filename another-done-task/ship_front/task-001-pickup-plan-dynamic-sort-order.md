# タスク001：ピックアッププランの動的並び順対応

**ステータス:** 未着手
**優先度:** 高
**ブランチ:** TBD
**壁打ち日:** 2026-01-08

---

## 概要

TOPページのピックアッププランUIの並び順を、フロント側の固定配列から、バックエンドAPIの`sortOrder`に基づく動的な並び順に変更する。

---

## 背景

### 現状の問題

- フロント側で`PICKUP_PLAN_KEYS`という固定配列で並び順を制御している
- 並び順を変更するたびにフロントのデプロイが必要
- バックエンドで管理画面から並び順を変更できるようになったが、フロントが対応していない

### バックエンドの変更（PR #13006 で対応済み）

- `PickupPlan`モデルに`sort_order`と`position`フィールドを追加
- GraphQL APIで`sortOrder`と`position`を返すように変更
- 管理画面から並び順を変更可能に
- APIレスポンスは`position → sortOrder → id`順でソート済み

### 設計方針（壁打ちで確定）

| 方針 | 説明 |
|------|------|
| **全件取得** | `keys: []`で全件取得し、APIのソート順をそのまま使う |
| **key判定** | `key === "popular"`のときだけリスト表示、それ以外はカルーセル表示 |
| **position判定** | `position === "top"`のプランのみ上部エリアに表示 |
| **コンポーネント構成維持** | 2つのコンポーネント（RecommendPickupPlan / PopularPlanRanking）で別々にAPI呼び出し |

---

## 事前調査で把握した既存実装

| ファイル | 内容 | 本タスクとの関連 |
|---------|------|-----------------|
| `src/components/ui-elements/recommend-pick-up-plan/index.tsx` | ピックアッププランのメインコンポーネント | **主な変更対象** |
| `src/apis/pickup-plans/get-pickup-plans-unified.gql` | GraphQLクエリ定義 | `sortOrder`と`position`フィールドを追加 |
| `src/components/ui-elements/recommend-pick-up-plan/pickup-plan-section/index.tsx` | 各セクションのカルーセル表示 | 変更なし |
| `src/app/(home)/_components/popular-plan-ranking/index.tsx` | 人気ランキング（リスト表示） | 変更なし |
| `src/app/(home)/page.tsx` | トップページ | 変更なし |

---

## 変更一覧

### 1. GraphQLクエリの変更（`get-pickup-plans-unified.gql`）

**変更内容**: `sortOrder`と`position`フィールドを追加

```graphql
# Before
query GetPickupPlans($keys: [String!]!) {
  pickupPlans(keys: $keys) {
    name
    key
    seeMoreUrl
    shipReservationPlanVariations { ... }
  }
}

# After
query GetPickupPlans($keys: [String!]!) {
  pickupPlans(keys: $keys) {
    name
    key
    seeMoreUrl
    sortOrder    # 追加
    position     # 追加
    shipReservationPlanVariations { ... }
  }
}
```

**理由**: バックエンドで追加された並び順情報をフロントで取得するため

---

### 2. RecommendPickupPlanコンポーネントの変更

**変更内容**: 固定配列を廃止し、APIのソート順を使用

```typescript
// Before
const PICKUP_PLAN_KEYS = [
  "has_coupon",
  "top",
  "middle",
  "bottom",
  "kanto_short_time",
  "kansai_short_time",
  "chubu_short_time",
  "kyushu_short_time",
  "okinawa_short_time",
];

export async function RecommendPickupPlan() {
  const { data: pickupPlansData } = await getClient().query({
    query: GetPickupPlansDocument,
    variables: {
      keys: PICKUP_PLAN_KEYS,
    },
  });

  const plansByKey = pickupPlansData.pickupPlans.reduce(
    (acc, plan) => {
      acc[plan.key] = plan;
      return acc;
    },
    {} as Record<string, ...>,
  );

  return (
    <div>
      {PICKUP_PLAN_KEYS.map((key) => {
        const pickupPlan = plansByKey[key];
        if (!pickupPlan) return null;
        return <PickupPlanSection key={key} pickupPlan={pickupPlan} />;
      })}
    </div>
  );
}

// After
export async function RecommendPickupPlan() {
  const { data: pickupPlansData } = await getClient().query({
    query: GetPickupPlansDocument,
    variables: {
      keys: [],  // 全件取得
    },
  });

  // position: "top" かつ key !== "popular" のプランのみ表示
  const topPlans = pickupPlansData.pickupPlans.filter(
    (plan) => plan.position === "top" && plan.key !== "popular"
  );

  return (
    <div className="tw-flex tw-flex-col tw-gap-spacer_10 md:tw-gap-spacer_10_px tw-overflow-hidden">
      {topPlans.map((pickupPlan) => (
        <PickupPlanSection key={pickupPlan.key} pickupPlan={pickupPlan} />
      ))}
    </div>
  );
}
```

**理由**:
- APIが`sortOrder`順でソート済みのデータを返すため、そのまま表示すればOK
- `popular`は別コンポーネントで表示するため除外
- `position: "top"`のみを上部エリアに表示

---

### 3. codegen実行

**変更内容**: GraphQLスキーマの変更を反映

```bash
cd ship_front
npm run codegen
```

**理由**: `sortOrder`と`position`の型を生成するため

---

## 実装手順

### Phase 1: GraphQLクエリ更新

- [x] `get-pickup-plans-unified.gql`に`sortOrder`と`position`を追加（完了済み）
- [ ] `npm run codegen`を実行して型を更新

### Phase 2: RecommendPickupPlanコンポーネント更新

- [ ] `PICKUP_PLAN_KEYS`定数を削除
- [ ] `keys: []`で全件取得に変更
- [ ] `position === "top"` かつ `key !== "popular"` でフィルタリング
- [ ] `plansByKey`のreduceロジックを削除（不要になるため）

### Phase 3: 動作確認

- [ ] 開発環境で表示確認
- [ ] 管理画面で並び順を変更し、フロントに反映されることを確認
- [ ] `popular`が上部エリアに表示されないことを確認

---

## 関連ファイル

### 変更対象

| ファイル | 変更内容 |
|---------|----------|
| `src/apis/pickup-plans/get-pickup-plans-unified.gql` | `sortOrder`と`position`フィールドを追加 |
| `src/components/ui-elements/recommend-pick-up-plan/index.tsx` | 固定配列廃止、API順で表示 |
| `src/common/libs/graphql/graphql.ts` | codegen自動生成（型更新） |
| `src/common/libs/graphql/gql.ts` | codegen自動生成 |

### 参照のみ（変更なし）

| ファイル | 参照理由 |
|---------|----------|
| `src/components/ui-elements/recommend-pick-up-plan/pickup-plan-section/index.tsx` | 既存のカルーセル表示ロジック確認 |
| `src/app/(home)/_components/popular-plan-ranking/index.tsx` | popularの表示ロジック確認 |
| `src/app/(home)/page.tsx` | コンポーネント配置確認 |

---

## 確認事項

- [ ] TypeScriptエラー: 0件
- [ ] 開発環境での表示確認
- [ ] 管理画面で並び順変更 → フロント反映確認
- [ ] `popular`が上部エリアに表示されないこと
- [ ] `shipReservationPlanVariations`が0件のプランは表示されないこと（既存動作維持）

---

## 注意事項

- `position: "bottom"`のプランは現在存在しないため、今回は対応不要
- 将来`bottom`エリアの表示が必要になった場合は追加対応
- `PopularPlanRanking`コンポーネントは今回変更なし（`keys: ["popular"]`のまま）

---

## 壁打ち決定事項サマリー

### 質問と回答一覧

| # | 質問 | 決定 |
|---|------|------|
| Q1 | 取得方法 | A: `keys: []`で全件取得、APIのソート順をそのまま使う |
| Q2 | position対応 | B: やる。`position: "top"`のみ上部エリアに表示 |
| Q2-A | bottomの表示位置 | popularの場合のみ下部表示（keyで判定） |
| Q2-B | bottomに複数プラン | A: 現時点ではpopularのみ |
| Q2-C | bottomのレイアウト | C: `key === "popular"`だけリスト、他はカルーセル |
| Q3 | popularの扱い | A: `key === "popular"`のときだけリスト表示 |
| Q4 | GraphQLクエリ | A: `sortOrder`と`position`を追加 |
| Q5 | コンポーネント構成 | B: 現状維持（2つのコンポーネントで別々にAPI呼び出し） |
| Q6 | 表示位置 | A: `popular`は常に下部エリアに固定表示 |

### 保留事項

| 項目 | 理由 |
|------|------|
| `position: "bottom"`の表示対応 | 現在使用されているデータがないため、将来必要になった時点で対応 |
