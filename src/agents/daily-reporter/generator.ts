import * as fs from 'fs';
import * as path from 'path';
import { DailyReport, SummarizedArticle, ArchiveEntry } from '../../types/index.js';
import { formatDate } from '../../utils/config.js';
import { renderPage } from '../../renderer/index.js';
import { DailyReportPage } from './DailyReportPage.js';
import { DailyArchivePage } from './DailyArchivePage.js';

export class DailyReportGenerator {
  private docsDir: string;

  constructor() {
    this.docsDir = path.join(process.cwd(), 'docs');
  }

  private ensureDir(subdir: string): string {
    const dir = path.join(this.docsDir, subdir);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    return dir;
  }

  generateDailyReport(report: DailyReport, outputPath?: string): string {
    const dateStr = formatDate(new Date(report.date));
    const fileName = `ai-news-${dateStr}.html`;
    const dailyDir = this.ensureDir('daily');
    const outputFile = outputPath || path.join(dailyDir, fileName);

    const html = this.buildDailyReportHTML(report);
    fs.writeFileSync(outputFile, html, 'utf8');
    console.log(`Daily report generated: ${outputFile}`);

    fs.copyFileSync(outputFile, path.join(dailyDir, 'ai-daily-latest.html'));
    return outputFile;
  }

  private buildDailyReportHTML(report: DailyReport): string {
    const dateStr = formatDate(new Date(report.date));
    const categorized = this.categorizeArticles(report.articles);
    return '<!DOCTYPE html>' + renderPage(DailyReportPage, { report, categorized, dateStr });
  }

  private categorizeArticles(articles: SummarizedArticle[]): Record<string, SummarizedArticle[]> {
    const categories: Record<string, SummarizedArticle[]> = {};
    for (const article of articles) {
      const cat = article.category || '综合资讯';
      if (!categories[cat]) categories[cat] = [];
      categories[cat].push(article);
    }
    for (const items of Object.values(categories)) {
      items.sort((a, b) => {
        const da = a.published ? new Date(a.published).getTime() : 0;
        const db = b.published ? new Date(b.published).getTime() : 0;
        return db - da || (b.summaryQuality || 0) - (a.summaryQuality || 0);
      });
    }
    return categories;
  }

  generateDailyArchive(archives: ArchiveEntry[]): string {
    const dailyDir = this.ensureDir('daily');
    const outputFile = path.join(dailyDir, 'archive.html');
    const html = '<!DOCTYPE html>' + renderPage(DailyArchivePage, { archives });
    fs.writeFileSync(outputFile, html, 'utf8');
    console.log(`Daily archive generated: ${outputFile}`);
    return outputFile;
  }
}
