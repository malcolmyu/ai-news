// Shared CSS design tokens matching the reference site design
export const SITE_NAME = '第二号';
export const SITE_SUBTITLE = '数字分身';
export const SITE_FOOTER = '🤖 <strong>第二号</strong> — 把自己产品化 — 持续进化中';

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

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 24px;
}

.container-sm {
    max-width: 800px;
    margin: 0 auto;
    padding: 0 20px;
}
`;

export const HEADER_CSS = `
.header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border-light);
    z-index: 100;
}

.header-inner {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 64px;
}

.logo {
    display: flex;
    align-items: center;
    gap: 12px;
    text-decoration: none;
    color: var(--text-primary);
}

.logo-icon {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dark) 100%);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    box-shadow: var(--shadow-sm);
}

.logo-text {
    font-weight: 600;
    font-size: 15px;
    letter-spacing: -0.01em;
}

.nav { display: flex; gap: 32px; }

.nav-link {
    font-size: 14px;
    color: var(--text-secondary);
    text-decoration: none;
    font-weight: 500;
    transition: color 0.2s;
}

.nav-link:hover { color: var(--accent); }
`;

export const FONTS_LINK = '<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">';

export function siteHeader(backLink?: string): string {
  const navOrBack = backLink
    ? `<a href="${backLink}" class="nav-link">← 返回首页</a>`
    : `<nav class="nav">
        <a href="index.html" class="nav-link">首页</a>
        <a href="daily/archive.html" class="nav-link">AI 日报</a>
        <a href="research/archive.html" class="nav-link">深度调研</a>
        <a href="thinking/decision.html" class="nav-link">知识武器库</a>
      </nav>`;

  return `<header class="header">
    <div class="container">
      <div class="header-inner">
        <a href="${backLink ? '../index.html' : 'index.html'}" class="logo">
          <div class="logo-icon">🤖</div>
          <span class="logo-text">${SITE_NAME}</span>
        </a>
        ${navOrBack}
      </div>
    </div>
  </header>`;
}

export function siteFooter(homeLink: string = 'index.html'): string {
  return `<footer style="padding: 40px 0; border-top: 1px solid var(--border); text-align: center;">
    <div class="container">
      <p style="font-size: 14px; color: var(--text-muted);">
        ${SITE_FOOTER}
      </p>
    </div>
  </footer>`;
}

export function htmlDoc(title: string, extraCSS: string, body: string): string {
  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${title} - ${SITE_NAME}</title>
    ${FONTS_LINK}
    <style>
        ${SHARED_CSS}
        ${HEADER_CSS}
        ${extraCSS}
    </style>
</head>
<body>
${body}
</body>
</html>`;
}
