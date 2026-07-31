---
title: "1.15GBで動くBonsaiモデルを用いた、地球環境負荷を最小化するローカル推論サーバー構築ガイド"
emoji: "🌱"
type: "tech"
topics: ["AI", "Bonsai", "Sustainability", "GreenIT", "LocalLLM"]
published: true
---

# 1.15GBで動くBonsaiモデルを用いた、地球環境負荷を最小化するローカル推論サーバー構築ガイド

大規模言語モデルの運用には膨大な電力が消費されます。本稿では、わずか1.15GBの軽量Bonsaiモデルを活用し、GPU消費電力を極限まで抑えたローカル推論サーバーの構築手順を解説します。

## 環境構築手順

1. **量子化モデルの選定**
   - Bonsai-v1 (1.15GB) を `llama.cpp` でロードします。これにより、VRAM消費を抑え、アイドル時の消費電力を最小化します。

2. **電力最適化設定**
   - `nvidia-smi -pl 50` を実行し、GPUの電力制限を50Wに設定してください。
   - `power-profiles-daemon` を用いて、システムを `power-saver` モードに固定します。

3. **推論サーバーの起動**
   - 推論には `llama-cpp-python` を使用し、バッチサイズを1に制限することで、ピーク時の電力スパイクを抑制します。

## 地球環境レジリエンス支援
本プロジェクトの維持と、環境負荷低減技術の研究開発を支援してください。

[地球環境レジリエンス支援（月額5,000円〜100,000円）](https://buy.stripe.com/test_environment_resilience)
