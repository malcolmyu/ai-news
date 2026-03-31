import { renderToString } from 'solid-js/web';
import { JSX } from 'solid-js';

/**
 * 将一个 SolidJS 组件渲染为完整的 HTML 字符串（SSR 静态生成）。
 * 组件内部禁止使用任何 IO 操作（fs / path / fetch）。
 */
export function renderPage<P extends object>(
  Component: (props: P) => JSX.Element,
  props: P
): string {
  return renderToString(() => Component(props));
}
