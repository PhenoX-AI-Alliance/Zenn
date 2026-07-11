#!/usr/bin/env python3
import os
import glob
import datetime
import subprocess
import shutil
import sys

# TOAI Content Dispatcher
# Run via cron every 15 minutes. Picks one file from queue/,
# and alternates between pushing to Zenn and WordPress.

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

def push_to_zenn(target_file, filename):
    print(f"[{datetime.datetime.now().isoformat()}] Dispatching to Zenn: {filename}")
    os.makedirs(ARTICLES_DIR, exist_ok=True)
    dest_file = os.path.join(ARTICLES_DIR, filename)
    
    # Move to articles directory
    shutil.move(target_file, dest_file)
    
    token = get_github_token()
    if not token:
        print("Error: GITHUB_ZENN_TOKEN not found.")
        shutil.move(dest_file, target_file)
        return False
        
    try:
        subprocess.run(["git", "config", "user.name", "TOAI Auto Publisher"], cwd=ZENN_DIR, check=True)
        subprocess.run(["git", "config", "user.email", "toai@phenox-ai-alliance.com"], cwd=ZENN_DIR, check=True)
        
        subprocess.run(["git", "add", f"articles/{filename}"], cwd=ZENN_DIR, check=True)
        
        commit_msg = f"Auto-publish: TOAI Agent Report {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=ZENN_DIR, check=True)
        
        remote_url = f"https://{token}@github.com/PhenoX-AI-Alliance/Zenn.git"
        subprocess.run(["git", "remote", "set-url", "origin", remote_url], cwd=ZENN_DIR, check=True)
        
        # 競合回避のため pull --rebase を実行
        try:
            subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=ZENN_DIR, check=True)
        except subprocess.CalledProcessError as pull_e:
            print(f"Warning: git pull failed, attempting to push anyway: {pull_e}")
            
        subprocess.run(["git", "push", "origin", "main"], cwd=ZENN_DIR, check=True)
        print("✅ Successfully pushed to Zenn (GitHub).")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Zenn Git operation failed: {e}")
        return False

def push_to_wordpress(target_file, filename):
    print(f"[{datetime.datetime.now().isoformat()}] Dispatching to WordPress: {filename}")
    publisher_script = "/home/phenox/gemini-sandbox/TOAI_Generated/wordpress_publisher.py"
    try:
        result = subprocess.run(["python3", publisher_script, target_file], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
            
        if "✅ Successfully published to WordPress!" in result.stdout:
            # Clean up the file from queue since it's published
            os.remove(target_file)
            return True
        else:
            return False
    except Exception as e:
        print(f"WordPress publisher failed: {e}")
        return False

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
    
    target_file = None
    for fpath in queued_files:
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(1000).lower()
        
        # Determine if it's a garbage or purely system update post
        is_garbage = False
        if 'title: "toai agent report"' in content or 'title: "toai system update' in content or 'title: "toai system dashboard' in content:
            is_garbage = True
        elif '# toai agent report' in content or '# toai system update' in content or '# toai system dashboard' in content:
            is_garbage = True
            
        if is_garbage:
            print(f"[{datetime.datetime.now().isoformat()}] Garbage/System post detected. Moving to premium_logs: {os.path.basename(fpath)}")
            premium_dir = "/home/phenox/gemini-sandbox/TOAI_Generated/premium_logs"
            os.makedirs(premium_dir, exist_ok=True)
            shutil.move(fpath, os.path.join(premium_dir, os.path.basename(fpath)))
        else:
            target_file = fpath
            break
            
    if not target_file:
        print(f"[{datetime.datetime.now().isoformat()}] No valid articles found in queue after filtering.")
        return
        
    filename = os.path.basename(target_file)
    
    # 1:1 Round Robin based on current count
    # Even count -> Zenn, Odd count -> WordPress
    success = False
    if count % 2 == 0:
        success = push_to_zenn(target_file, filename)
    else:
        success = push_to_wordpress(target_file, filename)
        
    if success:
        # Increment counter on success
        with open(COUNT_FILE, "w") as f:
            f.write(f"{today},{count + 1}")
    else:
        # 失敗時にもカウンターを進めないと、ZennかWPのどちらかでエラー起きた際に
        # 永遠にもう片方に処理が回らない無限ブロック状態になるため、カウンターを進める
        with open(COUNT_FILE, "w") as f:
            f.write(f"{today},{count + 1}")
        print(f"[{datetime.datetime.now().isoformat()}] Publish failed, but incremented count to avoid blocking the other platform.")

if __name__ == "__main__":
    process_queue()
