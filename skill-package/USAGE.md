# AI News Daily - Quick Usage Guide

## Quick Start for Claude Code

### Option 1: Use Claude Code to install

Tell Claude Code:

> "Please install the ai-news-daily skill from the skill-package directory"

Claude will:
1. Read the skill configuration
2. Copy files to Claude Code skills directory
3. Set up the environment
4. Run a test to verify everything works

### Option 2: Manual Installation

1. **Copy files to Claude Code skills**:
```bash
cd ai-news/skill-package
mkdir -p ~/.claude/skills/ai-news-daily
cp -r ../../{src,config,templates,requirements.txt,.env.example,..} ~/.claude/skills/ai-news-daily/
cp * ~/.claude/skills/ai-news-daily/
```

2. **Install dependencies**:
```bash
cd ~/.claude/skills/ai-news-daily
./install.sh
```

3. **Configure sources**:
```bash
# Edit config/sources.yaml and add your RSS/HTML sources
nano config/sources.yaml
```

4. **Add API key**:
```bash
cp .env.example .env
nano .env  # Add your OpenRouter API key
```

## Usage Examples in Claude Code

Once installed, you can invoke the skill by saying:

### Basic Usage

1. **Generate today's news**:
> "Generate today's AI news digest"

2. **Check news without summarization**:
> "Fetch today's news but don't summarize (for testing)"

3. **Specific date**:
> "Create a news report for March 25, 2026"

### Advanced Usage

4. **Custom output location**:
> "Generate today's news and save to /tmp/news.html"

5. **Verbose mode for debugging**:
> "Generate today's news with verbose logging"

6. **Use different config**:
> "Generate news using my tech-sources.yaml config"

### Automation

7. **Set up daily cron job**:
> "Help me create a cron job to run this every day at 9 AM"

## Direct Commands (if added to PATH)

```bash
# Generate today's news
ai-news

# Specific date
ai-news --date 2026-03-25

# Verbose mode
ai-news --verbose

# Skip summarization (faster)
ai-news --no-summarize

# Custom output
ai-news --output ~/Documents/news.html
```

## Common Workflows

### Setup Workflow
1. Install skill
2. Edit config/sources.yaml
3. Add API key to .env
4. Test: `ai-news --no-summarize --verbose`
5. Full run: `ai-news`

### Daily Workflow
Just tell Claude: "Create today's news digest"

### Maintenance Workflow
1. Check logs: `ai-news --verbose`
2. Update sources: Edit config/sources.yaml
3. Test new sources: `ai-news --no-summarize`
4. Full run: `ai-news`

## Troubleshooting

### "Skill not found"
- Make sure files are in ~/.claude/skills/ai-news-daily/
- Run ./install.sh to set up

### "Module not found"
- Activate venv: `source venv/bin/activate`
- Or run via ./run.sh which handles activation

### "No articles found"
- Check if sources are active in config/sources.yaml
- Verify internet connection
- Use --verbose to see detailed logs

### "API errors"
- Check .env for correct API key
- Verify OpenRouter account has credits
- Try --no-summarize to isolate API issues

## File Locations

After installation:
- Skill dir: ~/.claude/skills/ai-news-daily/
- Config: ~/.claude/skills/ai-news-daily/config/sources.yaml
- .env: ~/.claude/skills/ai-news-daily/.env
- Output: ~/.claude/skills/ai-news-daily/output/
- Virtual env: ~/.claude/skills/ai-news-daily/venv/

## Tips

1. **Start small**: Add 2-3 sources first, test, then add more
2. **Use categories**: Organize sources by topic (Tech, AI, Research, etc.)
3. **Limit articles**: Keep max_articles low (2-3) to control API costs
4. **Monitor usage**: Check API usage in OpenRouter dashboard
5. **Backup config**: Keep a backup of your sources.yaml
6. **Test first**: Use --no-summarize when testing new sources

## AI-Generated Commands

Tell Claude Code what you want to do in natural language:

- "Give me today's AI news summary"
- "Fetch and summarize news from my RSS feeds"
- "Create a news digest without AI summaries (for testing)"
- "Show me yesterday's news report"
- "Check which sources are working properly"

Claude will generate and execute the appropriate commands.
