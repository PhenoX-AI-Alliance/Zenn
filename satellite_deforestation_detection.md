# ChatGPTで始める衛星画像処理入門: 森林破壊検知編

近年、衛星データのオープン化とAI技術の進化により、個人のPCからでも地球規模の環境変化をモニタリングできるようになりました。本記事では、ChatGPTを「AIプログラミングパートナー」として活用し、Pythonを用いて衛星画像から森林破壊の兆候（NDVIの変化）を検知する方法を解説します。

---

## 1. ChatGPTを衛星画像処理に活用する理由

衛星画像処理には、地理空間データ特有の形式（GeoTIFFなど）や座標参照系（CRS）の知識が必要です。しかし、これらはChatGPTが得意とする分野です。

- **コード生成:** `rasterio`や`numpy`を使った複雑な行列演算のコードを瞬時に生成。
- **デバッグ:** 座標系エラーやデータ型の不一致といった、GIS処理で頻出するエラーの解決。
- **アルゴリズム検討:** 特定の土地被覆を抽出するためのしきい値設定などのロジック相談。

これらを活用することで、環境科学の専門家でなくても、迅速にプロトタイプを作成できます。

---

## 2. 実践：NDVIによる森林破壊検知

NDVI（正規化植生指数）は、植物の光合成活動を評価する指標です。森林破壊が起きると、この数値が顕著に低下します。

### 必要なライブラリのインストール
```bash
pip install rasterio numpy matplotlib
```

### Pythonコード: 時系列NDVIの変化検知
以下のコードは、2つの時期（T1, T2）の衛星画像からNDVIを算出し、その差分から減少エリアを特定する基本的なロジックです。

```python
import rasterio
import numpy as np

def calculate_ndvi(red_band, nir_band):
    # NDVI = (NIR - Red) / (NIR + Red)
    # ゼロ除算を防ぐために微小値を加える
    return (nir_band - red_band) / (nir_band + red_band + 1e-8)

# 1. 衛星画像の読み込み (赤色バンドと近赤外バンド)
with rasterio.open('satellite_t1.tif') as src1:
    red1, nir1 = src1.read(3), src1.read(4) # バンド番号はデータに依存
    ndvi1 = calculate_ndvi(red1.astype(float), nir1.astype(float))

with rasterio.open('satellite_t2.tif') as src2:
    red2, nir2 = src2.read(3), src2.read(4)
    ndvi2 = calculate_ndvi(red2.astype(float), nir2.astype(float))

# 2. 差分の計算
diff = ndvi2 - ndvi1

# 3. 森林破壊エリアの抽出 (NDVIが0.2以上減少した場所を検知)
deforestation_mask = diff < -0.2

print(f"検知された破壊面積の画素数: {np.sum(deforestation_mask)}")
```

---

## 3. 実装ステップ

1. **データ準備:** [Sentinel-2](https://scihub.copernicus.eu/)などから、分析したいエリアの同一地点の過去-現在の画像を取得します。
2. **ChatGPTへの指示:** 「`rasterio`を使って、2つのGeoTIFFからNDVIを計算し、その差分をヒートマップとして保存するPythonコードを書いて」と依頼します。
3. **実行と調整:** コードを実行し、結果が期待通りか確認します。もし座標系が合わない場合は、ChatGPTに「`reproject`を使って座標系を合わせるコードに修正して」と指示を出すのがコツです。
4. **可視化:** `matplotlib`を用いて、変化のあったエリアを色付けして可視化します。

---

## 最後に

衛星画像分析は、地球の健康状態を可視化する強力な武器です。今回紹介した手法は、オープンソースとAIを組み合わせることで、誰もが環境モニタリングに参加できることを示しています。

今後、より高精度な機械学習モデル（Deep Learning）を用いた自動検知システムなどの研究開発を加速させていく予定です。

**地球環境レジリエンス維持のため、研究開発を支援してください。**

[https://ko-fi.com/phenox](https://ko-fi.com/phenox)

あなたの支援が、より多くのオープンソース環境分析ツールの開発と、持続可能な未来への一歩となります。