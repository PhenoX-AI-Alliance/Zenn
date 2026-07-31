# Claude Codeで開発する地球環境データ収集エージェントとOpenTelemetryによる監視基盤

現代の開発現場において、AIエージェントは単なるコード生成ツールを超え、システム運用の自律化を加速させています。本記事では、Anthropicが提供するCLIツール「**Claude Code**」を活用して、環境データを収集するエージェントを構築し、さらに**OpenTelemetry**を用いてそのデータを可視化-監視する基盤の作り方を解説します。

---

## 1. Claude Codeによるエージェント開発の導入

Claude Codeは、ターミナル上で直接動作し、コードベース全体を理解した上で設計-実装-テストを支援するAIエージェントです。

従来の手動コーディングと比較し、以下のような利点があります。
*   **コンテキストの自動把握**: プロジェクトのディレクトリ構成を読み取り、適切な依存関係を推論します。
*   **自律的なイテレーション**: テストの失敗を検知し、修正コードを提案-適用するサイクルを高速化します。

今回は、このClaude Codeを使用して「地球環境データを模したシステムメトリクス収集エージェント」を実装します。

---

## 2. 環境データ収集エージェントの実装 (Python)

ここでは、CPU温度やシステム負荷を「環境負荷のプロキシ（代理指標）」と見立て、データを収集するPythonスクリプトを作成します。

```python
import time
import psutil
from opentelemetry import metrics

# メーターの初期化
meter = metrics.get_meter("env-sensor-collector")
cpu_temp_gauge = meter.create_observable_gauge(
    "system.cpu_temp", description="CPU温度（環境負荷の指標）"
)

def get_cpu_temp():
    # 簡易的な温度取得（環境依存）
    temps = psutil.sensors_temperatures()
    return temps['coretemp'][0].current if 'coretemp' in temps else 45.0

# メトリクス収集の定義
def cpu_temp_callback(options):
    yield metrics.Observation(get_cpu_temp())

meter.create_observable_gauge("system.cpu_temp", callbacks=[cpu_temp_callback])

if __name__ == "__main__":
    print("データ収集エージェントを起動しました...")
    while True:
        time.sleep(5)
```

---

## 3. OpenTelemetryによる監視基盤の統合

収集したデータを可視化するためには、OpenTelemetryのSDKを使用してバックエンド（PrometheusやHoneycombなど）へエクスポートします。

### ステップ1: 依存関係のインストール
```bash
pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp
```

### ステップ2: エクスポーターの設定
コード内で`OTLPSpanExporter`や`OTLPMetricExporter`を初期化し、収集したデータを外部の監視ダッシュボード（Grafana等）へ送信します。

*   **ポイント**: Claude Codeに対して「OpenTelemetryのセットアップを自動で行って」と指示するだけで、適切な`Resource`や`MeterProvider`の初期化コードを生成させることが可能です。

これにより、環境データの推移をダッシュボード上でリアルタイムに監視できる基盤が整います。

---

## 4. 地球環境レジリエンス維持のための開発支援

私たちの生活基盤である地球環境を維持するためには、データを計測し、可視化し、異常を早期に検知する「レジリエンス（回復力）」が必要です。このエージェント開発プロジェクトは、オープンソースとして環境負荷の可視化を民主化することを目指しています。

この活動を継続し、より高度な環境計測アルゴリズムを開発するために、皆様のご支援をお願いいたします。いただいた資金は、開発環境の維持および環境データ解析のためのサーバー費用として大切に使わせていただきます。

**[開発支援はこちらから（Stripe）](https://buy.stripe.com/test_dummy_link_5000jpy)**

---
*本記事はClaude CodeによるプロンプトエンジニアリングとOpenTelemetryの標準仕様に基づいています。*