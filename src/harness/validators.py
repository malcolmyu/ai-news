"""
Content validation system for AI News System.

This module provides comprehensive content validation capabilities to ensure
all outputs meet quality standards, structural requirements, and consistency rules.
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import re
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    is_valid: bool
    errors: List[str] = None
    warnings: List[str] = None
    score: Optional[float] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class QualityMetrics:
    """Quality metrics for content evaluation."""
    readability_score: float = 0.0
    keyword_density: float = 0.0
    structure_score: float = 0.0
    coherence_score: float = 0.0
    completeness_score: float = 0.0
    overall_score: float = 0.0


class ContentValidator:
    """Comprehensive content validation system for AI News System."""

    # Validation constants
    SUMMARY_LENGTH_MIN = 50
    SUMMARY_LENGTH_MAX = 300
    KEYWORD_MIN_COUNT = 2
    KEYWORD_MIN_LENGTH = 3
    KEYWORD_MAX_LENGTH = 50
    QUALITY_SCORE_THRESHOLD = 0.7
    READING_TIME_MIN = 30  # seconds
    READING_TIME_MAX = 600  # 10 minutes
    MAX_KEYWORD_DENSITY = 0.05  # 5%

    # Thinking model validation patterns
    THINKING_PATTERNS = {
        "research_required": r"(需要研究|需要调研|research needed|further investigation)",
        "analysis_required": r"(需要分析|需要评估|analysis needed|evaluation required)",
        "uncertainty": r"(不确定|可能|不确定因素|uncertain|might|perhaps)"
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize ContentValidator with optional configuration."""
        self.config = config or {}
        self.quality_threshold = self.config.get('quality_threshold', self.QUALITY_SCORE_THRESHOLD)
        logger.info("ContentValidator initialized")

    def validate_summary_length(self, summary: str, min_length: Optional[int] = None,
                                max_length: Optional[int] = None) -> ValidationResult:
        """
        Validate summary length constraints.

        Args:
            summary: The summary text to validate
            min_length: Minimum length (characters), defaults to SUMMARY_LENGTH_MIN
            max_length: Maximum length (characters), defaults to SUMMARY_LENGTH_MAX

        Returns:
            ValidationResult with validation status
        """
        logger.info("Validating summary length")

        min_len = min_length or self.SUMMARY_LENGTH_MIN
        max_len = max_length or self.SUMMARY_LENGTH_MAX

        errors = []
        warnings = []
        length = len(summary.strip())

        if length < min_len:
            errors.append(f"Summary too short: {length} characters (minimum {min_len})")

        if length > max_len:
            errors.append(f"Summary too long: {length} characters (maximum {max_len})")

        if len(summary.split()) < 10:
            warnings.append("Summary might be too concise")

        score = 1.0 if not errors else max(0.0, 1.0 - (len(errors) * 0.3))

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            score=score,
            metadata={"length": length, "range": f"{min_len}-{max_len}"}
        )

    def validate_keywords(self, content: str, keywords: List[str],
                         min_count: Optional[int] = None) -> ValidationResult:
        """
        Validate keyword presence in content.

        Args:
            content: Content to validate
            keywords: List of required keywords
            min_count: Minimum required keywords, defaults to KEYWORD_MIN_COUNT

        Returns:
            ValidationResult with validation status
        """
        logger.info("Validating keywords")

        errors = []
        warnings = []
        present_keywords = []
        min_req = min_count or self.KEYWORD_MIN_COUNT

        if not keywords:
            errors.append("No keywords provided")
            return ValidationResult(is_valid=False, errors=errors)

        content_lower = content.lower()
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if len(keyword) < self.KEYWORD_MIN_LENGTH:
                warnings.append(f"Keyword too short: '{keyword}' (< {self.KEYWORD_MIN_LENGTH} chars)")
            elif len(keyword) > self.KEYWORD_MAX_LENGTH:
                warnings.append(f"Keyword too long: '{keyword}' (> {self.KEYWORD_MAX_LENGTH} chars)")
            else:
                if keyword_lower in content_lower:
                    present_keywords.append(keyword)

        found_count = len(present_keywords)
        if found_count < min_req:
            errors.append(f"Insufficient keywords: {found_count}/{min_req} found")

        # Calculate keyword density
        content_words = len(content.split())
        keyword_density = found_count / max(content_words, 1)
        if keyword_density > self.MAX_KEYWORD_DENSITY:
            warnings.append(f"Keyword density too high: {keyword_density:.2%}")

        score = min(1.0, found_count / max(min_req, 1))

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            score=score,
            metadata={
                "found_keywords": present_keywords,
                "missing_keywords": list(set(keywords) - set(present_keywords)),
                "keyword_density": keyword_density,
                "found_count": found_count,
                "required_count": min_req
            }
        )

    def check_quality_score(self, content: str, content_type: str = "article") -> QualityMetrics:
        """
        Calculate comprehensive quality score for content.

        Args:
            content: Content to evaluate
            content_type: Type of content (article, report, summary, etc.)

        Returns:
            QualityMetrics object with detailed quality measurements
        """
        logger.info("Checking quality score")

        metrics = QualityMetrics()

        # Readability score (simple heuristic)
        sentences = len(re.split(r'[.!?]+', content))
        words = len(content.split())
        avg_sentence_length = words / max(sentences, 1)

        # Good readability: sentences between 10-25 words
        if 10 <= avg_sentence_length <= 25:
            metrics.readability_score = 0.9
        elif avg_sentence_length < 5:
            metrics.readability_score = 0.5
        elif avg_sentence_length > 40:
            metrics.readability_score = 0.6
        else:
            metrics.readability_score = 0.8

        # Structure score (check for headings, paragraphs)
        has_headings = bool(re.search(r'^#{1,6}\s', content, re.MULTILINE))
        paragraphs = len([p for p in content.split('\n\n') if p.strip()])

        if content_type == "report":
            # Reports should have headings and multiple sections
            structure_points = 0
            if has_headings:
                structure_points += 0.5
            if paragraphs >= 3:
                structure_points += 0.5
            metrics.structure_score = structure_points
        else:
            # Articles should have headings and paragraphs
            structure_points = 0
            if has_headings:
                structure_points += 0.3
            if paragraphs >= 2:
                structure_points += 0.4
            if len(content) > 200:
                structure_points += 0.3
            metrics.structure_score = min(1.0, structure_points)

        # Coherence score (check for transitions, logical flow)
        transition_words = [
            'however', 'therefore', 'furthermore', 'moreover', 'consequently',
            'meanwhile', 'nevertheless', 'although', 'because', 'since'
        ]
        transition_count = sum(1 for word in transition_words if word.lower() in content.lower())
        metrics.coherence_score = min(1.0, 0.3 + (transition_count * 0.1))

        # Completeness score (check for key elements)
        completeness_points = 0
        if content_type in ["article", "report"]:
            # Check for intro, body, conclusion patterns
            first_100 = content[:100].lower()
            last_100 = content[-100:].lower()

            if any(word in first_100 for word in ['introduction', 'overview', 'summary']):
                completeness_points += 0.3
            if len(content) > 300:
                completeness_points += 0.4
            if any(word in last_100 for word in ['conclusion', 'summary', 'future', 'recommendations']):
                completeness_points += 0.3
        else:
            completeness_points = 0.7  # Default for non-structured content

        metrics.completeness_score = completeness_points

        # Calculate overall score
        weights = {
            'readability': 0.25,
            'structure': 0.25,
            'coherence': 0.25,
            'completeness': 0.25
        }

        metrics.overall_score = (
            metrics.readability_score * weights['readability'] +
            metrics.structure_score * weights['structure'] +
            metrics.coherence_score * weights['coherence'] +
            metrics.completeness_score * weights['completeness']
        )

        return metrics

    def validate_report_structure(self, report_content: str,
                                 required_sections: Optional[List[str]] = None) -> ValidationResult:
        """
        Validate report structure and required sections.

        Args:
            report_content: The report content to validate
            required_sections: List of required section titles (without # prefix)

        Returns:
            ValidationResult with structure validation status
        """
        logger.info("Validating report structure")

        errors = []
        warnings = []

        # Default required sections
        default_sections = [
            "executive summary",
            "introduction",
            "main content",
            "conclusion",
            "recommendations"
        ]

        required = required_sections or default_sections

        # Find all headings
        headings = re.findall(r'^#{1,6}\s+(.+)$', report_content, re.MULTILINE)
        headings_lower = [h.lower().strip() for h in headings]

        # Check for required sections
        found_sections = []
        for required_section in required:
            if any(required_section.lower() in heading for heading in headings_lower):
                found_sections.append(required_section)
            else:
                errors.append(f"Missing required section: {required_section}")

        # Check heading hierarchy
        heading_levels = re.findall(r'^(#{1,6})\s', report_content, re.MULTILINE)
        if heading_levels:
            levels = [len(h) for h in heading_levels]
            if max(levels) - min(levels) > 2:
                warnings.append("Uneven heading hierarchy detected")

        # Check for orphaned content (content without headings)
        sections = re.split(r'^#{1,6}\s', report_content, flags=re.MULTILINE)
        if len([s for s in sections if s.strip()]) > len(headings) + 1:
            warnings.append("Content found outside of structured headings")

        # Calculate structure score
        required_found = len(found_sections)
        required_total = len(required)
        structure_score = required_found / max(required_total, 1)

        if len(headings) < 3:
            warnings.append("Very few headings - consider structuring content better")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            score=structure_score,
            metadata={
                "found_sections": found_sections,
                "missing_sections": list(set(required) - set(found_sections)),
                "total_headings": len(headings),
                "heading_levels": list(set(heading_levels)) if heading_levels else []
            }
        )

    def validate_thinking_model(self, thinking_content: str) -> ValidationResult:
        """
        Validate thinking model content structure and quality.

        Args:
            thinking_content: The thinking model content to validate

        Returns:
            ValidationResult with thinking model validation status
        """
        logger.info("Validating thinking model")

        errors = []
        warnings = []

        if not thinking_content or not thinking_content.strip():
            errors.append("Thinking model content is empty")
            return ValidationResult(is_valid=False, errors=errors)

        # Check for required thinking patterns
        found_patterns = {}
        for pattern_name, pattern_regex in self.THINKING_PATTERNS.items():
            if re.search(pattern_regex, thinking_content, re.IGNORECASE):
                found_patterns[pattern_name] = True
            else:
                found_patterns[pattern_name] = False

        # Analyze uncertainty level
        uncertainty_indicators = [
            'uncertain', 'maybe', 'perhaps', 'might', 'could', 'possibly',
            '不确定', '可能', '也许', '或许', '大概'
        ]

        uncertainty_count = sum(
            thinking_content.lower().count(indicator)
            for indicator in uncertainty_indicators
        )

        # Calculate thinking quality score
        words = len(thinking_content.split())
        if words < 50:
            errors.append(f"Thinking model too short: {words} words (minimum 50)")

        if words > 1000:
            warnings.append(f"Thinking model very long: {words} words")

        # Score based on depth indicators
        depth_indicators = [
            'because', 'therefore', 'analysis', 'reasoning', 'evaluation',
            'assessment', 'consideration', 'implication', 'consequence'
        ]

        depth_score = sum(
            1 for indicator in depth_indicators
            if indicator in thinking_content.lower()
        ) / len(depth_indicators)

        # Uncertainty should be moderate (not too certain, not too uncertain)
        if uncertainty_count == 0:
            warnings.append("No uncertainty indicators - might be overconfident")
        elif uncertainty_count > 10:
            warnings.append("High uncertainty - might lack confidence")

        thinking_score = 0.5 + (depth_score * 0.5)  # 0.5 base + depth contribution
        if uncertainty_count == 0:
            thinking_score *= 0.9
        elif uncertainty_count > 10:
            thinking_score *= 0.8

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            score=min(1.0, thinking_score),
            metadata={
                "thinking_patterns": found_patterns,
                "uncertainty_indicators": uncertainty_count,
                "content_length": words,
                "depth_indicators": depth_score
            }
        )

    def validate_article(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Comprehensive article validation.

        Args:
            content: Article content
            metadata: Article metadata (title, keywords, etc.)

        Returns:
            Combined validation result
        """
        logger.info("Performing comprehensive article validation")

        metadata = metadata or {}
        all_errors = []
        all_warnings = []

        # Validate summary if present
        if 'summary' in metadata:
            summary_result = self.validate_summary_length(metadata['summary'])
            all_errors.extend(summary_result.errors)
            all_warnings.extend(summary_result.warnings)

        # Validate keywords
        if 'keywords' in metadata:
            keywords_result = self.validate_keywords(content, metadata['keywords'])
            all_errors.extend(keywords_result.errors)
            all_warnings.extend(keywords_result.warnings)

        # Check quality score
        quality_metrics = self.check_quality_score(content, "article")
        if quality_metrics.overall_score < self.quality_threshold:
            all_warnings.append(f"Quality score below threshold: {quality_metrics.overall_score:.2f}")

        # Check length constraints
        content_length = len(content)
        if content_length < 500:
            all_warnings.append(f"Article content very short: {content_length} characters")
        elif content_length > 10000:
            all_warnings.append(f"Article content very long: {content_length} characters")

        is_valid = len(all_errors) == 0
        # Calculate score as average of all validation scores
        score = quality_metrics.overall_score if is_valid else quality_metrics.overall_score * 0.7

        return ValidationResult(
            is_valid=is_valid,
            errors=all_errors,
            warnings=all_warnings,
            score=score,
            metadata={
                "quality_metrics": quality_metrics.__dict__,
                "content_length": content_length,
                "validation_type": "full_article"
            }
        )

    def validate_report(self, report_content: str, metadata: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Comprehensive report validation.

        Args:
            report_content: Report content
            metadata: Report metadata

        Returns:
            Combined validation result
        """
        logger.info("Performing comprehensive report validation")

        metadata = metadata or {}
        all_errors = []
        all_warnings = []

        # Validate structure
        structure_result = self.validate_report_structure(report_content, metadata.get('required_sections'))
        all_errors.extend(structure_result.errors)
        all_warnings.extend(structure_result.warnings)

        # Validate keywords if present
        if 'keywords' in metadata:
            keywords_result = self.validate_keywords(report_content, metadata['keywords'])
            all_errors.extend(keywords_result.errors)
            all_warnings.extend(keywords_result.warnings)

        # Check quality score
        quality_metrics = self.check_quality_score(report_content, "report")
        if quality_metrics.overall_score < self.quality_threshold:
            all_errors.append(f"Quality score below threshold: {quality_metrics.overall_score:.2f}")

        # Check report-specific requirements
        content_length = len(report_content)
        if content_length < 2000:
            all_warnings.append(f"Report content might be too short: {content_length} characters")

        is_valid = len(all_errors) == 0
        score = quality_metrics.overall_score if is_valid else quality_metrics.overall_score * 0.7

        return ValidationResult(
            is_valid=is_valid,
            errors=all_errors,
            warnings=all_warnings,
            score=score,
            metadata={
                "quality_metrics": quality_metrics.__dict__,
                "content_length": content_length,
                "structure_metadata": structure_result.metadata,
                "validation_type": "full_report"
            }
        )
