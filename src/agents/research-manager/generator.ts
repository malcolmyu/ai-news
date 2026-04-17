import * as fs from 'fs';
import * as path from 'path';
import { marked } from 'marked';
import { ResearchEntry, ResearchMetadata } from '../../types/index.js';
import { renderPage } from '../../renderer/index.js';
import { ResearchArchivePage } from './ResearchArchivePage.js';
import { ResearchReportPage } from './ResearchReportPage.js';

export class ResearchGenerator {
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

  generateResearchArchive(entries: ResearchEntry[]): string {
    const researchDir = this.ensureDir('research');
    const outputFile = path.join(researchDir, 'archive.html');
    const html = '<!DOCTYPE html>\n' + renderPage(ResearchArchivePage, { entries });
    fs.writeFileSync(outputFile, html, 'utf8');
    console.log(`Research archive generated: ${outputFile}`);
    return outputFile;
  }

  async generateReportPage(metadata: ResearchMetadata, markdownContent: string): Promise<string> {
    const researchDir = this.ensureDir('research');
    
    // Change extension from .md to .html
    const htmlFileName = metadata.file.replace(/\.md$/, '.html');
    const outputFile = path.join(researchDir, htmlFileName);
    
    const contentHtml = await marked.parse(markdownContent);
    const date = metadata.addedDate ? new Date(metadata.addedDate).toLocaleDateString('zh-CN') : new Date().toLocaleDateString('zh-CN');
    
    const html = '<!DOCTYPE html>\n' + renderPage(ResearchReportPage, { 
      title: metadata.title,
      date,
      category: metadata.category,
      contentHtml
    });
    
    fs.writeFileSync(outputFile, html, 'utf8');
    return outputFile;
  }
}
