# トランザクショナル・アウトボックス・パターンで実現するデータ整合性  
**〜地球環境レジリエンスのためのデータ基盤〜**  

---  

## 1. はじめに  

地球環境モニタリングや気候変動シミュレーションなど、持続可能な社会を支えるシステムでは、**膨大な観測データ** と **高頻度なトランザクション** が同時に扱われます。  
こうしたシステムでは、リレーショナルデータベース（RDB）で **ACID トランザクション** を守りつつ、NoSQL（例：Amazon DynamoDB）で **スケーラブルな読み取り／書き込み** を実現する「ハイブリッド永続化」が一般的です。  

しかし、RDB と DynamoDB の **二重書き込み（Dual‑write）** を素朴に実装すると、データ不整合やデータ損失のリスクが生じます。本記事では、**トランザクショナル・アウトボックス・パターン** を用いてこの問題を解決し、地球環境レジリエンスを支える堅牢なデータ基盤を構築する具体的な実装例を示します。  

---  

## 2. デュアルライト問題とは  

| 項目 | RDB (例: PostgreSQL) | DynamoDB |
|------|----------------------|----------|
| **トランザクション** | ACID 準拠、複数テーブルの原子的更新 | 単一アイテムの条件付き書き込みのみ原子的 |
| **スキーマ** | 正規化されたリレーショナル | キー・バリュー / ドキュメント |
| **スケーラビリティ** | 垂直スケール中心 | 水平スケール自動 |

### 2.1 典型的な失敗シナリオ  

```text
1. アプリケーションが RDB で観測レコードを INSERT するトランザクションを開始
2. 同一トランザクション内で DynamoDB にも同一データを PutItem する
3. RDB のコミット直前にネットワーク障害発生 → RDB ロールバック
4. DynamoDB への PutItem はすでに成功済み → データが DynamoDB のみに残る
```

結果として **「RDB にないデータが DynamoDB に存在する」** 状態になり、後続の集計・分析ジョブが誤った結果を出力します。  

---  

## 3. トランザクショナル・アウトボックス・パターンの概要  

| 要素 | 役割 |
|------|------|
| **Outbox テーブル (RDB)** | トランザクション内で「本体データ」と「イベントレコード」を原子的に書き込む |
| **Relay / Poller** | Outbox テーブルをポーリングし、未送信イベントを DynamoDB へ書き込む |
| **冪等性キー** | DynamoDB の `ConditionExpression` で重複書き込みを防止 |
| **トランザクション境界** | RDB のコミット = イベントの永続化保証 |

**メリット**  

- RDB の ACID を犠牲にせず、DynamoDB への書き込みを **確実に・順序通り** 実行可能  
- リトライ・再処理が容易（Outbox レコードの `status` で管理）  
- データ基盤の **監査ログ** としても機能  

---  

## 4. 実装例：観測データの永続化フロー  

### 4.1 アーキテクチャ図（テキスト表現）  

```mermaid
flowchart LR
    App[アプリケーション] -->|1. トランザクション開始| DB[(PostgreSQL)]
    DB -->|2. 本体 + Outbox INSERT| DB
    DB -->|3. コミット| DB
    Poller[Outbox Poller (Spring Batch / Lambda)] -->|4. 未送信イベント取得| DB
    Poller -->|5. DynamoDB PutItem (冪等)| DDB[(DynamoDB)]
    DDB -->|6. 成功時 Outbox 更新| DB
```

### 4.2 データモデル  

#### 4.2.1 本体テーブル `observations`  

```sql
CREATE TABLE observations (
    obs_id          UUID PRIMARY KEY,
    station_id      VARCHAR(20) NOT NULL,
    observed_at     TIMESTAMPTZ NOT NULL,
    temperature_c   NUMERIC(5,2),
    humidity_pct    NUMERIC(5,2),
    co2_ppm         INTEGER,
    payload_json    JSONB        -- 拡張用
);
```

#### 4.2.2 アウトボックステーブル `outbox_events`  

```sql
CREATE TABLE outbox_events (
    event_id        UUID PRIMARY KEY,
    aggregate_id    UUID NOT NULL,          -- observations.obs_id
    event_type      VARCHAR(50) NOT NULL,   -- 'ObservationCreated'
    payload         JSONB NOT NULL,         -- DynamoDB に書き込むアイテム全文
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    status          VARCHAR(20) NOT NULL DEFAULT 'PENDING', -- PENDING / SENT / FAILED
    retry_count     INT NOT NULL DEFAULT 0,
    last_error      TEXT
);
CREATE INDEX idx_outbox_pending ON outbox_events (status, created_at) WHERE status = 'PENDING';
```

### 4.3 アプリケーション側のトランザクション (Spring Boot + JPA)  

```java
@Service
@RequiredArgsConstructor
public class ObservationService {

    private final ObservationRepository obsRepo;          // JPA
    private final OutboxEventRepository outboxRepo;       // JPA
    private final ObjectMapper mapper = new ObjectMapper();

    @Transactional
    public Observation create(ObservationRequest req) {
        // 1️⃣ 本体レコード作成
        Observation obs = Observation.builder()
                .obsId(UUID.randomUUID())
                .stationId(req.getStationId())
                .observedAt(req.getObservedAt())
                .temperatureC(req.getTemperatureC())
                .humidityPct(req.getHumidityPct())
                .co2Ppm(req.getCo2Ppm())
                .payloadJson(mapper.valueToTree(req.getExtra()))
                .build();
        obsRepo.save(obs);

        // 2️⃣ Outbox イベント作成（同一トランザクション内）
        Map<String, Object> ddbItem = Map.of(
                "pk", "OBS#" + obs.getStationId(),
                "sk", "TS#" + obs.getObservedAt().toInstant().toEpochMilli(),
                "obsId", obs.getObsId().toString(),
                "temperatureC", obs.getTemperatureC(),
                "humidityPct", obs.getHumidityPct(),
                "co2Ppm", obs.getCo2Ppm(),
                "extra", obs.getPayloadJson()
        );

        OutboxEvent event = OutboxEvent.builder()
                .eventId(UUID.randomUUID())
                .aggregateId(obs.getObsId())
                .eventType("ObservationCreated")
                .payload(mapper.valueToTree(ddbItem))
                .build();
        outboxRepo.save(event);

        return obs;
    }
}
```

> **ポイント**: `@Transactional` により、`observations` と `outbox_events` の INSERT が **同一 ACID トランザクション** でコミットされます。  

### 4.4 Outbox Poller (AWS Lambda + Java)  

```java
public class OutboxPollerHandler implements RequestHandler<ScheduledEvent, Void> {

    private final DataSource dataSource = DataSourceBuilder.create().build();
    private final DynamoDbClient ddb = DynamoDbClient.builder()
            .region(Region.AP_NORTHEAST_1)
            .build();
    private final ObjectMapper mapper = new ObjectMapper();

    @Override
    public Void handleRequest(ScheduledEvent event, Context context) {
        final int BATCH_SIZE = 100;
        try (Connection conn = dataSource.getConnection()) {
            conn.setAutoCommit(false);

            // 1️⃣ PENDING イベントを SELECT FOR UPDATE SKIP LOCKED で取得
            String sql = """
                SELECT event_id, aggregate_id, event_type, payload
                FROM outbox_events
                WHERE status = 'PENDING'
                ORDER BY created_at
                LIMIT ?
                FOR UPDATE SKIP LOCKED
                """;
            try (PreparedStatement ps = conn.prepareStatement(sql)) {
                ps.setInt(1, BATCH_SIZE);
                ResultSet rs = ps.executeQuery();

                while (rs.next()) {
                    UUID eventId = UUID.fromString(rs.getString("event_id"));
                    JsonNode payload = mapper.readTree(rs.getString("payload"));

                    // 2️⃣ DynamoDB へ冪等書き込み
                    PutItemRequest putReq = PutItemRequest.builder()
                            .tableName("ObservationsDDB")
                            .item(payload.traverse(mapper::convertValue).readValueAs(Map.class))
                            .conditionExpression("attribute_not_exists(pk) AND attribute_not_exists(sk)")
                            .build();

                    try {
                        ddb.putItem(putReq);
                        markSent(conn, eventId);
                    } catch (ConditionalCheckFailedException e) {
                        // 既に存在 → 成功とみなしステータス更新
                        markSent(conn, eventId);
                    } catch (Exception e) {
                        markFailed(conn, eventId, e.getMessage());
                    }
                }
            }
            conn.commit();
        } catch (Exception e) {
            context.getLogger().log("Poller fatal: " + e.getMessage());
        }
        return null;
    }

    private void markSent(Connection conn, UUID eventId) throws SQLException {
        try (PreparedStatement ps = conn.prepareStatement(
                "UPDATE outbox_events SET status='SENT', retry_count=0 WHERE event_id=?")) {
            ps.setObject(1, eventId);
            ps.executeUpdate();
        }
    }

    private void markFailed(Connection conn, UUID eventId, String err) throws SQLException {
        try (PreparedStatement ps = conn.prepareStatement(
                "UPDATE outbox_events SET status='FAILED', retry_count=retry_count+1, last_error=? WHERE event_id=?")) {
            ps.setString(1, err);
            ps.setObject(2, eventId);
            ps.executeUpdate();
        }
    }
}
```

**キーポイント**  

- `SELECT … FOR UPDATE SKIP LOCKED` で **並行ポーラー間の競合を回避**  
- DynamoDB の `ConditionExpression` で **冪等性** を保証（同一 PK/SK が存在すれば書き込みスキップ）  
- 失敗時は `retry_count` をインクリメントし、指数バックオフで再試行可能  

### 4.5 インフラ構成 (IaC 例: AWS CDK TypeScript)  

```typescript
import * as cdk from 'aws-cdk-lib';
import * as rds from 'aws-cdk-lib/aws-rds';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';

export class EarthResilienceStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // 1️⃣ Aurora PostgreSQL (Serverless v2)
    const db = new rds.DatabaseCluster(this, 'ObsDB', {
      engine: rds.DatabaseClusterEngine.auroraPostgres({ version: rds.AuroraPostgresEngineVersion.VER_15_4 }),
      serverlessV2MinCapacity: 0.5,
      serverlessV2MaxCapacity: 4,
      defaultDatabaseName: 'earth',
      credentials: rds.Credentials.fromGeneratedSecret('admin'),
      vpc: new ec2.Vpc(this, 'Vpc', { maxAzs: 2 }),
    });

    // 2️⃣ DynamoDB テーブル
    const ddb = new dynamodb.Table(this, 'ObservationsDDB', {
      partitionKey: { name: 'pk', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'sk', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      pointInTimeRecovery: true,
    });

    // 3️⃣ Outbox Poller Lambda (Java 21)
    const poller = new lambda.Function(this, 'OutboxPoller', {
      runtime: lambda.Runtime.JAVA_21,
      handler: 'com.example.OutboxPollerHandler',
      code: lambda.Code.fromAsset('../outbox-poller/target/outbox-poller-1.0.jar'),
      timeout: cdk.Duration.minutes(5),
      environment: {
        JDBC_URL: `jdbc:postgresql://${db.clusterEndpoint.hostname}:5432/earth`,
        DB_SECRET_ARN: db.secret?.secretArn ?? '',
        DDB_TABLE: ddb.tableName,
      },
      vpc: db.vpc,
      vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
    });

    db.secret?.grantRead(poller);
    ddb.grantWriteData(poller);

    // 4️⃣ EventBridge スケジュール (1分ごと)
    new events.Rule(this, 'PollerSchedule', {
      schedule: events.Schedule.rate(cdk.Duration.minutes(1)),
      targets: [new targets.LambdaFunction(poller)],
    });
  }
}
```

---  

## 5. 運用上の考慮点  

| 項目 | 対策 |
|------|------|
| **Outbox 膨張** | 定期的な `DELETE FROM outbox_events WHERE status='SENT' AND created_at < now() - interval '7 days'` を実行 |
| **遅延監視** | CloudWatch Metrics で `OutboxPendingCount` を可視化し、閾値超過でアラート |
| **冪等性キー設計** | `pk = "OBS#<station_id>"`, `sk = "TS<epoch_millis>"` で一意性を担保 |
| **スキーマ進化** | `payload_json` にバージョンフィールド (`schema_version`) を含め、コンシューマー側で互換処理 |
| **災害復旧** | Aurora Global Database + DynamoDB Global Tables でマルチリージョン冗長化 |

---  

## 6. まとめ  

- **デュアルライト問題** は、RDB と DynamoDB のトランザクション境界が異なるために発生する。  
- **トランザクショナル・アウトボックス・パターン** を導入すると、RDB の ACID トランザクション内で「本体データ」と「イベント」を原子的に永続化でき、後続の非同期リレーで DynamoDB へ確実に反映できる。  
- 実装例では、Spring Boot の `@Transactional` で Outbox 書き込みを行い、AWS Lambda (EventBridge 定期実行) が `SELECT … FOR UPDATE SKIP LOCKED` で未送信イベントを取得、DynamoDB の `ConditionExpression` で冪等 PutItem を実現している。  
- このアーキテクチャは、**地球環境モニタリング** のような高信頼・高スループットが求められるワークロードでも、データ整合性を保ちながらスケールアウト可能。  

---  

## 7. 参考資料  

- *Transactional Outbox Pattern* – Martin Fowler, 2020  
- AWS Documentation: **DynamoDB Conditional Writes**  
- PostgreSQL `SELECT … FOR UPDATE SKIP LOCKED`  
- Spring Boot `@Transactional` Best Practices  

---  

この記事が役に立ったら、ぜひ支援をお願いします！ https://ko-fi.com/toai5