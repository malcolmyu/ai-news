import { describe, it, beforeEach, afterEach, mock } from 'node:test';
import assert from 'node:assert/strict';
import {
  loadConfig,
  ensureDir,
  writeJSONFile,
  readJSONFile,
  formatDate,
  normalizeVolcengineCodingBaseUrl,
} from '../../utils/config.js';
import * as fs from 'fs';
import * as path from 'path';

describe('Config Utilities', () => {
  describe('formatDate', () => {
    it('should format current date correctly', () => {
      const formatted = formatDate();
      const datePattern = /^\d{4}-\d{2}-\d{2}$/;
      assert.ok(datePattern.test(formatted));
    });

    it('should format specific date correctly', () => {
      const testDate = new Date('2024-12-31');
      const formatted = formatDate(testDate);
      assert.equal(formatted, '2024-12-31');
    });
  });

  describe('file operations', () => {
    const tempDir = path.join(process.cwd(), 'temp-test-dir');
    const tempFile = path.join(tempDir, 'test.json');

    afterEach(() => {
      if (fs.existsSync(tempFile)) {
        fs.unlinkSync(tempFile);
      }
      if (fs.existsSync(tempDir)) {
        fs.rmdirSync(tempDir, { recursive: true });
      }
    });

    it('should ensure directory exists', () => {
      assert.ok(!fs.existsSync(tempDir));

      ensureDir(tempDir);

      assert.ok(fs.existsSync(tempDir));
      assert.ok(fs.statSync(tempDir).isDirectory());
    });

    it('should write JSON file', () => {
      ensureDir(tempDir);
      const testData = { key: 'value', number: 123, array: [1, 2, 3] };

      writeJSONFile(tempFile, testData);

      assert.ok(fs.existsSync(tempFile));

      const fileContent = fs.readFileSync(tempFile, 'utf8');
      const parsedData = JSON.parse(fileContent);
      assert.deepEqual(parsedData, testData);
    });

    it('should read existing JSON file', () => {
      ensureDir(tempDir);
      const testData = { key: 'value', nested: { obj: true } };
      fs.writeFileSync(tempFile, JSON.stringify(testData, null, 2));

      const result = readJSONFile(tempFile);

      assert.deepEqual(result, testData);
    });

    it('should return null when file does not exist', () => {
      const nonExistentFile = path.join(tempDir, 'non-existent-file.json');
      const result = readJSONFile(nonExistentFile);
      assert.equal(result, null);
    });
  });

  describe('loadConfig', () => {
    it('should load configuration from YAML files', () => {
      const config = loadConfig();

      assert.ok(config);
      assert.ok(config.llm);
      assert.equal(typeof config.llm.apiKey, 'string');
      assert.equal(typeof config.llm.baseUrl, 'string');
      assert.equal(typeof config.llm.model, 'string');

      assert.ok(Array.isArray(config.rssSources));
      assert.ok(Array.isArray(config.htmlSources));
      assert.ok(config.harness);
    });

    it('should load existing RSS and HTML sources', () => {
      const config = loadConfig();

      assert.ok(config.rssSources.length > 0);
      config.rssSources.forEach(source => {
        assert.ok(source.name);
        assert.ok(source.url);
        assert.ok(source.category);
        assert.ok(typeof source.enabled === 'boolean');
      });

      assert.ok(config.htmlSources.length > 0);
      config.htmlSources.forEach(source => {
        assert.ok(source.name);
        assert.ok(source.url);
        assert.ok(source.category);
        assert.ok(typeof source.enabled === 'boolean');
        if (source.type === 'html') {
          assert.ok(source.selector);
        }
      });
    });

    it('normalizes Volcano coding base URL when /v3 is omitted', () => {
      assert.equal(
        normalizeVolcengineCodingBaseUrl('https://ark.cn-beijing.volces.com/api/coding'),
        'https://ark.cn-beijing.volces.com/api/coding/v3'
      );
      assert.equal(
        normalizeVolcengineCodingBaseUrl('https://ark.cn-beijing.volces.com/api/coding/v3'),
        'https://ark.cn-beijing.volces.com/api/coding/v3'
      );
    });
  });
});
