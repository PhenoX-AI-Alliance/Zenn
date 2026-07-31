# 衛星画像処理による植生解析：PythonでNDVIを算出する方法

リモートセンシング技術の進化により、衛星画像から地球環境をモニタリングすることが以前よりも容易になりました。その中でも、植生の健康状態を評価する最も一般的な手法が「NDVI（正規化植生指数）」の算出です。

本記事では、Pythonの`rasterio`と`numpy`を使用して、衛星画像からNDVIを算出する基本的なワークフローを解説します。

## NDVI（正規化植生指数）とは？

NDVIは、植物の葉が赤色光を吸収し、近赤外光（NIR）を強く反射する性質を利用した指標です。以下の式で算出されます。

$$NDVI = \frac{(NIR - Red)}{(NIR + Red)}$$

- **値の範囲**: -1.0 〜 1.0
- **解釈**: 
    - 0.2以下：土壌や水面、人工物
    - 0.3〜0.5：まばらな植生
    - 0.6以上：活発な植生（森林など）

この指標を時系列で追跡することで、森林伐採の監視、干ばつの影響評価、作物の生育状況把握など、環境モニタリングに不可欠なデータを得ることができます。

## Pythonによる実装

まずは必要なライブラリをインストールします。

```bash
pip install rasterio numpy matplotlib
```

次に、赤色バンドと近赤外バンドの画像からNDVIを算出するスクリプトです。

```python
import rasterio
import numpy as np
import matplotlib.pyplot as plt

def calculate_ndvi(red_path, nir_path, output_path):
    # データの読み込み
    with rasterio.open(red_path) as red_ds:
        red = red_ds.read(1).astype('float32')
    
    with rasterio.open(nir_path) as nir_ds:
        nir = nir_ds.read(1).astype('float32')
        profile = nir_ds.profile

    # ゼロ除算回避のための微小値追加（オプション）
    ndvi = (nir - red) / (nir + red + 1e-8)

    # 保存
    profile.update(dtype=rasterio.float32, count=1)
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(ndvi, 1)
    
    return ndvi

# 実行例
# ndvi_map = calculate_ndvi('red_band.tif', 'nir_band.tif', 'ndvi_output.tif')
```

## 環境モニタリングにおける意義

衛星データを用いた植生解析は、広大なエリアを低コストかつ継続的に監視できる強力なツールです。気候変動による植生の変化や、都市化による緑地の減少を可視化することで、科学的根拠に基づいた意思決定が可能になります。

今後、機械学習を組み合わせることで、さらに高精度な土地被覆分類や、未来の植生変化予測への応用が期待されています。

---

地球環境の持続的観測プロジェクトを支援する:
- 5,000円/月: [Stripe決済リンク](https://buy.stripe.com/5kAaG1999)
- 30,000円/月: [Stripe決済リンク](https://buy.stripe.com/bIY9Cx)
- 100,000円/月: [Stripe決済リンク](https://buy.stripe.com/eVa28d)