# AIと衛星データで地球のレジリエンスを可視化する：PythonによるNDVI解析入門

気候変動や都市化が地球環境に与える影響を定量的に把握することは、持続可能な未来を築くための第一歩です。近年、Sentinel-2などの高解像度衛星データと、ChatGPTをはじめとする大規模言語モデル（LLM）の組み合わせにより、専門的な画像処理のハードルが劇的に下がっています。

本記事では、Pythonを活用した衛星画像解析の基本と、AIをパートナーとして開発を効率化する方法を解説します。

---

### 1. Pythonによる衛星データ解析の基本
衛星データ（特に欧州宇宙機関のSentinel-2）は、可視光線だけでなく近赤外線（NIR）などのバンドを含んでおり、地表の状態を詳細に分析可能です。Pythonでは、主に以下のライブラリを使用して解析を行います。

*   **rasterio**: 衛星画像（GeoTIFF）の読み込み-書き込み
*   **numpy**: 数値計算（バンド演算）
*   **matplotlib**: データの可視化

まずは、これらのライブラリをインストールします。
```bash
pip install rasterio numpy matplotlib
```

---

### 2. LLMを活用したスクリプト開発
衛星画像処理のコードをゼロから書くのは複雑ですが、ChatGPTなどのLLMを活用すれば、必要なアルゴリズムの生成やエラー修正を大幅に加速できます。

**LLMへのプロンプト例：**
> 「Sentinel-2の赤色バンド（B04）と近赤外線バンド（B08）のGeoTIFFファイルを読み込み、NDVIを計算して可視化するPythonスクリプトを作成してください。エラーハンドリングも含めて記述してください。」

このように意図を伝えることで、すぐに動作する雛形が得られます。さらに、「計算結果を正規化してヒストグラムを表示して」といった追加要望にも即座に応えてくれるため、試行錯誤のサイクルを高速化できます。

---

### 3. 具体例：NDVI（正規化植生指標）の計算
NDVIは、植生の活性度を示す指標です。以下のコードは、赤色バンドと近赤外線バンドを用いてNDVIを算出する基本的な例です。

```python
import rasterio
import numpy as np
import matplotlib.pyplot as plt

# データの読み込み
with rasterio.open('B04.tif') as red_band:
    red = red_band.read(1).astype('float32')
with rasterio.open('B08.tif') as nir_band:
    nir = nir_band.read(1).astype('float32')

# NDVI計算: (NIR - Red) / (NIR + Red)
ndvi = (nir - red) / (nir + red + 1e-8) # 0除算防止

# 可視化
plt.imshow(ndvi, cmap='RdYlGn')
plt.colorbar(label='NDVI')
plt.title('Vegetation Health Analysis')
plt.show()
```

このコードをベースに、特定の地域を切り抜いたり、時系列で変化を追う機能を追加していくことで、環境レジリエンスの評価が可能になります。

---

### 4. まとめ：地球の未来をコードで描く
AIを駆使することで、衛星データ解析は「専門家のもの」から「誰もが環境変化をモニタリングできるツール」へと進化しました。この技術を使い、森林破壊の監視や都市の緑地計画など、地球環境のレジリエンス向上に貢献するプロジェクトをぜひ始めてみてください。

継続的な開発と、より高度な解析手法の共有を支えてくださる皆様を募集しています。

**地球環境の持続可能性をコードで支える：**
[https://ko-fi.com/phenox](https://ko-fi.com/phenox) を設置し、継続的な開発を支援してください。また、月額5,000円のライトプランから100,000円のエンタープライズプランまでのサポートティアを用意しています。詳細は [https://buy.stripe.com/test_dummy_link](https://buy.stripe.com/test_dummy_link) へ。