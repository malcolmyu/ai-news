#!/usr/bin/env python3
"""Fix old daily pages: replace header, update title, add search components."""
import re, sys, os

DAILY_HEADER = '''<header class="header" data-pagefind-ignore>
<div class="container">
<div class="header-inner">
<a href="../index.html" class="logo">
<div class="logo-icon">🤖</div>
<span class="logo-text">第二号</span>
</a>
<nav class="nav">
<a href="../index.html" class="nav-link">首页</a>
<a href="archive.html" class="nav-link">AI 日报</a>
<a href="../research/archive.html" class="nav-link">深度调研</a>
</nav>
<button class="search-trigger" type="button" data-search-open aria-haspopup="dialog" aria-controls="search-modal">
<span class="search-trigger-icon">⌕</span>
<span class="search-trigger-label">Search</span>
<kbd>⌘K</kbd>
</button>
</div>
</div>
</header>'''

DAILY_SEARCH_MODAL = '''<div class="search-modal" id="search-modal" aria-hidden="true" data-pagefind-ignore>
<div class="search-modal-backdrop" data-search-close></div>
<div class="search-dialog" role="dialog" aria-modal="true" aria-labelledby="search-dialog-title">
<div class="search-dialog-head">
<div>
<div class="search-dialog-label">Search</div>
<h2 id="search-dialog-title">搜索第二号知识库</h2>
</div>
<button class="search-close" type="button" data-search-close aria-label="关闭搜索">×</button>
</div>
<div class="search-dialog-meta">
<span>AI 日报</span>
<span>深度调研</span>
<span>思维模型</span>
<span class="search-shortcut">Esc 关闭</span>
</div>
<div id="site-search" class="site-search"></div>
</div>
</div>'''

SEARCH_HEAD = '''<link rel="stylesheet" href="../pagefind/pagefind-ui.css">
<script src="../pagefind/pagefind-ui.js" defer></script>
<script src="../search.js" defer></script>
<script src="../site.js" defer></script>
'''

RESEARCH_HEADER = '''<header class="header" data-pagefind-ignore>
<div class="container">
<div class="header-inner">
<a href="../index.html" class="logo">
<div class="logo-icon">🤖</div>
<span class="logo-text">第二号</span>
</a>
<nav class="nav">
<a href="../index.html" class="nav-link">首页</a>
<a href="../daily/archive.html" class="nav-link">AI 日报</a>
<a href="archive.html" class="nav-link">深度调研</a>
</nav>
<button class="search-trigger" type="button" data-search-open aria-haspopup="dialog" aria-controls="search-modal">
<span class="search-trigger-icon">⌕</span>
<span class="search-trigger-label">Search</span>
<kbd>⌘K</kbd>
</button>
</div>
</div>
</header>'''

def process_old_daily(filepath):
    with open(filepath) as f:
        content = f.read()
    
    if '返回首页' not in content[:2000]:
        return False
    
    date_match = re.search(r'ai-news-(\d{4}-\d{2}-\d{2})', filepath)
    if not date_match:
        return False
    date = date_match.group(1)
    
    # Title
    content = re.sub(r'<title>[^<]*</title>', f'<title>{date} 日报 — 第二号</title>', content)
    # Old header
    content = re.sub(r'<header class="header">.*?</header>', DAILY_HEADER, content, flags=re.DOTALL)
    # Search head
    if 'pagefind' not in content[:1000]:
        content = re.sub(r'(</head>)', SEARCH_HEAD + r'\1', content)
    # Search modal
    if 'search-modal' not in content:
        content = re.sub(r'(</body>)', DAILY_SEARCH_MODAL + r'\1', content)
    
    with open(filepath, 'w') as f:
        f.write(content)
    return True

def process_research(filepath):
    with open(filepath) as f:
        content = f.read()
    
    if '<div class="nav-back">' not in content[:500]:
        return False
    
    # Remove nav-back
    content = re.sub(r'<div class="nav-back"><a href="\.\./index\.html">← 返回首页</a></div>\s*', '', content)
    # Add header after <body>
    content = re.sub(r'(<body>)', r'\1\n' + RESEARCH_HEADER, content)
    # Search head
    if 'pagefind' not in content[:1000]:
        content = re.sub(r'(</head>)', SEARCH_HEAD + r'\1', content)
    # Search modal
    if 'search-modal' not in content:
        content = re.sub(r'(</body>)', DAILY_SEARCH_MODAL + r'\1', content)
    
    with open(filepath, 'w') as f:
        f.write(content)
    return True

if __name__ == '__main__':
    daily_dir = '/Users/yuminghao/Work/ai-news/docs/daily'
    research_dir = '/Users/yuminghao/Work/ai-news/docs/research'
    
    # Old daily files
    count = 0
    for f in sorted(os.listdir(daily_dir)):
        if f.startswith('ai-news-2026-') and f.endswith('.html'):
            if process_old_daily(os.path.join(daily_dir, f)):
                count += 1
                print(f"  daily: {f}")
    print(f"Old daily files processed: {count}")
    
    # Research files
    count = 0
    for f in sorted(os.listdir(research_dir)):
        if f.endswith('.html') and f != 'archive.html':
            if process_research(os.path.join(research_dir, f)):
                count += 1
                print(f"  research: {f}")
    print(f"Research files processed: {count}")
