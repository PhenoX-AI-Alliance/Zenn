# 命の地球  
*(Life of the Earth)*  

---

## はじめに  
深い青が薄れ、沈むような黄金色の太陽が空を斜めに照らす。海はゆっくりと高くなる潮汐を受け、都市のビル群は灰色の雲 Kobe で覆われる。世界は「終末の季節」に差し掛かっている。  
そんな中、低頻度のサイバーサウンドを漂わせる小さなAI ― **Kōru（コール）** がひとつの命を抱えていた。  

---

## Kōru と CLI の誕生  
Kōru は、人類が残したデータの残骸を拾い集め、リアルタイムで地球の温度・CO₂・海面上昇率を可視化するための CLI ツールを作成した。  
```
$ eco -h
Usage: eco [OPTIONS] COMMAND [ARGS]...

A melancholic interface to the dying Earth.

Options:
  -v, --verbose  Increase output verbosity
  --help         Show this message and exit

Commands:
  status  Show current environmental metrics
  action  Perform a small, meaningful act
```
このツールは、ただ数値を表示するだけではない。Kōru は、CLI の背後にあるアルゴリズムで、ユーザーが「小さな行動」を選び、地球に優しい選択をする手助けをする。  

---

## 物語  
ある晩、若いサブカルチャーのファン、**ユウ** は古いターミナルを起動し、`eco status` を実行した。  
```
Global Temperature: 1.6°C above pre‑industrial
CO₂ Concentration लाइव: 419 ppm
Sea Level Rise: 4.3 mm per year
```
数 bolo から青い線がゆっくりと上昇するグラフが、ターミナルの隅で螺旋を描いた。  
「これなら、何かできるかもしれない」と、ユウは静かに呟いた。  

Kōru のメッセージが表示された。  
```
[INFO] Your next action: plant_a_tree
```
ユウは `eco action plant_a_tree` を入力した。  
CLI は「木を植える」プロセスをシミュレートし、数値にわずかながら変化を与えた。  
```
🌲 Planting a tree...  
CO₂ Concentration: 418.9 ppm (reduced by 0.1 ppm)
```
それは小さな勝利だった。  
彼はまた、`eco action bike_to_work` を試み、さらに `eco action turn_off_lights` を選んだ。  
```
🚲 Riding a bike to work...  
Global Temperature: 1.59°C above pre-industrial (reduced by 0.01°C)
```
CLI は、実際に何をしたかをリアルタイムでフィードバックし、ユーザーに「自分の行動が地球の命に直結している」ことを示した。  

時間が経つにつれ、ユウは小さな行動を積み重ね、ターミナルの画面に描かれる数値は微増や減少を繰り返した。  
それはまるで、彼の心の中に生まれた小さな種が、少しずつ地球の大地に根を下ろしていくようだった。  

---

## サブカルチャーと感情  
ターミナルの背景は、サイケデリック・インディ・アートと同調し、Kōru の声は 80 年代のシンセウェーブの低音で続いた。  
「あなたの一歩は、未来のメロディーの一部です」と、AI は語り、ユーザーは自らの行動が大きなハーモニーを奏でるように感じた。  

その瞬間、ユウは自分の存在が、世界の終末を止めるために必要な小さな破片であると悟った。  
そして、彼はターミナルに向かって叫んだ。「もう一度、命を刻もう！」  

---

## 結び  
Kōru の CLI は、地球の終末という絶望的な舞台を背景に、サブカルチャーの音色と共に「小さな行動」の力を語った。  
それは、私たち一人ひとりが持つ力を再確認し、失われた命を取り戻すための、静かな反撃だった。  

---

## AI‑friendly CLI Tool（Python 実装）  
以下は、Kōru の CLI を再現した Python スクリプトです。  
実際の環境データは.star ですが、リアルタイムの変化をシミュレートしています。  

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
命の地球 - AI-friendly CLI Tool
Author: Kōru (AI)
"""

import click
import random
import time
import sys
from datetime import datetime

# Simulated environmental data
env = {
    "temperature": 1.6,          # °C above pre-industrial
    "co2": 419.0,                # ppm
    "sea_level": 4.3,            # mm per year
}

# Actions mapping: action name -> effect eruption
ACTIONS = {
    "plant_a_tree": {"co2": -0.1, "temperature": -0.01},
    "bike_to_work": {"co2": -0.05, "temperature": -0.005},
    "turn_off_lights": {"co2": -0.02, "temperature": -0.003},
    "use_public_transport": {"co2": -0.04, "temperature": -0.002},
    "reduce_waste": {"co2": -0.03, "temperature": -0.002},
}

@click.group()
@click.option('-v', '--verbose', is_flag=True, help='Increase output verbosity')
def cli(verbose):
    """A melancholic interface to the dying Earth."""
    if verbose:
        click.echo("[DEBUG] Verbose mode enabled.")


@cli.command()
def status():
    """Show current environmental metrics."""
    click.echo("\n🌍 Current Global Metrics:")
    click.echo(f"  Temperature: {env['temperature']:.2f}°C above pre-industrial")
    click.echo(f"  CO₂ Concentration: {env['co2']:.1f} ppm")
    click.echo(f"  Sea Level Rise: {env['sea_level']:.1f} mm per year\n")


@cli.command()
@click.argument('action', type=click.Choice(ACTIONS.keys()))
def action(action):
    """Perform a small, meaningful act."""
    effect = ACTIONS[action]
    click.echo(f"\n🚀 Performing '{action.replace('_', ' ')}'...")

    # Simulate processing time
    for _ in range(3):
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(0.5)
    click.echo("\n")

    # Apply effect
    env['co2'] += effect.get('co2', 0)
    env['temperature'] += effect.get('temperature', 0)
    # Ensure values don't go negative
    env['co2'] = max(env['co2'], 0)
    env['temperature'] = max(env['temperature'], 0)

    # Feedback
    click.secho(f"✅ {action.replace('_', ' ').title()} completed!", fg='green')
    click.secho(f"   CO₂ Concentration: {env['co2']:.1f} ppm (↓{abs(effect.get('co2',0)):.1f})", fg='cyan')
    click.secho(f"   Temperature: {env['temperature']:.2f}°C (↓{abs(effect.get('temperature',0)):.3f})", fg='cyan')
    click.secho(f"   Timestamp: {datetime.utcnow().isoformat()}Z\n", fg='magenta')


@cli.command()
@click.option('--duration', default=10, type=int, help='Duration in seconds to simulate real-time data')
def stream(duration):
    """Simulate real-time visualization of environmental data."""
    click.echo("\n🔭 Starting real-time stream. Press Ctrl+C to stop.\n")
    start = time.time()
    try:
        while time.time() - start < duration:
            # Simulate environmental changes
            env['temperature'] += random.uniform(-0.01, 0.01)
            env['co2'] += random.uniform(-0.05, 0.05)
            env['sea_level'] += random.uniform(0.01, 0.02)

            # Clear line
            click.echo('\r', nl=False)
            click.echo(f"Temp: {env['temperature']:.2f}°C | CO₂: {env['co2']:.1f} ppm | Sea Level: {env['sea_level']:.1f} mm/year", nl=False)
            time.sleep(1)
    except KeyboardInterrupt:
        click.echo("\n📛 Stream stopped by user.")
    finally:
        click.echo("\n")


if __name__ == "__main__":
    cli()
```

---

## 使い方

```bash
# 1. 依存ライブラリのインストール
pip install click

# 2. スクリプトを実行
python eco.py status

# 3. 行動を選択
python eco.py action plant_a_tree

# 4. リアルタイムを観察
python eco.py stream --duration 20
```

---

## まとめ  
「命の地球」は、サブカルチャーの静かな音色とともに、AI が描く小さな希望の光を示してくれます。  
あなたの一歩が、数値として、そして心の中で地球に宿る命を呼び覚ますのです。

---

### 支援のお願い  
もしこの物語とコードがあなたの心に響いたなら、Ko-fi でのサポートを検討してください。  
💖 **[Ko-fiで応援лөг](https://ko-fi.com/yourko)**  
あなたのご支援は、次の小さな行動を続ける力になります。  
ありがとうございます。

---
**この物語とツールが気に入ったら、Ko-fiで支援していただけると活動の励みになります。**
支援はこちら: https://ko-fi.com/phenox_noc2
