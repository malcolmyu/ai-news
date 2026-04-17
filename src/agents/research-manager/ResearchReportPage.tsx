import { Layout } from '../../renderer/components/Layout.js';

const REPORT_CSS = `
.report-header { background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%); color: white; padding: 48px 0; margin-top: 64px; }
.report-header h1 { font-size: 28px; font-weight: 700; color: white; margin-bottom: 8px; }
.report-header .metadata { display: flex; gap: 16px; font-size: 14px; opacity: 0.9; }
.markdown-body { padding: 32px 0; line-height: 1.6; color: var(--text-primary); }
.markdown-body h2 { margin-top: 2em; margin-bottom: 1em; padding-bottom: 0.3em; border-bottom: 1px solid var(--border-color); }
.markdown-body h3 { margin-top: 1.5em; margin-bottom: 0.8em; }
.markdown-body p { margin-bottom: 1em; }
.markdown-body ul, .markdown-body ol { margin-bottom: 1em; padding-left: 2em; }
.markdown-body li { margin-bottom: 0.25em; }
.markdown-body blockquote { margin: 1.5em 0; padding-left: 1em; border-left: 4px solid var(--border-color); color: var(--text-secondary); }
.markdown-body pre { background: var(--bg-secondary); padding: 16px; border-radius: 8px; overflow-x: auto; margin-bottom: 1em; }
.markdown-body code { font-family: ui-monospace, SFMono-Regular, Consolas, monospace; background: var(--bg-secondary); padding: 0.2em 0.4em; border-radius: 3px; font-size: 0.9em; }
.markdown-body pre code { padding: 0; background: transparent; }
.markdown-body a { color: var(--primary-color); text-decoration: none; }
.markdown-body a:hover { text-decoration: underline; }
`;

export interface ResearchReportPageProps {
  title: string;
  date: string;
  category: string;
  contentHtml: string;
}

export function ResearchReportPage(props: ResearchReportPageProps) {
  return (
    <Layout title={props.title} backLink="./archive.html" extraCss={REPORT_CSS}>
      <div class="report-header">
        <div class="container-sm">
          <h1>{props.title}</h1>
          <div class="metadata">
            <div class="meta-item">
              <span class="meta-icon">📅</span>
              {props.date}
            </div>
            <div class="meta-item">
              <span class="meta-icon">📁</span>
              {props.category}
            </div>
          </div>
        </div>
      </div>
      <main class="container-sm">
        <div class="markdown-body" innerHTML={props.contentHtml} />
      </main>
    </Layout>
  );
}
