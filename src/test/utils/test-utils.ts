import type { Article, SourceConfig } from '../../types/index.js';

export function createMockArticle(overrides: Partial<Article> = {}): Article {
  return {
    title: 'Test Article',
    link: 'https://example.com/test',
    summary: 'This is a test article summary',
    content: 'Full article content',
    published: new Date('2024-01-01'),
    category: 'Technology',
    categories: ['AI', 'Technology'],
    source: 'Test Source',
    ...overrides,
  };
}

export function createMockRSSSource(overrides: Partial<SourceConfig> = {}): SourceConfig {
  return {
    name: 'Test RSS Source',
    url: 'https://example.com/feed.xml',
    category: 'Technology',
    enabled: true,
    type: 'rss',
    ...overrides,
  };
}

export function createMockHTMLSource(overrides: Partial<SourceConfig> = {}): SourceConfig {
  return {
    name: 'Test HTML Source',
    url: 'https://example.com',
    category: 'Technology',
    enabled: true,
    type: 'html',
    selector: 'article',
    ...overrides,
  };
}

export function mockConsole() {
  const originalLog = console.log;
  const originalError = console.error;
  const originalWarn = console.warn;
  const originalInfo = console.info;
  const originalDebug = console.debug;

  const logs: string[] = [];
  const errors: string[] = [];
  const warnings: string[] = [];
  const infos: string[] = [];
  const debugs: string[] = [];

  console.log = (...args) => logs.push(args.join(' '));
  console.error = (...args) => errors.push(args.join(' '));
  console.warn = (...args) => warnings.push(args.join(' '));
  console.info = (...args) => infos.push(args.join(' '));
  console.debug = (...args) => debugs.push(args.join(' '));

  return {
    logs,
    errors,
    warnings,
    infos,
    debugs,
    restore: () => {
      console.log = originalLog;
      console.error = originalError;
      console.warn = originalWarn;
      console.info = originalInfo;
      console.debug = originalDebug;
    },
  };
}

export function createMockRSSContent(title: string = 'Test Article', link: string = 'https://example.com/test'): string {
  return `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Feed</title>
    <link>https://example.com</link>
    <description>Test RSS Feed</description>
    <item>
      <title><![CDATA[${title}]]></title>
      <link><![CDATA[${link}]]></link>
      <description><![CDATA[This is a test article]]></description>
      <pubDate>Mon, 01 Jan 2024 00:00:00 GMT</pubDate>
      <category>AI</category>
      <category>Technology</category>
    </item>
  </channel>
</rss>`;
}

export function createMockAtomContent(title: string = 'Test Article', link: string = 'https://example.com/test'): string {
  return `<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Test Feed</title>
  <link href="https://example.com"/>
  <updated>2024-01-01T00:00:00Z</updated>
  <id>https://example.com/feed</id>
  <entry>
    <title>${title}</title>
    <link href="${link}"/>
    <summary>This is a test article</summary>
    <published>2024-01-01T00:00:00Z</published>
    <category term="AI"/>
    <category term="Technology"/>
  </entry>
</feed>`;
}
