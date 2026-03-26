#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 日报生成系统主程序

使用示例:
    python src/main.py
    python src/main.py --date 2026-03-25
    python src/main.py --verbose
    python src/main.py --no-summarize
"""

import os
import sys
import argparse
import logging
import yaml
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict
import time

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from dotenv import load_dotenv
except ImportError:
    # 如果 dotenv 未安装，创建一个空的 load_dotenv 函数
    def load_dotenv(*args, **kwargs):
        pass
from src.fetchers import RSSFetcher, HTMLFetcher, validate_rss_sources, validate_html_sources
from src.summarizer import ArticleSummarizer, create_summarizer
from src.generator import HTMLGenerator, generate_daily_news

# 配置日志
def setup_logging(verbose: bool = False):
    """设置日志配置"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def load_config(config_path: str) -> Dict:
    """
    加载配置文件

    Args:
        config_path: 配置文件路径

    Returns:
        配置字典
    """
    logger = logging.getLogger(__name__)
    logger.info(f"正在加载配置文件: {config_path}")

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        if not config:
            raise ValueError("配置文件为空")

        logger.info("配置文件加载成功")
        return config

    except FileNotFoundError:
        logger.error(f"配置文件未找到: {config_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"配置文件格式错误: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"加载配置文件失败: {str(e)}")
        raise

def validate_environment():
    """
    验证环境变量是否配置正确

    Returns:
        是否配置正确
    """
    logger = logging.getLogger(__name__)

    required_vars = ['OPENROUTER_API_KEY']
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        logger.error(f"缺少必要的环境变量: {', '.join(missing_vars)}")
        logger.error("请复制 .env.example 到 .env 并填写相应的值")
        return False

    return True

def fetch_rss_articles(fetcher: RSSFetcher, rss_sources: List[Dict], target_date: datetime, days: int = 3) -> List[Dict]:
    """
    抓取 RSS 源的文章

    Args:
        fetcher: RSS 抓取器
        rss_sources: RSS 源配置列表
        target_date: 目标日期
        days: 抓取近几天的文章

    Returns:
        文章列表
    """
    logger = logging.getLogger(__name__)
    logger.info("开始抓取 RSS 源...")

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
            articles = fetcher.fetch_articles(source, target_date)
            if articles:
                all_articles.extend(articles)
                successful_sources += 1
                logger.info(f"✓ 成功获取 {len(articles)} 篇文章")
            else:
                logger.warning(f"⚠ 未获取到文章 (可能是当天无更新)")

        except Exception as e:
            logger.error(f"✗ 抓取失败: {str(e)}")
            failed_sources.append(source_name)

    logger.info(f"\nRSS 抓取完成:")
    logger.info(f"  - 成功源: {successful_sources}")
    logger.info(f"  - 失败源: {len(failed_sources)}")
    if failed_sources:
        logger.info(f"  - 失败列表: {', '.join(failed_sources)}")
    logger.info(f"  - 总文章数: {len(all_articles)}")

    return all_articles

def fetch_html_articles(fetcher: HTMLFetcher, html_sources: List[Dict]) -> List[Dict]:
    """
    抓取 HTML 源的文章

    Args:
        fetcher: HTML 抓取器
        html_sources: HTML 源配置列表

    Returns:
        文章列表
    """
    logger = logging.getLogger(__name__)
    logger.info("开始抓取 HTML 源...")

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
            # HTML 源抓取不限制日期，返回所有可用文章
            articles = fetcher.fetch_articles(source, datetime.now(timezone.utc))
            if articles:
                all_articles.extend(articles)
                successful_sources += 1
                logger.info(f"✓ 成功获取 {len(articles)} 篇文章")
            else:
                logger.warning(f"⚠ 未获取到文章")

        except Exception as e:
            logger.error(f"✗ 抓取失败: {str(e)}")
            failed_sources.append(source_name)

    logger.info(f"\nHTML 抓取完成:")
    logger.info(f"  - 成功源: {successful_sources}")
    logger.info(f"  - 失败源: {len(failed_sources)}")
    if failed_sources:
        logger.info(f"  - 失败列表: {', '.join(failed_sources)}")
    logger.info(f"  - 总文章数: {len(all_articles)}")

    return all_articles

def generate_summaries(summarizer: ArticleSummarizer, articles: List[Dict],
                      no_summarize: bool = False) -> List[Dict]:
    """
    为文章生成摘要

    Args:
        summarizer: 摘要生成器
        articles: 文章列表
        no_summarize: 是否跳过摘要生成

    Returns:
        带摘要的文章列表
    """
    logger = logging.getLogger(__name__)

    if no_summarize:
        logger.info("跳过摘要生成 (--no-summarize)")
        return articles

    if not articles:
        logger.warning("文章列表为空，跳过摘要生成")
        return []

    logger.info(f"开始为 {len(articles)} 篇文章生成摘要...")
    logger.info(f"使用模型: {summarizer.model}")

    try:
        # 生成摘要
        summarized_articles = summarizer.summarize_articles(articles)

        logger.info(f"摘要生成完成: 成功 {len(summarized_articles)}/{len(articles)}")

        return summarized_articles

    except Exception as e:
        logger.error(f"摘要生成失败: {str(e)}")
        logger.warning("将返回未摘要的文章")
        return articles

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description='AI 日报生成系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python src/main.py                                   # 生成当天的日报
  python src/main.py --date 2026-03-25                 # 生成指定日期的日报
  python src/main.py --verbose                         # 显示详细日志
  python src/main.py --no-summarize                    # 跳过摘要生成（仅抓取）
  python src/main.py --config custom/config.yaml       # 使用自定义配置
  python src/main.py --output /tmp/output              # 指定输出目录
        """
    )

    parser.add_argument('--date', type=str, help='指定日期 (YYYY-MM-DD)，默认为今天')
    parser.add_argument('--config', type=str, default='config/sources.yaml', help='配置文件路径')
    parser.add_argument('--output', type=str, default='output', help='输出目录')
    parser.add_argument('--no-summarize', action='store_true', help='跳过摘要生成')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细日志')

    args = parser.parse_args()

    # 设置日志
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    # 打印 banner
    logger.info("="*60)
    logger.info("AI 日报生成系统")
    logger.info("="*60)

    # 加载 .env 文件
    env_path = project_root / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        logger.info(f"已加载环境变量: {env_path}")
    else:
        logger.warning(f"未找到 .env 文件: {env_path}")

    # 验证环境
    if not validate_environment():
        sys.exit(1)

    try:
        # 加载配置
        config = load_config(args.config)

        # 解析目标日期
        if args.date:
            target_date = datetime.strptime(args.date, '%Y-%m-%d')
        else:
            target_date = datetime.now()

        target_date = target_date.replace(tzinfo=timezone.utc)
        logger.info(f"目标日期: {target_date.strftime('%Y-%m-%d')}")

        # 初始化组件
        rss_fetcher = RSSFetcher()
        html_fetcher = HTMLFetcher()

        # 获取 API 配置
        api_key = os.getenv('OPENROUTER_API_KEY')
        base_url = os.getenv('OPENROUTER_BASE_URL')
        model = os.getenv('OPENROUTER_MODEL')

        # 创建摘要生成器
        summarizer_kwargs = {'api_key': api_key}
        if base_url:
            summarizer_kwargs['base_url'] = base_url
        if model:
            summarizer_kwargs['model'] = model

        summarizer = ArticleSummarizer(**summarizer_kwargs)

        # 获取 RSS 配置
        rss_sources = config.get('rss_sources', [])
        html_sources = config.get('html_sources', [])
        settings = config.get('settings', {})

        if not rss_sources and not html_sources:
            logger.error("配置文件中没有找到任何 RSS 源或 HTML 源")
            sys.exit(1)

        logger.info(f"配置中共有 {len(rss_sources)} 个 RSS 源和 {len(html_sources)} 个 HTML 源")

        # 抓取文章
        all_articles = []

        # 抓取 RSS 文章
        if rss_sources:
            # 获取天数设置
            days = settings.get('publish_date_within_days', 3)
            logger.info(f"抓取近 {days} 天的文章")
            rss_articles = fetch_rss_articles(rss_fetcher, rss_sources, target_date, days)
            all_articles.extend(rss_articles)
        else:
            logger.info("未配置 RSS 源，跳过")

        # 抓取 HTML 文章
        if html_sources:
            html_articles = fetch_html_articles(html_fetcher, html_sources)
            all_articles.extend(html_articles)
        else:
            logger.info("未配置 HTML 源，跳过")

        logger.info(f"\n抓取完成，共获取 {len(all_articles)} 篇文章")

        if not all_articles:
            logger.warning("未获取到任何文章，将生成空日报")

        # 生成摘要
        summarized_articles = generate_summaries(summarizer, all_articles, args.no_summarize)

        # 生成 HTML
        logger.info("\n开始生成 HTML 日报...")
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / f"ai-news-{target_date.strftime('%Y-%m-%d')}.html"

        generator = HTMLGenerator()
        generator.generate_html(
            articles=summarized_articles,
            output_path=str(output_path),
            generation_time=datetime.now(),
            title="AI 日报",
            subtitle="近一周精选"
        )

        # 打印摘要统计
        if not args.no_summarize:
            stats = summarizer.get_stats()
            logger.info(f"\nAPI 使用统计:")
            logger.info(f"  - 成功请求: {stats['successful_requests']}")
            logger.info(f"  - 失败请求: {stats['failed_requests']}")
            logger.info(f"  - Token 用量: {stats['total_tokens_used']}")

        logger.info(f"\n" + "="*60)
        logger.info(f"✅ AI 日报生成完成!")
        logger.info(f"📄 文件: {output_path}")
        logger.info(f"📊 文章数: {len(summarized_articles)}")
        logger.info("="*60)

        # 打印下一操作提示
        logger.info("\n您可以:")
        logger.info(f"  1. 在浏览器中打开: open {output_path}")
        logger.info(f"  2. 查看文件内容: cat {output_path}")

    except Exception as e:
        logger.error(f"执行失败: {str(e)}")
        if args.verbose:
            logger.exception("详细错误信息:")
        sys.exit(1)

if __name__ == '__main__':
    main()
