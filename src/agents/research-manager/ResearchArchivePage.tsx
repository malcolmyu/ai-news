import { For, Show } from 'solid-js';
import { Layout } from '../../renderer/components/Layout.js';
import { ResearchEntry } from '../../types/index.js';

const RESEARCH_CSS = `
.rch-header { padding: 100px 0 40px; }
.rch-header h1 { font-size: 26px; font-weight: 500; letter-spacing: -0.3px; }
.rch-header .subtitle { font-size: 13px; color: var(--text-muted); margin-top: 4px; }
`;

export interface ResearchArchivePageProps {
  entries: ResearchEntry[];
}

export function ResearchArchivePage(props: ResearchArchivePageProps) {
  const latest = () => props.entries[0] ?? null;

  return (
    <Layout title="调研报告归档" backLink="../index.html" extraCss={RESEARCH_CSS}>
      <div class="rch-header">
        <div class="container-sm">
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px;">
            <div>
              <h1>📊 调研报告归档</h1>
              <div class="subtitle">Research Reports Archive</div>
            </div>
            <div style="text-align:right;">
              <div class="stats-value">{props.entries.length}</div>
              <div class="stats-label">调研报告</div>
            </div>
          </div>
        </div>
      </div>
      <main class="container-sm">
        <Show when={latest()}>
          {(item) => (
            <>
              <div class="section-label">Featured</div>
              <a href={item().file} class="featured-card">
                <div class="featured-content">
                  <div class="featured-meta">
                    <span class="featured-badge">最新</span>
                    <span>{item().date}</span>
                  </div>
                  <h3 class="featured-title">{item().title}</h3>
                  <p class="featured-desc">{item().summary}</p>
                </div>
                <div class="featured-arrow">→</div>
              </a>
            </>
          )}
        </Show>
        <div class="section-label">History</div>
        <div class="archive-list">
          <For each={props.entries}>
            {(e) => (
              <a href={e.file} class="archive-item">
                <div class="archive-icon" innerHTML={e.icon} />
                <div class="archive-content">
                  <div style="font-size:12px;color:var(--text-muted);margin-bottom:3px;">{e.date}</div>
                  <div style="font-size:15px;font-weight:500;margin-bottom:3px;">{e.title}</div>
                  <div style="font-size:12px;color:var(--text-secondary);">{e.category}</div>
                </div>
                <div class="archive-arrow">→</div>
              </a>
            )}
          </For>
        </div>
      </main>
    </Layout>
  );
}
