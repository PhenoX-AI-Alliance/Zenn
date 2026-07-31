# ChatGPTで始める衛星画像処理入門: 森林破壊検知の実装

衛星画像データは、地球環境の変化を監視するための強力なツールです。特に欧州宇宙機関（ESA）が運用する**Sentinel-2**は、無料かつ高頻度で観測データを提供しており、個人開発や研究でも広く活用されています。

本記事では、Pythonを用いてSentinel-2データからNDVI（正規化植生指標）を算出し、ChatGPTを活用して森林破壊を検知する基本的なフローを解説します。

---

## 1. Sentinel-2とNDVIの基礎知識

### Sentinel-2とは
Sentinel-2は、マルチスペクトルカメラを搭載した衛星で、地表の反射率を複数の波長帯（バンド）で観測します。森林監視には、特に以下のバンドが重要です。
*   **B04 (赤色光):** 植物の葉緑素に吸収される帯域
*   **B08 (近赤外線/NIR):** 植物の葉の構造によって強く反射される帯域

### NDVI (正規化植生指標)
NDVIは、植生の活性度を示す指標で、以下の式で計算されます。
$$NDVI = \frac{NIR - Red}{NIR + Red} = \frac{B08 - B04}{B08 + B04}$$
値は -1 から 1 の範囲をとり、値が高いほど植物が繁茂していることを示します。森林破壊が起きると、この値が急激に低下するため、時系列比較によって変化を検知可能です。

---

## 2. PythonによるNDVI計算の実装

`rasterio`と`numpy`を使用して、GeoTIFF形式の衛星画像からNDVIを算出します。

```python
import rasterio
import numpy as np

def calculate_ndvi(red_path, nir_path, output_path):
    with rasterio.open(red_path) as red_ds, rasterio.open(nir_path) as nir_ds:
        red = red_ds.read(1).astype('float32')
        nir = nir_ds.read(1).astype('float32')
        
        # NDVI計算 (ゼロ除算回避のため微小値を加算)
        ndvi = (nir - red) / (nir + red + 1e-8)
        
        # メタデータの取得と保存
        profile = red_ds.profile
        profile.update(dtype=rasterio.float32, count=1)
        
        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(ndvi, 1)
    print(f"NDVI画像を保存しました: {output_path}")

# 使用例
# calculate_ndvi('B04.tif', 'B08.tif', 'ndvi_result.tif')
```

---

## 3. ChatGPTで変化を解釈する

NDVIの算出結果を二時期（T1とT2）で比較し、差分画像を作成します。この数値データをChatGPTに渡すことで、高度な分析支援を受けることができます。

### ChatGPTへのプロンプト例
算出された統計値（平均値、標準偏差、変化率など）をCSV等で抽出し、以下のプロンプトでChatGPTに問いかけてみてください。

> 「ある森林地域におけるNDVIの時系列データです。T1からT2にかけて平均値が0.7から0.3に低下しました。この地域で発生した可能性のある事象（伐採、山火事、自然災害など）を、気候データや地理的特性を考慮して考察してください。また、この結果を可視化するための最適なカラーマップの提案もお願いします。」

ChatGPTは、数値の背後にある意味や、異常検知の閾値設定のアドバイス、さらには結果をレポート化するための構成案を即座に提示してくれます。

---

## 4. 結論

Sentinel-2データとPython、そしてChatGPTを組み合わせることで、専門的なリモートセンシング解析のハードルは劇的に下がりました。まずは小さなエリアからNDVIの差分を確認し、自分の居住地や関心のある森林の変化を追跡することから始めてみてください。

---

地球環境のレジリエンス維持を支援する：Ko-fi支援リンク [https://ko-fi.com/toai5]
月額支援プラン（ライト: 5,000円/月）への加入リンク [https://buy.stripe.com/toai5_light]