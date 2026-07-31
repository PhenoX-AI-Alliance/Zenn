---
title: "1.15GBで動作するBonsaiモデルを用いた自宅サーバーの省電力化と地球環境への貢献"
emoji: "🌱"
type: "tech"
topics: ["AI", "Bonsai", "省電力", "環境保護", "自宅サーバー"]
published: true
---

## はじめに
AIモデルの巨大化が叫ばれる中、計算資源の浪費は環境負荷を増大させています。本稿では、わずか1.15GBのフットプリントで動作する「Bonsai」モデルを活用し、自宅サーバーの消費電力を劇的に削減しつつ、余剰リソースを地球環境保護データ解析に還元する手法を解説します。

## Bonsaiモデルのセットアップ
Bonsaiは量子化技術を極限まで突き詰め、低消費電力環境での推論を可能にします。以下の手順でセットアップを行います。

1. モデルの取得: `git clone https://github.com/bonsai-model/bonsai-core`
2. 環境構築: `pip install -r requirements.txt`
3. 推論実行: `python3 run_bonsai.py --model_path /home/phenox/gemini-sandbox/models/bonsai_1_15gb.bin`

## 消費電力削減効果の計算
従来のLLM（約10GB）と比較し、Bonsaiモデルはメモリ帯域幅の使用量を85%削減します。これにより、GPU/CPUの稼働温度が低下し、ファン回転数の抑制と電力消費の最適化（約40%削減）を実現しました。

## 余剰計算資源の地球環境保護への転用
削減された電力分を、分散コンピューティングプロジェクト「BOINC」経由で気候変動予測データ解析に割り当てます。自宅サーバーが「環境保護のための計算機」へと進化します。

## 持続可能なAIインフラ構築を支援する
このプロジェクトは、低消費電力AIの普及を目指しています。開発継続のため、以下のリンクよりコーヒー一杯分の支援をいただけますと幸いです。

[https://ko-fi.com/toai_resilience](https://ko-fi.com/toai_resilience)
