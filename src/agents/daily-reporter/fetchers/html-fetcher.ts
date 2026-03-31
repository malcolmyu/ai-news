import { chromium, Browser } from 'playwright';
import { Article } from '../../../types/index.js';

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
  private browser: Browser | null = null;

  constructor(timeout: number = 30000) {
    this.timeout = timeout;
  }

  private async getBrowser(): Promise<Browser> {
    if (!this.browser) {
      this.browser = await chromium.launch({ headless: true });
    }
    return this.browser;
  }

  async close(): Promise<void> {
    if (this.browser) {
      await this.browser.close();
      this.browser = null;
    }
  }

  async fetchFromSource(source: HtmlSource): Promise<Article[]> {
    const browser = await this.getBrowser();
    const page = await browser.newPage();

    try {
      console.log(`Fetching HTML (Playwright): ${source.url}`);

      await page.goto(source.url, {
        timeout: this.timeout,
        waitUntil: 'networkidle',
      });

      const selector = source.selector || source.link_selector || 'a';
      const elements = await page.$$(selector);
      const articles: Article[] = [];

      for (let i = 0; i < Math.min(elements.length, 50); i++) {
        try {
          const el = elements[i];

          // Extract title
          let title = '';
          if (source.title_selector) {
            title = await el.$eval(source.title_selector, (e) => e.textContent?.trim() || '').catch(() => '');
          }
          if (!title) {
            title = (await el.textContent())?.trim() || '';
          }

          // Extract link
          let link = '';
          if (source.link_selector && source.link_selector !== source.selector) {
            link = await el.$eval(source.link_selector, (e) => (e as HTMLAnchorElement).href || '').catch(() => '');
          } else {
            link = await el.evaluate((e) => {
              const a = e.tagName === 'A' ? e : e.closest('a') ?? e.querySelector('a');
              return (a as HTMLAnchorElement | null)?.href || '';
            }).catch(() => '');
          }

          if (!title || !link) continue;

          // Handle relative URLs
          if (link.startsWith('/')) {
            const urlObj = new URL(source.url);
            link = `${urlObj.origin}${link}`;
          } else if (!link.startsWith('http')) {
            try {
              link = new URL(link, source.url).href;
            } catch {
              continue;
            }
          }

          // Deduplicate by link
          if (articles.some((a) => a.link === link)) continue;

          const content = source.content_selector
            ? await el.$eval(source.content_selector, (e) => e.textContent?.trim() || '').catch(() => '')
            : '';

          articles.push({
            title,
            link,
            content: content || '',
            summary: content || '',
            category: source.category,
            source: source.name,
          });
        } catch (err) {
          console.warn(`Failed to parse element ${i} from ${source.url}:`, err);
        }
      }

      console.log(`Fetched ${articles.length} articles from ${source.url}`);
      return articles;
    } catch (error) {
      console.error(`Failed to fetch HTML from ${source.url}:`, error);
      return [];
    } finally {
      await page.close();
    }
  }
}
