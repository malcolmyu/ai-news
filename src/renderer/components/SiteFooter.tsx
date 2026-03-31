import { SITE_FOOTER_HTML } from '../styles/shared.css.js';

export function SiteFooter() {
  return (
    <footer style="padding: 40px 0; border-top: 1px solid var(--border); text-align: center;">
      <div class="container">
        <p style="font-size: 14px; color: var(--text-muted);" innerHTML={SITE_FOOTER_HTML} />
      </div>
    </footer>
  );
}
