#!/bin/bash
#===============================================================================
# generate-daily-html.sh — Pipeline for AI Builders Daily Digest
#
# Usage:
#   bash scripts/generate-daily-html.sh 2026-05-13 digest.txt
#
# The digest file is a plain-text or markdown summary of the day's AI news.
# The script extracts all X/Twitter and YouTube URLs from it, downloads media,
# and outputs HTML snippets for embedding into the hand-crafted daily page.
#
# Steps:
#   1. Extract URLs from digest text
#   2. Fetch media (images, thumbnails) via fetch-daily-media.sh
#   3. Print HTML embed snippets for each media item
#   4. Print instructions for archive.html update
#   5. Print instructions for index.html (homepage) update
#
# Dependencies: curl, jq, grep, sed — all system default
#===============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------
DATE="${1:-}"
DIGEST_FILE="${2:-}"

if [[ -z "$DATE" || -z "$DIGEST_FILE" ]]; then
  echo "Usage: bash scripts/generate-daily-html.sh YYYY-MM-DD <digest-text-file>" >&2
  exit 1
fi

if [[ ! -f "$DIGEST_FILE" ]]; then
  echo "Error: digest file not found: $DIGEST_FILE" >&2
  exit 1
fi

# Derive paths
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="docs/daily/assets/${DATE}"
ASSETS_REL="assets/${DATE}"          # relative to docs/daily/
HTML_FILE="docs/daily/ai-news-${DATE}.html"

echo "============================================" >&2
echo "  AI Builders Daily Digest Pipeline" >&2
echo "  Date:   ${DATE}" >&2
echo "  Input:  ${DIGEST_FILE}" >&2
echo "  Media:  ${OUTPUT_DIR}" >&2
echo "============================================" >&2

# ---------------------------------------------------------------------------
# Step 1: Extract URLs from digest text
#   Matches: x.com/*/status/*, twitter.com/*/status/*, youtube.com/*, youtu.be/*
# ---------------------------------------------------------------------------
echo "" >&2
echo "--- Step 1: Extracting URLs ---" >&2

# Extract unique URLs matching our supported platforms
URLS=$(grep -oE 'https?://(x\.com|twitter\.com)/[A-Za-z0-9_]+/status/[0-9]+' "$DIGEST_FILE" || true)
URLS+=$'\n'$(grep -oE 'https?://(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[A-Za-z0-9_?=&-]+' "$DIGEST_FILE" || true)

# Deduplicate and filter empty lines
URLS=$(echo "$URLS" | grep -v '^$' | sort -u || true)

if [[ -z "$URLS" ]]; then
  echo "  No X/Twitter or YouTube URLs found in digest text." >&2
  echo "  Nothing to do. Exiting." >&2
  exit 0
fi

echo "  Found $(echo "$URLS" | wc -l | tr -d ' ') URLs:" >&2
echo "$URLS" | while read -r u; do echo "    - $u" >&2; done

# Build JSON input for fetch-daily-media.sh
URLS_JSON=$(echo "$URLS" | jq -R -s 'split("\n") | map(select(length > 0))')

FETCH_INPUT=$(jq -n \
  --arg date "$DATE" \
  --arg output_dir "$OUTPUT_DIR" \
  --argjson urls "$URLS_JSON" \
  '{date: $date, output_dir: $output_dir, urls: $urls}')

# ---------------------------------------------------------------------------
# Step 2: Fetch media
# ---------------------------------------------------------------------------
echo "" >&2
echo "--- Step 2: Fetching media ---" >&2

# Create output directory
mkdir -p "$PROJECT_DIR/$OUTPUT_DIR"

# Run the fetch script, capturing JSON result
FETCHER="$SCRIPT_DIR/fetch-daily-media.sh"
if [[ ! -x "$FETCHER" ]]; then
  echo "  Making fetch-daily-media.sh executable..." >&2
  chmod +x "$FETCHER"
fi

MEDIA_JSON=$(echo "$FETCH_INPUT" | bash "$FETCHER" 2>&2)
FETCH_EXIT=$?

if [[ $FETCH_EXIT -ne 0 ]]; then
  echo "  Warning: fetch-daily-media.sh exited with code $FETCH_EXIT" >&2
fi

# Quick summary of what was downloaded
X_COUNT=$(echo "$MEDIA_JSON" | jq '[.media[] | select(.type == "x")] | length' 2>/dev/null || echo 0)
YT_COUNT=$(echo "$MEDIA_JSON" | jq '[.media[] | select(.type == "youtube")] | length' 2>/dev/null || echo 0)
X_IMAGES=$(echo "$MEDIA_JSON" | jq '[.media[] | select(.type == "x") | .images // [] | length] | add' 2>/dev/null || echo 0)
echo "  Downloaded: ${X_IMAGES} images from ${X_COUNT} tweets, ${YT_COUNT} YouTube thumbnails" >&2

# ---------------------------------------------------------------------------
# Step 3: Generate HTML embed snippets for each media item
# ---------------------------------------------------------------------------
echo "" >&2
echo "--- Step 3: HTML embed snippets ---" >&2
echo ""

image_attrs() {
  local path="$1"
  local full_path="$PROJECT_DIR/$path"
  local width=""
  local height=""

  if command -v sips >/dev/null 2>&1 && [[ -f "$full_path" ]]; then
    width=$(sips -g pixelWidth "$full_path" 2>/dev/null | awk '/pixelWidth/ {print $2}')
    height=$(sips -g pixelHeight "$full_path" 2>/dev/null | awk '/pixelHeight/ {print $2}')
  elif command -v identify >/dev/null 2>&1 && [[ -f "$full_path" ]]; then
    width=$(identify -format '%w' "$full_path" 2>/dev/null || true)
    height=$(identify -format '%h' "$full_path" 2>/dev/null || true)
  fi

  if [[ -n "$width" && -n "$height" ]]; then
    printf ' width="%s" height="%s"' "$width" "$height"
  fi
}

# Print HTML snippets for embedding into the daily page
echo "$MEDIA_JSON" | jq -r '.media[] | @json' | while read -r item; do
  TYPE=$(echo "$item" | jq -r '.type')
  URL=$(echo "$item" | jq -r '.url')

  if [[ "$TYPE" == "x" ]]; then
    USERNAME=$(echo "$item" | jq -r '.username // ""')
    TWEET_ID=$(echo "$item" | jq -r '.tweet_id // ""')
    IMAGES=$(echo "$item" | jq -r '.images // []')
    ERROR=$(echo "$item" | jq -r '.error // ""')

    echo "  <!-- ${USERNAME} — ${URL} -->"
    if [[ -n "$ERROR" ]]; then
      echo "  <!-- [MEDIA FAILED] ${ERROR} — add manual screenshot if needed -->"
    else
      # Print <img> tags with relative paths (relative to docs/daily/)
      IMAGE_COUNT=$(echo "$IMAGES" | jq 'length')
      if [[ "$IMAGE_COUNT" -gt 0 ]]; then
        GALLERY_CLASS="vitem-gallery"
        if [[ "$IMAGE_COUNT" -eq 2 ]]; then
          GALLERY_CLASS="vitem-gallery cols-2"
        elif [[ "$IMAGE_COUNT" -gt 2 ]]; then
          GALLERY_CLASS="vitem-gallery cols-3"
        fi
        echo "  <div class=\"${GALLERY_CLASS}\">"
      fi
      IDX=0
      echo "$IMAGES" | jq -r '.[]' | while read -r abs_path; do
        # Convert absolute path to relative path from docs/daily/
        BASENAME=$(basename "$abs_path")
        REL_PATH="${ASSETS_REL}/${BASENAME}"
        ATTRS=$(image_attrs "docs/daily/${REL_PATH}")
        echo "    <img src=\"${REL_PATH}\"${ATTRS} loading=\"lazy\" alt=\"${USERNAME} tweet ${TWEET_ID} image ${IDX}\">"
        IDX=$((IDX + 1))
      done
      if [[ "$IMAGE_COUNT" -gt 0 ]]; then
        echo "  </div>"
      fi
    fi
    echo ""

  elif [[ "$TYPE" == "youtube" ]]; then
    VIDEO_ID=$(echo "$item" | jq -r '.video_id // ""')
    THUMBNAIL=$(echo "$item" | jq -r '.thumbnail // ""')
    ERROR=$(echo "$item" | jq -r '.error // ""')

    echo "  <!-- YouTube — ${URL} -->"

    # YouTube embed block
    if [[ -n "$VIDEO_ID" ]]; then
      echo "  <div class=\"video-container\" style=\"position:relative;padding-bottom:56.25%;margin-top:10px;\">"
      echo "    <iframe src=\"https://www.youtube-nocookie.com/embed/${VIDEO_ID}\" style=\"position:absolute;top:0;left:0;width:100%;height:100%;border:0;border-radius:8px;\" allowfullscreen></iframe>"
      echo "  </div>"
    fi

    if [[ -n "$THUMBNAIL" ]]; then
      BASENAME=$(basename "$THUMBNAIL")
      REL_PATH="${ASSETS_REL}/${BASENAME}"
      ATTRS=$(image_attrs "docs/daily/${REL_PATH}")
      echo "  <!-- Thumbnail: <div class=\"vitem-gallery\"><img src=\"${REL_PATH}\"${ATTRS} loading=\"lazy\" alt=\"YouTube thumbnail\"></div> -->"
    fi

    if [[ -n "$ERROR" ]]; then
      echo "  <!-- [THUMBNAIL FAILED] ${ERROR} -->"
    fi
    echo ""

  else
    echo "  <!-- Unknown type: ${URL} -->"
    echo ""
  fi
done

# ---------------------------------------------------------------------------
# Step 4: Archive update instructions
# ---------------------------------------------------------------------------
echo "--- Step 4: Archive update ---" >&2
echo "  Add a link to ${HTML_FILE} in docs/daily/archive.html:" >&2
echo "" >&2
echo "  <li><a href=\"ai-news-${DATE}.html\">${DATE} — AI Builders Daily</a></li>" >&2
echo "" >&2
echo "  Place it at the top of the archived-days list (reverse chronological order)." >&2

# ---------------------------------------------------------------------------
# Step 5: Homepage update instructions
# ---------------------------------------------------------------------------
echo "" >&2
echo "--- Step 5: Site index update ---" >&2
echo "  Run: npm run site:update" >&2
echo "  This scans docs/daily/ and docs/research/, then updates homepage and archive pages." >&2

# ---------------------------------------------------------------------------
# Final summary
# ---------------------------------------------------------------------------
echo "" >&2
echo "============================================" >&2
echo "  Pipeline complete." >&2
echo "  Media dir:  ${OUTPUT_DIR}" >&2
echo "  HTML file:  ${HTML_FILE}" >&2
echo "============================================" >&2

exit 0
