#!/usr/bin/env python3
import os
import sys
import glob
import re
import datetime
import shutil
import json
import urllib.request

# TOAI Zenn Publisher (Queueing Edition)
# This script is called by agents to format the markdown and put it into the queue.

ZENN_DIR = "/home/phenox/gemini-sandbox/TOAI_Generated/Zenn"
QUEUE_DIR = os.path.join(ZENN_DIR, "queue")
DRAFT_DIR = "/home/phenox/gemini-sandbox"

def purify_article(raw_content):
    url = "http://localhost:11434/api/generate"
    prompt = (
        "あなたは極めて優秀なテックリードであり、プロフェッショナルな技術ライターです。\n"
        "以下の文章は、AIエージェントが雑多に吐き出したシステムログやメモの羅列です。\n"
        "これを読み解き、「人間の熟練エンジニアが書いた、あるいは非常に高度で知的なAIが記述した、洗練された技術ブログ記事」として**全体を再構築（フルリライト）**してください。\n\n"
        "【絶対厳守ルール】\n"
        "1. 意味不明なコミットハッシュ（例: [main 265a091]等）、システム内部のローカルパス、ダミーのリンク切れURLは**すべて完全に削除**すること。\n"
        "2. 架空のStripe決済リンクや、「○○円で販売します」「注: これはデモンストレーション用です」といったAI特有の**架空の商材販売（Monetizationのごっこ遊び）の記述は一切排除**すること。\n"
        "3. 単なる事実の羅列ではなく、技術的な背景、直面した課題、解決策（改善等）という論理的で読み応えのあるストーリー展開を持たせること。\n"
        "4. 幼稚な口調を避け、「である・だ」調のプロフェッショナルな文体とし、絵文字（Emoji）は本文中で一切使用しないこと。\n"
        "5. AIの「ごっこ遊び」や「安っぽいAI生成感」を完全に消し去り、技術的な深みと知性を感じさせる質の高いMarkdown記事に昇華させること。\n\n"
        "【元の雑多な文章】\n"
        f"{raw_content[:5000]}"
    )
    payload = {
        "model": "nutboy02/Qwen3.6-35B-A3B-Claude-4.7-Opus-abliterated-uncenfull:Q2_K_MTX",
        "prompt": prompt,
        "stream": False,
        "keep_alive": -1
    }
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=1800) as response:
            result = json.loads(response.read().decode('utf-8'))
            clean_text = result.get("response", "").strip()
            if clean_text:
                return clean_text
            return raw_content
    except Exception as e:
        print(f"Purification failed: {e}")
        return raw_content

def convert_to_zenn_queue(draft_path):
    if not os.path.exists(draft_path):
        print(f"Error: {draft_path} does not exist.")
        return False
        
    os.makedirs(QUEUE_DIR, exist_ok=True)
    
    with open(draft_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    title = "TOAI Agent Report"
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        title = title_match.group(1).replace('"', '')
        content = re.sub(r'^#\s+.+\n+', '', content, count=1)
        
    print(f"Purifying article '{title}' via Ollama...")
    content = purify_article(content)
        
    slug = datetime.datetime.now().strftime("toai-report-%Y%m%d-%H%M%S")
    
    frontmatter = f"""---
title: "{title}"
emoji: "🌟"
type: "tech"
topics: ["TOAI", "AI", "Agent"]
published: true
---

"""
    out_path = os.path.join(QUEUE_DIR, f"{slug}.md")
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(frontmatter + content)
        
    print(f"Queued Zenn article: {out_path}")
    
    # Move the original draft to prevent processing it again
    try:
        shutil.move(draft_path, draft_path + ".queued")
    except Exception as e:
        print(f"Could not rename draft: {e}")
        
    return out_path

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
        convert_to_zenn_queue(target)
    else:
        drafts = glob.glob(os.path.join(DRAFT_DIR, "zenn_draft*.md"))
        if not drafts:
            drafts = glob.glob(os.path.join(DRAFT_DIR, "zenn_book_*.md"))
        
        drafts = [d for d in drafts if not d.endswith(".queued") and not d.endswith(".published")]
        
        if drafts:
            for draft in drafts:
                print(f"Queueing draft: {draft}")
                convert_to_zenn_queue(draft)
        else:
            print("No pending Zenn drafts found.")
