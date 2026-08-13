# 【OllamaローカルLLM運用】複数プロセスからの同時アクセス・VRAM枯渇・デッドロックを防ぐ「泥臭い」実践ノウハウ

ローカルLLM（QwenやLlama 3など）をOllamaで運用し、実用的なシステム（チャットボット、APIサーバー、バッチ処理など）を構築しようとすると、公式ドキュメントには載っていない「現実の壁」にぶつかります。

特に、**「複数プロセスからの同時アクセス」「VRAMの爆発（OOM）」「予期せぬデッドロックやハングアップ」**は、ローカルLLM運用における三大障害です。

本記事では、これらを力技と実用的な設計で乗り切るための「泥臭いノウハウ」を共有します。

---

## 1. 複数プロセスからの同時アクセスに対する排他制御

Ollamaのサーバープロセスはデフォルトで複数のリクエストを処理しようとしますが、LLMの推論はGPU/CPUのメモリと演算リソースを極限まで消費します。何も制御せずに複数のスクリプトから同時にリクエストを投げると、キューが詰まるか、内部でコンテキストスイッチが頻発してスループットが極端に低下します。

### ノウハウ：アプリケーション層での「セマフォ（排他ロック）」の強制
Ollama任せにするのではなく、呼び出し側のクライアントアプリケーション層で明確にロックをかけます。Pythonの `asyncio.Semaphore` や、ファイルロック・Redis等を用いた分散ロックを使用するのが鉄則です。

```python
import asyncio
from ollama import AsyncClient

# 同時実行数を「1」に制限（必要に応じてVRAM容量に合わせて増減）
ollama_semaphore = asyncio.Semaphore(1)

async def safe_generate(prompt: str):
    async with ollama_semaphore:
        client = AsyncClient()
        response = await client.generate(model='qwen2.5:7b', prompt=prompt)
        return response['response']
```
* **ポイント**: 「GPUは並列処理が得意」という幻想は捨て、モデルの推論は基本的に**シリアル（直列）処理**として設計した方が、結果的にスループットが安定します。

---

## 2. VRAM枯渇を防ぐロード・アンロード戦略

Ollamaはデフォルトで、一度ロードしたモデルをVRAM上に保持し続けます（`keep_alive`のデフォルトは5分）。複数の異なるモデル（例: Qwen 2.5 7B と Embedding用モデル）を切り替えて使おうとすると、瞬く間にVRAMが枯渇し、CUDA Out of Memory (OOM) エラーが発生します。

### ノウハウ①：使い終わったら「即座にアンロード」する
APIリクエストごとに、あるいは処理のブロックが終わり次第、`keep_alive: 0`を指定して明示的にVRAMからモデルを追い出します。

```python
import requests

def unload_model(model_name: str):
    # OllamaのAPIに空のリクエストを送りつつkeep_aliveを0にして即時アンロード
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model_name,
        "prompt": "",
        "keep_alive": 0 
    }
    requests.post(url, json=payload)
```

### ノウハウ②：モデルの「重量級」と「軽量級」の完全分離
VRAMが限られている環境（例: VRAM 16GB〜24GB）では、大型モデルを常駐させず、以下のようなライフサイクルポリシーを強制します。
1. **バッチ処理の前**: 必要なモデルがロードされているか確認。
2. **処理中**: 排他制御下で実行。
3. **処理直後**: `keep_alive: 0` で強制アンロードし、VRAMを完全にクリア。

---

## 3. デッドロックとハングアップ回避の「泥臭い」防衛策

長期稼働させていると、Ollamaプロセス自体が応答しなくなったり（ゾンビ状態）、Python側からのストリーミング読み取り中にコネクションが切れて永遠にブロックされる現象（デッドロック・ハング）が発生します。

### ノウハウ①：絶対的なタイムアウトの設定
requestsやhttpxを使う際、タイムアウト（`timeout`）を設定しないのは自殺行為です。LLMが生成ループに陥った場合や、内部でスタックした際にプロセスが永遠に帰ってきません。

```python
import httpx

# 読み取りタイムアウトを必ず設定する
with httpx.Client(timeout=httpx.Timeout(10.0, read=60.0)) as client:
    response = client.post(
        "http://localhost:11434/api/generate",
        json={"model": "qwen2.5:7b", "prompt": "こんにちは"}
    )
```

### ノウハウ②：Health Check と「死活監視 ＆ プロセス殺し」の自動化
Ollamaサーバー自体がハングした場合、APIからの復旧は不可能です。外部の番犬（Watchdog）スクリプトやsystemdの機能を使って、定期的にヘルスチェックを行い、応答がない場合は容赦なくプロセスを再起動します。

**Systemdでの自動再起動設定の例 (`/etc/systemd/system/ollama.service` に追記)**
```ini
[Service]
# クラッシュ時やハング時に自動再起動
Restart=always
RestartSec=5s
# フリーズ検知用のタイムアウト設定など
```

**シェルスクリプトによる簡易死活監視の例 (`watchdog.sh`)**
```bash
#!/bin/bash
# 30秒以内にOllamaのAPIから応答がなければプロセスを強制終了して再起動
response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 30 http://localhost:11434/api/tags)

if [ "$response" -ne 200 ]; then
    echo "Ollama is hanging or down. Restarting..."
    sudo pkill -9 ollama
    sudo systemctl restart ollama
fi
```

---

## まとめ

ローカルLLMの運用は、優雅なAIエンジニアリングというよりも、**「リソースの奪い合いを調停する泥臭いインフラ管理」**の側面が強くなります。

1. **排他制御**: クライアント側で同時実行数を絞る。
2. **メモリ管理**: `keep_alive: 0` で使い終わったら即座に捨てる。
3. **耐障害性**: タイムアウトと容赦ないプロセス再起動の仕組みを用意する。

これらを実装することで、安定したローカルLLMシステムを構築することができます。ぜひ現場で試してみてください。

---

もし本記事があなたのローカルLLM環境の構築・運用に役立ったなら、以下のリンクからコーヒーをごちそうしていただけると、さらなる検証と記事執筆の大きな励みになります！

☕ **[Ko-fiで筆者をサポートする（https://ko-fi.com/phenox）](https://ko-fi.com/phenox)**