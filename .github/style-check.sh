#!/usr/bin/env bash
#===============================================================================
# ai-news Style & Integrity Check
# Runs before deployment to catch common issues.
# Usage:
#   bash ai-news-style-check.sh <path-to-ai-news-repo>
#   exit 0 = all checks passed, exit 1 = issues found
#===============================================================================

set -o pipefail

REPO="${1:-$PWD}"
ERRORS=0
WARNINGS=0

red()   { printf '\033[31m%s\033[0m\n' "$1"; }
green() { printf '\033[32m%s\033[0m\n' "$1"; }
yellow(){ printf '\033[33m%s\033[0m\n' "$1"; }
bold()  { printf '\033[1m%s\033[0m\n' "$1"; }

check() {
  if [ $? -eq 0 ]; then
    green "  \xE2\x9C\x93 $1"
  else
    red "  \xE2\x9C\x97 $1"
    ERRORS=$((ERRORS + 1))
  fi
}

warn() {
  yellow "  \xE2\x9A\xA0 $1"
  WARNINGS=$((WARNINGS + 1))
}

println() { printf "\n"; }

cd "$REPO" || { red "ERROR: Cannot cd to $REPO"; exit 1; }
bold "═══════════════════════════════════════════"
bold "  ai-news Style & Integrity Check"
bold "  Repo: $(basename "$REPO")"
bold "═══════════════════════════════════════════"
println

# ── Part 0: File Integrity ─────────────────────────────────────────
bold "【File Integrity】"

# Check for truncation (files containing literal "[truncated]")
for f in docs/index.html docs/research/archive.html docs/research/*.html; do
  [ -f "$f" ] || continue
  if grep -q '\[truncated\]' "$f" 2>/dev/null; then
    red "  \xE2\x9C\x97 $f contains '[truncated]' — file was truncated during write!"
    ERRORS=$((ERRORS + 1))
  fi
done

# All HTML files must end with </html>
for f in docs/*.html docs/research/*.html docs/daily/*.html; do
  [ -f "$f" ] || continue
  if ! tail -c 10 "$f" | grep -q '</html>'; then
    red "  \xE2\x9C\x97 $f does not end with </html> — incomplete file!"
    ERRORS=$((ERRORS + 1))
  fi
done
check "All HTML files are complete (no truncation)"

println

# ── Part 0.5: Shared Stylesheet Integrity ─────────────────────────────
bold "【Design System (docs/styles.css)】"

if [ -f docs/styles.css ]; then
  # Verify key design tokens are present
  grep -q '#2563eb' docs/styles.css 2>/dev/null
  check "Accent color #2563eb defined"

  grep -q '#f5f5f4' docs/styles.css 2>/dev/null
  check "Background color #f5f5f4 defined"

  grep -q '#1c1c1c' docs/styles.css 2>/dev/null
  check "Text primary #1c1c1c defined"

  grep -q '#e8e8e6' docs/styles.css 2>/dev/null
  check "Border color #e8e8e6 defined"

  grep -q 'border-radius.*14px' docs/styles.css 2>/dev/null
  check "Card border-radius 14px defined"

  grep -q 'font-family.*Inter' docs/styles.css 2>/dev/null
  check "Inter font family set"
else
  red "  \xE2\x9C\x97 docs/styles.css not found!"
  ERRORS=$((ERRORS + 1))
fi

println

# ── Part 1: Homepage ───────────────────────────────────────────────
bold "【Homepage (docs/index.html)】"

[ -f docs/index.html ] || { red "  \xE2\x9C\x97 docs/index.html not found"; ERRORS=$((ERRORS+1)); }

# Must have both daily and research sections
grep -q 'id="daily"' docs/index.html 2>/dev/null
check "Homepage has Daily section"

grep -q 'id="research"' docs/index.html 2>/dev/null
check "Homepage has Research section"

# Must have footer
grep -q '</footer>' docs/index.html 2>/dev/null
check "Homepage has footer"

# No <span> wrapping <link> in <head>
if grep -q '<span><link' docs/index.html 2>/dev/null; then
  red "  \xE2\x9C\x97 Homepage has <span> wrapping <link> — invalid HTML!"
  ERRORS=$((ERRORS + 1))
else
  green "  \xE2\x9C\x93 No <span> wrapping <link>"
fi

# No stats check needed (removed intentionally)

println

# ── Part 2: Research Reports Style Consistency ─────────────────────
bold "【Research Reports Style (vs managed-agents.html reference)】"

REFERENCE="docs/research/managed-agents.html"
if [ ! -f "$REFERENCE" ]; then
  yellow "  \xE2\x9A\xA0 Reference report $REFERENCE not found, skipping style comparison"
  println
else
  for REPORT in docs/research/*.html; do
    BASENAME=$(basename "$REPORT")
    [ "$BASENAME" = "archive.html" ] && continue
    [ "$BASENAME" = "managed-agents.html" ] && continue

    printf "  Checking: %s\n" "$BASENAME"

    # 2a. CSS Variables — design tokens belong in shared styles.css
    if grep -q ':root' "$REPORT" 2>/dev/null; then
      warn "$BASENAME uses :root CSS variables — use shared styles.css instead"
    else
      green "    \xE2\x9C\x93 No local :root (using shared styles.css)"
    fi

    # 2b. Extra web fonts (only Inter allowed)
    FONT_COUNT=$(grep -c 'fonts.googleapis.com' "$REPORT" 2>/dev/null || echo 0)
    if [ "$FONT_COUNT" -gt 1 ]; then
      warn "$BASENAME imports multiple fonts ($FONT_COUNT) — should only import Inter"
    fi

    if grep -q 'JetBrains\|Noto\|Roboto\|Source Sans\|IBM Plex' "$REPORT" 2>/dev/null; then
      warn "$BASENAME uses non-Inter web font"
    fi

    # 2c. Unified header navigation (replaced nav-back)
    if grep -q 'data-pagefind-ignore' "$REPORT" 2>/dev/null; then
      :
    else
      warn "$BASENAME has no unified header (data-pagefind-ignore)"
    fi

    # 2d. Shared stylesheet ensures correct palette & border-radius
    if grep -q 'styles.css' "$REPORT" 2>/dev/null; then
      green "    â Uses shared styles.css"
    else
      # Legacy: hardcoded value checks for files without shared stylesheet
      if grep -q '#f5f5f4' "$REPORT" 2>/dev/null; then
        :
      else
        warn "$BASENAME: background color does not match #f5f5f4"
      fi
      if grep -q 'border-radius.*14px' "$REPORT" 2>/dev/null; then
        :
      else
        warn "$BASENAME: card border-radius not 14px"
      fi
    fi

    printf "\n"
  done
fi

println
# ── Part 3: Link Integrity ────────────────────────────────────────
bold "【Link Integrity】"

# Homepage should not link to .md files
MD_LINKS=$(grep -oE 'href="[^"]+\.md"' docs/index.html 2>/dev/null)
if [ -n "$MD_LINKS" ]; then
  red "  \xE2\x9C\x97 Homepage links to .md files — must use .html!"
  printf "    %s\n" "$MD_LINKS"
  ERRORS=$((ERRORS + 1))
else
  green "  \xE2\x9C\x93 No .md links on homepage"
fi

# All research reports should exist (mentioned in homepage/archive)
for report in $(grep -oE 'research/[a-zA-Z0-9_-]+\.html' docs/index.html 2>/dev/null); do
  if [ ! -f "docs/$report" ]; then
    red "  \xE2\x9C\x97 Homepage links to $report but file does not exist!"
    ERRORS=$((ERRORS + 1))
  fi
done
check "All homepage links point to existing files"

println

# ── Summary ────────────────────────────────────────────────────────
bold "═══════════════════════════════════════════"
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
  bold "  RESULT: \xF0\x9F\x94\xB5 PASS \xE2\x80\x94 All checks passed"
elif [ $ERRORS -eq 0 ] && [ $WARNINGS -gt 0 ]; then
  yellow "  RESULT: \xE2\x9A\xA0\xEF\xB8\x8F PASS with $WARNINGS warning(s)"
else
  red "  RESULT: \xE2\x9D\x8C FAIL \xE2\x80\x94 $ERRORS error(s) and $WARNINGS warning(s)"
fi
bold "═══════════════════════════════════════════"
println

exit $(( ERRORS > 0 ? 1 : 0 ))
