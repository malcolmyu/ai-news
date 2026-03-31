import * as https from 'https';
import * as http from 'http';
import { JSDOM } from 'jsdom';
import { load as cheerioLoad } from 'cheerio';
import { Article } from '../types/index.js';
import axios from 'axios';

export interface HtmlSource {
  name: string;
  url: string;
  selector: string;
  title_selector?: string;
  link_selector?: string;
  content_selector?: string;
  category?: string;
}

export class HTMLFetcher {
  private timeout: number;

  constructor(timeout: number = 30000) {
    this.timeout = timeout;
  }

  async fetchFromSource(source: HtmlSource): Promise<Article[]> {
    try {
      console.log(`Fetching HTML: ${source.url}`);

      const response = await axios.get(source.url, {
        timeout: this.timeout,
        headers: {
          'User-Agent': 'Mozilla/5.0 (compatible; GrowthWebsiteBot/1.0)',
          'Accept': 'text/html,application/xhtml+xml,application/xml',
        },
        maxRedirects: 5,
      });

      const dom = new JSDOM(response.data);
      const document = dom.window.document;

      const elements = document.querySelectorAll(source.selector);
      const articles: Article[] = [];

      for (let i = 0; i < Math.min(elements.length, 50); i++) {
        try {
          const element = elements[i];

          let title = '';
          let link = '';

          if (source.title_selector) {
            const titleElement = element.querySelector(source.title_selector);
            title = titleElement?.textContent?.trim() || '';
          } else {
            title = element.textContent?.trim() || '';
          }

          if (source.link_selector) {
            const linkElement = element.querySelector(source.link_selector);
            link = linkElement?.getAttribute('href') || '';
          } else {
            const anchorElement = element.closest('a') || element.querySelector('a');
            link = anchorElement?.getAttribute('href') || '';
          }

          if (!title || !link) {
            continue;
          }

          // Handle relative URLs
          if (link.startsWith('/')) {
            const urlObj = new URL(source.url);
            link = `${urlObj.origin}${link}`;
          } else if (link.startsWith('./') || link.startsWith('../')) {
            const urlObj = new URL(source.url);
            link = new URL(link, urlObj.href).href;
          }

          const content = source.content_selector
            ? element.querySelector(source.content_selector)?.textContent?.trim()
            : '';

          articles.push({
            title,
            link,
            content: content || '',
            summary: content || '',
            category: source.category,
            source: source.name,
          });

        } catch (error) {
          console.warn(`Failed to parse article ${i}:`, error);
        }
      }

      console.log(`Fetched ${articles.length} articles from ${source.url}`);
      return articles;

    } catch (error) {
      console.error(`Failed to fetch HTML from ${source.url}:`, error);
      return [];
    }
  }
}
