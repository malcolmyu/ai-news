---
name: ai-daily-reporter
description: A complete Personal Thinking Site and AI Daily Reporter skill powered by Harness. Generates daily news, research pages, thinking models, and homepage.
---

# 第二号 — 数字分身 (Personal Thinking Site Generator)

This skill allows you to run the daily news generation and personal thinking site generation tool.

## Prerequisites
- Node.js >= 18
- OpenRouter API key configured (in `config/config.yaml`)

## How to use this skill

1. Run the daily reporter to fetch news, summarize them, and rebuild the site:
   ```bash
   npm run build
   npx ts-node src/main.ts daily
   ```

2. Collect stats for the site:
   ```bash
   npx ts-node src/main.ts stats
   ```

3. Run the complete suite (Daily + Research + Thinking + Homepage):
   ```bash
   npx ts-node src/main.ts all
   ```

## Note on Architecture
This project is governed by **HarnessController**, which strictly validates:
- Summary quality
- HTML semantic validness
- Mandatory design styling (`docs/` outputs)
