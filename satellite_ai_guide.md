# ChatGPTで始める衛星画像処理入門

近年、人工衛星から得られる地球観測データ（リモートセンシングデータ）の重要性が飛躍的に高まっています。特に、森林減少、ヒートアイランド現象、水質汚濁といった環境問題の監視において、AIを活用した迅速な解析が不可欠です。

本ガイドでは、ChatGPTを活用し、Pythonを用いた衛星画像処理のワークフローを構築する方法を解説します。

---

## 1. 衛星画像処理の基本ワークフロー

衛星画像解析は通常、以下のステップで行われます。
1. **データ取得**: Sentinel-2やLandsatなどの公開データを入手。
2. **前処理**: 幾何補正や大気補正。
3. **解析**: 指数計算（NDVIなど）や機械学習による分類。
4. **可視化**: 解析結果の地図化。

ChatGPTは、このプロセスにおける「コード生成」および「解析ロジックの最適化」において強力なパートナーとなります。

## 2. 実践：PythonによるNDVI（植生指数）の算出

森林の健全性を監視するため、最も広く使われる指標であるNDVIを算出するコードを生成します。

### ChatGPTへのプロンプト例
> 「PythonとRasterioライブラリを使用して、Sentinel-2の赤色バンド（B04）と近赤外線バンド（B08）からNDVIを計算し、GeoTIFFとして保存するコードを書いてください。」

### 生成されるPythonコードの例
```python
import rasterio
import numpy as np

def calculate_ndvi(red_path, nir_path, output_path):
    with rasterio.open(red_path) as red:
        red_data = red.read(1).astype('float32')
    with rasterio.open(nir_path) as nir:
        nir_data = nir.read(1).astype('float32')
        profile = nir.profile

    # NDVI計算: (NIR - Red) / (NIR + Red)
    ndvi = (nir_data - red_data) / (nir_data + red_data + 1e-8)

    profile.update(dtype=rasterio.float32, count=1)
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(ndvi.astype(rasterio.float32), 1)

# 使用例
calculate_ndvi('B04.tif', 'B08.tif', 'ndvi_result.tif')
```

## 3. 環境監視への応用

*   **森林減少の監視**: 時系列のNDVIデータを比較し、閾値以下のエリアを「森林喪失」として抽出します。
*   **ヒートアイランド対策**: 衛星の熱赤外バンドを利用して地表温度（LST）を算出し、都市の緑地計画の効果を検証します。
*   **水質モニタリング**: 水域の反射スペクトルからクロロフィル濃度を推定し、赤潮などの予兆を検知します。

ChatGPTのAPIを活用することで、これらの解析結果を要約させ、自動的にレポートを作成するシステムも構築可能です。

---

## 地球環境監視プロジェクトへの支援
本プロジェクトの持続的な運用と、オープンソース衛星解析ツールの開発のため、皆様のご支援をお願いいたします。
[地球環境監視プロジェクトを支援する (Ko-fi)](https://ko-fi.com/toai_resilience)

### 支援プラン
- ライトプラン: 500円/月 (感謝のメールと解析レポート共有)
- スタンダードプラン: 5,000円/月 (解析アルゴリズムの先行公開)
- プロフェッショナルプラン: 20,000円/月 (個別データ解析サポート)
- エンタープライズプラン: 100,000円/月 (地球環境レジリエンス解析の共同研究)