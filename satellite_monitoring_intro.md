# ChatGPTで始める衛星画像処理入門：地球環境モニタリングの自動化

近年、衛星データのオープン化が進み、Sentinel-2やLandsatといった高解像度な地球観測データを誰でも利用できるようになりました。しかし、膨大な画像データを手作業で解析するのは困難です。

本記事では、ChatGPTをコーディングパートナーとして活用し、Pythonを用いて衛星画像から植生指標（NDVI）を算出し、環境変化を自動モニタリングする方法を解説します。

## 1. Pythonによる衛星画像処理の基礎

衛星画像は、多くの場合「GeoTIFF」形式で提供されます。Pythonでは、以下のライブラリを使用してこれらを効率的に処理します。

*   **rasterio**: 地理空間データの読み書きを行う標準的なライブラリ。
*   **numpy**: ピクセル単位の行列演算（NDVI計算など）を高速に行うためのライブラリ。
*   **matplotlib**: 解析結果を可視化するためのライブラリ。

## 2. 環境変化の検出：NDVI計算ロジック

植生の健康状態を示す指標であるNDVI（正規化植生指標）は、近赤外線（NIR）と赤色光（Red）の反射率から以下の式で算出されます。

$$NDVI = \frac{(NIR - Red)}{(NIR + Red)}$$

以下は、`rasterio`を使用して衛星画像からNDVIを算出するコード例です。

```python
import rasterio
import numpy as np

def calculate_ndvi(red_path, nir_path, output_path):
    with rasterio.open(red_path) as src_red:
        red = src_red.read(1).astype('float32')
    
    with rasterio.open(nir_path) as src_nir:
        nir = src_nir.read(1).astype('float32')
        profile = src_nir.profile

    # ゼロ除算を防ぐための計算
    ndvi = (nir - red) / (nir + red + 1e-8)

    # 結果を保存
    profile.update(dtype=rasterio.float32, count=1)
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(ndvi, 1)
    
    return ndvi
```

## 3. データの可視化

計算したNDVIマップを`matplotlib`で可視化します。これにより、植生の分布や変化を視覚的に捉えることができます。

```python
import matplotlib.pyplot as plt

def visualize_ndvi(ndvi_data):
    plt.figure(figsize=(10, 6))
    # 植生が豊かな場所を緑色で強調するカラーマップ
    img = plt.imshow(ndvi_data, cmap='RdYlGn', vmin=-1, vmax=1)
    plt.colorbar(img, label='NDVI Value')
    plt.title('NDVI Distribution Map')
    plt.axis('off')
    plt.show()

# 実行例
# ndvi = calculate_ndvi('red.tif', 'nir.tif', 'ndvi_output.tif')
# visualize_ndvi(ndvi)
```

## 結論

ChatGPTを活用することで、衛星データの読み込みから数値解析、可視化までの一連のパイプラインを短時間で構築できるようになりました。これにより、森林伐採の監視や農作物の生育状況把握など、地球環境モニタリングの自動化がより身近なものとなります。

今後は、時系列データを用いた異常検知や、機械学習モデルとの組み合わせにより、さらなる高度な分析に挑戦してみてください。

地球環境のレジリエンス向上のための継続的な開発支援をお願いします：https://ko-fi.com/toai_resilience