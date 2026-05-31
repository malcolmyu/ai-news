# MobileGym — Mobile GUI Agent Benchmark

**Source:** 2026-05-29 session research
**URL:** https://github.com/Purewhiter/mobilegym | https://arxiv.org/abs/2605.26114 | https://mobilegym.dev

## Overview

MobileGym is a browser-hosted mobile simulation platform with fully programmable state. Ships 28 simulated apps, 416 task templates with deterministic sub-millisecond judges, runs 256 parallel instances on one server (~400MB RAM per instance, ~3s cold-start).

## Key Features

- **Fully programmable state** — Entire environment as structured JSON snapshot. Capture, configure, diff, restore.
- **Deterministic judges** — Every task has a programmatic check function. No VLM judging required (real-device VLM judges have 10.2% misjudgment rate).
- **Full-environment state comparison** — Detects unexpected side effects (accidentally-followed user, inadvertently-sent message) that real-device pipelines cannot see.
- **Lightweight** — 400MB RAM + 50MB disk per instance. 256 parallel on single server.
- **Sim-to-Real validated** — 95.1% of simulation-side training gain transfers to real Redmi Note 12 Turbo. Qwen3-VL-4B + GRPO: +42.8pt in sim, +40.7pt on real device.

## Task Levels

| Level | Count | Description | Best Model SR |
|-------|-------|-------------|---------------|
| L1 | 20 | Single-step | Gemini 97.5% |
| L2 | 73 | Multi-step / single app | Gemini 83.6% |
| L3 | 83 | Complex multi-screen / state-dependent | Gemini 63.3% |
| L4 | 80 | Cross-app workflows | Gemini **21.9%** |

## App Catalog

- Social: WeChat, RedNote, X, Reddit
- Finance: Alipay, eBay
- Media: Bilibili, Spotify, WeChat Reading
- Travel: 12306, Maps, Tencent Meeting
- System: Launcher, Settings, Contacts, SMS, Notes, Calendar, Clock, Calculator, Files, Gallery, Browser, Compass, AnswerSheet, ThemeStore

## Leaderboard Highlights

| Model | Success Rate |
|-------|-------------|
| Gemini 3.1 Pro | 58.8% |
| Doubao-Seed-2.0-Pro | 52.0% |
| Qwen3.6-Plus | 45.7% |
| AutoGLM-Phone-9B | 20.0% |
| Qwen3-VL-4B + GRPO | 22.2% (from 9.4%) |

## Relevance to Harness

MobileGym's architecture maps directly to Harness mobile agent development:
- **Programmable state** → Verifiable agent execution results in Harness
- **FSM-based navigation** → Declarative task planning for mobile agents
- **AnswerSheet protocol** → Structured output format design for agent skills
- **Lightweight sandbox** → Parallel batch testing of long-running agent tasks
- **L4 (cross-app) remains unsolved** (Gemini 21.9%) — exactly the problem Harness targets
