# AI News Daily - Claude Code Skill

Automated AI-powered daily news digest generator.

## Quick Start

1. **Copy this directory** to Claude Code skills location:
```bash
cp -r /path/to/ai-news/skill-package/* ~/.claude/skills/ai-news-daily/
```

2. **Install the skill**:
```bash
cd ~/.claude/skills/ai-news-daily
./install.sh
```

3. **Configure**:
```bash
cd ~/.claude/skills/ai-news-daily
# Edit config/sources.yaml to add your RSS/HTML sources
cp config/sources.yaml config/sources.yaml.backup
# Add your sources

# Configure environment
cp .env.example .env
# Add your OpenRouter API key to .env
```

## Usage in Claude Code

Simply use the skill by describing what you want:

```
"Generate today's AI news digest"

"Create a news report for March 25, 2026"

"Fetch news from my configured sources and save to /tmp"
```

Or use direct commands:

```bash
# Navigate to skill directory
cd ~/.claude/skills/ai-news-daily

# Run directly
./run.sh

# With options
./run.sh --date 2026-03-25 --verbose
./run.sh --no-summarize  # Skip AI summarization (faster)
./run.sh --output /tmp/my-news
```

## Directory Structure

```
ai-news-daily/
├── SKILL.md                 # Skill documentation
├── skill.json              # Skill configuration
├── install.sh              # Installation script
├── requirements.txt        # Python dependencies
├── config/
│   └── sources.yaml       # Source configuration
├── src/
│   ├── main.py           # Main entry point
│   ├── fetchers/         # RSS and HTML fetchers
│   ├── summarizer.py     # OpenRouter API integration
│   └── generator.py      # HTML report generation
└── output/              # Generated reports
```

## Adding to Claude Code Session

If you want to use the AI news generator in your current Claude Code session:

```bash
# From any directory, run the skill
~/.claude/skills/ai-news-daily/run.sh

# Or add to PATH for easier access
ln -s ~/.claude/skills/ai-news-daily/run.sh ~/bin/ai-news
```

## Automation

### Daily Cron Job

Add to your crontab:
```bash
0 9 * * * ~/.claude/skills/ai-news-daily/run.sh
```

### Weekly Report

```bash
# Every Monday at 9 AM
0 9 * * 1 ~/.claude/skills/ai-news-daily/run.sh --date $(date -d 'last monday' +%Y-%m-%d)
```

## Configuration Examples

### Tech News Sources

```yaml
rss_sources:
  - name: "TechCrunch"
    url: "https://techcrunch.com/feed/"
    category: "Tech News"
    max_articles: 3

  - name: "Verge"
    url: "https://www.theverge.com/rss/index.xml"
    category: "Tech News"
    max_articles: 3

html_sources:
  - name: "OpenAI Blog"
    url: "https://openai.com/blog"
    category: "AI Research"
    max_articles: 2
    selectors:
      link: "a[href*='/blog/']"
```

### AI Research Sources

```yaml
rss_sources:
  - name: "arXiv AI"
    url: "http://arxiv.org/rss/cs.AI"
    category: "AI Research"
    max_articles: 3

  - name: "Papers With Code"
    url: "https://paperswithcode.com/rss.xml"
    category: "AI Research"
    max_articles: 3
```

## Troubleshooting

### Permission Denied

```bash
chmod +x ~/.claude/skills/ai-news-daily/run.sh
chmod +x ~/.claude/skills/ai-news-daily/install.sh
chmod +x ~/.claude/skills/ai-news-daily/src/main.py
```

### Virtual Environment Issues

```bash
cd ~/.claude/skills/ai-news-daily
rm -rf venv
./install.sh
```

### No Articles Found

- Check your sources in `config/sources.yaml`
- Verify date range in settings
- Use `--verbose` flag to see detailed logs
- Test individual sources with `--no-summarize` for faster debugging

## Updates

To update the skill:

```bash
cd ~/.claude/skills/ai-news-daily
# backup your config
cp config/sources.yaml ~/sources-backup.yaml
# pull latest changes
git pull
# restore your config
cp ~/sources-backup.yaml config/sources.yaml
```

## Support

For issues and feature requests, please create an issue in the project repository.
