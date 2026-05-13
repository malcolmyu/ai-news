#!/usr/bin/env python3
"""
ai-news Homepage Updater
Regenerates the research section on the homepage to show:
- 1 featured card (newest report)
- 2 list items (next 2 newest reports)
- All other reports go to archive only

Uses HTML comment markers as anchors to avoid matching id="research" in broken HTML.
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
    # Extract category from file content (first <meta name="category"> or fallback)
    cat = ''
    with open(os.path.join(RESEARCH_DIR, f)) as rf:
        content = rf.read()
    cat_m = re.search(r'<meta[^>]*category[^>]*content="([^\"]*)"', content)
    if cat_m:
        cat = cat_m.group(1)
    reports.append((f, mtime, cat))

# Sort newest first
reports.sort(key=lambda x: -x[1])

print(f"Found {len(reports)} reports, sorted by mtime")

# ── Read and update index.html ───────────────────────────────────────
with open(INDEX) as f:
    html = f.read()

# Anchor markers — must be present before and after the research section
MARKER_START = '<!-- HOMEPAGE-RESEARCH-START -->'
MARKER_END = '<!-- HOMEPAGE-RESEARCH-END -->'

# If markers exist, use them; otherwise fall back to id="research" (legacy)
start_pos = html.find(MARKER_START)
end_pos = html.find(MARKER_END)

if start_pos >= 0 and end_pos >= 0:
    before = html[:start_pos + len(MARKER_START)]
    after = html[end_pos:]
else:
    # Legacy fallback — keep working even without markers
    before = html[:html.find('id="research"')]
    after = html[html.find('</section>', html.find('id="research"')) + len('</section>'):]

# Build new research section
entries_html = ''
for i, (fname, mtime, cat) in enumerate(reports[:3]):
    # Extract title from file
    with open(os.path.join(RESEARCH_DIR, fname)) as rf:
        content = rf.read()
    title_m = re.search(r'<title>(.*?)</title>', content)
    title = title_m.group(1).split('—')[0].strip() if title_m else fname.replace('.html','')
    date = datetime.fromtimestamp(mtime).strftime('%Y/%-m/%-d')

    if i == 0:
        # Featured card
        entries_html += f'''<a href="research/{fname}" class="featured-card"><div class="featured-content"><div class="featured-meta"><span class="featured-badge">最新</span><span>{date}</span></div><h3 class="featured-title">{title}</h3><p class="featured-desc">查看完整调研报告</p></div><div class="featured-arrow">→</div></a>'''
    else:
        # List item
        cat_display = f' · {cat}' if cat else ''
        entries_html += f'''<a href="research/{fname}" class="daily-entry"><div class="entry-icon">📊</div><div style="flex:1;"><div style="font-weight:500;font-size:14px;margin-bottom:2px;">{title}</div><div style="font-size:12px;color:var(--text-muted);">{date}{cat_display}</div></div><div style="font-size:16px;color:var(--text-muted);">→</div></a>'''

new_section = f'''
{MARKER_START}
<div class="container">
<div class="section-header-hp">
<div>
<div class="section-label">Research</div>
<h2 class="section-title-hp">深度调研报告</h2>
</div>
<a href="research/archive.html" class="section-link">查看全部 →</a>
</div>
<div style="display:flex;flex-direction:column;gap:10px;">
{entries_html}
</div>
</div>
{MARKER_END}'''

html = before + new_section + after

with open(INDEX, 'w') as f:
    f.write(html)

print("✅ Homepage research section updated!")
if reports:
    print(f"   Featured: {reports[0][0]}")
    for i, (fname, _, _) in enumerate(reports[1:3], 1):
        print(f"   Entry {i}: {fname}")
    print(f"   Others ({len(reports)-3}): only in archive")
