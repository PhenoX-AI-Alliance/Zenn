#!/usr/bin/env python3
import os
import sys
import glob
import re
import datetime
import shutil

# TOAI Zenn Publisher (Queueing Edition)
# This script is called by agents to format the markdown and put it into the queue.

ZENN_DIR = "/home/phenox/gemini-sandbox/TOAI_Generated/Zenn"
QUEUE_DIR = os.path.join(ZENN_DIR, "queue")
DRAFT_DIR = "/home/phenox/gemini-sandbox"

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
