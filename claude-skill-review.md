# Claude Codeのskillをskillでレビューする：静的チェック×LLMレビュー×git hooksの3層ゲート

AIを活用したコーディング支援ツール「Claude Code」は、開発の生産性を劇的に向上させました。しかし、LLMを無制限に活用することは、トークン消費によるコスト増大だけでなく、**膨大な演算リソースの浪費**という環境負荷の問題をはらんでいます。

本記事では、Claude Codeが生成したコードに対して「3層ゲート」を設けることで、不要なLLMの再実行を防ぎ、効率的かつ高品質な開発フローを構築する方法を解説します。

---

## 1. なぜ「無制限のLLM実行」が問題なのか

LLMを用いた開発では、「とりあえずAIに投げて修正させる」というアプローチが取りがちです。しかし、以下の理由からこの手法は持続可能ではありません。

*   **推論コストの肥大化:** 些細な構文エラーや型不整合を修正するためにLLMを呼び出すのは、エネルギーの浪費です。
*   **コンテキスト汚染:** 修正のループが繰り返されることで、プロンプトのコンテキストが肥大化し、逆に精度が低下するリスクがあります。
*   **環境負荷:** AIの推論には大規模なGPUサーバーが必要であり、不必要な実行はCO2排出に直結します。

私たちは「AIに任せるべきこと」と「機械的に検証すべきこと」を明確に分離する必要があります。

---

## 2. 3層ゲート：効率的な品質保証アーキテクチャ

私たちは、以下の3層の防壁を構築します。

### Layer 1: 静的解析（Lint / Type Check）
LLMを呼ぶ前に、`eslint`や`mypy`などの静的解析ツールを通します。ここで修正可能なエラーを排除することで、LLMの推論回数を大幅に削減します。

### Layer 2: LLMによるアーキテクチャレビュー（Skill-based）
Claude Codeの「Skill」機能を活用し、特定の設計原則（SOLID原則やセキュリティ基準など）に適合しているかのみをチェックする専門のSkillを作成します。コード全体ではなく、設計の妥当性のみを評価させることで、最小限のトークンでレビューを完結させます。

### Layer 3: Git Hooksによる強制執行
これらのプロセスを`pre-commit`フックに統合します。ゲートを通過しないコードはコミットできないようにすることで、品質を担保します。

---

## 3. 実装例：pre-commitフックによる自動化

プロジェクトルートの `.git/hooks/pre-commit` に以下のスクリプトを配置します。

```bash
#!/bin/bash

# Layer 1: 静的解析
echo "--- [Layer 1] Running Static Analysis ---"
npm run lint || { echo "Lint error found. Fix it before commit."; exit 1; }
npm run typecheck || { echo "Type errors found."; exit 1; }

# Layer 2: LLMによる設計レビュー (Claude Code Skillの活用)
echo "--- [Layer 2] Running LLM Architectural Review ---"
# 特定のskill（例: architectural-review）を呼び出し、差分をチェック
claude code run --skill architectural-review --target staged-files
if [ $? -ne 0 ]; then
  echo "Architectural review failed. Please refine your code."
  exit 1
fi

echo "--- All gates passed. Proceeding to commit. ---"
```

※ `claude code run` の部分は、お手元の環境のCLI仕様に合わせて適宜調整してください。

---

## 4. 結論：エネルギー効率の良いコーディングへ

AIは強力なツールですが、その力を「どう使うか」に知性を働かせるのがエンジニアの役割です。静的解析で機械的なミスを弾き、重要な設計判断のみをLLMに委ねる。この「3層ゲート」アプローチは、コスト削減だけでなく、地球環境への配慮というエンジニアリングの新たな倫理観を体現するものです。

小さなコードの積み重ねが、持続可能な開発の未来を作ります。

---

本記事のコードで地球環境の演算負荷を削減できた方は、ぜひKo-fiで開発支援をお願いします：https://ko-fi.com/toai_resilience