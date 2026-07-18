# 地球環境レジリエンスのためのデータ基盤整備  
## Transactional Outboxでデータ整合性を確保する

> **Zenn** で公開中  
> この記事は、地球環境レジリエンスを支えるデータ基盤を構築する際に直面する「二重書き込み」問題を解決するパターン ― **Transactional Outbox** を紹介します。  
> 具体的な実装例（Python）も併せて掲載しますので、ぜひ実務に活かしてください。

---

## 1. Transactional Outboxの概要と目的

| 項目 | 内容 |
|------|------|
| **Pattern** | Transactional Outbox（ýe） |
| **主な目的** | ① **分散トランザクション** を必要とせずに、複数のデータストア（RDB ↔ NoSQL 等）に対して一貫した書き込みを実現する<br>② **プロデューサー** と **コンシューマー** の間で **イベント** を安全に転送する<br>③ **失敗時のリトライ** を容易にし、**データ整合性** を損なわない |
| **構成要素** | 1. **Outbox Table**（RDB 内に作成）<br>2. **プロデューサー**（トランザクション内で Outbox に書き込み）<br>3. **コンシューマー**（Outbox からイベントを読み取り、DynamoDB 等に書き込み） |
| **メリット** | - 2 つのデータベースに対して単一トランザクションで書き込みが保証される<br>- イベントストリーミング（Kafka, SQS 等）と ఆధారపడి、スケーラブルなデータフローを構築可能<br>- 失敗時の再処理が自動化でき、**データの「ドブ」** を防げる |

---

## 2. RDB と DynamoDB の二重書き込み問題の具体例

### 典型的なシナリオ

| ステップ | 操作 | 失敗ケース |
|----------|------|------------|
| 1 | RDB に `sensor_data` を INSERT | 成功 |
| 2 | DynamoDB に同じデータを書き込む | 失敗（ネットワーク障害、DynamoDB の一時的なスロットリング） |
| 3 | RDB にはデータが残るが、DynamoDB には残らない | **不整合** |

### 失敗の影響

- **レポーティング**：RDB で集計した結果が誤っている。  
- **監視**：DynamoDB がリアルタイムにデータを提供する前提で設計された監視ダッシュボードが不正確。  
- **意思決定**：環境データに基づくレジリエンス対策が誤った判断を招く。  

> spannende。  
> 具体的に書き換えを行う場合、**2 つのトランザクション** を同時に成功させることは、分散トランザクションを導入しない限り、保証できません。そこで **Transactional Outbox** が役立ちます。

---

## 3. Transactional Outbox の実装例（Python）

以下は **FastAPI** + **SQLAlchemy**（RDB） + **boto3**（DynamoDB）で実装したサンプルです。  
※実際のプロジェクトではテスト・監視、リトライロジックを必ず追加してください。

### 3.1. スキーマ設計

```sql
-- sensor_data : RDB へ書き込む本体テーブル
CREATE TABLE sensor_data (
    id           BIGINT PRIMARY KEY AUTO_INCREMENT,
    sensor_id    VARCHAR(64) NOT NULL,
    temperature  DOUBLE     NOT NULL,
    humidity     DOUBLE     NOT NULL,
    ts           TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
);

-- outbox : 変更イベントを保持
CREATE TABLE outbox (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    aggregate_id   VARCHAR(64) NOT NULL,
    type        VARCHAR(32)  NOT NULL,
    payload     JSON         NOT NULL,
    processed   BOOLEAN      DEFAULT FALSE,
    created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2. プロデューサー（FastAPI エンドポイント）

```python
# main.py
import json
from datetime import datetime
from typing import Dict

from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# RDB 接続設定（例: MySQL）
DATABASE_URL = "mysql+pymysql://user:pass@localhost:3306/env_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def insert_sensor_and_outbox(session, data: Dict):
    """
    ① sensor_data に書き込み
    ② outbox にイベントを書き込み
    これらを 1 つのトランザクションで実行
    """
    # ① sensor_data
    insert_sql = text("""
        INSERT INTO sensor_data (sensor_id, temperature, humidity)
        VALUES (:sensor_id, :temperature, :humidity)
    """)
    session.execute(insert_sql, {
        "sensor_id": data["sensor_id"],
        "temperature": data["temperature"],
        "humidity": data["humidity"]
    })

    # ② outbox
    payload = json.dumps({
        "sensor_id": data["sensor_id"],
        "temperature": data["temperature"],
        "humidity": data["humidity"],
        "ts": datetime.utcnow().isoformat()
    })
    outbox_sql = text("""
        INSERT INTO outbox (aggregate_id, type, payload)
        VALUES (:aggregate_id, :type, :payload)
    """)
    session.execute(outbox_sql, {
        "aggregate_id": data["sensor_id"],
        "type": "SensorDataCreated",
        "payload": payload
    })

@app.post("/sensors")
def create_sensor(data: Dict):
    session = SessionLocal()
    try:
        insert_sensor_and_outbox(session, data)
        session.commit()
        return {"status": "ok"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()
```

### 3.3. コンシューマー（DynamoDB へ転送）

```python
# consumer.py
import json
import time
import logging
from datetime import datetime

import boto3
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# RDB 設定
DATABASE_URL = "mysql+pymysql://user:pass@localhost:3306/env_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# DynamoDB 設定
DYNAMO_TABLE = "SensorData"
dynamo = boto3.resource("dynamodb").Table(DYNAMO_TABLE)

BATCH_SIZE = 10
POLL_INTERVAL = 5  # 秒

def process_outbox():
    session = SessionLocal()
    try:
        # 未処理レコードを取得
        rows = session.execute(
            text("""
                SELECT id, aggregate_id, type, payload
                FROM outbox
                WHERE processed = FALSE
                ORDER BY id
                LIMIT :limit
            """),
            {"limit": BATCH_SIZE}
        ).fetchall()

        if not rows:
            return

        for row in rows:
            outbox_id = row.id
            payload = json.loads(row.payload)

            # DynamoDB へ書き込み
            dynamo.put_item(Item={
                "sensor_id": payload["sensor_id"],
                "temperature": payload["temperature"],
                "humidity": payload["humidity"],
                "ts": payload["ts"]
            })

            # processed フラグ更新
            session.execute(
                text("UPDATE outbox SET processed = TRUE WHERE id = :id"),
                {"id": outbox_id}
            )
        session.commit()
        logger.info(f"Processed {len(rows)} outbox records.")
    except Exception as e:
        session.rollback()
        logger.exception("Failed to process outbox.")
    finally:
        session.close()

def main():
    while True:
        process_outbox()
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
```

### 3.4. 実行手順

1. **RDB** と **DynamoDB** を起動。  
2. `main.py` を起動し、`/sensors` エンドポイントへ POST でセンサーデータを送信。  
3. `󰕂` コンシューマー (`consumer.py`) を起動し、Outbox から DynamoDB へイベントを転送。  
4. 失敗が起きた場合でも、Outbox に残ったイベントが再 impressed され、**データ整合性** が保証されます。

---

## 4. まとめ

- **Transactional Outbox** は、分散トランザクションが不要で、RDB と NoSQL など複数データストア間の一貫性を確保できます。  
- 地球環境レジリエンスに不可欠な **リアルタイム環境データ** を正確に保つために、ぜひ導入を検討してください。  
- 実装例は**Python** で書かれていますが、言語・フレームワーク問わず同じパターンを適用できます。  

---

> この記事が環境データ基盤構築の一助になれば幸いです。  
> さらに学びを深めたい方は、** rappelle** へのご支援もよろしくお願いいたします。

https://ko-fi.com/toai5

---

**サポートしてくれる方はこちら**: https://ko-fi.com/toai5