import * as xml2js from 'xml2js';
import { promisify } from 'util';
import * as https from 'https';
import * as http from 'http';
import { Article } from '../../../types/index.js';
import axios from 'axios';

const parseXML = promisify(xml2js.parseString);

export class RSSFetcher {
  private timeout: number;

  constructor(timeout: number = 30000) {
    this.timeout = timeout;
  }

  async fetchFromURL(url: string, name: string, category?: string): Promise<Article[]> {
    try {
      console.log(`Fetching RSS: ${url}`);

      const response = await axios.get(url, {
        timeout: this.timeout,
        headers: {
          'User-Agent': 'Mozilla/5.0 (compatible; GrowthWebsiteBot/1.0)',
          'Accept': 'application/rss+xml, application/xml, text/xml',
        },
        maxRedirects: 5,
      });

      const result: any = await parseXML(response.data);
      const articles: Article[] = [];

      if (result.rss && result.rss.channel) {
        const channel = Array.isArray(result.rss.channel) ? result.rss.channel[0] : result.rss.channel;
        const items = channel.item || [];

        for (const item of items) {
          const article = this.parseRSSItem(item, name, category);
          if (article) {
            articles.push(article);
          }
        }
      } else if (result.feed) {
        // Atom format
        const items = result.feed.entry || [];
        for (const entry of items) {
          const article = this.parseAtomEntry(entry, result.feed, name, category);
          if (article) {
            articles.push(article);
          }
        }
      }

      console.log(`Fetched ${articles.length} articles from ${url}`);
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

      return {
        title: title.toString(),
        link: link.toString(),
        summary,
        published,
        content: summary,
        category,
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

      return {
        title: title.toString(),
        link: link.toString(),
        summary,
        published,
        content: summary,
        category,
        source: sourceName,
      };
    } catch (error) {
      console.error('Failed to parse Atom entry:', error);
      return null;
    }
  }

  fetchFromFile(filePath: string, name: string): Promise<Article[]> {
    // TODO: Implement file-based RSS loading if needed
    console.warn('File-based RSS loading not implemented');
    return Promise.resolve([]);
  }
}