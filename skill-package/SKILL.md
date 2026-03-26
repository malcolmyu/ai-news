---
name: ai-news-daily
description: Generate AI daily news digest by fetching RSS feeds and HTML pages, summarizing articles with OpenRouter API, and producing formatted HTML reports.
---

# AI News Daily Generator

Automatically fetches content from RSS feeds and HTML pages, generates AI-powered summaries using OpenRouter API, and creates formatted HTML daily reports.

## Features

- 📰 **RSS/Atom Feed Support**: Fetches articles from RSS/Atom feeds with date filtering
- 🌐 **HTML Page Scraping**: Extracts articles from HTML pages using CSS selectors
- 🤖 **AI Summarization**: Uses OpenRouter API to generate concise Chinese summaries
- 📊 **Formatted Reports**: Generates beautiful HTML reports organized by category
- ⚙️ **Configurable Sources**: Manage sources via YAML configuration
- 📝 **Category Support**: Automatically categorizes and groups articles
- 🔗 **Source Links**: Preserves original article links for easy access
- 📅 **Date Filtering**: Fetches only recent articles (configurable days range)
- 🔢 **Volume Control**: Limits articles per source to control output size

## Installation

1. **Copy the ai-news project** to your workspace:
```bash
git clone <repository-url>
cd ai-news
```

2. **Install dependencies**:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env and add your OpenRouter API key
```

4. **Configure sources**:
Edit `config/sources.yaml` to add/remove RSS and HTML sources

## Usage

### Generate Daily News

```bash
# Activate virtual environment
source venv/bin/activate

# Generate today's news
python src/main.py

# Generate news for specific date
python src/main.py --date 2026-03-25

# Skip summarization (faster, for testing)
python src/main.py --no-summarize

# Enable verbose logging
python src/main.py --verbose

# Custom output directory
python src/main.py --output /path/to/output

# Custom config file
python src/main.py --config custom/config.yaml
```

### Cron Job Setup

Add to crontab for daily automated generation:

```bash
# Run every day at 9 AM
0 9 * * * cd /path/to/ai-news && source venv/bin/activate && python src/main.py
```

## Configuration

### Global Settings (config/sources.yaml)

```yaml
settings:
  fetch_timeout: 30           # HTTP timeout in seconds
  max_retries: 3              # Retry attempts for failed requests
  summary_max_length: 200     # Summary length in characters
  summary_model: "anthropic/claude-3-sonnet"  # AI model for summarization
  publish_date_within_days: 3 # Fetch articles from last N days
  output_dir: "output"        # Output directory
  template_file: "templates/newsletter.html"  # HTML template
```

### Source Configuration

#### RSS Sources

```yaml
rss_sources:
  - name: "Source Name"        # Display name
    url: "https://.../feed.xml" # RSS/Atom URL
    category: "Category"       # Article category
    enabled: true              # Enable/disable
    max_articles: 3            # Max articles to fetch (per source)
```

#### HTML Sources

```yaml
html_sources:
  - name: "Blog Name"          # Display name
    url: "https://.../blog"    # Page URL
    description: "Description" # Optional description
    category: "Category"       # Article category
    enabled: true              # Enable/disable
    max_articles: 2            # Max articles to fetch (per source)
    selectors:                 # CSS selectors
      link: "a[href*='/blog/']"   # Link selector (required)
      # Or use detailed selectors:
      container: "main"           # Container element
      article: "article"          # Article elements
      title: "h2"                 # Title element
      link: "a"                   # Link element
      date: "time"                # Date element (optional)
```

**Important**: HTML sources are limited to max 2 articles per source to control volume

## Output Example

The generated HTML report includes:

- **Header**: Report title, generation date, article count
- **Sections by Category**: Articles grouped by category
- **Article Cards**: Title, summary, source, link
- **Responsive Design**: Works on desktop and mobile
- **Dark Mode Support**: Automatic dark mode based on system preference

Example article card:
```html
<div class="news-card">
    <div class="news-header">
        <h3 class="news-title">Article Title</h3>
        <span class="news-source">Source Name</span>
    </div>
    <p class="news-summary">AI-generated summary of the article...</p>
    <a href="https://original-article.com" class="news-link" target="_blank">
        Read Original →
    </a>
</div>
```

## Supported HTML Source Patterns

The system supports two HTML scraping modes:

### 1. Link-based Extraction (Recommended)

For sites with clear link patterns:

```yaml
selectors:
  link: "a[href*='/blog/']"  # Selects all links containing /blog/
```

### 2. Element-based Extraction

For traditional blog layouts:

```yaml
selectors:
  container: "main"          # Optional: container element
  article: "article"         # Article element selector
  title: "h2"               # Title element selector
  link: "a"                 # Link element selector
  date: "time"              # Optional: date element selector
```

## Troubleshooting

### RSS Feed Issues

1. **Invalid feed format**: Check if URL returns valid RSS/Atom XML
2. **Date parsing errors**: Some feeds use non-standard date formats
3. **Connection timeouts**: Increase `fetch_timeout` in settings

### HTML Scraping Issues

1. **Dynamic content**: Sites using heavy JavaScript may not work (use RSS if available)
2. **Selector not working**: Use browser dev tools to inspect element selectors
3. **Rate limiting**: Add delays or use proxy for high-frequency scraping

### API Issues

1. **OpenRouter errors**: Check API key and account balance
2. **Rate limiting**: System uses tenacity for automatic retries
3. **Model availability**: Try different models if one is unavailable

### Common Solutions

- **No articles fetched**: Check date range and source filters
- **Old articles included**: Verify date parsing and timezone handling
- **Missing summaries**: Check OpenRouter API status and quotas

## Requirements

```
feedparser==6.0.11
requests==2.31.0
beautifulsoup4==4.12.2
openai==1.54.0
jinja2==3.1.2
pyyaml==6.0.1
python-dotenv==1.0.0
lxml>=6.0.2
markdown==3.5.1
tenacity>=8.0.0
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | OpenRouter API key | Required |
| `OPENROUTER_BASE_URL` | API base URL | `https://openrouter.ai/api/v1` |
| `OPENROUTER_MODEL` | AI model | `anthropic/claude-3-sonnet` |
| `API_TIMEOUT` | API request timeout | `60` |

## License

MIT License
