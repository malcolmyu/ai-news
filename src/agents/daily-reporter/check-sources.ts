import * as fs from 'fs';
import * as yaml from 'js-yaml';
import { RSSFetcher } from './fetchers/rss-fetcher.js';
import { HTMLFetcher, HtmlSource } from './fetchers/html-fetcher.js';
import { Logger } from '../../utils/config.js';

interface SourceValidationResult {
  source: string;
  type: 'rss' | 'html';
  status: 'ok' | 'error' | 'skipped';
  message?: string;
  articles?: number;
}

class SourceChecker {
  private logger: Logger;
  private rssFetcher: RSSFetcher;
  private htmlFetcher: HTMLFetcher;
  private configPath: string;

  constructor() {
    this.logger = new Logger('SourceChecker');
    this.rssFetcher = new RSSFetcher();
    this.htmlFetcher = new HTMLFetcher();
    this.configPath = './config/sources.yaml';
  }

  async checkSource(configPath?: string): Promise<SourceValidationResult[]> {
    if (configPath) {
      this.configPath = configPath;
    }

    this.logger.log(`Checking sources from ${this.configPath}`);

    if (!fs.existsSync(this.configPath)) {
      this.logger.error(`Config file not found: ${this.configPath}`);
      return [];
    }

    const configContent = fs.readFileSync(this.configPath, 'utf8');
    const config = yaml.load(configContent) as any;

    const results: SourceValidationResult[] = [];
    const promises: Promise<void>[] = [];

    // Check RSS sources
    if (config.rss_sources) {
      for (const source of config.rss_sources) {
        promises.push(this.checkRssSource(source, results));
      }
    }

    // Check HTML sources
    if (config.html_sources) {
      for (const source of config.html_sources) {
        promises.push(this.checkHtmlSource(source, results));
      }
    }

    await Promise.all(promises);

    this.printResults(results);
    return results;
  }

  private async checkRssSource(source: any, results: SourceValidationResult[]): Promise<void> {
    const result: SourceValidationResult = {
      source: source.name,
      type: 'rss',
      status: 'ok',
    };

    if (!source.enabled) {
      result.status = 'skipped';
      result.message = 'Source disabled';
      results.push(result);
      return;
    }

    try {
      this.logger.log(`Checking RSS source: ${source.name}`);
      const articles = await this.rssFetcher.fetchFromURL(
        source.url,
        source.name,
        source.category,
        source.filter_categories,
        source.max_articles
      );

      result.articles = articles.length;
      result.message = `Successfully fetched ${articles.length} articles`;

      this.logger.log(`✓ ${source.name}: ${articles.length} articles`);
    } catch (error) {
      result.status = 'error';
      result.message = error instanceof Error ? error.message : 'Unknown error';
      this.logger.error(`✗ ${source.name}: ${result.message}`);
    }

    results.push(result);
  }

  private async checkHtmlSource(source: any, results: SourceValidationResult[]): Promise<void> {
    const result: SourceValidationResult = {
      source: source.name,
      type: 'html',
      status: 'ok',
    };

    if (!source.enabled) {
      result.status = 'skipped';
      result.message = 'Source disabled';
      results.push(result);
      return;
    }

    try {
      this.logger.log(`Checking HTML source: ${source.name}`);
      const htmlSource: HtmlSource = {
        name: source.name,
        url: source.url,
        selector: source.selector || '',
        title_selector: source.title_selector,
        link_selector: source.link_selector,
        content_selector: source.content_selector,
        category: source.category,
      };

      const articles = await this.htmlFetcher.fetchFromSource(htmlSource);

      result.articles = articles.length;
      result.message = `Successfully fetched ${articles.length} articles`;

      this.logger.log(`✓ ${source.name}: ${articles.length} articles`);
    } catch (error) {
      result.status = 'error';
      result.message = error instanceof Error ? error.message : 'Unknown error';
      this.logger.error(`✗ ${source.name}: ${result.message}`);
    }

    results.push(result);
  }

  private printResults(results: SourceValidationResult[]): void {
    console.log('\n=== Source Validation Results ===\n');

    const stats = {
      total: results.length,
      ok: results.filter(r => r.status === 'ok').length,
      error: results.filter(r => r.status === 'error').length,
      skipped: results.filter(r => r.status === 'skipped').length,
    };

    // Group by status
    const byStatus = results.reduce((acc, result) => {
      if (!acc[result.status]) {
        acc[result.status] = [];
      }
      acc[result.status].push(result);
      return acc;
    }, {} as Record<string, SourceValidationResult[]>);

    // Print errors first
    if (byStatus.error?.length > 0) {
      console.log('❌ Errors:');
      byStatus.error.forEach(result => {
        console.log(`  - ${result.source}: ${result.message || 'Unknown error'}`);
      });
      console.log();
    }

    // Print successful
    if (byStatus.ok?.length > 0) {
      console.log('✅ Working:');
      byStatus.ok.forEach(result => {
        console.log(`  - ${result.source}: ${result.articles} articles`);
      });
      console.log();
    }

    // Print skipped
    if (byStatus.skipped?.length > 0) {
      console.log('⏭️  Skipped:');
      byStatus.skipped.forEach(result => {
        console.log(`  - ${result.source}: ${result.message}`);
      });
      console.log();
    }

    // Print summary
    console.log('=== Summary ===');
    console.log(`Total sources: ${stats.total}`);
    console.log(`✅ Working: ${stats.ok}`);
    console.log(`❌ Errors: ${stats.error}`);
    console.log(`⏭️  Skipped: ${stats.skipped}`);

    if (stats.error > 0) {
      process.exit(1);
    }
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const checker = new SourceChecker();
  const configPath = process.argv[2];

  checker.checkSource(configPath).catch(error => {
    console.error('Failed to run source checker:', error);
    process.exit(1);
  });
}

export { SourceChecker };