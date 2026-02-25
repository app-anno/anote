# Firebase × BigQuery で実現する、React Nativeアプリを確実に成長させる仕組みづくり

## LTスクリプト（10分）

---

### 1. 自己紹介 & 問いかけ（2分）

はい、じゃあ始めさせていただきます。「Firebase × BigQuery で実現する、React Nativeアプリを確実に成長させる仕組みづくり」というテーマで発表させていただきます。

まず自己紹介なんですけど、React NativeとReactをメインで4年ほどやっていて、Laravelでバックエンドも書いたりしてます。あとはデータ分析もやっていて、BigQueryとTableauを使ってKPI設計だったりA/Bテストの分析基盤を作ったりしてました。

---

で、今日話す内容なんですけど、React NativeアプリでA/Bテストを並列で回してグロースさせる仕組みを、FirebaseとBigQueryだけで作る方法を共有します。

自分はもともと全然グロースできてなくて、最初のベンチャーで2年間いろいろ機能作ったのに日の収益300円から伸びなかったり、副業で某大手車メーカーとか大手玩具メーカーのアプリを開発したのにストアの評価が星2だったりっていう経験がありました。

で、その後ゲームアプリの事業部で3人チームでA/Bテストをちゃんと回すようにしたら、ほぼゼロから累計1,500万ダウンロードまで1年で伸ばせたんですよね。

ハーバードの研究でも、A/Bテストを導入したスタートアップは1年後にパフォーマンスが30〜100%向上するっていうデータが出てます。最近AIで開発は速くなったんですけど、速く作れても検証しないとグロースしないんで、その仕組みの部分を具体的なコード付きで共有できたらなと思います。

今日はこんな順番で話します。

---

**＜今日話すこと＞**

1. **A/Bテストの回し方** — 1本ずつ → 並列で回す
2. **仕組みの全体像** — Firebase × BigQueryの下準備
3. **実装と運用** — コンポーネントの出し分けとBigQueryでの分析
4. **結果の判定** — 勝ち/負け/ニュートラル/微差の4分類

FirebaseとBigQueryだけでできるんで、わりと個人開発でもいけるレベル感の話です。

---

### 2. A/Bテストの回し方（1.5分）

で、A/Bテストの回し方なんですけど、普通は1本ずつ回すと思うんですよね。A群とB群にユーザーを分けて、だいたい300人くらいで有意差が見えてくるんで、300人テストして結果見て、次の300人でまたテストして、っていうのを順番にやっていく。

これだと検証スピードが全然出ないんですよね。月に1〜2本しかテストできない。特にユーザー数がそこまで多くないアプリだと致命的で、1本終わるまで次が回せないから、仮説の検証がめちゃくちゃ遅い。

で、まず一つ知っておいてほしいのが、A/BテストってAとBの2パターンだけじゃなくて、**A・B・C・D群みたいに1つのテストで複数パターン同時に比較できる**んですよね。たとえばボタンの色を4パターン試したいなら、4群に分けて一気に回せる。わざわざ2つずつ比較する必要がないんですよ。

で、さらにそこから気づいたのが、**テスト自体も並列で回せる**ということ。ランダムセグメントでユーザーを区切れば、テスト同士が干渉しない。これに切り替えてから、週に7〜8本同時にA/Bテストを回せるようになりました。月1〜2本だったのが、週7〜8本。検証のスピード感が根本的に変わったんですよね。

---

### 3. 仕組みの全体像（2分）

仕組みの全体像なんですけど、めちゃくちゃシンプルです。

大きく言うと、**Firebase SDK → ログ送信 → BigQueryに自動エクスポート → クエリで分析**。これだけです。

#### ① 下準備：ExpoにFirebaseを入れてBigQuery連携する

まずExpoのReact NativeプロジェクトにFirebase SDKを入れます。`@react-native-firebase/app` と `@react-native-firebase/analytics` をインストールします。**注意点として、Expo Goでは動作しないので、Development Build（カスタムDev Client）が必要です**。

セットアップの流れとしては：

1. `npx expo install expo-dev-client @react-native-firebase/app @react-native-firebase/analytics`
2. Firebaseコンソールからアプリを登録して、`google-services.json`（Android）と `GoogleService-Info.plist`（iOS）をプロジェクトルートに配置
3. `app.json` に Config Plugin を設定：

```json
{
  "expo": {
    "android": {
      "googleServicesFile": "./google-services.json"
    },
    "ios": {
      "googleServicesFile": "./GoogleService-Info.plist"
    },
    "plugins": [
      "@react-native-firebase/app",
      "@react-native-firebase/analytics",
      [
        "expo-build-properties",
        {
          "ios": {
            "useFrameworks": "static"
          }
        }
      ]
    ]
  }
}
```

4. `npx expo prebuild` → `npx expo run:ios` / `npx expo run:android`、またはEAS Buildでビルド

で、FirebaseコンソールからBigQueryエクスポートを有効にする（プロジェクト設定 → 統合 → BigQuery でリンク設定）。これでFirebaseのログが自動でBigQueryに流れる状態になります。

#### ② ユーザーの振り分け方法

ここがキモなんですけど、Firebaseの **ユーザープロパティ** を使います。

やることはシンプルで、ユーザーがアプリを起動した時に、テスト項目ごとに `Math.random()` で0〜1の乱数を生成して、閾値で振り分けるだけです。たとえば0.5未満ならA群、0.5以上ならB群、みたいな感じ。

で、ポイントなのが、**テスト項目ごとに独立した乱数で判定する**ということ。ナビゲーションUIのテスト、広告表示のテスト、新機能のテスト、それぞれ別の乱数で振り分けるんで、テスト同士が干渉しないんですよね。だから並列で回せる。

振り分けた結果は `AsyncStorage` に保存して永続化します。一度決まったグループは変わらないようにする。これが大事で、途中でグループが変わるとデータがノイズまみれになるんで。

#### ③ Firebaseユーザープロパティへの同期

で、保存したグループ情報を `analytics().setUserProperty(name, value)` でFirebaseのユーザープロパティとして送る。これがめちゃくちゃ重要で、**ユーザープロパティに入れておくと、以降そのユーザーが送る全てのイベントログに自動でA/B情報が紐づく**んですよね。イベントごとにいちいちパラメータを仕込まなくていい。BigQueryに流れてきたデータをクエリで叩けば、A群とB群で「この指標に差があるか」がすぐわかります。

**注意点として、カスタムユーザープロパティは1プロジェクトあたり最大25個までです**。並列でテストを回す場合はこの上限を意識して、終了したテストのプロパティは使い回すなどの運用が必要になります。

---

### 4. 実装と運用（2.5分）

React Nativeでの実装なんですけど、流れとしては「乱数振り分け → 永続化 → Firebase同期 → コンポーネント出し分け」です。

まず振り分けのコアロジックなんですけど、テスト項目ごとに `Math.random()` と設定した比率を比較して判定します。

```tsx
// ABTestHelper.ts のイメージ

// テストごとの比率設定
const RATIOS = {
  testNavUI: 0.5,        // 50%にA群を適用
  testRecommend: 0.5,
  testAdFormat: 0.3,     // 30%にA群を適用
};

// 乱数による独立振り分け
function generateConfig() {
  return {
    testNavUI: Math.random() < RATIOS.testNavUI ? 'A' : 'B',
    testRecommend: Math.random() < RATIOS.testRecommend ? 'A' : 'B',
    testAdFormat: Math.random() < RATIOS.testAdFormat ? 'A' : 'B',
  };
}
```

各テストが独立した乱数で判定されるんで、全ての組み合わせが発生しうる設計です。これで複数テストが干渉しない。

で、これを `AsyncStorage` に保存して永続化する。次回起動時は保存された設定を優先して読み込むんで、ユーザーのグループが勝手に変わることがない。

```tsx
// 永続化
await AsyncStorage.setItem('ab_config', JSON.stringify(config));

// Firebase同期（ユーザープロパティとして送信）
await Promise.all(
  Object.entries(config).map(([name, value]) =>
    analytics().setUserProperty(name, value)
  )
);
```

`analytics().setUserProperty()` でユーザープロパティとして送るのがポイントで、イベントパラメータじゃなくてプロパティにすることで、全てのイベントログに自動でA/B情報が紐づきます。

コンポーネントの出し分けは、取得した設定値で条件分岐するだけ。

```tsx
const abConfig = useABTestConfig();

if (abConfig.testNavUI === 'A') {
  return <NewNavigationUI />;
}
return <DefaultNavigationUI />;
```

---

#### 実際にBigQuery上でどう見えるか

で、BigQueryでどんな感じでデータが入ってくるかっていうと、Firebase Analyticsのイベントデータのテーブルに `user_properties` っていうカラムがあって、そこにさっき `setUserProperty` で送った値がちゃんと入ってます。

なので、たとえば「testNavUIがAのユーザー」と「Bのユーザー」で継続率とか広告収益とかを比較するクエリを書けば、テストの結果がすぐわかる。

```sql
SELECT
  (SELECT value.string_value
   FROM UNNEST(user_properties)
   WHERE key = 'testNavUI') AS test_group,
  COUNT(DISTINCT user_pseudo_id) AS users,
  -- 継続率、広告収益、CVRなど見たいKPIを集計
FROM
  `project.analytics_xxxxx.events_*`
WHERE
  _TABLE_SUFFIX BETWEEN '20250201' AND '20250228'
GROUP BY
  1
```

こんな感じで、テスト群とコントロール群のKPIが並んで出てくるんで、どっちが良かったかが一目でわかります。

---

#### Tips: BigQuery MCP がめちゃくちゃ便利

ちなみにちょっとしたTipsなんですけど、最近BigQueryのMCPサーバーっていうのがあって、Claude CodeとかCursor上からBigQueryに直接クエリを投げられるんですよね。

なので、わざわざBigQueryのコンソール開かなくても、Claude Codeに「このテストの結果出して」って聞けば、クエリ書いてくれて、結果まで出してくれる。分析のスピードがさらに上がるんで、めちゃくちゃおすすめです。

---

### 5. 判定と意思決定 & まとめ（2分）

結果の判定なんですけど、自分は4パターンで考えてます。**勝ち、負け、ニュートラル、微差**。

正直、有意差がつく「勝ち」ってそんなに多くないです。でも「負け」がわかることもめちゃくちゃ大事で、ユーザーに求められてない機能を早く切れる。ハーバードの研究でも、A/Bテストをやってるスタートアップはスケールするか早く撤退するかのどちらかになる、つまり**中途半端な停滞が減る**っていう結果が出てるんですよね。

で、ニュートラルの時、つまりどっちでも変わらない時はどうするかっていうと、開発体験が良い方とか、コードがシンプルな方を採用します。ユーザーにとって変わらないなら、開発しやすい方を選んだ方がその後の改善スピードが上がるんで。

微差の場合は、もう少しN数を増やして様子を見るか、別の切り口でテストし直すかを判断します。

---

まとめると、**AIで速く作れる時代になったからこそ、速くリリースして、ユーザーの反応をデータで見て、確実に成長させるサイクルを回す**。これが大事だと思ってます。

FirebaseとBigQueryだけでこの仕組みは作れるんで、個人開発でも、少人数のチームでも、ぜひ試してみてほしいなと思います。

ご清聴ありがとうございました！

あ、最後に一個だけ。実はこのLT登壇するって決めてからちょっと会社が潰れちゃいまして（笑）。もしこんなやつでよければ、お仕事のお声がけとかいただけるとめちゃくちゃ嬉しいです。ありがとうございました！

---

## 参考文献

- **Experimentation and startup performance: Evidence from A/B testing**
  - Rembrand Koning (Harvard Business School), Sharique Hasan (Duke), Aaron Chatterji (Duke)
  - A/Bテスト導入後1年でスタートアップのパフォーマンスが30〜100%向上
  - 早期ステージのスタートアップほど効果が大きい
  - https://www.hbs.edu/ris/Publication%20Files/AB_Testing_R_R_08b97538-ed3f-413e-bc38-c239b175d868.pdf