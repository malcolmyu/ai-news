import { createHash } from 'crypto';
import { Article, SourceConfig } from '../../types/index.js';
import { writeJSONFile, ensureDir, formatDate, readJSONFile } from '../../utils/config.js';
import * as path from 'path';

/** 文件名前缀，避免与 daily 目录下其它文件混淆。 */
export const SOURCE_PROGRESS_FILE_PREFIX = 'src-';

export function makeSourceSlug(source: { name: string; url: string }): string {
  const hash = createHash('sha256').update(`${source.name}\n${source.url}`).digest('hex').slice(0, 16);
  const ascii = source.name
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
    .slice(0, 48);
  const prefix = ascii || 'source';
  return `${prefix}-${hash}`;
}

/** 用于合并 progress：同一篇文不同 query/hash 视为同一链接 */
export function normalizeArticleLink(link: string): string {
  try {
    const u = new URL(link);
    u.hash = '';
    let p = u.pathname;
    if (p.length > 1 && p.endsWith('/')) {
      p = p.slice(0, -1);
    }
    u.pathname = p;
    return u.href.toLowerCase();
  } catch {
    return link.trim().toLowerCase();
  }
}

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

/** 每源一个文件：聚合观测到的全部文章（按 link 去重） */
export interface SourceProgressArticle {
  title: string;
  link: string;
  publishedDate: string | null;
  /** 最近一次在本次日报流程中抓取到该条时的报告日期 */
  reportDate: string;
  category?: string;
  categories?: string[];
  hasSummary: boolean;
  summaryLength: number;
}

export interface SourceProgressFile {
  _schema: 'ai-news-source-progress/v2';
  sourceName: string;
  sourceUrl: string;
  sourceType: 'rss' | 'html';
  updatedAt: string;
  articles: SourceProgressArticle[];
}

/** v1 遗留（仅用于迁移） */
interface SourceRunEntry {
  reportDate: string;
  articles: SourceCheckResult['articles'];
}

function migrateFileToArticles(raw: unknown): SourceProgressArticle[] {
  if (!raw || typeof raw !== 'object') return [];
  const o = raw as Record<string, unknown>;
  const schema = o._schema as string | undefined;

  if (schema === 'ai-news-source-progress/v2' && Array.isArray(o.articles)) {
    return (o.articles as SourceProgressArticle[]).map(a => ({ ...a }));
  }

  if (schema === 'ai-news-source-progress/v1' && Array.isArray(o.runs)) {
    const map = new Map<string, SourceProgressArticle>();
    const runs = [...(o.runs as SourceRunEntry[])].sort((a, b) =>
      a.reportDate.localeCompare(b.reportDate)
    );
    for (const run of runs) {
      if (!run.articles) continue;
      for (const a of run.articles) {
        const key = normalizeArticleLink(a.link);
        map.set(key, {
          title: a.title,
          link: a.link,
          publishedDate: a.publishedDate,
          reportDate: run.reportDate,
          category: a.category,
          categories: a.categories,
          hasSummary: a.hasSummary,
          summaryLength: a.summaryLength,
        });
      }
    }
    return Array.from(map.values());
  }

  return [];
}

export class DailyChecker {
  private progressDir: string;

  constructor(progressDirOverride?: string) {
    this.progressDir = progressDirOverride ?? path.join(process.cwd(), '.agent', 'progress', 'daily');
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

  /**
   * 将当次运行中各源抓取到的文章合并进 `.agent/progress/daily/src-<slug>.json`（按 link 聚合，无 runs）。
   */
  persistSourceProgress(report: DailyCheckReport): string[] {
    const written: string[] = [];
    const now = new Date().toISOString();

    for (const src of report.sources) {
      const slug = makeSourceSlug({ name: src.sourceName, url: src.sourceUrl });
      const fileName = `${SOURCE_PROGRESS_FILE_PREFIX}${slug}.json`;
      const filePath = path.join(this.progressDir, fileName);

      const existingRaw = readJSONFile(filePath);
      const prior = migrateFileToArticles(existingRaw);
      const byKey = new Map<string, SourceProgressArticle>();

      for (const a of prior) {
        byKey.set(normalizeArticleLink(a.link), { ...a });
      }

      for (const a of src.articles) {
        const key = normalizeArticleLink(a.link);
        const prev = byKey.get(key);
        byKey.set(key, {
          title: a.title,
          link: a.link,
          publishedDate: a.publishedDate ?? prev?.publishedDate ?? null,
          reportDate: report.date,
          category: a.category ?? prev?.category,
          categories: a.categories ?? prev?.categories,
          hasSummary: a.hasSummary,
          summaryLength: a.summaryLength,
        });
      }

      const articles = Array.from(byKey.values()).sort((x, y) =>
        normalizeArticleLink(x.link).localeCompare(normalizeArticleLink(y.link))
      );

      const fileDoc: SourceProgressFile = {
        _schema: 'ai-news-source-progress/v2',
        sourceName: src.sourceName,
        sourceUrl: src.sourceUrl,
        sourceType: src.sourceType,
        updatedAt: now,
        articles,
      };

      writeJSONFile(filePath, fileDoc);
      written.push(filePath);
    }

    return written;
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
