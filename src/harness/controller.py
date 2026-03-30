"""
Harness Controller - Main orchestration layer for AI News System constraints.

This module provides the central controller that coordinates validation, styling,
and templating across the entire AI News System.
"""

from typing import Dict, List, Any, Optional, Union
import yaml
import logging
from pathlib import Path
import os

from .validators import ContentValidator, ValidationResult, QualityMetrics
from .styles import StyleConstraints
from .templates import TemplateManager, TemplateContext

logger = logging.getLogger(__name__)


class HarnessController:
    """
    Main controller for AI News System constraint management.

    This class orchestrates all constraint control activities including:
    - Configuration management
    - Content validation
    - Style application
    - Template rendering
    - Quality checking
    """

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """
        Initialize HarnessController.

        Args:
            config_path: Path to harness configuration file
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config: Dict[str, Any] = {}
        self.validator: ContentValidator = None
        self.style_manager: StyleConstraints = None
        self.template_manager: TemplateManager = None

        self._load_config()
        self._initialize_components()

        logger.info("HarnessController initialized")

    def _get_default_config_path(self) -> Path:
        """Get default configuration file path."""
        # Try multiple possible locations
        possible_paths = [
            Path("config/harness.yaml"),
            Path("src/config/harness.yaml"),
            Path("etc/harness.yaml"),
            Path.cwd() / "config" / "harness.yaml"
        ]

        for path in possible_paths:
            if path.exists():
                logger.debug(f"Found default config at: {path}")
                return path

        logger.warning("No default config file found, using empty configuration")
        return Path("config/harness.yaml")

    def _load_config(self):
        """Load configuration from file."""
        try:
            if not self.config_path.exists():
                logger.warning(f"Config file not found: {self.config_path}")
                self.config = self._get_default_config()
                return

            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}

            logger.info(f"Configuration loaded from {self.config_path}")

        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            self.config = self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration when file is not available."""
        return {
            'styles': {
                'theme': 'default',
                'colors': {},
                'fonts': {},
                'layouts': {}
            },
            'constraints': {
                'validation': {
                    'summary_length_min': 50,
                    'summary_length_max': 300,
                    'quality_threshold': 0.7
                }
            },
            'templates': {
                'default_template': 'minimal',
                'strict_validation': True
            }
        }

    def _initialize_components(self):
        """Initialize sub-components with configuration."""
        try:
            # Initialize validator
            validation_config = self.config.get('constraints', {}).get('validation', {})
            self.validator = ContentValidator(validation_config)

            # Initialize style manager
            style_config = self.config.get('styles', {})
            self.style_manager = StyleConstraints(style_config)

            # Initialize template manager
            template_config = self.config.get('templates', {})
            self.template_manager = TemplateManager(template_config)

            logger.debug("All components initialized")

        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise

    def validate_article(self, article_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate article content and metadata.

        Args:
            article_data: Dictionary containing:
                - content: Article body content (required)
                - summary: Article summary (optional)
                - keywords: List of keywords (optional)
                - title: Article title (optional)

        Returns:
            ValidationResult with validation status
        """
        logger.info("Validating article")

        # Extract data with defaults
        content = article_data.get('content', '')
        metadata = article_data.copy()

        # Use validator
        result = self.validator.validate_article(content, metadata)

        logger.info(f"Article validation result: {'Valid' if result.is_valid else 'Invalid'} (score: {result.score:.2f})")
        return result

    def validate_report(self, report_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate report content and structure.

        Args:
            report_data: Dictionary containing:
                - content: Report body content (required)
                - sections: List of required section names (optional)
                - keywords: List of keywords (optional)
                - title: Report title (optional)

        Returns:
            ValidationResult with validation status
        """
        logger.info("Validating report")

        # Extract data with defaults
        content = report_data.get('content', '')
        metadata = report_data.copy()

        # Use validator
        result = self.validator.validate_report(content, metadata)

        logger.info(f"Report validation result: {'Valid' if result.is_valid else 'Invalid'} (score: {result.score:.2f})")
        return result

    def validate_summary(self, summary_text: str, min_length: Optional[int] = None,
                        max_length: Optional[int] = None) -> ValidationResult:
        """
        Validate summary length and quality.

        Args:
            summary_text: The summary to validate
            min_length: Minimum summary length (optional)
            max_length: Maximum summary length (optional)

        Returns:
            ValidationResult with validation status
        """
        logger.info("Validating summary")

        result = self.validator.validate_summary_length(summary_text, min_length, max_length)

        logger.info(f"Summary validation result: {'Valid' if result.is_valid else 'Invalid'} (length: {result.metadata.get('length', 0)})")
        return result

    def validate_keywords(self, content: str, keywords: List[str],
                         min_count: Optional[int] = None) -> ValidationResult:
        """
        Validate keyword presence in content.

        Args:
            content: Content to check
            keywords: List of keywords to validate
            min_count: Minimum required keywords (optional)

        Returns:
            ValidationResult with validation status
        """
        logger.info("Validating keywords")

        result = self.validator.validate_keywords(content, keywords, min_count)

        valid_kws = result.metadata.get('found_count', 0)
        total_kws = len(keywords)
        logger.info(f"Keywords validation: {valid_kws}/{total_kws} found")
        return result

    def validate_thinking_model(self, thinking_content: str) -> ValidationResult:
        """
        Validate thinking model content structure.

        Args:
            thinking_content: The thinking model content to validate

        Returns:
            ValidationResult with validation status
        """
        logger.info("Validating thinking model")

        result = self.validator.validate_thinking_model(thinking_content)

        logger.info(f"Thinking model validation: {'Valid' if result.is_valid else 'Invalid'} (score: {result.score:.2f})")
        return result

    def check_quality(self, content: str, content_type: str = "article") -> QualityMetrics:
        """
        Check content quality metrics.

        Args:
            content: Content to evaluate
            content_type: Type of content (article, report, etc.)

        Returns:
            QualityMetrics with detailed quality measurements
        """
        logger.info("Checking content quality")

        metrics = self.validator.check_quality_score(content, content_type)

        logger.info(f"Quality score: {metrics.overall_score:.2f}")
        return metrics

    def apply_template(self, template_type: str, content_data: Dict[str, Any],
                      style_options: Optional[Dict[str, Any]] = None) -> str:
        """
        Apply template to content with style integration.

        Args:
            template_type: Type of template to apply
            content_data: Data to populate template
            style_options: Style customization options (optional)

        Returns:
            Rendered HTML content
        """
        logger.info(f"Applying template: {template_type}")

        try:
            rendered = self.template_manager.render_with_style(template_type, content_data, style_options)
            logger.info("Template application completed")
            return rendered

        except Exception as e:
            logger.error(f"Template application failed: {e}")
            raise

    def get_stylesheet(self, theme: str = "default") -> str:
        """
        Get CSS stylesheet for specified theme.

        Args:
            theme: Theme name (default, dark, minimal)

        Returns:
            Complete CSS stylesheet
        """
        logger.info(f"Getting stylesheet for theme: {theme}")
        return self.style_manager.get_css(theme)

    def validate_and_render(self, content_type: str, content_data: Dict[str, Any],
                           template_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate content and render with template.

        Args:
            content_type: Type of content (article, report, thinking)
            content_data: Content and metadata
            template_type: Template to use (defaults based on content_type)

        Returns:
            Dictionary with validation result and rendered content
        """
        logger.info(f"Validate and render: {content_type}")

        # Validate based on content type
        if content_type == "article":
            validation_result = self.validate_article(content_data)
        elif content_type == "report":
            validation_result = self.validate_report(content_data)
        elif content_type == "thinking":
            validation_result = self.validate_thinking_model(content_data.get('content', ''))
        else:
            # Generic validation
            validation_result = ValidationResult(
                is_valid=True,
                errors=[],
                warnings=["Unknown content type, no specific validation applied"],
                score=0.5
            )

        # Determine template
        if template_type is None:
            template_map = {
                "article": "article_summary",
                "report": "research_report",
                "thinking": "thinking_model",
                "daily": "daily_report"
            }
            template_type = template_map.get(content_type, "minimal")

        # Render if validation passed or warnings only
        rendered_content = None
        if validation_result.is_valid or (validation_result.errors and validation_result.warnings):
            render_data = content_data.copy()
            if 'title' not in render_data:
                render_data['title'] = f"{content_type.title()} Content"

            try:
                rendered_content = self.apply_template(template_type, render_data)
            except Exception as e:
                logger.error(f"Rendering failed: {e}")
                validation_result.errors.append(f"Rendering error: {str(e)}")
                validation_result.is_valid = False

        return {
            "validation": validation_result,
            "rendered_content": rendered_content,
            "template_type": template_type
        }

    def batch_validate(self, items: List[Dict[str, Any]], content_type: str) -> List[Dict[str, Any]]:
        """
        Validate multiple items in batch.

        Args:
            items: List of content items to validate
            content_type: Type of content (article, report, thinking)

        Returns:
            List of validation results with metadata
        """
        logger.info(f"Batch validating {len(items)} items of type {content_type}")

        results = []
        for idx, item in enumerate(items):
            try:
                result = self.validate_and_render(content_type, item)
                results.append({
                    "index": idx,
                    "data": item,
                    "validation": result["validation"],
                    "status": "success"
                })
            except Exception as e:
                logger.error(f"Batch validation failed for item {idx}: {e}")
                results.append({
                    "index": idx,
                    "data": item,
                    "validation": ValidationResult(
                        is_valid=False,
                        errors=[str(e)],
                        score=0.0
                    ),
                    "status": "error"
                })

        logger.info(f"Batch validation completed: {len([r for r in results if r['validation'].is_valid])}/{len(items)} valid")
        return results

    def get_configuration(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self.config.copy()

    def reload_configuration(self):
        """Reload configuration from file."""
        logger.info("Reloading configuration")
        self._load_config()
        self._initialize_components()
        logger.info("Configuration reloaded")

    def get_system_info(self) -> Dict[str, Any]:
        """Get system information and status."""
        return {
            "status": "operational",
            "version": "1.0.0",
            "config_path": str(self.config_path),
            "config_loaded": bool(self.config),
            "components": {
                "validator": self.validator is not None,
                "style_manager": self.style_manager is not None,
                "template_manager": self.template_manager is not None
            },
            "supported_templates": self.template_manager.get_available_templates() if self.template_manager else [],
            "quality_threshold": self.config.get('constraints', {}).get('validation', {}).get('quality_threshold', 0.7)
        }
