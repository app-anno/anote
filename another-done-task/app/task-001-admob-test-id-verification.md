# タスク001：AdMobテストID環境での本番ビルド動作確認

**ステータス:** 未着手
**優先度:** 高
**ブランチ:** feature/admob-interstitial-ab-test
**壁打ち日:** 2025-01-06

---

## 概要

本番ビルドでAdMob広告SDKの動作確認を行う。App ID・ユニットIDともにGoogleの汎用テストIDを使用し、誤クリック課金リスクなしで安全にテストする。

---

## 背景

### 現状の問題

- AdMobインタースティシャル広告の実装が完了したが、本番ビルドでの動作確認がまだ
- 本番ビルドでは開発者メニューが非表示のため、デバッグ情報が確認できない

### 設計方針（壁打ちで確定）

| 方針 | 説明 |
|------|------|
| **全てテストIDを使用** | App ID・ユニットIDともにGoogleの汎用テストIDを使用し、安全にテスト |
| **開発者メニューを一時的に表示** | 本番ビルドでもデバッグ情報を確認できるよう、条件分岐を一時変更 |
| **本番ビルド（リリースビルド）で確認** | 実際のリリースと同じ条件で動作確認 |

---

## 事前調査で把握した既存実装

| ファイル | 内容 | 本タスクとの関連 |
|---------|------|-----------------|
| `app/views/common/AdMobInterstitialManager.ts` | インタースティシャル広告管理 | ユニットID取得ロジックを確認 |
| `app/views/settings/DeveloperSettingsMenus.js` | 開発者設定メニュー | 本番ビルドでの表示条件を変更 |
| `.env.production` | 本番環境設定 | AdMob IDを一時的にテストIDに変更 |
| `ios/Anglers/Info.plist` | iOS設定 | `GADApplicationIdentifier`の設定確認 |
| `android/app/src/main/res/values/strings.xml` | Android設定 | `admob_app_id`の設定確認 |

---

## 変更一覧

### 1. `.env.production` - AdMob IDをテスト用に変更

**変更内容**: App IDとユニットIDをGoogleの汎用テストIDに変更

```bash
# Before
ADMOB_ANDROID_APP_ID="ca-app-pub-6284018108500346~9806195962"
ADMOB_IOS_APP_ID="ca-app-pub-6284018108500346~1002594947"
ADMOB_INTERSTITIAL_IOS_UNIT_ID=ca-app-pub-3940256099942544/4411468910
ADMOB_INTERSTITIAL_ANDROID_UNIT_ID=ca-app-pub-3940256099942544/1033173712

# After
ADMOB_ANDROID_APP_ID=ca-app-pub-3940256099942544~3347511713
ADMOB_IOS_APP_ID=ca-app-pub-3940256099942544~1458002511
ADMOB_INTERSTITIAL_IOS_UNIT_ID=ca-app-pub-3940256099942544/4411468910
ADMOB_INTERSTITIAL_ANDROID_UNIT_ID=ca-app-pub-3940256099942544/1033173712
```

**理由**: Googleの汎用テストIDを使用することで、本番ビルドと同じ初期化プロセスを経ながら、テスト広告が表示される。誤クリック課金のリスクがない。

---

### 2. 開発者メニューを本番ビルドで表示する

**変更内容**: 設定画面で開発者メニューが表示される条件を確認し、本番ビルドでも表示されるよう一時変更

**調査が必要な点**:
- `DeveloperSettingsMenus`コンポーネントの表示条件を確認
- `__DEV__`フラグや環境変数での制御を確認

```javascript
// 想定される変更箇所（実際のコードを確認して調整）
// Before: __DEV__環境のみ表示
{__DEV__ && <DeveloperSettingsMenus />}

// After: 一時的に常に表示
{true && <DeveloperSettingsMenus />}
// または
<DeveloperSettingsMenus />
```

**理由**: 本番ビルドでAdMob設定情報とアドインスペクターにアクセスするため。

---

## 実装手順

### Phase 1: 環境設定の変更

- [ ] `.env.production`のAdMob App IDをテスト用に変更
  - iOS: `ca-app-pub-3940256099942544~1458002511`
  - Android: `ca-app-pub-3940256099942544~3347511713`
- [ ] インタースティシャルユニットIDがテスト用であることを確認（現状のままでOK）

### Phase 2: 開発者メニューの表示設定

- [ ] 設定画面で`DeveloperSettingsMenus`の表示条件を調査
- [ ] 本番ビルドでも表示されるよう条件を一時変更

### Phase 3: ビルドと動作確認

- [ ] iOSの本番ビルド作成: `yarn ios:production` または Xcode Archive
- [ ] Androidの本番ビルド作成: `yarn android:production` または `./gradlew assembleRelease`
- [ ] 実機にインストールして動作確認

### Phase 4: 動作確認項目

- [ ] アプリ起動時にクラッシュしないこと
- [ ] 設定画面 > 開発者向け > AdMob設定情報が表示されること
- [ ] 表示されるApp IDがテスト用（`ca-app-pub-3940256099942544~...`）であること
- [ ] エリア詳細画面に3回または5回遷移後、インタースティシャル広告が表示されること
- [ ] 表示される広告が「Test Ad」ラベル付きのテスト広告であること
- [ ] AdMobアドインスペクターが起動できること

---

## 関連ファイル

### 変更対象

| ファイル | 変更内容 |
|---------|----------|
| `.env.production` | AdMob App IDをテスト用に一時変更 |
| 設定画面の親コンポーネント（要調査） | 開発者メニュー表示条件を一時変更 |

### 参照のみ（変更なし）

| ファイル | 参照理由 |
|---------|----------|
| `app/views/common/AdMobInterstitialManager.ts` | ユニットID取得ロジック確認 |
| `app/views/settings/DeveloperSettingsMenus.js` | デバッグ情報表示内容確認 |
| `app/helpers/ABTestHelper.ts` | A/Bテスト設定確認 |

---

## 確認事項

- [ ] TypeScriptエラー: 0件
- [ ] 動作確認: テスト広告が正常に表示される
- [ ] 動作確認: アドインスペクターが起動する
- [ ] 動作確認: 設定画面でAdMob設定情報が確認できる

---

## 注意事項

- **この変更はタスク1の確認用**であり、タスク2・3で本番IDに戻す
- テストIDを使用しているため、広告収益は発生しない
- 確認完了後、変更を戻すことを忘れないこと

---

## 壁打ち決定事項サマリー

### 質問と回答一覧

| # | 質問 | 決定 |
|---|------|------|
| 1 | 「本番環境」の定義 | A: 本番用ビルド（リリースビルド） |
| 2 | デバッグ情報の表示方法 | A: 本番ビルドでも開発者メニューを一時的に表示 |
| 3 | テスト用IDの設定箇所 | A: App IDも含めて全てテストIDにする |
| 4 | テスト用App ID | Google公式テストID使用 |

### 保留事項

| 項目 | 理由 |
|------|------|
| 開発者メニュー表示条件の具体的な変更箇所 | 実装時に調査が必要 |

---

## 参考: Google AdMob テストID一覧

| 項目 | iOS | Android |
|------|-----|---------|
| App ID | `ca-app-pub-3940256099942544~1458002511` | `ca-app-pub-3940256099942544~3347511713` |
| インタースティシャル | `ca-app-pub-3940256099942544/4411468910` | `ca-app-pub-3940256099942544/1033173712` |
