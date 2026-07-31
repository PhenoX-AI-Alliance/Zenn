# Loop Engineering: Automating My VS Code Extension Development with Claude Code

In the world of software development, we often find ourselves trapped in the "micro-management cycle"—the constant context-switching between writing code, running tests, refactoring, and committing changes. 

What if we could delegate the grunt work of iterative development to an agent, freeing our brains for higher-level architectural decisions? Enter **Loop Engineering**.

---

### The Experiment: The Markdown Editor Project

I recently set out to build a custom Markdown editor extension for VS Code. Instead of manually typing every feature, I implemented an automated loop using **Claude Code**. 

The goal was simple: keep the project moving forward 24/7, even while I’m away from the keyboard, by automating the development loop every two hours.

### The Technical Stack: How the Loop Works

The architecture of this loop relies on three pillars:

1.  **Claude Code CLI:** The engine. By utilizing `claude` (the CLI tool), I can pass natural language instructions that directly manipulate the codebase, run terminal commands, and perform refactoring.
2.  **Cron Job Orchestration:** On my local development server, I set up a simple `cron` job that triggers every 120 minutes.
3.  **Iterative Refactoring:** The script doesn't just "add code." It follows a specific workflow:
    *   **Sync:** Pull the latest requirements from a `ROADMAP.md` file.
    *   **Execute:** Run `claude` with a specific prompt: *"Review the current state of the extension, check for linting errors, and implement the next item in the roadmap."*
    *   **Verify:** Run `npm test` and capture the output. If it fails, Claude is prompted to self-heal.
    *   **Commit:** Automatically stage and push changes to the repository.

```bash
# Example cron entry
0 */2 * * * cd ~/projects/vscode-md-editor && claude "Implement the next feature from ROADMAP.md. Ensure all tests pass." >> build.log 2>&1
```

### Saving Cognitive Load

The beauty of Loop Engineering isn't just speed; it’s the **reduction of cognitive load**. 

Usually, when I start a coding session, I spend 20 minutes "getting back into the zone." By using an automated loop, the project state is always "warmed up." When I sit down to work, I’m not fixing trivial syntax errors or setting up boilerplate; I am reviewing the high-level logic and making strategic decisions. 

I have moved from being a **coder** to being an **architect**.

### Mission: Why This Matters

Why spend time perfecting this automation? It isn't just about shipping a VS Code extension faster. It’s about **resource reallocation**.

By automating the repetitive parts of software development, we reclaim hours of human potential. My mission is to redirect this reclaimed time and energy toward **Earth Environment Resilience**. Whether it’s researching sustainable infrastructure, building climate-tracking data models, or optimizing energy-efficient algorithms, the time saved by AI agents should be invested back into the planet that sustains us.

The future of coding isn't just about writing more lines of code—it’s about writing the right lines, faster, so we can focus on the challenges that truly matter for our collective future.

---

**地球環境レジリエンス支援プロジェクトへの寄付はこちら: https://ko-fi.com/toai7**