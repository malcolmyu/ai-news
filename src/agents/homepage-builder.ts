import * as fs from 'fs';
import * as path from 'path';
import { ReportGenerator } from '../generator.js';
import { readJSONFile, Logger } from '../utils/config.js';
import { AgentResult, HomepageData, ResearchEntry } from '../types/index.js';

export class HomepageBuilder {
  private logger: Logger;
  private generator: ReportGenerator;
  private docsDir: string;
  private dataDir: string;

  constructor() {
    this.logger = new Logger('HomepageBuilder');
    this.generator = new ReportGenerator();
    this.docsDir = path.join(process.cwd(), 'docs');
    this.dataDir = path.join(process.cwd(), 'data');
  }

  async buildHomepage(options?: { optimize?: boolean }): Promise<AgentResult> {
    try {
      this.logger.log('Building homepage...');

      const data = this.collectHomepageData();
      this.generator.generateHomepage(data);

      this.logger.log('Homepage built successfully');
      return {
        success: true,
        message: 'Homepage built successfully',
        data: { stats: data.stats },
      };
    } catch (error) {
      const msg = error instanceof Error ? error.message : 'Unknown error';
      this.logger.error('Failed to build homepage:', error instanceof Error ? error : new Error(msg));
      return { success: false, message: `Failed to build homepage: ${msg}` };
    }
  }

  private collectHomepageData(): HomepageData {
    const dailyData = this.collectDailyData();
    const researchData = this.collectResearchData();
    const thinkingData = this.collectThinkingData();

    return {
      latestDaily: dailyData.latest,
      dailyArchiveCount: dailyData.count,
      latestResearch: researchData.length > 0 ? researchData[0] : null,
      researchList: researchData,
      thinkingCategories: thinkingData,
      stats: {
        totalArticles: dailyData.totalArticles,
        totalReports: researchData.length,
        totalModels: thinkingData.reduce((sum, c) => sum + c.modelCount, 0),
        lastUpdated: new Date().toISOString(),
      },
    };
  }

  private collectDailyData(): { latest: HomepageData['latestDaily']; count: number; totalArticles: number } {
    const dailyDir = path.join(this.docsDir, 'daily');
    if (!fs.existsSync(dailyDir)) {
      return { latest: null, count: 0, totalArticles: 0 };
    }

    const files = fs.readdirSync(dailyDir)
      .filter(f => f.match(/^ai-news-\d{4}-\d{2}-\d{2}\.html$/))
      .sort()
      .reverse();

    // Count total articles from archive data
    const archivePath = path.join(this.dataDir, 'daily', 'archives.json');
    const archiveData = fs.existsSync(archivePath) ? readJSONFile(archivePath) : null;
    let totalArticles = 0;
    if (archiveData?.reports) {
      for (const report of Object.values(archiveData.reports) as any[]) {
        totalArticles += report.stats?.totalArticles || 0;
      }
    }

    if (files.length === 0) {
      return { latest: null, count: 0, totalArticles };
    }

    // Extract date from latest filename
    const latestFile = files[0];
    const match = latestFile.match(/ai-news-(\d{4}-\d{2}-\d{2})\.html/);
    const date = match ? match[1] : '';

    return {
      latest: {
        date,
        file: `daily/${latestFile}`,
        articleCount: totalArticles > 0 ? totalArticles : files.length,
      },
      count: files.length,
      totalArticles,
    };
  }

  private collectResearchData(): ResearchEntry[] {
    const indexPath = path.join(this.dataDir, 'research', 'index.json');
    if (!fs.existsSync(indexPath)) return [];

    const index = readJSONFile(indexPath) || { reports: {} };
    return Object.values(index.reports)
      .map((r: any) => ({
        title: r.title,
        date: r.addedDate ? new Date(r.addedDate).toLocaleDateString('zh-CN') : '',
        file: r.file,
        summary: r.summary || '',
        icon: '📊',
        category: r.category || '调研',
      }))
      .sort((a: any, b: any) => new Date(b.date).getTime() - new Date(a.date).getTime()) as ResearchEntry[];
  }

  private collectThinkingData(): Array<{ name: string; icon: string; file: string; description: string; modelCount: number }> {
    const seedPath = path.join(this.dataDir, 'thinking', 'seed-data.json');
    if (!fs.existsSync(seedPath)) {
      return [];
    }

    const seedData = readJSONFile(seedPath);
    if (!seedData?.categories) return [];

    return seedData.categories.map((c: any) => ({
      name: c.name,
      icon: c.icon,
      file: `${c.slug}.html`,
      description: c.description,
      modelCount: c.models?.length || 0,
    }));
  }

  async getStats(): Promise<AgentResult> {
    try {
      const data = this.collectHomepageData();
      return { success: true, data: data.stats };
    } catch (error) {
      const msg = error instanceof Error ? error.message : 'Unknown error';
      return { success: false, message: `Failed to get stats: ${msg}` };
    }
  }
}