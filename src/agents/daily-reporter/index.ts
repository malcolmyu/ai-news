import { RSSFetcher } from './fetchers/rss-fetcher.js';
import { HTMLFetcher } from './fetchers/html-fetcher.js';
import { Summarizer } from './summarizer.js';
import { DailyReportGenerator } from './generator.js';
import { HomepageBuilder } from '../homepage-builder/index.js';
import { loadConfig, formatDate, writeJSONFile, readJSONFile, Logger } from '../../utils/config.js';
import { Config, Article, SummarizedArticle, DailyReport, ArchiveEntry } from '../../types/index.js';
import { DailyChecker, DailyCheckReport } from './daily-checker.js';
import * as fs from 'fs';
import * as path from 'path';

const MAX_ARTICLES_PER_SOURCE = 2;

export class DailyReporter {
  private logger: Logger;
  private rssFetcher: RSSFetcher;
  private htmlFetcher: HTMLFetcher;
  private summarizer?: Summarizer;
  private generator: DailyReportGenerator;
  private config: Config;
  private dailyChecker: DailyChecker;

  constructor(config?: Config) {
    this.logger = new Logger('DailyReporter');
    this.rssFetcher = new RSSFetcher();
    this.htmlFetcher = new HTMLFetcher();
    this.generator = new DailyReportGenerator();
    this.dailyChecker = new DailyChecker();
    this.config = config || loadConfig();

    // Initialize summarizer if API key is available (ANTHROPIC_* 火山方舟 或 OPENROUTER_*)
    if (this.config.llm?.apiKey) {
      this.summarizer = new Summarizer(this.config.llm.apiKey, this.config.llm.baseUrl, {
        model: this.config.llm.model,
      });
    } else {
      this.logger.warn('LLM API key not configured (ANTHROPIC_API_KEY or OPENROUTER_API_KEY), summaries will not be generated');
    }
  }

  async generateDailyReport(date?: Date, options?: {
    noSummarize?: boolean;
    outputPath?: string;
    verbose?: boolean;
  }): Promise<string> {
    const targetDate = date || new Date();
    const dateStr = formatDate(targetDate);

    this.logger.log(`Generating daily report for ${dateStr}`);
    const startTime = Date.now();

    // Initialize daily check report
    const checkReport = this.dailyChecker.createEmptyReport(targetDate);

    try {
      // Fetch articles
      this.logger.log('Fetching articles from sources...');
      const fetchResult = await this.fetchArticlesWithCheck(checkReport, targetDate);

      const allArticles = fetchResult.allArticles;
      this.logger.log(`Fetched ${allArticles.length} raw articles`);

      // Filter to only today's articles
      const todayArticles = this.filterByDate(allArticles, targetDate);
      this.logger.log(`Filtered to ${todayArticles.length} articles for ${dateStr}`);

      if (todayArticles.length === 0) {
        this.dailyChecker.addWarning(checkReport, `No articles found for ${dateStr}`);
      }

      // Limit per source: max MAX_ARTICLES_PER_SOURCE per source
      const limitedArticles = this.limitPerSource(todayArticles, MAX_ARTICLES_PER_SOURCE);
      this.logger.log(`After per-source limit: ${limitedArticles.length} articles`);

      // Summarize articles
      let summarizedArticles: SummarizedArticle[] = [];

      if (!options?.noSummarize && this.summarizer && limitedArticles.length > 0) {
        this.logger.log('Summarizing articles...');
        summarizedArticles = await this.summarizer.summarizeBatch(limitedArticles);
      } else if (options?.noSummarize || limitedArticles.length === 0) {
        this.logger.log('Skipping article summarization');
        summarizedArticles = limitedArticles.map(article => ({
          ...article,
          summary: article.summary || article.content || '',
          summarized: false,
          summaryQuality: 0,
        }));
      } else {
        this.logger.warn('No summarizer available, using original content');
        summarizedArticles = limitedArticles.map(article => ({
          ...article,
          summary: article.summary || article.content || '',
          summarized: false,
          summaryQuality: 0,
        }));
      }

      // Create report object
      const report: DailyReport = {
        date: dateStr,
        articles: summarizedArticles,
        stats: {
          totalArticles: summarizedArticles.length,
          summarizedArticles: summarizedArticles.filter(a => a.summarized).length,
          avgSummaryQuality: this.calculateAvgQuality(summarizedArticles),
        },
      };

      // Save report data
      const dataPath = path.join(process.cwd(), 'data', 'daily', 'archives.json');
      this.saveReportToArchive(report, dataPath);

      // Generate HTML report
      const outputPath = options?.outputPath;
      const reportFile = this.generator.generateDailyReport(report, outputPath);

      // Generate archive page
      this.logger.log('Generating daily archive page...');
      const archives = this.buildArchiveEntries();
      this.generator.generateDailyArchive(archives);

      // Rebuild homepage
      this.logger.log('Rebuilding homepage...');
      const homepageBuilder = new HomepageBuilder();
      await homepageBuilder.buildHomepage();

      const duration = Date.now() - startTime;
      this.logger.log(`Daily report generated in ${duration}ms: ${reportFile}`);

      return reportFile;
    } catch (error) {
      this.logger.error('Failed to generate daily report:', error as Error);

      // Fetch-phase progress 已在 fetchArticlesWithCheck 末尾落盘；此处仅记录告警
      checkReport.warnings.push(`Report generation failed: ${(error as Error).message}`);

      throw error;
    } finally {
      // Always close Playwright browser (avoid zombie Chromium processes)
      await this.htmlFetcher.close();
    }
  }

  private buildArchiveEntries(): ArchiveEntry[] {
    const dailyDir = path.join(process.cwd(), 'docs', 'daily');
    if (!fs.existsSync(dailyDir)) return [];

    const files = fs.readdirSync(dailyDir)
      .filter(f => f.match(/^ai-news-\d{4}-\d{2}-\d{2}\.html$/))
      .sort()
      .reverse();

    // Read article counts from archive data
    const archivePath = path.join(process.cwd(), 'data', 'daily', 'archives.json');
    const archiveData = fs.existsSync(archivePath) ? readJSONFile(archivePath) : { reports: {} };

    return files.map(f => {
      const match = f.match(/ai-news-(\d{4})-(\d{2})-(\d{2})\.html/);
      const date = match ? `${match[1]}-${match[2]}-${match[3]}` : '';
      const dateDisplay = match ? `${match[1]}年${parseInt(match[2])}月${parseInt(match[3])}日` : f;
      const reportData = archiveData?.reports?.[date];
      const articles = reportData?.stats?.totalArticles || 0;

      return { date, dateDisplay, file: f, articles };
    });
  }

  private async fetchArticlesWithCheck(checkReport: DailyCheckReport, targetDate: Date): Promise<{ allArticles: Article[] }> {
    const allArticles: Article[] = [];

    // Check if target date is today
    const todayStr = formatDate(new Date());
    const targetDateStr = formatDate(targetDate);
    const isToday = todayStr === targetDateStr;

    // Fetch from RSS sources
    if (this.config.rssSources) {
      for (const source of this.config.rssSources.filter(s => s.enabled)) {
        // Skip GitHub Trending if not generating today's report
        if (source.name === 'GitHub Trending Daily' && !isToday) {
          this.logger.log(`Skipping ${source.name} (not generating today's report)`);
          continue;
        }

        const fetchStart = Date.now();
        try {
          this.logger.log(`Fetching from ${source.name}...`);
          let articles = await this.rssFetcher.fetchFromURL(
            source.url,
            source.name,
            source.category,
            source.filter_categories,
            source.max_articles
          );
          if (source.name === 'GitHub Trending Daily') {
            articles = this.stampArticlesWithReportDay(articles, targetDate);
          }

          allArticles.push(...articles);

          const duration = Date.now() - fetchStart;
          this.dailyChecker.addSourceCheck(checkReport, source, articles, true, undefined, duration);

          if (articles.length === 0) {
            this.dailyChecker.addWarning(checkReport, `Source ${source.name} returned 0 articles`);
          }
        } catch (error) {
          const duration = Date.now() - fetchStart;
          this.dailyChecker.addSourceCheck(checkReport, source, [], false, (error as Error).message, duration);
          this.logger.error(`Failed to fetch from RSS source ${source.name}:`, error as Error);
        }
      }
    }

    // Fetch from HTML sources
    if (this.config.htmlSources) {
      for (const source of this.config.htmlSources.filter(s => s.enabled)) {
        const fetchStart = Date.now();
        try {
          this.logger.log(`Fetching from ${source.name}...`);
          const htmlSource = {
            name: source.name,
            url: source.url,
            selector: source.selector || '',
            title_selector: source.title_selector,
            link_selector: source.link_selector,
            content_selector: source.content_selector,
            date_selector: source.date_selector,
            resolve_missing_article_date: source.resolve_missing_article_date,
            category: source.category,
          };
          const articles = await this.htmlFetcher.fetchFromSource(htmlSource);
          allArticles.push(...articles);

          const duration = Date.now() - fetchStart;
          this.dailyChecker.addSourceCheck(checkReport, source, articles, true, undefined, duration);

          if (articles.length === 0) {
            this.dailyChecker.addWarning(checkReport, `Source ${source.name} returned 0 articles`);
          }
        } catch (error) {
          const duration = Date.now() - fetchStart;
          this.dailyChecker.addSourceCheck(checkReport, source, [], false, (error as Error).message, duration);
          this.logger.error(`Failed to fetch from HTML source ${source.name}:`, error as Error);
        }
      }
    }

    // Remove duplicates based on title and link
    const uniqueArticles = this.removeDuplicates(allArticles);

    const progressPaths = this.dailyChecker.persistSourceProgress(checkReport);
    this.logger.log(
      `Source progress saved (${progressPaths.length} files) under .agent/progress/daily/`
    );

    // Print summary of daily check
    this.logger.log(`\n=== Daily Check Summary ===`);
    console.log(this.dailyChecker.generateSummary(checkReport));

    return { allArticles: uniqueArticles };
  }

  private removeDuplicates(articles: Article[]): Article[] {
    const seen = new Set<string>();
    const unique: Article[] = [];

    for (const article of articles) {
      // Create a composite key
      const key = `${article.title}|${article.link}`.toLowerCase().trim();

      if (!seen.has(key)) {
        seen.add(key);
        unique.push(article);
      }
    }

    return unique;
  }

  /**
   * Filter articles to only include those published on the target date.
   * 无 `published` 的条目仍保留（兼容旧数据）；HTML 源在配置 `date_selector` / 详情页解析后应与 RSS 同一天规则一致。
   */
  /** GitHub Trending RSS 无可靠 post 日期：以本次生成日报的目标日作为 published（与 fetch 当天对齐） */
  private stampArticlesWithReportDay(articles: Article[], targetDate: Date): Article[] {
    const ymd = formatDate(targetDate);
    const [y, m, d] = ymd.split('-').map(Number);
    const published = new Date(Date.UTC(y, m - 1, d));
    return articles.map(a => ({ ...a, published }));
  }

  private filterByDate(articles: Article[], targetDate: Date): Article[] {
    const targetDateStr = formatDate(targetDate);

    return articles.filter(article => {
      if (!article.published) {
        return true;
      }

      const articleDateStr = formatDate(new Date(article.published));
      return articleDateStr === targetDateStr;
    });
  }

  /**
   * Limit the number of articles per source.
   */
  private limitPerSource(articles: Article[], maxPerSource: number): Article[] {
    const sourceCount: Record<string, number> = {};
    const limited: Article[] = [];

    for (const article of articles) {
      const source = article.source || 'unknown';
      sourceCount[source] = (sourceCount[source] || 0);

      if (sourceCount[source] < maxPerSource) {
        limited.push(article);
        sourceCount[source]++;
      }
    }

    return limited;
  }

  private calculateAvgQuality(articles: SummarizedArticle[]): number {
    if (articles.length === 0) return 0;

    const totalQuality = articles.reduce((sum, article) => sum + (article.summaryQuality || 0), 0);
    return totalQuality / articles.length;
  }

  private saveReportToArchive(report: DailyReport, dataPath: string): void {
    try {
      const existingData = readJSONFile(dataPath) || { reports: {} };

      existingData.reports[report.date] = {
        date: report.date,
        file: `ai-daily-${report.date}.html`,
        stats: report.stats,
        generated: new Date().toISOString(),
      };

      writeJSONFile(dataPath, existingData);
      this.logger.log('Report saved to archive');
    } catch (error) {
      this.logger.error('Failed to save report to archive:', error as Error);
    }
  }

  async getStats(): Promise<any> {
    const dataPath = path.join(process.cwd(), 'data', 'daily', 'archives.json');
    const data = readJSONFile(dataPath) || { reports: {} };

    const reports = Object.values(data.reports);
    const totalArticles = reports.reduce((sum: number, report: any) => sum + (report.stats?.totalArticles || 0), 0);

    return {
      totalReports: reports.length,
      totalArticles,
      averageArticlesPerReport: totalArticles / reports.length || 0,
      latestReport: reports.length > 0 ? reports[reports.length - 1] : null,
    };
  }
}
