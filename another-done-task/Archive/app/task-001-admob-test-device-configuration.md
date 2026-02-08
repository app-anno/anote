# タスク001：AdMob テストデバイス設定と iOS App ID 環境変数化

**ステータス:** 未着手
**優先度:** 高
**ブランチ:** feature/admob-interstitial-ab-test（既存）
**壁打ち日:** 2026-01-06

---

## 概要

AdMob のテストデバイス設定を実装し、iOS の `GADApplicationIdentifier` を環境変数から参照するように修正する。これにより、本番環境でも開発者デバイスではテスト広告が表示され、ポリシー違反なくテストが可能になる。

---

## 背景

### 現状の問題

1. **AdMob テストデバイス設定が未実装**: AppLovin MAX では `setTestDeviceAdvertisingIds()` でテストデバイスを登録しているが、AdMob では未設定
2. **iOS Info.plist の GADApplicationIdentifier が直書き**: Staging 用の App ID（`~9581128395`）がハードコードされており、環境ごとに切り替わらない
3. **本番広告のテストが困難**: 本番ビルドで広告をテストすると収益がカウントされポリシー違反のリスクがある

### 設計方針（壁打ちで確定）

| 方針 | 説明 |
|------|------|
| **テストデバイスID管理** | `index.js` にコードで直接記載（AppLovin MAX と同じパターン） |
| **iOS App ID 参照** | `.env` の `ADMOB_IOS_APP_ID` を `$(ADMOB_IOS_APP_ID)` で参照 |
| **テストデバイスID** | 後から追加（現時点では空配列 + コメント） |

---

## 事前調査で把握した既存実装

| ファイル | 内容 | 本タスクとの関連 |
|---------|------|-----------------|
| `index.js:69-77` | AppLovin MAX のテストデバイス設定 | 同じパターンで AdMob も実装 |
| `app/views/common/AdMobInterstitialManager.ts` | AdMob インタースティシャル広告マネージャー | テストデバイス設定の恩恵を受ける |
| `ios/Anglers/Info.plist:49-50` | GADApplicationIdentifier の直書き設定 | 環境変数化の対象 |
| `.env`, `.env.staging`, `.env.production` | 各環境の ADMOB_IOS_APP_ID 設定 | 参照元 |

---

## 変更一覧

### 1. `index.js` - AdMob テストデバイス設定追加

**変更内容**: AdMob SDK の初期化時にテストデバイスIDを設定

```javascript
// Before
import AppLovinMAX from 'react-native-applovin-max';
// ... AppLovin MAX の設定のみ

// After
import AppLovinMAX from 'react-native-applovin-max';
import mobileAds from 'react-native-google-mobile-ads';

// AppLovin MAX の初期化（既存）
// ...

// AdMob テストデバイス設定
// 本番環境でも指定したテストデバイスにはテスト広告を表示
// テストデバイスIDはログから取得:
// - iOS: Xcode Console で "<Google> To get test ads on this device..." を検索
// - Android: Logcat で "I/Ads: Use RequestConfiguration.Builder.setTestDeviceIds" を検索
mobileAds()
  .setRequestConfiguration({
    testDeviceIdentifiers: [
      'EMULATOR', // エミュレーター/シミュレーター
      // 以下にテストデバイスIDを追加（ログから取得）
      // 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx', // anno iPhone
      // 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy', // anno Android
    ],
  })
  .then(() => {
    console.log('AdMob test device configuration set');
  })
  .catch((error) => {
    console.error('AdMob test device configuration error:', error);
  });
```

**理由**: AppLovin MAX と同様のパターンで、本番環境でも開発者デバイスではテスト広告が表示されるようにする

---

### 2. `ios/Anglers/Info.plist` - GADApplicationIdentifier 環境変数化

**変更内容**: 直書きの App ID を環境変数参照に変更

```xml
<!-- Before -->
<key>GADApplicationIdentifier</key>
<string>ca-app-pub-6284018108500346~9581128395</string>

<!-- After -->
<key>GADApplicationIdentifier</key>
<string>$(ADMOB_IOS_APP_ID)</string>
```

**理由**: 環境（dev/staging/prod）ごとに正しい App ID が自動で設定されるようにする

---

## 実装手順

### Phase 1: iOS Info.plist の修正

- [ ] `ios/Anglers/Info.plist` の `GADApplicationIdentifier` を `$(ADMOB_IOS_APP_ID)` に変更
- [ ] iOS ビルドして、正しい App ID が設定されていることを確認

### Phase 2: AdMob テストデバイス設定の追加

- [ ] `index.js` に `react-native-google-mobile-ads` の import を追加
- [ ] `mobileAds().setRequestConfiguration()` でテストデバイス設定を追加
- [ ] コメントでテストデバイスID取得方法を記載

### Phase 3: 動作確認

- [ ] iOS シミュレーターで広告が表示されることを確認
- [ ] Android エミュレーターで広告が表示されることを確認
- [ ] ログに「AdMob test device configuration set」が出力されることを確認

---

## 関連ファイル

### 変更対象

| ファイル | 変更内容 |
|---------|----------|
| `index.js` | AdMob テストデバイス設定を追加 |
| `ios/Anglers/Info.plist` | GADApplicationIdentifier を環境変数参照に変更 |

### 参照のみ（変更なし）

| ファイル | 参照理由 |
|---------|----------|
| `.env` | ADMOB_IOS_APP_ID の値確認（`ca-app-pub-6284018108500346~8046693055`） |
| `.env.staging` | ADMOB_IOS_APP_ID の値確認（`ca-app-pub-6284018108500346~9581128395`） |
| `.env.production` | ADMOB_IOS_APP_ID の値確認（`ca-app-pub-6284018108500346~1002594947`） |
| `app/views/common/AdMobInterstitialManager.ts` | テストデバイス設定の恩恵を受ける既存実装 |

---

## 確認事項

- [ ] TypeScriptエラー: 0件
- [ ] iOS ビルド成功
- [ ] Android ビルド成功
- [ ] 動作確認: シミュレーター/エミュレーターで広告表示
- [ ] 動作確認: ログ出力確認

---

## 注意事項

- テストデバイスIDはログから取得する必要がある（プログラム的に取得するAPIは存在しない）
- テストデバイスIDは AppLovin MAX の IDFA とは別物
- 本番リリース前にテストデバイス設定のコードを削除する必要はない（テストデバイスとして登録されたデバイスのみテスト広告が表示される）

---

## 壁打ち決定事項サマリー

### 質問と回答一覧

| # | 質問 | 決定 |
|---|------|------|
| 1 | iOS の `GADApplicationIdentifier` を環境変数化するか | A: する（`.env` を参照） |
| 2 | AdMob テストデバイス設定を追加する場所 | A: `index.js` に追加 |
| 3 | テストデバイスIDの管理方法 | A: コードに直接記載 |
| 4 | テストデバイスIDは取得済みか | A: 未取得（後で追加） |
| 5 | iOS の環境変数化の仕組み | A: 既存の仕組みで問題なし |
| 6 | 本番環境用テストデバイスID登録 | A: 実装する |
| 7 | AdMob テストデバイスID取得の案内 | B: 不要 |
| 8 | IDFA を設定画面に表示するか | B: 不要 |

### 保留事項

| 項目 | 理由 |
|------|------|
| 実際のテストデバイスID | 後から各開発者がログを確認して追加 |

---

## 参考リンク

- [Enable test ads - Android | Google for Developers](https://developers.google.com/admob/android/test-ads)
- [Enable test ads - iOS | Google for Developers](https://developers.google.com/admob/ios/test-ads)
- [react-native-google-mobile-ads Documentation](https://docs.page/invertase/react-native-google-mobile-ads)
