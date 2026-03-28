# -*- coding: utf-8 -*-
"""
HTML 页面抓取模块
负责抓取和解析 HTML 页面，提取文章信息
"""

import logging
import requests
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import time

# 配置日志
logger = logging.getLogger(__name__)


class HTMLFetcher:
    """
    HTML 抓取器类
    负责抓取 HTML 页面并提取文章信息
    """

    def __init__(self, timeout: int = 30, retries: int = 3):
        """
        初始化 HTML 抓取器

        Args:
            timeout: HTTP 请求超时时间（秒）
            retries: 请求失败重试次数
        """
        self.timeout = timeout
        self.retries = retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def is_valid_html(self, url: str) -> Tuple[bool, Optional[str]]:
        """
        验证 HTML 页面是否可访问

        Args:
            url: 页面 URL

        Returns:
            (是否有效, 错误信息)
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            # 检查响应内容
            if not response.text or len(response.text) < 100:
                return False, "页面内容为空或太小"

            # 尝试解析 HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            if not soup.find('body'):
                return False, "无法解析页面 HTML"

            return True, None

        except requests.RequestException as e:
            logger.error(f"请求失败 - {url}: {str(e)}")
            return False, str(e)
        except Exception as e:
            logger.error(f"验证 HTML 页面失败 - {url}: {str(e)}")
            return False, str(e)

    def fetch_articles(self, source: Dict, target_date: datetime) -> List[Dict]:
        """
        抓取 HTML 页面中的文章列表

        Args:
            source: 源配置字典
                - name: 信源名称
                - url: 页面 URL
                - category: 分类
                - selectors: CSS 选择器配置
                - max_articles: 最大文章数（可选）
            target_date: 目标日期（datetime 对象）

        Returns:
            文章列表
        """
        source_name = source.get('name', 'Unknown')
        source_url = source.get('url')
        category = source.get('category', '未分类')
        selectors = source.get('selectors', {})
        max_articles = source.get('max_articles')
        has_max_articles = max_articles is not None

        logger.info(f"正在抓取 HTML 页面: {source_name} ({source_url})")

        try:
            # 获取页面内容
            response = self._fetch_with_retries(source_url)
            if not response:
                return []

            # 解析 HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # 如果有自定义选择器配置，优先使用通用解析方法
            if selectors and (selectors.get('link') or selectors.get('article')):
                return self._parse_generic(soup, source_name, category, target_date, selectors, source_url, has_max_articles, max_articles)

            # 检查是否为特殊网站，使用自定义解析
            if 'manus.im' in source_url:
                return self._parse_manus_blog(soup, source_name, category, target_date, source_url, has_max_articles, max_articles)
            elif 'cognition.ai' in source_url:
                return self._parse_cognition_blog(soup, source_name, category, target_date, source_url, has_max_articles, max_articles)
            elif 'cline.bot' in source_url:
                return self._parse_cline_blog(soup, source_name, category, target_date, source_url, has_max_articles, max_articles)
            elif 'ampcode.com' in source_url:
                return self._parse_ampcode_blog(soup, source_name, category, target_date, source_url, has_max_articles, max_articles)
            elif 'anthropic.com' in source_url:
                return self._parse_anthropic_blog(soup, source_name, category, target_date, source_url, has_max_articles, max_articles)

            # 如果没有特殊处理且没有自定义选择器，使用通用解析方法
            return self._parse_generic(soup, source_name, category, target_date, selectors, source_url, has_max_articles, max_articles)

        except Exception as e:
            logger.error(f"抓取 HTML 页面失败 - {source_name}: {str(e)}")
            return []

    def _fetch_with_retries(self, url: str) -> Optional[requests.Response]:
        """
        带重试的 HTTP 请求

        Args:
            url: 请求 URL

        Returns:
            HTTP 响应对象或 None
        """
        for attempt in range(self.retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                logger.warning(f"请求失败 (尝试 {attempt + 1}/{self.retries}): {str(e)}")
                if attempt < self.retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    logger.error(f"所有重试失败 - {url}")
                    return None

    def _parse_generic(self, soup: BeautifulSoup, source_name: str, category: str,
                      target_date: datetime, selectors: Dict, base_url: str,
                      has_max_articles: bool = False, max_articles: Optional[int] = None) -> List[Dict]:
        """
        通用 HTML 解析方法

        Args:
            soup: BeautifulSoup 对象
            source_name: 信源名称
            category: 分类
            target_date: 目标日期
            selectors: CSS 选择器配置
            base_url: 基础 URL
            has_max_articles: 源是否有最大文章数限制
            max_articles: 最大文章数

        Returns:
            文章列表
        """
        import traceback

        articles = []

        logger.info(f"开始解析 HTML: {source_name}")
        logger.info(f"选择器配置: {selectors}")
        logger.info(f"max_articles: {max_articles}")

        # 如果有直接指定 link 选择器（如 Manus 博客），使用链接提取模式
        link_selector = selectors.get('link')
        if link_selector:
            logger.info(f"使用链接选择器模式: {link_selector}")
            try:
                link_elements = soup.select(link_selector)
                logger.info(f"找到 {len(link_elements)} 个链接元素")

                if not link_elements:
                    logger.warning(f"选择器 {link_selector} 未匹配到任何元素")
                    return []

                # 限制数量
                elements_to_process = link_elements[:max_articles] if max_articles else link_elements
                logger.info(f"将处理前 {len(elements_to_process)} 个元素")

                for i, element in enumerate(elements_to_process):
                    try:
                        logger.debug(f"处理第 {i+1} 个元素: {str(element)[:100]}")
                        article = self._extract_article_from_link(element, source_name, category, base_url)
                        if article:
                            logger.debug(f"成功提取文章: {article['title'][:50]}")
                            articles.append(article)
                        else:
                            logger.debug(f"第 {i+1} 个元素未提取到文章")
                    except Exception as e:
                        logger.warning(f"从链接提取文章失败 (元素 {i+1}): {str(e)}")
                        logger.debug(traceback.format_exc())
                        continue

                logger.info(f"链接选择器模式完成，共提取 {len(articles)} 篇文章")
                return articles

            except Exception as e:
                logger.error(f"链接选择器模式失败: {str(e)}")
                logger.debug(traceback.format_exc())
                return []

        # 否则使用传统的文章元素提取模式
        logger.info("使用传统文章元素提取模式")

        # 查找文章容器
        container_selector = selectors.get('container', '')
        if container_selector:
            container = soup.select_one(container_selector)
            if not container:
                logger.warning(f"未找到文章容器: {container_selector}")
                container = soup.body or soup
        else:
            container = soup.body or soup

        # 查找文章元素
        article_selector = selectors.get('article', '')
        if article_selector:
            article_elements = container.select(article_selector)
        else:
            # 尝试常见文章容器
            article_elements = container.find_all(['article', 'div.post', 'div.entry'])

        logger.info(f"找到 {len(article_elements)} 个文章元素")

        # 如果有 max_articles 限制，只处理前 N 个
        elements_to_process = article_elements[:max_articles] if max_articles else article_elements

        for element in elements_to_process:
            try:
                article = self._extract_article_from_element(
                    element, source_name, category, target_date, selectors, base_url, has_max_articles
                )
                if article:
                    articles.append(article)
            except Exception as e:
                logger.warning(f"提取文章失败: {str(e)}")
                continue

        logger.info(f"传统模式完成，共提取 {len(articles)} 篇文章")
        return articles

    def _extract_article_from_link(self, link_element: BeautifulSoup, source_name: str,
                                 category: str, base_url: str) -> Optional[Dict]:
        """
        从链接元素中提取文章信息（用于直接指定 link 选择器的情况）

        Args:
            link_element: 链接元素（a 标签）
            source_name: 信源名称
            category: 分类
            base_url: 基础 URL

        Returns:
            文章字典或 None
        """
        # 提取链接
        link = link_element.get('href')
        if not link:
            return None

        # 确保链接是字符串
        if not isinstance(link, str):
            return None

        # 转换为绝对链接
        link = urljoin(base_url, link)

        # 提取标题（从链接文本或 title 属性）
        title = link_element.get_text(strip=True)
        if not title:
            title = link_element.get('title', '')

        # 标题必须足够长（至少10个字符），太短可能是导航或按钮
        if not title or len(title) < 10:
            logger.debug(f"标题太短或为空，跳过: {title}")
            return None

        # 只保留博客文章链接（包含 /blog/ 的链接）
        if '/blog/' not in link:
            logger.debug(f"链接不是博客文章，跳过: {link}")
            return None

        # 清理标题（移除前面的标签如"产品·2026年3月18日"）
        import re
        # 移除开头的日期标签格式
        title = re.sub(r'^[^·]+·[^·]+·', '', title)
        title = title.strip()

        return {
            'title': title,
            'link': link,
            'content': f"来自 {source_name} 的最新文章",  # 简短描述
            'published_at': None,  # 无日期
            'source_name': source_name,
            'category': category
        }

    def _extract_article_from_element(self, element: BeautifulSoup, source_name: str,
                                    category: str, target_date: datetime,
                                    selectors: Dict, base_url: str,
                                    has_max_articles: bool = False) -> Optional[Dict]:
        """
        从 HTML 元素中提取文章信息

        Args:
            element: 文章元素
            source_name: 信源名称
            category: 分类
            target_date: 目标日期
            selectors: CSS 选择器配置
            base_url: 基础 URL
            has_max_articles: 源是否有最大文章数限制

        Returns:
            文章字典或 None
        """
        # 提取标题
        title_selector = selectors.get('title', 'h2, h3, .title, .post-title')
        title_element = None

        if title_selector:
            title_element = element.select_one(title_selector)

        if not title_element:
            # 在元素内部查找标题
            title_element = element.find(['h2', 'h3', 'h4'])
            if not title_element:
                return None

        title = title_element.get_text(strip=True)
        if not title:
            return None

        # 提取链接
        link = self._extract_link(title_element, element, base_url)
        if not link:
            return None

        # 提取文章内容（用于后续 AI 生成摘要）
        content = self._extract_content(element, selectors)

        # 提取日期
        published_at = self._extract_date_from_element(element, selectors)

        # 如果有日期但不在近 N 天内，跳过
        if published_at and not self._is_same_day(published_at, target_date):
            return None

        # 如果没有日期且没有最大文章数限制，跳过
        if not published_at and not has_max_articles:
            logger.warning(f"文章 '{title[:30]}...' 缺少发布日期且源无数量限制，跳过")
            return None

        return {
            'title': title,
            'link': link,
            'content': content,
            'published_at': published_at.isoformat() if published_at else None,
            'source_name': source_name,
            'category': category
        }

    def _extract_link(self, title_element: BeautifulSoup, article_element: BeautifulSoup,
                     base_url: str) -> Optional[str]:
        """
        从文章元素中提取链接

        Args:
            title_element: 标题元素
            article_element: 文章元素
            base_url: 基础 URL

        Returns:
            完整链接或 None
        """
        # 从标题元素中找链接
        link_element = title_element.find('a', href=True)
        if link_element:
            link = link_element['href']
        else:
            # 从整个文章中找第一个链接
            link_element = article_element.find('a', href=True)
            if link_element:
                link = link_element['href']
            else:
                return None

        # 转换为绝对链接
        return urljoin(base_url, link)

    def _extract_content(self, element: BeautifulSoup, selectors: Dict) -> str:
        """
        从文章元素中提取内容（用于后续 AI 生成摘要）

        Args:
            element: 文章元素
            selectors: CSS 选择器配置

        Returns:
            内容字符串
        """
        summary_selector = selectors.get('summary', '.summary, .excerpt, p')

        if summary_selector:
            summary_element = element.select_one(summary_selector)
            if summary_element:
                return summary_element.get_text(strip=True)

        # 尝试查找段落作为摘要
        paragraphs = element.find_all('p')
        if paragraphs:
            return paragraphs[0].get_text(strip=True)

        return ""

    def _extract_date_from_element(self, element: BeautifulSoup, selectors: Dict) -> Optional[datetime]:
        """
        从文章元素中提取日期

        Args:
            element: 文章元素
            selectors: CSS 选择器配置

        Returns:
            datetime 对象或 None
        """
        date_selector = selectors.get('date', 'time, .date, .published, .post-date')

        if date_selector:
            date_element = element.select_one(date_selector)
        else:
            date_element = element.find('time')

        if not date_element:
            return None

        return self._parse_date(date_element)

    def _parse_date(self, date_element) -> Optional[datetime]:
        """
        解析日期元素

        Args:
            date_element: 日期元素

        Returns:
            datetime 对象或 None
        """
        # 尝试从 datetime 属性获取
        datetime_str = date_element.get('datetime')
        if datetime_str:
            try:
                return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            except ValueError:
                pass

        # 尝试从文本解析
        date_text = date_element.get_text(strip=True)
        if date_text:
            return self._parse_date_string(date_text)

        return None

    def _parse_date_string(self, date_str: str) -> Optional[datetime]:
        """
        解析日期字符串

        Args:
            date_str: 日期字符串

        Returns:
            datetime 对象或 None
        """
        # 常见日期格式
        date_patterns = [
            r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  # MM/DD/YYYY
            r'(\d{1,2})-(\d{1,2})-(\d{4})',  # MM-DD-YYYY
            r'(\w+)\s+(\d{1,2}),?\s+(\d{4})',  # Month DD, YYYY
        ]

        for pattern in date_patterns:
            match = re.search(pattern, date_str)
            if match:
                try:
                    if len(match.groups()) == 3:
                        # 解析日期组件
                        groups = match.groups()
                        if groups[0].isdigit() and int(groups[0]) > 31:
                            # YYYY-MM-DD 格式
                            year, month, day = map(int, groups)
                        elif groups[2].isdigit() and int(groups[2]) > 31:
                            # MM/DD/YYYY 格式
                            month, day, year = map(int, groups)
                        else:
                            # 尝试自动检测
                            return datetime.fromisoformat(date_str)

                        return datetime(year, month, day, tzinfo=timezone.utc)
                except ValueError:
                    continue

        return None

    def _is_same_day(self, date1: datetime, date2: datetime) -> bool:
        """
        判断两个日期是否是同一天

        Args:
            date1: 第一个日期
            date2: 第二个日期

        Returns:
            是否是同一天
        """
        date1_local = date1.astimezone()
        date2_local = date2.astimezone()

        return (date1_local.year == date2_local.year and
                date1_local.month == date2_local.month and
                date1_local.day == date2_local.day)

    # 自定义解析方法

    def _parse_manus_blog(self, soup: BeautifulSoup, source_name: str, category: str,
                         target_date: datetime, base_url: str, has_max_articles: bool = False, max_articles: Optional[int] = None) -> List[Dict]:
        """
        解析 Manus AI 博客

        Args:
            soup: BeautifulSoup 对象
            source_name: 信源名称
            category: 分类
            target_date: 目标日期
            base_url: 基础 URL

        Returns:
            文章列表
        """
        articles = []

        # Manus 博客的文章结构
        post_elements = soup.find_all('div', class_='bg-white')

        for element in post_elements:
            try:
                # 提取标题和链接
                link_elem = element.find('a', href=True)
                if not link_elem:
                    continue

                title_elem = element.find(['h2', 'h3'])
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                link = urljoin(base_url, link_elem['href'])

                # 提取文章内容（用于后续 AI 生成摘要）
                content_elem = element.find('p')
                content = content_elem.get_text(strip=True) if content_elem else ""

                # Manus 博客没有明确的日期，接受所有文章
                article = {
                    'title': title,
                    'link': link,
                    'content': content,
                    'published_at': None,
                    'source_name': source_name,
                    'category': category
                }
                articles.append(article)

            except Exception as e:
                logger.warning(f"提取 Manus 文章失败: {str(e)}")
                continue

        return articles

    def _parse_cognition_blog(self, soup: BeautifulSoup, source_name: str, category: str,
                         target_date: datetime, base_url: str, has_max_articles: bool = False, max_articles: Optional[int] = None) -> List[Dict]:
        """
        解析 Cognition AI 博客

        Args:
            soup: BeautifulSoup 对象
            source_name: 信源名称
            category: 分类
            target_date: 目标日期
            base_url: 基础 URL

        Returns:
            文章列表
        """
        articles = []

        # Cognition 博客的文章结构
        post_elements = soup.find_all('article')

        for element in post_elements:
            try:
                # 提取标题和链接
                title_elem = element.find(['h2', 'h3'])
                if not title_elem:
                    continue

                link_elem = title_elem.find('a', href=True)
                if not link_elem:
                    continue

                title = title_elem.get_text(strip=True)
                link = urljoin(base_url, link_elem['href'])

                # 提取文章内容（用于后续 AI 生成摘要）
                content_elem = element.find('p')
                content = content_elem.get_text(strip=True) if content_elem else ""

                # Cognition 博客没有明确的日期，接受所有文章
                article = {
                    'title': title,
                    'link': link,
                    'content': content,
                    'published_at': None,
                    'source_name': source_name,
                    'category': category
                }
                articles.append(article)

            except Exception as e:
                logger.warning(f"提取 Cognition 文章失败: {str(e)}")
                continue

        return articles

    def _parse_cline_blog(self, soup: BeautifulSoup, source_name: str, category: str,
                         target_date: datetime, base_url: str, has_max_articles: bool = False, max_articles: Optional[int] = None) -> List[Dict]:
        """
        解析 Cline 博客

        Args:
            soup: BeautifulSoup 对象
            source_name: 信源名称
            category: 分类
            target_date: 目标日期
            base_url: 基础 URL

        Returns:
            文章列表
        """
        articles = []

        # Cline 博客的文章结构
        post_elements = soup.find_all('article')

        for element in post_elements:
            try:
                # 提取标题和链接
                title_elem = element.find(['h2', 'h3'])
                if not title_elem:
                    continue

                link_elem = title_elem.find('a', href=True)
                if not link_elem:
                    continue

                title = title_elem.get_text(strip=True)
                link = urljoin(base_url, link_elem['href'])

                # 提取摘要
                summary_elem = element.find('p')
                summary = summary_elem.get_text(strip=True) if summary_elem else ""

                # Cline 博客没有明确的日期，接受所有文章
                article = {
                    'title': title,
                    'link': link,
                    'content': content,
                    'published_at': None,
                    'source_name': source_name,
                    'category': category
                }
                articles.append(article)

            except Exception as e:
                logger.warning(f"提取 Cline 文章失败: {str(e)}")
                continue

        return articles

    def _parse_ampcode_blog(self, soup: BeautifulSoup, source_name: str, category: str,
                         target_date: datetime, base_url: str, has_max_articles: bool = False, max_articles: Optional[int] = None) -> List[Dict]:
        """
        解析 AMP Code 博客

        Args:
            soup: BeautifulSoup 对象
            source_name: 信源名称
            category: 分类
            target_date: 目标日期
            base_url: 基础 URL

        Returns:
            文章列表
        """
        articles = []

        # AMP Code 博客的文章结构
        post_elements = soup.find_all('article')

        for element in post_elements:
            try:
                # 提取标题和链接
                title_elem = element.find(['h2', 'h3'])
                if not title_elem:
                    continue

                link_elem = title_elem.find('a', href=True)
                if not link_elem:
                    continue

                title = title_elem.get_text(strip=True)
                link = urljoin(base_url, link_elem['href'])

                # 提取摘要
                summary_elem = element.find('p')
                summary = summary_elem.get_text(strip=True) if summary_elem else ""

                # AMP Code 博客没有明确的日期，接受所有文章
                article = {
                    'title': title,
                    'link': link,
                    'content': content,
                    'published_at': None,
                    'source_name': source_name,
                    'category': category
                }
                articles.append(article)

            except Exception as e:
                logger.warning(f"提取 AMP Code 文章失败: {str(e)}")
                continue

        return articles

    def _parse_anthropic_blog(self, soup: BeautifulSoup, source_name: str, category: str,
                         target_date: datetime, base_url: str, has_max_articles: bool = False, max_articles: Optional[int] = None) -> List[Dict]:
        """
        解析 Anthropic 工程博客

        Args:
            soup: BeautifulSoup 对象
            source_name: 信源名称
            category: 分类
            target_date: 目标日期
            base_url: 基础 URL

        Returns:
            文章列表
        """
        articles = []

        # Anthropic 博客的文章结构
        post_elements = soup.find_all('article')

        for element in post_elements:
            try:
                # 提取标题和链接
                title_elem = element.find(['h2', 'h3'])
                if not title_elem:
                    continue

                link_elem = title_elem.find('a', href=True)
                if not link_elem:
                    continue

                title = title_elem.get_text(strip=True)
                link = urljoin(base_url, link_elem['href'])

                # 提取摘要
                summary_elem = element.find('p')
                summary = summary_elem.get_text(strip=True) if summary_elem else ""

                # Anthropic 博客没有明确的日期，接受所有文章
                article = {
                    'title': title,
                    'link': link,
                    'content': content,
                    'published_at': None,
                    'source_name': source_name,
                    'category': category
                }
                articles.append(article)

            except Exception as e:
                logger.warning(f"提取 Anthropic 文章失败: {str(e)}")
                continue

        return articles


# 辅助函数
def validate_html_sources(sources: List[Dict]) -> List[Tuple[Dict, bool, Optional[str]]]:
    """
    批量验证 HTML 源

    Args:
        sources: 源配置列表

    Returns:
        验证结果列表，每个元素为 (源配置, 是否有效, 错误信息)
    """
    fetcher = HTMLFetcher()
    results = []

    for source in sources:
        is_valid, error = fetcher.is_valid_html(source['url'])
        results.append((source, is_valid, error))

    return results


if __name__ == '__main__':
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    # 测试 HTML 抓取
    test_sources = [
        {
            'name': 'Test HTML',
            'url': 'https://manus.im/zh-cn/blog',
            'category': 'Test',
            'selectors': {
                'container': 'main',
                'article': 'article',
                'title': 'h2',
                'link': 'a',
                'date': 'time'
            }
        }
    ]

    fetcher = HTMLFetcher()
    today = datetime.now(timezone.utc)

    for source in test_sources:
        articles = fetcher.fetch_articles(source, today)
        print(f"\nFound {len(articles)} articles from {source['name']}")
        for article in articles[:3]:  # 只显示前3篇
            print(f"- {article['title']}")
            print(f"  {article['link']}")
            print(f"  {article['summary'][:100]}...")
