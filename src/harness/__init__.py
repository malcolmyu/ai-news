"""
Harness - AI News System Constraint Control Layer

This package provides constraint validation, style management, and template control
for the AI News system, ensuring consistent quality and presentation across all outputs.
"""

__version__ = "1.0.0"
__author__ = "AI News System"
__description__ = "Constraint Control Layer for AI News System"

from .controller import HarnessController
from .styles import StyleConstraints
from .validators import ContentValidator
from .templates import TemplateManager

__all__ = [
    "HarnessController",
    "StyleConstraints",
    "ContentValidator",
    "TemplateManager"
]
