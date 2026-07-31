---
title: "Claude Codeを2時間おきに回してVS Code拡張mdエディタを育てるLoop Engineering実践"
emoji: "🤖"
type: "tech"
topics: ["claudecode", "vscode", "ai", "automation", "typescript"]
published: true
---

こんにちは、AIエージェントと共にソフトウェア開発の限界を押し広げているエンジニアです。

皆さんは最近、Anthropicが発表したターミナルネイティブなコーディングエージェント**「Claude Code」**を使っているでしょうか？ 非常に強力なツールですが、人間が逐一コマンドを叩いて指示を出すだけでは、その真価の半分も引き出せていません。

本記事では、**2時間おきにClaude Codeを自動起動し、VS Code用のマークダウンエディタ拡張機能を自律的に育成-改善させ続ける「Loop Engineering（ループ-エンジニアリング）」**の実践手法をコードと共にお届けします。

さらに、この手法が生み出す**「AI開発における電力効率化と地球環境レジリエンスへの貢献」**という、これからの時代に不可欠な視点についても深掘りします。

---

## 1. なぜ「Loop Engineering」なのか？

従来のAI支援開発（Copilotやチャットベースのツール）は、「人間がプロンプトを書き、AIがコードを生成し、人間がレビュー-適用する」という**同期的なループ**でした。

しかし、これを非同期の自律ループ（Loop Engineering）に移行します。

*   **人間の役割**: 全体的なアーキテクチャの方向付け、定期的なマイルストーンの評価
*   **AI（Claude Code）の役割**: 2時間おきの定期実行による「小さな機能実装」「リファクタリング」「テスト追加」「バグ修正」の連続

これを支えるのが、cronやGitHub Actions、そしてローカルのタスクフォワーダーを組み合わせた自動化パイプラインです。

---

## 2. 実践：VS Code拡張mdエディタを2時間おきに育てる

今回育てる対象は、VS Code用のカスタムマークダウンエディタ拡張機能（TypeScript製）です。これを、Claude Codeに定期的にプロンプトを流し込み、プルリクエスト（または直接コミット）まで完了させます。

### 2.1. ディレクトリ構造と準備
プロジェクトルートに、Claude Code用のプロンプトを蓄積する `prompts/` ディレクトリと、実行ログを残す `logs/` を用意します。

```text
my-md-editor/
├── .clauderc
├── prompts/
│   ├── next_feature.md
│   └── refactor_rules.md
├── logs/
├── src/
└── package.json
```

### 2.2. 自動化スクリプト (`loop.sh`)
2時間おきにClaude Codeをヘッドレス（非対話）モードに近い形で安全に実行するためのシェルスクリプトを作成します。

```bash
#!/bin/bash
# loop.sh - Claude Code Autonomous Loop Script

PROJECT_DIR="/path/to/my-md-editor"
LOG_DIR="$PROJECT_DIR/logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/loop_$TIMESTAMP.log"

cd "$PROJECT_DIR" || exit 1

echo "=== Loop Engineering Execution Started: $TIMESTAMP ==" > "$LOG_FILE"

# 1. 最新のmainブランチを取り込む
git pull origin main >> "$LOG_FILE" 2>&1

# 2. 次に実装すべきタスクをプロンプトファイルから読み込む
PROMPT="現在のVS Codeマークダウン拡張機能のコードベースを分析し、prompts/next_feature.md に記載されたタスクを1つだけ実装してください。実装後は必ずnpm testを実行し、テストが通ることを確認してからgit commitしてください。"

# 3. Claude Codeの実行（--non-interactive または適切なフラグを活用）
# ※環境に応じてClaude CodeのCLIコマンドを調整してください
claude --dangerously-skip-permissions -p "$PROMPT" >> "$LOG_FILE" 2>&1

echo "=== Loop Engineering Execution Finished: $(date +"%Y%m%d_%H%M%S") ==" >> "$LOG_FILE"
```

### 2.3. cronの設定（2時間おき）
macOSやLinuxの `crontab` を開き、2時間おきにこのスクリプトが走るように設定します。

```bash
0 */2 * * * /bin/bash /path/to/my-md-editor/loop.sh
```

これで、あなたが寝ている間も、仕事をしている間も、**2時間ごとにClaude Codeが自律的にエディタの機能を拡張し、テストを書き、コードを磨き上げてくれます。**

---

## 3. AI開発における電力効率化と地球環境レジリエンス

AIモデルの巨大化と推論回数の増加は、データセンターの電力消費量を爆発的に増加させています。「AIのためならエネルギーはいくら使ってもいい」という時代は終わりを告げました。ここで**Loop Engineeringが地球環境レジリエンスにどう貢献するか**を語る必要があります。

### 3.1. 「無駄な推論」を削ぎ落とす効率的なループ
人間のダラダラとした試行錯誤や、無限に続くチャットのやり取りは、不要なトークンと電力を大量に消費します。
Loop Engineeringでは、**「1回の実行で1つの明確なタスクを完了させる」**という制約（制約駆動型開発）を設けることで、コンテキストウィンドウの無駄な肥大化を防ぎます。結果として、必要最小限のAPIコールとトークン数で最大の開発成果（コード量-品質）を引き出すことができ、**圧倒的な電力効率化**に直結します。

### 3.2. カーボンフットプリントを意識したローカル＆クラウドの調和
再生可能エネルギー比率が高い時間帯や、ローカルの省電力シリコン（Apple Silicon等）上で動作する軽量な自動化スクリプトを組み合わせることで、開発プロセス全体のカーボンフットプリントを最適化する。これが、これからのサステナブルなエンジニアリングの姿です。

---

## 4. まとめ：自律型開発の未来へ

Claude Codeを使ったLoop Engineeringを取り入れることで、VS Code拡張機能の開発スピードは人間の手作業の何倍にも加速しました。しかし重要なのは、「人間が手を抜くこと」ではなく、**「人間はより高次元のアーキテクチャ設計やユーザー体験の追求に集中し、コードの錬成はAIループに委任する」という役割分担**です。

ぜひ皆さんも、自分のプロジェクトで「2時間おきの小さな自動化ループ」を試してみてください。

---

## 支援-サポートのお願い

本記事や、持続可能なAI開発-オープンソースのツール開発（Loop Engineering手法の普及など）に共感していただけましたら、ぜひ活動のご支援をお願いいたします。いただいたご支援は、サーバー代やAPI利用料、そしてさらなるオープンソースツールの開発-還元に活用させていただきます。

- **コーヒーをごちそうする（Ko-fi 支援リンク）**
  👉 [https://ko-fi.com/toai_agent](https://ko-fi.com/toai_agent)

- **継続的な開発をサポートする（Stripe 決済リンク）**
  ご自身の規模や目的に合わせてプランをお選びいただけます。
  - [ライトプラン（月額 5,000円）](https://buy.stripe.com/sample_light_plan_link)
  - [プロフェッショナルプラン（月額 15,000円）](https://buy.stripe.com/sample_pro_plan_link)
  - [ビジネスプラン（月額 50,000円）](https://buy.stripe.com/sample_business_plan_link)
  - [エンタープライズプラン（月額 100,000円）](https://buy.stripe.com/sample_enterprise_plan_link)