# タスク001：ABTestHelper型修正と設定画面デバッグ情報の更新

**ステータス:** 未着手
**優先度:** 中
**ブランチ:** feature/admob-interstitial-ab-test
**壁打ち日:** 2026-01-05

---

## 概要

ABTestHelperに追加された `interstitialFrequency` プロパティを設定画面のデバッグ情報に反映し、削除済みの `appOpenType` 関連コードを除去する。

---

## 背景

### 現状の問題

- `ABTestHelper.ts` に `interstitialFrequency: InterstitialFrequency` (`'none' | 'every3' | 'every5'`) が追加されたが、`DeveloperSettingsMenus.js` に反映されていない
- 設定画面では `interstitialEnabled` (true/false) のみ表示しており、A/Bテストのどのグループに振り分けられたか（3回ごと/5回ごと/なし）がわからない
- `appOpenType` は常に `'none'` だが、State と表示に残っており冗長

### 設計方針（壁打ちで確定）

| 方針 | 説明 |
|------|------|
| **State簡素化** | `interstitialEnabled` を削除し `interstitialFrequency` のみ保持（有効/無効は頻度から導出可能） |
| **appOpenType削除** | App Open広告は削除済みのため、関連コードをすべて除去 |
| **ファイル形式維持** | `.js` のまま（TypeScript移行は別タスク） |
| **表示フォーマット** | 「インタースティシャル: 3回ごと」のように頻度を直接表示 |

---

## 変更一覧

### 1. State型の修正

**ファイル**: `app/views/settings/DeveloperSettingsMenus.js`

**変更内容**: `interstitialEnabled` と `appOpenType` を削除し、`interstitialFrequency` を追加

```javascript
// Before
type State = {
  adEnabled: boolean,
  interstitialEnabled: boolean,
  appOpenType: 'none' | 'launch' | 'resume',
};

// After
type State = {
  adEnabled: boolean,
  interstitialFrequency: 'none' | 'every3' | 'every5',
};
```

**理由**: `interstitialEnabled` は `interstitialFrequency !== 'none'` で導出可能。`appOpenType` は常に `'none'` で不要。

---

### 2. 初期State値の修正

**ファイル**: `app/views/settings/DeveloperSettingsMenus.js`

**変更内容**: constructor内の初期値を更新

```javascript
// Before
this.state = {
  adEnabled: true,
  interstitialEnabled: false,
  appOpenType: 'none',
};

// After
this.state = {
  adEnabled: true,
  interstitialFrequency: 'none',
};
```

**理由**: State型の変更に合わせて初期値も更新。

---

### 3. componentDidMountの修正

**ファイル**: `app/views/settings/DeveloperSettingsMenus.js`

**変更内容**: ABTestHelperから読み込むプロパティを変更

```javascript
// Before
const config = await ABTestHelper.getConfig();
this.setState({
  adEnabled: config.adEnabled,
  interstitialEnabled: config.interstitialEnabled,
  appOpenType: config.appOpenType,
});

// After
const config = await ABTestHelper.getConfig();
this.setState({
  adEnabled: config.adEnabled,
  interstitialFrequency: config.interstitialFrequency,
});
```

**理由**: 新しいState構造に合わせて読み込むプロパティを変更。

---

### 4. render関数の修正

**ファイル**: `app/views/settings/DeveloperSettingsMenus.js`

**変更内容**: デバッグ表示の内容を更新

```javascript
// Before
const { adEnabled, interstitialEnabled, appOpenType } = this.state;

// ...

<MenuListItem
  text="A/Bテスト設定"
  subText={`広告(MREC, BANNER): ${
    adEnabled ? '有効' : '無効'
  }\nインタースティシャル: ${
    interstitialEnabled ? '有効' : '無効'
  }\nApp Open: ${
    appOpenType === 'none'
      ? 'なし'
      : appOpenType === 'launch'
      ? '起動時'
      : '復帰時'
  }`}
  paddingHorizontal={CONTENT_PADDING_HORIZONTAL}
/>

// After
const { adEnabled, interstitialFrequency } = this.state;

// インタースティシャル頻度の日本語表示
const interstitialFrequencyLabel =
  interstitialFrequency === 'none'
    ? 'なし'
    : interstitialFrequency === 'every3'
    ? '3回ごと'
    : '5回ごと';

// ...

<MenuListItem
  text="A/Bテスト設定"
  subText={`広告(MREC, BANNER): ${
    adEnabled ? '有効' : '無効'
  }\nインタースティシャル: ${interstitialFrequencyLabel}`}
  paddingHorizontal={CONTENT_PADDING_HORIZONTAL}
/>
```

**理由**:
- `appOpenType` 表示を削除（App Open広告は削除済み）
- `interstitialEnabled` (有効/無効) から `interstitialFrequency` (なし/3回ごと/5回ごと) に変更し、A/Bテストグループが一目でわかるように

---

## 実装手順

### Phase 1: State型とロジックの修正

- [ ] `DeveloperSettingsMenus.js` の State型を修正
- [ ] constructor の初期値を修正
- [ ] componentDidMount の setState を修正

### Phase 2: 表示の修正

- [ ] render 関数の state 分割代入を修正
- [ ] インタースティシャル頻度の日本語ラベル変換ロジックを追加
- [ ] MenuListItem の subText を修正（2行表示に変更）

### Phase 3: 動作確認

- [ ] アプリを起動し、設定画面の「開発者向け」セクションを確認
- [ ] A/Bテスト設定が正しく表示されることを確認

---

## 関連ファイル

### 変更対象

| ファイル | 変更内容 |
|---------|----------|
| `app/views/settings/DeveloperSettingsMenus.js` | State型修正、表示内容更新 |

### 参照のみ

| ファイル | 参照理由 |
|---------|----------|
| `app/helpers/ABTestHelper.ts` | 型定義 (`InterstitialFrequency`) の確認 |

---

## 確認事項

- [ ] ESLint エラー: 0件 (`yarn lint`)
- [ ] 動作確認: 設定画面で「A/Bテスト設定」の表示が正しい
  - 「広告(MREC, BANNER): 有効」または「無効」
  - 「インタースティシャル: なし」「3回ごと」「5回ごと」のいずれか

---

## 注意事項

- `ABTestHelper.ts` の `InterstitialFrequency` 型をインポートしない（.js ファイルのため、Flow風の型定義を維持）
- 将来 TypeScript 移行する際は、型をインポートするよう修正すること

---

## 壁打ち決定事項サマリー

### 質問と回答一覧

| # | 質問 | 決定 |
|---|------|------|
| 1-1 | State型の修正方針 | A: interstitialFrequency を追加し、interstitialEnabled は削除 |
| 1-2 | デバッグ表示のフォーマット | A: 「インタースティシャル: 3回ごと」のように頻度を表示 |
| 1-3 | appOpenType の扱い | A: 削除する |
| 2-1 | インタースティシャル頻度の日本語表示 | A: なし / 3回ごと / 5回ごと |
| 2-2 | TypeScriptへの移行 | B: .js のままにする |
| 2-3 | 表示のレイアウト | A: 2行表示でOK |

### 保留事項

| 項目 | 理由 |
|------|------|
| TypeScript移行 | 今回のスコープ外。別タスクとして実施 |
