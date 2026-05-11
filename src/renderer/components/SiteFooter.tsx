import { SITE_FOOTER_HTML } from '../styles/shared.css.js';

export function SiteFooter() {
  return (
    <footer style="padding: 32px 0; border-top: 1px solid var(--border); text-align: center; margin-top: 48px;">
      <div class="container">
        <p style="font-size: 13px; color: var(--text-muted);" innerHTML={SITE_FOOTER_HTML} />
      </div>
    </footer>
  );
}
