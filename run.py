#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Growth Website System CLI - Unified command-line interface

This is the main entry point for all operations in the Growth Website System.
It provides a unified interface to interact with all agents through commands.

Usage examples:
    # Generate daily report
    python run.py daily --date 2026-03-30 --verbose

    # Add research report
    python run.py research add --file report.html --category tech

    # Create thinking model
    python run.py thinking create --topic "决策框架" --file content.md

    # Update homepage
    python run.py homepage build --optimize

    # Execute all agents
    python run.py all --push

    # Check quality
    python run.py harness check --file output.html

    # View statistics
    python run.py stats --json

    # Push to git
    python run.py git push --message "Update content"
"""

import sys
import os
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.team.coordinator import TeamCoordinator, setup_logging

logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        prog='run.py',
        description='Growth Website System - Unified CLI Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s daily --date 2026-03-30                     # Generate daily report for specific date
  %(prog)s research add --file report.html             # Add research report
  %(prog)s thinking create --topic "AI" --file ai.md   # Create thinking model
  %(prog)s homepage build                              # Build homepage
  %(prog)s all                                         # Execute all agents
  %(prog)s stats                                       # Show system statistics
  %(prog)s --verbose                                   # Run with verbose logging
        """
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    parser.add_argument(
        '--config',
        type=str,
        default='config/sources.yaml',
        help='Configuration file path (default: config/sources.yaml)'
    )

    # Main command subparsers
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Daily command
    daily_parser = subparsers.add_parser('daily', help='Daily report operations')
    daily_parser.add_argument('--date', type=str, help='Date (YYYY-MM-DD), defaults to today')
    daily_parser.add_argument('--no-summarize', action='store_true', help='Skip summary generation')
    daily_parser.add_argument('--push', action='store_true', help='Auto-push to git after generation')
    daily_parser.set_defaults(func=handle_daily)

    # Research command
    research_parser = subparsers.add_parser('research', help='Research report operations')
    research_subparsers = research_parser.add_subparsers(dest='research_action')

    research_add = research_subparsers.add_parser('add', help='Add research report')
    research_add.add_argument('--file', type=str, required=True, help='Report file path')
    research_add.add_argument('--category', type=str, help='Report category')
    research_add.add_argument('--no-push', action='store_true', help='Skip git push')
    research_add.set_defaults(func=handle_research_add)

    research_stats = research_subparsers.add_parser('stats', help='Show research statistics')
    research_stats.set_defaults(func=handle_research_stats)

    # Thinking command
    thinking_parser = subparsers.add_parser('thinking', help='Thinking model operations')
    thinking_subparsers = thinking_parser.add_subparsers(dest='thinking_action')

    thinking_create = thinking_subparsers.add_parser('create', help='Create thinking model')
    thinking_create.add_argument('--topic', type=str, required=True, help='Model topic')
    thinking_create.add_argument('--file', type=str, required=True, help='Content file path')
    thinking_create.add_argument('--model-type', type=str, default='framework', help='Model type')
    thinking_create.add_argument('--no-push', action='store_true', help='Skip git push')
    thinking_create.set_defaults(func=handle_thinking_create)

    thinking_update = thinking_subparsers.add_parser('update', help='Update thinking model')
    thinking_update.add_argument('--id', type=str, required=True, help='Model ID')
    thinking_update.add_argument('--file', type=str, required=True, help='Updates file path')
    thinking_update.set_defaults(func=handle_thinking_update)

    # Homepage command
    homepage_parser = subparsers.add_parser('homepage', help='Homepage operations')
    homepage_parser.add_argument('--optimize', action='store_true', help='Enable optimizations')
    homepage_parser.set_defaults(func=handle_homepage)

    # All command
    all_parser = subparsers.add_parser('all', help='Execute all agents')
    all_parser.add_argument('--push', action='store_true', help='Push to git after completion')
    all_parser.add_argument('--skip-daily', action='store_true', help='Skip daily report generation')
    all_parser.set_defaults(func=handle_all)

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show system statistics')
    stats_parser.add_argument('--json', action='store_true', help='Output as JSON')
    stats_parser.add_argument('--agent', type=str, help='Show specific agent stats')
    stats_parser.set_defaults(func=handle_stats)

    # Git command
    git_parser = subparsers.add_parser('git', help='Git operations')
    git_subparsers = git_parser.add_subparsers(dest='git_action')

    git_push = git_subparsers.add_parser('push', help='Push changes to git')
    git_push.add_argument('--message', '-m', type=str, help='Commit message')
    git_push.set_defaults(func=handle_git_push)

    # Harness command
    harness_parser = subparsers.add_parser('harness', help='Harness operations')
    harness_subparsers = harness_parser.add_subparsers(dest='harness_action')

    harness_check = harness_subparsers.add_parser('check', help='Check file quality')
    harness_check.add_argument('--file', type=str, required=True, help='File to check')
    harness_check.set_defaults(func=handle_harness_check)

    harness_info = harness_subparsers.add_parser('info', help='Show harness info')
    harness_info.set_defaults(func=handle_harness_info)

    return parser


def format_result(result: Dict[str, Any], args: argparse.Namespace) -> None:
    """Format and display execution result."""
    if args.command:
        print(f"\n{'='*60}")
        print(f"Command: {args.command}")
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"{'='*60}")

        if result.get('status') == 'success':
            if 'result' in result:
                print("\nResults:")
                print(json.dumps(result['result'], indent=2, ensure_ascii=False))
            print(f"\nDuration: {result.get('duration', 0):.2f}s")
        else:
            print(f"\nError: {result.get('error', 'Unknown error')}")

        print(f"{'='*60}\n")
    else:
        # Raw output for non-command results
        print(json.dumps(result, indent=2, ensure_ascii=False))


def handle_daily(args: argparse.Namespace, coordinator: TeamCoordinator) -> Dict[str, Any]:
    """Handle daily command."""
    command_parts = ['daily', 'generate']
    if args.date:
        command_parts.extend(['--date', args.date])
    if args.no_summarize:
        command_parts.append('--no-summarize')

    result = coordinator.execute(' '.join(command_parts))

    if result['status'] == 'success' and args.push:
        git_result = git_push(coordinator, 'Update daily report')
        result['git_push'] = git_result

    return result


def handle_research_add(args: argparse.Namespace, coordinator: TeamCoordinator) -> Dict[str, Any]:
    """Handle research add command."""
    command_parts = ['research', 'add', '--file', args.file]
    if args.category:
        command_parts.extend(['--category', args.category])

    result = coordinator.execute(' '.join(command_parts))

    if result['status'] == 'success' and not args.no_push:
        git_result = git_push(coordinator, f'Add research report: {args.file}')
        result['git_push'] = git_result

    return result


def handle_research_stats(args: argparse.Namespace, coordinator: TeamCoordinator) -> Dict[str, Any]:
    """Handle research stats command."""
    stats = coordinator.agents['research'].get_category_stats()
    return {
        'status': 'success',
        'stats': stats
    }


def handle_thinking_create(args: argparse.Namespace, coordinator: TeamCoordinator) -> Dict[str, Any]:
    """Handle thinking create command."""
    command_parts = ['thinking', 'create', '--topic', args.topic, '--file', args.file]
    if args.model_type:
        command_parts.extend(['--model-type', args.model_type])

    result = coordinator.execute(' '.join(command_parts))

    if result['status'] == 'success' and not args.no_push:
        git_result = git_push(coordinator, f'Add thinking model: {args.topic}')
        result['git_push'] = git_result

    return result


def handle_thinking_update(args: argparse.Namespace, coordinator: TeamCoordinator) -> Dict[str, Any]:
    """Handle thinking update command."""
    command_parts = ['thinking', 'update', '--id', args.id, '--file', args.file]
    result = coordinator.execute(' '.join(command_parts))
    return result


def handle_homepage(args: argparse.Namespace, coordinator: TeamCoordinator) -> Dict[str, Any]:
    """Handle homepage command."""
    command_parts = ['homepage', 'build']
    if args.optimize:
        command_parts.append('--optimize')

    result = coordinator.execute(' '.join(command_parts))
    return result


def handle_all(args: argparse.Namespace, coordinator: TeamCoordinator) -> Dict[str, Any]:
    """Handle all command."""
    result = coordinator.execute_all()

    if args.push and result.get('status') == 'completed':
        git_result = git_push(coordinator, 'Update all content')
        result['git_push'] = git_result

    return result


def handle_stats(args: argparse.Namespace, coordinator: TeamCoordinator) -> Dict[str, Any]:
    """Handle stats command."""
    if args.agent:
        agent_status = coordinator.get_agent_status()
        if args.agent in agent_status:
            return {
                'status': 'success',
                'agent': args.agent,
                'stats': agent_status[args.agent]
            }
        else:
            return {
                'status': 'error',
                'error': f'Unknown agent: {args.agent}'
            }

    stats = coordinator.get_stats()

    if args.json:
        return stats
    else:
        # Human-readable format
        print(f"\n{'='*60}")
        print("SYSTEM STATISTICS")
        print(f"{'='*60}")
        print(f"\nSystem Operations:")
        print(f"  Total: {stats['system']['total_operations']}")
        print(f"  Successful: {stats['system']['successful_operations']}")
        print(f"  Failed: {stats['system']['failed_operations']}")
        print(f"  Success Rate: {stats['system']['success_rate']:.1%}")

        print(f"\nContent Statistics:")
        print(f"  Daily Reports: {stats['content']['daily_reports']}")
        print(f"  Research Reports: {stats['content']['research_reports']}")
        print(f"  Thinking Models: {stats['content']['thinking_models']}")
        print(f"  Today's Items: {stats['content']['today_items']}")

        print(f"\nAgent Status:")
        for agent_name, agent_stats in stats['agents'].items():
            print(f"  {agent_name}:")
            print(f"    Operations: {agent_stats['operation_count']}")
            print(f"    Errors: {agent_stats['error_count']}")
            print(f"    Success Rate: {agent_stats['success_rate']:.1%}")

        print(f"{'='*60}\n")

        return {'status': 'success', 'displayed': True}


def handle_harness_check(args: argparse.Namespace, coordinator: TeamCoordinator) -> Dict[str, Any]:
    """Handle harness check command."""
    file_path = Path(args.file)
    if not file_path.exists():
        return {
            'status': 'error',
            'error': f'File not found: {args.file}'
        }

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    quality_metrics = coordinator.harness.check_quality(content)

    return {
        'status': 'success',
        'file': args.file,
        'quality_score': quality_metrics.overall_score,
        'metrics': quality_metrics.__dict__ if hasattr(quality_metrics, '__dict__') else str(quality_metrics)
    }


def handle_harness_info(args: argparse.Namespace, coordinator: TeamCoordinator) -> Dict[str, Any]:
    """Handle harness info command."""
    info = coordinator.harness.get_system_info()
    return {
        'status': 'success',
        'info': info
    }


def git_push(coordinator: TeamCoordinator, message: str = 'Update website content') -> Dict[str, Any]:
    """Helper function to push changes to git."""
    try:
        import subprocess

        print(f"\nPushing changes to git...")

        # Add all changes
        subprocess.run(['git', 'add', '.'], check=True, capture_output=True)

        # Commit
        commit_result = subprocess.run(
            ['git', 'commit', '-m', message],
            capture_output=True,
            text=True
        )

        if commit_result.returncode != 0:
            if 'nothing to commit' not in commit_result.stderr:
                raise Exception(f'Git commit failed: {commit_result.stderr}')

        # Push
        push_result = subprocess.run(
            ['git', 'push'],
            capture_output=True,
            text=True
        )

        if push_result.returncode != 0:
            raise Exception(f'Git push failed: {push_result.stderr}')

        return {
            'status': 'success',
            'message': 'Changes pushed to git successfully'
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


def handle_git_push(args: argparse.Namespace, coordinator: TeamCoordinator) -> Dict[str, Any]:
    """Handle git push command."""
    message = args.message or f'Update website content - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    return git_push(coordinator, message)


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    try:
        # Initialize coordinator
        coordinator = TeamCoordinator(config_path=args.config)

        # Handle command
        if hasattr(args, 'func'):
            result = args.func(args, coordinator)
            if not getattr(args, 'json', False) and not getattr(args, 'command', '') == 'stats':
                format_result(result, args)
            else:
                print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.command == 'stats':
            result = handle_stats(args, coordinator)
        else:
            parser.print_help()
            sys.exit(1)

        # Exit with appropriate code
        if isinstance(result, dict) and result.get('status') == 'error':
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        logger.error(f'Fatal error: {e}')
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
