# -*- coding: utf-8 -*-
"""
HTML 生成器模块
基于 Jinja2 模板引擎生成格式化的新闻日报
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from jinja2 import Template, Environment, BaseLoader

# 配置日志
logger = logging.getLogger(__name__)


class HTMLGenerator:
    """
    HTML 生成器类
    负责生成格式化的 AI 日报 HTML
    """

    def __init__(self, template_path: Optional[str] = None):
        """
        初始化 HTML 生成器

        Args:
            template_path: 自定义模板文件路径（可选）
        """
        self.template_path = Path(template_path) if template_path else None
        self.default_template = self._get_default_template()

    def generate_html(self, articles: List[Dict], output_path: str, generation_time: Optional[datetime] = None,
                     title: str = "AI 日报", subtitle: str = "近一周精选") -> str:
        """
        生成 HTML 日报

        Args:
            articles: 文章列表
            output_path: 输出文件路径
            generation_time: 生成时间（默认为当前时间）
            title: 页面标题
            subtitle: 副标题

        Returns:
            生成的 HTML 内容
        """
        if not articles:
            logger.warning("文章列表为空，将生成空日报")

        if not generation_time:
            generation_time = datetime.now()

        # 按分类组织文章
        categorized_articles = self._categorize_articles(articles)

        # 计算统计信息
        stats = self._calculate_stats(articles, categorized_articles)

        # 准备模板数据
        template_data = {
            'title': title,
            'subtitle': subtitle,
            'generation_time': generation_time,
            'articles': articles,
            'categorized_articles': categorized_articles,
            'stats': stats,
            'total_count': len(articles)
        }

        # 渲染模板
        if self.template_path and self.template_path.exists():
            # 使用自定义模板
            html_content = self._render_from_file(template_data)
        else:
            # 使用默认模板
            html_content = self._render_default_template(template_data)

        # 保存到文件
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(html_content, encoding='utf-8')

        logger.info(f"HTML 日报已生成: {output_path}")
        logger.info(f"包含 {len(articles)} 篇文章，{len(categorized_articles)} 个分类")

        return html_content

    def _categorize_articles(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """
        按 category 字段对文章进行分类

        Args:
            articles: 文章列表

        Returns:
            按分类组织的文章字典
        """
        categorized = {}

        for article in articles:
            category = article.get('category', '未分类')
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(article)

        return categorized

    def _calculate_stats(self, articles: List[Dict], categorized_articles: Dict[str, List[Dict]]) -> Dict:
        """
        计算统计信息

        Args:
            articles: 文章列表
            categorized_articles: 按分类组织的文章字典

        Returns:
            统计信息字典
        """
        stats = {
            'total_articles': len(articles),
            'total_categories': len(categorized_articles),
            'articles_by_category': {}
        }

        for category, category_articles in categorized_articles.items():
            stats['articles_by_category'][category] = len(category_articles)

        return stats

    def _get_default_template(self) -> str:
        """
        获取默认的 HTML 模板

        Returns:
            模板字符串
        """
        return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}{% if subtitle %} - {{ subtitle }}{% endif %}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #fafafa;
            --card: #ffffff;
            --accent: #3b82f6;
            --text: #1f2937;
            --text-secondary: #6b7280;
            --border: #e5e7eb;
            --shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            --shadow-hover: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 0 20px;
        }

        header {
            background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
            color: white;
            padding: 48px 0;
            margin-bottom: 32px;
        }

        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        h1 {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 8px;
        }

        @media (prefers-color-scheme: dark) {
            h1 {
                color: #f9fafb;
            }
        }

        .subtitle {
            font-size: 14px;
            opacity: 0.8;
        }

        .stats {
            text-align: right;
        }

        .stats-value {
            font-size: 36px;
            font-weight: 700;
            color: #60a5fa;
        }

        .stats-label {
            font-size: 12px;
            opacity: 0.7;
        }

        .section {
            margin-bottom: 40px;
        }

        .section-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 2px solid var(--border);
        }

        .section-title {
            font-size: 20px;
            font-weight: 600;
        }

        .section-count {
            margin-left: auto;
            background: var(--bg);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 13px;
            color: var(--text-secondary);
        }

        .news-list {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .news-card-link {
            text-decoration: none;
            color: inherit;
            display: block;
        }

        /* 摘要中的列表样式 */
        .news-summary ul,
        .news-summary ol {
            padding-left: 0;
            margin: 12px 0;
            list-style: none;
        }

        .news-summary li {
            position: relative;
            padding-left: 24px;
            margin: 6px 0;
            line-height: 1.6;
        }

        /* 无序列表 - 使用圆点 */
        .news-summary ul li::before {
            content: "";
            position: absolute;
            left: 10px;
            top: 10px;
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: var(--accent);
        }

        /* 有序列表 - 使用数字卡片 */
        .news-summary ol {
            counter-reset: item;
        }

        .news-summary ol li {
            counter-increment: item;
        }

        .news-summary ol li::before {
            content: counter(item);
            position: absolute;
            left: 0;
            top: 2px;
            width: 20px;
            height: 20px;
            background: var(--accent);
            color: white;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: 600;
        }

        /* 标题样式 */
        .news-summary h1,
        .news-summary h2,
        .news-summary h3,
        .news-summary h4 {
            font-size: 15px;
            font-weight: 700;
            margin: 16px 0 8px 0;
            color: var(--text);
            line-height: 1.4;
        }

        /* 强调文本 */
        .news-summary strong,
        .news-summary b {
            color: var(--text);
            font-weight: 600;
        }

        /* 段落间距 */
        .news-summary p {
            margin: 8px 0;
        }

        .news-card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 24px;
            box-shadow: var(--shadow);
            transition: all 0.2s ease;
        }

        .news-card:hover {
            box-shadow: var(--shadow-hover);
            transform: translateY(-4px);
            border-color: var(--accent);
        }

        .news-card:hover .news-title {
            color: var(--accent);
        }

        /* 特色卡片 - 如果文章内容较长 */
        .news-card.featured {
            background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
            border-color: #dbeafe;
        }

        @media (prefers-color-scheme: dark) {
            .news-card {
                background: #1f2937;
                border-color: #374151;
            }

            .news-card.featured {
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                border-color: #1e40af;
            }
        }

        .news-meta {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 12px;
            font-size: 13px;
            color: var(--text-secondary);
            font-weight: 500;
        }

        .news-source {
            color: var(--accent);
            font-weight: 600;
            text-decoration: none;
            letter-spacing: 0.01em;
        }

        .news-source::after {
            content: "";
            display: inline-block;
            width: 4px;
            height: 4px;
            border-radius: 50%;
            background: var(--border);
            margin-left: 8px;
            vertical-align: middle;
        }

        .news-title {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 12px;
            color: var(--text);
            line-height: 1.5;
            letter-spacing: -0.01em;
        }

        .news-summary {
            font-size: 14px;
            color: var(--text-secondary);
            line-height: 1.7;
        }

        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: var(--text-secondary);
        }

        .empty-state-icon {
            font-size: 48px;
            margin-bottom: 16px;
        }

        .empty-state-text {
            font-size: 16px;
        }

        /* 响应式断点 */
        @media (max-width: 640px) {
            .header-content {
                flex-direction: column;
                gap: 24px;
                text-align: center;
            }

            .stats {
                text-align: center;
            }

            h1 {
                font-size: 24px;
            }

            .stats-value {
                font-size: 28px;
            }

            .section-title {
                font-size: 18px;
            }

            .news-card {
                padding: 16px;
            }

            .news-title {
                font-size: 15px;
            }

            .news-summary {
                font-size: 13px;
            }
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --bg: #111827;
                --card: #1f2937;
                --text: #f9fafb;
                --text-secondary: #9ca3af;
                --border: #374151;
                --shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
                --shadow-hover: 0 4px 12px rgba(0, 0, 0, 0.4);
            }

            header {
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            }

            .news-card {
                background: var(--card);
                border-color: var(--border);
            }

            .news-title {
                color: var(--text);
            }
        }

        /* 打印样式 */
        @media print {
            header {
                background: none;
                color: var(--text);
            }

            .stats-value {
                color: var(--text);
            }

            .news-card {
                box-shadow: none;
                border: 1px solid var(--border);
            }

            .news-link {
                background: none;
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="header-content">
                <div>
                    <h1>🤖 {{ title }}</h1>
                    <p class="subtitle">
                        {{ generation_time.strftime('%Y-%m-%d') }}
                        {% if subtitle %} - {{ subtitle }}{% endif %}
                    </p>
                </div>
                <div class="stats">
                    <div class="stats-value">{{ total_count }}</div>
                    <div class="stats-label">条资讯</div>
                </div>
            </div>
        </div>
    </header>

    <main class="container">
        {% if not articles %}
            <div class="empty-state">
                <div class="empty-state-icon">📚</div>
                <div class="empty-state-text">今日暂无更新</div>
            </div>
        {% else %}
            {% for category, category_articles in categorized_articles.items() %}
                {% if category_articles %}
                    <section class="section">
                        <div class="section-header">
                            <h2 class="section-title">{{ category }}</h2>
                            <span class="section-count">{{ category_articles|length }} 条</span>
                        </div>
                        <div class="news-list">
                            {% for article in category_articles %}
                                <a href="{{ article.link }}" class="news-card-link" target="_blank" rel="noopener noreferrer">
                                    <article class="news-card">
                                        <div class="news-meta">
                                            <span class="news-source">{{ article.source_name }}</span>
                                            <span>·</span>
                                            {% if article.published_at %}
                                                <span>{{ article.published_at[:10] }}</span>
                                            {% else %}
                                                <span>近期</span>
                                            {% endif %}
                                        </div>
                                        <h3 class="news-title">{{ article.title }}</h3>
                                        <p class="news-summary">{{ article.summary }}</p>
                                    </article>
                                </a>
                            {% endfor %}
                        </div>
                    </section>
                {% endif %}
            {% endfor %}
        {% endif %}
    </main>
</body>
</html>"""

    def _render_from_file(self, data: Dict) -> str:
        """
        从文件模板渲染

        Args:
            data: 模板数据

        Returns:
            渲染后的 HTML
        """
        template_content = self.template_path.read_text(encoding='utf-8')
        template = Template(template_content)
        return template.render(**data)

    def _render_default_template(self, data: Dict) -> str:
        """
        从默认模板渲染

        Args:
            data: 模板数据

        Returns:
            渲染后的 HTML
        """
        template = Template(self.default_template)
        return template.render(**data)


# 辅助函数
def generate_daily_news(articles: List[Dict], output_dir: str = "output") -> str:
    """
    生成每日新闻（便捷函数）

    Args:
        articles: 文章列表
        output_dir: 输出目录

    Returns:
        生成的文件路径
    """
    generator = HTMLGenerator()
    today = datetime.now()
    output_path = Path(output_dir) / f"ai-news-{today.strftime('%Y-%m-%d')}.html"

    generator.generate_html(
        articles=articles,
        output_path=str(output_path),
        generation_time=today
    )

    return str(output_path)


if __name__ == '__main__':
    # 测试代码
    import logging
    from datetime import timedelta

    logging.basicConfig(level=logging.INFO)

    # 测试数据
    test_articles = [
        {
            'title': 'How Moda Builds Production-Grade AI Design Agents with Deep Agents',
            'summary': 'Moda是一个面向非设计师的AI设计平台，提供完全可编辑的2D矢量画布和Cursor式AI侧边栏。其核心采用Deep Agents构建多代理系统，包括设计代理、研究代理和品牌套件代理，辅以LangSmith提供可观测性。',
            'link': 'https://blog.langchain.com/how-moda-builds-production-grade-ai-design-agents-with-deep-agents/',
            'source_name': 'LangChain Blog',
            'published_at': '2026-03-25T10:00:00',
            'category': 'Agent产品'
        },
        {
            'title': 'Show HN: AI Roundtable – Let 200 models debate your question',
            'summary': 'AI Roundtable 是一个在线工具，用户输入问题后可以让约200种不同的AI模型展开辩论并给出各自的回答，帮助用户从多角度了解问题的可能答案和思考路径。',
            'link': 'https://opper.ai/ai-roundtable/',
            'source_name': 'Hacker News',
            'published_at': '2026-03-25T12:00:00',
            'category': 'AI新闻'
        },
        {
            'title': 'TurboQuant: Redefining AI efficiency with extreme compression',
            'summary': 'TurboQuant提出了一种极致压缩技术，能够在保持模型性能的前提下，将AI模型的体积和计算需求大幅度降低，使得大模型可以在资源受限的设备上高效运行。',
            'link': 'https://research.google/blog/turboquant-redefining-ai-efficiency-with-extreme-compression/',
            'source_name': 'Google Research',
            'published_at': '2026-03-25T14:00:00',
            'category': 'AI研究'
        }
    ]

    # 生成 HTML
    generator = HTMLGenerator()
    output_path = "output/test-ai-news.html"

    html_content = generator.generate_html(
        articles=test_articles,
        output_path=output_path,
        title="AI 日报测试",
        subtitle="近一周精选"
    )

    logger.info(f"测试 HTML 已生成: {output_path}")
    logger.info(f"文件大小: {len(html_content)} 字节")
