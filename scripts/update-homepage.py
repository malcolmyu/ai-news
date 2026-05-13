#!/usr/bin/env python3
"""
ai-news Homepage Updater
Regenerates the research section on the homepage to show:
- 1 featured card (newest report)
- 2 list items (next 2 newest reports)
- All other reports go to archive only
"""
import re, os, json
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, 'docs', 'index.html')

# ── Build report registry from actual files ──────────────────────────
RESEARCH_DIR = os.path.join(ROOT, 'docs', 'research')
reports = []
for f in os.listdir(RESEARCH_DIR):
    if not f.endswith('.html') or f == 'archive.html':
        continue
    mtime = os.path.getmtime(os.path.join(RESEARCH_DIR, f))
    reports.append((f, mtime))

# Sort newest first
reports.sort(key=lambda x: -x[1])

print(f"Found {len(reports)} reports, sorted by mtime")

# ── Read and update index.html ───────────────────────────────────────
with open(INDEX) as f:
    html = f.read()

# Everything before research section
before = html[:html.find('id="research"')]
# Everything after research section
after = html[html.find('</section>', html.find('id="research"')) + len('</section>'):]

# Build new research section
entries_html = ''
for i, (fname, mtime) in enumerate(reports[:3]):
    # Extract title from file
    with open(os.path.join(RESEARCH_DIR, fname)) as rf:
        content = rf.read()
    # Try to extract title from <title> or h1
    title_m = re.search(r'<title>(.*?)</title>', content)
    title = title_m.group(1).split('—')[0].strip() if title_m else fname.replace('.html','')
    # Date from mtime
    date = datetime.fromtimestamp(mtime).strftime('%Y/%-m/%-d')

    if i == 0:
        # Featured card
        entries_html += f'''<a href="research/{fname}" class="featured-card"><div class="featured-content"><div class="featured-meta"><span class="featured-badge">最新</span><span>{date}</span></div><h3 class="featured-title">{title}</h3><p class="featured-desc">查看完整调研报告</p></div><div class="featured-arrow">→</div></a>'''
    else:
        # List item
        entries_html += f'''<a href="research/{fname}" class="daily-entry"><div class="entry-icon">📊</div><div style="flex:1;"><div style="font-weight:500;font-size:14px;margin-bottom:2px;">{title}</div><div style="font-size:12px;color:var(--text-muted);">{date}</div></div><div style="font-size:16px;color:var(--text-muted);">→</div></a>'''

new_section = f'''id="research"><div class="container"><div class="section-header-hp"><div><div class="section-label">Research</div><h2 class="section-title-hp">深度调研报告</h2></div><a href="research/archive.html" class="section-link">查看全部 →</a></div>{entries_html}</div></section>'''

html = before + new_section + after

with open(INDEX, 'w') as f:
    f.write(html)

print("✅ Homepage research section updated!")
print(f"   Featured: {reports[0][0]}")
for i, (fname, _) in enumerate(reports[1:3], 1):
    print(f"   Entry {i}: {fname}")
print(f"   Others ({len(reports)-3}): only in archive")
