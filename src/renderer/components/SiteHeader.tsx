import { SITE_NAME } from '../styles/shared.css.js';

interface SiteHeaderProps {
  backLink?: string;  // 传入时显示"← 返回首页"，否则显示完整导航
}

export function SiteHeader(props: SiteHeaderProps) {
  const logoHref = props.backLink ? '../index.html' : 'index.html';

  return (
    <header class="header">
      <div class="container">
        <div class="header-inner">
          <a href={logoHref} class="logo">
            <div class="logo-icon">🤖</div>
            <span class="logo-text">{SITE_NAME}</span>
          </a>
          {props.backLink
            ? <a href={props.backLink} class="nav-link">← 返回首页</a>
            : (
              <nav class="nav">
                <a href="index.html" class="nav-link">首页</a>
                <a href="daily/archive.html" class="nav-link">AI 日报</a>
                <a href="research/archive.html" class="nav-link">深度调研</a>
              </nav>
            )
          }
        </div>
      </div>
    </header>
  );
}
