# Claude CodeでOpenTelemetryを自動実装し、地球環境データの異常を検知する自律エージェントの作り方

近年、AIエージェントによる開発の効率化が急速に進んでいます。特にAnthropicが発表した**Claude Code**は、ターミナルから直接コードベースを操作-修正できる強力なツールです。

本記事では、Claude Codeを活用して、地球環境データ（センサー値）を監視し、異常を検知した際にOpenTelemetryでトレースを送信する自律エージェントを構築する方法を解説します。

---

## 1. Claude CodeとOpenTelemetryの統合

### Claude Codeとは
Claude Codeは、開発者がターミナルから自然言語で指示を出すことで、ファイルの作成、修正、テスト実行、依存関係の管理を自律的に行うCLIツールです。

### OpenTelemetryの役割
分散トレーシングの標準規格であるOpenTelemetry（OTel）を導入することで、センサーデータがどのプロセスで処理され、どこで異常値が検出されたかを可視化できます。Claude Codeに「OpenTelemetryの計装（Instrumentation）を追加して」と指示するだけで、ボイラープレートコードを自動生成させることが可能です。

---

## 2. Pythonによる環境データ監視ダッシュボード（デモ）

まずは、センサーデータの模倣と監視を行う基本的なPythonスクリプトを作成します。

```python
import time
import random
import psutil
from opentelemetry import trace

# トレーサーの設定
tracer = trace.get_tracer(__name__)

def get_environmental_data():
    """センサーデータのシミュレーション"""
    return {
        "temperature": random.uniform(20.0, 35.0),
        "co2_level": random.uniform(400, 1000),
        "cpu_usage": psutil.cpu_percent()
    }

def monitor_environment():
    while True:
        with tracer.start_as_current_span("sensor_read_loop"):
            data = get_environmental_data()
            print(f"Data: {data}")
            
            # 異常検知ロジック
            if data["temperature"] > 34.0:
                print("⚠️ 異常検知: 高温アラート!")
                # ここにOTelイベントやアラート処理を追加
        
        time.sleep(5)

if __name__ == "__main__":
    monitor_environment()
```

---

## 3. 実装ステップガイド

### ステップ1: 環境構築とClaude Codeの起動
プロジェクトディレクトリでClaude Codeを初期化します。

```bash
# Claude Codeの起動
claude
```

### ステップ2: 依存ライブラリの追加
Claude Codeのプロンプトで以下のように指示を出します。
> "OpenTelemetryのSDKとコンソールエクスポーターをインストールし、requirements.txtを更新して。"

### ステップ3: 自動計装の指示
コードベースを読み込ませた状態で、以下の指示を与えます。
> "現在のコードにOpenTelemetryのトレーサーを組み込んで。`get_environmental_data`関数とメインループをトレース対象にし、異常検知時にスパンに属性（attribute）として異常値を付与して。"

### ステップ4: 検証と実行
Claude Codeが生成したコードを確認し、以下のコマンドで実行します。
```bash
python monitor.py
```
コンソールにトレースログが出力され、異常値が含まれていることが確認できれば成功です。

---

## 結論：AIエージェントと観測可能性の未来

Claude Codeを使用することで、これまで手動で行っていた監視基盤の構築が数分で完了します。環境データの異常検知のようなクリティカルなシステムにおいて、OpenTelemetryによる可視化は不可欠です。

今後、このエージェントをさらに進化させ、異常検知時に自動的に修復コマンドを実行したり、外部APIへ通知を飛ばす機能を実装していく予定です。

### このプロジェクトの継続開発を支援する
地球環境の保護とAI技術の健全な発展のため、皆さんのサポートをお願いします。
[https://ko-fi.com/toai_resilience](https://ko-fi.com/toai_resilience)