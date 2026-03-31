import * as fs from 'fs';
import * as path from 'path';
import { ThinkingCategory } from '../../types/index.js';
import { renderPage } from '../../renderer/index.js';
import { ThinkingPage } from './ThinkingPage.js';

export class ThinkingGenerator {
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

  generateThinkingPage(category: ThinkingCategory, allCategories: ThinkingCategory[]): string {
    const thinkingDir = this.ensureDir('thinking');
    const outputFile = path.join(thinkingDir, `${category.slug}.html`);
    const html = '<!DOCTYPE html>' + renderPage(ThinkingPage, { category, allCategories });
    fs.writeFileSync(outputFile, html, 'utf8');
    console.log(`Thinking page generated: ${outputFile}`);
    return outputFile;
  }
}
