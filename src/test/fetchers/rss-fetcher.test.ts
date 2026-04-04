import { describe, it, beforeEach, afterEach, mock } from 'node:test';
import assert from 'node:assert/strict';
import { RSSFetcher } from '../../agents/daily-reporter/fetchers/rss-fetcher.js';
import { createMockRSSContent, createMockAtomContent } from '../utils/test-utils.js';
import axios from 'axios';

describe('RSSFetcher', () => {
  let fetcher: RSSFetcher;

  beforeEach(() => {
    fetcher = new RSSFetcher(5000);
  });

  describe('constructor', () => {
    it('should create RSSFetcher instance with default timeout', () => {
      const defaultFetcher = new RSSFetcher();
      assert.ok(defaultFetcher);
    });

    it('should create RSSFetcher instance with custom timeout', () => {
      assert.ok(fetcher);
    });
  });

  describe('fetchFromURL', () => {
    it('should create fetcher instance without errors', () => {
      assert.ok(fetcher);
    });

    it('should accept valid URL parameters', () => {
      assert.ok(typeof fetcher.fetchFromURL === 'function');
    });

    it('should return Promise type from fetch method', () => {
      const result = fetcher.fetchFromURL('https://example.com/feed', 'Test Source');
      assert.ok(result);
      assert.ok(typeof result.then === 'function');
      assert.ok(typeof result.catch === 'function');
    });
  });
});
