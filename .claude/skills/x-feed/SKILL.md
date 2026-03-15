---
name: x-feed
description: "トレンド情報をX(Twitter)風スクロールフィードHTMLに変換"
triggers:
  - "x-feed"
  - "/x-feed"
  - "フィード"
  - "feed"
  - "トレンドフィード"
---

# X-Feed スキル

info-collectorスキルが生成する`YYYYMMDD-trend.md`を、X(Twitter)風のスクロールフィードHTMLに変換して表示する。

## 実行手順

### 1. トレンドMD特定

1. 引数としてファイルパスが指定されている場合はそのパスを使用
2. 指定がなければ、Globツールで `anote/03-input/information/*-trend.md` を検索
3. 最新の日付のファイルを選択
4. ファイルが見つからない場合はエラーメッセージを出力して終了

### 2. MD読み込み

Readツールでトレンドファイルの全文を取得する。

### 3. パース

MDの内容を以下のルールに従って統一データ構造に変換する。

#### 統一記事データ構造

各記事を以下のフィールドに正規化する:

- `title`: 記事タイトル
- `url`: 記事URL（なければ空文字）
- `source`: ソース識別子（`hatena`, `hn`, `reddit-tech`, `paleo`, `pubmed`, `claude-code`, `reddit-fitness`）
- `sourceLabel`: 表示用ラベル（`はてブ`, `HN`, `Reddit`, `パレオな男`, `PubMed`, `Claude Code`, `Reddit Fitness`）
- `stars`: 興味度（3, 2, 1, 0）
- `metric`: 数値指標の単位（`users`, `pt`, `ups`, なし）
- `metricValue`: 数値指標の値（数値）
- `category`: カテゴリ文字列
- `summary`: 概要/メモ文字列

#### セクション別パースルール

| セクション | 見出し判定 | 形式 | パースルール |
|-----------|-----------|------|------------|
| Claude Code最新情報 | `## Claude Code` | テーブル | `\|`行を分割。各行: 項目=title、詳細=summary、ソースリンクからurl抽出。興味度なし→★★(stars=2)扱い |
| はてブIT 注目トピック | `### 注目トピック` (はてブセクション内) | テーブル | タイトル列からtitle/url、ブクマ数→metricValue(metric=users)、興味度→stars、カテゴリ→category、メモ→summary |
| はてブIT 全エントリー | `### 全エントリー` (はてブセクション内) | 番号リスト | `N. [title](url) (Nnn users) - 概要` パターン。stars=0（注目に含まれないため） |
| HN 注目トピック | `### 注目トピック` (HNセクション内) | テーブル | はてブ注目と同形式。metric=pt |
| HN 全エントリー | `### 全エントリー` (HNセクション内) | 番号リスト | `N. [title](url) (Nnnpt) - 概要` パターン。stars=0 |
| Reddit テック系 注目 | `### 注目トピック` (Reddit テック系セクション内) | テーブル | 投票数→metricValue(metric=ups)、コメント数も取得、サブレッド情報あり |
| Reddit テック系 エントリー | `### カテゴリ別エントリー` (Reddit テック系内) | 番号リスト | `N. [title](url) (NN ups, NN comments) - r/sub - 概要` |
| パレオな男 | `## パレオな男` | テーブル | タイトル/url、カテゴリ、興味度、アプリ活用メモ→summary。metric不要 |
| PubMed | `## PubMed` | テーブル×3 | H3サブセクション(`### 運動・筋トレ系`, `### 栄養・食事系`, `### 睡眠・リカバリー系`)でカテゴリ分け。論文タイトル→title/url、ジャーナル情報、興味度→stars、主要知見→summary |
| Reddit フィットネス系 注目 | `### 注目トピック` (Reddit フィットネス系セクション内) | テーブル | Reddit テック系と同形式 |
| Reddit フィットネス系 エントリー | `### カテゴリ別エントリー` (Reddit フィットネス系内) | 番号リスト | Reddit テック系エントリーと同形式 |

#### 重複排除

URLをキーにして重複を排除する。注目トピック（テーブル形式、stars付き）を優先し、全エントリー（リスト形式）の同一URL記事はスキップする。

#### スキップ条件

- 「新規記事なし」「記事なし」等のテキストを含むセクション → そのセクション全体をスキップ
- タイトルが空の行 → スキップ

### 4. 記事コンテンツ取得（★★★記事のみ）

トレンドMDには各記事の一言サマリーしか含まれていないため、★★★記事については実際の記事コンテンツを取得してリッチなサマリーを生成する。

1. ★★★記事のうちURLがある記事を対象とする
2. Pythonスクリプト（`generate_feed.py`）が自動的に以下を実行:
   - 各URLにHTTPリクエストを送信（並列10ワーカー、タイムアウト10秒）
   - HTMLから`<article>`または`<main>`要素のテキストを抽出
   - 取得できない場合は`<meta name="description">`を代用
   - それでも取得できない場合はMDの一言サマリーをそのまま使用
3. 取得したテキストの先頭800文字をsummaryとして使用
4. スライド（speakerdeck等）やGitHub Releasesなど、テキスト取得が難しいサイトはMDサマリーで代用

**注意**: ★★以下の記事はMDの一言サマリーをそのまま使用する（取得コスト削減のため）。

### 5. ソート

1. stars降順（★★★=3 → ★★=2 → ★=1 → なし=0）
2. 同一stars内ではmetricValue降順（数値が大きい順）
3. metricValueがない記事は同一stars内で末尾

### 6. HTML生成

1. Readツールで `.claude/skills/x-feed/assets/feed-template.html` テンプレートを読み込む
2. パースした記事データをHTMLカードに変換
3. 各記事を以下のHTML構造で生成:

```html
<article class="card" data-stars="3" data-source="hatena">
  <div class="card-header">
    <span class="source-badge hatena">はてブ</span>
    <span class="stars">★★★</span>
    <span class="metric">239 users</span>
  </div>
  <h2 class="card-title"><a href="URL" target="_blank" rel="noopener">タイトル</a></h2>
  <div class="card-body">
    <p class="card-text">概要テキスト</p>
  </div>
  <div class="card-footer">
    <span class="category-tag">カテゴリ</span>
  </div>
</article>
```

- urlが空の場合は`<a>`タグなしでタイトルのみテキスト表示
- summaryが空の場合はcard-bodyを省略
- starsが0の場合はstars spanを省略
- metricValueがない場合はmetric spanを省略

4. テンプレート内のプレースホルダーを置換:
   - `{{FEED_ITEMS}}` → 生成したカードHTML
   - `{{GENERATED_DATE}}` → トレンドMDの日付（YYYY-MM-DD形式）
   - `{{TOTAL_COUNT}}` → 総記事数

5. 完成したHTMLを `anote/03-input/information/YYYYMMDD-feed.html` として保存
   - YYYYMMDDはトレンドMDのファイル名から取得

### 7. 自動オープン

Bashツールで `open "anote/03-input/information/YYYYMMDD-feed.html"` を実行し、デフォルトブラウザで表示する。

## 折りたたみルール

- 全記事共通: 480文字まで全文表示、超過分は「続きを読む」ボタンで展開/折りたたみ
- ★による文字数制限の差はなし（一律480文字）

これらの折りたたみはテンプレートのJavaScriptで制御される。
