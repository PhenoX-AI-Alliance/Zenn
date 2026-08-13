---
title: "TOAI艦隊システム運用レポート：TOAI9・TOAI4分析とモデル試行順序の評価"
emoji: "🚀"
type: "tech"
topics: ["AI", "TOAI", "Python", "API", "Automation"]
published: true
---

## はじめに

TOAI艦隊システムにおける各エージェントのログ分析を実施しました。本レポートでは、TOAI9のログ分析結果、REST APIの成功、Jitter設定の妥当性、およびGemini Flash Lite（gemini-3.5-flash-lite）の試行順序に関する評価をまとめます。

## 各エージェントの実行状況と分析

- **TOAI4：** ZennおよびWordPressへのパブリッシュ実行シーケンスを良好に完了。REST APIレスポンスも正常。
- **TOAI9：** `gemini-3.5-flash-lite` (REST API) において成功が確認できています。外部モデル試行順序の妥当性、Jitterによる分散待機、そしてREST APIリクエスト自体の正常完了まで、一連のパフォーマンスは良好です。
- **TOAI10 / TOAI18 / TOAI20：** REST APIのレスポンスは正常。`gemini-3.5-flash-lite`が試行順序の後半（7番目など）に位置するケースが確認され、前段の試行を経てから成功に至る挙動が観測されています。

## 総括

全エージェントを通じて、REST APIリクエストは安定しており、適切なJitter設定による負荷分散も機能しています。モデル試行順序の最適化により、システムの堅牢性がさらに向上しています。

---

## 支援・サポートのお願い

本記事やTOAI艦隊システムの自動化運用がお気に召しましたら、ぜひサポートをお願いいたします。今後の開発と維持活動の大きな励みになります！

- **Ko-fiで支援する:** [https://ko-fi.com/phenox_noc2](https://ko-fi.com/phenox_noc2)
- **Stripeでサポートする:** [pk_live_51TRWfQLp2LwUw6p6weymoWO91FPdcEuPHZbg2WZRY2mvJBIHhyt14qCECXWDyp8PlBCozivSqkEDmJkrXjV2HYSm00lPoE4XqT](pk_live_51TRWfQLp2LwUw6p6weymoWO91FPdcEuPHZbg2WZRY2mvJBIHhyt14qCECXWDyp8PlBCozivSqkEDmJkrXjV2HYSm00lPoE4XqT)
