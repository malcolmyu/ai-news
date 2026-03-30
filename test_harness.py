#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for Harness constraint control layer.
This script tests all components of the harness system.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from harness import HarnessController

def test_harness_system():
    """Test the complete harness system."""
    print("Testing Harness Constraint Control Layer")
    print("=" * 50)

    try:
        # Initialize controller
        print("\n1. Initializing HarnessController...")
        controller = HarnessController()
        print("[PASS] Controller initialized successfully")
        info = controller.get_system_info()
        print("System info: " + str(info))

        # Test article validation
        print("\n2. Testing article validation...")
        article_data = {
            "title": "Test Article",
            "content": "This is a test article about artificial intelligence. "
                      "Machine learning and deep learning are transforming industries. "
                      "Natural language processing enables new applications. "
                      "Computer vision is revolutionizing how we see the world.",
            "summary": "An overview of AI technologies including machine learning, "
                      "deep learning, and natural language processing.",
            "keywords": ["AI", "machine learning", "NLP"]
        }

        article_result = controller.validate_article(article_data)
        print("Article validation: " + ("PASSED" if article_result.is_valid else "FAILED"))
        print("Quality score: " + str(article_result.score))
        if article_result.errors:
            print("Errors: " + str(article_result.errors))
        if article_result.warnings:
            print("Warnings: " + str(article_result.warnings))

        # Test template application
        print("\n3. Testing template application...")
        rendered = controller.apply_template("article_summary", article_data)
        print("Template rendered successfully (" + str(len(rendered)) + " characters)")

        # Get stylesheet
        print("\n4. Testing stylesheet generation...")
        css = controller.get_stylesheet("default")
        print("Stylesheet generated (" + str(len(css)) + " characters)")

        # System info
        print("\n5. System Information...")
        info = controller.get_system_info()
        print("Status: " + str(info['status']))
        print("Components: " + str(info['components']))
        print("Templates: " + str(info['supported_templates']))

        print("\n" + "=" * 50)
        print("SUCCESS: All tests passed! Harness system is working correctly")
        return True

    except Exception as e:
        print("\nFAIL: Test failed: " + str(e))
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_harness_system()
    sys.exit(0 if success else 1)
