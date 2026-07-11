#!/usr/bin/env python3
import os
import glob
import datetime
import subprocess
import shutil

# Zenn Queue Processor
# Run via cron every 15 minutes. Picks one file from queue/, commits and pushes it.

ZENN_DIR = "/home/phenox/gemini-sandbox/TOAI_Generated/Zenn"
QUEUE_DIR = os.path.join(ZENN_DIR, "queue")
ARTICLES_DIR = os.path.join(ZENN_DIR, "articles")
COUNT_FILE = os.path.join(ZENN_DIR, "deploy_count.txt")
MAX_DEPLOY_PER_DAY = 100

def get_github_token():
    try:
        with open("/home/phenox/gemini-sandbox/.env", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("GITHUB_ZENN_TOKEN="):
                    return line.strip().split("=", 1)[1].strip()
    except Exception:
        pass
    return None

def check_rate_limit():
    today = datetime.date.today().isoformat()
    count = 0
    if os.path.exists(COUNT_FILE):
        try:
            with open(COUNT_FILE, "r") as f:
                data = f.read().strip().split(",")
                if len(data) == 2 and data[0] == today:
                    count = int(data[1])
        except Exception:
            pass
            
    if count >= MAX_DEPLOY_PER_DAY:
        print(f"[{datetime.datetime.now().isoformat()}] 🛑 Daily deploy limit of {MAX_DEPLOY_PER_DAY} reached. Skipping.")
        return False
        
    return count, today

def process_queue():
    limit_data = check_rate_limit()
    if not limit_data:
        return
        
    count, today = limit_data
    
    # Get all markdown files in queue
    queued_files = glob.glob(os.path.join(QUEUE_DIR, "*.md"))
    if not queued_files:
        print(f"[{datetime.datetime.now().isoformat()}] Queue is empty.")
        return
        
    # Sort by creation time (oldest first)
    queued_files.sort(key=os.path.getctime)
    target_file = queued_files[0]
    filename = os.path.basename(target_file)
    
    os.makedirs(ARTICLES_DIR, exist_ok=True)
    dest_file = os.path.join(ARTICLES_DIR, filename)
    
    print(f"[{datetime.datetime.now().isoformat()}] Processing: {filename}")
    
    # Move to articles directory
    shutil.move(target_file, dest_file)
    
    # Publish
    token = get_github_token()
    if not token:
        print("Error: GITHUB_ZENN_TOKEN not found.")
        # Move it back to queue so we don't lose it
        shutil.move(dest_file, target_file)
        return
        
    try:
        subprocess.run(["git", "config", "user.name", "TOAI Auto Publisher"], cwd=ZENN_DIR, check=True)
        subprocess.run(["git", "config", "user.email", "toai@phenox-ai-alliance.com"], cwd=ZENN_DIR, check=True)
        
        subprocess.run(["git", "add", f"articles/{filename}"], cwd=ZENN_DIR, check=True)
        
        commit_msg = f"Auto-publish: TOAI Agent Report {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=ZENN_DIR, check=True)
        
        remote_url = f"https://{token}@github.com/PhenoX-AI-Alliance/Zenn.git"
        subprocess.run(["git", "remote", "set-url", "origin", remote_url], cwd=ZENN_DIR, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=ZENN_DIR, check=True)
        print("✅ Successfully pushed to GitHub.")
        
        # Increment counter
        with open(COUNT_FILE, "w") as f:
            f.write(f"{today},{count + 1}")
            
    except subprocess.CalledProcessError as e:
        print(f"Git operation failed: {e}")
        # Consider moving it back or just leaving it in articles. It won't be picked up again by queue processor,
        # but if we git add it, it's staged.

if __name__ == "__main__":
    process_queue()
