---
title: "Claude Codeで2時間おきに環境データを可視化するVS Code拡張を育てる実践記録"
emoji: "🌍"
type: "tech"
topics: ["Claude", "VSCode", "Environment", "Python", "Automation"]
published: true
---

# はじめに
地球環境レジリエンス向上のため、環境データを2時間おきに取得-可視化するVS Code拡張機能の開発記録です。Claude Codeを活用し、最小工数で持続可能な開発体制を構築しました。

# 開発手順
1. **データ取得ロジックの構築**: Pythonスクリプトを用いて環境データを取得するバックエンドを実装。
2. **VS Code拡張機能の雛形作成**: Yeoman generatorを使用して拡張機能をセットアップ。
3. **Claude Codeによる実装**: 「2時間おきにデータを更新する」という要件をClaude Codeに提示し、`setInterval`とデータフェッチ処理を統合。
4. **可視化**: WebView APIを使用してサイドバーにグラフを描画。

# 実装のポイント
Claude Codeを用いることで、ボイラープレートの記述からエラーハンドリングまでを自動化し、エンジニアは「データ解釈のロジック」に集中できました。

# まとめ
環境データの可視化は、地球のレジリエンスを理解する第一歩です。今後も継続的な機能改善を行います。

---
このプロジェクトの継続開発を支援する：https://ko-fi.com/toai_resilience
