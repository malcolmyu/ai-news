import { For } from 'solid-js';
import { Layout } from '../../renderer/components/Layout.js';
import { DailyReport, SummarizedArticle } from '../../types/index.js';
import { formatDate } from '../../utils/config.js';

const DAILY_CSS = `
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
@media (max-width: 640px) { h1 { font-size: 24px; } .news-card { padding: 16px; } }
@media (prefers-color-scheme: dark) {
  :root { --bg-primary: #111827; --bg-secondary: #1f2937; --text-primary: #f9fafb; --text-secondary: #9ca3af; --border: #374151; }
  .daily-header { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); }
}`;

function ArticleCard(props: { article: SummarizedArticle }) {
  const dateDisplay = props.article.published ? formatDate(new Date(props.article.published)) : '近期';
  return (
    <article class="news-card">
      <div class="news-meta">
        <span class="news-source">{props.article.source || ''}</span>
        <span>·</span>
        <span>{dateDisplay}</span>
      </div>
      <h3 class="news-title">{props.article.title}</h3>
      <p class="news-summary">{props.article.summary || ''}</p>
      <a href={props.article.link} class="news-link" target="_blank" rel="noopener noreferrer">阅读原文 →</a>
    </article>
  );
}

function CategorySection(props: { category: string; articles: SummarizedArticle[] }) {
  return (
    <section class="section">
      <div class="section-header">
        <h2 class="section-title">{props.category}</h2>
        <span class="section-count">{props.articles.length} 条</span>
      </div>
      <div class="news-list">
        <For each={props.articles}>{(article) => <ArticleCard article={article} />}</For>
      </div>
    </section>
  );
}

export interface DailyReportPageProps {
  report: DailyReport;
  categorized: Record<string, SummarizedArticle[]>;
  dateStr: string;
}

export function DailyReportPage(props: DailyReportPageProps) {
  const entries = () => Object.entries(props.categorized).filter(([, a]) => a.length > 0);
  return (
    <Layout title={`AI 日报 - ${props.dateStr}`} backLink="../index.html" extraCss={DAILY_CSS}>
      <div class="daily-header">
        <div class="container-sm">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
              <h1>🤖 AI 日报</h1>
              <p class="subtitle">{props.dateStr}</p>
            </div>
            <div style="text-align:right;">
              <div class="stats-value">{props.report.articles.length}</div>
              <div class="stats-label">条资讯</div>
            </div>
          </div>
        </div>
      </div>
      <main class="container-sm" style="padding-top: 32px;">
        <For each={entries()}>{([cat, articles]) => <CategorySection category={cat} articles={articles} />}</For>
      </main>
    </Layout>
  );
}
