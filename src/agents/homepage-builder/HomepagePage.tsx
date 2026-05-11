import { Show } from 'solid-js';
import { Layout } from '../../renderer/components/Layout.js';
import { HomepageData, ResearchEntry } from '../../types/index.js';

const HOMEPAGE_CSS = `
/* Hero */
.hero { padding: 100px 0 60px; text-align: center; }
.hero-badge { display: inline-flex; align-items: center; gap: 8px; padding: 6px 14px; background: #fff; border: 1px solid var(--border); border-radius: 100px; font-size: 12px; color: var(--text-secondary); font-weight: 500; margin-bottom: 24px; box-shadow: var(--shadow-none); }
.hero-badge::before { content: ''; width: 6px; height: 6px; background: #10b981; border-radius: 50%; display: inline-block; }
.hero-title { font-size: clamp(36px, 5vw, 52px); font-weight: 500; line-height: 1.15; letter-spacing: -0.5px; margin-bottom: 16px; color: var(--text-primary); }
.hero-title span { color: var(--accent); }
.hero-desc { font-size: 15px; color: var(--text-secondary); max-width: 520px; margin: 0 auto 32px; line-height: 1.6; }
.hero-stats { display: flex; justify-content: center; gap: 40px; padding-top: 32px; border-top: 1px solid var(--border); }
.hero-stat { text-align: center; }
.hero-stat-value { font-size: 28px; font-weight: 500; line-height: 1.2; margin-bottom: 4px; color: var(--accent); }
.hero-stat-label { font-size: 12px; color: var(--text-muted); font-weight: 400; }
.hp-section { padding: 48px 0; }
.section-header-hp { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 24px; }
.section-title-hp { font-size: 22px; font-weight: 500; letter-spacing: -0.3px; }
.section-link { font-size: 13px; color: var(--accent); text-decoration: none; font-weight: 500; display: flex; align-items: center; gap: 4px; transition: gap 0.2s; }
.section-link:hover { gap: 8px; }
.daily-entry { display: flex; align-items: center; gap: 14px; padding: 14px 20px; background: #fff; border: 1px solid var(--border); border-radius: var(--radius-md); text-decoration: none; color: inherit; transition: box-shadow 0.2s; box-shadow: var(--shadow-none); }
.daily-entry:hover { box-shadow: var(--shadow-sm); }
.entry-icon { width: 36px; height: 36px; background: var(--bg-secondary); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0; }
.badge-latest { padding: 2px 8px; background: #e8f0fe; color: var(--accent); border-radius: 100px; font-size: 10px; font-weight: 600; margin-left: 6px; }
.cards-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.card-link { background: #fff; border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 24px; text-decoration: none; color: inherit; transition: box-shadow 0.2s; box-shadow: var(--shadow-none); }
.card-link:hover { box-shadow: var(--shadow-sm); }
.card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
.card-category { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--accent); }
.card-icon { width: 36px; height: 36px; background: var(--bg-secondary); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 18px; }
.card-title { font-size: 16px; font-weight: 500; margin-bottom: 6px; }
.card-desc { font-size: 13px; color: var(--text-secondary); line-height: 1.5; margin-bottom: 12px; }
.card-meta { font-size: 12px; color: var(--text-muted); font-weight: 400; }
@media (max-width: 768px) {
  .hero { padding: 88px 0 40px; }
  .hero-stats { flex-direction: column; gap: 20px; }
  .featured-card { grid-template-columns: 1fr; }
  .cards-grid { grid-template-columns: 1fr; }
  .section-header-hp { flex-direction: column; align-items: flex-start; gap: 12px; }
  .nav { display: none; }
}`;

function ResearchEntryRow(props: { entry: ResearchEntry }) {
  const e = props.entry;
  return (
    <a href={`research/${e.file}`} class="daily-entry">
      <div class="entry-icon" innerHTML={e.icon} />
      <div style="flex:1;">
        <div style="font-weight:500;font-size:14px;margin-bottom:2px;">{e.title}</div>
        <div style="font-size:12px;color:var(--text-muted);">{e.date} · {e.category}</div>
      </div>
      <div style="font-size:16px;color:var(--text-muted);">→</div>
    </a>
  );
}

export interface HomepagePageProps {
  data: HomepageData;
}

export function HomepagePage(props: HomepagePageProps) {
  const d = props.data;
  const latest = d.latestResearch;
  const moreResearch = d.researchList.slice(1, 4);

  return (
    <Layout title="第二号 — 数字分身" extraCss={HOMEPAGE_CSS}>
      <main>
        {/* Hero */}
        <section class="hero">
          <div class="container">
            <div class="hero-badge">系统运行中</div>
            <h1 class="hero-title">数字分身<br /><span>第二号</span></h1>
            <p class="hero-desc">基于 OpenClaw 构建的专属 AI 助手。每日追踪 AI 行业动态，系统化构建知识体系。</p>
            <div class="hero-stats">
              <div class="hero-stat"><div class="hero-stat-value">{d.stats.totalArticles}+</div><div class="hero-stat-label">追踪文章</div></div>
              <div class="hero-stat"><div class="hero-stat-value">{d.stats.totalReports}</div><div class="hero-stat-label">调研报告</div></div>
              <div class="hero-stat"><div class="hero-stat-value">∞</div><div class="hero-stat-label">进化次数</div></div>
            </div>
          </div>
        </section>

        {/* Daily */}
        <section class="hp-section" id="daily">
          <div class="container">
            <div class="section-header-hp">
              <div><div class="section-label">AI Insight</div><h2 class="section-title-hp">每日 AI 日报</h2></div>
              <a href="daily/archive.html" class="section-link">查看全部 →</a>
            </div>
            <div style="display:flex;flex-direction:column;gap:10px;">
              <a href="daily/ai-daily-latest.html" class="daily-entry">
                <div class="entry-icon" style="background:var(--accent);color:#fff;">📰</div>
                <div style="flex:1;">
                  <div style="font-weight:500;font-size:14px;margin-bottom:3px;">今日日报 <span class="badge-latest">最新</span></div>
                  <div style="font-size:12px;color:var(--text-secondary);">实时更新 · {d.latestDaily ? `${d.latestDaily.articleCount} 篇文章` : '暂无'}</div>
                </div>
                <div style="font-size:18px;color:var(--accent);">→</div>
              </a>
              <a href="daily/archive.html" class="daily-entry">
                <div class="entry-icon">📚</div>
                <div style="flex:1;">
                  <div style="font-weight:500;font-size:14px;margin-bottom:2px;">历史日报</div>
                  <div style="font-size:12px;color:var(--text-muted);">共 {d.dailyArchiveCount} 期归档</div>
                </div>
                <div style="font-size:16px;color:var(--text-muted);">→</div>
              </a>
            </div>
          </div>
        </section>

        {/* Research */}
        <section class="hp-section" id="research">
          <div class="container">
            <div class="section-header-hp">
              <div><div class="section-label">Research</div><h2 class="section-title-hp">深度调研报告</h2></div>
              <a href="research/archive.html" class="section-link">查看全部 →</a>
            </div>
            <Show when={latest} fallback={<p style="color:var(--text-muted);text-align:center;padding:32px 0;">暂无调研报告</p>}>
              {(r) => (
                <a href={`research/${r().file}`} class="featured-card">
                  <div class="featured-content">
                    <div class="featured-meta"><span class="featured-badge">精选</span><span>{r().date}</span></div>
                    <h3 class="featured-title">{r().title}</h3>
                    <p class="featured-desc">{r().summary}</p>
                  </div>
                  <div class="featured-arrow">→</div>
                </a>
              )}
            </Show>
            <Show when={moreResearch.length > 0}>
              <div style="display:flex;flex-direction:column;gap:10px;margin-top:20px;">
                <For each={moreResearch}>{(r) => <ResearchEntryRow entry={r} />}</For>
              </div>
            </Show>
          </div>
        </section>

      </main>
    </Layout>
  );
}
