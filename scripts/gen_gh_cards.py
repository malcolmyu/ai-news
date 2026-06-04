#!/usr/bin/env python3
"""Fetch GitHub repo data and generate HTML cards for daily digest trending section.
Usage: python3 scripts/gen_gh_cards.py <daily_html_path> [--translations trans.json]
Reads repo URLs from GitHub Trending section, fetches data from GitHub API,
and generates repo card HTML vitems.
--translations: optional JSON file mapping "owner/repo" -> Chinese description.
"""

import requests, json, re, os, sys
from pathlib import Path

WORKDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(WORKDIR, 'docs', 'daily', 'assets')

def fetch_repo(owner, repo):
    """Fetch repo data from GitHub API. Returns dict or None."""
    url = f'https://api.github.com/repos/{owner}/{repo}'
    try:
        r = requests.get(url, headers={'Accept': 'application/vnd.github+json'}, timeout=10)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

def esc(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def fmt_num(n):
    if n >= 1000:
        return f'{n/1000:.1f}k'
    return str(n)

def card_html(repo_data, owner, repo_name, translation=None):
    avatar = repo_data.get('owner', {}).get('avatar_url', '')
    desc = repo_data.get('description') or ''
    stars = repo_data.get('stargazers_count', 0)
    forks = repo_data.get('forks_count', 0)
    language = repo_data.get('language') or ''
    topics = repo_data.get('topics', [])[:4]
    homepage = repo_data.get('homepage', '')

    card = f'''    <div class="vitem">
      <a href="https://github.com/{owner}/{repo_name}" target="_blank" class="gh-card">
        <div class="gh-header">
          <img class="gh-avatar" src="{avatar}" alt="" loading="lazy">
          <div class="gh-repo">
            <span class="gh-owner">{owner}</span><span class="gh-sep">/</span><span class="gh-name">{repo_name}</span>
          </div>
          <span class="gh-stars">⭐ {fmt_num(stars)}</span>
        </div>'''
    if desc:
        card += f'''
        <div class="gh-body">{esc(desc)}</div>'''
    if translation:
        card += f'''
        <div class="gh-translation">{esc(translation)}</div>'''
    card += f'''
        <div class="gh-meta">'''
    if language:
        card += f'''
          <span class="gh-lang">● {language}</span>'''
    card += f'''
          <span class="gh-forks">🍴 {fmt_num(forks)}</span>'''
    if topics:
        topic_tags = ''.join(f'<span class="gh-topic">{t}</span>' for t in topics)
        card += f'''
          <span class="gh-topics">{topic_tags}</span>'''
    card += f'''
        </div>
      </a>
    </div>'''
    return card

def process_daily(html_path, translations=None):
    translations = translations or {}
    with open(html_path) as f:
        html = f.read()

    # Find GitHub Trending section
    gh_start = html.index('<div class="label-sm">GitHub Trending</div>')
    sec_end = html.find('</section>', gh_start) + len('</section>')

    # Extract repo URLs: github.com/owner/repo
    urls = re.findall(r'github\.com/([^/]+)/([^/"\s<>]+)', html[gh_start:sec_end])
    seen = set()
    repos = []
    for owner, repo in urls:
        repo = repo.rstrip('/')
        key = f'{owner}/{repo}'
        if key not in seen:
            seen.add(key)
            repos.append((owner, repo, key))

    cards = []
    for owner, repo, key in repos:
        data = fetch_repo(owner, repo)
        if data and 'owner' in data:
            cards.append(card_html(data, owner, repo, translation=translations.get(key, '')))
        else:
            print(f"  FAIL: {owner}/{repo} — keeping original", file=sys.stderr)

    cards_html = '\n'.join(cards)

    # Find vlist-2col inside GitHub Trending section and replace its content
    vlist_start = html.find('<div class="vlist-2col">', gh_start)
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

    new_section = html[:gh_start] + '<div class="label-sm">GitHub Trending</div>\n  <div class="vlist-2col">\n' + cards_html + '\n  </div>\n</section>'
    new_html = new_section + html[sec_end:]

    with open(html_path, 'w') as f:
        f.write(new_html)
    print(f"Updated GitHub Trending in {html_path} with {len(cards)} repo cards")

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('html_path', nargs='?', default=None)
    p.add_argument('--translations', type=str, default=None, help='JSON file: {"owner/repo": "中文描述", ...}')
    args = p.parse_args()

    path = args.html_path or os.path.join(WORKDIR, 'docs', 'daily', 'ai-news-2026-06-04.html')

    trans = {}
    if args.translations:
        with open(args.translations) as f:
            trans = json.load(f)

    process_daily(path, translations=trans)
