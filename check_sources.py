#!/usr/bin/env python3
"""
信源检查工具
检查配置文件中所有 RSS 和 HTML 源的有效性
"""

import sys
import os
from pathlib import Path
import argparse
import yaml
from typing import List, Dict, Tuple
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.fetchers import RSSFetcher, HTMLFetcher, validate_rss_sources, validate_html_sources


def load_config(config_path: str) -> Dict:
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"加载配置文件失败: {str(e)}", file=sys.stderr)
        sys.exit(1)


def print_header(text: str) -> None:
    """打印标题"""
    print(f"\n{'=' * 70}")
    print(f" {text}")
    print(f"{'=' * 70}")


def print_section(text: str) -> None:
    """打印章节"""
    print(f"\n{text}")
    print('-' * 70)


def check_rss_sources(rss_sources: List[Dict]) -> List[Tuple[Dict, bool, str]]:
    """检查 RSS 源"""
    if not rss_sources:
        print("  未配置 RSS 源")
        return []

    print(f"\n正在检查 {len(rss_sources)} 个 RSS 源...")

    results = validate_rss_sources(rss_sources)

    for i, (source, is_valid, error) in enumerate(results, 1):
        status = "✓" if is_valid else "✗"
        print(f"  {status} [{i}] {source['name']}")
        print(f"    URL: {source['url']}")
        if not is_valid:
            print(f"    错误: {error}")
        print()

    return results


def check_html_sources(html_sources: List[Dict]) -> List[Tuple[Dict, bool, str]]:
    """检查 HTML 源"""
    if not html_sources:
        print("  未配置 HTML 源")
        return []

    print(f"\n正在检查 {len(html_sources)} 个 HTML 源...")

    results = validate_html_sources(html_sources)

    for i, (source, is_valid, error) in enumerate(results, 1):
        status = "✓" if is_valid else "✗"
        print(f"  {status} [{i}] {source['name']}")
        print(f"    URL: {source['url']}")
        print(f"    分类: {source.get('category', '未分类')}")
        if not is_valid:
            print(f"    错误: {error}")
        print()

    return results


def print_summary(rss_results: List[Tuple[Dict, bool, str]],
                  html_results: List[Tuple[Dict, bool, str]]) -> None:
    """打印总结"""
    print_header("检查结果总结")

    # RSS 统计
    total_rss = len(rss_results)
    valid_rss = sum(1 for _, is_valid, _ in rss_results if is_valid)
    invalid_rss = total_rss - valid_rss

    # HTML 统计
    total_html = len(html_results)
    valid_html = sum(1 for _, is_valid, _ in html_results if is_valid)
    invalid_html = total_html - valid_html

    print_section("统计信息")
    print(f"  RSS 源:  {valid_rss}/{total_rss} 有效 ({invalid_rss} 个失效)")
    print(f"  HTML 源: {valid_html}/{total_html} 有效 ({invalid_html} 个失效)")
    print(f"  总计:    {valid_rss + valid_html}/{total_rss + total_html} 有效")

    # 失效源详情
    if invalid_rss > 0 or invalid_html > 0:
        print_section("失效源详情")

        if invalid_rss > 0:
            print("  RSS 源:")
            for source, _, error in rss_results:
                if not _:
                    print(f"    - {source['name']}: {error}")

        if invalid_html > 0:
            print("\n  HTML 源:")
            for source, _, error in html_results:
                if not _:
                    print(f"    - {source['name']}: {error}")

        print("\n  建议:")
        print("    1. 检查网络连接")
        print("    2. 验证 URL 是否正确")
        print("    3. 检查源网站是否可访问")
        print("    4. 考虑移除长期失效的源")
        print("    5. 更新选择器配置（针对 HTML 源）")

    #最终结果
    print_section("最终状态")
    if valid_rss + valid_html == 0:
        print("  ❌ 严重错误: 没有有效的信源！")
        print("  系统将无法正常工作，请立即检查配置。")
        return False
    elif invalid_rss + invalid_html > 0:
        print("  ⚠️  警告: 部分信源无效")
        print("  系统可以运行，但建议修复失效的信源。")
        return True
    else:
        print("  ✅ 所有信源都有效")
        print("  系统配置正确，可以正常运行。")
        return True


def export_valid_sources(rss_results: List[Tuple[Dict, bool, str]],
                        html_results: List[Tuple[Dict, bool, str]],
                        output_file: str) -> None:
    """导出有效的源配置"""
    valid_config = {
        'rss_sources': [source for source, is_valid, _ in rss_results if is_valid],
        'html_sources': [source for source, is_valid, _ in html_results if is_valid]
    }

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(valid_config, f, allow_unicode=True, default_flow_style=False)

        print(f"\n✅ 有效源配置已导出到: {output_file}")
    except Exception as e:
        print(f"\n❌ 导出失败: {str(e)}", file=sys.stderr)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='检查配置文件中所有信源的有效性',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python check_sources.py                          # 检查所有信源
  python check_sources.py --config custom.yaml     # 使用自定义配置
  python check_sources.py --export valid.yaml      # 导出有效源
  python check_sources.py -v                       # 显示详细错误
        """
    )

    parser.add_argument('--config', '-c',
                       type=str,
                       default='config/sources.yaml',
                       help='配置文件路径 (默认: config/sources.yaml)')

    parser.add_argument('--export', '-e',
                       type=str,
                       help='导出有效源配置到指定文件')

    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='显示详细错误信息')

    args = parser.parse_args()

    # 打印 banner
    print_header("AI 日报系统 - 信源检查工具")
    print(f"\n检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"配置文件: {args.config}")

    # 加载配置
    if not os.path.exists(args.config):
        print(f"\n❌ 配置文件不存在: {args.config}", file=sys.stderr)
        sys.exit(1)

    config = load_config(args.config)
    rss_sources = config.get('rss_sources', [])
    html_sources = config.get('html_sources', [])

    print(f"\n信源总数:")
    print(f"  RSS 源: {len(rss_sources)}")
    print(f"  HTML 源: {len(html_sources)}")

    # 检查信源
    rss_results = check_rss_sources(rss_sources)
    html_results = check_html_sources(html_sources)

    # 打印总结
    is_healthy = print_summary(rss_results, html_results)

    # 导出有效源（如果指定）
    if args.export:
        export_valid_sources(rss_results, html_results, args.export)

    # 退出码
    sys.exit(0 if is_healthy else 1)


if __name__ == '__main__':
    main()
