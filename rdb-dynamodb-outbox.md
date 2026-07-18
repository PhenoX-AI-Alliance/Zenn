---
title: "RDBとDynamoDBの二重書き込みで発生する整合性問題とTransactional Outboxで実現する地球環境レジリエンスデータ管理"
topics: ["aws", "dynamodb", "rdb", "architecture", "sustainability"]
type: "tech"
published: true
---

# RDBとDynamoDBの二重書き込みで発生する整合性問題とTransactional Outboxによる地球環境レジリエンスデータ管理

## はじめに

近年、クラウドネイティブなアーキテクチャが一般化し、特に規模の大きいシステムではデータベースの選択が重要な課題となっています。本稿では、リレーショナルデータベース（RDB）とNoSQLデータベースであるDynamoDBを組み合わせたハイブリッド構成において、二重書き込みが引き起こす整合性問題を解析し、Transactional Outboxパターンを用いた解決策を紹介します。特に「地球環境レジリエンス」という具体的なユースケースに焦点を当て、実装例を交えながら技術的詳細を解説します。

## 1. RDBとDynamoDBの二重書き込みが引き起こす整合性問題

### 1.1 背景：ハイブリッドデータストアアーキテクチャ

現代の多くのシステムは、トランザクション処理にはRDB（例：PostgreSQL）を、スケーラビリティや高速リクエスト処理にはDynamoDBを使用するハイブリッド構成を取ることが一般的です。例えば：

- **RDB**: 公式データ（書き込み厳密性が求められる）
- **DynamoDB**: 非公式データやキャッシュ層（読み取り高速化・スケーラビリティ向上）

### 1.2 発生しやすい整合性問題

二重書き込みシナリオでは、以下の問題が発生しやすくなります。

#### (1) 書き込み失敗による不整合

```
[アプリケーション] 
   │
   ├─> [RDB] 書き込み成功 ✅
   │
   └─> [DynamoDB] 書き込み失敗 ❌
```

この場合、RDBには正しいデータが保存されているが、DynamoDBには反映されていないため、読み取り側からは不正確なデータが返される。

#### (2) 順序不整合（イベント遅延）

DynamoDB側の書き込みが RDB よりも遅れる場合、一時的に整合性が崩れる。

#### (3.2 デッドレター（Dead Letter）蓄積

DynamoDB側のエラーが解決されず、再試行が続けられない状態に陥る。

---

## 2. Transactional Outboxパターンの概要

### 2.1 パターンの定義

Transactional Outboxは、**「1つのトランザクション内で「メインデータ」と「アウトボックス用メッセージテーブル」の両方を書き込む」**という手法です。このパターンにより、メインデータベースとサブスケール先（例：DynamoDBや他システム）間の整合性が保証されます。

### 2.2 基本構成要素

| 要素 | 説明 |
|------|------|
| メインデータテーブル | RDB内の公式データ保存先 |
| アウトボックステーブル | 同じトランザクション内で更新されるメッセージキュー |
| デリーバー | アウトボックスからメッセージを読み取り、DynamoDB等へ転送するプロセス |

---

## 3. 地球環境レジリエンスデータ管理における応用例

### 3.1 ユースケース概要

「地球環境レジリエンス」とは、気候変動や自然災害に対する社会的・技術的耐性を支えるデータ基盤を指します。例えば：

- 気象観測データの蓄積
- 災害被害情報のリアルタイム共有
- 復旧資源の最適配分

このようなシステムでは、**「正確性」と「可用性」の両立**が求められます。

### 3.2 要求仕様

| 項目 | 内容 |
|------|------|
| 書き込み | 公式データはRDB、非公式データや集計結果はDynamoDB |
| 整合性 | RDBとDynamoDBのデータ不整合を最小化 |
| 可用性 | DynamoDBによる高速読み取りを維持 |
| 信頼性 | メッセージのロストや duplication を防止 |

---

## 4. Transactional Outboxによる実装例

### 4.1 テーブル設計

#### (1) メインテーブル（RDB）

```sql
CREATE TABLE environmental_events (
    id UUID PRIMARY KEY,
    event_type VARCHAR(50),
    location POINT,
    timestamp TIMESTAMP,
    severity INT
);
```

#### (2) アウトボックステーブル

```sql
CREATE TABLE outbox_messages (
    id UUID PRIMARY KEY,
    aggregate_id UUID,
    payload JSONB,
    published_at TIMESTAMP DEFAULT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

### 4.2 書き込みプロセス（例：Node.js + TypeORM）

```typescript
await dataSource.transaction(async (tx) => {
    // メインデータの書き込み
    const event = tx.create(EnvironmentalEvent, {
        id: uuid(),
        eventType: 'FLOOD',
        location: { type: 'Point', coordinates: [139.6917, 35.6895] },
        timestamp: new Date(),
        severity: 3
    });
    await tx.save(event);

    // アウトボックスメッセージの書き込み
    const message = tx.create(OutboxMessage, {
        id: uuid(),
        aggregateId: event.id,
        payload: JSON.stringify({
            type: 'EnvironmentalEventCreated',
            data: event
        }),
        publishedAt: null
    });
    await tx.save(message);
});
```

---

### 4.3 デリーバー（DynamoDBへの転送プロセス）

```javascript
const deliverMessages = async () => {
    const messages = await db.query(`
        SELECT * FROM outbox_messages 
        WHERE published_at IS NULL 
        ORDER BY created_at ASC 
        LIMIT 100
    `);

    for (const msg of messages) {
        try {
            const payload = JSON.parse(msg.payload);
            await dynamoDb.put({
                TableName: 'EnvironmentalEvents',
                Item: {
                    pk: `EVENT#${payload.data.id}`,
                    sk: `TIMESTAMP#${payload.data.timestamp}`,
                    ...payload.data
                }
            }).promise();

            // 成功したらフラグを立てる
            await db.query(`
                UPDATE outbox_messages 
                SET published_at = NOW() 
                WHERE id = $1
            `, [msg.id]);

        } catch (err) {
            console.error('DynamoDB書き込み失敗:', err);
            // エラー時はリトライ対象とする
        }
    }
};
```

---

## 5. メリットとベストプラクティス

### 5.1 メリット

| 項目 | 説明 |
|------|------|
| 整合性保証 | RDBとDynamoDBの同期不整合を回避 |
| 非同期処理 | DynamoDB側の書き込み負荷を分散 |
| エラー耐性 | 失敗時の再試行が容易 |
| スケーラビリティ | デリーバーの並列化により負荷分散 |

### 5.2 ベストプラクティス

- **Idempotencyの確保**  
  DynamoDBへの書き込みは冪等性を持たせ、重複書き込みを防ぐ。

- **メッセージの有効期限設定**  
  `outbox_messages` には TTL を設定し、一定時間経過後の未処理メッセージを削除。

- **De-duplicationキーの使用**  
  DynamoDB側で `id` をパーティションキーとして使用し、同一イベントの重複登録を防ぐ。

---

## 6. 補足：Transactional Outbox vs DynamoDB Streams vs Change Data Capture (CDC)

| 比較項目 | Transactional Outbox | DynamoDB Streams | CDC（例：Debezium） |
|----------|----------------------|------------------|---------------------|
| 整合性保証 | ✅ 強力 | ❌ 保証なし | ✅ RDB側は保証 |
| 実装難易度 | 中 | 低 | 高 |
| 可搬性 | 高 | 低（DynamoDB限定） | 中 |
| 遅延 | 数秒〜数分 | リアルタイム | 数秒 |

DynamoDB Streamsは高速だが整合性保証がないため、RDBとの整合性が必要な場合は **Transactional Outbox が適切** です。

---

## 7. おわりに：地球環境レジロジエンスに向けたデータ戦略

地球規模の環境データ管理においては、「正確性」と「スケーラビリティ」の両立が不可欠です。RDBとDynamoDBのハイブリッド構成はその実現に貢献しますが、整合性問題は必ず発生します。

そこで、Transactional Outboxパターンは「**書き込み一貫性**」と「**非同期伝播**」の両方を満たす有力なソリューションです。特に気候モニタリングや災害応答システムのようなクリティカルな領域では、このパターンの導入は推奨されます。

---

## 参考文献・リンク

- [Martin Fowler - Transactional Outbox](https://www.martinfowler.com/articles/patterns-of-distributed-systems/transactional-outbox.html)
- AWS公式ドキュメント：DynamoDBとRDSの連携
- Debezium - CDCツール

---

ご質問や特定の言語/フレームワークでの実装例（Spring Boot、Laravel、Goなど）が必要であれば、後ほどご相談ください。

## まとめ
本稿では、RDBとDynamoDBの二重書き込みにおける整合性問題と、Transactional Outboxパターンによる解決策、そしてそれが地球環境レジリエンスデータ管理にどう貢献するかを解説しました。

## 支援のお願い
この技術記事が役立ちましたら、今後の執筆活動を応援していただけると幸いです。
ぜひ以下のリンクからご支援ください：
https://ko-fi.com/phenox_noc2
