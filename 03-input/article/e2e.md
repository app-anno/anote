@Masahiro Anno_1/22午前休_1/23全休 @Shunsuke Igarashi
ウェルスナビの方、我々と同じ状況下でのテストを追加なので参考になるかもしれません！

Android / iOSアプリのE2Eテスト全部で250シナリオを自動化しました！
モバイルアプリにおけるE2Eテストの自動化 ← 特にこちら
https://zenn.dev/coconala/articles/a3a5e33cd1d981
https://zenn.dev/wn_engineering/articles/b0c174e0913a30

現職でやっているアプリのe2eテストでplaywrigthのmcpを使ってみています
（今触り始めた）
https://github.com/microsoft/playwright-mcp
7 件の返信Ukyo Mashiko 12/8卒  [17:54]
Playwrightって業界的に評価やっぱり良いんですかね？

Playwrightはスクロールがうまく使えない印象で、Seleniumの方が柔軟性高いなって感じてます
[移行しました]Shinya Azuma  [18:49]
僕もPythonでselenium書くこと多かったので、慣れてはいるんですけど、playwrightはwait_for_selectorで要素出てくるの待ってくれたりするのが便利だったりして使ってみています  
(ただ、seleniumのほうが調整しやすいってのもわかる )
Ukyo Mashiko 12/8卒  [18:54]
なるほど〜〜という反面、sleepとか完全に読み込みするまで待つようにこちら側でSeleniumで制御すれば良いだけじゃん？みたいな気持ちもあってモヤモヤしますねw

テストを気軽にかけるって意味ではPlaywrightの方が上手なんでしょうね 
（Seleniumは腰が重いw） （編集済み） 
[移行しました]Shinya Azuma  [06:32]
まじでそれですね 
表示遅延することあるから余分にsleepさせて調整しようとか、idでうまくボタン押せないからxpath使おうとか柔軟にいろいろできるからSeleniumでいいじゃん！は僕もそう思いますw

今回playwright mcp使ってみようって思ったのが、アクセシビリティツリーを使って要素の検索とかをしてくれるみたいなんですよね
自然言語でいろいろテストできそうだから非エンジニアでもCaludeとか使えればテスト楽なんじゃないか？みたいな感じで、とりあえず触ってみるかーっと思った昨日でした！
（急遽MTG呼ばれる&子供のお風呂とかで結局mcp設定してブラウザ立ち上げるところまでしかできなかったから今日リトライ←） （編集済み） 
Ukyo Mashiko 12/8卒  [13:21]
前にブラウザを自動操作してもらって居酒屋探してもらったんですけど、スクロールしてくれなくて、使えなかったんですよね  

https://devanglersjp.slack.com/archives/C074YMXNH50/p1744789415824109
Playwright MCPとCursorで居酒屋探し
画面収録 2025-04-16 16.38.31.mov 1xtimes_engineers 内のスレッド | 2025年4月16日 | メッセージを確認する[移行しました]Shinya Azuma  [13:27]
そういうことなんですね
Playwright mcpがすでに酒飲んで酔ってる説Ukyo Mashiko 12/8卒  [13:46]
クロールできないのは相当酔ってますねw
帰らせたほうがいいですw