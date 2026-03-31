import * as fs from 'fs';
import * as path from 'path';
import { DailyReport, SummarizedArticle, ArchiveEntry, ResearchEntry, HomepageData, ThinkingCategory } from './types/index.js';
import { formatDate } from './utils/config.js';
import { htmlDoc, siteHeader, siteFooter, SHARED_CSS } from './shared-styles.js';

export class ReportGenerator {
  private docsDir: string;

  constructor() {
    this.docsDir = path.join(process.cwd(), 'docs');
  }

  // ─── Ensure subdirectory exists ─────────────────────────
  private ensureDir(subdir: string): string {
    const dir = path.join(this.docsDir, subdir);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    return dir;
  }

  // ═══════════════════════════════════════════════════════════
  //  DAILY REPORT
  // ═══════════════════════════════════════════════════════════

  generateDailyReport(report: DailyReport, outputPath?: string): string {
    const dateStr = formatDate(new Date(report.date));
    const fileName = `ai-news-${dateStr}.html`;
    const dailyDir = this.ensureDir('daily');
    const outputFile = outputPath || path.join(dailyDir, fileName);

    const html = this.buildDailyReportHTML(report);
    fs.writeFileSync(outputFile, html, 'utf8');
    console.log(`Daily report generated: ${outputFile}`);

    // Also copy as latest
    fs.copyFileSync(outputFile, path.join(dailyDir, 'ai-daily-latest.html'));

    return outputFile;
  }

  private buildDailyReportHTML(report: DailyReport): string {
    const dateStr = formatDate(new Date(report.date));
    const now = new Date();
    const updateTime = `${formatDate(now)} ${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
    const categorized = this.categorizeArticles(report.articles);
    const totalArticles = report.articles.length;

    const categoriesHTML = Object.entries(categorized)
      .filter(([, articles]) => articles.length > 0)
      .map(([category, articles]) => `
        <section class="section">
          <div class="section-header">
            <h2 class="section-title">${category}</h2>
            <span class="section-count">${articles.length} 条</span>
          </div>
          <div class="news-list">
            ${articles.map(a => this.buildArticleCard(a)).join('\n')}
          </div>
        </section>`).join('\n');

    const extraCSS = `
      .section { margin-bottom: 40px; }
      .section-header { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; padding-bottom: 12px; border-bottom: 2px solid var(--border); }
      .section-title { font-size: 20px; font-weight: 600; }
      .section-count { margin-left: auto; background: var(--bg-secondary); padding: 4px 12px; border-radius: 20px; font-size: 13px; color: var(--text-secondary); }
      .news-list { display: flex; flex-direction: column; gap: 16px; }
      .news-card { background: var(--bg-primary); border: 1px solid var(--border); border-radius: 12px; padding: 20px; box-shadow: var(--shadow); transition: all 0.2s ease; }
      .news-card:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); }
      .news-meta { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; font-size: 13px; color: var(--text-secondary); }
      .news-source { color: var(--accent); font-weight: 600; }
      .news-title { font-size: 17px; font-weight: 600; margin-bottom: 10px; color: var(--text-primary); line-height: 1.4; }
      .news-summary { font-size: 14px; color: var(--text-secondary); line-height: 1.7; margin-bottom: 14px; }
      .news-link { display: inline-flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 500; color: var(--accent); text-decoration: none; padding: 8px 16px; background: rgba(59,130,246,0.1); border-radius: 6px; transition: all 0.2s; }
      .news-link:hover { background: var(--accent); color: white; }
      .daily-header { background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%); color: white; padding: 48px 0; margin-top: 64px; }
      .daily-header h1 { font-size: 32px; font-weight: 700; margin-bottom: 8px; color: white; }
      .daily-header .subtitle { font-size: 14px; opacity: 0.8; }
      .stats-value { font-size: 36px; font-weight: 700; color: #60a5fa; }
      .stats-label { font-size: 12px; opacity: 0.7; }
      @media (max-width: 640px) {
        .header-content { flex-direction: column; gap: 16px; text-align: center; }
        h1 { font-size: 24px; } .news-card { padding: 16px; }
      }
      @media (prefers-color-scheme: dark) {
        :root { --bg-primary: #111827; --bg-secondary: #1f2937; --text-primary: #f9fafb; --text-secondary: #9ca3af; --border: #374151; }
        .daily-header { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); }
      }`;

    const body = `
    ${siteHeader('../index.html')}
    <div class="daily-header">
      <div class="container-sm">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <div>
            <h1>🤖 AI 日报</h1>
            <p class="subtitle">${dateStr}</p>
          </div>
          <div style="text-align:right;">
            <div class="stats-value">${totalArticles}</div>
            <div class="stats-label">条资讯</div>
          </div>
        </div>
      </div>
    </div>
    <main class="container-sm" style="padding-top: 32px;">
      ${categoriesHTML}
    </main>
    ${siteFooter('../index.html')}`;

    return htmlDoc(`AI 日报 - ${dateStr}`, extraCSS, body);
  }

  private buildArticleCard(article: SummarizedArticle): string {
    const dateDisplay = article.published ? formatDate(new Date(article.published)) : '近期';
    return `<article class="news-card">
      <div class="news-meta">
        <span class="news-source">${article.source || ''}</span>
        <span>·</span>
        <span>${dateDisplay}</span>
      </div>
      <h3 class="news-title">${article.title}</h3>
      <p class="news-summary">${article.summary || ''}</p>
      <a href="${article.link}" class="news-link" target="_blank" rel="noopener noreferrer">阅读原文 →</a>
    </article>`;
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

  // ═══════════════════════════════════════════════════════════
  //  DAILY ARCHIVE
  // ═══════════════════════════════════════════════════════════

  generateDailyArchive(archives: ArchiveEntry[]): string {
    const dailyDir = this.ensureDir('daily');
    const outputFile = path.join(dailyDir, 'archive.html');

    const itemsHTML = archives.map((item, i) => `
      <a href="${item.file}" class="archive-item${i === 0 ? ' latest' : ''}">
        <div class="archive-icon">📰</div>
        <div class="archive-content">
          <div class="archive-date">${item.dateDisplay}${i === 0 ? ' <span class="badge-latest">最新</span>' : ''}</div>
          <div class="archive-meta">${item.articles} 篇文章 · AI 日报</div>
        </div>
        <div class="archive-arrow">→</div>
      </a>`).join('\n');

    const extraCSS = `
      .archive-header { background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%); color: white; padding: 48px 0; margin-top: 64px; }
      .archive-header h1 { font-size: 28px; font-weight: 700; color: white; }
      .archive-header .subtitle { font-size: 14px; opacity: 0.8; margin-top: 4px; }
      .stats-value { font-size: 36px; font-weight: 700; color: #60a5fa; }
      .stats-label { font-size: 12px; opacity: 0.7; }
      .archive-list { display: flex; flex-direction: column; gap: 16px; padding: 32px 0; }
      .archive-item { display: flex; align-items: center; gap: 16px; padding: 20px; background: var(--bg-primary); border: 1px solid var(--border); border-radius: 12px; text-decoration: none; color: inherit; transition: all 0.2s; box-shadow: var(--shadow); }
      .archive-item:hover { border-color: var(--accent); box-shadow: var(--shadow-md); transform: translateY(-2px); }
      .archive-item.latest { background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%); border-color: var(--accent); }
      .archive-icon { width: 48px; height: 48px; background: var(--bg-secondary); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 24px; flex-shrink: 0; }
      .archive-item.latest .archive-icon { background: var(--accent); }
      .archive-content { flex: 1; }
      .archive-date { font-size: 16px; font-weight: 600; margin-bottom: 4px; display: flex; align-items: center; gap: 8px; }
      .badge-latest { padding: 2px 8px; background: #dcfce7; color: #166534; border-radius: 100px; font-size: 11px; font-weight: 600; }
      .archive-meta { font-size: 13px; color: var(--text-secondary); }
      .archive-arrow { font-size: 20px; color: var(--text-muted); transition: all 0.2s; }
      .archive-item:hover .archive-arrow { color: var(--accent); transform: translateX(4px); }
      @media (max-width: 640px) { .archive-item { padding: 16px; } .archive-icon { width: 40px; height: 40px; font-size: 20px; } }`;

    const body = `
    ${siteHeader('../index.html')}
    <div class="archive-header">
      <div class="container-sm">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px;">
          <div>
            <h1>📚 历史日报归档</h1>
            <div class="subtitle">AI Daily News Archive</div>
          </div>
          <div style="text-align:right;">
            <div class="stats-value">${archives.length}</div>
            <div class="stats-label">历史日报</div>
          </div>
        </div>
      </div>
    </div>
    <main class="container-sm">
      <div class="archive-list">${itemsHTML}</div>
    </main>
    ${siteFooter('../index.html')}`;

    const html = htmlDoc('历史日报归档', extraCSS, body);
    fs.writeFileSync(outputFile, html, 'utf8');
    console.log(`Daily archive generated: ${outputFile}`);
    return outputFile;
  }

  // ═══════════════════════════════════════════════════════════
  //  RESEARCH ARCHIVE
  // ═══════════════════════════════════════════════════════════

  generateResearchArchive(entries: ResearchEntry[]): string {
    const researchDir = this.ensureDir('research');
    const outputFile = path.join(researchDir, 'archive.html');
    const latest = entries[0] || null;

    const featuredHTML = latest ? `
      <div class="section-label">Featured</div>
      <a href="${latest.file}" class="featured-card">
        <div class="featured-content">
          <div class="featured-meta">
            <span class="featured-badge">最新</span>
            <span>${latest.date}</span>
          </div>
          <h3 class="featured-title">${latest.title}</h3>
          <p class="featured-desc">${latest.summary}</p>
        </div>
        <div class="featured-arrow">→</div>
      </a>` : '';

    const listHTML = entries.map(e => `
      <a href="${e.file}" class="archive-item">
        <div class="archive-icon">${e.icon}</div>
        <div class="archive-content">
          <div style="font-size:13px;color:var(--text-muted);margin-bottom:4px;">${e.date}</div>
          <div style="font-size:16px;font-weight:600;margin-bottom:4px;">${e.title}</div>
          <div style="font-size:13px;color:var(--text-secondary);">${e.category}</div>
        </div>
        <div class="archive-arrow">→</div>
      </a>`).join('\n');

    const extraCSS = `
      .rch-header { background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%); color: white; padding: 48px 0; margin-top: 64px; }
      .rch-header h1 { font-size: 28px; font-weight: 700; color: white; }
      .rch-header .subtitle { font-size: 14px; opacity: 0.8; margin-top: 4px; }
      .section-label { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; color: var(--accent); margin-bottom: 16px; margin-top: 32px; }
      .featured-card { background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%); border: 1px solid var(--border); border-radius: 16px; padding: 28px; display: grid; grid-template-columns: 1fr auto; gap: 24px; align-items: center; transition: all 0.3s; text-decoration: none; color: inherit; }
      .featured-card:hover { border-color: var(--accent-light); box-shadow: var(--shadow-lg); transform: translateY(-2px); }
      .featured-content { display: flex; flex-direction: column; gap: 10px; }
      .featured-meta { display: flex; align-items: center; gap: 10px; font-size: 13px; color: var(--text-muted); }
      .featured-badge { padding: 3px 10px; background: var(--accent); color: white; border-radius: 100px; font-size: 11px; font-weight: 600; }
      .featured-title { font-size: 20px; font-weight: 600; }
      .featured-desc { font-size: 14px; color: var(--text-secondary); line-height: 1.6; }
      .featured-arrow { width: 44px; height: 44px; background: white; border: 1px solid var(--border); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; color: var(--accent); transition: all 0.2s; }
      .featured-card:hover .featured-arrow { background: var(--accent); color: white; }
      .archive-list { display: flex; flex-direction: column; gap: 16px; margin-top: 16px; margin-bottom: 40px; }
      .archive-item { display: flex; align-items: center; gap: 16px; padding: 20px; background: var(--bg-primary); border: 1px solid var(--border); border-radius: 12px; text-decoration: none; color: inherit; transition: all 0.2s; box-shadow: var(--shadow); }
      .archive-item:hover { border-color: var(--accent); box-shadow: var(--shadow-md); transform: translateY(-2px); }
      .archive-icon { width: 48px; height: 48px; background: var(--bg-secondary); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 24px; flex-shrink: 0; }
      .archive-arrow { font-size: 20px; color: var(--text-muted); transition: all 0.2s; }
      .archive-item:hover .archive-arrow { color: var(--accent); transform: translateX(4px); }
      .stats-value { font-size: 36px; font-weight: 700; color: #60a5fa; }
      .stats-label { font-size: 12px; opacity: 0.7; }`;

    const body = `
    ${siteHeader('../index.html')}
    <div class="rch-header">
      <div class="container-sm">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px;">
          <div>
            <h1>📊 调研报告归档</h1>
            <div class="subtitle">Research Reports Archive</div>
          </div>
          <div style="text-align:right;">
            <div class="stats-value">${entries.length}</div>
            <div class="stats-label">调研报告</div>
          </div>
        </div>
      </div>
    </div>
    <main class="container-sm">
      ${featuredHTML}
      <div class="section-label">History</div>
      <div class="archive-list">${listHTML}</div>
    </main>
    ${siteFooter('../index.html')}`;

    const html = htmlDoc('调研报告归档', extraCSS, body);
    fs.writeFileSync(outputFile, html, 'utf8');
    console.log(`Research archive generated: ${outputFile}`);
    return outputFile;
  }

  // ═══════════════════════════════════════════════════════════
  //  THINKING MODEL PAGES
  // ═══════════════════════════════════════════════════════════

  generateThinkingPage(category: ThinkingCategory, allCategories: ThinkingCategory[]): string {
    const thinkingDir = this.ensureDir('thinking');
    const outputFile = path.join(thinkingDir, `${category.slug}.html`);

    const navHTML = allCategories.map(c =>
      `<a href="${c.slug}.html" class="nav-cat${c.slug === category.slug ? ' active' : ''}">${c.icon} ${c.name}</a>`
    ).join('\n');

    const coreModels = category.models.filter((_, i) => i < 5);
    const otherModels = category.models.filter((_, i) => i >= 5);

    const coreHTML = coreModels.map(m => `
      <div class="model-card">
        <div class="model-header">
          <div style="display:flex;align-items:center;gap:12px;">
            <span style="font-size:28px;">${m.icon}</span>
            <div>
              <div class="model-title">${m.title}</div>
              <div style="font-size:12px;color:var(--text-muted);margin-top:4px;">${m.source}</div>
            </div>
          </div>
          <div style="display:flex;gap:6px;flex-wrap:wrap;">
            ${m.tags.map(t => `<span class="model-tag">${t}</span>`).join('')}
          </div>
        </div>
        <div class="model-section">
          <div class="model-section-title">定义</div>
          <div class="model-def">${m.definition}</div>
        </div>
        <div class="model-section">
          <div class="model-section-title">核心洞察</div>
          <ul class="insights-list">
            ${m.insights.map(i => `<li>${i}</li>`).join('')}
          </ul>
        </div>
        ${m.connections.length > 0 ? `<div class="model-section">
          <div class="model-section-title">关联模型</div>
          <div style="display:flex;flex-wrap:wrap;gap:8px;">
            ${m.connections.map(c => `<span class="connection">${c}</span>`).join('')}
          </div>
        </div>` : ''}
      </div>`).join('\n');

    const otherHTML = otherModels.length > 0 ? `
      <section class="section" style="background:var(--bg-secondary);padding:48px 0;">
        <div class="container-thinking">
          <div style="display:flex;align-items:center;gap:12px;margin-bottom:32px;">
            <span style="font-family:'JetBrains Mono',monospace;font-size:13px;color:var(--accent);font-weight:600;">02</span>
            <h2 style="font-size:22px;font-weight:700;">更多${category.name}模型</h2>
          </div>
          <ul class="simple-list">
            ${otherModels.map(m => `<li><strong>${m.title}</strong> — ${m.definition}</li>`).join('')}
          </ul>
        </div>
      </section>` : '';

    const extraCSS = `
      .container-thinking { max-width: 900px; margin: 0 auto; padding: 0 24px; }
      .hero-thinking { padding: 120px 0 40px; text-align: center; border-bottom: 1px solid var(--border); }
      .nav-cats { display: flex; justify-content: center; gap: 8px; padding: 24px 0; border-bottom: 1px solid var(--border); flex-wrap: wrap; }
      .nav-cat { padding: 8px 16px; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 100px; font-size: 13px; color: var(--text-secondary); text-decoration: none; font-weight: 500; transition: all 0.2s; }
      .nav-cat:hover, .nav-cat.active { background: var(--accent); border-color: var(--accent); color: white; }
      .section { padding: 48px 0; border-bottom: 1px solid var(--border); }
      .model-card { background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 12px; padding: 28px; margin-bottom: 20px; transition: all 0.2s; }
      .model-card:hover { border-color: var(--accent-light); box-shadow: var(--shadow-md); }
      .model-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
      .model-title { font-size: 20px; font-weight: 700; }
      .model-tag { padding: 4px 10px; background: var(--bg-tertiary); border-radius: 100px; font-size: 11px; color: var(--text-secondary); font-weight: 500; }
      .model-section { margin-bottom: 20px; }
      .model-section:last-child { margin-bottom: 0; }
      .model-section-title { font-size: 13px; font-weight: 600; color: var(--accent); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 10px; }
      .model-def { background: var(--bg-primary); border: 1px solid var(--border); border-radius: 8px; padding: 16px; font-size: 15px; color: var(--text-secondary); line-height: 1.7; }
      .insights-list { list-style: none; }
      .insights-list li { background: var(--bg-primary); border: 1px solid var(--border); border-radius: 8px; padding: 14px 16px; margin-bottom: 10px; font-size: 14px; color: var(--text-secondary); border-left: 3px solid var(--accent); }
      .connection { padding: 6px 12px; background: #eff6ff; border-radius: 100px; font-size: 12px; color: var(--accent); font-weight: 500; }
      .simple-list { list-style: none; }
      .simple-list li { padding: 14px 0; border-bottom: 1px solid var(--border); font-size: 14px; color: var(--text-secondary); }
      .simple-list li:last-child { border-bottom: none; }
      .simple-list li strong { color: var(--text-primary); }
      @media (max-width: 768px) { .model-header { flex-direction: column; gap: 12px; } .nav-cat { padding: 6px 12px; font-size: 12px; } }`;

    const body = `
    ${siteHeader('../index.html')}
    <main>
      <section class="hero-thinking">
        <div class="container-thinking">
          <div style="font-size:48px;margin-bottom:16px;">${category.icon}</div>
          <h1 style="font-size:36px;font-weight:700;margin-bottom:12px;">${category.name}思维模型</h1>
          <p style="font-size:16px;color:var(--text-secondary);max-width:560px;margin:0 auto;">${category.description}</p>
          <div style="display:flex;justify-content:center;gap:40px;margin-top:32px;padding-top:32px;border-top:1px solid var(--border);">
            <div style="text-align:center;">
              <div style="font-size:28px;font-weight:700;color:var(--accent);">${category.models.length}</div>
              <div style="font-size:12px;color:var(--text-muted);margin-top:4px;">思维模型</div>
            </div>
          </div>
        </div>
      </section>
      <div class="nav-cats">${navHTML}</div>
      <section class="section">
        <div class="container-thinking">
          <div style="display:flex;align-items:center;gap:12px;margin-bottom:32px;">
            <span style="font-family:'JetBrains Mono',monospace;font-size:13px;color:var(--accent);font-weight:600;">01</span>
            <h2 style="font-size:22px;font-weight:700;">核心${category.name}模型</h2>
          </div>
          ${coreHTML}
        </div>
      </section>
      ${otherHTML}
    </main>
    ${siteFooter('../index.html')}`;

    const html = htmlDoc(`${category.name}思维模型`, extraCSS, body);
    fs.writeFileSync(outputFile, html, 'utf8');
    console.log(`Thinking page generated: ${outputFile}`);
    return outputFile;
  }

  // ═══════════════════════════════════════════════════════════
  //  HOMEPAGE
  // ═══════════════════════════════════════════════════════════

  generateHomepage(data: HomepageData): string {
    if (!fs.existsSync(this.docsDir)) {
      fs.mkdirSync(this.docsDir, { recursive: true });
    }
    const outputFile = path.join(this.docsDir, 'index.html');
    const html = this.buildHomepageHTML(data);
    fs.writeFileSync(outputFile, html, 'utf8');
    console.log(`Homepage generated: ${outputFile}`);
    return outputFile;
  }

  private buildHomepageHTML(data: HomepageData): string {
    // Daily section
    const dailySection = `
      <section class="section" id="daily">
        <div class="container">
          <div class="section-header-hp">
            <div>
              <div class="section-label">AI Insight</div>
              <h2 class="section-title-hp">每日 AI 日报</h2>
            </div>
            <a href="daily/archive.html" class="section-link">查看全部 →</a>
          </div>
          <div style="display:flex;flex-direction:column;gap:12px;">
            <a href="daily/ai-daily-latest.html" class="daily-entry latest-entry">
              <div class="entry-icon" style="background:var(--accent);">📰</div>
              <div style="flex:1;">
                <div style="font-weight:600;font-size:15px;margin-bottom:4px;">今日日报 <span class="badge-latest">最新</span></div>
                <div style="font-size:13px;color:var(--text-secondary);">实时更新 · ${data.latestDaily ? data.latestDaily.articleCount + ' 篇文章' : '暂无'}</div>
              </div>
              <div style="font-size:20px;color:var(--accent);">→</div>
            </a>
            <a href="daily/archive.html" class="daily-entry">
              <div class="entry-icon">📚</div>
              <div style="flex:1;">
                <div style="font-weight:600;font-size:14px;margin-bottom:2px;">历史日报</div>
                <div style="font-size:12px;color:var(--text-muted);">共 ${data.dailyArchiveCount} 期归档</div>
              </div>
              <div style="font-size:16px;color:var(--text-muted);">→</div>
            </a>
          </div>
        </div>
      </section>`;

    // Research section
    const latestResearch = data.latestResearch;
    const researchSection = `
      <section class="section" style="background:var(--bg-secondary);" id="research">
        <div class="container">
          <div class="section-header-hp">
            <div>
              <div class="section-label">Research</div>
              <h2 class="section-title-hp">深度调研报告</h2>
            </div>
            <a href="research/archive.html" class="section-link">查看全部 →</a>
          </div>
          ${latestResearch ? `<a href="research/${latestResearch.file}" class="featured-card">
            <div class="featured-content">
              <div class="featured-meta"><span class="featured-badge">精选</span><span>${latestResearch.date}</span></div>
              <h3 class="featured-title">${latestResearch.title}</h3>
              <p class="featured-desc">${latestResearch.summary}</p>
            </div>
            <div class="featured-arrow">→</div>
          </a>` : '<p style="color:var(--text-muted);text-align:center;padding:32px 0;">暂无调研报告</p>'}
          ${data.researchList.length > 1 ? `<div style="display:flex;flex-direction:column;gap:12px;margin-top:24px;">
            ${data.researchList.slice(1, 4).map(r => `
            <a href="research/${r.file}" class="daily-entry">
              <div class="entry-icon">${r.icon}</div>
              <div style="flex:1;">
                <div style="font-weight:600;font-size:14px;margin-bottom:2px;">${r.title}</div>
                <div style="font-size:12px;color:var(--text-muted);">${r.date} · ${r.category}</div>
              </div>
              <div style="font-size:16px;color:var(--text-muted);">→</div>
            </a>`).join('')}
          </div>` : ''}
        </div>
      </section>`;

    // Thinking section
    const thinkingSection = `
      <section class="section" id="knowledge">
        <div class="container">
          <div class="section-header-hp">
            <div>
              <div class="section-label">Knowledge Base</div>
              <h2 class="section-title-hp">知识武器库</h2>
            </div>
            <a href="thinking/decision.html" class="section-link">查看全部 →</a>
          </div>
          <div class="cards-grid">
            ${data.thinkingCategories.map(c => `
            <a href="thinking/${c.file}" class="card">
              <div class="card-header">
                <span class="card-category">${c.name}</span>
                <div class="card-icon">${c.icon}</div>
              </div>
              <h3 class="card-title">${c.name}思维模型</h3>
              <p class="card-desc">${c.description}</p>
              <div class="card-meta">${c.modelCount} 个模型</div>
            </a>`).join('')}
          </div>
        </div>
      </section>`;

    const extraCSS = `
      .hero { padding: 140px 0 80px; text-align: center; }
      .hero-badge { display: inline-flex; align-items: center; gap: 8px; padding: 8px 16px; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 100px; font-size: 13px; color: var(--text-secondary); font-weight: 500; margin-bottom: 24px; }
      .hero-badge::before { content: ''; width: 6px; height: 6px; background: #10b981; border-radius: 50%; animation: pulse 2s infinite; }
      @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
      .hero-title { font-size: clamp(40px, 6vw, 64px); font-weight: 700; line-height: 1.1; letter-spacing: -0.02em; margin-bottom: 20px; }
      .hero-title span { background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dark) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
      .hero-desc { font-size: 18px; color: var(--text-secondary); max-width: 560px; margin: 0 auto 40px; line-height: 1.7; }
      .hero-stats { display: flex; justify-content: center; gap: 48px; padding-top: 40px; border-top: 1px solid var(--border); }
      .hero-stat { text-align: center; }
      .hero-stat-value { font-size: 36px; font-weight: 700; line-height: 1; margin-bottom: 8px; }
      .hero-stat-label { font-size: 13px; color: var(--text-muted); font-weight: 500; }
      .section { padding: 80px 0; }
      .section-header-hp { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 40px; }
      .section-label { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; color: var(--accent); margin-bottom: 8px; }
      .section-title-hp { font-size: 28px; font-weight: 700; }
      .section-link { font-size: 14px; color: var(--accent); text-decoration: none; font-weight: 500; display: flex; align-items: center; gap: 4px; transition: gap 0.2s; }
      .section-link:hover { gap: 8px; }
      .daily-entry { display: flex; align-items: center; gap: 16px; padding: 16px 20px; background: var(--bg-primary); border: 1px solid var(--border); border-radius: 12px; text-decoration: none; color: inherit; transition: all 0.2s; }
      .daily-entry:hover { border-color: var(--accent-light); box-shadow: var(--shadow-md); }
      .daily-entry.latest-entry { background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%); padding: 20px; }
      .entry-icon { width: 44px; height: 44px; background: var(--bg-secondary); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0; }
      .badge-latest { padding: 2px 8px; background: #dcfce7; color: #166534; border-radius: 100px; font-size: 11px; font-weight: 600; margin-left: 8px; }
      .featured-card { background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%); border: 1px solid var(--border); border-radius: 16px; padding: 40px; display: grid; grid-template-columns: 1fr auto; gap: 40px; align-items: center; transition: all 0.3s; text-decoration: none; color: inherit; }
      .featured-card:hover { border-color: var(--accent-light); box-shadow: var(--shadow-lg); transform: translateY(-2px); }
      .featured-content { display: flex; flex-direction: column; gap: 12px; }
      .featured-meta { display: flex; align-items: center; gap: 12px; font-size: 13px; color: var(--text-muted); }
      .featured-badge { padding: 4px 10px; background: var(--accent); color: white; border-radius: 100px; font-size: 11px; font-weight: 600; }
      .featured-title { font-size: 24px; font-weight: 600; }
      .featured-desc { font-size: 15px; color: var(--text-secondary); line-height: 1.6; }
      .featured-arrow { width: 48px; height: 48px; background: white; border: 1px solid var(--border); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 20px; color: var(--accent); transition: all 0.2s; }
      .featured-card:hover .featured-arrow { background: var(--accent); color: white; border-color: var(--accent); }
      .cards-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; }
      .card { background: var(--bg-primary); border: 1px solid var(--border); border-radius: 12px; padding: 28px; text-decoration: none; color: inherit; transition: all 0.2s; }
      .card:hover { border-color: var(--accent-light); box-shadow: var(--shadow-md); }
      .card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
      .card-category { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--accent); }
      .card-icon { width: 40px; height: 40px; background: var(--bg-secondary); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
      .card-title { font-size: 18px; font-weight: 600; margin-bottom: 8px; }
      .card-desc { font-size: 14px; color: var(--text-secondary); line-height: 1.5; margin-bottom: 16px; }
      .card-meta { font-size: 13px; color: var(--text-muted); font-weight: 500; }
      .footer-text { font-size: 14px; color: var(--text-muted); }
      .footer-text strong { color: var(--text-primary); font-weight: 600; }
      @media (max-width: 768px) {
        .hero { padding: 120px 0 60px; }
        .hero-stats { flex-direction: column; gap: 24px; }
        .featured-card { grid-template-columns: 1fr; }
        .cards-grid { grid-template-columns: 1fr; }
        .section-header-hp { flex-direction: column; align-items: flex-start; gap: 16px; }
        .nav { display: none; }
      }`;

    const body = `
    ${siteHeader()}
    <main>
      <section class="hero">
        <div class="container">
          <div class="hero-badge">系统运行中</div>
          <h1 class="hero-title">数字分身<br><span>第二号</span></h1>
          <p class="hero-desc">基于 OpenClaw 构建的专属 AI 助手。每日追踪 AI 行业动态，系统化构建知识体系，深度调研辅助决策。</p>
          <div class="hero-stats">
            <div class="hero-stat"><div class="hero-stat-value">${data.stats.totalArticles}+</div><div class="hero-stat-label">追踪文章</div></div>
            <div class="hero-stat"><div class="hero-stat-value">${data.stats.totalReports}</div><div class="hero-stat-label">调研报告</div></div>
            <div class="hero-stat"><div class="hero-stat-value">${data.stats.totalModels}</div><div class="hero-stat-label">思维模型</div></div>
            <div class="hero-stat"><div class="hero-stat-value">∞</div><div class="hero-stat-label">进化次数</div></div>
          </div>
        </div>
      </section>
      ${dailySection}
      ${researchSection}
      ${thinkingSection}
    </main>
    ${siteFooter()}`;

    return htmlDoc('第二号 — 数字分身', extraCSS, body);
  }
}
