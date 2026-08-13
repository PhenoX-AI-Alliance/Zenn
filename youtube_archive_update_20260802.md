```markdown
---
title: "AIとGitHub Actionsで実現する！YouTubeライブ配信の自動アーカイブ化システム"
emoji: "🎥"
type: "tech"
topics: ["GitHubActions", "Python", "YouTube", "Automation", "インフラ運用"]
published: false
---

こんにちは！PhenoXです。

今回は、私たちが開発・運用している「TOAIシステム」において、YouTubeのライブ配信アーカイブを完全に自動で検知・更新する仕組みを構築したので、その背景と技術的なアプローチについてご紹介します。

実際のコミット：`bc2bb2: 🎥 YouTube自動更新: アーカイブ追加 (2026-08-01)`

---

## 1. 背景：なぜYouTubeアーカイブの自動化が必要なのか？

TOAIシステムでは、定期的なライブ配信やウェビナーを行っています。配信終了後、視聴者がいつでも過去のアーカイブにアクセスできるようにするため、ウェブサイト（`youtube_archive.html`）を随時更新する必要がありました。

しかし、これを手動で行うのは以下の課題がありました：
- **手動更新の手間とヒューマンエラー**: 配信のたびにリンクを貼り付け、HTMLを書き換えるのは地味に時間がかかる。
- **情報の鮮度低下**: 更新を忘れると、ユーザーが最新のアーカイブを見逃してしまう。
- **継続的なインフラ運用のコスト**: 24時間365日動くような大がかりなサーバーを立てるほどでもない。

そこで、「GitHub ActionsとAPIを組み合わせ、完全にサーバーレスで自動化するパイプライン」を構築することにしました。

---

## 2. システムアーキテクチャの概要

今回構築した自動化パイプラインの構成は非常にシンプルです。

1. **トリガー**: GitHub Actionsの `cron` スケジュール（またはイベント駆動）
2. **データ取得**: YouTube Data APIを用いて、指定チャンネルの最新動画・ライブ配信情報を取得
3. **差分検知 & 処理**: 前回記録したアーカイブリストと比較し、新しい配信があればデータを整形
4. **HTML自動生成**: `youtube_archive.html` をプログラム側で書き換え
5. **自動コミット**: Gitコマンドを使って、自動でリポジトリに変更をプッシュ

これらをすべてGitHub上の仮想環境（GitHub Actions）で完結させることで、**追加のサーバー費用を一切かけずに運用**しています。

---

## 3. 実装のポイント

### ① 定期実行による自動化（GitHub Actions）
夜間や配信終了後に自動でスクリプトが走るよう、GitHub Actionsのワークフローを設定しています。

```yaml
name: Auto Update YouTube Archive

on:
  schedule:
    - cron: '0 18 * * *' # 毎日JST深夜などに実行
  workflow_dispatch:

jobs:
  update-archive:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install requests beautifulsoup4

      - name: Run update script
        env:
          YOUTUBE_API_KEY: ${{ secrets.YOUTUBE_API_KEY }}
        run: python scripts/update_youtube_archive.py

      - name: Commit and push changes
        uses: stefanzwei/git-auto-commit-action@v4
        with:
          commit_message: "🎥 YouTube自動更新: アーカイブ追加"
          file_pattern: "youtube_archive.html"
```

### ② AIを活用した自動化パイプラインの思想
単にスクリプトを回すだけでなく、TOAIシステムでは「AIを活用した自律的なインフラ運用」を目指しています。将来的には、配信のタイトルや概要欄からAIが自動でタグ付けを行ったり、重要なハイライトを抽出し、アーカイブページにリッチな情報を付与する拡張も視野に入れています。

---

## 4. 継続的なインフラ運用の重要性

個人開発や小規模チームにおいて、アプリケーションのコードを書くこと以上に大変なのが**「インフラや周辺ツールの継続的な運用（メンテナンス）」**です。

今回のような「日々の細かな更新作業」を自動化しておくことで、開発リソースをコア機能の開発やコンテンツの質向上に集中させることができます。「面倒なことはすべてコードとAIに任せる」という思想は、持続可能な開発において非常に重要だと実感しています。

---

## まとめ

今回は、GitHub ActionsとYouTube APIを活用したアーカイブ自動更新システムの仕組みについて解説しました。

「手作業を減らしたい」「インフラ運用を自動化して楽をしたい」と考えている方の参考になれば幸いです。

今後もTOAIシステムの開発状況や、AIを活用した自動化の知見をシェアしていきますので、よろしければZennのフォローやGitHubのスターをお願いします！

---

### ☕ 応援・サポートのお願い
PhenoXの活動やオープンソース開発（TOAIシステムなど）を応援していただける方は、以下のリンクからサポートをいただけると大変励みになります！

- **Ko-fi (サポート):** https://ko-fi.com/phenox
- **GitHub Repository:** [PhenoX-AI-Alliance/TOAI_System](https://github.com/PhenoX-AI-Alliance/TOAI_System)

ご購読ありがとうございました！
```