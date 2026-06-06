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
    FONT_COUNT=$(grep -c 'fonts.googleapis.com/css2?family=' "$REPORT" 2>/dev/null || echo 0)
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

    printf "\n"
  done
fi

println

# ── Part 3: Font Size Constraints ──────────────────────────────────
bold "【Font Size Constraints】"

# Content text (body, p, .text-body, .vitem-desc, etc.) must not exceed 13px.
# Uses Python for precise pixel value extraction from inline styles.
font_check_py() {
  "$PYTHON_BIN" -c "
import re, sys
with open('$1') as f:
    html = f.read()

issues = []
# Check inline style font-size values
for m in re.finditer(r'style=\"([^\"]*)\"', html):
    style = m.group(1)
    fs = re.search(r'font-size:\s*(\\d+)\\s*px', style)
    if fs:
        val = int(fs.group(1))
        # Allow up to 14px for headings (h1-h4) but flag >14px in non-heading context
        if val > 14:
            # Check if this is a legitimate heading override (h1-h4 are larger in shared CSS)
            # Get context: look backward for <h1, <h2, etc.
            ctx_start = max(0, m.start() - 30)
            ctx = html[ctx_start:m.start()]
            if not re.search(r'<(h[1-4]|title|stat-num|hero-)', ctx):
                issues.append(f'font-size:{val}px in non-heading context')
        if val > 16:
            # Anything >16px is definitely wrong for body text
            issues.append(f'font-size:{val}px exceeds maximum (16px)')
    # Check for font-size > 13px in <style> blocks
for m in re.finditer(r'<style>(.*?)</style>', html, re.DOTALL):
    css = m.group(1)
    for fm in re.finditer(r'font-size:\s*(\\d+)\\s*px', css):
        val = int(fm.group(1))
        # In CSS, flag selectors with font-size > 15px for non-heading elements
        if val > 15:
            # Get the CSS rule context (100 chars before)
            rule_start = max(0, fm.start() - 100)
            rule_ctx = css[rule_start:fm.end()]
            # Skip heading selectors and known large elements
            if not re.search(r'(h[1-4]|stat-num|\\.hero-|nav-|\\.search-)', rule_ctx):
                issues.append(f'CSS font-size:{val}px in non-heading rule')

if issues:
    for i in issues[:5]:
        print(f'    ISSUE: {i}')
    sys.exit(1)
" 2>/dev/null
}

for f in docs/daily/*.html docs/research/*.html; do
  [ -f "$f" ] || continue
  bn=$(basename "$f")
  if font_check_py "$f"; then
    green "  ✓ $bn — font sizes within limits"
  else
    red "  ✗ $bn — font-size exceeds max (body text ≤13px, headings ≤32px)"
    ERRORS=$((ERRORS + 1))
  fi
done

println

# ── Part 3.5: YouTube Embed Check ──────────────────────────────────
bold "【YouTube Embed Check — 深度对话】"

for f in docs/daily/*.html; do
  [ -f "$f" ] || continue
  bn=$(basename "$f")
  if grep -q '深度对话' "$f" 2>/dev/null; then
    # Extract all YouTube URLs from the file
    ALL_YT=$(grep -oE 'https?://(www\.)?(youtube\.com/[^"[:space:]]+|youtu\.be/[a-zA-Z0-9_-]+)' "$f" 2>/dev/null)
    if [ -n "$ALL_YT" ]; then
      # Check for channel links — these cannot be embedded
      CHANNEL_LINKS=$(echo "$ALL_YT" | grep -E 'youtube\.com/@' 2>/dev/null)
      # Check for valid video URLs
      VIDEO_LINKS=$(echo "$ALL_YT" | grep -E 'youtube\.com/watch\?v=|youtu\.be/' 2>/dev/null)

      if [ -n "$CHANNEL_LINKS" ] && [ -z "$VIDEO_LINKS" ]; then
        red "  ✗ $bn — 深度对话 links to YouTube channel (@username), not a video. No iframe embed possible."
        ERRORS=$((ERRORS + 1))
      elif [ -n "$VIDEO_LINKS" ]; then
        if grep -q '<iframe.*youtube' "$f" 2>/dev/null; then
          green "  ✓ $bn — YouTube video embedded via iframe"
        else
          red "  ✗ $bn — 深度对话 has YouTube video link but no <iframe> embed"
          ERRORS=$((ERRORS + 1))
        fi
      fi
    else
      green "  ✓ $bn — no YouTube links in 深度对话"
    fi
  fi
done

println

# ── Part 3.6: Image Content Check — 建造者动态 ─────────────────────
bold "【Image Content Check — 建造者动态】"

for f in docs/daily/*.html; do
  [ -f "$f" ] || continue
  bn=$(basename "$f")
  if grep -q '建造者动态' "$f" 2>/dev/null; then
    # Count vitem entries in builder section and those with images
    IMG_EXIT=0
    "$PYTHON_BIN" -c "
import re, sys
with open('$f') as fh:
    html = fh.read()
# Find 建造者 dynamic section
m = re.search(r'class=\"label-sm\"[^>]*>建造者动态.*?</section>', html, re.DOTALL)
if m:
    section = m.group(0)
    vitems = re.findall(r'class=\"vitem\"', section)
    vitem_galleries = re.findall(r'vitem-gallery', section)
    total = len(vitems)
    with_img = len(vitem_galleries)
    if total == 0:
        sys.exit(0)  # no items, skip
    ratio = with_img / total
    if ratio < 0.3:
        print(f'Only {with_img}/{total} builder items have images ({ratio:.0%})')
        # WARN only — many tweets are text-only with no media
        sys.exit(2)
    print(f'{with_img}/{total} builder items have images')
" 2>/dev/null
    IMG_EXIT=$?
    if [ $IMG_EXIT -eq 0 ]; then
      green "  ✓ $bn — 建造者动态 has sufficient images"
    elif [ $IMG_EXIT -eq 2 ]; then
      warn "$bn — 建造者动态 lacks images (check if source tweets had media)"
    else
      red "  ✗ $bn — 建造者动态 lacks images (need ≥30% items with vitem-gallery)"
      ERRORS=$((ERRORS + 1))
    fi
  fi
done

println

# ── Part 3.7: Image Content Check — GitHub Trending ─────────────────
bold "【Image Content Check — GitHub Trending】"

for f in docs/daily/*.html; do
  [ -f "$f" ] || continue
  bn=$(basename "$f")
  if grep -q 'GitHub Trending' "$f" 2>/dev/null; then
    if "$PYTHON_BIN" -c "
import re, sys
with open('$f') as fh:
    html = fh.read()
m = re.search(r'class=\"label-sm\"[^>]*>GitHub Trending.*?</section>', html, re.DOTALL)
if m:
    section = m.group(0)
    vitems = re.findall(r'class=\"vitem\"', section)
    vitem_galleries = re.findall(r'vitem-gallery', section)
    total = len(vitems)
    with_img = len(vitem_galleries)
    if total == 0:
        sys.exit(0)
    ratio = with_img / total
    if ratio < 0.2:
        print(f'Only {with_img}/{total} trending items have images ({ratio:.0%})')
        sys.exit(1)
    print(f'{with_img}/{total} trending items have images')
" 2>/dev/null; then
      green "  ✓ $bn — GitHub Trending has sufficient repo images"
    else
      red "  ✗ $bn — GitHub Trending lacks repo images (need ≥20% items with vitem-gallery)"
      ERRORS=$((ERRORS + 1))
    fi
  fi
done

println
# ── Part 3.8: GitHub Trending Layout Check ─────────────────────────
bold "【GitHub Trending Layout】"

for f in docs/daily/*.html; do
  [ -f "$f" ] || continue
  bn=$(basename "$f")
  if grep -q 'GitHub Trending' "$f" 2>/dev/null; then
    # GitHub Trending section must use vlist-2col layout (dual-column waterfall)
    # Check by looking for vlist-2col within the Trending card
    if "$PYTHON_BIN" -c "
import re, sys
with open('$f') as fh:
    html = fh.read()
# Find the GitHub Trending section — look for label-sm + GitHub Trending in a card
m = re.search(r'class=\"label-sm\"[^>]*>GitHub Trending.*?</section>', html, re.DOTALL)
if m:
    section = m.group(0)
    if 'vlist-2col' in section:
        sys.exit(0)
    else:
        print('GitHub Trending section does not use vlist-2col layout')
        sys.exit(1)
" 2>/dev/null; then
      green "  ✓ $bn — GitHub Trending uses vlist-2col layout"
    else
      red "  ✗ $bn — GitHub Trending must use vlist-2col (dual-column waterfall) layout"
      ERRORS=$((ERRORS + 1))
    fi
  fi
done

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

# ── Part 6: Homepage Featured Card ────────────────────────────────
bold "【Homepage Featured Card】"

FEATURED_CHECK=$(grep -c 'class="featured-card"' "$REPO/docs/index.html" 2>/dev/null || echo 0)
if [ "$FEATURED_CHECK" -ge 1 ]; then
  green "  \\xE2\\x9C\\x93 Homepage research section has featured-card"
else
  red "  \\xE2\\x9C\\x97 Homepage research section missing featured-card (first item must use class=\"featured-card\", not daily-entry)"
  ERRORS=$((ERRORS + 1))
fi

# Check for guard comments
GUARD_START=$(grep -c 'FEATURED-CARD-START' "$REPO/docs/index.html" 2>/dev/null || echo 0)
GUARD_END=$(grep -c 'FEATURED-CARD-END' "$REPO/docs/index.html" 2>/dev/null || echo 0)
if [ "$GUARD_START" -ge 1 ] && [ "$GUARD_END" -ge 1 ]; then
  green "  \\xE2\\x9C\\x93 Featured card guard comments present"
else
  yellow "  \\xE2\\x9A\\xA0 Featured card guard comments missing (should have FEATURED-CARD-START / FEATURED-CARD-END)"
  WARNINGS=$((WARNINGS + 1))
fi

println

# ── Part 6.5: Homepage Daily List — Max 3 Days ─────────────────────
bold "【Homepage Daily List (3-day limit)】"

# Count daily-entry items in daily-left (excluding daily-entry-archive)
DAILY_COUNT=$("$PYTHON_BIN" -c "
import re, sys
with open('$REPO/docs/index.html') as f:
    html = f.read()
m = re.search(r'class=\"daily-left\"[^>]*>(.*?)</div>', html, re.DOTALL)
if m:
    section = m.group(1)
    entries = re.findall(r'class=\"daily-entry[\" ](?!.*daily-entry-archive)', section)
    print(len(entries))
    sys.exit(0 if len(entries) == 3 else 1)
" 2>/dev/null)
if [ "$DAILY_COUNT" = "3" ]; then
  green "  \\xE2\\x9C\\x93 Daily list has exactly 3 entries (today + yesterday + day before)"
else
  red "  \\xE2\\x9C\\x97 Daily list has ${DAILY_COUNT:-?} entries — must have exactly 3 (today + yesterday + day before)"
  ERRORS=$((ERRORS + 1))
fi

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
