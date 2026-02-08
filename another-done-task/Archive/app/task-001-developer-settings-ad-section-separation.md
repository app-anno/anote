# タスク001：開発者設定画面の広告設定セクション分離

**ステータス:** 未着手
**優先度:** 中
**ブランチ:** TBD
**壁打ち日:** 2025-01-05

---

## 概要

開発者設定画面の「AppLovin設定情報」セクションからAdMob関連を分離し、「AdMob設定情報」と「AdMobアドインスペクター」を新規セクションとして追加する。AppLovinのInterstitial情報は使用しなくなったため除外する。

---

## 背景

### 現状の問題

- AppLovin設定情報セクション内にAppLovinとAdMobの情報が混在している
- AppLovinのインタースティシャル広告は使用しなくなったが、まだ表示されている
- AdMob専用のアドインスペクター（デバッグツール）がない

### 設計方針（壁打ちで確定）

| 方針 | 説明 |
|------|------|
| **セクション分離** | AppLovin設定情報とAdMob設定情報を別セクションに分離 |
| **AppLovin Interstitial除外** | 使用しなくなったAppLovinのInterstitial情報は除外 |
| **表示順序** | 既存順序を維持し、末尾にAdMob関連を追加 |
| **UI統一** | AdMob設定情報はAppLovinと同じフォーマット・挙動 |
| **エラーハンドリング** | console.errorのみ（Alertなし） |

---

## 事前調査で把握した既存実装

| ファイル | 内容 | 本タスクとの関連 |
|---------|------|-----------------|
| `app/views/settings/DeveloperSettingsMenus.js` | 開発者向け設定メニュー | 変更対象 |
| `app/views/common/AdMobInterstitialManager.ts` | AdMobインタースティシャル管理 | AdMob実装の参考 |
| `.env.staging` | 環境変数設定 | ADMOB_APP_ID等の確認 |

---

## 変更一覧

### 1. AppLovin設定情報からInterstitial除外

**変更内容**: `renderAppLovinConfigInfo`メソッドからInterstitial関連の表示を削除

```javascript
// Before
const interstitialUnitId = Platform.select({
  android: Config.APPLOVIN_INTERSTITIAL_ANDROID_UNIT_ID || 'Not Set',
  ios: Config.APPLOVIN_INTERSTITIAL_IOS_UNIT_ID || 'Not Set',
});

// AdMob Interstitial Unit ID
const admobInterstitialUnitId = Platform.select({
  android: Config.ADMOB_INTERSTITIAL_ANDROID_UNIT_ID || 'Not Set',
  ios: Config.ADMOB_INTERSTITIAL_IOS_UNIT_ID || 'Not Set',
});

// ...

const configInfo = `【環境情報】
...
Interstitial (AppLovin):
${interstitialUnitId} ${isValidInterstitial ? '✅' : '❌'}

Interstitial (AdMob):
${admobInterstitialUnitId} ${isValidAdmobInterstitial ? '✅' : '❌'}
...`;

// After
// interstitialUnitId, admobInterstitialUnitId の定義を削除
// isValidInterstitial, isValidAdmobInterstitial の定義を削除

const configInfo = `【環境情報】
Platform: ${platform.toUpperCase()}
Environment: ${environment}
AppLovin User Ratio: ${userRatio}

【AppLovin SDK Key】
${sdkKey?.substring(0, 20)}... ${isValidSdkKey ? '✅' : '❌'}

【広告ユニットID】
Banner (320x50):
${bannerUnitIds} ${isValidBanner ? '✅' : '❌'}

MREC (300x250):
${mrecUnitIds} ${isValidMrec ? '✅' : '❌'}

✅ = 正常な形式
❌ = プレースホルダーまたは未設定`;
```

**理由**: AppLovinのインタースティシャルは使用しなくなったため、混乱を避けるために除外

---

### 2. AdMob設定情報セクション追加

**変更内容**: `renderAdMobConfigInfo`メソッドを新規追加

```javascript
renderAdMobConfigInfo = () => {
  const platform = Platform.OS;
  const environment = Config.APP_ENV || 'unknown';

  // AdMob App ID
  const appId = Config.ADMOB_APP_ID || 'Not Set';

  // AdMob Interstitial Unit ID
  const interstitialUnitId = Platform.select({
    android: Config.ADMOB_INTERSTITIAL_ANDROID_UNIT_ID || 'Not Set',
    ios: Config.ADMOB_INTERSTITIAL_IOS_UNIT_ID || 'Not Set',
  });

  // 設定が正しいかチェック
  const isValidAppId = appId?.startsWith('ca-app-pub-');
  const isValidInterstitial = interstitialUnitId?.startsWith('ca-app-pub-');

  const configInfo = `【環境情報】
Platform: ${platform.toUpperCase()}
Environment: ${environment}

【AdMob App ID】
${appId} ${isValidAppId ? '✅' : '❌'}

【インタースティシャル広告ユニットID】
${interstitialUnitId} ${isValidInterstitial ? '✅' : '❌'}

✅ = 正常な形式
❌ = プレースホルダーまたは未設定`;

  return (
    <MenuListItem
      text="AdMob設定情報"
      subText={configInfo}
      onPress={() => this.handleCopyAdMobConfig(configInfo, 'AdMob設定情報')}
      paddingHorizontal={CONTENT_PADDING_HORIZONTAL}
    />
  );
};

handleCopyAdMobConfig = (text: string, label: string) => {
  Clipboard.setString(text);
  Alert.alert('コピー完了', `${label}をクリップボードにコピーしました`);
};
```

**理由**: AdMob固有の設定情報を独立したセクションとして表示

---

### 3. AdMobアドインスペクターボタン追加

**変更内容**: `handleOpenAdMobAdInspector`メソッドを新規追加し、renderに追加

```javascript
// import追加
import { MobileAds } from 'react-native-google-mobile-ads';

// メソッド追加
handleOpenAdMobAdInspector = async () => {
  try {
    await MobileAds().openAdInspector();
  } catch (error) {
    const errorDetails = {
      message: error.message,
      code: error.code,
      platform: Platform.OS,
    };
    console.error('Failed to open AdMob ad inspector:', errorDetails);
  }
};
```

**理由**: AdMob広告のデバッグ用にアドインスペクターを起動できるようにする

---

### 4. renderメソッドの更新

**変更内容**: 新規セクションをrenderに追加

```javascript
// Before
render() {
  // ...
  return (
    <MenuList title="開発者向け" paddingHorizontal={CONTENT_PADDING_HORIZONTAL}>
      <MenuListItem text="A/Bテスト設定" ... />
      <MenuListItem text="A/Bテストをリセット" ... />
      {this.renderAppLovinConfigInfo()}
      <MenuListItem text="AppLovinメディエーションデバッガー" ... />
    </MenuList>
  );
}

// After
render() {
  // ...
  return (
    <MenuList title="開発者向け" paddingHorizontal={CONTENT_PADDING_HORIZONTAL}>
      <MenuListItem text="A/Bテスト設定" ... />
      <MenuListItem text="A/Bテストをリセット" ... />
      {this.renderAppLovinConfigInfo()}
      <MenuListItem text="AppLovinメディエーションデバッガー" ... />
      {this.renderAdMobConfigInfo()}
      <MenuListItem
        text="AdMobアドインスペクター"
        onPress={this.handleOpenAdMobAdInspector}
        paddingHorizontal={CONTENT_PADDING_HORIZONTAL}
      />
    </MenuList>
  );
}
```

**理由**: 既存順序を維持しつつ、末尾にAdMob関連を追加

---

## 実装手順

### Phase 1: AppLovin設定情報の修正

- [ ] `renderAppLovinConfigInfo`からInterstitial関連コードを削除
- [ ] 不要な変数（interstitialUnitId, admobInterstitialUnitId等）を削除

### Phase 2: AdMob設定情報の追加

- [ ] `react-native-google-mobile-ads`から`MobileAds`をimport
- [ ] `handleCopyAdMobConfig`メソッドを追加
- [ ] `renderAdMobConfigInfo`メソッドを追加
- [ ] `handleOpenAdMobAdInspector`メソッドを追加

### Phase 3: renderメソッドの更新

- [ ] `{this.renderAdMobConfigInfo()}`を追加
- [ ] AdMobアドインスペクターのMenuListItemを追加

### Phase 4: 動作確認

- [ ] iOS/Androidで設定画面を開いて表示確認
- [ ] AppLovin設定情報にInterstitialが表示されないことを確認
- [ ] AdMob設定情報が正しく表示されることを確認
- [ ] AdMob設定情報タップでクリップボードにコピーされることを確認
- [ ] AdMobアドインスペクターが起動することを確認

---

## 関連ファイル

### 変更対象

| ファイル | 変更内容 |
|---------|----------|
| `app/views/settings/DeveloperSettingsMenus.js` | AppLovin設定からInterstitial除外、AdMob設定情報・アドインスペクター追加 |

### 新規作成

なし

### 参照のみ（変更なし）

| ファイル | 参照理由 |
|---------|----------|
| `app/views/common/AdMobInterstitialManager.ts` | AdMob実装パターンの参考 |
| `.env.staging` | 環境変数名の確認 |

---

## 確認事項

- [ ] ESLintエラー: 0件
- [ ] 動作確認: iOS/Android両方で設定画面の表示・操作確認

---

## 注意事項

- `MobileAds`のimportはnamed importで行う（`import { MobileAds } from 'react-native-google-mobile-ads'`）
- AdMobアドインスペクターはテストデバイスでのみ動作するため、本番環境では動作しない可能性あり

---

## 壁打ち決定事項サマリー

### 質問と回答一覧

| # | 質問 | 決定 |
|---|------|------|
| 1 | AppLovin設定情報から除外する項目 | A: AppLovinのInterstitialだけ除外（Banner, MRECは残す） |
| 2 | AdMob設定情報に表示する項目 | A: AdMob App ID + Interstitial Unit ID のみ |
| 3 | AdMobアドインスペクターのエラーハンドリング | A: console.errorのみ |
| 4 | セクションの表示順序 | A: 既存順序維持、末尾にAdMob追加 |
| 5 | AdMob設定情報の表示フォーマット | A: AppLovinと同じ形式（検証マーク付き） |
| 6 | タップ時の挙動 | A: クリップボードにコピー + Alert表示 |

### 保留事項

なし
