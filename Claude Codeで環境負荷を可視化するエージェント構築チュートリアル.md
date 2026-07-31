# Building a Sustainable AI Monitor: Tracking Environmental Impact with Claude Code and Herdr

As AI development accelerates, the carbon footprint of compute-intensive tasks has become a critical concern for developers. Integrating environmental monitoring into your development workflow is no longer just "nice-to-have"—it is a core component of sustainable engineering.

In this tutorial, we will build a Python-based agent that monitors real-time power consumption and CO2 emissions using the `herdr` API, orchestrated through the `claude-code` CLI.

---

## 1. Why Monitor Environmental Impact?

Local LLM agents and large-scale model training consume significant electricity. By tracking the power metrics of our development environment, we can:
*   **Identify energy-intensive code paths:** Optimize algorithms that cause power spikes.
*   **Optimize scheduling:** Run heavy workloads during hours when the local grid is powered by renewable energy.
*   **Promote Accountability:** Quantify the "carbon cost" of each feature built.

## 2. Integration: Herdr API and Claude Code

`herdr` provides a streamlined API for tracking power consumption metrics, while `claude-code` allows us to interact with our codebase using natural language to automate the deployment of these monitors.

### Prerequisites
1.  **Claude Code:** Installed via `npm install -g @anthropic-ai/claude-code`
2.  **Herdr API Key:** Obtain from your [Herdr dashboard](https://herdr.dev).

### CLI Command to Initialize the Agent
You can use `claude-code` to scaffold your monitoring agent:
```bash
claude "Create a python script that fetches power metrics from the herdr API and logs them to a local JSON file every 60 seconds."
```

## 3. Practical Implementation Logic

Below is a Python script that acts as the monitoring agent. It queries the `herdr` API and calculates the estimated CO2 impact based on the current energy mix.

```python
import requests
import time
import json

HERDR_API_URL = "https://api.herdr.dev/v1/metrics"
API_KEY = "your_herdr_api_key_here"

def log_environmental_impact():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    try:
        response = requests.get(HERDR_API_URL, headers=headers)
        data = response.json()
        
        # Calculate impact
        power_watts = data.get("power_consumption_w")
        co2_g = power_watts * 0.0004  # Example grid intensity factor
        
        log_entry = {
            "timestamp": time.time(),
            "power_w": power_watts,
            "co2_g": co2_g
        }
        
        with open("impact_log.json", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
            
        print(f"Logged: {power_watts}W | Estimated CO2: {co2_g:.4f}g")
        
    except Exception as e:
        print(f"Error fetching metrics: {e}")

if __name__ == "__main__":
    while True:
        log_environmental_impact()
        time.sleep(60)
```

## 4. Conclusion: Towards Sustainable AI

Building a monitor is the first step toward conscious computing. By integrating `herdr` into your CI/CD pipeline and using `claude-code` to refactor energy-hungry functions, you can significantly reduce the ecological footprint of your projects. Sustainable AI is not just about efficient hardware; it is about the visibility we bring to our development processes.

地球環境レジリエンスへの貢献（月額支援）: https://buy.stripe.com/example_payment_link