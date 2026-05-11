# GPT-Researcher Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Integrate the GPT-Researcher open-source framework via Docker (running with DuckDuckGo to avoid API key requirements) to perform deep web research when running `npm run research`, mapping the output to the `ResearchManager`.

**Architecture:**
We will create a `docker-compose.yml` to host the `gpt-researcher` backend locally. Then we'll build a `DeepResearchAgent` in Node.js that hits its REST API endpoint (`/api/research` or WebSocket), waits for the generated Markdown report, and pipes it directly into the existing `ResearchManager.addReport()` flow.

**Tech Stack:** Docker, GPT-Researcher, Typescript, Axios.

---

### Task 1: Docker Configuration

**Files:**
- Create: `docker-compose.research.yml`

**Step 1: Create the docker compose file**
Defines `gpt-researcher` service using `assafelovic/gpt-researcher` image. Expose port 8000. Inject `RETRIEVER=duckduckgo`.

### Task 2: Build the DeepResearchAgent

**Files:**
- Create: `src/agents/research-agent/index.ts`

**Step 1: Write the Axios API client**
Create `DeepResearchAgent` class with a `conductResearch(query: string)` method to POST to `http://localhost:8000/api/research` or connect via WS. Returns the markdown.

### Task 3: Hook into Main and CLI

**Files:**
- Modify: `src/main.ts`

**Step 1: Add CLI parsing for research**
Parse `args[3]` as the topic. Initialize `DeepResearchAgent`.

**Step 2: Connect to ResearchManager**
Pass the generated markdown text through a temporary file to `ResearchManager.addReport(path, "deep-research")`.

### Verification

Run: `docker-compose -f docker-compose.research.yml up -d`
Run: `npm run research "2026 LLM Trends"`
Expected: Fetches from backend and saves to docs/research.
