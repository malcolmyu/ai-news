# -*- coding: utf-8 -*-
"""
RSS 订阅源抓取模块
负责抓取和解析 RSS/Atom 订阅源，提取当天发布的文章
"""

import logging
import feedparser
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse
import re

# 配置日志
logger = logging.getLogger(__name__)


class RSSFetcher:
    """
    RSS 抓取器类
    负责抓取 RSS/Atom 订阅源并提取文章信息
    """

class RSSFetcher:
    """
    RSS 抓取器类
    负责抓取 RSS/Atom 订阅源并提取文章信息

    注意：feedparser 库本身不支持 timeout 参数，因此我们使用 requests 库先获取内容，
    然后再用 feedparser 解析。这样可以实现超时控制。
    """

    def __init__(self, timeout: int = 30):
        """
        初始化 RSS 抓取器

        Args:
            timeout: HTTP 请求超时时间（秒）
        """
        self.timeout = timeout
        self._setup_feedparser()

    def _setup_feedparser(self):
        """配置 feedparser"""
        # 设置用户代理
        feedparser.USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

    def is_valid_rss(self, url: str) -> Tuple[bool, Optional[str]]:
        """
        验证 RSS 源是否有效

        Args:
            url: RSS 源 URL

        Returns:
            (是否有效, 错误信息)
        """
        try:
            # 使用 requests 库来获取 RSS 内容，以支持 timeout
            import requests
            try:
                response = requests.get(url, timeout=self.timeout, headers={'User-Agent': feedparser.USER_AGENT})
                response.raise_for_status()
                content = response.content
            except Exception as e:
                logger.error(f"获取 RSS 源失败 - {url}: {str(e)}")
                return False, str(e)

            feed = feedparser.parse(content)

            # 检查解析错误
            if feed.bozo:
                logger.warning(f"RSS 解析警告 - {url}: {feed.bozo_exception}")
                # 有些警告不影响使用，继续检查

            # 检查是否有文章
            if not feed.entries:
                return False, "RSS 源中没有找到文章条目"

            # 检查必要的字段
            if not feed.feed.get('title'):
                return False, "RSS 源缺少标题信息"

            return True, None

        except Exception as e:
            logger.error(f"验证 RSS 源失败 - {url}: {str(e)}")
            return False, str(e)

    def fetch_articles(self, source: Dict, target_date: datetime, days: int = 3) -> List[Dict]:
        """
        抓取指定日期当天发布的文章

        Args:
            source: 源配置字典
                - name: 信源名称
                - url: RSS URL
                - category: 分类
                - max_articles: 最大文章数（可选）
            target_date: 目标日期（datetime 对象）

        Returns:
            文章列表，每个文章包含标题、链接、摘要等信息
        """
        source_name = source.get('name', 'Unknown')
        source_url = source.get('url')
        category = source.get('category', '未分类')
        max_articles = source.get('max_articles')  # 获取最大文章数限制

        logger.info(f"正在抓取 RSS 源: {source_name} ({source_url}) - 近{days}天")

        try:
            # 使用 requests 获取 RSS 内容，以支持 timeout
            import requests
            response = requests.get(source_url, timeout=self.timeout, headers={'User-Agent': feedparser.USER_AGENT})
            response.raise_for_status()
            content = response.content

            # 解析 RSS
            feed = feedparser.parse(content)

            if feed.bozo and not feed.entries:
                logger.error(f"RSS 源解析失败 - {source_name}: {feed.bozo_exception}")
                return []

            articles = []
            logger.info(f"RSS 源 '{source_name}' 共有 {len(feed.entries)} 篇文章")

            # 如果有 max_articles 限制，只处理前 N 篇
            entries_to_process = feed.entries[:max_articles] if max_articles else feed.entries

            for entry in entries_to_process:
                try:
                    # 提取文章信息
                    article = self._extract_article(entry, source_name, category, target_date, days)
                    if article:
                        articles.append(article)
                except Exception as e:
                    logger.warning(f"提取文章失败: {str(e)}")
                    continue

            # 过滤近 N 天发布的文章
            recent_articles = self._filter_recent_articles(articles, target_date, days)

            logger.info(f"从 '{source_name}' 获取到 {len(recent_articles)} 篇近{days}天发布的文章")
            return recent_articles

        except Exception as e:
            logger.error(f"抓取 RSS 源失败 - {source_name}: {str(e)}")
            return []

    def _extract_article(self, entry, source_name: str, category: str, target_date: datetime, days: int = 3) -> Optional[Dict]:
        """
        从 RSS 条目中提取文章信息

        Args:
            entry: feedparser 条目对象
            source_name: 信源名称
            category: 分类
            target_date: 目标日期

        Returns:
            文章字典或 None
        """
        # 提取标题
        title = entry.get('title', '').strip()
        if not title:
            logger.warning(f"文章缺少标题，跳过")
            return None

        # 提取链接
        link = entry.get('link')
        if not link:
            # 尝试从 id 中提取链接
            link = entry.get('id')
            if not link or not link.startswith('http'):
                logger.warning(f"文章 '{title}' 缺少有效链接，跳过")
                return None

        # 提取摘要/内容
        summary = self._extract_content(entry)
        if not summary:
            # 如果没有摘要，使用标题作为内容
            summary = title

        # 提取发布日期
        published_at = self._extract_date(entry)
        if not published_at:
            # 如果没有日期，默认使用当前时间（作为备选）
            logger.warning(f"文章 '{title}' 缺少发布日期，将使用当前时间作为备选")
            published_at = datetime.now(timezone.utc)
        elif not self._is_within_days(published_at, target_date, days):
            # 检查是否是近 N 天的文章
            return None

        return {
            'title': title,
            'link': link,
            'summary': summary,
            'published_at': published_at.isoformat(),
            'source_name': source_name,
            'category': category
        }

    def _is_within_days(self, date: datetime, target_date: datetime, days: int) -> bool:
        """
        判断日期是否在目标日期的指定天数范围内

        Args:
            date: 要检查的日期
            target_date: 目标日期
            days: 天数范围

        Returns:
            是否在指定天数范围内
        """
        # 计算日期差
        date_local = date.astimezone()
        target_local = target_date.astimezone()

        # 计算日期差（忽略时间）
        date_only = date_local.date()
        target_only = target_local.date()

        delta = target_only - date_only

        # 检查是否在指定天数内（包括当天）
        return 0 <= delta.days <= days

    def _extract_content(self, entry) -> str:
        """
        从 RSS 条目中提取内容/摘要

        Args:
            entry: feedparser 条目对象

        Returns:
            内容字符串
        """
        # 优先使用 content 字段
        if 'content' in entry and entry.content:
            return entry.content[0].value.strip()

        # 其次使用 summary 字段
        if 'summary' in entry and entry.summary:
            return entry.summary.strip()

        # 最后使用 description 字段
        if 'description' in entry and entry.description:
            return entry.description.strip()

        return ""

    def _extract_date(self, entry) -> Optional[datetime]:
        """
        从 RSS 条目中提取发布日期

        Args:
            entry: feedparser 条目对象

        Returns:
            datetime 对象或 None
        """
        import time

        # 尝试多个日期字段
        date_fields = ['published_parsed', 'updated_parsed', 'created_parsed', 'date_parsed']

        for field in date_fields:
            if field in entry and entry[field]:
                try:
                    # feedparser 返回的是 time.struct_time
                    # 将 struct_time 转换为时间戳
                    struct_time = entry[field]
                    timestamp = time.mktime(struct_time)
                    return datetime.fromtimestamp(timestamp, tz=timezone.utc)
                except (AttributeError, ValueError, TypeError, OSError):
                    continue

        # 尝试直接解析日期字符串
        date_str_fields = ['published', 'updated', 'created', 'date']
        for field in date_str_fields:
            if field in entry and entry[field]:
                try:
                    # 使用 feedparser 的日期解析
                    parsed = feedparser._parse_date(entry[field])
                    if parsed:
                        # parsed 是 time.struct_time
                        timestamp = time.mktime(parsed)
                        return datetime.fromtimestamp(timestamp, tz=timezone.utc)
                except (AttributeError, ValueError, TypeError, OSError):
                    continue

        return None

    def _filter_recent_articles(self, articles: List[Dict], target_date: datetime, days: int = 3) -> List[Dict]:
        """
        过滤出近 N 天发布的文章

        Args:
            articles: 文章列表
            target_date: 目标日期
            days: 天数范围

        Returns:
            近 N 天发布的文章列表
        """
        recent_articles = []

        for article in articles:
            try:
                published_at = datetime.fromisoformat(article['published_at'])
                if self._is_within_days(published_at, target_date, days):
                    recent_articles.append(article)
            except (ValueError, TypeError):
                continue

        return recent_articles

    def get_source_info(self, url: str) -> Optional[Dict]:
        """
        获取 RSS 源的基本信息

        Args:
            url: RSS 源 URL

        Returns:
            源信息字典或 None
        """
        try:
            feed = feedparser.parse(url, timeout=self.timeout)

            if not feed.feed:
                return None

            return {
                'title': feed.feed.get('title', ''),
                'description': feed.feed.get('description', ''),
                'link': feed.feed.get('link', ''),
                'last_updated': feed.feed.get('updated', ''),
                'total_entries': len(feed.entries)
            }

        except Exception as e:
            logger.error(f"获取 RSS 源信息失败: {str(e)}")
            return None


# 辅助函数
def validate_rss_sources(sources: List[Dict]) -> List[Tuple[Dict, bool, Optional[str]]]:
    """
    批量验证 RSS 源

    Args:
        sources: 源配置列表

    Returns:
        验证结果列表，每个元素为 (源配置, 是否有效, 错误信息)
    """
    fetcher = RSSFetcher()
    results = []

    for source in sources:
        is_valid, error = fetcher.is_valid_rss(source['url'])
        results.append((source, is_valid, error))

    return results


if __name__ == '__main__':
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    # 测试 RSS 抓取
    test_sources = [
        {
            'name': 'Test RSS',
            'url': 'https://s.baoyu.io/feed.xml',
            'category': 'Test'
        }
    ]

    fetcher = RSSFetcher()
    today = datetime.now(timezone.utc)

    for source in test_sources:
        articles = fetcher.fetch_articles(source, today)
        print(f"\nFound {len(articles)} articles from {source['name']}")
        for article in articles[:3]:  # 只显示前3篇
            print(f"- {article['title']}")
            print(f"  {article['link']}")
            print(f"  {article['published_at']}")
