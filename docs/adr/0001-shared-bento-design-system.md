# 001 — Shared Bento Design System with CSS Custom Properties

Context: 34 HTML files each carried their own inline `<style>` block duplicating the same bento design tokens (accent `#5e6ad2`, background `#f5f5f4`, border-radius 14px, Inter font). Two visual schemes coexisted — bento (22 files) and an older blue scheme (`#3b82f6`, 19 files). The `style-check.sh` pre-deployment check enforced a "no CSS :root variables" convention for research reports, because consistency relied on copy-pasted hardcoded values.

Decision: Extract all shared design tokens and component classes into a single `docs/styles.css` using CSS custom properties (`:root { --accent, --bg-primary, --border, --radius-lg, … }`). All HTML files link to this stylesheet. The older blue scheme (thinking/ pages, deleted homepage.html) is retired in favor of bento. The style-check.sh now validates design tokens in `styles.css` and verifies each report links to it, rather than grepping for hardcoded hex values per file.

Why: A shared stylesheet turns the design system into a deep module — a small interface (~80 class names + ~15 tokens) with high leverage (34 callers). Changing the accent color is now a one-line edit, not a 22-file search-and-replace. CSS custom properties were chosen over hardcoded values despite the old convention because in a truly shared stylesheet, the variables are the design system — they provide a single source of truth, readable names, and a path to dark-mode theming.

Considered alternative: Using hardcoded values throughout styles.css to preserve the "no variables" convention. Rejected because that convention was a workaround for the inline-styles-per-file world; variables in a shared file serve a different purpose and are worth the precedent change.

Consequences:
- `docs/styles.css` is now the design system seam; any page that links to it inherits bento styling automatically
- Thinking model pages (cognition, communication, decision, product) lost their distinct blue identity — now unified under bento
- Standalone dark-theme presentation pages (`docs/20260510-thariq-html.html`, `docs/20260512-guizang-ppt.html`) keep their own inline styles — they are not part of the bento content system
- `style-check.sh` `:root` check is relaxed to allow the shared stylesheet; per-report check now validates the link rather than hex values
