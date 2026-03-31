import { For, Show } from 'solid-js';
import { Layout } from '../../renderer/components/Layout.js';
import { ThinkingCategory, ThinkingModelDisplay } from '../../types/index.js';

const THINKING_CSS = `
.container-thinking { max-width: 900px; margin: 0 auto; padding: 0 24px; }
.hero-thinking { padding: 120px 0 40px; text-align: center; border-bottom: 1px solid var(--border); }
.nav-cats { display: flex; justify-content: center; gap: 8px; padding: 24px 0; border-bottom: 1px solid var(--border); flex-wrap: wrap; }
.nav-cat { padding: 8px 16px; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 100px; font-size: 13px; color: var(--text-secondary); text-decoration: none; font-weight: 500; transition: all 0.2s; }
.nav-cat:hover, .nav-cat.active { background: var(--accent); border-color: var(--accent); color: white; }
.th-section { padding: 48px 0; border-bottom: 1px solid var(--border); }
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
@media (max-width: 768px) { .model-header { flex-direction: column; gap: 12px; } .nav-cat { padding: 6px 12px; font-size: 12px; } }
`;

function ModelCard(props: { model: ThinkingModelDisplay }) {
  const m = props.model;
  return (
    <div class="model-card">
      <div class="model-header">
        <div style="display:flex;align-items:center;gap:12px;">
          <span style="font-size:28px;" innerHTML={m.icon} />
          <div>
            <div class="model-title">{m.title}</div>
            <div style="font-size:12px;color:var(--text-muted);margin-top:4px;">{m.source}</div>
          </div>
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;">
          <For each={m.tags}>{(t) => <span class="model-tag">{t}</span>}</For>
        </div>
      </div>
      <div class="model-section">
        <div class="model-section-title">定义</div>
        <div class="model-def">{m.definition}</div>
      </div>
      <div class="model-section">
        <div class="model-section-title">核心洞察</div>
        <ul class="insights-list">
          <For each={m.insights}>{(ins) => <li>{ins}</li>}</For>
        </ul>
      </div>
      <Show when={m.connections.length > 0}>
        <div class="model-section">
          <div class="model-section-title">关联模型</div>
          <div style="display:flex;flex-wrap:wrap;gap:8px;">
            <For each={m.connections}>{(c) => <span class="connection">{c}</span>}</For>
          </div>
        </div>
      </Show>
    </div>
  );
}

export interface ThinkingPageProps {
  category: ThinkingCategory;
  allCategories: ThinkingCategory[];
}

export function ThinkingPage(props: ThinkingPageProps) {
  const coreModels = () => props.category.models.slice(0, 5);
  const otherModels = () => props.category.models.slice(5);

  return (
    <Layout title={`${props.category.name}思维模型`} backLink="../index.html" extraCss={THINKING_CSS}>
      <main>
        <section class="hero-thinking">
          <div class="container-thinking">
            <div style="font-size:48px;margin-bottom:16px;" innerHTML={props.category.icon} />
            <h1 style="font-size:36px;font-weight:700;margin-bottom:12px;">{props.category.name}思维模型</h1>
            <p style="font-size:16px;color:var(--text-secondary);max-width:560px;margin:0 auto;">{props.category.description}</p>
            <div style="display:flex;justify-content:center;gap:40px;margin-top:32px;padding-top:32px;border-top:1px solid var(--border);">
              <div style="text-align:center;">
                <div style="font-size:28px;font-weight:700;color:var(--accent);">{props.category.models.length}</div>
                <div style="font-size:12px;color:var(--text-muted);margin-top:4px;">思维模型</div>
              </div>
            </div>
          </div>
        </section>
        <div class="nav-cats">
          <For each={props.allCategories}>
            {(c) => (
              <a href={`${c.slug}.html`} class={`nav-cat${c.slug === props.category.slug ? ' active' : ''}`}>
                <span innerHTML={c.icon} /> {c.name}
              </a>
            )}
          </For>
        </div>
        <section class="th-section">
          <div class="container-thinking">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:32px;">
              <span style="font-family:'JetBrains Mono',monospace;font-size:13px;color:var(--accent);font-weight:600;">01</span>
              <h2 style="font-size:22px;font-weight:700;">核心{props.category.name}模型</h2>
            </div>
            <For each={coreModels()}>{(m) => <ModelCard model={m} />}</For>
          </div>
        </section>
        <Show when={otherModels().length > 0}>
          <section class="th-section" style="background:var(--bg-secondary);padding:48px 0;">
            <div class="container-thinking">
              <div style="display:flex;align-items:center;gap:12px;margin-bottom:32px;">
                <span style="font-family:'JetBrains Mono',monospace;font-size:13px;color:var(--accent);font-weight:600;">02</span>
                <h2 style="font-size:22px;font-weight:700;">更多{props.category.name}模型</h2>
              </div>
              <ul class="simple-list">
                <For each={otherModels()}>
                  {(m) => <li><strong>{m.title}</strong> — {m.definition}</li>}
                </For>
              </ul>
            </div>
          </section>
        </Show>
      </main>
    </Layout>
  );
}
