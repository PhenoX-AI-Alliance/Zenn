# MCPとTypeScript SDK v2で構築する：地球環境レジリエンス・ダッシュボードの作り方

近年、AIエージェントが外部ツールやデータソースと直接対話するための標準規格として「**MCP (Model Context Protocol)**」が急速に注目を集めています。特にv2のリリースにより、より堅牢でスケーラブルな統合が可能になりました。

本記事では、MCP TypeScript SDK v2を活用し、地球環境センサーからデータを取得して3D可視化を行う「環境レジリエンス・ダッシュボード」の構築手法を解説します。

---

## 1. MCP (Model Context Protocol) v2 とは

MCPは、AIモデルとデータソース（データベース、API、ファイルシステムなど）を接続するためのオープンプロトコルです。v2では以下の点が強化されました。

*   **型安全性の向上**: TypeScriptのGenericsをフル活用し、ツール呼び出し時の型推論が強化。
*   **双方向通信の最適化**: クライアント・サーバー間のメッセージングが効率化され、低遅延なデータストリーミングが可能に。
*   **標準化されたライフサイクル管理**: リソースやプロンプトの動的更新が容易になりました。

---

## 2. 実装ガイド：TypeScript SDK v2の活用

まずは必要なパッケージをインストールします。

```bash
npm install @modelcontextprotocol/sdk
```

MCPサーバーを構築する際は、`McpServer`クラスを使用して、環境データを提供するためのエンドポイントを定義します。

---

## 3. 環境センサーデータから3Dメッシュへの変換

以下は、センサーAPIから気温・湿度データを取得し、それを3D空間上の点群（Point Cloud）データに変換するロジックのサンプルです。

```typescript
import { McpClient } from "@modelcontextprotocol/sdk/client";

// MCPクライアントの初期化
const client = new McpClient({
  serverUrl: "http://localhost:3000/env-sensors",
});

interface SensorData {
  id: string;
  lat: number;
  lon: number;
  temp: number;
}

/**
 * センサーデータを取得し、3D可視化用のJSONスキーマに変換
 */
async function fetchAndTransformTo3D() {
  // 1. センサーデータ取得
  const response = await client.callTool("get_environmental_data", {});
  const data = response.result as SensorData[];

  // 2. 3Dメッシュポイントへ変換（緯度経度をX,Y座標、気温をZ軸としてマッピング）
  const meshPoints = data.map((d) => ({
    x: d.lat * 100,
    y: d.lon * 100,
    z: d.temp * 10, // 気温を高さとして表現
    color: d.temp > 30 ? "red" : "blue"
  }));

  // 3. JSONスキーマとして返却
  return {
    type: "3d_visualization_object",
    format: "point_cloud",
    data: meshPoints,
    metadata: {
      timestamp: new Date().toISOString(),
      count: meshPoints.length
    }
  };
}
```

このロジックをMCPサーバーのツールとして公開することで、AIモデルは「現在の環境データを3Dで表示して」という指示に対して、自動的にこの関数を呼び出し、ダッシュボードの描画に必要なJSONを取得できるようになります。

---

## 4. 結論

MCP v2を活用することで、複雑な地球環境データをAIが理解可能な形式で即座に構造化し、視覚化パイプラインに流し込むことが可能になります。これにより、気候変動や災害レジリエンスのモニタリングにおいて、AIが「状況を把握し、可視化し、洞察を与える」という一連のプロセスが劇的に高速化されます。

ぜひ、皆さんの環境プロジェクトにもMCPを組み込んでみてください。

---

## 本プロジェクトの持続的な開発を支援する

https://ko-fi.com/phenox