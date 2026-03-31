import { For } from 'solid-js';
import { Layout } from '../../renderer/components/Layout.js';
import { ArchiveEntry } from '../../types/index.js';

const ARCHIVE_EXTRA_CSS = `
.archive-header { background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%); color: white; padding: 48px 0; margin-top: 64px; }
.archive-header h1 { font-size: 28px; font-weight: 700; color: white; }
.archive-header .subtitle { font-size: 14px; opacity: 0.8; margin-top: 4px; }
@media (max-width: 640px) { .archive-item { padding: 16px; } .archive-icon { width: 40px; height: 40px; font-size: 20px; } }
`;

export interface DailyArchivePageProps {
  archives: ArchiveEntry[];
}

export function DailyArchivePage(props: DailyArchivePageProps) {
  return (
    <Layout title="历史日报归档" backLink="../index.html" extraCss={ARCHIVE_EXTRA_CSS}>
      <div class="archive-header">
        <div class="container-sm">
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px;">
            <div>
              <h1>📚 历史日报归档</h1>
              <div class="subtitle">AI Daily News Archive</div>
            </div>
            <div style="text-align:right;">
              <div class="stats-value">{props.archives.length}</div>
              <div class="stats-label">历史日报</div>
            </div>
          </div>
        </div>
      </div>
      <main class="container-sm">
        <div class="archive-list">
          <For each={props.archives}>
            {(item, i) => (
              <a href={item.file} class={`archive-item${i() === 0 ? ' latest' : ''}`}>
                <div class="archive-icon">📰</div>
                <div class="archive-content">
                  <div class="archive-date">
                    {item.dateDisplay}
                    {i() === 0 && <span class="badge-latest">最新</span>}
                  </div>
                  <div class="archive-meta">{item.articles} 篇文章 · AI 日报</div>
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
