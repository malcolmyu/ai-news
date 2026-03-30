"""
HomepageBuilderAgent - Dynamic homepage generation and content aggregation.

This module provides:
- Dynamic content aggregation from all agents
- Statistics generation and trend analysis
- SEO optimization and performance tuning
- Multi-device responsive design
- Template-based page generation with Harness integration
"""

from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime, timedelta
import json
import re
import logging
from dataclasses import dataclass, asdict
import hashlib

try:
    from ..harness.controller import HarnessController
    from ..harness.templates import TemplateManager
    from ..harness.styles import StyleConstraints
except ImportError:
    # Direct import for standalone execution
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from harness.controller import HarnessController
    from harness.templates import TemplateManager
    from harness.styles import StyleConstraints

logger = logging.getLogger(__name__)


@dataclass
class HomePageStats:
    """Homepage statistics data structure."""
    daily_total: int = 0
    daily_today: int = 0
    daily_this_week: int = 0
    daily_this_month: int = 0
    research_total: int = 0
    research_by_category: Dict[str, int] = None
    thinking_total: int = 0
    thinking_active: int = 0
    keywords_cloud: List[Dict[str, Any]] = None
    trends_30days: List[Dict[str, Any]] = None
    generation_time: str = ""
    last_updated: str = ""


@dataclass
class ContentFeed:
    """Content feed data structure."""
    daily_latest: Optional[Dict[str, Any]] = None
    daily_highlights: List[Dict[str, Any]] = None
    research_latest: List[Dict[str, Any]] = None
    research_featured: List[Dict[str, Any]] = None
    thinking_latest: List[Dict[str, Any]] = None
    thinking_featured: List[Dict[str, Any]] = None
    updates: Optional[Dict[str, Any]] = None


class HomepageBuilderAgent:
    """
    Homepage builder agent for dynamic content aggregation and page generation.

    This agent integrates with all other agents to collect latest content,
    generate comprehensive statistics, and produce optimized homepage HTML.
    """

    def __init__(self, harness: HarnessController):
        """
        Initialize HomepageBuilderAgent.

        Args:
            harness: HarnessController instance for style and template management
        """
        self.harness = harness
        self.data_dir = Path("data")
        self.output_dir = Path("output")
        self.docs_dir = Path("docs")

        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        self.docs_dir.mkdir(exist_ok=True)

        # Subdirectories
        (self.data_dir / "daily").mkdir(exist_ok=True)
        (self.data_dir / "research").mkdir(exist_ok=True)
        (self.data_dir / "thinking").mkdir(exist_ok=True)
        (self.data_dir / "homepage").mkdir(exist_ok=True)

        self.template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}} - 个人自主成长网站系统</title>
    <meta name="description" content="{{meta_description}}">
    <meta name="keywords" content="{{meta_keywords}}">
    <meta name="author" content="AI News System">
    <meta name="robots" content="index, follow">

    <!-- Open Graph -->
    <meta property="og:title" content="{{og_title}}">
    <meta property="og:description" content="{{og_description}}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{{og_url}}">
    <meta property="og:image" content="{{og_image}}">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{{twitter_title}}">
    <meta name="twitter:description" content="{{twitter_description}}">
    <meta name="twitter:image" content="{{twitter_image}}">

    <!-- Preconnect and DNS prefetch -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="dns-prefetch" href="https://fonts.googleapis.com">
    <link rel="dns-prefetch" href="https://fonts.gstatic.com">

    <!-- Critical CSS -->
    <style>
    {{{critical_css}}}
    </style>

    <!-- Stylesheets -->
    <link rel="stylesheet" href="/assets/css/main.css" media="print" onload="this.media='all'">
    <noscript><link rel="stylesheet" href="/assets/css/main.css"></noscript>

    <!-- Structured Data -->
    <script type="application/ld+json">
    {{{structured_data}}}
    </script>
</head>
<body>
    <!-- Header -->
    <header class="header glass-effect">
        <nav class="nav container">
            <div class="logo">
                <a href="/" class="text-gradient font-bold text-xl">Growth System</a>
            </div>
            <ul class="nav-menu">
                <li><a href="#daily" class="nav-link">日报</a></li>
                <li><a href="#research" class="nav-link">调研</a></li>
                <li><a href="#thinking" class="nav-link">思考</a></li>
                <li><a href="#stats" class="nav-link">统计</a></li>
            </ul>
            <button class="mobile-menu-toggle" aria-label="Toggle menu">
                <span></span>
                <span></span>
                <span></span>
            </button>
        </nav>
    </header>

    <!-- Hero Section -->
    <section id="hero" class="hero-section">
        <div class="container">
            <div class="hero-content text-center">
                <h1 class="hero-title text-gradient">个人自主成长网站系统</h1>
                <p class="hero-subtitle">基于AI日报生成、深度调研、思考模型沉淀的统一平台</p>
                <div class="hero-stats grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
                    <div class="stat-item">
                        <div class="stat-number">{{daily_total}}</div>
                        <div class="stat-label">日报总数</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{{research_total}}</div>
                        <div class="stat-label">调研报告</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{{thinking_total}}</div>
                        <div class="stat-label">思考模型</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{{today_items}}</div>
                        <div class="stat-label">今日新增</div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Daily Section -->
    <section id="daily" class="section">
        <div class="container">
            <div class="section-header text-center mb-12">
                <h2 class="section-title text-gradient">最新日报</h2>
                <p class="section-subtitle">AI生成的最新技术资讯</p>
            </div>
            {{{daily_content}}}
        </div>
    </section>

    <!-- Research Section -->
    <section id="research" class="section bg-neutral-50">
        <div class="container">
            <div class="section-header text-center mb-12">
                <h2 class="section-title text-gradient">调研报告</h2>
                <p class="section-subtitle">深度调研分析</p>
            </div>
            {{{research_content}}}
        </div>
    </section>

    <!-- Thinking Section -->
    <section id="thinking" class="section">
        <div class="container">
            <div class="section-header text-center mb-12">
                <h2 class="section-title text-gradient">思考模型</h2>
                <p class="section-subtitle">体系化思考沉淀</p>
            </div>
            {{{thinking_content}}}
        </div>
    </section>

    <!-- Stats Section -->
    <section id="stats" class="section bg-neutral-50">
        <div class="container">
            <div class="section-header text-center mb-12">
                <h2 class="section-title text-gradient">数据统计</h2>
                <p class="section-subtitle">系统运行状况一览</p>
            </div>
            {{{stats_content}}}
        </div>
    </section>

    <!-- Footer -->
    <footer class="footer glass-effect">
        <div class="container">
            <div class="footer-content">
                <p>&copy; 2026 AI News System. Generated at {{last_updated}}</p>
                <p class="text-sm text-neutral-500">Powered by Growth Website System</p>
            </div>
        </div>
    </footer>

    <!-- Scripts -->
    <script src="/assets/js/main.js" defer></script>
</body>
</html>
"""

        logger.info("HomepageBuilderAgent initialized")

    def build_homepage(self, updates: Optional[Dict[str, Any]] = None) -> str:
        """
        Main method: Build complete homepage.

        Args:
            updates: Optional dictionary containing updates for specific sections

        Returns:
            Complete HTML string for homepage
        """
        logger.info("Starting homepage build process")
        start_time = datetime.now()

        # 1. Collect latest content from all sources
        content_feed = self.get_latest_content()
        if updates:
            content_feed.updates = updates

        # 2. Generate comprehensive statistics
        stats = self.generate_stats()
        stats.generation_time = (datetime.now() - start_time).total_seconds()

        # 3. Build HTML sections
        html_data = {
            "title": "AI News System",
            "meta_description": "Personal Growth Website System powered by AI News",
            "meta_keywords": "AI News, Growth, Research, Thinking Models",
            "og_title": "AI News System - Personal Growth Website",
            "og_description": "Comprehensive AI-powered news and research platform",
            "og_url": "https://example.com",
            "og_image": "/assets/images/hero.jpg",
            "twitter_title": "AI News System",
            "twitter_description": "AI News and Research Platform",
            "twitter_image": "/assets/images/hero.jpg",
            "critical_css": self.get_critical_css(),
            "structured_data": self.generate_structured_data(stats),
            "last_updated": datetime.now().isoformat(),
            "daily_content": self.build_daily_section(content_feed),
            "research_content": self.build_research_section(content_feed),
            "thinking_content": self.build_thinking_section(content_feed),
            "stats_content": self.build_stats_section(stats),
            **asdict(stats)
        }

        # 4. Calculate today items for hero stats
        html_data["today_items"] = stats.daily_today + sum(
            stats.research_by_category.values() if stats.research_by_category else []
        ) + stats.thinking_today if hasattr(stats, 'thinking_today') else 0

        # 5. Render final HTML
        html = self.render_template(html_data)

        # 6. Apply optimizations
        html = self.optimize_for_seo(html, stats)
        html = self.optimize_performance(html)

        # 7. Save to files
        self.save_html(html)

        # 8. Save feed data
        self.save_feed(content_feed, stats)

        logger.info(f"Homepage build completed in {stats.generation_time:.2f}s")
        return html

    def get_latest_content(self) -> ContentFeed:
        """
        Get latest content from all data sources.

        Returns:
            ContentFeed object with latest content
        """
        feed = ContentFeed()

        # Get latest daily report
        daily_data = self.get_latest_daily()
        if daily_data:
            feed.daily_latest = daily_data
            feed.daily_highlights = daily_data.get("articles", [])[:3]

        # Get latest research reports
        research_data = self.get_latest_research()
        if research_data:
            feed.research_latest = research_data[:6]  # Latest 6
            feed.research_featured = research_data[:3]  # Featured 3

        # Get latest thinking models
        thinking_data = self.get_latest_thinking()
        if thinking_data:
            feed.thinking_latest = thinking_data[:6]  # Latest 6
            feed.thinking_featured = thinking_data[:3]  # Featured 3

        logger.info(f"Collected content: {len(feed.daily_highlights or [])} daily, {len(feed.research_latest or [])} research, {len(feed.thinking_latest or [])} thinking")
        return feed

    def get_latest_daily(self) -> Optional[Dict[str, Any]]:
        """Get the latest daily report from archives."""
        try:
            archives_file = self.data_dir / "daily" / "archives.json"
            if not archives_file.exists():
                return None

            with open(archives_file, 'r', encoding='utf-8') as f:
                archives = json.load(f)

            if not archives or "reports" not in archives:
                return None

            # Get latest report
            latest = max(archives["reports"], key=lambda x: x.get("date", ""))

            # Load full report if available
            if "file_path" in latest:
                report_file = self.data_dir / latest["file_path"]
                if report_file.exists():
                    with open(report_file, 'r', encoding='utf-8') as f:
                        latest["content"] = f.read()

            return latest

        except Exception as e:
            logger.error(f"Failed to get latest daily: {e}")
            return None

    def get_latest_research(self) -> List[Dict[str, Any]]:
        """Get latest research reports."""
        try:
            index_file = self.data_dir / "research" / "index.json"
            if not index_file.exists():
                return []

            with open(index_file, 'r', encoding='utf-8') as f:
                research_index = json.load(f)

            return research_index.get("reports", [])[:10]  # Get latest 10

        except Exception as e:
            logger.error(f"Failed to get latest research: {e}")
            return []

    def get_latest_thinking(self) -> List[Dict[str, Any]]:
        """Get latest thinking models."""
        try:
            models_file = self.data_dir / "thinking" / "models.json"
            if not models_file.exists():
                return []

            with open(models_file, 'r', encoding='utf-8') as f:
                models_index = json.load(f)

            return models_index.get("models", [])[:10]  # Get latest 10

        except Exception as e:
            logger.error(f"Failed to get latest thinking: {e}")
            return []

    def generate_stats(self) -> HomePageStats:
        """
        Generate comprehensive statistics.

        Returns:
            HomePageStats object with all statistics
        """
        stats = HomePageStats()
        stats.last_updated = datetime.now().isoformat()

        # Daily stats
        try:
            archives_file = self.data_dir / "daily" / "archives.json"
            if archives_file.exists():
                with open(archives_file, 'r', encoding='utf-8') as f:
                    archives = json.load(f)

                stats.daily_total = len(archives.get("reports", []))

                today = datetime.now().strftime("%Y-%m-%d")
                today_count = sum(1 for r in archives.get("reports", []) if r.get("date") == today)
                stats.daily_today = today_count

                # Week and month stats
                now = datetime.now()
                week_ago = now - timedelta(days=7)
                month_ago = now - timedelta(days=30)

                for report in archives.get("reports", []):
                    report_date = datetime.strptime(report.get("date", "1970-01-01"), "%Y-%m-%d")
                    if report_date >= week_ago:
                        stats.daily_this_week += 1
                    if report_date >= month_ago:
                        stats.daily_this_month += 1

                # Keywords from daily reports
                all_keywords = []
                for report in archives.get("reports", []):
                    if "keywords" in report:
                        all_keywords.extend(report["keywords"])

                # Generate keyword cloud
                keyword_counts = {}
                for kw in all_keywords:
                    keyword_counts[kw] = keyword_counts.get(kw, 0) + 1

                top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:20]
                stats.keywords_cloud = [
                    {"text": word, "size": count, "count": count}
                    for word, count in top_keywords
                ]

                # Trends for last 30 days
                trends = {}
                for i in range(30):
                    date_str = (now - timedelta(days=29-i)).strftime("%Y-%m-%d")
                    trends[date_str] = next(
                        (r.get("articles_count", 0) for r in archives.get("reports", []) if r.get("date") == date_str),
                        0
                    )

                stats.trends_30days = [
                    {"date": date, "count": count}
                    for date, count in trends.items()
                ]
        except Exception as e:
            logger.error(f"Error generating daily stats: {e}")

        # Research stats
        try:
            index_file = self.data_dir / "research" / "index.json"
            if index_file.exists():
                with open(index_file, 'r', encoding='utf-8') as f:
                    research_index = json.load(f)

                stats.research_total = len(research_index.get("reports", []))

                # Group by category
                category_counts = {}
                for report in research_index.get("reports", []):
                    category = report.get("category", "uncategorized")
                    category_counts[category] = category_counts.get(category, 0) + 1

                stats.research_by_category = category_counts
        except Exception as e:
            logger.error(f"Error generating research stats: {e}")

        # Thinking stats
        try:
            models_file = self.data_dir / "thinking" / "models.json"
            if models_file.exists():
                with open(models_file, 'r', encoding='utf-8') as f:
                    models_index = json.load(f)

                stats.thinking_total = len(models_index.get("models", []))

                # Count active (not archived) models
                active_count = sum(
                    1 for m in models_index.get("models", [])
                    if not m.get("archived", False)
                )
                stats.thinking_active = active_count
        except Exception as e:
            logger.error(f"Error generating thinking stats: {e}")

        logger.info(f"Generated stats: {stats.daily_total} daily, {stats.research_total} research, {stats.thinking_total} thinking")
        return stats

    def build_daily_section(self, feed: ContentFeed) -> str:
        """Build daily report section HTML."""
        if not feed.daily_latest:
            return '<div class="empty-state"><p>暂无日报内容</p></div>'

        latest = feed.daily_latest
        html = f"""
        <div class="daily-section">
            <div class="daily-latest card">
                <div class="card-header">
                    <h3 class="card-title">{latest.get('title', 'AI日报')}</h3>
                    <span class="text-sm text-neutral-600">{latest.get('date', '')}</span>
                </div>
                <div class="card-content">
                    <p class="mb-4">{latest.get('summary', '今日AI领域重要资讯')}</p>
        """

        # Add highlights
        if feed.daily_highlights:
            html += '<div class="highlights"><h4 class="font-semibold mb-3">今日亮点</h4><div class="grid grid-cols-1 md:grid-cols-3 gap-4">'
            for article in feed.daily_highlights:
                html += f"""
                <div class="highlight-card">
                    <h5 class="font-medium text-sm mb-2">{article.get('title', 'Unknown')}</h5>
                    <p class="text-xs text-neutral-600">{article.get('source', 'AI News System')}</p>
                </div>
                """
            html += '</div></div>'

        # Add view full report link
        if "file_path" in latest:
            html += f'<a href="/{latest["file_path"]}" class="btn btn-primary mt-4">查看完整日报</a>'

        html += '</div></div></div>'
        return html

    def build_research_section(self, feed: ContentFeed) -> str:
        """Build research section HTML."""
        if not feed.research_latest:
            return '<div class="empty-state"><p>暂无调研报告</p></div>'

        html = '<div class="research-section grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">'

        for report in feed.research_latest[:6]:  # Show first 6
            category = report.get('category', 'research')
            html += f"""
            <div class="research-card card">
                <div class="card-header">
                    <span class="category-badge category-{category}">{category}</span>
                    <span class="text-sm text-neutral-600">{report.get('date', '')}</span>
                </div>
                <div class="card-content">
                    <h3 class="card-title">{report.get('title', 'Untitled')}</h3>
                    <p class="text-neutral-600">{report.get('summary', 'No summary')}</p>
                    <div class="card-footer mt-4">
                        <a href="/{report.get('file_path', '#')}" class="text-primary-600 font-semibold">阅读报告 →</a>
                    </div>
                </div>
            </div>
            """

        html += '</div>'
        return html

    def build_thinking_section(self, feed: ContentFeed) -> str:
        """Build thinking models section HTML."""
        if not feed.thinking_latest:
            return '<div class="empty-state"><p>暂无思考模型</p></div>'

        html = '<div class="thinking-section grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">'

        for model in feed.thinking_latest[:6]:  # Show first 6
            concepts = model.get('concepts', [])
            html += f"""
            <div class="thinking-card card">
                <div class="card-header">
                    <span class="version-badge">v{model.get('version', '1.0')}</span>
                    <span class="text-sm text-neutral-600">{model.get('created_date', '')}</span>
                </div>
                <div class="card-content">
                    <h3 class="card-title">{model.get('title', 'Untitled')}</h3>
                    <p class="text-neutral-600">{model.get('description', 'No description')}</p>
                    <div class="concepts mt-4">
                        <div class="flex flex-wrap gap-2">
            """
            for concept in concepts[:3]:  # Show first 3 concepts
                html += f'<span class="concept-tag">{concept}</span>'

            if len(concepts) > 3:
                html += f'<span class="concept-more">+{len(concepts) - 3}</span>'

            html += f"""
                        </div>
                    </div>
                    <div class="card-footer mt-4">
                        <a href="/{model.get('file_path', '#')}" class="text-primary-600 font-semibold">查看模型 →</a>
                    </div>
                </div>
            </div>
            """

        html += '</div>'
        return html

    def build_stats_section(self, stats: HomePageStats) -> str:
        """Build statistics section HTML."""
        html = '<div class="stats-section grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">'

        # Daily stats
        html += f"""
        <div class="stat-card card">
            <div class="card-header">
                <h3 class="card-title">日报统计</h3>
                <span class="stat-icon">📰</span>
            </div>
            <div class="card-content">
                <div class="stat-item">
                    <div class="stat-number">{stats.daily_total}</div>
                    <div class="stat-label">历史总数</div>
                </div>
                <div class="grid grid-cols-3 gap-2 mt-4">
                    <div class="stat-mini">
                        <div class="stat-mini-number">{stats.daily_today}</div>
                        <div class="stat-mini-label">今日</div>
                    </div>
                    <div class="stat-mini">
                        <div class="stat-mini-number">{stats.daily_this_week}</div>
                        <div class="stat-mini-label">本周</div>
                    </div>
                    <div class="stat-mini">
                        <div class="stat-mini-number">{stats.daily_this_month}</div>
                        <div class="stat-mini-label">本月</div>
                    </div>
                </div>
            </div>
        </div>
        """

        # Research stats
        html += f"""
        <div class="stat-card card">
            <div class="card-header">
                <h3 class="card-title">调研统计</h3>
                <span class="stat-icon">🔬</span>
            </div>
            <div class="card-content">
                <div class="stat-item">
                    <div class="stat-number">{stats.research_total}</div>
                    <div class="stat-label">报告总数</div>
                </div>
                <div class="mt-4">
        """

        if stats.research_by_category:
            for category, count in list(stats.research_by_category.items())[:5]:
                html += f'<div class="flex justify-between items-center py-1"><span class="capitalize">{category}</span><span class="font-semibold">{count}</span></div>'

        html += """
                </div>
            </div>
        </div>
        """

        # Thinking stats
        html += f"""
        <div class="stat-card card">
            <div class="card-header">
                <h3 class="card-title">思考模型</h3>
                <span class="stat-icon">🤔</span>
            </div>
            <div class="card-content">
                <div class="stat-item">
                    <div class="stat-number">{stats.thinking_total}</div>
                    <div class="stat-label">模型总数</div>
                </div>
                <div class="mt-4">
                    <div class="flex justify-between items-center py-1">
                        <span>活跃模型</span>
                        <span class="font-semibold">{stats.thinking_active}</span>
                    </div>
                    <div class="flex justify-between items-center py-1">
                        <span>归档模型</span>
                        <span class="font-semibold">{stats.thinking_total - stats.thinking_active}</span>
                    </div>
                </div>
            </div>
        </div>
        """

        html += '</div>'

        # Add trends chart and keywords cloud
        if stats.trends_30days or stats.keywords_cloud:
            html += '<div class="mt-12 grid grid-cols-1 lg:grid-cols-2 gap-6">'

            # Trends chart
            if stats.trends_30days:
                html += """
                <div class="chart-card card">
                    <div class="card-header">
                        <h3 class="card-title">30天趋势</h3>
                        <span class="stat-icon">📊</span>
                    </div>
                    <div class="card-content">
                        <canvas id="trends-chart" data-trends='{{trends_json}}'></canvas>
                    </div>
                </div>
                """.replace('{{trends_json}}', json.dumps(stats.trends_30days))

            # Keywords cloud
            if stats.keywords_cloud:
                html += """
                <div class="cloud-card card">
                    <div class="card-header">
                        <h3 class="card-title">关键词云</h3>
                        <span class="stat-icon">🏷️</span>
                    </div>
                    <div class="card-content">
                        <div id="keywords-cloud" data-keywords='{{keywords_json}}'></div>
                    </div>
                </div>
                """.replace('{{keywords_json}}', json.dumps(stats.keywords_cloud))

            html += '</div>'

        return html

    def render_template(self, data: Dict[str, Any]) -> str:
        """Render HTML using the template."""
        # Simple string replacement for now
        # In production, consider using a proper templating engine
        html = self.template
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            if isinstance(value, str):
                html = html.replace(placeholder, value)
            else:
                html = html.replace(placeholder, str(value))

        logger.info("Template rendered successfully")
        return html

    def get_critical_css(self) -> str:
        """Get critical CSS for above-the-fold content."""
        return """
        /* Critical CSS for homepage */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            line-height: 1.6;
            color: #334155;
            background: #ffffff;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 1rem;
        }

        .text-gradient {
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .section {
            padding: 4rem 0;
        }

        .section-header {
            margin-bottom: 3rem;
        }

        .card {
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .fade-in {
            animation: fadeIn 0.5s ease-in;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        """

    def generate_structured_data(self, stats: HomePageStats) -> str:
        """Generate structured data (JSON-LD) for SEO."""
        structured_data = {
            "@context": "https://schema.org",
            "@type": "website",
            "name": "AI News System - Personal Growth Website",
            "description": "Comprehensive AI-powered news and research platform",
            "url": "https://example.com",
            "potentialAction": {
                "@type": "SearchAction",
                "target": "https://example.com/search?q={search_term_string}",
                "query-input": "required name=search_term_string"
            },
            "mainEntity": {
                "@type": "CollectionPage",
                "name": "AI News and Research Aggregator",
                "articleSection": [
                    {
                        "@type": "Report",
                        "name": "AI Daily Reports",
                        "numberOfItems": stats.daily_total
                    },
                    {
                        "@type": "Report",
                        "name": "Research Reports",
                        "numberOfItems": stats.research_total
                    },
                    {
                        "@type": "CreativeWork",
                        "name": "Thinking Models",
                        "numberOfItems": stats.thinking_total
                    }
                ]
            },
            "dateModified": stats.last_updated
        }

        return json.dumps(structured_data, ensure_ascii=False, indent=2)

    def optimize_for_seo(self, html: str, stats: HomePageStats) -> str:
        """Apply SEO optimizations."""
        # Ensure canonical URL
        if '<link rel="canonical"' not in html:
            canonical = '<link rel="canonical" href="https://example.com" />'
            html = html.replace('</head>', f'  {canonical}\n</head>')

        # Ensure meta robots
        if '<meta name="robots"' not in html:
            robots = '<meta name="robots" content="index, follow" />'
            html = html.replace('</head>', f'  {robots}\n</head>')

        logger.info("SEO optimizations applied")
        return html

    def optimize_performance(self, html: str) -> str:
        """Apply performance optimizations."""
        # Minify HTML
        html = self._minify_html(html)

        # Inline critical CSS (already inlined in critical_css)

        # Add loading attributes
        html = re.sub(r'<img ', r'<img loading="lazy" ', html)

        logger.info("Performance optimizations applied")
        return html

    def _minify_html(self, html: str) -> str:
        """Simple HTML minification."""
        # Remove comments
        html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)

        # Remove extra whitespace
        html = re.sub(r'>\\s+<', '><', html)
        html = re.sub(r'\\s{2,}', ' ', html)
        html = re.sub(r'\\n', '', html)

        return html.strip()

    def save_html(self, html: str):
        """Save HTML to output directories."""
        # Save to output (development)
        output_file = self.output_dir / "index.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        # Save to docs (production/published)
        docs_file = self.docs_dir / "index.html"
        with open(docs_file, 'w', encoding='utf-8') as f:
            f.write(html)

        # Also save as homepage.html for compatibility
        homepage_file = self.docs_dir / "homepage.html"
        with open(homepage_file, 'w', encoding='utf-8') as f:
            f.write(html)

        logger.info(f"HTML saved to {output_file}, {docs_file}, and {homepage_file}")

    def save_feed(self, feed: ContentFeed, stats: HomePageStats):
        """Save feed data for caching and API usage."""
        feed_data = {
            "feed": asdict(feed),
            "stats": asdict(stats),
            "generated_at": datetime.now().isoformat()
        }

        feed_file = self.data_dir / "homepage" / "feed.json"
        with open(feed_file, 'w', encoding='utf-8') as f:
            json.dump(feed_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Feed data saved to {feed_file}")


# Test harness
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create harness
    harness = HarnessController()

    # Create agent
    agent = HomepageBuilderAgent(harness)

    # Build homepage
    print("Building homepage...")
    html = agent.build_homepage()
    print(f"Homepage built successfully! ({len(html)} characters)")
    print("Files saved to:")
    print(f"  - output/index.html")
    print(f"  - docs/index.html")
    print(f"  - docs/homepage.html")
