import { Article, SourceConfig } from '../../types/index.js';
import { writeJSONFile, ensureDir, formatDate } from '../../utils/config.js';
import * as path from 'path';

export interface SourceCheckResult {
  sourceName: string;
  sourceUrl: string;
  sourceType: 'rss' | 'html';
  enabled: boolean;
  fetchedArticles: number;
  articles: Array<{
    title: string;
    link: string;
    publishedDate: string | null;
    category: string | undefined;
    categories: string[] | undefined;
    hasSummary: boolean;
    summaryLength: number;
  }>;
  fetchSuccess: boolean;
  errorMessage?: string;
  fetchDuration?: number;
}

export interface DailyCheckReport {
  date: string;
  generatedAt: string;
  totalSources: number;
  successfulSources: number;
  failedSources: number;
  totalFetchedArticles: number;
  sources: SourceCheckResult[];
  warnings: string[];
}

export class DailyChecker {
  private progressDir: string;

  constructor() {
    this.progressDir = path.join(process.cwd(), '.agent', 'progress', 'daily');
    ensureDir(this.progressDir);
  }

  createEmptyReport(date: Date): DailyCheckReport {
    const dateStr = formatDate(date);
    return {
      date: dateStr,
      generatedAt: new Date().toISOString(),
      totalSources: 0,
      successfulSources: 0,
      failedSources: 0,
      totalFetchedArticles: 0,
      sources: [],
      warnings: [],
    };
  }

  addSourceCheck(
    report: DailyCheckReport,
    source: SourceConfig,
    articles: Article[],
    fetchSuccess: boolean,
    errorMessage?: string,
    fetchDuration?: number
  ): void {
    const sourceResult: SourceCheckResult = {
      sourceName: source.name,
      sourceUrl: source.url,
      sourceType: source.type,
      enabled: source.enabled,
      fetchedArticles: articles.length,
      articles: articles.map(article => ({
        title: article.title,
        link: article.link,
        publishedDate: article.published ? formatDate(new Date(article.published)) : null,
        category: article.category,
        categories: article.categories,
        hasSummary: !!article.summary,
        summaryLength: article.summary?.length || 0,
      })),
      fetchSuccess,
      errorMessage,
      fetchDuration,
    };

    report.sources.push(sourceResult);
    report.totalSources++;

    if (fetchSuccess) {
      report.successfulSources++;
    } else {
      report.failedSources++;
    }

    report.totalFetchedArticles += articles.length;
  }

  addWarning(report: DailyCheckReport, warning: string): void {
    report.warnings.push(warning);
  }

  saveReport(report: DailyCheckReport): string {
    const fileName = `daily-checker-${report.date}.json`;
    const filePath = path.join(this.progressDir, fileName);
    writeJSONFile(filePath, report);
    return filePath;
  }

  generateSummary(report: DailyCheckReport): string {
    const lines: string[] = [];
    lines.push(`=== Daily Check Report: ${report.date} ===`);
    lines.push(`Generated at: ${report.generatedAt}`);
    lines.push('');
    lines.push(`Total sources: ${report.totalSources}`);
    lines.push(`  - Successful: ${report.successfulSources}`);
    lines.push(`  - Failed: ${report.failedSources}`);
    lines.push(`Total articles fetched: ${report.totalFetchedArticles}`);
    lines.push('');
    lines.push('Source breakdown:');

    for (const source of report.sources) {
      const status = source.fetchSuccess ? '✓' : '✗';
      lines.push(`  ${status} ${source.sourceName} (${source.sourceType}): ${source.fetchedArticles} articles`);
      if (!source.fetchSuccess && source.errorMessage) {
        lines.push(`      Error: ${source.errorMessage}`);
      }
    }

    if (report.warnings.length > 0) {
      lines.push('');
      lines.push('Warnings:');
      for (const warning of report.warnings) {
        lines.push(`  ⚠️  ${warning}`);
      }
    }

    return lines.join('\n');
  }
}
