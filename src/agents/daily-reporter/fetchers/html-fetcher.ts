import { chromium, Browser } from 'playwright';
import { Article } from '../../../types/index.js';
import { Logger } from '../../../utils/config.js';

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
  private logger: Logger;

  constructor(timeout: number = 30000) {
    this.timeout = timeout;
    this.logger = new Logger('HTMLFetcher');
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
      this.logger.log(`Fetching HTML (Playwright): ${source.url}`);

      // domcontentloaded is faster and more reliable than networkidle on SPAs
      await page.goto(source.url, {
        timeout: this.timeout,
        waitUntil: 'domcontentloaded',
      });

      const selector = source.selector || source.link_selector || 'a';

      // Wait for at least one matching element (up to 10s)
      try {
        await page.waitForSelector(selector, { timeout: 10000 });
      } catch {
        this.logger.warn(`Selector "${selector}" not found on ${source.url}, returning empty`);
        return [];
      }

      const elements = await page.$$(selector);
      const articles: Article[] = [];
      const seenLinks = new Set<string>(); // O(1) dedup

      for (let i = 0; i < Math.min(elements.length, 50); i++) {
        try {
          const el = elements[i];

          // Extract title
          let title = '';
          if (source.title_selector) {
            title = await el.$eval(source.title_selector, (e) => e.textContent?.trim() ?? '').catch(() => '');
          }
          if (!title) {
            title = (await el.textContent())?.trim() ?? '';
          }

          // Extract href via getAttribute (safe in both browser and Node TS contexts)
          let rawHref = '';
          if (source.link_selector && source.link_selector !== source.selector) {
            rawHref = await el.$eval(source.link_selector, (e) => e.getAttribute('href') ?? '').catch(() => '');
          } else {
            rawHref = await el.evaluate((e) => {
              const a = e.tagName === 'A' ? e : e.closest('a') ?? e.querySelector('a');
              return a?.getAttribute('href') ?? '';
            }).catch(() => '');
          }

          if (!rawHref || !title) continue;

          // Normalize URL — reject non-http(s) and resolve relative paths
          let link: string;
          try {
            const base = new URL(source.url);
            if (rawHref.startsWith('//')) {
              link = `${base.protocol}${rawHref}`;
            } else if (rawHref.startsWith('/')) {
              link = `${base.origin}${rawHref}`;
            } else if (rawHref.startsWith('http://') || rawHref.startsWith('https://')) {
              link = rawHref;
            } else if (rawHref.startsWith('mailto:') || rawHref.startsWith('javascript:') || rawHref.startsWith('#')) {
              continue; // skip non-navigable hrefs
            } else {
              link = new URL(rawHref, source.url).href;
            }
          } catch {
            continue;
          }

          // O(1) dedup by resolved link
          if (seenLinks.has(link)) continue;
          seenLinks.add(link);

          const content = source.content_selector
            ? await el.$eval(source.content_selector, (e) => e.textContent?.trim() ?? '').catch(() => '')
            : '';

          articles.push({
            title,
            link,
            content,
            summary: content,
            category: source.category,
            source: source.name,
          });
        } catch (err) {
          this.logger.warn(`Failed to parse element ${i} from ${source.url}: ${err}`);
        }
      }

      this.logger.log(`Fetched ${articles.length} articles from ${source.url}`);
      return articles;
    } catch (error) {
      this.logger.error(`Failed to fetch HTML from ${source.url}`, error as Error);
      return [];
    } finally {
      await page.close();
    }
  }
}
