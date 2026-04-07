import { chromium, Browser, Page } from 'playwright';
import { Article } from '../../../types/index.js';
import { Logger } from '../../../utils/config.js';

export interface HtmlSource {
  name: string;
  url: string;
  selector: string;
  /** 相对每条匹配元素，取标题（避免整段 a 的 textContent 混入日期等） */
  title_selector?: string;
  link_selector?: string;
  content_selector?: string;
  /** 相对每条链接根元素，用于取发布日期（默认尝试 `div[class*="__date"]`） */
  date_selector?: string;
  /** 列表无日期时打开文章页，从嵌入数据解析发布时间 */
  resolve_missing_article_date?: boolean;
  category?: string;
}

const EN_MONTH: Record<string, number> = {
  Jan: 0,
  Feb: 1,
  Mar: 2,
  Apr: 3,
  May: 4,
  Jun: 5,
  Jul: 6,
  Aug: 7,
  Sep: 8,
  Oct: 9,
  Nov: 10,
  Dec: 11,
};

/** 解析列表中的英文日期文案，如 "Mar 25, 2026"（按公历日对齐 UTC，与 formatDate 一致） */
export function parseEnglishDateText(text: string): Date | undefined {
  const t = text.trim();
  if (!t) return undefined;
  const m = t.match(/^([A-Za-z]{3})\s+(\d{1,2}),\s+(\d{4})$/);
  if (m) {
    const mon = EN_MONTH[m[1]];
    if (mon === undefined) return undefined;
    const day = parseInt(m[2], 10);
    const year = parseInt(m[3], 10);
    return new Date(Date.UTC(year, mon, day));
  }
  const ms = Date.parse(t);
  if (Number.isNaN(ms)) return undefined;
  return new Date(ms);
}

/**
 * 从标题文案中剥离 "Mar 25, 2026" 式日期（用于列表未单独给 __date 节点时）
 */
export function extractEnglishDateFromTitle(title: string): { title: string; published?: Date } {
  const re = /\b([A-Za-z]{3})\s+(\d{1,2}),\s+(\d{4})\b/;
  const m = title.match(re);
  if (!m) return { title: title.trim() };
  const published = parseEnglishDateText(`${m[1]} ${m[2]}, ${m[3]}`);
  const clean = title
    .replace(re, '')
    .replace(/\s+/g, ' ')
    .replace(/^[·\s\-–—|]+|[·\s\-–—|]+$/g, '')
    .trim();
  return { title: clean || title.trim(), published };
}

/**
 * 从 Anthropic 文章页 HTML 中的 Sanity 载荷解析 `_createdAt`（与站内展示日期一致来源）
 */
export function parseAnthropicArticleCreatedAt(html: string): Date | undefined {
  const m = html.match(/"_createdAt":"([^"]+)"/);
  if (!m?.[1]) return undefined;
  const ms = Date.parse(m[1]);
  if (Number.isNaN(ms)) return undefined;
  return new Date(ms);
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

  private async fetchPublishedFromArticlePage(page: Page, url: string): Promise<Date | undefined> {
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: this.timeout });
      const html = await page.content();
      return parseAnthropicArticleCreatedAt(html);
    } catch (e) {
      this.logger.warn(`resolve_missing_article_date failed for ${url}: ${e}`);
      return undefined;
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

          let published: Date | undefined;
          const dateSel = source.date_selector ?? 'div[class*="__date"]';
          try {
            const dateHandle = await el.$(dateSel);
            if (dateHandle) {
              const dateText = (await dateHandle.textContent())?.trim() ?? '';
              published = parseEnglishDateText(dateText);
              await dateHandle.dispose();
            }
          } catch {
            /* ignore date parse errors for this row */
          }

          if (!published) {
            const fromTitle = extractEnglishDateFromTitle(title);
            title = fromTitle.title;
            published = fromTitle.published;
          }

          articles.push({
            title,
            link,
            content,
            summary: content,
            category: source.category,
            source: source.name,
            published,
          });
        } catch (err) {
          this.logger.warn(`Failed to parse element ${i} from ${source.url}: ${err}`);
        }
      }

      if (source.resolve_missing_article_date) {
        for (const art of articles) {
          if (!art.published) {
            const resolved = await this.fetchPublishedFromArticlePage(page, art.link);
            if (resolved) {
              art.published = resolved;
            }
          }
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
