#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily Reporter Agent
负责 AI 日报的生成、验证和归档
"""

import os
import sys
import json
import logging
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
import yaml
import re

# 导入 Auckland 核心库
from src.fetchers import RSSFetcher, HTMLFetcher, validate_rss_sources, validate_html_sources
from src.summarizer import ArticleSummarizer, create_summarizer
from src.generator import HTMLGenerator, generate_daily_news
from src.harness import HarnessController

logger = logging.getLogger(__name__)


class DailyReporterAgent:
    """
    Daily Reporter Agent

    职责：
    1. 从配置了 RSS/HTML 源抓取文章
    2. 使用 AI 生成摘要
    3. 通过 Harness 验证文章内容
    4. 生成符合 Harness 样式的 HTML 日报
    5. 更新归档数据和文件
    6. 提供质量报告
    """

    def __init__(self, harness: HarnessController, config_path: str = "config/sources.yaml"):
        """
        初始化 Daily Reporter Agent

        Args:
            harness: HarnessController 实例，用于约束控制
            config_path: 源配置文件路径
        """
        self.harness = harness
        self.config_path = Path(config_path)
        self.project_root = Path(__file__).parent.parent.parent

        # 初始化抓取器
        self.rss_fetcher = RSSFetcher()
        self.html_fetcher = HTMLFetcher()

        # 验证环境
        self._validate_environment()

        # 归档配置
        self.archive_dir = self.project_root / "data" / "daily"
        self.archive_file = self.archive_dir / "archives.json"
        self.output_dir = self.project_root / "output"

        # 确保目录存在
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)

        logger.info("DailyReporterAgent 初始化完成")

    def _validate_environment(self):
        """验证必要的环境变量"""
        required_vars = ['OPENROUTER_API_KEY']
        missing_vars = []

        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            raise ValueError(f"缺少必要的环境变量: {', '.join(missing_vars)}")

    def _load_config(self) -> Dict[str, Any]:
        """
        加载源配置文件

        Returns:
            配置字典
        """
        logger.info(f"正在加载配置文件: {self.config_path}")

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            if not config:
                raise ValueError("配置文件为空")

            logger.info("配置文件加载成功")
            return config
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            raise

    def _create_summarizer(self, config: Dict) -> ArticleSummarizer:
        """
        创建摘要生成器

        Args:
            config: 配置字典

        Returns:
            ArticleSummarizer 实例
        """
        api_key = os.getenv('OPENROUTER_API_KEY')
        base_url = os.getenv('OPENROUTER_BASE_URL')
        model = os.getenv('OPENROUTER_MODEL') or config.get('settings', {}).get('summary_model')

        summarizer_kwargs = {'api_key': api_key}
        if base_url:
            summarizer_kwargs['base_url'] = base_url
        if model:
            summarizer_kwargs['model'] = model

        return ArticleSummarizer(**summarizer_kwargs)

    def fetch_articles(self, target_date: datetime) -> List[Dict]:
        """
        抓取文章

        Args:
            target_date: 目标日期

        Returns:
            文章列表
        """
        logger.info("开始抓取文章...")

        config = self._load_config()
        all_articles = []

        # 抓取 RSS 文章
        rss_sources = config.get('rss_sources', [])
        if rss_sources:
            days = config.get('settings', {}).get('publish_date_within_days', 3)
            logger.info(f"抓取 RSS 源: {len(rss_sources)} 个源，近 {days} 天")

            rss_articles = self._fetch_rss_articles(rss_sources, target_date, days)
            all_articles.extend(rss_articles)
        else:
            logger.info("未配置 RSS 源，跳过")

        # 抓取 HTML 文章
        html_sources = config.get('html_sources', [])
        if html_sources:
            logger.info(f"抓取 HTML 源: {len(html_sources)} 个源")
            html_articles = self._fetch_html_articles(html_sources)
            all_articles.extend(html_articles)
        else:
            logger.info("未配置 HTML 源，跳过")

        logger.info(f"抓取完成，共获取 {len(all_articles)} 篇文章")
        return all_articles

    def _fetch_rss_articles(self, rss_sources: List[Dict], target_date: datetime, days: int) -> List[Dict]:
        """
        抓取 RSS 文章

        Args:
            rss_sources: RSS 源配置列表
            target_date: 目标日期
            days: 抓取天数

        Returns:
            RSS 文章列表
        """
        all_articles = []
        successful_sources = 0
        failed_sources = []

        for i, source in enumerate(rss_sources, 1):
            source_name = source.get('name', f'RSS源#{i}')

            if not source.get('enabled', True):
                logger.info(f"跳过禁用的 RSS 源: {source_name}")
                continue

            logger.info(f"[{i}/{len(rss_sources)}] 抓取 RSS 源: {source_name}")

            try:
                articles = self.rss_fetcher.fetch_articles(source, target_date)
                if articles:
                    all_articles.extend(articles)
                    successful_sources += 1
                    logger.info(f"✓ 成功获取 {len(articles)} 篇文章")
                else:
                    logger.warning(f"⚠ 未获取到文章")
            except Exception as e:
                logger.error(f"✗ 抓取失败: {str(e)}")
                failed_sources.append(source_name)

        logger.info(f"RSS 抓取完成: 成功 {successful_sources} 个源，失败 {len(failed_sources)} 个源")
        if failed_sources:
            logger.info(f"失败源: {', '.join(failed_sources)}")

        return all_articles

    def _fetch_html_articles(self, html_sources: List[Dict]) -> List[Dict]:
        """
        抓取 HTML 文章

        Args:
            html_sources: HTML 源配置列表

        Returns:
            HTML 文章列表
        """
        all_articles = []
        successful_sources = 0
        failed_sources = []

        for i, source in enumerate(html_sources, 1):
            source_name = source.get('name', f'HTML源#{i}')

            if not source.get('enabled', True):
                logger.info(f"跳过禁用的 HTML 源: {source_name}")
                continue

            logger.info(f"[{i}/{len(html_sources)}] 抓取 HTML 源: {source_name}")

            try:
                articles = self.html_fetcher.fetch_articles(source, datetime.now(timezone.utc))
                if articles:
                    all_articles.extend(articles)
                    successful_sources += 1
                    logger.info(f"✓ 成功获取 {len(articles)} 篇文章")
                else:
                    logger.warning(f"⚠ 未获取到文章")
            except Exception as e:
                logger.error(f"✗ 抓取失败: {str(e)}")
                failed_sources.append(source_name)

        logger.info(f"HTML 抓取完成: 成功 {successful_sources} 个源，失败 {len(failed_sources)} 个源")
        if failed_sources:
            logger.info(f"失败源: {', '.join(failed_sources)}")

        return all_articles

    def generate_summaries(self, articles: List[Dict], no_summarize: bool = False) -> List[Dict]:
        """
        生成文章摘要

        Args:
            articles: 文章列表
            no_summarize: 是否跳过摘要生成

        Returns:
            带摘要的文章列表
        """
        if no_summarize:
            logger.info("跳过摘要生成")
            return articles

        if not articles:
            logger.warning("文章列表为空，跳过摘要生成")
            return []

        config = self._load_config()
        summarizer = self._create_summarizer(config)

        logger.info(f"开始为 {len(articles)} 篇文章生成摘要")
        logger.info(f"使用模型: {summarizer.model}")

        try:
            summarized_articles = summarizer.summarize_articles(articles)
            logger.info(f"摘要生成完成: 成功 {len(summarized_articles)}/{len(articles)}")

            return summarized_articles
        except Exception as e:
            logger.error(f"摘要生成失败: {str(e)}")
            logger.warning("将返回未摘要的文章")
            return articles

    def validate_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        通过 Harness 验证文章

        Args:
            articles: 文章列表

        Returns:
            验证通过的文章列表
        """
        logger.info("开始验证文章质量...")

        validated_articles = []
        for i, article in enumerate(articles, 1):
            try:
                if self.harness.validate_article(article):
                    validated_articles.append(article)
                    logger.debug(f"文章 {i}/{len(articles)} 验证通过")
                else:
                    logger.warning(f"文章 {i}/{len(articles)} 验证失败: {article.get('title', 'Untitled')}")
            except Exception as e:
                logger.error(f"验证文章 {i}/{len(articles)} 时出错: {str(e)}")

        logger.info(f"文章验证完成: {len(validated_articles)}/{len(articles)} 通过")
        return validated_articles

    def generate_daily_report(self, date: Optional[str] = None, no_summarize: bool = False) -> Dict[str, Any]:
        """
        生成日报

        Args:
            date: 日期字符串 (YYYY-MM-DD)，默认使用今天
            no_summarize: 是否跳过摘要生成

        Returns:
            包含 html, articles_count, quality_score 的字典
        """
        # 解析日期
        if date:
            target_date = datetime.strptime(date, '%Y-%m-%d')
        else:
            target_date = datetime.now()
        target_date = target_date.replace(tzinfo=timezone.utc)

        date_str = target_date.strftime('%Y-%m-%d')
        logger.info(f"开始生成日报: {date_str}")

        # 1. 抓取文章
        articles = self.fetch_articles(target_date)

        if not articles:
            logger.warning("未获取到任何文章")

        # 2. 生成摘要
        summarized_articles = self.generate_summaries(articles, no_summarize)

        # 3. 验证文章
        validated_articles = self.validate_articles(summarized_articles)

        # 4. 生成 HTML
        logger.info("开始生成 HTML 日报...")
        generator = HTMLGenerator()

        output_path = self.output_dir / f"ai-daily-{date_str}.html"
        html_content = generator.generate_html(
            articles=validated_articles,
            output_path=str(output_path),
            generation_time=target_date,
            title="AI 日报",
            subtitle=f"{date_str} 精选"
        )

        # 5. 质量检查
        quality_score = self.harness.check_quality(html_content)
        logger.info(f"质量评分: {quality_score:.2f}")

        # 6. 更新归档
        archive_metadata = {
            "date": date_str,
            "articles_count": len(validated_articles),
            "quality_score": quality_score,
            "file_path": str(output_path),
            "generated_at": datetime.now().isoformat()
        }
        self.update_archive(date_str, archive_metadata)

        # 7. 复制到文档目录
        self._copy_to_docs(output_path, date_str)

        logger.info("日报生成完成")

        return {
            "html": html_content,
            "articles_count": len(validated_articles),
            "quality_score": quality_score,
            "output_path": str(output_path)
        }

    def update_archive(self, date: str, metadata: Dict[str, Any]) -> bool:
        """
        更新归档文件

        Args:
            date: 日期字符串 (YYYY-MM-DD)
            metadata: 归档元数据

        Returns:
            是否成功更新
        """
        logger.info("开始更新归档数据...")

        try:
            # 加载现有归档数据
            if self.archive_file.exists():
                with open(self.archive_file, 'r', encoding='utf-8') as f:
                    archives = json.load(f)
            else:
                archives = {"daily_reports": []}

            # 查找或添加归档条目
            daily_reports = archives.get("daily_reports", [])
            existing_index = None

            for i, report in enumerate(daily_reports):
                if report.get("date") == date:
                    existing_index = i
                    break

            if existing_index is not None:
                # 更新现有条目
                daily_reports[existing_index] = metadata
                logger.info(f"更新现有归档: {date}")
            else:
                # 添加新条目（插入开头）
                daily_reports.insert(0, metadata)
                logger.info(f"添加新归档: {date}")

            # 保存更新
            archives["daily_reports"] = daily_reports
            with open(self.archive_file, 'w', encoding='utf-8') as f:
                json.dump(archives, f, ensure_ascii=False, indent=2)

            logger.info("归档数据更新完成")
            return True

        except Exception as e:
            logger.error(f"更新归档数据失败: {str(e)}")
            return False

    def get_latest_daily(self) -> Optional[Dict[str, Any]]:
        """
        获取最新日报的元数据

        Returns:
            最新日报元数据，如果没有则返回 None
        """
        if not self.archive_file.exists():
            return None

        try:
            with open(self.archive_file, 'r', encoding='utf-8') as f:
                archives = json.load(f)

            daily_reports = archives.get("daily_reports", [])
            if daily_reports:
                return daily_reports[0]  # 第一个是最新的

            return None
        except Exception as e:
            logger.error(f"读取归档数据失败: {str(e)}")
            return None

    def _copy_to_docs(self, output_path: Path, date_str: str):
        """
        复制生成的文件到 docs 目录

        Args:
            output_path: 生成的 HTML 文件路径
            date_str: 日期字符串
        """
        try:
            docs_dir = self.project_root / "docs"
            docs_dir.mkdir(exist_ok=True)

            # 复制带日期的版本
            dst_file = docs_dir / f"ai-daily-{date_str}.html"
            shutil.copy2(output_path, dst_file)
            logger.info(f"已复制到 docs: {dst_file}")

            # 同时创建 latest 版本
            latest_file = docs_dir / "ai-daily-latest.html"
            shutil.copy2(output_path, latest_file)
            logger.info(f"已更新 latest 版本: {latest_file}")

        except Exception as e:
            logger.error(f"复制到 docs 失败: {str(e)}")

    def count_articles_in_html(self, html_path: Path) -> int:
        """
        统计 HTML 中的文章数量

        Args:
            html_path: HTML 文件路径

        Returns:
            文章数量
        """
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # 统计 news-card 类数量
            return len(re.findall(r'class="news-card"', content))
        except Exception as e:
            logger.error(f"统计文章数量失败: {str(e)}")
            return 0


def setup_logging(verbose: bool = False):
    """设置日志配置"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def main():
    """主函数（CLI 入口）"""
    import argparse

    parser = argparse.ArgumentParser(description='Daily Reporter Agent')
    parser.add_argument('--date', type=str, help='指定日期 (YYYY-MM-DD)，默认为今天')
    parser.add_argument('--config', type=str, default='config/sources.yaml', help='配置文件路径')
    parser.add_argument('--no-summarize', action='store_true', help='跳过摘要生成')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细日志')

    args = parser.parse_args()

    # 设置日志
    setup_logging(args.verbose)

    # 初始化 Harness
    harness = HarnessController()

    # 初始化 Agent
    agent = DailyReporterAgent(harness=harness, config_path=args.config)

    # 生成日报
    result = agent.generate_daily_report(
        date=args.date,
        no_summarize=args.no_summarize
    )

    # 输出结果
    print("\n" + "="*60)
    print("Daily Reporter Agent 执行完成")
    print("="*60)
    print(f"文章数量: {result['articles_count']}")
    print(f"质量评分: {result['quality_score']:.2f}")
    print(f"输出文件: {result['output_path']}")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
