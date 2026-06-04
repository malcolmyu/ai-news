#!/usr/bin/env python3
"""Fetch RSS feeds and generate HTML cards for daily digest RSS section.
Usage: python3 scripts/gen_rss_cards.py <daily_html_path>
Reads feeds from feeds.json, fetches recent articles, generates RSS vitem cards,
and inserts them into the daily HTML.
"""

import json, os, sys, re
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone, timedelta
import xml.etree.ElementTree as ET
import requests

WORKDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_feeds():
    path = os.path.join(WORKDIR, 'feeds.json')
    with open(path) as f:
        return json.load(f)['feeds']

def fetch_feed(feed):
    """Fetch and parse RSS/Atom feed. Returns list of article dicts."""
    try:
        r = requests.get(feed['url'], timeout=15, headers={'User-Agent': 'ai-news-bot/1.0'})
        if r.status_code != 200:
            return []
        root = ET.fromstring(r.content)

        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        items = root.findall('.//item') or root.findall('.//atom:entry', ns)
        if not items:
            items = root.findall('.//{http://www.w3.org/2005/Atom}entry')

        articles = []

        for item in items:
            title = item.find('title')
            link = item.find('link')
            desc = item.find('description')

            title = title.text.strip() if title is not None and title.text else ''
            if link is not None:
                link = link.get('href') or (link.text.strip() if link.text else '')
            else:
                link = ''
            desc_raw = desc.text.strip() if desc is not None and desc.text else ''

            # Clean description: strip HTML tags
            desc_clean = re.sub(r'<[^>]+>', '', desc_raw)[:200].strip()
            if not desc_clean and len(title) > 50:
                desc_clean = title[:200]

            pub = item.find('pubDate')
            if pub is None:
                pub = item.find('.//{http://www.w3.org/2005/Atom}published')
            if pub is None:
                pub = item.find('.//{http://www.w3.org/2005/Atom}updated')
            pub_date = None
            if pub is not None and pub.text:
                try:
                    pub_date = parsedate_to_datetime(pub.text.strip())
                except Exception:
                    try:
                        pub_date = datetime.strptime(pub.text.strip()[:19], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
                    except Exception:
                        try:
                            pub_date = datetime.strptime(pub.text.strip()[:10], '%Y-%m-%d').replace(tzinfo=timezone.utc)
                        except Exception:
                            pass

            if pub_date and title:
                articles.append({
                    'title': title,
                    'link': link,
                    'description': desc_clean or '',
                    'source': feed['name'],
                    'date': pub_date.strftime('%m-%d %H:%M'),
                })

        # Sort by date desc, limit per source
        articles.sort(key=lambda a: a['date'], reverse=True)
        return articles[:2]
    except Exception as e:
        print(f"  RSS FAIL: {feed['name']} — {e}", file=sys.stderr)
        return []

def esc(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def card_html(article):
    title = esc(article['title'])
    desc = esc(article['description']) if article['description'] else ''
    link = article['link']
    source = article['source']
    date = article['date']

    card = f'''    <div class="vitem">
      <a href="{link}" target="_blank" class="rss-card">
        <div class="rss-header">
          <span class="rss-source">{source}</span>
          <span class="rss-date">{date}</span>
        </div>
        <div class="rss-title">{title}</div>'''
    if desc:
        card += f'''
        <div class="rss-desc">{desc}</div>'''
    card += f'''
      </a>
    </div>'''
    return card

def process_daily(html_path):
    feeds = load_feeds()
    all_articles = []
    for feed in feeds:
        articles = fetch_feed(feed)
        all_articles.extend(articles)
        print(f"  {feed['name']}: {len(articles)} recent articles")

    # Sort by date desc
    all_articles.sort(key=lambda a: a['date'], reverse=True)

    if not all_articles:
        print("No recent RSS articles found")
        return

    with open(html_path) as f:
        html = f.read()

    cards = [card_html(a) for a in all_articles]
    cards_html = '\n'.join(cards)

    # Build RSS section HTML
    sources_str = ' · '.join(f['name'] for f in feeds)
    rss_section = f'''<section class="card span-4">
  <div class="label-sm">RSS 精选</div>
  <h2>值得关注的文章</h2>
  <div class="vlist-2col" style="margin-top:12px;">
{cards_html}
  </div>
  <div class="quote" style="margin-top:12px;font-size:12px;color:#8b8b8b;">
    RSS 源：{sources_str}
  </div>
</section>'''

    # Remove all existing RSS sections
    while True:
        existing = html.find('<div class="label-sm">RSS 精选</div>')
        if existing == -1:
            break
        sec_start = html.rfind('<section', 0, existing)
        sec_end = html.find('</section>', existing) + len('</section>')
        html = html[:sec_start] + html[sec_end:]

    # Insert RSS section before builder section
    builder_pos = html.index('<div class="label-sm">建造者动态</div>')
    # Find the opening <section> tag before it
    sec_start = html.rfind('<section', 0, builder_pos)
    new_html = html[:sec_start] + rss_section + '\n\n' + html[sec_start:]

    with open(html_path, 'w') as f:
        f.write(new_html)
    print(f"Inserted RSS section with {len(all_articles)} articles into {html_path}")

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(WORKDIR, 'docs', 'daily', 'ai-news-2026-06-04.html')
    process_daily(path)
