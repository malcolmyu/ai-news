import { JSX } from 'solid-js';
import { SHARED_CSS, HEADER_CSS, ARCHIVE_CSS, FONTS_LINK, SITE_NAME } from '../styles/shared.css.js';
import { SiteHeader } from './SiteHeader.js';
import { SiteFooter } from './SiteFooter.js';

interface LayoutProps {
  title: string;
  extraCss?: string;
  backLink?: string;   // 传入时 header 显示"← 返回首页"，否则显示完整导航
  children: JSX.Element;
}

export function Layout(props: LayoutProps) {
  return (
    <html lang="zh-CN">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>{props.title} - {SITE_NAME}</title>
        <span innerHTML={FONTS_LINK} />
        <style innerHTML={`${SHARED_CSS}${HEADER_CSS}${ARCHIVE_CSS}${props.extraCss ?? ''}`} />
      </head>
      <body>
        <SiteHeader backLink={props.backLink} />
        {props.children}
        <SiteFooter />
      </body>
    </html>
  );
}
