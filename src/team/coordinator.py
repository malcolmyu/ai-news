#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Team Coordinator - Central orchestration layer for Growth Website System

This module provides the TeamCoordinator class that:
1. Manages all agents (DailyReporter, ResearchManager, ThinkingSystem, HomepageBuilder)
2. Parses and dispatches commands to appropriate agents
3. Tracks operation status and errors
4. Manages configuration and state
5. Provides unified interface for the CLI
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple, Union
import argparse
import re
from dataclasses import dataclass, asdict

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from harness import HarnessController
from agents import DailyReporterAgent, ResearchManagerAgent, ThinkingSystemAgent, HomepageBuilderAgent

logger = logging.getLogger(__name__)


@dataclass
class OperationLog:
    """Operation log entry."""
    timestamp: str
    command: str
    agent: str
    action: str
    params: Dict[str, Any]
    result: str
    error: Optional[str]
    duration: float


@dataclass
class AgentStatus:
    """Agent status information."""
    name: str
    ready: bool
    last_operation: Optional[str]
    operation_count: int
    error_count: int


class TeamCoordinator:
    """
    Team Coordinator - Central orchestration for the Growth Website System.

    Responsible for:
    - Coordinating all agents
    - Command parsing and dispatch
    - State management
    - Error handling
    - Result aggregation
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Team Coordinator.

        Args:
            config_path: Path to configuration file
        """
        self.project_root = Path(__file__).parent.parent.parent
        self.config_path = config_path or self.project_root / "config" / "sources.yaml"
        self.data_dir = self.project_root / "data"
        self.output_dir = self.project_root / "output"
        self.docs_dir = self.project_root / "docs"

        # Initialize Harness Controller
        self.harness = HarnessController()

        # Initialize all agents
        self.agents = {
            "daily": DailyReporterAgent(self.harness, str(self.config_path)),
            "research": ResearchManagerAgent(self.harness),
            "thinking": ThinkingSystemAgent(self.harness),
            "homepage": HomepageBuilderAgent(self.harness)
        }

        # Operation tracking
        self.operation_log: List[OperationLog] = []
        self.agent_status: Dict[str, AgentStatus] = {
            name: AgentStatus(name=name, ready=True, last_operation=None, operation_count=0, error_count=0)
            for name in self.agents.keys()
        }

        # Ensure directories
        (self.project_root / "data" / "system").mkdir(parents=True, exist_ok=True)

        logger.info("TeamCoordinator initialized with all agents")

    def parse_command(self, command: str) -> Tuple[str, str, Dict[str, Any]]:
        """
        Parse command string into agent, action, and parameters.

        Args:
            command: Command string (e.g., "daily generate --date 2026-03-30")

        Returns:
            Tuple of (agent_name, action, params)

        Raises:
            ValueError: If command format is invalid
        """
        logger.info(f"Parsing command: {command}")

        # Split command into parts
        parts = command.strip().split()
        if not parts:
            raise ValueError("Empty command")

        # Extract agent and action
        agent_name = parts[0]
        action = parts[1] if len(parts) > 1 else "execute"

        # Parse parameters
        params = {}
        i = 2
        while i < len(parts):
            if parts[i].startswith("--"):
                param_name = parts[i][2:]
                if i + 1 < len(parts) and not parts[i + 1].startswith("--"):
                    params[param_name] = parts[i + 1]
                    i += 2
                else:
                    params[param_name] = True
                    i += 1
            else:
                # Handle positional arguments
                if "args" not in params:
                    params["args"] = []
                params["args"].append(parts[i])
                i += 1

        logger.info(f"Parsed command -> agent: {agent_name}, action: {action}, params: {params}")
        return agent_name, action, params

    def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a command by parsing and dispatching to appropriate agent.

        Args:
            command: Command string to execute
            **kwargs: Additional keyword arguments

        Returns:
            Dict containing execution result, status, and metadata
        """
        start_time = datetime.now()
        operation_id = len(self.operation_log)

        try:
            # Parse command
            agent_name, action, params = self.parse_command(command)

            # Validate agent
            if agent_name not in self.agents:
                raise ValueError(f"Unknown agent: {agent_name}. Available: {list(self.agents.keys())}")

            # Update agent status
            self.agent_status[agent_name].last_operation = f"{action}"
            self.agent_status[agent_name].operation_count += 1

            # Merge kwargs into params
            params.update(kwargs)

            # Execute action on agent
            logger.info(f"Executing {action} on {agent_name} with params: {params}")
            result = self._execute_agent_action(agent_name, action, params)

            # Check if homepage should be updated
            if self.should_update_homepage(command):
                logger.info("Homepage update triggered")
                homepage_result = self.agents["homepage"].build_homepage(updates={agent_name: result})
                result["homepage_updated"] = True
                result["homepage_result"] = homepage_result

            # Log success
            duration = (datetime.now() - start_time).total_seconds()
            self._log_operation(
                command=command,
                agent=agent_name,
                action=action,
                params=params,
                result="success",
                error=None,
                duration=duration
            )

            logger.info(f"Command executed successfully in {duration:.2f}s")

            return {
                "status": "success",
                "agent": agent_name,
                "action": action,
                "result": result,
                "duration": duration,
                "operation_id": operation_id
            }

        except Exception as e:
            # Log error
            duration = (datetime.now() - start_time).total_seconds()
            self._log_operation(
                command=command,
                agent=agent_name if 'agent_name' in locals() else "unknown",
                action=action if 'action' in locals() else "unknown",
                params=params if 'params' in locals() else {},
                result="error",
                error=str(e),
                duration=duration
            )

            # Update agent error count
            if 'agent_name' in locals() and agent_name in self.agent_status:
                self.agent_status[agent_name].error_count += 1

            logger.error(f"Command execution failed: {str(e)}")

            return {
                "status": "error",
                "error": str(e),
                "agent": agent_name if 'agent_name' in locals() else "unknown",
                "action": action if 'action' in locals() else "unknown",
                "duration": duration,
                "operation_id": operation_id
            }

    def _execute_agent_action(self, agent_name: str, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute action on specific agent.

        Args:
            agent_name: Name of the agent
            action: Action to perform
            params: Parameters for the action

        Returns:
            Result from agent execution
        """
        agent = self.agents[agent_name]

        if agent_name == "daily":
            if action == "generate" or action == "execute":
                return agent.generate_daily_report(
                    date=params.get("date"),
                    no_summarize="no-summarize" in params
                )
            else:
                raise ValueError(f"Unknown action '{action}' for daily agent")

        elif agent_name == "research":
            if action == "add" or action == "execute":
                report_file = params.get("file")
                if not report_file:
                    raise ValueError("Missing required parameter: --file")
                return agent.process_report(
                    Path(report_file),
                    category=params.get("category")
                )
            elif action == "stats":
                return agent.get_category_stats()
            else:
                raise ValueError(f"Unknown action '{action}' for research agent")

        elif agent_name == "thinking":
            if action == "create" or action == "execute":
                topic = params.get("topic")
                content_file = params.get("file")
                if not topic:
                    raise ValueError("Missing required parameter: --topic")
                if not content_file:
                    raise ValueError("Missing required parameter: --file")

                with open(content_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                return agent.create_thinking_model(
                    topic=topic,
                    content=content,
                    model_type=params.get("model_type", "framework")
                )
            elif action == "update":
                model_id = params.get("id")
                updates_file = params.get("file")
                if not model_id:
                    raise ValueError("Missing required parameter: --id")
                if not updates_file:
                    raise ValueError("Missing required parameter: --file")

                with open(updates_file, 'r', encoding='utf-8') as f:
                    updates = json.load(f)

                return agent.update_model(model_id, updates)
            else:
                raise ValueError(f"Unknown action '{action}' for thinking agent")

        elif agent_name == "homepage":
            if action == "build" or action == "execute":
                return {"html": agent.build_homepage(updates=params.get("updates"))}
            else:
                raise ValueError(f"Unknown action '{action}' for homepage agent")

        else:
            raise ValueError(f"Unknown agent: {agent_name}")

    def should_update_homepage(self, command: str) -> bool:
        """
        Determine if homepage should be updated after executing command.

        Args:
            command: The command that was executed

        Returns:
            True if homepage should be updated
        """
        agent_name = command.split()[0] if command.split() else ""

        # Update homepage after these agents execute
        update_triggers = ["daily", "research", "thinking"]

        return agent_name in update_triggers

    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get status of all agents.

        Returns:
            Dict containing status information for all agents
        """
        return {
            agent_name: {
                "ready": status.ready,
                "last_operation": status.last_operation,
                "operation_count": status.operation_count,
                "error_count": status.error_count,
                "success_rate": (
                    (status.operation_count - status.error_count) / status.operation_count
                    if status.operation_count > 0 else 0.0
                )
            }
            for agent_name, status in self.agent_status.items()
        }

    def _log_operation(self, command: str, agent: str, action: str,
                      params: Dict[str, Any], result: str,
                      error: Optional[str], duration: float):
        """
        Log operation to operation log and file.

        Args:
            command: Original command string
            agent: Agent name
            action: Action performed
            params: Parameters used
            result: Result status (success/error)
            error: Error message if any
            duration: Operation duration in seconds
        """
        log_entry = OperationLog(
            timestamp=datetime.now(timezone.utc).isoformat(),
            command=command,
            agent=agent,
            action=action,
            params=params,
            result=result,
            error=error,
            duration=duration
        )

        self.operation_log.append(log_entry)

        # Save to file
        log_file = self.project_root / "data" / "system" / "operation_log.json"
        try:
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    existing_logs = json.load(f)
            else:
                existing_logs = []

            existing_logs.append(asdict(log_entry))

            # Keep only last 1000 operations
            if len(existing_logs) > 1000:
                existing_logs = existing_logs[-1000:]

            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(existing_logs, f, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"Failed to save operation log: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get system statistics.

        Returns:
            Dict containing system statistics
        """
        total_ops = len(self.operation_log)
        successful_ops = sum(1 for log in self.operation_log if log.result == "success")
        failed_ops = total_ops - successful_ops

        # Get stats from homepage builder
        homepage_stats = self.agents["homepage"].generate_stats()

        return {
            "system": {
                "total_operations": total_ops,
                "successful_operations": successful_ops,
                "failed_operations": failed_ops,
                "success_rate": successful_ops / total_ops if total_ops > 0 else 0.0,
                "agents": len(self.agents)
            },
            "content": {
                "daily_reports": homepage_stats.daily_total,
                "research_reports": homepage_stats.research_total,
                "thinking_models": homepage_stats.thinking_total,
                "today_items": homepage_stats.daily_today
            },
            "agents": self.get_agent_status()
        }

    def execute_all(self) -> Dict[str, Any]:
        """
        Execute all agents for complete system update.

        Returns:
            Dict containing results from all agents
        """
        logger.info("Executing all agents for complete system update")

        results = {}
        errors = []

        # Execute daily agent
        try:
            logger.info("Executing daily agent...")
            results["daily"] = self.execute("daily generate")
        except Exception as e:
            logger.error(f"Daily agent failed: {e}")
            errors.append(f"Daily: {str(e)}")
            results["daily"] = {"status": "error", "error": str(e)}

        # Execute research agent (if reports exist)
        research_output_dir = self.project_root / "output" / "research"
        if research_output_dir.exists():
            try:
                logger.info("Processing research reports...")
                report_files = list(research_output_dir.glob("*.html"))
                for report_file in report_files[:5]:  # Process first 5 reports
                    results[f"research_{report_file.stem}"] = self.execute(f"research add --file {report_file}")
            except Exception as e:
                logger.error(f"Research agent failed: {e}")
                errors.append(f"Research: {str(e)}")
                results["research"] = {"status": "error", "error": str(e)}

        # Execute thinking agent (if models exist)
        thinking_dir = self.project_root / "data" / "thinking"
        if thinking_dir.exists():
            try:
                logger.info("Processing thinking models...")
                models_file = thinking_dir / "models.json"
                if models_file.exists():
                    with open(models_file, 'r', encoding='utf-8') as f:
                        models_data = json.load(f)
                    results["thinking"] = {"models_count": len(models_data.get("models", []))}
            except Exception as e:
                logger.error(f"Thinking agent failed: {e}")
                errors.append(f"Thinking: {str(e)}")

        # Always update homepage last
        try:
            logger.info("Updating homepage...")
            results["homepage"] = self.execute("homepage build")
        except Exception as e:
            logger.error(f"Homepage agent failed: {e}")
            errors.append(f"Homepage: {str(e)}")
            results["homepage"] = {"status": "error", "error": str(e)}

        return {
            "status": "completed_with_errors" if errors else "completed",
            "results": results,
            "errors": errors if errors else None,
            "timestamp": datetime.now().isoformat()
        }


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


if __name__ == "__main__":
    # For testing
    coordinator = TeamCoordinator()

    # Test stats
    print("\nSystem Stats:")
    print(json.dumps(coordinator.get_stats(), indent=2, ensure_ascii=False))
