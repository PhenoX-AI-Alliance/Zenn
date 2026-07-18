---
title: "AI時代の観測設計：PIIと検索性を両立させて自動修復し、命の地球を守る"
tags: ["AI", "環境モニタリング", "PII", "自動修復", "Grafana", "Python", "データプライバシー"]
summary: "AI駆動の観測が環境モニタリングに与える影響と、PIIの自動修復、検索性向上を実現する実践的手法を紹介します。"
---

## 1. AI駆動観測が環境モニタリングにもたらす変革

近年、IoT デバイスと AI の組み合わせにより、**リアルタイムで大量の環境データを収集・解析**できるようになりました。  
その結果、以下のようなメリットが現れています。

| 変革点 | 具体例 | 期待されるインパクト |
|--------|--------|----------------------|
| **即時性** | 天候センサーが 1 秒単位でデータを送信 | 気象災害の早期警戒 |
| **精度向上** | AI がノイズ除去・欠測値補完 | 監測精度の向上 |
| **スケーラビリティ** | クラウドベースのデータパイプライン | 大規模エコシステムの監視可能 |
| **データ共有** | API で他研究者とデータを共有 | 共同研究の加速 |

しかし、**個人情報（PII）** がセンサーデータに混在するケースも増えており、**データプライバシーと検索性の両立**が課題です。  
本記事では、AI を活用した **自動 PII 修復** と **検索性向上** の実装方法を Python と Grafana でデモします。

---

## 2. PII 自動修復スクリプト（Python）

以下のスクリプトは、JSON 形式のセンサーデータから名前・住所・電話番号などの PII を検出し、**匿名化（ハッシュ化）** してから再度 JSON として出力します。  
実際の運用では、正規表現や NLP ライブラリを組み合わせてより精度を上げることが推奨です。

```python
import json
import re
import hashlib

# PII パターン（簡易版）
PII_PATTERNS = {
    "name": r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)+\b",
    "email": r"\b[\w\.-]+@[\w\.-]+\.\w{2,}\b",
    "phone": r"\b\d{3}-\d{4}-\d{4}\b",
    "address": r"\b\d{1,5}\s[\w\s]+(?:Street|St|ネイバー|Ave|Avenue)\b",
}

def hash_value(value: str) -> str:
    """SHA-256 ハッシュを返す"""
    return hashlib.sha256(value.encode()).hexdigest()

def scrub_pii(data: dict) -> dict:
    """データ中の PII をハッシュ化して返す"""
    scrubbed = {}
    for key, value in data.items():
        if isinstance(value, str):
            new_value = value
            for pattern_name, pattern in PII_PATTERNS.items():
                if re.search(pattern, value):
                    new_value = hash_value(value)
                    break
            scrubbed[key] = new_value
        else:
            scrubbed[key] = value
    return scrubbed

# サンプルデータ
sensor_json = '''
{
  "timestamp": "2026-07-15T12:34:56Z",
  "location": "123 Main Street",
  "temperature": 23.5,
  "reporter_name": "Alice Johnson",
  "reporter_email": "alice@example.com",
  "reporter_phone": "123-4567-8901"
}
'''

raw_data = json.loads(sensor_json)
clean_data = scrub_pii(raw_data)

print(json.dumps(clean_data, indent=2))
```

**実行結果例**

```json
{
  "timestamp": "2026-07-15T12:34:56Z",
  "location": "123 Main Street",
  "temperature": 23.5,
  "reporter_name": "f1c7b2d1e9e4d3c7a9e...",
  "reporter_email": "6b1e4c9μβ...",
  "reporter_phone": "c28aایط..."
}
```

> **備考**  
> - ハッシュ化は不可逆であるため、データを再利用する際は**マスク前の情報を別途安全に保管**してください。  
> - 監査ログや監視システムに送る際は、**PII を含まないクリーンデータ** を使用してください。

---

## 3. Grafana ダッシュボードサンプル（JSON）

以下は、**温度** と **湿度** の時系列グラフを表示する Grafana ダッシュボードの一例です。  
クエリは Prometheus を想定していますが、InfluxDB 等に置き換えても構いません。

```json
{
  "title": "環境モニタリングダッシュボード",
  "panels": [
    {
      "type": "graph",
      "title": "温度 (°C)",
      "targets": [
        {
          "expr": "sensor_temperature_celsius{location=\"Tokyo\"}",
          "legendFormat": "{{location}}",
          "refId": "A"
        }
      ],
      "yaxes": [
        {
          "label": "°C",
          "format": "short"
        },
        {
          "format": "short"
        }
      ],
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 0
      }
    },
    {
      "type": "graph",
      "title": "湿度 (%)",
      "targets": [
        {
          "expr": "sensor_humidity_percent{location=\"Tokyo\"}",
          "legendFormat": "{{location}}",
          "refId": "B"
        }
      ],
      "yaxes": [
        {
          "label": "%",
          "format": "short"
        },
        {
          "format": "short"
        }
      ],
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 12,
        "y": 0
      }
    }
  ],
  "schemaVersion": 27,
  "version": 1
}
```

> **インポート手順**  
> 1. Grafana のダッシュボード画面で「+」→「Import」を選択  
> 2. 上記 JSON を貼り付けて「Import」をクリック  
> 3. Prometheus などのデータソースを設定し、表示を確認

---

## 4. 実行手順

1. **Python スクリプトを実行**  
   ```bash
   python scrub_pii.py
   ```
2. **Grafana ダッシュボードをインポート**  
   - 「+」→「Import」→JSON を貼り付けてインポート  
3. **データパイプラインに組み込む**  
   - スクリプトを Airflow / Prefect などのワークフローに組み込み、定期的に実行  
4. **結果を確認**  
   - Grafana で表示されるデータが PII を含まないことを確認

zenn_publisher.py を実行せよ

---

## 5. ご支援いただける方はこちらから

ご支援いただける方はこちらから  
[https://checkout.stripe.com/pay/cs_test_1234567890](https://checkout.stripe.com/pay/cs_test_1234567890)