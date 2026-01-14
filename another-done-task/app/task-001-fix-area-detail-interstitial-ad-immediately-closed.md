# タスク001：マップタブからエリア詳細遷移時のインタースティシャル広告が即座に閉じられるバグの修正

**ステータス:** 未着手
**優先度:** 高
**ブランチ:** TBD
**壁打ち日:** 2026-01-06

---

## 概要

マップタブのアクションシートから「釣り場の情報を見る」ボタンを押してエリア詳細画面に遷移した際、インタースティシャル広告がすぐに閉じられてしまうバグを修正する。

---

## 背景

### 現状の問題

- マップ画面でマーカーをタップ → `AreaInfoActionSheet` が表示される
- 「釣り場の情報を見る」ボタン押下 → `handleAreaNavigation()` が呼ばれる
- `closeSheet()` でアクションシートを閉じた**直後**に `navigation.navigate('AreasShow')` で遷移が実行される
- アクションシートの閉じるアニメーション中に画面遷移が開始され、UIレイヤーの競合が発生
- `ShowView.js` の `componentDidMount()` で広告表示処理が即座に開始される
- 結果として、広告が表示された瞬間にすぐ閉じられてしまう

### 根本原因

`AreaInfoActionSheet.tsx` の `handleAreaNavigation` 関数（514-535行目）で、`closeSheet()` と `navigation.navigate()` が同期的に連続実行されている。アクションシートの閉じるアニメーションが完了する前に画面遷移が開始されるため、UIの状態が不整合になる。

```typescript
// 現在の問題のあるコード
const handleAreaNavigation = useCallback(
  (isFishingPlan?: boolean): void => {
    closeSheet();  // ← アクションシートを即座に閉じる（アニメーション開始）
    // ↓ アニメーション完了を待たずに即座に遷移
    payload.navigation.navigate('AreasShow', {
      area: selectedAreaDetail,
    });
  },
  [closeSheet, payload, selectedAreaDetail],
);
```

### 設計方針（壁打ちで確定）

| 方針 | 説明 |
|------|------|
| **広告表示タイミング** | アクションシートが完全に閉じてから、エリア詳細画面に遷移し、遷移完了後に広告を表示 |
| **修正アプローチ** | ActionSheet の `onClose` プロップを使い、シートが閉じた時に遷移処理を実行 |
| **遷移情報の保持** | `useRef` を使って遷移情報を保持し、`onClose` で参照して遷移を実行 |

---

## 事前調査で把握した既存実装

| ファイル | 内容 | 本タスクとの関連 |
|---------|------|-----------------|
| `app/views/areas/main/components/ActionSheets/AreaInfoActionSheet.tsx` | マップのアクションシート | 修正対象。`handleAreaNavigation` と `closeSheet` の実装箇所 |
| `app/views/areas/main/ShowView.js` | エリア詳細画面（クラスコンポーネント） | `componentDidMount` で広告表示をトリガー |
| `app/views/common/AdMobInterstitialManager.ts` | インタースティシャル広告マネージャー | 広告表示ロジック（変更不要） |
| `app/helpers/ABTestHelper.ts` | A/Bテスト設定 | 参照のみ（変更不要） |

---

## 変更一覧

### 1. `AreaInfoActionSheet.tsx` に `pendingNavigationRef` を追加

**ファイル**: `app/views/areas/main/components/ActionSheets/AreaInfoActionSheet.tsx`

**変更内容**: 遷移情報を保持する `useRef` を追加

```typescript
// Before（該当コードなし）

// After（useRef追加）
// 既存のuseRefの近くに追加（384行目付近）
const isMountedRef = useRef(true);

// ↓ 新規追加
type PendingNavigation = {
  type: 'area' | 'ship' | 'result' | 'areaResults' | 'shipCatches';
  isFishingPlan?: boolean;
  result?: Result;
} | null;

const pendingNavigationRef = useRef<PendingNavigation>(null);
```

**理由**: `onClose` コールバックで遷移を実行するために、ボタン押下時の遷移情報を保持する必要がある。`useRef` は再レンダリングを引き起こさないため適切。

---

### 2. `closeSheet` 関数の変更

**変更内容**: 単純に `SheetManager.hide()` を呼ぶだけに留める（変更なしでOK）

```typescript
// 現在のコード（変更不要）
const closeSheet = useCallback(() => {
  SheetManager.hide(SHEET_IDS.AREA_INFO);
  // State will be reset when sheet opens again via useEffect
}, []);
```

---

### 3. `handleAreaNavigation` 関数の変更

**変更内容**: 遷移情報を `pendingNavigationRef` にセットしてから `closeSheet()` を呼ぶ

```typescript
// Before
const handleAreaNavigation = useCallback(
  (isFishingPlan?: boolean): void => {
    closeSheet();
    if (payload.isShip) {
      const url = createShipsUrl(
        String(selectedAreaDetail?.id),
        isFishingPlan,
      );
      const appendUtmParams = utmParams.searchCardMapShipDetail(url);
      const linkUrl =
        GoogleUtils.generateWebviewAnalyticsUrl(appendUtmParams);
      payload.navigation.navigate('Ships', {
        url: linkUrl,
      });
    } else {
      payload.navigation.navigate('AreasShow', {
        area: selectedAreaDetail,
      });
    }
  },
  [closeSheet, payload, selectedAreaDetail],
);

// After
const handleAreaNavigation = useCallback(
  (isFishingPlan?: boolean): void => {
    // 遷移情報をrefに保持
    pendingNavigationRef.current = {
      type: payload.isShip ? 'ship' : 'area',
      isFishingPlan,
    };
    // シートを閉じる（onCloseで遷移が実行される）
    closeSheet();
  },
  [closeSheet, payload.isShip],
);
```

**理由**: アクションシートの閉じるアニメーションが完了してから遷移を実行するため。

---

### 4. `onPressResult` 関数の変更

**変更内容**: 遷移情報を `pendingNavigationRef` にセットしてから `closeSheet()` を呼ぶ

```typescript
// Before
const onPressResult = useCallback(
  (result: Result): void => {
    closeSheet();
    payload.navigation.navigate('Result', { result });
  },
  [closeSheet, payload.navigation],
);

// After
const onPressResult = useCallback(
  (result: Result): void => {
    pendingNavigationRef.current = {
      type: 'result',
      result,
    };
    closeSheet();
  },
  [closeSheet],
);
```

---

### 5. `onPressAreaAllButton` 関数の変更

```typescript
// Before
const onPressAreaAllButton = useCallback((): void => {
  closeSheet();
  payload.navigation.navigate('AreasResults', {
    area: selectedAreaDetail,
  });
}, [closeSheet, payload.navigation, selectedAreaDetail]);

// After
const onPressAreaAllButton = useCallback((): void => {
  pendingNavigationRef.current = {
    type: 'areaResults',
  };
  closeSheet();
}, [closeSheet]);
```

---

### 6. `onPressShipAllButton` 関数の変更

```typescript
// Before
const onPressShipAllButton = useCallback((): void => {
  closeSheet();
  payload.navigation.navigate('AppShipsCatches', {
    ship_id: selectedAreaDetail?.id,
  });
}, [closeSheet, payload.navigation, selectedAreaDetail]);

// After
const onPressShipAllButton = useCallback((): void => {
  pendingNavigationRef.current = {
    type: 'shipCatches',
  };
  closeSheet();
}, [closeSheet]);
```

---

### 7. `onPressShip` 関数の変更

```typescript
// Before
const onPressShip = useCallback((): void => {
  closeSheet();
  const { navigation } = payload;
  const url = createShipsUrl(String(selectedAreaDetail?.id));
  const appendUtmParams = utmParams.searchFishSpecies(url);
  const linkUrl = GoogleUtils.generateWebviewAnalyticsUrl(appendUtmParams);
  navigation.navigate('Ships', {
    url: linkUrl,
  });
}, [closeSheet, payload, selectedAreaDetail]);

// After
const onPressShip = useCallback((): void => {
  pendingNavigationRef.current = {
    type: 'ship',
    isFishingPlan: false,
  };
  closeSheet();
}, [closeSheet]);
```

---

### 8. `handleSheetClose` 関数の新規追加

**変更内容**: シートが閉じた後に遷移を実行する `handleSheetClose` 関数を追加

```typescript
// 新規追加（closeSheet関数の後に追加）
const handleSheetClose = useCallback(() => {
  const pending = pendingNavigationRef.current;
  if (!pending) return;

  // refをクリア
  pendingNavigationRef.current = null;

  switch (pending.type) {
    case 'area':
      payload.navigation.navigate('AreasShow', {
        area: selectedAreaDetail,
      });
      break;
    case 'ship': {
      const url = createShipsUrl(
        String(selectedAreaDetail?.id),
        pending.isFishingPlan,
      );
      const appendUtmParams = pending.isFishingPlan
        ? utmParams.searchCardMapShipDetail(url)
        : utmParams.searchFishSpecies(url);
      const linkUrl = GoogleUtils.generateWebviewAnalyticsUrl(appendUtmParams);
      payload.navigation.navigate('Ships', {
        url: linkUrl,
      });
      break;
    }
    case 'result':
      if (pending.result) {
        payload.navigation.navigate('Result', { result: pending.result });
      }
      break;
    case 'areaResults':
      payload.navigation.navigate('AreasResults', {
        area: selectedAreaDetail,
      });
      break;
    case 'shipCatches':
      payload.navigation.navigate('AppShipsCatches', {
        ship_id: selectedAreaDetail?.id,
      });
      break;
  }
}, [payload, selectedAreaDetail]);
```

**理由**: シートが完全に閉じた後に遷移を実行することで、UIレイヤーの競合を防ぐ。

---

### 9. ActionSheet に `onClose` プロップを追加

**変更内容**: ActionSheet コンポーネントに `onClose` プロップを追加

```typescript
// Before
return (
  <ActionSheet
    id={SHEET_IDS.AREA_INFO}
    gestureEnabled
    zIndex={1}
    snapPoints={INITIAL_SNAP_POINTS as unknown as number[]}
    indicatorStyle={{ height: 0 }}
    containerStyle={{ maxHeight: '100%', height: '100%' }}
    initialSnapIndex={0}
  >
    ...
  </ActionSheet>
);

// After
return (
  <ActionSheet
    id={SHEET_IDS.AREA_INFO}
    gestureEnabled
    zIndex={1}
    snapPoints={INITIAL_SNAP_POINTS as unknown as number[]}
    indicatorStyle={{ height: 0 }}
    containerStyle={{ maxHeight: '100%', height: '100%' }}
    initialSnapIndex={0}
    onClose={handleSheetClose}
  >
    ...
  </ActionSheet>
);
```

**理由**: シートが完全に閉じた後に `handleSheetClose` が呼ばれ、遷移が実行される。

---

## 実装手順

### Phase 1: 型定義と useRef の追加

- [ ] `PendingNavigation` 型を定義
- [ ] `pendingNavigationRef` を追加

### Phase 2: 遷移関数の修正

- [ ] `handleAreaNavigation` を修正（遷移情報をrefにセット → closeSheet）
- [ ] `onPressResult` を修正
- [ ] `onPressAreaAllButton` を修正
- [ ] `onPressShipAllButton` を修正
- [ ] `onPressShip` を修正

### Phase 3: onClose ハンドラーの実装

- [ ] `handleSheetClose` 関数を新規追加
- [ ] ActionSheet に `onClose={handleSheetClose}` を追加

### Phase 4: 動作確認

- [ ] マップタブでマーカーをタップ → アクションシートが表示される
- [ ] 「釣り場の情報を見る」ボタン押下 → アクションシートが閉じてからエリア詳細画面に遷移する
- [ ] エリア詳細画面で広告が表示される（A/Bテストで広告表示グループの場合）
- [ ] 広告がすぐに閉じられないことを確認
- [ ] 「すべての釣果を見る」ボタンでの遷移も正常に動作することを確認
- [ ] 釣果タップでの遷移も正常に動作することを確認

---

## 関連ファイル

### 変更対象

| ファイル | 変更内容 |
|---------|---------|
| `app/views/areas/main/components/ActionSheets/AreaInfoActionSheet.tsx` | `pendingNavigationRef` 追加、遷移関数の修正、`handleSheetClose` 追加、`onClose` プロップ追加 |

### 新規作成

なし

### 参照のみ（変更なし）

| ファイル | 参照理由 |
|---------|---------|
| `app/views/areas/main/ShowView.js` | 広告表示トリガーの確認 |
| `app/views/common/AdMobInterstitialManager.ts` | 広告表示ロジックの確認 |
| `app/helpers/ABTestHelper.ts` | A/Bテスト設定の確認 |

---

## 確認事項

- [ ] TypeScriptエラー: 0件
- [ ] ESLint警告: 0件
- [ ] 動作確認: マップ → アクションシート → エリア詳細の遷移フロー
- [ ] 動作確認: 広告表示（A/Bテスト広告表示グループの場合）
- [ ] 動作確認: 広告が即座に閉じられないこと

---

## 注意事項

- `react-native-actions-sheet` のバージョンは `0.9.7` を使用
- `onClose` プロップがこのバージョンでサポートされているか、実装時に確認が必要
  - もしサポートされていない場合は、`SheetManager.hide()` の戻り値（Promise）を `await` するか、`setTimeout` で遅延を入れるアプローチに変更する
- 他のアクションシート（`FishesActionSheet`, `TargetFishesActionSheet` など）でも同様の問題がある場合は、同じパターンで修正する

---

## 壁打ち決定事項サマリー

### 質問と回答一覧

| # | 質問 | 決定 |
|---|------|------|
| 1 | 広告表示のタイミング | A: アクションシートが完全に閉じてから、エリア詳細画面に遷移し、遷移完了後に広告を表示 |
| 2 | 広告が閉じられるタイミング | D: 詳細は不明だが、結果として広告がすぐ閉じてしまう |
| 3 | 修正アプローチ | A: `closeSheet()` にコールバックまたは Promise を追加し、完了後に遷移を実行 |
| 4 | - | - |
| 5 | ActionSheet の `onClose` コールバックについて | B: ActionSheet の `onClose` プロップを使い、シートが閉じた時に遷移処理を実行 |
| 6 | 遷移先の情報の保持方法 | B: `useRef` を使って遷移情報を保持し、`onClose` で参照して遷移を実行 |

### 保留事項

| 項目 | 理由 |
|------|------|
| `onClose` プロップのサポート確認 | `react-native-actions-sheet` v0.9.7 で `onClose` がサポートされているか実装時に確認が必要 |
