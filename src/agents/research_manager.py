"""
Research Manager Agent - Manages research reports with metadata extraction,
validation, categorization, and index management.

This agent integrates with HarnessController for constraint enforcement
and provides intelligent research report management capabilities.
"""

import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import hashlib
from dataclasses import dataclass
from collections import defaultdict

from harness.controller import HarnessController
from harness.validators import ValidationResult

logger = logging.getLogger(__name__)


@dataclass
class ReportMetadata:
    """Structured metadata for a research report."""
    title: str
    summary: str
    date: str
    keywords: List[str]
    author: Optional[str] = None
    category: Optional[str] = None
    sections: List[str] = None
    word_count: int = 0
    file_hash: str = ""
    quality_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "title": self.title,
            "summary": self.summary,
            "date": self.date,
            "keywords": self.keywords,
            "author": self.author,
            "category": self.category,
            "sections": self.sections or [],
            "word_count": self.word_count,
            "file_hash": self.file_hash,
            "quality_score": self.quality_score
        }


class ResearchManagerAgent:
    """
    Research Manager Agent responsible for processing research reports,
    extracting metadata, validating content, managing categories,
    and updating indexes.
    """

    # Categories definition
    CATEGORIES = {
        "tech": "技术",
        "product": "产品",
        "business": "商业",
        "methodology": "方法论",
        "ai": "人工智能",
        "data": "数据科学",
        "design": "设计",
        "strategy": "战略"
    }

    def __init__(self, harness: HarnessController):
        """
        Initialize ResearchManagerAgent.

        Args:
            harness: HarnessController instance for validation and rendering
        """
        self.harness = harness
        self.data_dir = Path("data/research")
        self.index_path = self.data_dir / "index.json"
        self.categories_dir = self.data_dir / "categories"

        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.categories_dir.mkdir(exist_ok=True)

        logger.info("ResearchManagerAgent initialized")

    def process_report(self, report_path: Path, category: str = None) -> Dict[str, Any]:
        """
        Complete processing workflow for a research report.

        Args:
            report_path: Path to the report file
            category: Optional predefined category

        Returns:
            Dictionary containing processing results
            {
                "metadata": ReportMetadata dict,
                "validation": ValidationResult dict,
                "categories": List[str] of suggested categories,
                "indexed": bool indicating if successfully indexed
            }
        """
        logger.info(f"Processing report: {report_path}")

        try:
            # 1. Extract metadata
            metadata = self.extract_metadata(report_path)
            logger.info(f"Extracted metadata: {metadata.title}")

            # 2. Validate report structure
            validation = self.validate_report_structure(report_path, metadata)
            logger.info(f"Validation result: {'Valid' if validation.is_valid else 'Invalid'}")

            # 3. Generate quality score
            metadata.quality_score = self.generate_quality_score(metadata)

            # 4. Suggest categories
            categories = self.suggest_categories(metadata.to_dict(), predefined_category=category)
            logger.info(f"Suggested categories: {categories}")

            # 5. Update all indexes
            self.update_all_indexes(metadata.to_dict(), categories)

            # 6. Find related reports
            related_reports = self.find_related_reports(metadata.to_dict(), limit=3)

            return {
                "metadata": metadata.to_dict(),
                "validation": {
                    "is_valid": validation.is_valid,
                    "score": validation.score,
                    "warnings": validation.warnings,
                    "errors": validation.errors
                },
                "categories": categories,
                "related_reports": related_reports,
                "indexed": True
            }

        except Exception as e:
            logger.error(f"Failed to process report {report_path}: {str(e)}")
            return {
                "metadata": {},
                "validation": {},
                "categories": [],
                "related_reports": [],
                "indexed": False,
                "error": str(e)
            }

    def extract_metadata(self, report_path: Path) -> ReportMetadata:
        """
        Extract comprehensive metadata from a research report.

        Args:
            report_path: Path to the report file

        Returns:
            ReportMetadata object containing extracted information
        """
        logger.info(f"Extracting metadata from {report_path}")

        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract title from multiple sources
            title = self._extract_title(content, report_path)

            # Extract summary/description
            summary = self._extract_summary(content)

            # Try to extract date from content or use file modification date
            date = self._extract_date(content) or datetime.now().strftime("%Y-%m-%d")

            # Extract keywords from meta tags and content
            keywords = self._extract_keywords(content)

            # Try to extract author
            author = self._extract_author(content)

            # Extract section structure
            sections = self._extract_sections(content)

            # Calculate word count
            word_count = len(re.findall(r'\w+', content))

            # Generate file hash for tracking
            file_hash = hashlib.md5(content.encode()).hexdigest()

            logger.info(f"Successfully extracted metadata: {title}")

            return ReportMetadata(
                title=title,
                summary=summary,
                date=date,
                keywords=keywords,
                author=author,
                sections=sections,
                word_count=word_count,
                file_hash=file_hash,
                quality_score=0.0  # Will be calculated later
            )

        except Exception as e:
            logger.error(f"Failed to extract metadata from {report_path}: {str(e)}")
            # Return minimal metadata on error
            return ReportMetadata(
                title=report_path.stem,
                summary="No summary available",
                date=datetime.now().strftime("%Y-%m-%d"),
                keywords=[],
                word_count=0,
                file_hash=""
            )

    def _extract_title(self, content: str, report_path: Path) -> str:
        """Extract title from HTML content or filename."""
        # Try <title> tag
        title_match = re.search(r'<title>(.*?)</title>', content, re.I | re.S)
        if title_match:
            return re.sub(r'<[^>]+>', '', title_match.group(1)).strip()

        # Try <h1>
        h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.I | re.S)
        if h1_match:
            return re.sub(r'<[^>]+>', '', h1_match.group(1)).strip()

        # Fallback to filename
        return report_path.stem.replace('-', ' ').replace('_', ' ').title()

    def _extract_summary(self, content: str) -> str:
        """Extract summary from meta description or first paragraph."""
        # Try meta description
        desc_match = re.search(
            r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']',
            content,
            re.I
        )
        if desc_match:
            return desc_match.group(1).strip()

        # Try first <p> paragraph
        p_match = re.search(r'<p>([^<]+)</p>', content)
        if p_match:
            text = re.sub(r'<[^>]+>', '', p_match.group(1)).strip()
            return text[:150] + "..." if len(text) > 150 else text

        return "点击查看完整报告 →"

    def _extract_date(self, content: str) -> Optional[str]:
        """Extract date from meta or content."""
        # Try meta date
        date_match = re.search(
            r'<meta[^>]*name=["\']date["\'][^>]*content=["\']([^"\']+)["\']',
            content,
            re.I
        )
        if date_match:
            return date_match.group(1)

        # Try various date patterns in content
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',
            r'(\d{4}/\d{2}/\d{2})',
            r'(\d{4}年\d{2}月\d{2}日)'
        ]

        for pattern in date_patterns:
            date_match = re.search(pattern, content)
            if date_match:
                return date_match.group(1)

        return None

    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from meta keywords and content analysis."""
        keywords = []

        # Try meta keywords
        kw_match = re.search(
            r'<meta[^>]*name=["\']keywords["\'][^>]*content=["\']([^"\']+)["\']',
            content,
            re.I
        )
        if kw_match:
            keywords.extend([kw.strip() for kw in kw_match.group(1).split(',')])

        # Also extract from headings and strong/em tags
        heading_text = re.findall(r'<h[1-3][^>]*>(.*?)</h[1-3]>', content, re.I | re.S)
        for heading in heading_text:
            # Add significant words from headings
            words = re.findall(r'\b[A-Z][a-z]+\b', re.sub(r'<[^>]+>', '', heading))
            keywords.extend(words)

        # Remove duplicates and limit to 10
        keywords = list(dict.fromkeys(keywords))[:10]

        return keywords

    def _extract_author(self, content: str) -> Optional[str]:
        """Extract author from meta author."""
        author_match = re.search(
            r'<meta[^>]*name=["\']author["\'][^>]*content=["\']([^"\']+)["\']',
            content,
            re.I
        )
        if author_match:
            return author_match.group(1)
        return None

    def _extract_sections(self, content: str) -> List[str]:
        """Extract section headings from the report."""
        sections = []
        heading_matches = re.findall(r'<h([1-3])[^>]*>(.*?)</h\1>', content, re.I | re.S)
        for level, heading in heading_matches:
            text = re.sub(r'<[^>]+>', '', heading).strip()
            if text and len(text) < 100:  # Reasonable heading length
                sections.append(text)
        return sections

    def suggest_categories(self, metadata: Dict[str, Any],
                          predefined_category: str = None,
                          confidence_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """
        Intelligently suggest categories for a research report.

        Args:
            metadata: Report metadata dictionary
            predefined_category: Optional predefined category
            confidence_threshold: Minimum confidence to include suggestion

        Returns:
            List of suggested categories with confidence scores
            [
                {"category": "tech", "confidence": 0.85},
                {"category": "ai", "confidence": 0.65}
            ]
        """
        logger.info("Suggesting categories for report")

        suggestions = []
        title_lower = metadata.get("title", "").lower()
        summary_lower = metadata.get("summary", "").lower()
        keywords = [kw.lower() for kw in metadata.get("keywords", [])]
        sections = [s.lower() for s in metadata.get("sections", [])]

        # Use predefined category with high confidence if provided
        if predefined_category:
            if predefined_category in self.CATEGORIES:
                suggestions.append({
                    "category": predefined_category,
                    "confidence": 0.9
                })
                logger.info(f"Using predefined category: {predefined_category}")
                return suggestions

        # Category-based keyword matching
        category_keywords = {
            "tech": {
                "keywords": ["技术", "开发", "编程", "软件", "架构", "系统", "工程", "code", "develop", "engineering"],
                "boost": 1.2
            },
            "product": {
                "keywords": ["产品", "用户", "需求", "功能", "设计", "体验", "界面", "product", "user", "ui", "ux"],
                "boost": 1.2
            },
            "business": {
                "keywords": ["商业", "市场", "营销", "策略", "盈利", "收入", "business", "market", "strategy"],
                "boost": 1.2
            },
            "methodology": {
                "keywords": ["方法", "流程", "管理", "敏捷", "实践", "methodology", "process", "management", "agile"],
                "boost": 1.2
            },
            "ai": {
                "keywords": ["人工智能", "机器学习", "深度学习", "ai", "ml", "machine", "neural", "algorithm"],
                "boost": 1.3
            },
            "data": {
                "keywords": ["数据", "分析", "统计", "数据库", "data", "analytics", "statistics", "database"],
                "boost": 1.2
            },
            "design": {
                "keywords": ["设计", "视觉", "交互", "美学", "design", "visual", "interaction", "aesthetic"],
                "boost": 1.2
            },
            "strategy": {
                "keywords": ["战略", "规划", "决策", "目标", "strategy", "planning", "decision", "vision"],
                "boost": 1.2
            }
        }

        # Score each category
        for category, config in category_keywords.items():
            score = 0.0
            keyword_list = config["keywords"]
            boost = config["boost"]

            # Check title matches (higher weight)
            for keyword in keyword_list:
                if keyword in title_lower:
                    score += 0.3 * boost

                # Check summary matches
                if keyword in summary_lower:
                    score += 0.2 * boost

                # Check keyword matches
                if any(keyword in kw for kw in keywords):
                    score += 0.15 * boost

                # Check section headings
                if any(keyword in section for section in sections):
                    score += 0.1 * boost

            # Normalize score to 0-1 range
            max_possible = len(keyword_list) * 0.3 * boost
            if max_possible > 0:
                score = min(score / max_possible, 1.0)

            # Add to suggestions if above threshold
            if score >= confidence_threshold:
                suggestions.append({
                    "category": category,
                    "confidence": round(score, 2)
                })

        # Sort by confidence and return top 3
        suggestions.sort(key=lambda x: x["confidence"], reverse=True)
        suggestions = suggestions[:3]

        # Ensure we have at least one category
        if not suggestions:
            suggestions.append({
                "category": "tech",
                "confidence": 0.5
            })

        logger.info(f"Category suggestions: {[s['category'] for s in suggestions]}")
        return suggestions

    def generate_quality_score(self, metadata: ReportMetadata) -> float:
        """
        Generate a quality score for the research report.

        Args:
            metadata: Report metadata

        Returns:
            Quality score between 0.0 and 1.0
        """
        logger.info("Generating quality score")

        score = 0.0
        max_score = 10.0

        # 1. Title quality (2 points)
        if len(metadata.title) >= 10:
            score += 1.0
        if len(metadata.title) <= 100:
            score += 1.0

        # 2. Summary quality (2 points)
        if len(metadata.summary) >= 20 and len(metadata.summary) <= 300:
            score += 2.0

        # 3. Keyword richness (1 point)
        if len(metadata.keywords) >= 3:
            score += 1.0

        # 4. Section structure (2 points)
        if len(metadata.sections) >= 2:
            score += 1.0
        if len(metadata.sections) <= 10:
            score += 1.0

        # 5. Word count (2 points)
        if metadata.word_count >= 500:
            score += 1.0
        if metadata.word_count <= 10000:
            score += 1.0

        # 6. Author information (1 point)
        if metadata.author:
            score += 1.0

        # Normalize to 0-1
        quality_score = round(score / max_score, 2)
        logger.info(f"Quality score: {quality_score}")

        return quality_score

    def validate_report_structure(self, report_path: Path, metadata: ReportMetadata) -> ValidationResult:
        """
        Validate report structure using Harness validation.

        Args:
            report_path: Path to report file
            metadata: Extracted metadata

        Returns:
            ValidationResult from Harness
        """
        logger.info("Validating report structure")

        try:
            # Read report content
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Create validation data
            validation_data = {
                "content": content,
                "title": metadata.title,
                "keywords": metadata.keywords,
                "sections": metadata.sections
            }

            # Use Harness validation
            return self.harness.validate_report(validation_data)

        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            # Return invalid result with error
            return ValidationResult(
                is_valid=False,
                score=0.0,
                errors=[f"Validation error: {str(e)}"],
                warnings=[],
                metadata={}
            )

    def update_all_indexes(self, metadata: Dict[str, Any], categories: List[Dict[str, Any]]) -> bool:
        """
        Update all research indexes with new report metadata.

        Args:
            metadata: Report metadata dictionary
            categories: List of suggested categories

        Returns:
            True if successful
        """
        logger.info("Updating all indexes")

        try:
            # Update main index
            self._update_main_index(metadata, categories)

            # Update category indexes
            for cat_info in categories:
                self._update_category_index(metadata, cat_info["category"])

            # Update homepage
            self.update_homepage(metadata)

            # Update archive
            self.update_archive(metadata)

            logger.info("All indexes updated successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to update indexes: {str(e)}")
            return False

    def _update_main_index(self, metadata: Dict[str, Any], categories: List[Dict[str, Any]]):
        """Update the main research index.json."""
        index_data = {}

        # Load existing index if available
        if self.index_path.exists():
            try:
                with open(self.index_path, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
            except:
                index_data = {}

        # Initialize structure
        if "reports" not in index_data:
            index_data["reports"] = []
        if "categories" not in index_data:
            index_data["categories"] = {}

        # Add report to index
        report_entry = {
            "title": metadata["title"],
            "summary": metadata["summary"],
            "date": metadata["date"],
            "keywords": metadata["keywords"],
            "author": metadata.get("author"),
            "categories": [cat["category"] for cat in categories],
            "quality_score": metadata["quality_score"],
            "file_hash": metadata["file_hash"]
        }

        # Check if report already exists (update vs add)
        existing_idx = None
        for idx, report in enumerate(index_data["reports"]):
            if report.get("file_hash") == metadata["file_hash"]:
                existing_idx = idx
                break

        if existing_idx is not None:
            index_data["reports"][existing_idx] = report_entry
            logger.info(f"Updated existing report in main index: {metadata['title']}")
        else:
            index_data["reports"].insert(0, report_entry)  # Add to beginning
            logger.info(f"Added new report to main index: {metadata['title']}")

        # Update category counts
        for cat_info in categories:
            cat = cat_info["category"]
            if cat not in index_data["categories"]:
                index_data["categories"][cat] = 0
            if existing_idx is None:
                index_data["categories"][cat] += 1

        # Save updated index
        self._save_json(self.index_path, index_data)

    def _update_category_index(self, metadata: Dict[str, Any], category: str):
        """Update category-specific index."""
        category_path = self.categories_dir / f"{category}.json"

        category_data = {}
        if category_path.exists():
            try:
                with open(category_path, 'r', encoding='utf-8') as f:
                    category_data = json.load(f)
            except:
                category_data = {}

        if "reports" not in category_data:
            category_data["reports"] = []

        # Add report to category
        report_entry = {
            "title": metadata["title"],
            "summary": metadata["summary"],
            "date": metadata["date"],
            "quality_score": metadata["quality_score"]
        }

        # Check for existing
        existing = False
        for idx, report in enumerate(category_data["reports"]):
            if report.get("title") == metadata["title"]:
                category_data["reports"][idx] = report_entry
                existing = True
                break

        if not existing:
            category_data["reports"].insert(0, report_entry)

        self._save_json(category_path, category_data)
        logger.info(f"Updated category index: {category}")

    def update_homepage(self, metadata: Dict[str, Any]):
        """Update homepage with new report highlight."""
        logger.info("Updating homepage with new report")

        # This method would integrate with Harness templates to update
        # the homepage showcase area. Implementation would depend on
        # the specific homepage structure and templating system.

        # Prepare data for homepage update
        homepage_data = {
            "type": "research",
            "title": metadata["title"],
            "summary": metadata["summary"],
            "date": metadata["date"],
            "quality_score": metadata["quality_score"]
        }

        # The actual homepage update logic would be handled by HomepageBuilderAgent
        # This method prepares and signals the update
        logger.info(f"Prepared homepage update data: {metadata['title']}")
        return homepage_data

    def update_archive(self, metadata: Dict[str, Any]):
        """Update archive with new report."""
        logger.info("Updating archive with new report")

        # Similar to homepage, this would prepare data for archive update
        archive_entry = {
            "date": metadata["date"],
            "title": metadata["title"],
            "keywords": metadata["keywords"],
            "quality_score": metadata["quality_score"]
        }

        logger.info(f"Prepared archive entry: {metadata['title']}")
        return archive_entry

    def find_related_reports(self, metadata: Dict[str, Any], limit: int = 3) -> List[Dict[str, Any]]:
        """
        Find related reports based on keywords and categories.

        Args:
            metadata: Report metadata
            limit: Maximum number of related reports to return

        Returns:
            List of related report metadata
        """
        logger.info(f"Finding related reports for: {metadata['title']}")

        if not self.index_path.exists():
            return []

        try:
            with open(self.index_path, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
        except:
            return []

        current_keywords = set(kw.lower() for kw in metadata.get("keywords", []))
        current_categories = set(metadata.get("categories", []))

        # Score other reports
        related = []
        for report in index_data.get("reports", []):
            if report["title"] == metadata["title"]:
                continue

            # Calculate similarity score
            score = 0.0

            # Keyword overlap
            report_keywords = set(kw.lower() for kw in report.get("keywords", []))
            if current_keywords and report_keywords:
                overlap = len(current_keywords & report_keywords)
                score += overlap / max(len(current_keywords), len(report_keywords)) * 0.6

            # Category overlap
            report_categories = set(report.get("categories", []))
            if current_categories and report_categories:
                cat_overlap = len(current_categories & report_categories)
                score += cat_overlap / max(len(current_categories), len(report_categories)) * 0.4

            # Quality bonus
            score *= (0.5 + report.get("quality_score", 0.5))

            if score > 0.2:  # Threshold
                related.append({
                    "title": report["title"],
                    "summary": report["summary"],
                    "date": report["date"],
                    "similarity_score": round(score, 2),
                    "quality_score": report.get("quality_score", 0)
                })

        # Sort by score and return top N
        related.sort(key=lambda x: (x["similarity_score"], x["quality_score"]), reverse=True)
        logger.info(f"Found {len(related)} related reports")

        return related[:limit]

    def get_category_stats(self) -> Dict[str, Any]:
        """Get statistics for all categories."""
        stats = {}

        if self.index_path.exists():
            try:
                with open(self.index_path, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)

                stats["total_reports"] = len(index_data.get("reports", []))
                stats["categories"] = index_data.get("categories", {})

                # Calculate average quality
                reports = index_data.get("reports", [])
                if reports:
                    quality_scores = [r.get("quality_score", 0) for r in reports]
                    stats["avg_quality_score"] = round(sum(quality_scores) / len(quality_scores), 2)
                else:
                    stats["avg_quality_score"] = 0.0

            except:
                stats = {"total_reports": 0, "categories": {}, "avg_quality_score": 0.0}

        else:
            stats = {"total_reports": 0, "categories": {}, "avg_quality_score": 0.0}

        logger.info(f"Category stats: {stats}")
        return stats

    def _save_json(self, path: Path, data: Dict[str, Any]):
        """Helper to save JSON data with proper formatting."""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
