# AI News Daily - Claude Code Skill Package

**Generate AI-powered daily news digests from RSS feeds and HTML sources.**

## 📦 Package Contents

This directory contains all files needed to package the AI News Daily project as a Claude Code skill:

### Documentation
- **SKILL.md** - Main skill documentation
- **IMPORT.md** - Detailed installation instructions
- **USAGE.md** - Quick usage guide
- **README.md** - Project overview

### Installation Scripts
- **install.sh** - Automated installation script
- **package.sh** - Creates distributable packages

### Configuration
- **skill.json** - Skill metadata and configuration

## 🚀 Quick Start

### Install the skill (automated):
```bash
cd skill-package
./install.sh
```

### Create a distributable package:
```bash
./package.sh  # Creates .tar.gz and .zip files
```

### Manual installation:
```bash
cp -r ../../{src,config,templates,requirements.txt,.env.example,..} ~/.claude/skills/ai-news-daily/
cp * ~/.claude/skills/ai-news-daily/
```

## 📁 Project Structure

After installation, the skill is located at: `~/.claude/skills/ai-news-daily/`

```
ai-news-daily/
├── SKILL.md              # This documentation
├── skill.json            # Skill configuration
├── install.sh            # Installation script
├── run.sh                # Runner script (generated)
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
├── .env.example          # Environment template
├── config/
│   └── sources.yaml     # Source configuration
├── src/
│   ├── main.py         # Main entry point
│   ├── fetchers/       # RSS and HTML fetchers
│   ├── summarizer.py   # OpenRouter API integration
│   └── generator.py    # HTML report generation
├── templates/
│   └── newsletter.html # HTML template
├── output/             # Generated reports
└── venv/               # Python virtual environment
```

## 📖 Full Documentation

See the following files for detailed information:

- **SKILL.md** - Complete skill documentation, usage examples, configuration
- **IMPORT.md** - Step-by-step installation guide with multiple methods
- **USAGE.md** - Quick reference for common tasks and commands
- **README.md** - Project overview and basic information

## 💡 How to Use

### In Claude Code:

Tell Claude what you want:

> "Generate today's AI news digest"

Claude will:
1. Navigate to the skill directory
2. Activate the virtual environment
3. Run the command with appropriate options
4. Show you the results

### Direct command:

```bash
~/.claude/skills/ai-news-daily/run.sh
```

Or if added to PATH:
```bash
ai-news
```

## 🛠️ Development

To develop or modify the skill:

1. Edit source files in `src/`
2. Update configuration in `config/`
3. Test with: `./run.sh --verbose --no-summarize`
4. Package with: `./package.sh`

## 📦 Distribution

To share this skill:

1. Run `./package.sh` to create distributable files
2. Share the generated `.tar.gz` or `.zip` file
3. Recipients can extract and run `./install.sh`

## 🔄 Updates

To update the skill:

```bash
cd ~/.claude/skills/ai-news-daily
git pull  # If cloned from git
./install.sh  # Re-run to update dependencies
```

## 📝 Notes

- Each source is limited to max 3 articles (RSS) or 2 articles (HTML)
- Requires OpenRouter API key for summarization
- Generated reports are HTML format with responsive design
- Supports both light and dark modes
- Cron-ready for daily automation

## 🔧 Customization

- Edit `config/sources.yaml` to add/remove sources
- Modify `templates/newsletter.html` to change appearance
- Update `src/summarizer.py` to change AI model or prompt
- Adjust article limits in source configuration

## 📊 Features Implemented

✅ RSS/Atom feed parsing
✅ HTML page scraping with CSS selectors
✅ AI-powered summarization (OpenRouter)
✅ Formatted HTML reports
✅ Category organization
✅ Date filtering (last 3 days)
✅ Article volume control
✅ Responsive design
✅ Dark mode support
✅ Cron automation ready
✅ Comprehensive logging
✅ Error handling and retries

## 🎯 Limitations

- HTML scraping may not work with heavily JavaScript-based sites
- API usage costs depend on OpenRouter pricing
- Date parsing depends on source format consistency
- Maximum articles per source enforced to control costs

## 📞 Support

For issues or feature requests:
- Check `USAGE.md` for troubleshooting
- Review logs with `--verbose` flag
- Verify API keys and source URLs
- Check internet connectivity

---

**AI News Daily - Your automated news digest generator! 🤖📰**
