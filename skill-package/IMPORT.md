# AI News Daily - Claude Code Skill Import Guide

This skill automatically generates AI-powered daily news digests from RSS feeds and HTML sources.

## ⚡ Quick Import (Recommended)

Run this command to automatically install the skill:

```bash
# Using curl
curl -fsSL https://raw.githubusercontent.com/malcolmyu/ai-news/main/skill-package/install.sh | bash

# Or clone and install
git clone https://github.com/malcolmyu/ai-news.git
cd ai-news
./skill-package/install.sh
```

## 📦 Manual Installation

### Option 1: Use the packaged tarball

1. **Extract the packaged skill**:
```bash
cd ai-news/skill-package
./package.sh  # Creates ai-news-daily-skill.tar.gz
```

2. **Extract and install**:
```bash
tar -xzf ai-news-daily-skill.tar.gz
cd ai-news-daily-skill-*/
./install.sh
```

### Option 2: Copy from source

```bash
# Copy to Claude Code skills directory
cp -r /path/to/ai-news/skill-package/* ~/.claude/skills/ai-news-daily/

# Copy project files
cp -r /path/to/ai-news/{src,config,templates,requirements.txt,.env.example} ~/.claude/skills/ai-news-daily/

# Install
cd ~/.claude/skills/ai-news-daily
./install.sh
```

### Option 3: Use as standalone project

```bash
cp -r /path/to/ai-news /path/to/my-news-project
cd /path/to/my-news-project
./skill-package/install.sh
```

## ⚙️ Post-Installation Setup

After installation:

### 1. Configure Sources

```bash
cd ~/.claude/skills/ai-news-daily

# Edit sources config
nano config/sources.yaml
```

Add your RSS and HTML sources following the examples in the file.

### 2. Configure API Key

```bash
cp .env.example .env
nano .env
```

Add your OpenRouter API key:
```env
OPENROUTER_API_KEY=your_api_key_here
```

### 3. Test the Installation

```bash
# Run a test (without API calls)
./run.sh --no-summarize --verbose

# Full run with summarization
./run.sh
```

## 🎯 Usage as Claude Code Skill

Once installed, you can invoke the skill in Claude Code by saying:

- "Generate today's AI news digest"
- "Fetch news from my configured sources"
- "Create a news report for March 25, 2026"
- "Update my daily news report"

Claude Code will automatically:
1. Navigate to the skill directory
2. Activate the virtual environment
3. Run the appropriate command
4. Show you the generated report

## 🔄 Daily Automation

### Cron Setup

Add this line to your crontab (run `crontab -e`):

```bash
# Generate news every day at 9:00 AM
0 9 * * * ~/.claude/skills/ai-news-daily/run.sh

# Or with custom output
0 9 * * * ~/.claude/skills/ai-news-daily/run.sh --output ~/news/
```

### LaunchAgent (macOS)

Create `~/Library/LaunchAgents/com.ai-news.daily.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ai-news.daily</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>~/.claude/skills/ai-news-daily/run.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
</dict>
</plist>
```

Then load it:
```bash
launchctl load ~/Library/LaunchAgents/com.ai-news.daily.plist
```

## 📁 Directory Structure After Installation

```
~/.claude/skills/ai-news-daily/
├── SKILL.md                 # Documentation
├── skill.json              # Configuration
├── install.sh              # Installer script
├── run.sh                  # Runner script
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (created after setup)
├── .env.example           # Environment template
├── config/
│   └── sources.yaml       # Your source configuration
├── src/
│   ├── main.py           # Main entry point
│   ├── fetchers/         # RSS and HTML fetchers
│   ├── summarizer.py     # OpenRouter API integration
│   ├── generator.py      # HTML report generation
│   └── __init__.py
├── templates/
│   └── newsletter.html   # HTML report template
├── output/               # Generated reports (created on first run)
└── venv/                 # Python virtual environment (created by install.sh)
```

## 🛠️ Troubleshooting

### Permission Denied
```bash
chmod +x ~/.claude/skills/ai-news-daily/run.sh
chmod +x ~/.claude/skills/ai-news-daily/install.sh
```

### Import Errors
```bash
cd ~/.claude/skills/ai-news-daily
source venv/bin/activate
pip install -r requirements.txt
```

### No Articles Found
- Check `config/sources.yaml` for correct URLs
- Use `--verbose` flag to see detailed logs
- Test sources with `--no-summarize` for faster debugging
- Verify sources are still active and have recent content

### API Errors
- Check OpenRouter API key in `.env`
- Verify account has sufficient credits
- Try `--no-summarize` to isolate API issues

## 📊 Usage Statistics

The skill tracks API usage:
- Successful/failed requests
- Token consumption
- Articles processed

View logs with `--verbose` flag or check:
- Output files: `output/ai-news-YYYY-MM-DD.html`
- Logs: Displayed in console during execution

## 🚀 Advanced Usage

### Custom Templates

Edit `templates/newsletter.html` to customize report appearance:
- Colors and fonts
- Layout and spacing
- Article card design
- Dark mode styling

### Multiple Configurations

Create different configurations for different purposes:

```bash
# Tech news only
cp config/sources.yaml config/tech-sources.yaml
# Edit to include only tech sources
./run.sh --config config/tech-sources.yaml --output output/tech-news/

# AI research only
cp config/sources.yaml config/research-sources.yaml
# Edit to include only research sources
./run.sh --config config/research-sources.yaml --output output/ai-research/
```

### Integration with Other Tools

The generated HTML can be:
- Converted to PDF with `pandoc`
- Sent via email with `mailutils`
- Uploaded to cloud storage with `rclone`
- Posted to Slack/Discord via webhooks

## 🔒 Security Notes

- API keys are stored in `.env` (not committed to git)
- Keep your `.env` file secure and don't share it
- The skill only reads from public RSS/HTML sources
- No personal data is collected or transmitted

## 📝 Version History

- **v1.0.0**: Initial release
  - RSS/Atom feed support
  - HTML page scraping
  - AI summarization with OpenRouter
  - Formatted HTML output
  - Configurable sources and limits

---

**Enjoy your automated AI news digest! 🤖📰**
