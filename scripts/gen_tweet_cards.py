#!/usr/bin/env python3
"""Fetch tweet data and generate HTML cards for daily digest builder section.
Usage: python3 scripts/gen_tweet_cards.py <daily_html_path>
Reads tweet URLs from the builder section, fetches data from syndication API,
downloads media, and generates tweet card HTML vitems.
"""

import requests, json, re, os, sys
from datetime import datetime, timezone
from PIL import Image
from io import BytesIO

WORKDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(WORKDIR, 'docs', 'daily', 'assets')

def fetch_tweet(tweet_id):
    """Fetch tweet data from syndication API. Returns dict or None."""
    url = f'https://cdn.syndication.twimg.com/tweet-result?id={tweet_id}&token=0'
    try:
        r = requests.get(url, timeout=10)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

def download_media(tweet, tweet_id):
    """Download and compress media. Returns relative path or None."""
    os.makedirs(ASSETS_DIR, exist_ok=True)
    local = os.path.join(ASSETS_DIR, f'tweet_{tweet_id}.jpg')
    if os.path.exists(local):
        return f'assets/tweet_{tweet_id}.jpg'

    img_url = None
    if 'photos' in tweet and tweet['photos']:
        img_url = tweet['photos'][0].get('url', '')
    elif 'entities' in tweet and 'media' in tweet['entities']:
        for m in tweet['entities']['media']:
            if m.get('type') in ('photo', 'video', 'animated_gif'):
                img_url = m.get('media_url_https', '')
                break
    if not img_url:
        return None

    try:
        r = requests.get(img_url, timeout=15)
        if r.status_code != 200:
            return None
        img = Image.open(BytesIO(r.content))
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        w, h = img.size
        if w > 1200:
            img = img.resize((1200, int(h * 1200 / w)), Image.LANCZOS)
        for q in [92, 85, 75, 65, 55]:
            img.save(local, 'JPEG', quality=q, optimize=True)
            if os.path.getsize(local) <= 500 * 1024:
                break
        return f'assets/tweet_{tweet_id}.jpg'
    except Exception:
        return None

def fmt_time(created_at):
    try:
        dt = datetime.strptime(created_at, '%a %b %d %H:%M:%S %z %Y')
        diff = datetime.now(timezone.utc) - dt
        if diff.days == 0: return dt.strftime('%H:%M')
        if diff.days == 1: return '昨天'
        return f'{dt.month}月{dt.day}日'
    except:
        return ''

def esc(text):
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return re.sub(r'(https?://[^\s]+)', r'<a href="\1" target="_blank">\1</a>', text)

def card_html(tweet, tweet_id, screen_name):
    u = tweet.get('user', {})
    name = u.get('name', screen_name)
    handle = u.get('screen_name', screen_name)
    avatar = u.get('profile_image_url_https', '')
    text = esc(tweet.get('text', ''))
    favs = tweet.get('favorite_count', 0)
    rts = tweet.get('retweet_count', 0)
    replies = tweet.get('conversation_count', 0) or tweet.get('reply_count', 0)
    date_str = fmt_time(tweet.get('created_at', ''))
    media = download_media(tweet, tweet_id)

    card = f'''    <div class="vitem">
      <div class="tweet-card">
        <div class="tweet-header">
          <img class="tweet-avatar" src="{avatar}" alt="" loading="lazy">
          <div class="tweet-author">
            <span class="tweet-name">{name}</span>
            <span class="tweet-handle">@{handle}</span>
          </div>
          <span class="tweet-date">{date_str}</span>
        </div>
        <div class="tweet-body">{text}</div>'''
    if media:
        card += f'''
        <div class="tweet-media"><img src="{media}" alt="" loading="lazy"></div>'''
    card += f'''
        <div class="tweet-metrics">
          <span>♥ {favs}</span>
          <span>↺ {rts}</span>
          <span>💬 {replies}</span>
        </div>
        <a href="https://x.com/{handle}/status/{tweet_id}" target="_blank" class="tweet-link">在 X 上查看</a>
      </div>
    </div>'''
    return card

def process_daily(html_path):
    with open(html_path) as f:
        html = f.read()

    builder_start = html.index('<div class="label-sm">建造者动态</div>')
    sec_end = html.find('</section>', builder_start) + len('</section>')
    builder_html = html[builder_start:sec_end]

    urls = re.findall(r'href="(https://x\.com/([^/]+)/status/(\d+))"', builder_html)
    cards = []
    for url, sn, tid in urls:
        tweet = fetch_tweet(tid)
        if tweet:
            cards.append(card_html(tweet, tid, sn))
        else:
            print(f"  FAIL: @{sn}/{tid} — keeping original", file=sys.stderr)

    cards_html = '\n'.join(cards)
    vlist_start = html.find('<div class="vlist-2col">', builder_start)
    depth = 0
    pos = vlist_start
    while pos < len(html):
        if html.startswith('<div', pos):
            depth += 1; pos += 4
        elif html.startswith('</div>', pos):
            depth -= 1
            if depth == 0:
                vlist_end = pos + 6; break
            pos += 6
        else:
            pos += 1

    new_section = html[:builder_start] + '<div class="label-sm">建造者动态</div>\n  <div class="vlist-2col">\n' + cards_html + '\n  </div>\n</section>'
    new_html = new_section + html[sec_end:]

    with open(html_path, 'w') as f:
        f.write(new_html)
    print(f"Updated {html_path} with {len(cards)} tweet cards")

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(WORKDIR, 'docs', 'daily', 'ai-news-2026-06-04.html')
    process_daily(path)
