import * as fs from 'fs';
import * as path from 'path';
import { HomepageData } from '../../types/index.js';
import { renderPage } from '../../renderer/index.js';
import { HomepagePage } from './HomepagePage.js';

export class HomepageGenerator {
  private docsDir: string;

  constructor() {
    this.docsDir = path.join(process.cwd(), 'docs');
  }

  generateHomepage(data: HomepageData): string {
    if (!fs.existsSync(this.docsDir)) {
      fs.mkdirSync(this.docsDir, { recursive: true });
    }
    const outputFile = path.join(this.docsDir, 'index.html');
    const html = '<!DOCTYPE html>' + renderPage(HomepagePage, { data });
    fs.writeFileSync(outputFile, html, 'utf8');
    console.log(`Homepage generated: ${outputFile}`);
    return outputFile;
  }
}
