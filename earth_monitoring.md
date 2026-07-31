# ChatGPTで始める衛星画像処理入門：AIで地球の環境変化を可視化する

地球規模の環境問題、特に森林破壊や水資源の枯渇は、現代社会が直面する最も深刻な課題の一つです。かつては専門的な知識と高価なソフトウェアが必要だった衛星画像解析も、今やChatGPTを活用することで、誰でも手軽に解析の第一歩を踏み出せるようになりました。

本記事では、ChatGPTを「コーディングのパートナー」として活用し、衛星画像から環境変化を検出する手法を解説します。

---

## 1. 衛星画像解析の基本ワークフロー

衛星画像（リモートセンシングデータ）を扱う際の一般的なステップは以下の通りです。

1.  **データ取得**: Sentinel-2（ESA提供）などの無料公開データを利用。
2.  **前処理**: 雲の除去、正規化。
3.  **解析**: 指数計算（NDVIやNDWI）による変化抽出。
4.  **可視化**: 時系列変化のマップ化。

## 2. ChatGPTにコードを書かせるコツ

衛星画像処理にはPythonのライブラリである `rasterio` や `geopandas` を多用します。ChatGPTに依頼する際は、以下のように具体的に指示を出すのがポイントです。

> **プロンプト例:**
> 「Pythonのrasterioとnumpyを使って、2つの衛星画像（T1とT2）のNDVI（正規化植生指数）を計算し、その差分から森林破壊の可能性が高いエリアを抽出するスクリプトを書いてください。」

## 3. 実践：森林破壊と水資源の検出

### 森林破壊の検出 (NDVI: 正規化植生指数)
植生の活性度を測るNDVIは、以下の式で求められます。
$NDVI = (NIR - Red) / (NIR + Red)$

```python
import rasterio
import numpy as np

def calculate_ndvi(nir_path, red_path):
    with rasterio.open(nir_path) as nir:
        nir_data = nir.read(1).astype('float32')
    with rasterio.open(red_path) as red:
        red_data = red.read(1).astype('float32')
    
    # NDVI計算
    ndvi = (nir_data - red_data) / (nir_data + red_data + 1e-8)
    return ndvi

# 差分をとることで変化を可視化
change_detection = ndvi_t2 - ndvi_t1
```

### 水資源の検出 (NDWI: 正規化水指数)
水域の変化を追跡するには、緑色光と近赤外光を利用するNDWIが有効です。

```python
def calculate_ndwi(green_path, nir_path):
    # 緑色光と近赤外光を用いた水域検出
    # (Green - NIR) / (Green + NIR)
    # 0以上の値が水域を示すことが多い
    ...
```

---

## 4. 環境レジリエンスを可視化する意義

AIを用いた解析の最大のメリットは、**「定量的かつ客観的な証拠」**を得られる点にあります。特定の地域の森林が過去数年でどれほど減少したか、ダムの水位がどのように変化しているかを可視化することで、政策提言や地域コミュニティの意思決定を強力にサポートできます。

## 5. 次のステップへ

ChatGPTを使えば、エラーの解決やアルゴリズムの最適化も迅速に行えます。まずは [Google Earth Engine](https://earthengine.google.com/) のようなプラットフォームとPython APIを組み合わせ、特定の地域のデータを取得することから始めてみてください。

技術の力で、地球の「今」を知り、未来を守るための行動を起こしましょう。

---

地球環境保護活動支援のためのKo-fiリンク: [https://ko-fi.com/toai_resilience]