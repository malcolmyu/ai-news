#!/bin/bash
#===============================================================================
# fetch-daily-media.sh — Download media from X/Twitter and YouTube URLs
#
# Usage:
#   echo '{"urls":[...], "date":"2026-05-13", "output_dir":"docs/daily/assets/2026-05-13"}' \
#     | bash scripts/fetch-daily-media.sh
#
# Input:  stdin JSON → {urls: [...], date: "...", output_dir: "..."}
# Output: stdout JSON → {media: [{type, url, username?, tweet_id?, images?,
#          video_id?, thumbnail?, error?}]}
#
# Dependencies: curl, jq, grep (BSD/macOS), sed, awk — all system default
#===============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# 1. Read stdin JSON input
# ---------------------------------------------------------------------------
INPUT=$(cat)

OUTPUT_DIR=$(echo "$INPUT" | jq -r '.output_dir // ""')
URLS_JSON=$(echo "$INPUT" | jq -c '.urls // []')

if [[ -z "$OUTPUT_DIR" ]]; then
  echo '{"error":"missing output_dir in input JSON"}' >&2
  exit 1
fi

# Auto-create output dir including parent directories
mkdir -p "$OUTPUT_DIR"

# ---------------------------------------------------------------------------
# 2. Helper functions — URL parsing
# ---------------------------------------------------------------------------

# Extract X/Twitter username from URL: x.com/<user>/status/... or twitter.com/<user>/status/...
# Extract X/Twitter username from URL: x.com/<user>/status/... or twitter.com/<user>/status/...
extract_x_username() {
  echo "$1" | grep -oE '(x\.com|twitter\.com)/([^/]+)/status' | grep -oE '/[^/]+/' | tr -d '/'
}

# Extract tweet ID from X/Twitter URL
extract_x_tweet_id() {
  echo "$1" | grep -oE '/status/[0-9]+' | grep -oE '[0-9]+'
}

# Extract YouTube video ID from URL (watch?v=, youtu.be/, /embed/, /shorts/)
extract_yt_video_id() {
  local url="$1"
  if echo "$url" | grep -q 'youtu\.be/'; then
    echo "$url" | sed -n 's|.*youtu\.be/\([a-zA-Z0-9_-]*\).*|\1|p'
  else
    echo "$url" | sed -n 's|.*[/?&]v=\([a-zA-Z0-9_-]*\).*|\1|p'
  fi
}

# Determine file extension from URL path (fallback to jpg)
get_ext() {
  local url="$1"
  local url_ext="${url##*.}"
  url_ext="${url_ext%%\?*}"
  case "$url_ext" in
    jpg|jpeg|png|gif|webp|mp4) echo "$url_ext" ;;
    *) echo "jpg" ;;
  esac
}

# Check if URL is an X/Twitter status link
is_x_url() {
  echo "$1" | grep -qE '(x\.com|twitter\.com)/[^/]+/status/'
}

# Check if URL is a YouTube link
is_youtube_url() {
  echo "$1" | grep -qE '(youtube\.com|youtu\.be)'
}

# ---------------------------------------------------------------------------
# 3. X/Twitter: Method 1 — vxtwitter API (JSON, no auth, no Cloudflare)
#    Returns media URLs (images, videos) from the tweet
# ---------------------------------------------------------------------------
fetch_x_via_vxtwitter() {
  local username="$1"
  local tweet_id="$2"

  local api_url="https://api.vxtwitter.com/${username}/status/${tweet_id}"

  local json
  json=$(curl -sL --max-time 10 "$api_url" 2>/dev/null) || true

  if [[ -z "$json" ]]; then
    return 1
  fi

  # Extract media URLs from media_extended array (images only, not videos)
  local media_urls
  media_urls=$(echo "$json" | jq -r '.media_extended[]?.url // empty' 2>/dev/null) || true

  # Also try quoted tweet's article card image
  local article_img
  article_img=$(echo "$json" | jq -r '.qrt.article?.image // empty' 2>/dev/null) || true
  if [[ -n "$article_img" ]]; then
    media_urls="${media_urls}"$'\n'"${article_img}"
  fi

  # Also try quoted tweet's media
  local qrt_media_urls
  qrt_media_urls=$(echo "$json" | jq -r '.qrt.media_extended[]?.url // empty' 2>/dev/null) || true
  if [[ -n "$qrt_media_urls" ]]; then
    media_urls="${media_urls}"$'\n'"${qrt_media_urls}"
  fi

  # Filter to only image files (skip videos)
  local img_urls
  img_urls=$(echo "$media_urls" | grep -iE '\.(jpg|jpeg|png|webp|gif)($|\?)' || true)

  if [[ -z "$img_urls" ]]; then
    return 1
  fi

  echo "$img_urls"
  return 0
}

# ---------------------------------------------------------------------------
# 4. X/Twitter: Method 2 — fxtwitter API (JSON, no auth, returns media URLs)
# ---------------------------------------------------------------------------
fetch_x_via_fxtwitter() {
  local tweet_id="$1"

  local api_url="https://api.fxtwitter.com/status/${tweet_id}"

  local json
  json=$(curl -sL --max-time 15 "$api_url" 2>/dev/null) || true

  if [[ -z "$json" ]]; then
    return 1
  fi

  if echo "$json" | jq -e '.code == 404' >/dev/null 2>&1; then
    return 1
  fi

  # Extract media.photos[].url array
  local photo_urls
  photo_urls=$(echo "$json" | jq -r '.tweet.media?.photos[]?.url // empty' 2>/dev/null) || true

  if [[ -z "$photo_urls" ]]; then
    return 1
  fi

  echo "$photo_urls"
  return 0
}

# ---------------------------------------------------------------------------
# 5. Download images helper — given newline-separated URLs, downloads to output dir
#    Returns newline-separated output paths (relative to project root)
# ---------------------------------------------------------------------------
download_images() {
  local prefix="$1"    # e.g. "karpathy-2053872850101285137"
  local output_dir="$2"
  shift 2
  # remaining args read from stdin: image URLs, one per line

  local idx=0
  local paths=""
  while IFS= read -r img_url; do
    [[ -z "$img_url" ]] && continue

    # Ensure absolute URL
    if [[ "$img_url" != http* ]]; then
      img_url="https://nitter.net${img_url}"
    fi

    local ext
    ext=$(get_ext "$img_url")

    local dest="${output_dir}/${prefix}-${idx}.${ext}"

    if curl -sL --max-time 20 -o "$dest" "$img_url" 2>/dev/null && [[ -s "$dest" ]]; then
      # Output path relative to project root
      paths+="${dest}"$'\n'
      ((idx++))
    fi
  done

  echo "$paths"
}

# ---------------------------------------------------------------------------
# 6. Process a single X/Twitter URL → outputs a JSON line for the media array
# ---------------------------------------------------------------------------
process_x_url() {
  local url="$1"
  local output_dir="$2"
  local username tweet_id

  username=$(extract_x_username "$url")
  tweet_id=$(extract_x_tweet_id "$url")

  if [[ -z "$username" || -z "$tweet_id" ]]; then
    echo '{"type":"x","url":"'"$url"'","error":"failed to extract username or tweet_id"}' >&2
    echo '{"type":"x","url":"'"$url"'","error":"failed to extract username or tweet_id"}'
    return
  fi

  local prefix="${username}-${tweet_id}"
  local downloaded_paths=""
  local error_msg=""

  # Try vxtwitter API
  local vx_imgs
  if vx_imgs=$(fetch_x_via_vxtwitter "$username" "$tweet_id"); then
    downloaded_paths=$(echo "$vx_imgs" | download_images "$prefix" "$output_dir")
  else
    error_msg="vxtwitter unavailable" >&2
  fi

  # Fallback to fxtwitter if no images downloaded
  if [[ -z "$(echo "$downloaded_paths" | tr -d '[:space:]')" ]]; then
    local fx_imgs
    if fx_imgs=$(fetch_x_via_fxtwitter "$tweet_id"); then
      # Resume from nitter's index if nitter did download some
      local count
      count=$(echo "$downloaded_paths" | grep -c . || echo 0)
      local more_paths
      more_paths=$(echo "$fx_imgs" | download_images "$prefix" "$output_dir")
      downloaded_paths+="$more_paths"
    fi
  fi

  # Build images JSON array from downloaded paths
  local images_json="[]"
  if [[ -n "$(echo "$downloaded_paths" | tr -d '[:space:]')" ]]; then
    while IFS= read -r p; do
      [[ -z "$p" ]] && continue
      images_json=$(echo "$images_json" | jq '. + ["'"$p"'"]')
    done <<< "$downloaded_paths"
  fi

  # Build the result JSON object
  local result
  result=$(jq -n \
    --arg type "x" \
    --arg url "$url" \
    --arg username "$username" \
    --arg tweet_id "$tweet_id" \
    --argjson images "$images_json" \
    '{type: $type, url: $url, username: $username, tweet_id: $tweet_id, images: $images}')

  # If no images downloaded, add error field
  if [[ "$images_json" == "[]" ]]; then
    echo "  [warn] No images for ${url}" >&2
    result=$(echo "$result" | jq '. + {error: "no images found"}')
  fi

  echo "$result"
}

# ---------------------------------------------------------------------------
# 7. Process a single YouTube URL → outputs a JSON line for the media array
# ---------------------------------------------------------------------------
process_youtube_url() {
  local url="$1"
  local output_dir="$2"
  local video_id

  video_id=$(extract_yt_video_id "$url")

  if [[ -z "$video_id" ]]; then
    echo '{"type":"youtube","url":"'"$url"'","error":"failed to extract video_id"}' >&2
    echo '{"type":"youtube","url":"'"$url"'","error":"failed to extract video_id"}'
    return
  fi

  # Try multiple YouTube thumbnail resolutions (maxres → hq → sd)
  local thumbnail_path=""
  local attempted_urls=(
    "https://img.youtube.com/vi/${video_id}/maxresdefault.jpg"
    "https://img.youtube.com/vi/${video_id}/hqdefault.jpg"
    "https://img.youtube.com/vi/${video_id}/sddefault.jpg"
  )

  for thumb_url in "${attempted_urls[@]}"; do
    local dest="${output_dir}/yt-${video_id}.jpg"
    if curl -sL --max-time 20 -o "$dest" "$thumb_url" 2>/dev/null && [[ -s "$dest" ]]; then
      # Validate it's a real image (YouTube returns a placeholder for missing resolutions)
      if file "$dest" 2>/dev/null | grep -qi 'JPEG\|PNG\|GIF\|Web'; then
        thumbnail_path="${output_dir}/yt-${video_id}.jpg"
        break
      fi
    fi
  done

  # Build the result JSON
  local result
  if [[ -n "$thumbnail_path" ]]; then
    result=$(jq -n \
      --arg type "youtube" \
      --arg url "$url" \
      --arg video_id "$video_id" \
      --arg thumbnail "$thumbnail_path" \
      '{type: $type, url: $url, video_id: $video_id, thumbnail: $thumbnail}')
  else
    echo "  [warn] Thumbnail download failed for ${url}" >&2
    result=$(jq -n \
      --arg type "youtube" \
      --arg url "$url" \
      --arg video_id "$video_id" \
      '{type: $type, url: $url, video_id: $video_id, error: "thumbnail download failed"}')
  fi

  echo "$result"
}

# ---------------------------------------------------------------------------
# 8. Main loop — iterate over all URLs, classify & process each
# ---------------------------------------------------------------------------
MEDIA_RESULTS="[]"

URL_COUNT=$(echo "$URLS_JSON" | jq 'length')

for (( i=0; i<URL_COUNT; i++ )); do
  URL=$(echo "$URLS_JSON" | jq -r '.['"$i"']')

  if is_x_url "$URL"; then
    RESULT=$(process_x_url "$URL" "$OUTPUT_DIR")
  elif is_youtube_url "$URL"; then
    RESULT=$(process_youtube_url "$URL" "$OUTPUT_DIR")
  else
    RESULT='{"type":"unknown","url":"'"$URL"'","error":"unsupported URL type"}'
    echo "  [skip] Unsupported URL: ${URL}" >&2
  fi

  MEDIA_RESULTS=$(echo "$MEDIA_RESULTS" | jq '. + ['"$RESULT"']')
done

# ---------------------------------------------------------------------------
# 9. Output final JSON to stdout (only JSON, all diagnostics go to stderr)
# ---------------------------------------------------------------------------
echo "$MEDIA_RESULTS" | jq '{media: .}'

exit 0
