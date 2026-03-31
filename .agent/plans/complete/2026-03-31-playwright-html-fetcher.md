# Playwright HTML Fetcher Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将 `HTMLFetcher` 从 axios+jsdom 静态抓取改为 Playwright headless 抓取，使 SPA 页面（Manus、Cognition、Cline 等）能正确渲染后提取文章链接。

**Architecture:** 用 `playwright` 包替换 `HTMLFetcher` 内部的 axios+jsdom 逻辑；启动一个共享的 Browser 实例复用（避免每次都冷启动），`fetchFromSource` 改为用 `page.goto()` + `page.waitForLoadState('networkidle')` 等待 JS 渲染完成，再用 `page.$$()` 按 selector 提取元素；`HtmlSource` 接口保持不变，调用方 `DailyReporter` 无需修改。

**Tech Stack:** `playwright` (Node.js)，TypeScript ESM，现有 `Article` 类型

---

### Task 1: 安装 playwright 依赖并安装 Chromium

**Files:**
- Modify: `package.json`（添加 playwright 依赖）

**Step 1: 安装依赖**

```bash
cd /Users/yuminghao/conductor/workspaces/ai-news/auckland
npm install playwright
npx playwright install chromium
```

Expected: `node_modules/playwright` 存在，`~/.cache/ms-playwright/chromium-*` 目录存在

**Step 2: 验证安装**

```bash
node -e "import('playwright').then(m => console.log('playwright version:', m.default.chromium.name()))"
```

Expected: 输出 `playwright version: chromium`

**Step 3: Commit**

```bash
git add package.json package-lock.json
git commit -m "chore: add playwright dependency"
```

---

### Task 2: 重写 HTMLFetcher 使用 Playwright

**Files:**
- Modify: `src/agents/daily-reporter/fetchers/html-fetcher.ts`（完整重写）

**Step 1: 替换实现**

将文件内容替换为以下代码（保留 `HtmlSource` 接口不变，调用方无需修改）：

```typescript
import { chromium, Browser, Page } from 'playwright';
import { Article } from '../../../types/index.js';

export interface HtmlSource {
  name: string;
  url: string;
  selector: string;
  title_selector?: string;
  link_selector?: string;
  content_selector?: string;
  category?: string;
}

export class HTMLFetcher {
  private timeout: number;
  private browser: Browser | null = null;

  constructor(timeout: number = 30000) {
    this.timeout = timeout;
  }

  private async getBrowser(): Promise<Browser> {
    if (!this.browser) {
      this.browser = await chromium.launch({ headless: true });
    }
    return this.browser;
  }

  async close(): Promise<void> {
    if (this.browser) {
      await this.browser.close();
      this.browser = null;
    }
  }

  async fetchFromSource(source: HtmlSource): Promise<Article[]> {
    const browser = await this.getBrowser();
    const page = await browser.newPage();

    try {
      console.log(`Fetching HTML (Playwright): ${source.url}`);

      await page.goto(source.url, {
        timeout: this.timeout,
        waitUntil: 'networkidle',
      });

      const selector = source.selector || source.link_selector || 'a';
      const elements = await page.$$(selector);
      const articles: Article[] = [];

      for (let i = 0; i < Math.min(elements.length, 50); i++) {
        try {
          const el = elements[i];

          let title = '';
          let link = '';

          if (source.title_selector) {
            title = await el.$eval(source.title_selector, (e) => e.textContent?.trim() || '').catch(() => '');
          } else {
            title = (await el.textContent())?.trim() || '';
          }

          if (source.link_selector) {
            link = await el.$eval(source.link_selector, (e) => e.getAttribute('href') || '').catch(() => '');
          } else {
            link = await el.evaluate((e) => {
              const a = e.closest('a') ?? e.querySelector('a');
              return a?.getAttribute('href') || '';
            }).catch(() => '');
          }

          if (!title || !link) continue;

          // Handle relative URLs
          if (link.startsWith('/')) {
            const urlObj = new URL(source.url);
            link = `${urlObj.origin}${link}`;
          } else if (link.startsWith('./') || link.startsWith('../')) {
            link = new URL(link, source.url).href;
          }

          const content = source.content_selector
            ? await el.$eval(source.content_selector, (e) => e.textContent?.trim() || '').catch(() => '')
            : '';

          articles.push({
            title,
            link,
            content: content || '',
            summary: content || '',
            category: source.category,
            source: source.name,
          });
        } catch (err) {
          console.warn(`Failed to parse article ${i}:`, err);
        }
      }

      console.log(`Fetched ${articles.length} articles from ${source.url}`);
      return articles;

    } catch (error) {
      console.error(`Failed to fetch HTML from ${source.url}:`, error);
      return [];
    } finally {
      await page.close();
    }
  }
}
```

**Step 2: 构建验证（类型检查）**

```bash
cd /Users/yuminghao/conductor/workspaces/ai-news/auckland
npm run build 2>&1 | tail -5
```

Expected: `Successfully compiled 27 files with Babel` 且 `tsc --noEmit` 零错误

**Step 3: Commit**

```bash
git add src/agents/daily-reporter/fetchers/html-fetcher.ts
git commit -m "feat: replace axios+jsdom with Playwright in HTMLFetcher"
```

---

### Task 3: 在 DailyReporter 中关闭 Browser 实例 + 启用 HTML 源

**Files:**
- Modify: `src/agents/daily-reporter/index.ts`（在 `generateDailyReport` 末尾加 `close()`）
- Modify: `config/sources.yaml`（将 5 个 HTML 源的 `enabled` 改为 `true`）

**Step 1: 在 DailyReporter 中关闭 browser**

在 `src/agents/daily-reporter/index.ts` 的 `fetchArticles()` 方法调用之后（`generateDailyReport` 的 try 块末尾），添加：

```typescript
// 关闭 Playwright browser（复用实例，用完即关）
await this.htmlFetcher.close();
```

**Step 2: 启用 HTML 源**

在 `config/sources.yaml` 中，将所有 `html_sources` 条目的 `enabled: false` 改为 `enabled: true`。

**Step 3: 端到端冒烟测试**

```bash
cd /Users/yuminghao/conductor/workspaces/ai-news/auckland
npm run build && node dist/main.js daily --no-summarize 2>&1 | grep -E "(Fetching HTML|Fetched [0-9]+ articles from|Filtered to|After per-source)"
```

Expected:
- 5 行 `Fetching HTML (Playwright): https://...`
- 每个源 `Fetched N articles from ...`（N > 0 表示成功）
- `Filtered to X articles` 数量增加（相比只有 RSS 源时的 12 篇）

**Step 4: Commit**

```bash
git add src/agents/daily-reporter/index.ts config/sources.yaml
git commit -m "feat: enable HTML sources with Playwright fetcher"
```

---

## 验收标准

1. `npm run build` 零错误、零警告
2. `node dist/main.js daily --no-summarize` 运行时，5 个 HTML 源不再报 `Failed to fetch` 错误
3. 至少 1 个 HTML 源能抓到 > 0 篇文章（网站内容决定，selector 可能需要微调）
4. `DailyReporter` 调用结束后 browser 实例被正确关闭（无僵尸进程）

## 注意事项

- `waitUntil: 'networkidle'` 会等待网络请求静默 500ms，超时默认 30s；如果某个 SPA 加载慢可调大 `timeout`
- Selector 是否准确取决于实际页面 DOM，部分站点可能需要在 Task 3 验收后微调 `config/sources.yaml` 的 selector
- `playwright` 体积较大（~60MB），`chromium` 二进制 ~150MB，首次 `npx playwright install chromium` 需要网络下载
