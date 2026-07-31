# ChatGPTで始める衛星画像処理入門：地球のレジリエンスを可視化する

気候変動や都市開発、自然災害の影響など、地球環境の変化を定量的かつ視覚的に捉える手段として「衛星画像解析」の重要性が高まっています。かつては専門的なリモートセンシングの知識や高価なソフトウェアが必要だったこの分野も、現在ではPythonとChatGPTの活用により、個人のPCから誰でもアクセス可能なものとなりました。

本記事では、衛星画像処理の基礎から、Pythonを用いた森林減少の検出手法までを解説します。

---

## 1. 衛星画像処理の現在地
現在、Sentinel-2やLandsatといった衛星データはオープンデータとして公開されており、誰でも解析が可能です。ChatGPTは、複雑な画像処理ライブラリのコード生成や、統計的な異常検知ロジックの構築において強力なパートナーとなります。

特に、NDVI（正規化植生指数）を用いた変化検知は、環境モニタリングの第一歩として非常に有効です。

## 2. 実践：Pythonによる森林減少の検出
衛星画像から植生の変化を抽出するには、近赤外線（NIR）と赤色光（Red）のバンドを利用した計算が一般的です。以下に、`rasterio`と`numpy`を用いた基本的な処理フローを示します。

### 事前準備
```bash
pip install rasterio numpy matplotlib
```

### 森林減少検出コード
このスクリプトは、2時点の衛星画像からNDVIを算出し、その差分から植生が減少した領域を特定する例です。

```python
import rasterio
import numpy as np

def calculate_ndvi(nir_band, red_band):
    # NDVI = (NIR - Red) / (NIR + Red)
    # ゼロ除算回避のためfloat型に変換
    nir = nir_band.astype(float)
    red = red_band.astype(float)
    ndvi = (nir - red) / (nir + red + 1e-8)
    return ndvi

def detect_deforestation(path_before, path_after, threshold=0.2):
    with rasterio.open(path_before) as src1, rasterio.open(path_after) as src2:
        # バンドを読み込み (ここでは仮にRed:バンド3, NIR:バンド4とする)
        red1, nir1 = src1.read(3), src1.read(4)
        red2, nir2 = src2.read(3), src2.read(4)

        ndvi1 = calculate_ndvi(nir1, red1)
        ndvi2 = calculate_ndvi(nir2, red2)

        # 植生が減少した領域を抽出
        diff = ndvi1 - ndvi2
        deforestation_mask = diff > threshold
        
        return deforestation_mask

# 使用例
# mask = detect_deforestation('sentinel_2022.tif', 'sentinel_2023.tif')
```

このコードにより、特定の閾値を超えてNDVIが低下した箇所を「森林が減少した可能性が高いエリア」として可視化できます。

---

## 3. 次のステップ
ChatGPTを活用すれば、さらに高度な解析も可能です。
- **機械学習モデルの構築**: Random ForestやCNN（畳み込みニューラルネットワーク）を用いた土地被覆分類。
- **API連携**: Google Earth Engine (GEE) とPythonを組み合わせた広域解析。

衛星画像処理は、単なる数値解析ではなく、地球の「健康状態」を診断するクリエイティブな作業です。ぜひ、今日からあなたの環境データ解析を始めてみてください。

---

## 環境データ解析の継続には資金が必要です
オープンソースの解析手法の開発や、衛星データの継続的なモニタリング環境を維持するためには、皆様のご支援が大きな力となります。以下のリンクからコーヒー一杯分のご支援をいただければ幸いです。

https://ko-fi.com/toai6