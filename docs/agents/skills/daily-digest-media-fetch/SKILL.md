---
name: daily-digest-media-fetch
description: Fetch media (images, thumbnails) from X/Twitter and YouTube URLs for ai-news daily digest, then emit dimension-aware local assets for masonry Builder cards.
---
# Daily Digest Media Fetch Workflow

## 项目内版本说明（2026-05-31）

此文件是从 Hermes 全局 skill 同步到 ai-news 仓库后的项目内 source of truth。后续日报生成应优先使用本项目内版本，并与 `scripts/fetch-daily-media.sh`、`scripts/generate-daily-html.sh`、`scripts/site_harness.py` 保持同步。

**当前项目要求：**
- 本地图片必须带 `width` / `height` HTML 属性，用于首屏前预判尺寸和瀑布流配平。
- 禁止写 `style="width:100%"` 这类 inline CSS；响应式宽度由共享 `.vitem-gallery img` 样式处理。
- Builder 动态必须放入 `.vlist.vlist-2col`，共享 `docs/site.js` 会自动按高度精确配平并在移动端恢复单列。
- 下载后的图片压缩目标是 800px 宽、JPEG 85、锐化；不要回退到 400px/55q。
- 校验由 `scripts/site_harness.py validate` 拦截 `.vitem-gallery` 本地图片缺宽高的问题。

## Scripts

Located in `/Users/yuminghao/Work/ai-news/scripts/`:

- `fetch-daily-media.sh` — Fetches media from URLs, outputs JSON with media paths. Supports **parallel download (6 concurrent)**, **Clash Verge proxy**, **video thumbnail extraction** from quoted tweets.

### Key capabilities (v2, 2026-05-30)

| Feature | Detail |
|---------|--------|
| **并发** | 6 路并行下载，17 URL 从 ~5min 降到 ~30s |
| **代理** | `proxy` 字段，sandbox 通过 `127.0.0.1:7897` 访问被墙 CDN |
| **视频缩略图** | 捕获 `media_extended[type=video].thumbnail_url`（主推文 + qrt 引用推文） |
| **YouTube CDN 备选** | `i.ytimg.com` 作为 `img.youtube.com` 的 fallback |
| **超时优化** | API 8s、下载 12s、YouTube 10s |

## Usage

### Fetch Media Only
```bash
echo '{
  "urls": [
    "https://x.com/karpathy/status/2053872850101285137",
    "https://www.youtube.com/watch?v=g5TWnUjbeFM"
  ],
  "date": "YYYY-MM-DD",
  "output_dir": "docs/daily/assets/YYYY-MM-DD",
  "proxy": "http://127.0.0.1:7897"
}' | bash scripts/fetch-daily-media.sh
```

**proxy 字段可选。** 设置后所有 curl 请求走代理。Clash Verge 默认端口 7897。sandbox 网络无法直连 `pbs.twimg.com` / `img.youtube.com` 时必需。

### Output JSON
```json
{
  "media": [
    {
      "type": "x",
      "url": "https://x.com/joshwoodward/status/...",
      "username": "joshwoodward",
      "tweet_id": "2060443102507302948",
      "images": ["docs/daily/assets/YYYY-MM-DD/joshwoodward-xxx-0.jpg"]
    },
    {
      "type": "youtube",
      "url": "https://www.youtube.com/watch?v=...",
      "video_id": "Gs2styCcwro",
      "thumbnail": "docs/daily/assets/YYYY-MM-DD/yt-xxx.jpg"
    },
    {
      "type": "x",
      "url": "https://x.com/garrytan/status/...",
      "username": "garrytan",
      "tweet_id": "...",
      "images": [],
      "error": "no media found"
    }
  ]
}
```

## X/Twitter Media Sources (priority order)

1. **api.vxtwitter.com** — Primary source. Works without auth, no Cloudflare. Returns JSON with `media_extended[]` and `qrt` (quoted tweet) object.
2. **Main tweet images** — `.media_extended[]` with `type == "image"`
3. **Main tweet video thumbnails** — `.media_extended[]` with `type == "video"` or `"animated_gif"` → `.thumbnail_url` (these ARE images, fetchable)
4. **Quoted tweet images** — `.qrt.media_extended[]` with `type == "image"`
5. **Quoted tweet video thumbnails** — `.qrt.media_extended[]` with `type == "video"` → `.thumbnail_url`
6. **Article card images** — `.qrt.article.image` (link preview cards in quoted tweets)
7. Falls back to **fxtwitter API** if vxtwitter returns nothing

## YouTube Media

- Downloads thumbnail from `img.youtube.com/vi/<id>/maxresdefault.jpg`
- Falls back CDN: `i.ytimg.com/vi/<id>/maxresdefault.jpg` (different CDN, sometimes reachable when `img.youtube.com` is blocked)
- Resolution fallback: maxresdefault → hqdefault → sddefault
- Validates the downloaded file is a real JPEG/PNG (YouTube returns placeholders for missing resolutions)

## Key behaviors

- **Parallel processing** — 6 concurrent workers, dramatically faster for digest-sized batches (17 URLs)
- **Video thumbnails are images** — `type == "video"` in vxtwitter has a `.thumbnail_url` that IS a regular JPEG. The script captures these (useful for demo tweets like Josh Woodward's Gemini demos)
- **Quote tweet depth** — Captures media from `.qrt.media_extended[]` (quoted tweets), critical when a builder just retweets/links to a demo
- If a tweet has no image media, reports `"error": "no media found"` — this is normal for text-only tweets
- All errors go to stderr; stdout is clean JSON
- Auto-creates output directory
- Timeouts: 8s API calls, 12s image downloads, 10s YouTube thumbnails

## HTML Integration

When generating daily digest HTML:
- **⛔ 禁止 inline `style="width:100%"`，本地图必须带 `width`/`height` 属性** — flex 容器中的 inline width 会导致级联溢出；HTML 属性只用于 intrinsic ratio，不等同于 CSS width。
- **⛔ 禁止把图塞在 vitem 右侧 `flex-shrink:0` 侧栏** — 这会导致图文割裂
- Use `.vitem-gallery` with CSS Grid inside `.vitem` — images flow naturally in the content column
- Multi-image: `class="vitem-gallery cols-2"` (2 images) or `cols-3` (3+ images)
- Single image: `class="vitem-gallery"` (auto-fit defaults to 1 column)
- Multi-image galleries are height-aligned by shared CSS: desktop uses same-row cropped thumbnails (`object-fit: cover`) and mobile returns to natural image height.
- Daily pages get click-to-zoom automatically from `docs/site.js`; do not wrap images in custom links or page-specific modal code.
- Legacy daily pages are upgraded at runtime by `upgradeLegacyDailyGalleries()` in `docs/site.js`: direct local `<img src="assets/...">` children under `.card` or `.vitem` are moved into generated `.vitem-gallery` wrappers. Do not remove this compatibility layer unless all old daily HTML has been migrated.
- Only add `<img>` tags for tweets that have images in the output
- Path: relative `assets/YYYY-MM-DD/xxx.jpg`
- Do NOT add placeholder img tags for tweets without media
- After downloading, **MUST compress images** (see Compression section)

**Correct HTML template (images embedded in content flow):**
```html
<div class="vitem">
  <div class="vitem-body">
    <div class="vitem-title">Builder Name</div>
    <div class="vitem-desc">Text content...</div>
  </div>
  <div class="vitem-gallery cols-2">
    <img src="assets/YYYY-MM-DD/xxx-0.jpg" width="1200" height="675" loading="lazy" alt="">
    <img src="assets/YYYY-MM-DD/xxx-1.jpg" width="1200" height="900" loading="lazy" alt="">
  </div>
  <div class="vitem-actions">
    <a href="URL" target="_blank" class="vitem-link">查看 →</a>
  </div>
</div>
```

### Image Compression (mandatory — do not skip)

Twitter's CDN returns high-quality JPEGs that are 100-200KB each. Must compress before embedding:

```bash
python3 -c "from PIL import Image, ImageFilter; import os
for f in os.listdir('docs/daily/assets/YYYY-MM-DD'):
    if not f.endswith('.jpg'): continue
    p=os.path.join('docs/daily/assets/YYYY-MM-DD',f); img=Image.open(p);img.load()
    if img.mode in ('P','RGBA','LA','CMYK'):img=img.convert('RGB')
    w,h=img.size
    # If <800px: re-download via wsrv.nl (see pitfall). Do NOT LANCZOS upscale.
    if w<800: print(f'WARNING: {f} is only {w}px — re-download via wsrv.nl')
    elif w>1200:img=img.resize((800,int(h*800/w)),Image.LANCZOS)
    img=img.filter(ImageFilter.UnsharpMask(radius=1,percent=80,threshold=2))  # sharpen
    img.save(p,'JPEG',quality=85,optimize=True,progressive=True)
    print(f'{f}: {os.path.getsize(p)//1024}KB')"
```

Target: < 600KB total, < 100KB per image. 800px wide + quality 85 + sharpen = clear on Retina displays.

## URLs from Digest Text

Extract all X/Twitter and YouTube URLs from the digest text using regex:
- `x\.com/[^/]+/status/[0-9]+` — X/Twitter status URLs
- `youtube\.com/watch\?v=` — YouTube watch URLs

## Cron Prompt Integration

The cron job `88c05cab9efd` that generates the daily HTML page should run this script as **Step 0** — a black-box pre-step BEFORE HTML generation. Key principles:

1. Run the script as a single `bash` command — don't try to replicate the logic
2. Extract image paths from JSON output with `jq`
3. Only embed `<img>` for entries that returned non-empty `images[]`
4. If ALL entries return "no media found" (common for text-heavy days), skip all image embedding — don't add placeholder markup
5. This step should NOT distract from the main content generation (the digest is the content, media is decoration)

## Pitfalls

### ⛔ "No media found" is often legitimate

Most builder tweets are text-only (opinions, analysis, links). On a typical day, 80-100% of tweets return "no media found". This is NOT a script failure — it's correct behavior. Do NOT rerun the script or try alternative methods when this happens.

Signals that "no media" is legitimate:
- The tweet text contains analysis/opinion (not a demo/screenshot)
- The tweeter is known for text-only content (VCs, researchers, PMs)
- The tweet is a link to external content

Signals that media SHOULD exist:
- Tweet text describes a visual demo ("check out this screen recording")
- Tweet is from a product launch ("announcing Replit Canvas")
- Tweet is from a designer/artist

### ⛔ Sandbox network can't reach image CDNs

`pbs.twimg.com` (Twitter image CDN) and `img.youtube.com` (YouTube thumbnail CDN) may be unreachable from the sandbox network. The script handles this gracefully:
- API calls succeed (vxtwitter returns JSON fine)
- Image downloads timeout → reported as "no media found"
- `i.ytimg.com` is tried as a fallback YouTube thumbnail CDN
- This is a network limitation, not a script bug

### ⛔ Image download fallback: wsrv.nl public proxy (when both direct and local proxy fail)

When `pbs.twimg.com` is blocked AND the local Clash Verge proxy is down, neither `--proxy http://127.0.0.1:7890` nor direct connection works. Use **wsrv.nl** as a last-resort public image proxy:

```bash
# wsrv.nl acts as a man-in-the-middle: it fetches from pbs.twimg.com and serves the result
SOURCE_URL="https://pbs.twimg.com/media/HJcdwczasAA1tDl.jpg?format=jpg&name=orig"
ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$SOURCE_URL', safe=''))")
curl -sL "https://wsrv.nl/?url=${ENCODED}&w=1200&q=90" -o output.jpg
```

**Key parameters:**
- `w=1200` — resize to 1200px wide (wsrv.nl handles the downscaling)
- `q=90` — JPEG quality 90 (high quality, wsrv.nl does the compression)
- `?format=jpg&name=orig` on the source URL — request full native resolution from Twitter
- No `--proxy` needed — wsrv.nl is a public service, reachable directly

**When to use:**
1. Direct `curl pbs.twimg.com` fails (HTTP 000 or timeout)
2. Clash Verge proxy (`127.0.0.1:7890` / `127.0.0.1:7897`) is not running or also fails
3. vxtwitter API returned image URLs but downloads fail

**Pitfalls:**
- Card preview images (`card_img/*`) may need `?format=jpg&name=large` instead of `?format=jpg&name=orig`
- wsrv.nl may return 500 for certain URLs — retry with different format parameters
- Downloaded images come at 1200px native resolution (~100-250KB each) — DO NOT compress further, they're already optimized
- This is a fallback, not the primary path. Prefer direct download via proxy when available.

### ⛔ Quote tweets are the primary source of media

Builders often share demos via quote tweets (retweeting someone else's video/screenshot and adding commentary). The media is on the QUOTED tweet, not the builder's tweet. The script handles this via `.qrt.media_extended[]` extraction, but only if the quote tweet's media is included in the vxtwitter response (usually yes).

### ⛔ Video files are not downloadable

Native Twitter videos (`.mp4` from `video.twimg.com`) aren't downloaded — only JPEG/PNG thumbnails. For demo videos, the thumbnail gives context but isn't playable. Consider embedding a thumbnail image + link to the tweet for video content.
