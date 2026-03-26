# -*- coding: utf-8 -*-
"""
OpenRouter API 摘要生成模块
使用 OpenRouter API 为文章生成中文摘要
"""

import logging
import os
import time
from typing import List, Dict, Optional, Union
from datetime import datetime
import openai
from tenacity import retry, stop_after_attempt, wait_exponential

# 配置日志
logger = logging.getLogger(__name__)

# 默认配置
DEFAULT_MODEL = "anthropic/claude-3-sonnet"
DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MAX_TOKENS = 500
DEFAULT_TEMPERATURE = 0.3


class ArticleSummarizer:
    """
    文章摘要生成器
    使用 OpenRouter API 为文章生成中文摘要
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None,
                 max_tokens: int = DEFAULT_MAX_TOKENS, temperature: float = DEFAULT_TEMPERATURE,
                 rate_limit_delay: float = 1.0):
        """
        初始化摘要生成器

        Args:
            api_key: OpenRouter API 密钥
            base_url: API 基础 URL
            model: 使用的模型名称
            max_tokens: 生成的最大 token 数
            temperature: 生成温度（控制创造性）
            rate_limit_delay: 请求间隔（秒）
        """
        # 从环境变量或参数获取配置
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.base_url = base_url or os.getenv('OPENROUTER_BASE_URL', DEFAULT_BASE_URL)
        self.model = model or os.getenv('OPENROUTER_MODEL', DEFAULT_MODEL)
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.rate_limit_delay = rate_limit_delay

        if not self.api_key:
            raise ValueError("未提供 OpenRouter API 密钥。请设置 OPENROUTER_API_KEY 环境变量或通过参数传入。")

        # 初始化 OpenAI 客户端
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        # 统计信息
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_tokens_used': 0,
            'total_articles_processed': 0
        }

    def summarize_articles(self, articles: List[Dict], batch_size: int = 5) -> List[Dict]:
        """
        批量生成文章摘要

        Args:
            articles: 文章列表，每个文章需要包含 title 和 summary/content
            batch_size: 批处理大小（用于控制并发，实际为串行处理）

        Returns:
            包含摘要的文章列表
        """
        if not articles:
            logger.warning("文章列表为空")
            return []

        logger.info(f"开始生成 {len(articles)} 篇文章的摘要，使用模型: {self.model}")

        summarized_articles = []
        failed_articles = []

        for i, article in enumerate(articles, 1):
            try:
                logger.info(f"处理文章 {i}/{len(articles)}: {article.get('title', 'Untitled')[:50]}...")

                # 生成摘要
                summary = self._summarize_single(article)

                if summary:
                    # 添加摘要到文章
                    article_with_summary = article.copy()
                    article_with_summary['summary'] = summary
                    summarized_articles.append(article_with_summary)
                    self.stats['successful_requests'] += 1
                    logger.info(f"✓ 摘要生成成功 ({len(summary)} 字)")
                else:
                    failed_articles.append(article)
                    self.stats['failed_requests'] += 1
                    logger.warning(f"✗ 摘要生成失败")

                self.stats['total_articles_processed'] += 1

                # 速率限制
                if i < len(articles):
                    time.sleep(self.rate_limit_delay)

            except Exception as e:
                logger.error(f"处理文章时出错: {str(e)}")
                failed_articles.append(article)
                self.stats['failed_requests'] += 1
                self.stats['total_articles_processed'] += 1

        # 记录统计信息
        self._log_stats()

        if failed_articles:
            logger.warning(f"{len(failed_articles)} 篇文章摘要生成失败")

        return summarized_articles

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _summarize_single(self, article: Dict) -> Optional[str]:
        """
        为单篇文章生成摘要（带重试）

        Args:
            article: 文章字典，需要包含 title 和 summary/content

        Returns:
            生成的摘要或 None
        """
        title = article.get('title', '')
        content = article.get('summary', '') or article.get('content', '')

        if not content:
            logger.warning(f"文章 '{title}' 没有内容，无法生成摘要")
            return None

        # 构建 prompt
        prompt = self._build_prompt(title, content)

        try:
            self.stats['total_requests'] += 1

            # 调用 API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes articles in Chinese."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            # 提取摘要
            summary = response.choices[0].message.content.strip()

            # 清理摘要（移除可能的多余内容）
            summary = self._clean_summary(summary)

            # 更新 token 统计
            if response.usage:
                self.stats['total_tokens_used'] += response.usage.total_tokens

            return summary

        except Exception as e:
            logger.error(f"API 调用失败: {str(e)}")
            raise  # 让重试装饰器捕获异常

    def _build_prompt(self, title: str, content: str) -> str:
        """
        构建摘要生成的 prompt

        Args:
            title: 文章标题
            content: 文章内容

        Returns:
            prompt 字符串
        """
        # 限制内容长度，避免超过 token 限制
        max_content_length = 3000  # 大约 1000 个汉字
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."

        prompt = f"""请用中文总结以下文章内容，提取核心要点，要求：

1. 准确理解文章的核心主题和关键信息
2. 用简洁、清晰的语言概括主要内容
3. 摘要长度控制在 150-200 字之间
4. 不要添加原文没有的信息或个人观点
5. 保持客观、中立的语气

文章标题：{title}

文章内容：
{content}

中文摘要："""

        return prompt

    def _clean_summary(self, summary: str) -> str:
        """
        清理生成的摘要

        Args:
            summary: 原始摘要

        Returns:
            清理后的摘要
        """
        # 移除常见的前缀
        prefixes_to_remove = [
            "中文摘要：",
            "摘要：",
            "以下是摘要：",
            "这篇文章的摘要：",
            "文章的摘要：",
        ]

        for prefix in prefixes_to_remove:
            if summary.startswith(prefix):
                summary = summary[len(prefix):].strip()

        # 移除常见的后缀
        suffixes_to_remove = [
            "（摘要）",
            "(摘要)",
            "【摘要】",
            "[摘要]",
        ]

        for suffix in suffixes_to_remove:
            if summary.endswith(suffix):
                summary = summary[:-len(suffix)].strip()

        # 确保摘要以句号结尾（如果不是以句号、问号或感叹号结尾）
        if summary and not summary[-1] in '。？！':
            summary += '。'

        return summary

    def summarize_with_different_models(self, article: Dict, models: List[str]) -> Dict[str, Optional[str]]:
        """
        使用多个模型生成摘要（用于测试不同模型的效果）

        Args:
            article: 文章
            models: 模型列表

        Returns:
            各模型生成的摘要
        """
        summaries = {}

        for model in models:
            logger.info(f"使用模型 {model} 生成摘要...")
            try:
                # 临时切换模型
                original_model = self.model
                self.model = model

                summary = self._summarize_single(article)
                if summary:
                    summaries[model] = summary
                    logger.info(f"模型 {model} 生成成功 ({len(summary)} 字)")
                else:
                    summaries[model] = None
                    logger.warning(f"模型 {model} 生成失败")

                # 恢复原始模型
                self.model = original_model

                # 速率限制
                time.sleep(self.rate_limit_delay)

            except Exception as e:
                logger.error(f"模型 {model} 出错: {str(e)}")
                summaries[model] = None

        return summaries

    def _log_stats(self):
        """记录统计信息"""
        success_rate = (self.stats['successful_requests'] / max(self.stats['total_requests'], 1)) * 100
        logger.info(
            f"\n摘要生成统计:\n"
            f"  - 总请求数: {self.stats['total_requests']}\n"
            f"  - 成功请求: {self.stats['successful_requests']}\n"
            f"  - 失败请求: {self.stats['failed_requests']}\n"
            f"  - 成功率: {success_rate:.1f}%\n"
            f"  - 总 Token 使用: {self.stats['total_tokens_used']}\n"
            f"  - 处理文章总数: {self.stats['total_articles_processed']}"
        )

    def get_stats(self) -> Dict:
        """
        获取统计信息

        Returns:
            统计信息字典
        """
        return self.stats.copy()


class BatchSummarizer:
    """
    批量摘要生成器（用于处理大量文章）
    """

    def __init__(self, summarizer: ArticleSummarizer, batch_size: int = 10):
        """
        初始化批量摘要生成器

        Args:
            summarizer: 文章摘要生成器实例
            batch_size: 每批处理的文章数
        """
        self.summarizer = summarizer
        self.batch_size = batch_size

    def process_large_batch(self, articles: List[Dict]) -> List[Dict]:
        """
        处理大量文章（分批处理）

        Args:
            articles: 文章列表

        Returns:
            包含摘要的文章列表
        """
        if not articles:
            return []

        all_results = []
        total_batches = (len(articles) + self.batch_size - 1) // self.batch_size

        logger.info(f"开始分批处理 {len(articles)} 篇文章，共 {total_batches} 批")

        for i in range(0, len(articles), self.batch_size):
            batch = articles[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1

            logger.info(f"处理第 {batch_num}/{total_batches} 批，包含 {len(batch)} 篇文章")

            # 生成摘要
            results = self.summarizer.summarize_articles(batch)
            all_results.extend(results)

            # 批次之间增加延迟
            if i + self.batch_size < len(articles):
                logger.info("等待 5 秒后继续...")
                time.sleep(5)

        return all_results


# 预设模型配置（价格和性能的平衡）
MODEL_CONFIGS = {
    'fast': {
        'model': 'anthropic/claude-3-haiku-20240307',
        'description': '快速经济型',
        'rate_limit_delay': 0.5
    },
    'balanced': {
        'model': 'anthropic/claude-3-sonnet',
        'description': '平衡型（推荐）',
        'rate_limit_delay': 1.0
    },
    'quality': {
        'model': 'anthropic/claude-3-opus',
        'description': '高质量型',
        'rate_limit_delay': 2.0
    }
}


def create_summarizer(preset: str = 'balanced', **kwargs) -> ArticleSummarizer:
    """
    创建摘要生成器（使用预设配置）

    Args:
        preset: 预设配置名 ('fast', 'balanced', 'quality')
        **kwargs: 其他参数

    Returns:
        摘要生成器实例
    """
    if preset not in MODEL_CONFIGS:
        raise ValueError(f"无效的预设: {preset}。请选择: {list(MODEL_CONFIGS.keys())}")

    config = MODEL_CONFIGS[preset]

    return ArticleSummarizer(
        model=config['model'],
        rate_limit_delay=config['rate_limit_delay'],
        **kwargs
    )


if __name__ == '__main__':
    # 测试代码
    import os
    from dotenv import load_dotenv

    # 加载环境变量
    load_dotenv()

    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 获取 API Key
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        logger.error("请设置 OPENROUTER_API_KEY 环境变量")
        exit(1)

    # 测试摘要生成
    test_articles = [
        {
            'title': '测试文章 1',
            'summary': '这是一篇关于人工智能和机器学习的文章。文章讨论了最新的深度学习技术，包括神经网络和大型语言模型的发展。作者还探讨了这些技术在实际应用中的挑战和机遇。',
            'link': 'https://example.com/article1'
        },
        {
            'title': '测试文章 2',
            'summary': '区块链技术正在改变金融行业。本文介绍了去中心化金融（DeFi）的基本概念，以及它如何提供更安全、透明的金融服务。文中还讨论了监管挑战和未来发展趋势。',
            'link': 'https://example.com/article2'
        }
    ]

    try:
        # 创建摘要生成器
        summarizer = ArticleSummarizer(api_key=api_key)

        # 生成摘要
        results = summarizer.summarize_articles(test_articles)

        # 显示结果
        print("\n" + "="*80)
        print("摘要生成结果:")
        print("="*80)

        for i, article in enumerate(results, 1):
            print(f"\n{i}. {article['title']}")
            print(f"   链接: {article['link']}")
            print(f"   摘要: {article['summary']}")

    except Exception as e:
        logger.error(f"测试失败: {str(e)}")
