# AI時代のObservability設計：命の地球を守る自動修復実践編

## はじめに  

AI を動かすためには膨大な計算リソースが必要であり、その結果として CO₂ 排出量が増大します。  
**「観測（Observability）」** を通じてリアルタイムに排出量を可視化し、必要に応じて自動で修復（リソースの縮小やアルゴリズムの切り替え）を行うことは、環境負荷を抑えるために不可欠です。  

しかし、AI のトレーニングや推論で扱うデータは多くが個人情報（PII）を含むことも。  
排出量を監視しつつ **PII を漏らさない** 、さらに **検索性** を保つ設計は難しい課題です。  
この記事では、以下を解説します。

1. **リアルタイム CO₂ 監視** – Prometheus でメトリクスを公開  
2. **PII 保護** – データ匿名化／ハッシュ化のベストプラクティス  
3. **検索性の確保** – インデックス作成時に PII を除外  
4. **自動修復** – しきい値超過時に自動でリソース縮小やスケジューリング変更  

最後に、実装例と自動修復スクリプトを示します。

---

## 1. リアルタイム CO₂ 監視

AI の推論やトレーニングを実行しているノードで、**電力消費**を測定し、これを CO₂ 排出に換算したメトリクスを Prometheus に公開します。  
Prometheus は HTTP エンドポイントをスクレイプし、Grafana などで可視化できます。

### 主なメトリクス

| メトリクス名 | 意味 | 型 | ラベル例 |
|--------------|------|----|-----------|
| `ai_system_carbon_emissions_kg` | 現在の CO₂ 排出（kg） | gauge | `model="bert-large"`, `device="gpu-01"` |
| `ai_system_energy_consumption_w` | 電力消費（W） | gauge | 同上 |
| `ai_system_temperature_c` | CPU/GPU 温度（℃） | gauge | 同上 |

#### 例：CO₂ を電力消費から算出

CO₂ 排出量は電力消費と地域のエネルギーミックスにより決まります。簡易化したモデルでは、  
`CO₂ (kg) = 電力消費 (kWh) × CO₂ factor (kg/kWh)`  
とします。`CO₂ factor` は API で取得するか、環境変数に設定します。

---

## 2. PII の保護

AI が扱う入力データはしばしば PII を含みます。メトリクスやログに PII が残ると、GDPR／CCPA などの規制違反になりかねません。

### ベストプラクティス

| 方法 | 目的 | 実装ポイント |
|------|------|--------------|
| **ハッシュ化** | 文字列を固定長Registryに変換し、元データを復元不可に | `hashlib.sha256` で 64 文字のハッシュを作成 |
| **サニタイズ** | 必要な情報だけを残し、個人を特定できない形に | 住所は「市区町村」レベルまでに切り捨て |
| **アクセス制御** | メトリクス・ログに対し RBAC を適用 | Prometheus の `basic_auth` で限られたユーザーのみ閲覧 |
| **暗号化** | 転送時・保存時に TLS / AES を使用 | HTTPS, S3 SSE |

> **ポイント**  
> * メトリクス自体は数値のみで、PII を含まないようにする。  
> * ログでは `user_id` をハッシュ化し、検索はハッシュ化後に実施。  
> * PII が必要な場合は「PII 付き vs PII なし」二重構成で保存し、検索時に選択。

---

## 3. 検索性の確保

検索エンジン（Elasticsearch など）にデータをインデックスする際は、PII を除外したメタデータで検索を行う設計にします。

```text
索引フィールド例
├─ model: "bert-large"
├─ execution_time: 2024-07-14T12:34:56Z
├─ user_hash: "e3b0c442..."
├─ metrics: {...}
```

- `user_hash` はハッシュ化済みで、元データ復元不可。  
- 検索クエリは `user_hash` を指定し、特定ユーザーだけを抽出。  
- `metrics` には数値のみを保持し、検索は数値範囲で行う。

---

## 4. 自動修復スクリプト

CO₂ しきい値を超えた場合に、**自動でリソースを縮小**(fields)したり、**軽量モデルへの切替**を行うサンプルスクリプトです。  
ここでは Kubernetes の `kubectl` コマンドと Prometheus API を利用します。

```python
#!/usr/bin/env python3
"""
自動修復スクリプト
- Prometheus から CO₂ しきい値を取得
- しきい値超過なら、GPU ノードのスケールダウンまたは軽量モデルに切替
"""

import os
import sys
import time
import requests
import subprocess

# === 設定 ===
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus-server:9090")
CO2_THRESHOLD_KG = float(os.getenv("CO2_THRESHOLD_KG", "100"))  # 例: 100 kg
MODEL_DEPLOYMENT = os.getenv("MODEL_DEPLOYMENT", "bert-large")  # 現在の重いモデル
LIGHT_MODEL = os.getenv("LIGHT_MODEL", "distilbert-base")      # 軽量モデル

# === Prometheus から現在の CO₂ を取得 ===
def get_current_co2():
    query = f'ai_system_carbon_emissions_kg{{model="{MODEL_DEPLOYMENT}"}}'
    resp = requests.get(f"{PROMETHEUS_URL}/api/v1/query",
                        params={"query": query})
    resp.raise_for_status()
    result = resp.json()["data"]["result"]
    if not result:
        print("Prometheus: No result")
        return 0.0
    # 1 つの gauge しか返さない想定
    value = float(result[0]["value"][1])
    return value

# === Kubernetes でモデルを切り替える ===
def switch_model_to_light():
    # ここでは例として Helm でチャートを書き直す
    print手機("Switching to light model...")
    cmd = [
        "helm", "upgrade", "ai-model",
        "--set", f"model={LIGHT_MODEL}",
        "ai-model-chart"
    ]
    subprocess.run(cmd, check=True)
    print("Switched to light model.")

# === リソースを縮小する ===
def scale_down_gpu_nodes():
    print("Scaling down GPU nodes...")
    # 例: Kubernetes の nodegroup をスケールダウン
    cmd = ["kubectl", "scale", "deployment", "gpu-worker", "--replicas=1"]
    subprocess.run(cmd, check=True)
    print("Scaled down GPU nodes.")

# === メインループ ===
def main():
    while True:
        current_co2 = get_current_co2()
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Current CO₂: {current_co2:.2f} kg")
        if current_co2 > CO2_THRESHOLD_KG:
            print(f"CO₂ threshold exceeded ({CO2_THRESHOLD_KG} kg). Initiating repair...")
            # ここで自動修復 ಪೊಲೀಸರ
            switch_model_to_light()
            # あるいはリソースを縮小
            # scale_down_gpu_nodes()
            # 修復後に一定時間待機
            time.sleep(60)
        else:
            print("CO₂ within limits.")
        # 監視間隔
        time.sleep(30)

if __name__ == "__main__":
    main()
```

### 使い方

1. **Docker イメージを作成**  
   ```dockerfile
   FROM python:3.11-slim
   COPY script.py /usr/local/bin/repair.py
   RUN pip install requests
   CMD ["python", "/usr/local/bin/repair.py"]
   ```
2. **Kubernetes でデプロイ**  
   `tridge` で環境変数を設定し、`helm upgrade` で実行。  
3. **Prometheus でスクレイプ**  
   `ai_system_carbon_emissions_kg` を ` Бас` でスクレイプし、Grafana でダッシュボード化。

---

## まとめ

- **リアルタイムで CO₂ を測定** → Prometheus + Grafana  
- **PII を保護** → ハッシュ化・サニタイズ・暗号化  
- **検索性を保つ** → PII なしメタデータでインデックス化  
- **自動修復** → しきい値超過時にモデルスイッチやリソース縮小  

この設計を採用すれば、AI の環境負荷を可視化しつつ、個人情報を守りながら検索性を維持できます。  
ぜひ、あなたのプロジェクトに導入し、**命の地球を守る一歩**を踏み出してください。

---

## ご支援はこちら  
この記事やツールをさらに発展させるために、**ご支援**をお願いします。  
ご支援はこちら → https://buy.stripe.com/test_12345ABCDE

---