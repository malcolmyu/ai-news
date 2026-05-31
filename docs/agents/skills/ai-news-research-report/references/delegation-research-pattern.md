# Parallel Delegation Pattern for Research Reports

## When to use

When generating a deep research report that requires:
- Architecture diagram generation (SVG)
- Multi-source research (GitHub repo, official docs, third-party articles)
- Template-based HTML synthesis

## Pattern

Delegate the heavy lifting to Flash workers in parallel, then synthesize with Pro:

```
Pro (Planner)
  ├── delegate_task #1 (Flash) → SVG architecture diagram
  │     task: "Follow architecture-diagram skill, generate dark SVG..."
  │     toolsets: [file, terminal, web]
  │
  ├── delegate_task #2 (Flash) → research GitHub + docs
  │     task: "Clone repo, crawl docs, extract modules/patterns/features"
  │     toolsets: [file, terminal, web]
  │
  └── Pro synthesizes both outputs + template CSS → write final HTML
```

## Key parameters for Flash workers

- `model`: `deepseek-v4-flash` (or equivalent cheap model)
- `toolsets`: `["file", "terminal", "web"]` — minimal, just what's needed
- `max_iterations`: 50 — enough for multi-step research
- Flash workers should return minimal summary + output file path

## Why this works

- Flash is 10x cheaper than Pro per token
- Research + diagram tasks are execution-heavy, not reasoning-heavy
- Parallelism cuts total time from ~30min to ~17min
- Pro only burns tokens on synthesis (highest-value cognitive work)

## Pitfalls

1. **Don't delegate the HTML writing** — Flash may hallucinate links, miss style consistency. Pro writes the final file.
2. **Read both Flash outputs before synthesizing** — Don't trust they're perfect. Verify file integrity first.
3. **Use tempfile + shutil.copy for HTML writing** — Same as Phase 9 in skill, avoids truncation.
4. **Clean up Flash temp files after synthesis** — rm the JSON and diagram HTML files.

## Example: Hermes Agent architecture report

| Role | Model | Task | Time |
|------|-------|------|------|
| Pro | deepseek-v4-pro | Read template, structure, synthesize | 2 min |
| Flash #1 | deepseek-v4-flash | SVG 5-layer architecture diagram (502 lines) | 9 min |
| Flash #2 | deepseek-v4-flash | GitHub clone + docs crawl + 31 modules extracted | 8 min |
| Pro | deepseek-v4-pro | Merge outputs → 941-line bento HTML → verify → push | 3 min |
| **Total** | | | **~22 min** |

## Embedding dark diagrams in light pages

When the architecture-diagram skill produces a dark-themed SVG, embed it in a light bento page inside a dark-background wrapper:

```html
<div class="diagram-wrap" style="background:#020617;border-radius:12px;padding:12px;margin-top:10px;overflow-x:auto;">
  <svg>...</svg>
</div>
```

This creates a striking contrast element without breaking the light page aesthetic. The dark diagram's JetBrains Mono font triggers a style-check warning ("non-Inter web font") — this is acceptable and intentional.
