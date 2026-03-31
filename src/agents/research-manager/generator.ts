import * as fs from 'fs';
import * as path from 'path';
import { ResearchEntry } from '../../types/index.js';
import { renderPage } from '../../renderer/index.js';
import { ResearchArchivePage } from './ResearchArchivePage.js';

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
    const html = '<!DOCTYPE html>' + renderPage(ResearchArchivePage, { entries });
    fs.writeFileSync(outputFile, html, 'utf8');
    console.log(`Research archive generated: ${outputFile}`);
    return outputFile;
  }
}
