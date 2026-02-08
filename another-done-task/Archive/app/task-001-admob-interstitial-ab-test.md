# タスク001：AdMob インタースティシャル広告 A/Bテスト実装

**ステータス:** 未着手
**優先度:** 高
**ブランチ:** feature/admob-interstitial-ab-test
**壁打ち日:** 2026-01-05

---

## 概要

エリア詳細画面にAdMobインタースティシャル広告を導入し、表示頻度についてA/Bテスト（3回ごと / 5回ごと / 非表示）を実施する。

---

## 背景

### 現状の問題

- 現在のコードベースはAppLovin MAXに完全移行済み
- インタースティシャル広告は`ABTestHelper.ts`で常に無効化されている（MVPフェーズ）
- エリア詳細画面での広告収益最適化が未実施

### 設計方針（壁打ちで確定）

| 方針 | 説明 |
|------|------|
| **ハイブリッド構成** | AppLovinのバナー/MRECは残し、インタースティシャルのみAdMobに変更 |
| **A/Bテスト** | アプリ内でABTestHelper.tsを拡張して3グループに振り分け |
| **カウント永続化** | AsyncStorageで累計カウント（アプリ削除まで保持） |
| **遷移検知** | componentDidMountで初回マウント時のみカウント |
| **広告表示タイミング** | 画面表示後にインタースティシャルを表示 |
| **ロード失敗時** | カウントをリセットして次のN回目まで待つ |
| **サブスク会員** | 広告を表示しない（既存動作を踏襲） |

---

## 変更一覧

### 1. AppLovin App Open広告の削除

**削除対象ファイル:**
- `app/common/AppLovinAppOpenManager.ts`

**変更内容**: ファイル全体を削除し、呼び出し元から参照を削除

**関連する呼び出し元の修正:**
- `config/AppProvider.js` - App Open広告の初期化コードを削除

---

### 2. AppLovinインタースティシャル広告の削除

**削除対象ファイル:**
- `app/views/common/AppLovinInterstitial.ts`

**変更内容**: ファイル全体を削除し、呼び出し元から参照を削除

**関連する呼び出し元の修正:**
- `app/views/posts/ShareSettingsView.js` - インタースティシャル広告のプリロード・表示コードを削除

---

### 3. 環境変数の追加（.env, .env.staging, .env.production）

**変更内容**: AdMobインタースティシャル用のユニットIDを追加

```bash
# Before（AppLovin設定のみ）
APPLOVIN_INTERSTITIAL_IOS_UNIT_ID=81671445ada5b906
APPLOVIN_INTERSTITIAL_ANDROID_UNIT_ID=a8958e109c9d7a74
APPLOVIN_APP_OPEN_IOS_UNIT_ID=6ad9ec6bec0ba49a
APPLOVIN_APP_OPEN_ANDROID_UNIT_ID=e6920ea4874eeb97

# After（AdMob設定を追加、AppLovinインタースティシャル/App Open設定を削除）
# AdMob Interstitial Unit IDs
ADMOB_INTERSTITIAL_ANDROID_UNIT_ID=ca-app-pub-3940256099942544/1033173712
ADMOB_INTERSTITIAL_IOS_UNIT_ID=ca-app-pub-3940256099942544/4411468910
```

**理由**: 過去のAdMob実装で使用していたユニットIDを復活させる

---

### 4. react-native-google-mobile-adsの追加

**変更内容**: package.jsonに依存関係を追加

```json
// package.json
{
  "dependencies": {
    "react-native-google-mobile-ads": "^14.0.0"
  }
}
```

**理由**: AdMobインタースティシャル広告の実装に必要

---

### 5. ABTestHelper.tsの拡張

**ファイル:** `app/helpers/ABTestHelper.ts`

**変更内容**: インタースティシャル広告のA/Bテストグループ振り分けロジックを追加

```typescript
// Before
export type AppOpenType = 'none' | 'launch' | 'resume';

export interface ABTestConfig {
  adEnabled: boolean;
  interstitialEnabled: boolean;
  appOpenType: AppOpenType;
}

// After
export type AppOpenType = 'none' | 'launch' | 'resume';
export type InterstitialFrequency = 'none' | 'every3' | 'every5';

export interface ABTestConfig {
  adEnabled: boolean;
  interstitialEnabled: boolean;
  appOpenType: AppOpenType;
  interstitialFrequency: InterstitialFrequency; // 新規追加
}

// AsyncStorage key 追加
const STORAGE_KEY_INTERSTITIAL_FREQUENCY = '@anglers:ab_test_interstitial_frequency';

// Firebase user property key 追加
const USER_PROPERTY_INTERSTITIAL_FREQUENCY = 'ab_interstitial_frequency';
```

**generateRandomConfig()の変更:**

```typescript
private generateRandomConfig(): ABTestConfig {
  const adEnabled = Math.random() < 0.9;

  // インタースティシャル広告のA/Bテスト振り分け
  // A: 3回ごと (33%)
  // B: 5回ごと (33%)
  // C: 非表示 (34%)
  let interstitialFrequency: InterstitialFrequency = 'none';
  const interstitialRandom = Math.random();
  if (interstitialRandom < 0.33) {
    interstitialFrequency = 'every3';
  } else if (interstitialRandom < 0.66) {
    interstitialFrequency = 'every5';
  } else {
    interstitialFrequency = 'none';
  }

  // interstitialEnabledはinterstitialFrequencyから導出
  const interstitialEnabled = interstitialFrequency !== 'none';

  // App Open広告は削除するため常にnone
  const appOpenType: AppOpenType = 'none';

  return {
    adEnabled,
    interstitialEnabled,
    appOpenType,
    interstitialFrequency,
  };
}
```

**新規メソッド追加:**

```typescript
/**
 * インタースティシャル広告の表示頻度を取得する
 */
async getInterstitialFrequency(): Promise<InterstitialFrequency> {
  const config = await this.getConfig();
  return config.interstitialFrequency;
}
```

**理由**: A/Bテストの3グループ（3回ごと / 5回ごと / 非表示）を振り分けるため

---

## 新規ユーティリティ関数

### 1. AdMobInterstitialManager（`app/views/common/AdMobInterstitialManager.ts`）

```typescript
import { InterstitialAd, AdEventType, TestIds } from 'react-native-google-mobile-ads';
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-community/async-storage';
import firebase from '@react-native-firebase/app';
import Config from 'react-native-config';
import ABTestHelper, { InterstitialFrequency } from '@helpers/ABTestHelper';
import { getSubscriptionStatus, waitForAdaptyReady } from '@common/SubscriptionStatusContext';

// AsyncStorage key
const STORAGE_KEY_AREA_VIEW_COUNT = '@anglers:area_detail_view_count';

// Firebase Analytics event names
const EVENT_INTERSTITIAL_SHOWN = 'admob_interstitial_shown';
const EVENT_INTERSTITIAL_FAILED = 'admob_interstitial_failed';

class AdMobInterstitialManager {
  private interstitialAd: InterstitialAd | null = null;
  private isLoading: boolean = false;
  private isLoaded: boolean = false;

  /**
   * 広告ユニットIDを取得
   */
  private getUnitId(): string {
    const unitId = Platform.select({
      ios: Config.ADMOB_INTERSTITIAL_IOS_UNIT_ID,
      android: Config.ADMOB_INTERSTITIAL_ANDROID_UNIT_ID,
    });

    // 未設定の場合はテストIDを使用
    if (!unitId) {
      return Platform.select({
        ios: TestIds.INTERSTITIAL,
        android: TestIds.INTERSTITIAL,
      }) as string;
    }

    return unitId;
  }

  /**
   * 現在のエリア詳細画面表示カウントを取得
   */
  async getViewCount(): Promise<number> {
    try {
      const countStr = await AsyncStorage.getItem(STORAGE_KEY_AREA_VIEW_COUNT);
      return countStr ? parseInt(countStr, 10) : 0;
    } catch (error) {
      console.error('Failed to get view count:', error);
      return 0;
    }
  }

  /**
   * エリア詳細画面表示カウントを更新
   */
  async incrementViewCount(): Promise<number> {
    try {
      const currentCount = await this.getViewCount();
      const newCount = currentCount + 1;
      await AsyncStorage.setItem(STORAGE_KEY_AREA_VIEW_COUNT, newCount.toString());
      return newCount;
    } catch (error) {
      console.error('Failed to increment view count:', error);
      return 0;
    }
  }

  /**
   * エリア詳細画面表示カウントをリセット
   */
  async resetViewCount(): Promise<void> {
    try {
      await AsyncStorage.setItem(STORAGE_KEY_AREA_VIEW_COUNT, '0');
    } catch (error) {
      console.error('Failed to reset view count:', error);
    }
  }

  /**
   * 広告を表示すべきかどうかを判定
   */
  private shouldShowAd(viewCount: number, frequency: InterstitialFrequency): boolean {
    if (frequency === 'none') {
      return false;
    }

    const threshold = frequency === 'every3' ? 3 : 5;
    return viewCount >= threshold;
  }

  /**
   * 次回広告表示の1回前かどうかを判定（プリロード用）
   */
  private shouldPreload(viewCount: number, frequency: InterstitialFrequency): boolean {
    if (frequency === 'none') {
      return false;
    }

    const threshold = frequency === 'every3' ? 3 : 5;
    return viewCount === threshold - 1;
  }

  /**
   * 広告をプリロード
   */
  async preload(): Promise<void> {
    if (this.isLoading || this.isLoaded) {
      return;
    }

    const unitId = this.getUnitId();
    this.isLoading = true;

    try {
      this.interstitialAd = InterstitialAd.createForAdRequest(unitId, {
        requestNonPersonalizedAdsOnly: true,
      });

      return new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          this.isLoading = false;
          reject(new Error('Ad load timeout'));
        }, 10000);

        this.interstitialAd!.addAdEventListener(AdEventType.LOADED, () => {
          clearTimeout(timeout);
          this.isLoading = false;
          this.isLoaded = true;
          console.log('AdMob interstitial ad loaded');
          resolve();
        });

        this.interstitialAd!.addAdEventListener(AdEventType.ERROR, (error) => {
          clearTimeout(timeout);
          this.isLoading = false;
          this.isLoaded = false;
          console.error('AdMob interstitial ad load error:', error);
          this.logAnalyticsError(error);
          reject(error);
        });

        this.interstitialAd!.load();
      });
    } catch (error) {
      this.isLoading = false;
      console.error('AdMob interstitial preload error:', error);
      throw error;
    }
  }

  /**
   * 広告を表示
   */
  async show(onClosed?: () => void): Promise<boolean> {
    if (!this.interstitialAd || !this.isLoaded) {
      console.log('AdMob interstitial ad not loaded');
      return false;
    }

    try {
      return new Promise((resolve) => {
        this.interstitialAd!.addAdEventListener(AdEventType.CLOSED, () => {
          this.isLoaded = false;
          this.interstitialAd = null;
          this.logAnalyticsShown();
          onClosed?.();
          resolve(true);
        });

        this.interstitialAd!.show();
      });
    } catch (error) {
      console.error('AdMob interstitial show error:', error);
      this.logAnalyticsError(error);
      return false;
    }
  }

  /**
   * エリア詳細画面遷移時のハンドラー
   * componentDidMountから呼び出す
   */
  async handleAreaDetailMount(): Promise<void> {
    try {
      // Adapty初期化待機
      await waitForAdaptyReady();

      // サブスク会員チェック
      const { isSubscribed } = await getSubscriptionStatus();
      if (isSubscribed) {
        console.log('AdMobInterstitialManager: サブスク会員のため広告非表示');
        return;
      }

      // A/Bテスト設定を取得
      const frequency = await ABTestHelper.getInterstitialFrequency();
      if (frequency === 'none') {
        console.log('AdMobInterstitialManager: A/Bテストで広告無効グループ');
        return;
      }

      // カウントをインクリメント
      const newCount = await this.incrementViewCount();
      console.log(`AdMobInterstitialManager: エリア詳細表示回数 ${newCount}`);

      // 広告表示判定
      if (this.shouldShowAd(newCount, frequency)) {
        console.log('AdMobInterstitialManager: 広告表示条件を満たしました');

        // プリロード済みなら表示、なければロード→表示
        if (this.isLoaded) {
          const shown = await this.show();
          if (shown) {
            await this.resetViewCount();
          }
        } else {
          // ロード→表示を試みる
          try {
            await this.preload();
            const shown = await this.show();
            if (shown) {
              await this.resetViewCount();
            }
          } catch (error) {
            console.error('AdMobInterstitialManager: 広告ロード失敗、カウントリセット', error);
            await this.resetViewCount();
          }
        }
      } else if (this.shouldPreload(newCount, frequency)) {
        // 次回表示のためにプリロード
        console.log('AdMobInterstitialManager: 次回表示のためプリロード開始');
        this.preload().catch((error) => {
          console.error('AdMobInterstitialManager: プリロード失敗', error);
        });
      }
    } catch (error) {
      console.error('AdMobInterstitialManager: handleAreaDetailMount error', error);
    }
  }

  /**
   * Firebase Analyticsに広告表示成功イベントを送信
   */
  private async logAnalyticsShown(): Promise<void> {
    try {
      await firebase.analytics().logEvent(EVENT_INTERSTITIAL_SHOWN, {
        ad_platform: 'admob',
        ad_format: 'interstitial',
        placement: 'area_detail',
      });
    } catch (error) {
      console.error('Failed to log analytics event:', error);
    }
  }

  /**
   * Firebase Analyticsに広告エラーイベントを送信
   */
  private async logAnalyticsError(error: any): Promise<void> {
    try {
      await firebase.analytics().logEvent(EVENT_INTERSTITIAL_FAILED, {
        ad_platform: 'admob',
        ad_format: 'interstitial',
        placement: 'area_detail',
        error_message: error?.message || 'Unknown error',
        error_code: error?.code || 'unknown',
      });
    } catch (analyticsError) {
      console.error('Failed to log analytics error event:', analyticsError);
    }
  }

  /**
   * リソースをクリーンアップ
   */
  destroy(): void {
    if (this.interstitialAd) {
      this.interstitialAd = null;
    }
    this.isLoading = false;
    this.isLoaded = false;
  }
}

// シングルトンインスタンスをエクスポート
export default new AdMobInterstitialManager();
```

---

### 2. エリア詳細画面（ShowView.js）への組み込み

**ファイル:** `app/views/areas/main/ShowView.js`

**変更内容**: componentDidMountでAdMobInterstitialManagerを呼び出し

```javascript
// import追加
import AdMobInterstitialManager from '@views/common/AdMobInterstitialManager';

// componentDidMountに追加
async componentDidMount() {
  // 既存の処理...

  // AdMobインタースティシャル広告のハンドリング
  AdMobInterstitialManager.handleAreaDetailMount();
}

// componentWillUnmountに追加（オプション）
componentWillUnmount() {
  // 既存の処理...

  // 必要に応じてクリーンアップ
  // AdMobInterstitialManager.destroy();
}
```

---

## 実装手順

### Phase 1: AppLovin削除

- [ ] `app/common/AppLovinAppOpenManager.ts` を削除
- [ ] `app/views/common/AppLovinInterstitial.ts` を削除
- [ ] `config/AppProvider.js` からApp Open広告の初期化コードを削除
- [ ] `app/views/posts/ShareSettingsView.js` からインタースティシャル広告コードを削除
- [ ] 環境変数（.env, .env.staging, .env.production）からAppLovinインタースティシャル/App Open関連の設定を削除

### Phase 2: AdMob導入

- [ ] `yarn add react-native-google-mobile-ads` を実行
- [ ] `npx pod-install` を実行（iOS）
- [ ] 環境変数にAdMobインタースティシャルのユニットIDを追加
- [ ] app.jsonのAdMob設定を確認（既存設定があるはず）

### Phase 3: A/Bテスト拡張

- [ ] `app/helpers/ABTestHelper.ts` に `InterstitialFrequency` 型を追加
- [ ] `ABTestConfig` インターフェースに `interstitialFrequency` を追加
- [ ] `generateRandomConfig()` にA/Bテスト振り分けロジックを実装
- [ ] `getInterstitialFrequency()` メソッドを追加
- [ ] AsyncStorage/Firebaseの保存・同期処理を追加

### Phase 4: AdMobインタースティシャル実装

- [ ] `app/views/common/AdMobInterstitialManager.ts` を新規作成
- [ ] プリロード機能を実装
- [ ] 表示機能を実装
- [ ] カウント管理機能を実装
- [ ] Firebase Analyticsイベント送信を実装

### Phase 5: エリア詳細画面への組み込み

- [ ] `app/views/areas/main/ShowView.js` にimportを追加
- [ ] componentDidMountで `handleAreaDetailMount()` を呼び出し
- [ ] 動作確認

### Phase 6: 動作確認・テスト

- [ ] A/Bテストの各グループで正しく動作することを確認
- [ ] 3回ごと表示グループでの動作確認
- [ ] 5回ごと表示グループでの動作確認
- [ ] 非表示グループでの動作確認
- [ ] サブスク会員での広告非表示確認
- [ ] Firebase Analyticsでイベントが送信されることを確認

---

## 関連ファイル

### 変更対象

| ファイル | 変更内容 |
|---------|----------|
| `app/helpers/ABTestHelper.ts` | InterstitialFrequency型追加、A/Bテスト振り分けロジック追加 |
| `app/views/areas/main/ShowView.js` | AdMobInterstitialManager呼び出し追加 |
| `config/AppProvider.js` | App Open広告初期化コード削除 |
| `app/views/posts/ShareSettingsView.js` | AppLovinインタースティシャル関連コード削除 |
| `.env` | AdMobインタースティシャルユニットID追加、AppLovin関連削除 |
| `.env.staging` | 同上 |
| `.env.production` | 同上 |
| `package.json` | react-native-google-mobile-ads追加 |

### 削除対象

| ファイル | 理由 |
|---------|------|
| `app/common/AppLovinAppOpenManager.ts` | App Open広告削除 |
| `app/views/common/AppLovinInterstitial.ts` | インタースティシャル広告をAdMobに置き換え |

### 新規作成

| ファイル | 説明 |
|---------|------|
| `app/views/common/AdMobInterstitialManager.ts` | AdMobインタースティシャル広告マネージャー |

---

## 確認事項

- [ ] TypeScriptエラー: 0件
- [ ] ESLintエラー: 0件
- [ ] iOS実機での動作確認
- [ ] Android実機での動作確認
- [ ] A/Bテスト各グループでの広告表示確認
- [ ] Firebase Analyticsでのイベント確認
- [ ] サブスク会員での広告非表示確認

---

## 注意事項

- **テスト用ユニットID**: 開発中はGoogleが提供するテスト用ユニットID（`ca-app-pub-3940256099942544/...`）を使用すること。本番リリース時に実際のユニットIDに差し替える
- **AppLovinバナー/MREC**: 引き続きAppLovinを使用するため、`react-native-applovin-max`と`AppLovinBanner.tsx`、`AppLovinMREC.tsx`は削除しない
- **既存のA/Bテスト設定との互換性**: 既存ユーザーは新しい`interstitialFrequency`フィールドが未設定のため、初回アクセス時にランダム振り分けが行われる

---

## 壁打ち決定事項サマリー

### 質問と回答一覧

| # | 質問 | 決定 |
|---|------|------|
| 1 | 広告SDKの選択 | B - AppLovinを残したまま、インタースティシャルのみAdMobに変更（ハイブリッド構成） |
| 2 | A/Bテストのグループ振り分けロジック | A - アプリ内でABTestHelper.tsを拡張して振り分け |
| 3 | 累計カウントの永続化方法 | A - AsyncStorageで永続化（アプリ削除まで保持） |
| 4 | AppLovinの削除範囲 | B - App Open広告 + インタースティシャル広告を削除（バナー/MRECはAppLovinで残す） |
| 5 | AdMob SDKの導入方法 | B - 既存のAdMob設定を復活させて使用 |
| 6 | サブスク会員の扱い | A - サブスク会員には広告を表示しない（既存動作を踏襲） |
| 7 | エリア詳細画面への遷移検知方法 | A - componentDidMountで初回マウント時のみカウント |
| 8 | 広告表示のタイミング | B - 画面表示後に広告を出す |
| 9 | 広告ロード失敗時の挙動 | B - 失敗したらカウントをリセットして、次のN回目まで待つ |
| 10 | A/Bテストのグループ振り分けタイミング | A - アプリ初回起動時に振り分け（以降は固定） |
| 11 | Firebase Analyticsへのイベント送信 | B - 広告表示成功 + 失敗時の両方でイベント送信 |
| 12 | AdMob広告ユニットIDの管理 | A - 環境変数（.env）で管理 |
| 13 | AdMobインタースティシャルのユニットID | A - 既存のAdMobユニットIDを使用（過去の実装で使ってたもの） |
| 14 | プリロードの実装 | A - プリロードあり（N-1回目の遷移時に次の広告をプリロード） |
| 15 | 削除対象のAppLovinファイル確認 | A - 提示した削除/残す方針でOK |

### 保留事項

| 項目 | 理由 |
|------|------|
| なし | 全ての要件が明確化された |
