import * as xml2js from 'xml2js';
import { promisify } from 'util';
import * as https from 'https';
import * as http from 'http';
import { Article } from '../../../types/index.js';
import * as url from 'url';

const parseXML = promisify(xml2js.parseString);

export class RSSFetcher {
  private timeout: number;

  constructor(timeout: number = 30000) {
    this.timeout = timeout;
  }

  async fetchFromURL(urlStr: string, name: string, category?: string, filterCategories?: string[], maxArticles?: number): Promise<Article[]> {
    try {
      console.log(`Fetching RSS: ${urlStr}`);

      // 使用原生 http/https 来获取内容，避免 axios 的问题
      const xmlData = await this.fetchURLWithNative(urlStr);

      const result: any = await parseXML(xmlData);
      let articles: Article[] = [];

      if (result && result.rss && result.rss.channel) {
        const channel = Array.isArray(result.rss.channel) ? result.rss.channel[0] : result.rss.channel;
        const items = channel.item || [];

        for (const item of items) {
          const article = this.parseRSSItem(item, name, category);
          if (article) {
            articles.push(article);
          }
        }
      } else if (result && result.feed) {
        // Atom format
        const items = result.feed.entry || [];
        for (const entry of items) {
          const article = this.parseAtomEntry(entry, result.feed, name, category);
          if (article) {
            articles.push(article);
          }
        }
      }

      // Apply category filtering if specified
      if (filterCategories && filterCategories.length > 0) {
        articles = articles.filter(article =>
          article.categories &&
          article.categories.some(cat => filterCategories.includes(cat))
        );
      }

      // Apply max articles limit if specified
      if (maxArticles && maxArticles > 0) {
        articles = articles.slice(0, maxArticles);
      }

      console.log(`Fetched ${articles.length} articles from ${urlStr}`);
      return articles;
    } catch (error) {
      console.error(`Failed to fetch RSS from ${url}:`, error);
      return [];
    }
  }

  private parseRSSItem(item: any, sourceName: string, category?: string): Article | null {
    try {
      const title = item.title?.[0] || '';
      const link = item.link?.[0] || item.link?._ || '';

      if (!title || !link) {
        return null;
      }

      let published: Date | undefined;
      if (item.pubDate?.[0]) {
        published = new Date(item.pubDate[0]);
      } else if (item.published?.[0]) {
        published = new Date(item.published[0]);
      }

      const summary = item.description?.[0] || item.summary?.[0] || '';

      // Parse categories from RSS item
      const categories: string[] = [];
      if (item.category) {
        if (Array.isArray(item.category)) {
          categories.push(...item.category.map((cat: any) => cat.toString()));
        } else {
          categories.push(item.category.toString());
        }
      }

      return {
        title: title.toString(),
        link: link.toString(),
        summary,
        published,
        content: summary,
        category,
        categories: categories.length > 0 ? categories : undefined,
        source: sourceName,
      };
    } catch (error) {
      console.error('Failed to parse RSS item:', error);
      return null;
    }
  }

  private parseAtomEntry(entry: any, feed: any, sourceName: string, category?: string): Article | null {
    try {
      const title = entry.title?.[0] || '';
      const linkElement = entry.link?.find((l: any) => l.$.rel === 'alternate') || entry.link?.[0];
      const link = linkElement?.$?.href || linkElement || '';

      if (!title || !link) {
        return null;
      }

      let published: Date | undefined;
      if (entry.published?.[0]) {
        published = new Date(entry.published[0]);
      } else if (entry.updated?.[0]) {
        published = new Date(entry.updated[0]);
      }

      const summary = entry.summary?.[0] || entry.content?.[0] || '';

      // Parse categories from Atom entry
      const categories: string[] = [];
      if (entry.category) {
        if (Array.isArray(entry.category)) {
          categories.push(...entry.category.map((cat: any) => cat.$.term || cat.toString()));
        } else {
          categories.push(entry.category.$.term || entry.category.toString());
        }
      }

      return {
        title: title.toString(),
        link: link.toString(),
        summary,
        published,
        content: summary,
        category,
        categories: categories.length > 0 ? categories : undefined,
        source: sourceName,
      };
    } catch (error) {
      console.error('Failed to parse Atom entry:', error);
      return null;
    }
  }

  private async fetchURLWithNative(urlStr: string): Promise<string> {
    const parsedUrl = new URL(urlStr);
    const protocol = parsedUrl.protocol === 'https:' ? https : http;

    return new Promise((resolve, reject) => {
      const req = protocol.request({
        hostname: parsedUrl.hostname,
        path: parsedUrl.pathname + (parsedUrl.search || ''),
        method: 'GET',
        headers: {
          'User-Agent': 'Mozilla/5.0 (compatible; GrowthWebsiteBot/1.0)',
          'Accept': 'application/rss+xml, application/xml, text/xml',
        }
      }, (res) => {
        let data = '';

        res.on('data', (chunk) => {
          data += chunk;
        });

        res.on('end', () => {
          resolve(data);
        });

        res.on('error', reject);
      });

      req.setTimeout(this.timeout, () => {
        req.destroy();
        reject(new Error(`Request timeout after ${this.timeout}ms`));
      });

      req.on('error', reject);
      req.end();
    });
  }

  fetchFromFile(filePath: string, name: string): Promise<Article[]> {
    // TODO: Implement file-based RSS loading if needed
    console.warn('File-based RSS loading not implemented');
    return Promise.resolve([]);
  }
}