import { For, Show } from 'solid-js';
import { Layout } from '../../renderer/components/Layout.js';
import { HomepageData, ResearchEntry } from '../../types/index.js';

const HOMEPAGE_CSS = `
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
.hp-section { padding: 80px 0; }
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
.cards-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; }
.card { background: var(--bg-primary); border: 1px solid var(--border); border-radius: 12px; padding: 28px; text-decoration: none; color: inherit; transition: all 0.2s; }
.card:hover { border-color: var(--accent-light); box-shadow: var(--shadow-md); }
.card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
.card-category { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--accent); }
.card-icon { width: 40px; height: 40px; background: var(--bg-secondary); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
.card-title { font-size: 18px; font-weight: 600; margin-bottom: 8px; }
.card-desc { font-size: 14px; color: var(--text-secondary); line-height: 1.5; margin-bottom: 16px; }
.card-meta { font-size: 13px; color: var(--text-muted); font-weight: 500; }
@media (max-width: 768px) {
  .hero { padding: 120px 0 60px; }
  .hero-stats { flex-direction: column; gap: 24px; }
  .featured-card { grid-template-columns: 1fr; }
  .cards-grid { grid-template-columns: 1fr; }
  .section-header-hp { flex-direction: column; align-items: flex-start; gap: 16px; }
  .nav { display: none; }
}`;

function ResearchEntryRow(props: { entry: ResearchEntry }) {
  const e = props.entry;
  return (
    <a href={`research/${e.file}`} class="daily-entry">
      <div class="entry-icon" innerHTML={e.icon} />
      <div style="flex:1;">
        <div style="font-weight:600;font-size:14px;margin-bottom:2px;">{e.title}</div>
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
            <p class="hero-desc">基于 OpenClaw 构建的专属 AI 助手。每日追踪 AI 行业动态，系统化构建知识体系，深度调研辅助决策。</p>
            <div class="hero-stats">
              <div class="hero-stat"><div class="hero-stat-value">{d.stats.totalArticles}+</div><div class="hero-stat-label">追踪文章</div></div>
              <div class="hero-stat"><div class="hero-stat-value">{d.stats.totalReports}</div><div class="hero-stat-label">调研报告</div></div>
              <div class="hero-stat"><div class="hero-stat-value">{d.stats.totalModels}</div><div class="hero-stat-label">思维模型</div></div>
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
            <div style="display:flex;flex-direction:column;gap:12px;">
              <a href="daily/ai-daily-latest.html" class="daily-entry latest-entry">
                <div class="entry-icon" style="background:var(--accent);">📰</div>
                <div style="flex:1;">
                  <div style="font-weight:600;font-size:15px;margin-bottom:4px;">今日日报 <span class="badge-latest">最新</span></div>
                  <div style="font-size:13px;color:var(--text-secondary);">实时更新 · {d.latestDaily ? `${d.latestDaily.articleCount} 篇文章` : '暂无'}</div>
                </div>
                <div style="font-size:20px;color:var(--accent);">→</div>
              </a>
              <a href="daily/archive.html" class="daily-entry">
                <div class="entry-icon">📚</div>
                <div style="flex:1;">
                  <div style="font-weight:600;font-size:14px;margin-bottom:2px;">历史日报</div>
                  <div style="font-size:12px;color:var(--text-muted);">共 {d.dailyArchiveCount} 期归档</div>
                </div>
                <div style="font-size:16px;color:var(--text-muted);">→</div>
              </a>
            </div>
          </div>
        </section>

        {/* Research */}
        <section class="hp-section" style="background:var(--bg-secondary);" id="research">
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
              <div style="display:flex;flex-direction:column;gap:12px;margin-top:24px;">
                <For each={moreResearch}>{(r) => <ResearchEntryRow entry={r} />}</For>
              </div>
            </Show>
          </div>
        </section>

        {/* Thinking */}
        <section class="hp-section" id="knowledge">
          <div class="container">
            <div class="section-header-hp">
              <div><div class="section-label">Knowledge Base</div><h2 class="section-title-hp">知识武器库</h2></div>
              <a href="thinking/decision.html" class="section-link">查看全部 →</a>
            </div>
            <div class="cards-grid">
              <For each={d.thinkingCategories}>
                {(c) => (
                  <a href={`thinking/${c.file}`} class="card">
                    <div class="card-header">
                      <span class="card-category">{c.name}</span>
                      <div class="card-icon" innerHTML={c.icon} />
                    </div>
                    <h3 class="card-title">{c.name}思维模型</h3>
                    <p class="card-desc">{c.description}</p>
                    <div class="card-meta">{c.modelCount} 个模型</div>
                  </a>
                )}
              </For>
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}
