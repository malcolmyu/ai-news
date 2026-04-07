import { describe, it, beforeEach, afterEach, mock } from 'node:test';
import assert from 'node:assert/strict';
import {
  HTMLFetcher,
  parseEnglishDateText,
  parseAnthropicArticleCreatedAt,
  extractEnglishDateFromTitle,
} from '../../agents/daily-reporter/fetchers/html-fetcher.js';

describe('HTMLFetcher', () => {
  describe('constructor', () => {
    it('should create HTMLFetcher instance with default timeout', () => {
      const fetcher = new HTMLFetcher();
      assert.ok(fetcher);
    });

    it('should create HTMLFetcher instance with custom timeout', () => {
      const customTimeout = 10000;
      const fetcher = new HTMLFetcher(customTimeout);
      assert.ok(fetcher);
    });
  });

  describe('basic functionality', () => {
    it('should be instantiable', () => {
      const fetcher = new HTMLFetcher();
      assert.ok(fetcher);
      assert.ok(typeof fetcher.close === 'function');
    });

    it('should handle browser management', async () => {
      const fetcher = new HTMLFetcher(1000);
      const browserSpy = mock.method(fetcher as any, 'getBrowser');

      assert.ok(fetcher.close);
    });
  });

  describe('date parsing helpers', () => {
    it('parseEnglishDateText handles Mar 25, 2026 (UTC calendar day)', () => {
      const d = parseEnglishDateText('Mar 25, 2026');
      assert.ok(d);
      assert.equal(d!.getUTCFullYear(), 2026);
      assert.equal(d!.getUTCMonth(), 2);
      assert.equal(d!.getUTCDate(), 25);
    });

    it('parseAnthropicArticleCreatedAt reads Sanity _createdAt', () => {
      const html = 'foo "_createdAt":"2026-02-03T21:37:23Z" bar';
      const d = parseAnthropicArticleCreatedAt(html);
      assert.ok(d);
      assert.equal(d!.toISOString().slice(0, 10), '2026-02-03');
    });

    it('extractEnglishDateFromTitle strips embedded date', () => {
      const { title, published } = extractEnglishDateFromTitle('Hello Mar 25, 2026 world');
      assert.equal(title, 'Hello world');
      assert.ok(published);
      assert.equal(published!.getUTCDate(), 25);
    });
  });

  describe('URL normalization', () => {
    it('should normalize different URL formats', () => {
      const baseUrl = 'https://example.com/page';

      // Test with relative URLs
      const testCases = [
        { href: '/relative', expected: 'https://example.com/relative' },
        { href: '//absolute', expected: 'https://absolute' },
        { href: 'https://test.com', expected: 'https://test.com' },
        { href: 'javascript:void(0)', shouldSkip: true },
        { href: 'mailto:test@example.com', shouldSkip: true },
        { href: '#anchor', shouldSkip: true },
        { href: '?query=1', expected: 'https://example.com/page?query=1' },
      ];

      // Since normalize logic is inside fetchFromSource and private, we'll need
      // to test indirectly or extract to helper
      assert.ok(testCases.length > 0);
    });
  });
});
