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
PYTHON_BIN="${PYTHON_BIN:-}"
if [ -z "$PYTHON_BIN" ]; then
  if [ -x "$REPO/scripts/python.sh" ]; then
    PYTHON_BIN="$("$REPO/scripts/python.sh" --print)"
  else
    PYTHON_BIN="${PYTHON:-python3}"
  fi
fi
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

# Check for read_file line number pollution in <style> blocks
# Browsers fail to parse CSS when selectors are prefixed like "15|.callout"
for f in docs/*.html docs/research/*.html docs/daily/*.html; do
  [ -f "$f" ] || continue
  # Extract <style> block and check for line number patterns
  if "$PYTHON_BIN" -c "
import re, sys
with open('$f') as fh:
    html = fh.read()
m = re.search(r'<style>(.*?)</style>', html, re.DOTALL)
if m and re.search(r'\\d+\\|\\.', m.group(1)):
    sys.exit(1)
" 2>/dev/null; then
    true  # clean
  else
    # Check if this file even has a <style> block
    if grep -q '<style>' "$f" 2>/dev/null; then
      red "  ✗ $f: <style> block contains line number prefixes — CSS will not parse!"
      ERRORS=$((ERRORS + 1))
    fi
  fi
done
check "No read_file line numbers in CSS blocks"

println

# ── Part 0.55: Image Path Sanity — catch docs/daily/ prefix in src ─────
bold "【Image Path Sanity】"

IMG_PATH_ISSUES=0
for f in docs/daily/*.html; do
  [ -f "$f" ] || continue
  # Catch docs/daily/ prefix: GitHub Pages serves from docs/, so
  # src="docs/daily/assets/..." resolves to /daily/docs/daily/assets/...
  # Correct form is src="assets/..." (page-relative)
  count=$(grep -c 'src="docs/daily/assets/' "$f" 2>/dev/null || true)
  if [ "$count" -gt 0 ]; then
    red "  ✗ $f — $count img src with 'docs/daily/' prefix (should be 'assets/…')"
    IMG_PATH_ISSUES=$((IMG_PATH_ISSUES + 1))
  fi
  # Catch pbs.twimg.com avatar URLs in tweet-avatar (cross-origin blocked)
  pbs_count=$(grep -c 'tweet-avatar.*pbs\.twimg\.com' "$f" 2>/dev/null || true)
  if [ "$pbs_count" -gt 0 ]; then
    red "  ✗ $f — $pbs_count tweet-avatar with pbs.twimg.com URL (must be local or unavatar.io)"
    IMG_PATH_ISSUES=$((IMG_PATH_ISSUES + 1))
  fi
done
[ "$IMG_PATH_ISSUES" -eq 0 ]
check "All daily HTML image paths are correct (no docs/daily/ prefix, no pbs.twimg.com)"

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

  grep -q '#fff.*card\|--bg-card.*#fff' docs/styles.css 2>/dev/null
  check "Card background #fff (via --bg-card)"

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

    # 2b. Geist + Inter font check (both required for research reports)
    if grep -q 'family=Geist:wght@400;500;600&family=Inter:wght@300;400;500;600' "$REPORT" 2>/dev/null; then
      green "    ✓ Geist + Inter fonts loaded"
    else
      warn "$BASENAME: missing Geist+Inter font (standard is family=Geist:wght@400;500;600&family=Inter:wght@300;400;500;600)"
    fi

    # Extra web fonts beyond Geist+Inter
    FONT_COUNT=$(grep -c 'fonts.googleapis.com/css2?family=' "$REPORT" 2>/dev/null || echo 0)
    if [ "$FONT_COUNT" -gt 1 ]; then
      warn "$BASENAME imports multiple font links ($FONT_COUNT) — should only import Geist+Inter in one link"
    fi

    if grep -q 'JetBrains\|Noto\|Roboto\|Source Sans\|IBM Plex' "$REPORT" 2>/dev/null; then
      warn "$BASENAME uses non-standard web font"
    fi

    # 2c. Unified header navigation (replaced nav-back)
    if grep -q 'data-pagefind-ignore' "$REPORT" 2>/dev/null; then
      :
    else
      warn "$BASENAME has no unified header (data-pagefind-ignore)"
    fi

    # 2d. Shared stylesheet ensures correct palette & border-radius
    if grep -q 'styles.css' "$REPORT" 2>/dev/null; then
      green "    \xE2\x9C\x93 Uses shared styles.css"
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

    # 2e. Standard footer — must contain the site-wide footer
    if grep -q '把自己产品化.*持续进化中' "$REPORT" 2>/dev/null; then
      green "    ✓ Standard footer present"
    else
      warn "$BASENAME: missing standard footer — should be: 🤖 <strong>第二号</strong> — 把自己产品化 — 持续进化中"
    fi

    printf "\n"
  done
fi

println

# ── Part 3: Structured content rules ───────────────────────────────
bold "【Structured Content Rules】"
green "  ✓ Daily/research section contracts are delegated to scripts/site_harness.py"
println
# ── Part 4: Link Integrity ────────────────────────────────────────
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

# ── Part 7: Structured Site Harness ─────────────────────────────────
bold "【Structured Site Harness】"

if "$PYTHON_BIN" scripts/site_harness.py validate; then
  green "  \xE2\x9C\x93 Content index, archives, and generated sections are consistent"
else
  red "  \xE2\x9C\x97 Structured site harness validation failed"
  ERRORS=$((ERRORS + 1))
fi

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
