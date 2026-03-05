---
name: info-collector
description: "アプリグロース・マーケ・UX・AI開発ツール・フィットネス科学に特化した情報収集"
triggers:
  - "情報収集"
  - "info-collector"
  - "トレンド"
  - "ネタ集め"
  - "/info-collector"
  - "フィットネス"
  - "fitness"
---

# 情報収集スキル（info-collector）

アプリグロース・マーケ・UX・AI開発ツール・フィットネス科学を中心に、はてなブックマークIT人気エントリー、Hacker News、Reddit、Claude Code公式情報、パレオな男、PubMedメタ分析を収集し、`anote/03-input/information/YYYYMMDD-trend.md` に保存する。

## 実行手順

### 0. 興味領域の定義

以下の10の興味領域を基準に記事を評価する：

1. **アプリグロース・マーケティング** — アプリマーケ、広告（TikTok/SNS）、ASO、Push通知、ポイ活、サブスク収益化
2. **UX/UI・プロダクトマネジメント** — ユーザー体験、認知負荷、N1分析、ユーザーインタビュー
3. **AI駆動開発** — Claude Code、Devin、Cursor、AI活用事例、LLM開発ツール
4. **React Native / Expo** — CNG移行、EAS Update、React DOM、クロスプラットフォーム
5. **チーム・組織・開発生産性** — リーダーシップ、スクラム、CI/CD、開発生産性
6. **ビジネス・事業戦略** — プロダクト戦略、グロースハック、スタートアップ
7. **フィットネス・運動科学** — 筋トレ（レジスタンストレーニング）、有酸素運動、HIIT、運動プログラミング、身体パフォーマンス、メタ分析
8. **栄養・食事** — マクロ栄養素、サプリメント、食事タイミング、プロテイン、腸内環境、ダイエット
9. **睡眠・リカバリー** — 睡眠の質、リカバリー戦略、ストレス管理、HRV、オーバートレーニング
10. **健康科学・エビデンス** — メタ分析、システマティックレビュー、RCT、行動変容、メンタルヘルスと運動

### 1. 重複排除の準備

1. `anote/03-input/information/collected-history.md` をReadツールで読み込む
2. ファイル内の全URLをリストとして保持する
3. 以降の収集ステップで、各記事URLをこのリストと照合し、既出URLの記事は出力から除外する
4. 新規記事のURLのみを収集結果に含める

### 2. Claude Code 公式情報の収集

以下のソースからClaude Code関連の最新情報を取得：

**Anthropicエンジニアリングブログ**
- https://www.anthropic.com/engineering
- WebFetchツールで最新記事をチェック
- Claude Code、Claude API、開発ツール関連の記事を抽出

**GitHub Releases**
- Bashツールで以下を実行：
```bash
gh api repos/anthropics/claude-code/releases --jq '.[0:5] | .[] | "\(.tag_name)|\(.name)|\(.published_at)|\(.html_url)"'
```
- 最新5件のリリース情報を取得

**Changelog**
- https://docs.anthropic.com/en/docs/claude-code/changelog
- WebFetchツールで最新の変更点を取得

### 3. はてブIT（日本市場）の収集

以下の4カテゴリから人気エントリーを取得（WebFetchツール使用）：

- https://b.hatena.ne.jp/hotentry/it （IT総合）
- https://b.hatena.ne.jp/hotentry/it/%E3%83%97%E3%83%AD%E3%82%B0%E3%83%A9%E3%83%9F%E3%83%B3%E3%82%B0 （プログラミング）
- https://b.hatena.ne.jp/hotentry/it/AI%E3%83%BB%E6%A9%9F%E6%A2%B0%E5%AD%A6%E7%BF%92 （AI・機械学習）
- https://b.hatena.ne.jp/hotentry/it/%E3%82%A8%E3%83%B3%E3%82%B8%E3%83%8B%E3%82%A2 （エンジニア）

取得項目：
- 各エントリーの**タイトル、元記事URL、ブックマーク数**を必ず取得すること
- はてブのエントリーページURLではなく、リンク先の元記事URLを抽出
- 重複排除：既出URLの記事は除外

### 4. Hacker News（グローバル）の収集

- https://news.ycombinator.com/
- WebFetchツールで取得
- 各記事の**タイトル、HNコメントページURL（`https://news.ycombinator.com/item?id=XXXXX`形式）、ポイント数**を取得
- **元記事URLではなくHNのコメントページURLを使用すること**
- **タイトルは日本語に翻訳して出力**
- 重複排除：既出URLの記事は除外

### 5. Reddit テック系（9サブレッド）の収集

**重要**: WebFetchツールはreddit.comをブロックするため、**Bashツールでcurlコマンドを使用**すること。
各サブレッドから `/hot.json?t=day&limit=10` で上位10件を取得。
**old.reddit.com**を使用（www.reddit.comではない）。
User-Agentヘッダーを設定: `"User-Agent: info-collector/1.0 (trend analysis tool)"`

取得例（Bashツールで実行）:
```bash
curl -s -H "User-Agent: info-collector/1.0 (trend analysis tool)" \
  "https://old.reddit.com/r/programming/hot.json?t=day&limit=10" | \
  jq -r '.data.children[] | "\(.data.title)|\(.data.ups)|\(.data.num_comments)|https://www.reddit.com\(.data.permalink)"'
```

データ構造:
- `data.children[].data.title`: タイトル
- `data.children[].data.ups`: 投票数
- `data.children[].data.num_comments`: コメント数
- `data.children[].data.permalink`: パス（`https://www.reddit.com` + permalink で完全URL）

**対象サブレッド（9つ）：**

AI開発ツール系（1サブレッド）:
- r/ClaudeCode

React Native/Expo系（2サブレッド）:
- r/reactnative
- r/expo

コア技術系（3サブレッド）:
- r/programming
- r/javascript
- r/webdev

テクノロジー系（1サブレッド）:
- r/technology

アプリビジネス系（2サブレッド）:
- r/AppBusiness
- r/startups

取得項目：
- 各記事の**タイトル、Redditコメントページの完全URL、投票数（ups）、コメント数**を取得
- **タイトルは日本語に翻訳して出力**
- 重複排除：既出URLの記事は除外

### 6. パレオな男（フィットネス・健康科学ブログ）の収集

- https://yuchrszk.blogspot.com/
- WebFetchツールでトップページを取得
- 最新記事（10件程度）の**タイトル、記事URL、投稿日**を抽出
- 記事はエビデンスベース（メタ分析・RCT紹介）の健康・フィットネス情報が中心
- 重複排除：既出URLの記事は除外

**カテゴリ分類の目安**（記事タイトルから判断）:
- 筋トレ・運動 → フィットネス・運動科学
- 食事・サプリ・栄養 → 栄養・食事
- 睡眠・ストレス・回復 → 睡眠・リカバリー
- メンタルヘルス・行動変容 → 健康科学・エビデンス

### 7. PubMed メタ分析（運動・栄養・睡眠）の収集

以下の検索クエリでPubMedから最新のメタ分析・システマティックレビューを取得（WebFetchツール使用）。
各クエリで最新5件程度を取得する。

**検索クエリ（3つ並列実行）:**

1. 運動・筋トレ系:
   - `https://pubmed.ncbi.nlm.nih.gov/?term=(exercise+OR+resistance+training+OR+aerobic+exercise+OR+HIIT)+AND+(meta-analysis+OR+systematic+review)&filter=dates.2025%2F1%2F1-&sort=date&size=10`

2. 栄養・食事系:
   - `https://pubmed.ncbi.nlm.nih.gov/?term=(nutrition+OR+protein+OR+supplement+OR+diet)+AND+(exercise+OR+fitness)+AND+(meta-analysis+OR+systematic+review)&filter=dates.2025%2F1%2F1-&sort=date&size=10`

3. 睡眠・リカバリー系:
   - `https://pubmed.ncbi.nlm.nih.gov/?term=(sleep+OR+recovery+OR+stress)+AND+(exercise+OR+physical+activity)+AND+(meta-analysis+OR+systematic+review)&filter=dates.2025%2F1%2F1-&sort=date&size=10`

取得項目：
- **論文タイトル（日本語訳）、PubMed URL、掲載ジャーナル名、出版年**
- 可能であればアブストラクトから**主要な知見を1行で要約**
- 重複排除：既出URLの論文は除外

### 8. Reddit フィットネス系サブレッド（5つ）の収集

**既存のReddit収集（ステップ5）と同じ方式で取得。** Bashツールでcurlコマンドを使用。
各サブレッドから `/hot.json?t=day&limit=10` で上位10件を取得。

**対象サブレッド（5つ）：**

フィットネス・筋トレ系（3サブレッド）:
- r/fitness
- r/bodyweightfitness
- r/weightroom

栄養系（1サブレッド）:
- r/nutrition

睡眠系（1サブレッド）:
- r/sleep

取得項目：
- 各記事の**タイトル、Redditコメントページの完全URL、投票数（ups）、コメント数**を取得
- **タイトルは日本語に翻訳して出力**
- 重複排除：既出URLの記事は除外

### 9. 分析・興味度判定

収集した情報を以下の基準で評価：

**興味度の定義**:
- ★★★: アプリグロース、マーケ、UX、Claude Code/AI開発ツール、React Native/Expo に直接関連。フィットネスアプリに活かせる運動・栄養・睡眠のエビデンス（メタ分析・RCT）に直接関連
- ★★: 開発生産性、チーム組織、ビジネス戦略、技術トレンド全般。フィットネス・健康関連の一般的な知見やトレンド
- ★: 一般的なIT/技術ニュース。一般的な健康情報

**カテゴリラベル**:
- アプリグロース / マーケ / UX / AI開発 / RN/Expo / 開発生産性 / ビジネス戦略 / 技術全般
- フィットネス・運動科学 / 栄養・食事 / 睡眠・リカバリー / 健康科学・エビデンス

**分析の観点**:
- 興味領域への関連度が高い記事を「注目トピック」として最上位に配置
- ポイント数/ブックマーク数/投票数が高い記事は特に注目
- 議論が活発なトピック（コメント数が多い）を優先
- 日本のエンジニアに刺さりやすい話題を重視
- フィットネスアプリの機能開発に直結するエビデンス（運動プログラム設計、栄養ガイダンス、睡眠改善）を特に重視
- メタ分析・システマティックレビューはエビデンスレベルが高いため優先的にピックアップ

### 10. 出力

**まず「情報収集完了。」というメッセージを返してから、結果を出力ファイルに保存。**

出力先: `anote/03-input/information/YYYYMMDD-trend.md`（YYYYMMDDは実行日の日付）

出力テンプレートは `~/.claude/skills/info-collector/assets/output-template.md` を参照。

出力ファイルの構成:
1. **Claude Code 最新情報** — 公式アップデート、新機能、Breaking Changes
2. **はてブIT（日本市場）** — 注目トピック（★★★のみテーブル） + 全エントリー
3. **Hacker News（グローバル）** — 注目トピック + 全エントリー
4. **Reddit テック系（9サブレッド）** — 注目トピック + カテゴリ別エントリー
5. **パレオな男（フィットネス科学）** — 最新記事一覧
6. **PubMed メタ分析（運動・栄養・睡眠）** — カテゴリ別の最新論文
7. **Reddit フィットネス系（5サブレッド）** — 注目トピック + カテゴリ別エントリー

### 11. 履歴ファイルの更新

収集完了後、新規に取得した全記事のURLを `anote/03-input/information/collected-history.md` に追記する。

フォーマット:
```markdown
## YYYY-MM-DD
- https://example.com/article1
- https://example.com/article2
```

- 既存の履歴内容は保持し、新しい日付のセクションを**ファイル先頭（`# 収集済み記事履歴` の直後）**に追加
- Editツールを使用して追記

## 注意事項

- WebFetchツールを使用して情報を取得（Redditを除く）
- **すべての記事にURLリンクを必ず含める（リンクなしは不可）**
- **はてブは元記事のURLを必ず取得**（はてブページURLではなく）
- **Hacker NewsはHNコメントページURL（`item?id=`形式）を使用**（元記事URLではなく）
- **Hacker News・Redditのタイトルは日本語に翻訳**
- **RedditはRedditコメントページの完全URL（`https://www.reddit.com/r/subreddit/comments/...`形式）を使用**
- Reddit APIレート制限に注意（1分あたり60リクエスト程度）
- 重複排除を必ず実施し、既出記事は出力に含めない
- 出力ファイルのYYYYMMDDは実行日の日付を使用
- 可能な限り並列でデータ取得を行い、効率化する
