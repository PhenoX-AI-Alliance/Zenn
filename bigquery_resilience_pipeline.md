# BigQueryによる地球環境レジリエンス指標（EERI）解析パイプラインの構築

気候変動や環境負荷の増大に伴い、地域ごとの環境レジリエンス（回復力）を定量化する「Earth Environmental Resilience Indexing (EERI)」の重要性が高まっています。本記事では、Google BigQueryを活用した大規模環境データ解析パイプラインの構築手法と、Claude Codeを活用した開発効率化のアプローチを解説します。

---

## 1. アーキテクチャ概要

EERIパイプラインは以下の3層構造で構成します。

1.  **Ingestion Layer**: Google Cloud Storage (GCS) を経由し、衛星データ（Sentinel/Landsat）や気象観測データをBigQueryへロード。
2.  **Processing Layer**: BigQuery SQLおよびDataformを用いたデータ変換（正規化-集計）。
3.  **Analytics Layer**: Looker StudioまたはVertex AIを用いたレジリエンス指標の可視化と予測。

---

## 2. Claude Codeによる開発効率化：Planモードとループエンジニアリング

複雑なデータパイプラインを構築する際、**Claude Code**の「Planモード」と「ループエンジニアリング」を活用することで、実装の精度を飛躍的に向上させることができます。

### Planモードの活用
まず、`claude`に対して「パイプラインのデータフロー図を作成し、必要なBigQueryのスキーマを定義せよ」と指示します。Planモードでは、コードを書く前に論理的整合性を確認できるため、手戻りを最小限に抑えられます。

### ループエンジニアリング
データ解析の試行錯誤（ループ）を自動化します。
*   **ステップ:** 
    1. クエリ実行結果の統計（平均値-外れ値）をClaudeにフィードバック。
    2. エラーログや性能ボトルネックを解析。
    3. Pythonスクリプトでクエリを動的生成し、最適化されたSQLを再デプロイ。

このサイクルを回すことで、人手では数時間かかるクエリチューニングを数分で完了させることが可能です。

---

## 3. 実装：BigQueryへのデータ統合

### Pythonによるデータロード（Google Cloud Client Library）
環境データをBigQueryへ投入する基本的なPythonコードです。

```python
from google.cloud import bigquery

def load_environmental_data(table_id, uri):
    client = bigquery.Client()
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
    )
    
    load_job = client.load_table_from_uri(uri, table_id, job_config=job_config)
    load_job.result()  # 完了待ち
    print(f"Loaded {load_job.output_rows} rows to {table_id}.")
```

### SQL：レジリエンス指標の計算
環境負荷データからレジリエンスを算出するクエリ例です。

```sql
-- EERI算出のための正規化ビュー
CREATE OR REPLACE VIEW `project.dataset.eeri_metrics` AS
SELECT
  region_id,
  timestamp,
  -- 植生指数と気温の相関によるレジリエンス係数
  SAFE_DIVIDE(ndvi_mean, temp_anomaly) AS resilience_score
FROM
  `project.dataset.raw_environmental_data`
WHERE
  timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 365 DAY)
GROUP BY 1, 2;
```

---

## 4. まとめ

BigQueryの強力なスケーラビリティとClaude Codeの推論能力を組み合わせることで、地球規模の膨大な環境データセットに対しても、迅速かつ正確なレジリエンス解析基盤を構築できます。この手法は、気候変動対策の意思決定を加速させるための強力な武器となるでしょう。

地球環境データ解析基盤の維持-改善を支援する
https://ko-fi.com/phenox_noc2