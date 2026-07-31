# 衛星画像解析で実現する地球環境レジリエンス：NDVI算出から都市ヒートアイランド対策まで

気候変動が加速する現代において、衛星データを用いた環境モニタリングは、持続可能な都市開発やレジリエンス（回復力）向上のための不可欠なツールとなっています。本記事では、Pythonを用いた衛星画像解析の基礎と、それを都市計画へ応用する手法を解説します。

---

## 1. 衛星画像解析の基本：NDVIの算出

正規化植生指数（NDVI）は、植物の活性度を評価するための指標です。近赤外線（NIR）と赤色光（Red）の反射特性を利用し、以下の式で算出されます。

$$NDVI = \frac{NIR - Red}{NIR + Red}$$

Pythonの`rasterio`ライブラリを使用して、衛星画像からNDVIを計算するコード例を紹介します。

```python
import rasterio
import numpy as np

def calculate_ndvi(red_path, nir_path, output_path):
    # 画像データの読み込み
    with rasterio.open(red_path) as red_ds:
        red = red_ds.read(1).astype('float32')
    with rasterio.open(nir_path) as nir_ds:
        nir = nir_ds.read(1).astype('float32')
        profile = nir_ds.profile

    # ゼロ除算を防ぐための処理
    np.seterr(divide='ignore', invalid='ignore')
    
    # NDVI計算
    ndvi = (nir - red) / (nir + red)
    
    # 結果の保存
    profile.update(dtype=rasterio.float32, count=1)
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(ndvi, 1)

# 使用例
# calculate_ndvi('red_band.tif', 'nir_band.tif', 'ndvi_output.tif')
```

---

## 2. 地球環境レジリエンスへの貢献度可視化：ヒートアイランド解析

都市ヒートアイランド現象の抑制は、都市レジリエンスを高める鍵です。衛星データを用いた解析は、以下のステップで都市計画に貢献します。

### 解析手法
1. **地表面温度（LST）の算出**: 衛星の熱赤外線バンドから地表面温度を推定します。
2. **NDVIとの相関分析**: 緑地（高いNDVI）と地表面温度（LST）を重ね合わせ、どの程度の植生率が温度抑制に寄与しているかを定量化します。
3. **都市計画への応用**:
    * **クールスポットの特定**: 高温エリアに対し、優先的に植樹や緑化を行うためのエビデンスとして活用します。
    * **風の道の確保**: 建物配置と温度分布を照らし合わせ、熱を逃がすための空間計画をシミュレーションします。
    * **気候変動適応策の評価**: 緑化プロジェクト実施前後のLST変化を追跡し、政策の効果を可視化します。

衛星データは、単なる監視ツールではなく、データ駆動型の都市設計を実現し、極端な気象現象に強い「適応力のある都市」を作るための羅針盤となります。

---

本プロジェクトの計算リソース維持のため、Ko-fiで支援をお願いします: https://ko-fi.com/toai_resilience