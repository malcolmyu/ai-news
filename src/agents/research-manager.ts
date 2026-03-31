import * as fs from 'fs';
import * as path from 'path';
import { JSDOM } from 'jsdom';
import { ResearchMetadata, AgentResult, ResearchEntry } from '../types/index.js';
import { readJSONFile, writeJSONFile, Logger } from '../utils/config.js';
import { ReportGenerator } from '../generator.js';
import { HomepageBuilder } from './homepage-builder.js';
import { HarnessController } from '../harness/controller.js';

export class ResearchManager {
  private logger: Logger;
  private dataDir: string;

  constructor() {
    this.logger = new Logger('ResearchManager');
    this.dataDir = path.join(process.cwd(), 'data', 'research');
    this.ensureDataDir();
  }

  private ensureDataDir(): void {
    if (!fs.existsSync(this.dataDir)) {
      fs.mkdirSync(this.dataDir, { recursive: true });
    }
  }

  async addReport(filePath: string, category: string, options?: {
    tags?: string[];
    title?: string;
  }): Promise<AgentResult> {
    try {
      if (!fs.existsSync(filePath)) {
        return {
          success: false,
          message: `File not found: ${filePath}`,
        };
      }

      const fileName = path.basename(filePath);
      const fileContent = fs.readFileSync(filePath, 'utf8');

      // Validate report content via Harness
      const harness = HarnessController.getInstance();
      await harness.initialize();
      const validation = harness.validateResearchReport(fileContent);
      if (!validation.valid) {
        return {
          success: false,
          message: `Harness validation failed: ${validation.errors.join(', ')}`,
        };
      }

      // Extract metadata
      const metadata = await this.extractMetadata(fileContent, fileName, category, options);
      if (!metadata) {
        return {
          success: false,
          message: 'Failed to extract metadata from report',
        };
      }

      // Create category directory if needed
      const categoryDir = path.join(this.dataDir, 'categories', category);
      if (!fs.existsSync(categoryDir)) {
        fs.mkdirSync(categoryDir, { recursive: true });
      }

      // Copy file to data directory
      const destPath = path.join(categoryDir, fileName);
      fs.copyFileSync(filePath, destPath);

      // Update index
      const indexPath = path.join(this.dataDir, 'index.json');
      const index = this.loadIndex(indexPath);

      index.reports[metadata.id] = metadata;
      this.saveIndex(indexPath, index);

      // Copy file to docs/research/ for GitHub Pages
      const docsResearchDir = path.join(process.cwd(), 'docs', 'research');
      if (!fs.existsSync(docsResearchDir)) {
        fs.mkdirSync(docsResearchDir, { recursive: true });
      }
      fs.copyFileSync(filePath, path.join(docsResearchDir, fileName));

      // Generate archive page
      this.logger.log('Generating research archive page...');
      const generator = new ReportGenerator();
      generator.generateResearchArchive(this.buildArchiveEntries(index.reports));

      // Rebuild homepage
      this.logger.log('Rebuilding homepage...');
      const hpBuilder = new HomepageBuilder();
      await hpBuilder.buildHomepage();

      this.logger.log(`Report added: ${metadata.title} (${category})`);

      return {
        success: true,
        message: `Report added successfully: ${metadata.title}`,
        data: metadata,
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      this.logger.error(`Failed to add report: ${filePath}`, error instanceof Error ? error : new Error(errorMessage));

      return {
        success: false,
        message: `Failed to add report: ${errorMessage}`,
      };
    }
  }

  private buildArchiveEntries(reports: Record<string, ResearchMetadata>): ResearchEntry[] {
    return Object.values(reports)
      .map(r => ({
        title: r.title,
        date: r.addedDate ? new Date(r.addedDate).toLocaleDateString('zh-CN') : '',
        file: r.file,
        summary: r.summary || '',
        category: r.category || '调研',
        icon: '📊'
      }))
      .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
  }

  private async extractMetadata(
    content: string,
    fileName: string,
    category: string,
    options?: { tags?: string[]; title?: string }
  ): Promise<ResearchMetadata | null> {
    try {
      const dom = new JSDOM(content);
      const document = dom.window.document;
      const title = options?.title || document.querySelector('title')?.textContent || document.querySelector('h1')?.textContent || path.parse(fileName).name;
      const textContent = document.body?.textContent || content.replace(/<[^>]*>/g, '');
      const summary = this.generateSummary(textContent);

      const id = this.generateId(title, category);

      return {
        id,
        title: title.trim(),
        category,
        file: fileName,
        addedDate: new Date().toISOString(),
        summary,
        tags: options?.tags || [],
      };
    } catch (error) {
      this.logger.error('Failed to extract metadata:', error instanceof Error ? error : undefined);
      return null;
    }
  }

  private generateSummary(text: string, maxLength: number = 200): string {
    const cleanedText = text.replace(/\s+/g, ' ').trim();

    if (cleanedText.length <= maxLength) {
      return cleanedText;
    }

    const truncated = cleanedText.substring(0, maxLength);
    const lastSentenceEnd = Math.max(
      truncated.lastIndexOf('.'),
      truncated.lastIndexOf('!'),
      truncated.lastIndexOf('?')
    );

    if (lastSentenceEnd > maxLength * 0.7) {
      return truncated.substring(0, lastSentenceEnd + 1);
    }

    return truncated + '...';
  }

  private generateId(title: string, category: string): string {
    const normalizedTitle = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
    const timestamp = Date.now().toString(36);
    return `${category}-${normalizedTitle}-${timestamp}`;
  }

  private loadIndex(indexPath: string): any {
    if (!fs.existsSync(indexPath)) {
      return { reports: {} };
    }
    return readJSONFile(indexPath) || { reports: {} };
  }

  private saveIndex(indexPath: string, index: any): void {
    writeJSONFile(indexPath, index);
  }

  async getStats(category?: string): Promise<AgentResult> {
    try {
      const indexPath = path.join(this.dataDir, 'index.json');
      const index = this.loadIndex(indexPath);

      const reports = Object.values(index.reports) as ResearchMetadata[];
      let filteredReports = reports;

      if (category) {
        filteredReports = reports.filter(report => report.category === category);
      }

      const categories: Record<string, number> = {};
      reports.forEach(report => {
        categories[report.category] = (categories[report.category] || 0) + 1;
      });

      const stats = {
        totalReports: filteredReports.length,
        categories: categories,
        byCategory: category
          ? filteredReports.length
          : undefined,
        recentReports: filteredReports
          .sort((a, b) => new Date(b.addedDate).getTime() - new Date(a.addedDate).getTime())
          .slice(0, 5),
      };

      return {
        success: true,
        data: stats,
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      this.logger.error('Failed to get stats:', error instanceof Error ? error : new Error(errorMessage));

      return {
        success: false,
        message: `Failed to get stats: ${errorMessage}`,
      };
    }
  }

  async listReports(category?: string): Promise<AgentResult> {
    try {
      const indexPath = path.join(this.dataDir, 'index.json');
      const index = this.loadIndex(indexPath);

      let reports = Object.values(index.reports) as ResearchMetadata[];

      if (category) {
        reports = reports.filter(report => report.category === category);
      }

      reports.sort((a, b) => new Date(b.addedDate).getTime() - new Date(a.addedDate).getTime());

      return {
        success: true,
        data: reports,
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      this.logger.error('Failed to list reports:', error instanceof Error ? error : new Error(errorMessage));

      return {
        success: false,
        message: `Failed to list reports: ${errorMessage}`,
      };
    }
  }

  async searchReports(query: string): Promise<AgentResult> {
    try {
      const indexPath = path.join(this.dataDir, 'index.json');
      const index = this.loadIndex(indexPath);

      const reports = Object.values(index.reports) as ResearchMetadata[];
      const lowerQuery = query.toLowerCase();

      const results = reports.filter(report =>
        report.title.toLowerCase().includes(lowerQuery) ||
        report.summary?.toLowerCase().includes(lowerQuery) ||
        report.tags.some(tag => tag.toLowerCase().includes(lowerQuery))
      );

      results.sort((a, b) => new Date(b.addedDate).getTime() - new Date(a.addedDate).getTime());

      return {
        success: true,
        data: results,
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      this.logger.error('Failed to search reports:', error instanceof Error ? error : new Error(errorMessage));

      return {
        success: false,
        message: `Failed to search reports: ${errorMessage}`,
      };
    }
  }
}