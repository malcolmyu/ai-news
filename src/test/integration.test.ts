import { describe, it, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { loadConfig } from '../utils/config.js';
import { RSSFetcher } from '../agents/daily-reporter/fetchers/rss-fetcher.js';

describe('Integration Tests', () => {
  describe('Core Modules Integration', () => {
    it('should load config and create fetchers', async () => {
      const config = loadConfig();
      assert.ok(config);

      const rssFetcher = new RSSFetcher();
      assert.ok(rssFetcher);

      assert.ok(config.rssSources.length > 0);
      assert.ok(config.htmlSources.length > 0);
    });

    it('should have valid config structure', async () => {
      const config = loadConfig();

      assert.ok(config.openRouter);
      assert.equal(typeof config.openRouter.apiKey, 'string');
      assert.equal(typeof config.openRouter.baseUrl, 'string');
      assert.equal(typeof config.openRouter.model, 'string');

      config.rssSources.forEach((source, index) => {
        assert.ok(source.name, `RSS source ${index} has no name`);
        assert.ok(source.url, `RSS source ${index} has no URL`);
        assert.ok(source.category, `RSS source ${index} has no category`);
        assert.equal(typeof source.enabled, 'boolean');
        assert.ok(['rss', 'html'].includes(source.type));
      });

      config.htmlSources.forEach((source, index) => {
        assert.ok(source.name, `HTML source ${index} has no name`);
        assert.ok(source.url, `HTML source ${index} has no URL`);
        assert.ok(source.category, `HTML source ${index} has no category`);
        assert.equal(typeof source.enabled, 'boolean');
        assert.ok(['rss', 'html'].includes(source.type));
        assert.ok(source.selector, `HTML source ${index} has no selector`);
      });
    });
  });

  describe('Basic Functionality', () => {
    it('should handle environment variables correctly', async () => {
      assert.equal(typeof process.env.OPENROUTER_API_KEY, 'string');
    });

    it('should locate configuration files', async () => {
      const fs = await import('fs');
      const path = await import('path');

      const configFile = path.join(process.cwd(), 'config/sources.yaml');
      assert.ok(fs.existsSync(configFile));

      const harnessFile = path.join(process.cwd(), 'config/harness.yaml');
      assert.ok(fs.existsSync(harnessFile));
    });
  });
});
