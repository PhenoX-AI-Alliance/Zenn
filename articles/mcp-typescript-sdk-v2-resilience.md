---
title: "【2026年最新】MCP TypeScript SDK v2で構築する！環境データ解析LLMエージェント実践ガイド"
emoji: "🌍"
type: "tech"
topics: ["mcp", "typescript", "llm", "ai", "stripe"]
published: true
---

# 【2026年最新】MCP TypeScript SDK v2で構築する！環境データ解析LLMエージェント実践ガイド

Model Context Protocol（MCP）は、LLMと外部データソースやツールを接続するための標準規格として急速に普及しています。2026年7月にリリースされた **TypeScript SDK v2** では、型安全性の飛躍的な向上、効率的な非同期ストリーミング、そして大幅に最適化された通信層が導入され、プロダクション環境での信頼性が格段に高まりました。

本記事では、この最新の **MCP TypeScript SDK v2** を用いて、リアルタイムの環境データ（気温、CO2濃度、気象予報など）を外部APIから取得し、LLMエージェントに供給して「地球環境レジリエンス評価」を行わせるサーバー・クライアントの構築手法をハンズオン形式で解説します。

---

## 1. MCP TypeScript SDK v2 の主な特徴

v1からv2へのアップデートにおいて、主に以下のアーキテクチャ上の進化を遂げました。

1. **厳格な型安全性（Strict Type Safety）**: Zodなどのスキーマ定義と完全に統合され、ツール呼び出し時の入力・出力の型推論が強化されました。実行時エラーを未然に防ぎます。
2. **非同期ストリーミング（Async Streaming）**: 大容量の時系列データやセンサーログをブロックせずにストリーミング転送できるようになり、レイテンシが大幅に削減されました。
3. **高パフォーマンス通信層（High-Performance Transport）**: プロセス間通信やSSE（Server-Sent Events）のオーバーヘッドが軽減され、マルチエージェント環境下でも安定したスループットを発揮します。

---

## 2. アーキテクチャの概要

今回は、以下の2つのコンポーネントを実装します。

- **環境データMCPサーバー**: 気温、CO2濃度、気象予報のモック/実APIをラップし、MCPプロトコルを通じてデータを提供するサーバー。
- **レジリエンス評価エージェント**: MCPクライアントとしてサーバーに接続し、取得したデータをLLM（ClaudeやGPTなど）に渡して地域ごとの環境レジリエンス（耐久・回復力）をスコアリングさせるアプリケーション。

---

## 3. 実装：環境データMCPサーバーの構築

まずはプロジェクトを初期化し、最新のMCP SDK（`@modelcontextprotocol/sdk` v2系）とZodをインストールします。

```bash
mkdir mcp-environment-server
cd mcp-environment-server
npm init -y
npm install @modelcontextprotocol/sdk zod
npm install -D typescript @types/node tsx
npx tsc --init
```

次に、サーバーコード（`src/server.ts`）を記述します。ここでは、SDK v2の新しい型安全なツール定義（`McpServer`クラス）を活用します。

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// MCP Server v2 のインスタンス化
const server = new McpServer({
  name: "environment-data-server",
  version: "2.0.0",
});

// モック環境データ取得関数
async function fetchEnvironmentalMetrics(location: string) {
  // 実際にはここで外部の気象APIやIoTセンサー基盤にリクエストを送る
  return {
    location,
    timestamp: new Date().toISOString(),
    temperatureCelsius: 28.5,
    humidityPercent: 65,
    co2Ppm: 420.3,
    weatherForecast: "Partially cloudy with high UV index",
  };
}

// ツール登録: 特定地域の環境データを取得する
server.tool(
  "get_environmental_metrics",
  "指定された地域のリアルタイム気温、CO2濃度、気象予報を取得します",
  {
    location: z.string().describe("調査対象の地域名（例: Tokyo, Amazon, Geneva）"),
  },
  async ({ location }) => {
    const data = await fetchEnvironmentalMetrics(location);
    
    // SDK v2ではストリーミングや構造化されたコンテンツ返却が容易に
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(data, null, 2),
        },
      ],
    };
  }
);

// 標準入出力（stdio）トランスポートを使用してサーバーを起動
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Environment MCP Server v2 running on stdio");
}

main().catch((error) => {
  console.error("Fatal error in main():", error);
  process.exit(1);
});
```

---

## 4. 実装：LLMエージェント（MCPクライアント）の構築

続いて、MCPサーバーと通信し、取得したデータを基に環境レジリエンス評価を行うクライアント側のコードを実装します。

```bash
cd ..
mkdir mcp-environment-client
cd mcp-environment-client
npm init -y
npm install @modelcontextprotocol/sdk dotenv
npm install -D typescript @types/node tsx
```

クライアントコード（`src/client.ts`）を記述します。

```typescript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

async function runAgent() {
  // 子プロセスとしてMCPサーバーを起動・接続
  const transport = new StdioClientTransport({
    command: "npx",
    args: ["tsx", "../mcp-environment-server/src/server.ts"],
  });

  const client = new Client(
    {
      name: "resilience-evaluator-agent",
      version: "2.0.0",
    },
    {
      capabilities: {},
    }
  );

  await client.connect(transport);
  console.log("Connected to Environment MCP Server");

  // 1. サーバー側が提供しているツール一覧の取得
  const toolsList = await client.listTools();
  console.log("Available Tools:", toolsList.tools.map(t => t.name));

  // 2. ツールの実行（例: Tokyoの環境データを取得）
  const targetLocation = "Tokyo";
  console.log(`\nFetching metrics for ${targetLocation}...`);
  
  const toolResult = await client.callTool({
    name: "get_environmental_metrics",
    arguments: { location: targetLocation },
  });

  const rawDataText = (toolResult.content[0] as { type: "text"; text: string }).text;
  const environmentalData = JSON.parse(rawDataText);

  console.log("Received Environmental Data:", environmentalData);

  // 3. ここでLLM（Claudeなど）にデータを渡し、レジリエンス評価を実行するプロンプトを構築
  console.log("\n--- LLM Resilience Evaluation Prompt ---");
  console.log(`
以下の環境データに基づき、${targetLocation} の現在の地球環境レジリエンス（気候変動や都市負荷に対する耐性・回復力）を評価し、改善のための推奨アクションを3つ提示してください。

[データ]
- 気温: ${environmentalData.temperatureCelsius}℃
- 湿度: ${environmentalData.humidityPercent}%
- CO2濃度: ${environmentalData.co2Ppm} PPM
- 気象予報: ${environmentalData.weatherForecast}
  `);

  // 接続の終了
  await client.close();
}

runAgent().catch(console.error);
```

---

## 5. まとめ

TypeScript SDK v2の登場により、MCPを活用したエージェント開発はさらに堅牢かつスピーディーになりました。今回構築した環境データ解析エージェントは、IoT基盤や各種公開気象APIと組み合わせることで、持続可能な都市計画や環境モニタリングの強力なツールとして実用化できます。

ぜひ最新のSDKを使って、あなたのAIエージェントに豊かな外部コンテキストを接続してみてください。

---

## 地球環境レジリエンス支援へのご協力のお願い

私たちが開発するオープンソースの環境データ解析ツールやMCPサーバー群は、持続可能な地球環境の維持、気候変動対策を進める研究者やエンジニアを支援するためのものです。

地球環境のレジリエンス向上およびオープンソースエコシステムの継続的な発展のために、ぜひ温かいサポートをお願いいたします。

