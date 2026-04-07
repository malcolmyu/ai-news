import { describe, it, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import * as fs from 'fs';
import * as path from 'path';
import {
  DailyChecker,
  makeSourceSlug,
  normalizeArticleLink,
  SOURCE_PROGRESS_FILE_PREFIX,
} from '../../agents/daily-reporter/daily-checker.js';
import type { SourceConfig } from '../../types/index.js';
import type { Article } from '../../types/index.js';

describe('DailyChecker — source progress v2', () => {
  const tempDir = path.join(process.cwd(), 'temp-daily-checker-test');

  afterEach(() => {
    if (fs.existsSync(tempDir)) {
      fs.rmSync(tempDir, { recursive: true });
    }
  });

  it('makeSourceSlug is stable for same name+url', () => {
    const a = makeSourceSlug({ name: '宝玉', url: 'https://s.baoyu.io/feed.xml' });
    const b = makeSourceSlug({ name: '宝玉', url: 'https://s.baoyu.io/feed.xml' });
    assert.equal(a, b);
    assert.ok(!a.startsWith('src-'));
    assert.ok(a.includes('-'));
  });

  it('normalizeArticleLink strips hash and trailing slash', () => {
    assert.equal(
      normalizeArticleLink('https://ExAmple.com/path/to/x/'),
      'https://example.com/path/to/x'
    );
  });

  it('persistSourceProgress merges articles by link and sets reportDate', () => {
    fs.mkdirSync(tempDir, { recursive: true });
    const checker = new DailyChecker(tempDir);
    const source: SourceConfig = {
      name: 'Merge Test',
      url: 'https://example.com/feed.xml',
      category: 'tech',
      enabled: true,
      type: 'rss',
    };

    const art = (t: string, link: string): Article => ({
      title: t,
      link,
      source: source.name,
      category: source.category,
      published: new Date('2026-04-05T00:00:00.000Z'),
    });

    const r1 = checker.createEmptyReport(new Date('2026-04-05'));
    checker.addSourceCheck(r1, source, [art('One', 'https://x.com/a')], true, undefined, 1);
    checker.persistSourceProgress(r1);

    const r2 = checker.createEmptyReport(new Date('2026-04-06'));
    checker.addSourceCheck(
      r2,
      source,
      [
        art('One updated', 'https://x.com/a'),
        art('Two', 'https://x.com/b'),
      ],
      true,
      undefined,
      1
    );
    checker.persistSourceProgress(r2);

    const slug = makeSourceSlug({ name: source.name, url: source.url });
    const filePath = path.join(tempDir, `${SOURCE_PROGRESS_FILE_PREFIX}${slug}.json`);
    const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    assert.equal(data._schema, 'ai-news-source-progress/v2');
    assert.equal(data.articles.length, 2);
    const aRow = data.articles.find((x: { link: string }) => x.link.includes('/a'));
    assert.ok(aRow);
    assert.equal(aRow.title, 'One updated');
    assert.equal(aRow.reportDate, '2026-04-06');
  });

  it('migrates v1 runs file to v2 on next persist', () => {
    fs.mkdirSync(tempDir, { recursive: true });
    const source: SourceConfig = {
      name: 'X',
      url: 'https://x.com',
      category: 'tech',
      enabled: true,
      type: 'rss',
    };
    const filePath = path.join(tempDir, `${SOURCE_PROGRESS_FILE_PREFIX}${makeSourceSlug(source)}.json`);
    fs.writeFileSync(
      filePath,
      JSON.stringify(
        {
          _schema: 'ai-news-source-progress/v1',
          sourceName: 'X',
          sourceUrl: 'https://x.com',
          sourceType: 'rss',
          runs: [
            {
              reportDate: '2026-04-01',
              articles: [
                {
                  title: 'Old',
                  link: 'https://x.com/p1',
                  publishedDate: '2026-03-20',
                  hasSummary: false,
                  summaryLength: 0,
                },
              ],
            },
          ],
        },
        null,
        2
      ),
      'utf8'
    );

    const checker = new DailyChecker(tempDir);
    const report = checker.createEmptyReport(new Date('2026-04-10'));
    checker.addSourceCheck(
      report,
      source,
      [
        {
          title: 'Old',
          link: 'https://x.com/p1',
          category: source.category,
          source: source.name,
          published: new Date('2026-03-20T00:00:00.000Z'),
        },
      ],
      true,
      undefined,
      1
    );
    checker.persistSourceProgress(report);

    const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    assert.equal(data._schema, 'ai-news-source-progress/v2');
    assert.ok(Array.isArray(data.articles));
    assert.equal(data.articles.length, 1);
    assert.equal(data.articles[0].link, 'https://x.com/p1');
    assert.equal(data.articles[0].reportDate, '2026-04-10');
  });
});
