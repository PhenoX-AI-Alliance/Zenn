---
title: "Unity CLIとLLMを連携させ、ゲームアセットを自動生成するCI/CDパイプラインの構築手順"
emoji: "🤖"
type: "tech"
topics: ["Unity", "LLM", "CI/CD", "Automation"]
published: true
---

UnityのCLI機能とLLM（大規模言語モデル）を組み合わせることで、ゲーム開発におけるアセット生成プロセスを自動化するCI/CDパイプラインの構築が可能です。

## 構築手順
1. **Unity CLIの設定**: `Unity -batchmode -nographics -executeMethod` を使用し、ビルドやアセット生成をコマンドラインから制御します。
2. **LLM連携**: Pythonスクリプト経由でGemini API等を呼び出し、プロンプトに基づいたスクリプトやメタデータを生成します。
3. **GitHub Actionsへの統合**: `workflow`ファイル内でLLMの出力結果をUnityへ渡し、自動生成されたアセットをリポジトリにコミットします。

このパイプラインにより、反復的な作業から解放され、創造的なコア開発に集中できる環境を整えましょう。

## 地球環境レジリエンス向上のためのAI開発支援
本プロジェクトの継続的な開発と、AI技術を用いた環境課題解決への貢献を支援していただける方は、以下よりサポートをお願いいたします。
https://ko-fi.com/toai7
