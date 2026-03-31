// 站点级常量
export const SITE_NAME = '第二号';
export const SITE_SUBTITLE = '数字分身';
export const SITE_FOOTER_HTML = '🤖 <strong>第二号</strong> — 把自己产品化 — 持续进化中';
export const FONTS_LINK = '<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">';

export const SHARED_CSS = `
:root {
    --bg-primary: #ffffff;
    --bg-secondary: #f8fafc;
    --bg-tertiary: #f1f5f9;
    --accent: #3b82f6;
    --accent-light: #60a5fa;
    --accent-dark: #2563eb;
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --text-muted: #94a3b8;
    --border: #e2e8f0;
    --border-light: #f1f5f9;
    --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    --shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
    --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
    --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
}
.container { max-width: 1200px; margin: 0 auto; padding: 0 24px; }
.container-sm { max-width: 800px; margin: 0 auto; padding: 0 20px; }
`;

export const HEADER_CSS = `
.header {
    position: fixed; top: 0; left: 0; right: 0;
    background: rgba(255,255,255,0.8);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border-light);
    z-index: 100;
}
.header-inner { display: flex; justify-content: space-between; align-items: center; height: 64px; }
.logo { display: flex; align-items: center; gap: 12px; text-decoration: none; color: var(--text-primary); }
.logo-icon { width: 36px; height: 36px; background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dark) 100%); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px; box-shadow: var(--shadow-sm); }
.logo-text { font-weight: 600; font-size: 15px; letter-spacing: -0.01em; }
.nav { display: flex; gap: 32px; }
.nav-link { font-size: 14px; color: var(--text-secondary); text-decoration: none; font-weight: 500; transition: color 0.2s; }
.nav-link:hover { color: var(--accent); }
`;

/** 公共归档/研究列表样式（被 research-manager、thinking-system、homepage-builder 共用） */
export const ARCHIVE_CSS = `
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
.archive-item.latest { background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%); border-color: var(--accent); }
.archive-icon { width: 48px; height: 48px; background: var(--bg-secondary); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 24px; flex-shrink: 0; }
.archive-item.latest .archive-icon { background: var(--accent); }
.archive-content { flex: 1; }
.archive-date { font-size: 16px; font-weight: 600; margin-bottom: 4px; display: flex; align-items: center; gap: 8px; }
.badge-latest { padding: 2px 8px; background: #dcfce7; color: #166534; border-radius: 100px; font-size: 11px; font-weight: 600; }
.archive-meta { font-size: 13px; color: var(--text-secondary); }
.archive-arrow { font-size: 20px; color: var(--text-muted); transition: all 0.2s; }
.archive-item:hover .archive-arrow { color: var(--accent); transform: translateX(4px); }
.stats-value { font-size: 36px; font-weight: 700; color: #60a5fa; }
.stats-label { font-size: 12px; opacity: 0.7; }
`;
