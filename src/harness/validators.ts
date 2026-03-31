import * as fs from 'fs';
import * as path from 'path';
import { JSDOM } from 'jsdom';

export interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

export class ContentValidator {
  validateDocument(html: string): ValidationResult {
    const result: ValidationResult = {
      valid: true,
      errors: [],
      warnings: [],
    };

    try {
      const dom = new JSDOM(html);
      const document = dom.window.document;

      // Check for title
      const titleElement = document.querySelector('title');
      if (!titleElement || !titleElement.textContent?.trim()) {
        result.errors.push('Document missing title');
        result.valid = false;
      }

      // Check for meta charset
      const charsetMeta = document.querySelector('meta[charset]');
      if (!charsetMeta) {
        result.warnings.push('Document missing charset meta tag');
      }

      // Check for viewport meta
      const viewportMeta = document.querySelector('meta[name="viewport"]');
      if (!viewportMeta) {
        result.warnings.push('Document missing viewport meta tag');
      }

      // Check heading structure
      const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
      if (headings.length === 0) {
        result.warnings.push('Document has no headings');
      }

      // Check for at least some content
      const paragraphs = document.querySelectorAll('p');
      if (paragraphs.length < 3) {
        result.warnings.push('Document has very few paragraphs');
      }

      // Check for broken internal links
      const links = document.querySelectorAll('a[href]');
      for (const link of Array.from(links)) {
        const href = link.getAttribute('href');
        if (href && href.startsWith('#')) {
          const target = document.querySelector(href);
          if (!target) {
            result.warnings.push(`Broken anchor link: ${href}`);
          }
        }
      }

    } catch (error: any) {
      result.errors.push(`Failed to parse HTML: ${error.message}`);
      result.valid = false;
    }

    return result;
  }

  validateSummary(summary: string): ValidationResult {
    const result: ValidationResult = {
      valid: true,
      errors: [],
      warnings: [],
    };

    if (!summary.trim()) {
      result.errors.push('Summary is empty');
      result.valid = false;
      return result;
    }

    if (summary.length < 50) {
      result.errors.push(`Summary too short (${summary.length} chars, minimum 50 chars)`);
      result.valid = false;
    }

    if (summary.length > 1000) {
      result.warnings.push(`Summary too long (${summary.length} chars, recommended max 1000 chars)`);
    }

    // Check for incomplete sentences
    const sentenceCount = (summary.match(/[.!?]/g) || []).length;
    if (sentenceCount < 2) {
      result.warnings.push('Summary should be multiple sentences');
    }

    // Check for clarity indicators
    const unclearPatterns = ['maybe', 'perhaps', 'possibly'];
    for (const pattern of unclearPatterns) {
      if (summary.toLowerCase().includes(pattern)) {
        result.warnings.push(`Summary contains uncertainty: "${pattern}"`);
      }
    }

    return result;
  }

  validateResearchReport(content: string): ValidationResult {
    const result: ValidationResult = {
      valid: true,
      errors: [],
      warnings: [],
    };

    if (!content.trim()) {
      result.errors.push('Research content is empty');
      result.valid = false;
      return result;
    }

    if (content.length < 300) {
      result.warnings.push('Research content very short');
    }

    // Check for required sections
    const requiredSections = ['summary', 'insights', 'references'];
    for (const section of requiredSections) {
      const pattern = new RegExp(`##?\\s+${section}`, 'i');
      if (!pattern.test(content)) {
        result.warnings.push(`Missing section: ${section}`);
      }
    }

    return result;
  }

  validateThinkingModel(content: string): ValidationResult {
    const result: ValidationResult = {
      valid: true,
      errors: [],
      warnings: [],
    };

    if (!content.trim()) {
      result.errors.push('Thinking model content is empty');
      result.valid = false;
      return result;
    }

    // Check for required elements
    const requiredElements = ['concepts', 'relationships', 'examples'];
    for (const element of requiredElements) {
      if (!content.toLowerCase().includes(element)) {
        result.warnings.push(`Content may lack: ${element}`);
      }
    }

    // Check structure
    const headerPattern = /^(#{1,6})\s+/gm;
    const headers = content.match(headerPattern) || [];
    if (headers.length < 3) {
      result.warnings.push('Content has limited structure');
    }

    return result;
  }
}
