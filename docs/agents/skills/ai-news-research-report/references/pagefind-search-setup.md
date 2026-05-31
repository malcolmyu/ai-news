# Pagefind 搜索集成参考

## 概述

ai-news 站点使用 [Pagefind](https://pagefind.app/) (v1.5.2) 实现客户端全文搜索。搜索 UI 集成在站点导航栏（⌘K 快捷键触发），覆盖所有 HTML 页面（日报 + 深度调研报告）。

## 文件清单

| 文件 | 用途 |
|------|------|
| `package.json` | 定义 `build:search` 脚本 → `pagefind --site docs --output-subdir pagefind` |
| `package-lock.json` | Pagefind 依赖锁定 |
| `docs/search.js` | 搜索 UI 逻辑（modal、快捷键、PagefindUI 初始化） |
| `docs/styles.css` | 搜索触发器按钮样式 + modal 样式 |
| `docs/index.html` | 搜索 HTML 结构（`#search-modal`、`#site-search`） + 引用 `pagefind/pagefind-ui.css` 和 `pagefind/pagefind-ui.js` |
| `docs/pagefind/` | **搜索索引文件（必须提交）** — 由 `npm run build:search` 生成 |

## 构建命令

```bash
npm ci                          # 安装 Pagefind
npm run build:search            # 生成 docs/pagefind/ 索引文件
```

## 部署注意事项

- **GitHub Pages source = branch deploy**（`malcolmyu/auckland`，`/docs`）
- `docs/pagefind/` 必须在仓库中（不能 gitignore），否则线上 404
- CI 中的 `build:search` 步骤验证索引可构建，但分支部署不依赖 CI 产物

## 索引更新时机

每次新增或修改 HTML 页面后：
```bash
npm run build:search
git add docs/pagefind/
git commit -m "chore: rebuild search index"
```

## 验证

```bash
# 索引文件存在
ls docs/pagefind/pagefind-ui.js

# 线上可访问
curl -sI 'https://malcolmyu.github.io/ai-news/pagefind/pagefind-ui.js' | head -1
# 期望: HTTP/2 200
```

## PagefindUI 配置要点

### showSubResults（必须开启）

PagefindUI 的 `showSubResults` **默认是 `false`** — 只显示标题，不含匹配关键字的上下文摘录。用户期望「搜索引擎」式的 snippet 展示（标题 + 关键词前后文），必须显式开启：

```js
new window.PagefindUI({
  element: "#site-search",
  showSubResults: true,      // ⛔ 必须显式 true，默认 false
  excerptLength: 30,         // 摘要长度（单词数），中文约 15-20 字
  // ... 其余配置
});
```

`excerptLength` 控制摘录长度（按单词计，中文约 15-20 字为宜）。

### CSS 陷阱：display: none 隐藏 excerpt

开启 `showSubResults: true` 后，excerpt 可能在 DOM 中存在但视觉上不可见。原因：站点 `styles.css` 中可能有针对 `.pagefind-ui__result-excerpt` 的 `display: none` 规则（当初 `showSubResults: false` 时添加的抑制样式）。**JS 配置和 CSS 必须同步检查**：

```css
/* 正确的 CSS — 让 excerpt 可见 */
.site-search .pagefind-ui__result-excerpt,
.site-search .pagefind-modular-list-excerpt {
  display: block;           /* ⛔ 不能是 none */
  min-width: 0;
  margin: 0;
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 400;
  line-height: 1.55;
}
```

调试方法：打开浏览器 DevTools → 搜索关键词 → 检查 `.pagefind-ui__result-excerpt` 的 computed `display` 值。期望是 `block`，如果是 `none` 则 CSS 覆盖了 Pagefind 默认样式。

`mark` 高亮样式已在 `styles.css` 中预置。

### baseUrl 陷阱：双重路径前缀

**症状：** 搜索结果链接变成 `https://malcolmyu.github.io/ai-news/ai-news/research/...`（双重 `ai-news/`）。

**根因：** Pagefind 的 Default UI 内部用 `baseUrl` 从 `result.url` 剥离前缀使其变成相对路径。默认 `baseUrl: "/"` → 剥离 `/` → `/ai-news/research/...` 变成 `ai-news/research/...`（相对）→ 浏览器在 `/ai-news/` 页面解析再叠加 → 双重前缀。

**诊断（DevTools）：**
```js
// Pagefind API 返回的 URL（正确）
(await pagefind.search('Agent')).results[0].data().url
// → "/ai-news/research/managed-agents.html"  ✓

// 但 DOM href 属性（错误 — 丢失前导 /）
document.querySelector('.pagefind-ui__result-link').getAttribute('href')
// → "ai-news/research/managed-agents.html"  ✗
```

**修复：** 设置 `baseUrl: "/ai-news/"` 让 UI 正确剥离站点前缀：
```js
new window.PagefindUI({
  element: "#site-search",
  baseUrl: "/ai-news/",  // ⛔ 必须匹配站点实际子路径
  showSubResults: true,
  excerptLength: 30,
  // ... 其余配置
});
```

**为什么 `processResult` 改不了：** `processResult` 只修改传给 UI 的数据对象，但 UI 渲染 `<a>` 标签时会重新处理 URL（用 `baseUrl` 剥离前缀）。即使 `processResult` 中确保 URL 以 `/` 开头，渲染后仍会被 UI 剥离。必须通过 `baseUrl` 配置解决。
