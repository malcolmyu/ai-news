# Add OpenAI Engineering RSS Source with Category Filtering

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add OpenAI news RSS source (https://openai.com/news/rss.xml) to daily reporter, extracting only articles with category "Engineering".

**Architecture:** Modify RSSFetcher to support item-level category parsing and filtering based on config-specified filter_categories. Add new RSS source config for OpenAI Engineering.

**Tech Stack:** TypeScript, xml2js, axios, existing RSSFetcher infrastructure

---

### Task 1: Modify RSSFetcher to parse item categories

**Files:**
- Modify: `src/agents/daily-reporter/fetchers/rss-fetcher.ts`

**Step 1: Add category parsing to parseRSSItem**

Read the file to see current implementation, then modify to extract categories from `<category>` elements.

**Step 2: Build to verify no TypeScript errors**

```bash
cd /Users/yuminghao/conductor/workspaces/ai-news/auckland
npm run build 2>&1 | tail -5
```

Expected: `Successfully compiled 27 files with Babel` and `tsc --noEmit` zero errors

**Step 3: Commit**

```bash
git add src/agents/daily-reporter/fetchers/rss-fetcher.ts
git commit -m "feat: parse categories from RSS items"
```

---

### Task 2: Add category filtering support to RSSFetcher

**Files:**
- Modify: `src/agents/daily-reporter/fetchers/rss-fetcher.ts`
- Modify: `src/types/index.ts` (add filter_categories to RSS source interface)

**Step 1: Add filter_categories config option**

Modify the fetcher to accept optional `filter_categories` and only return items matching these categories.

**Step 2: Build to verify no TypeScript errors**

```bash
cd /Users/yuminghao/conductor/workspaces/ai-news/auckland
npm run build 2>&1 | tail -5
```

Expected: `Successfully compiled 27 files with Babel` and `tsc --noEmit` zero errors

**Step 3: Commit**

```bash
git add src/agents/daily-reporter/fetchers/rss-fetcher.ts src/types/index.ts
git commit -m "feat: add category filtering to RSSFetcher"
```

---

### Task 3: Add OpenAI Engineering RSS source to config

**Files:**
- Modify: `config/sources.yaml`

**Step 1: Add OpenAI RSS source configuration**

Add to rss_sources section:
```yaml
  - name: "OpenAI Engineering"
    url: "https://openai.com/news/rss.xml"
    description: "OpenAI Engineering blog via RSS"
    category: "AI框架"
    enabled: true
    max_articles: 3
    filter_categories: ["Engineering"]
```

**Step 2: Verify YAML syntax**

```bash
python3 -c "import yaml; yaml.safe_load(open('config/sources.yaml'))" && echo "YAML syntax valid"
```

Expected: Output "YAML syntax valid"

**Step 3: Commit**

```bash
git add config/sources.yaml
git commit -m "feat: add OpenAI Engineering RSS source"
```

---

### Task 4: Test RSSFetcher with OpenAI Engineering source

**Files:**
- Run: `tests/rss-fetcher.test.ts` (create if doesn't exist)

**Step 1: Create integration test**

```typescript
import { RSSFetcher } from '../src/agents/daily-reporter/fetchers/rss-fetcher';

describe('RSSFetcher', () => {
  it('should fetch articles from OpenAI RSS with Engineering category filter', async () => {
    const fetcher = new RSSFetcher();
    const articles = await fetcher.fetchFromURL(
      'https://openai.com/news/rss.xml',
      'OpenAI Engineering',
      'AI框架',
      ['Engineering']
    );

    expect(articles.length).toBeGreaterThan(0);
    expect(articles.length).toBeLessThanOrEqual(3); // max_articles: 3

    // Verify all articles have Engineering category
    for (const article of articles) {
      expect(article.categories).toContain('Engineering');
    }
  }, 30000); // 30s timeout for network request
});
```

**Step 2: Run test**

```bash
npm run build && npm test tests/rss-fetcher.test.ts
```

Expected: Test passes, showing "Fetched 1-3 articles" and no errors

**Step 3: Commit test**

```bash
git add tests/rss-fetcher.test.ts
git commit -m "test: add OpenAI Engineering RSS integration test"
```

---

### Task 5: End-to-end smoke test with daily reporter

**Files:**
- Verify via CLI: `dist/main.js`

**Step 1: Build and run daily report**

```bash
cd /Users/yuminghao/conductor/workspaces/ai-news/auckland
npm run build && node dist/main.js daily --no-summarize 2>&1 | grep -E "(Fetching RSS|Fetched [0-9]+ articles from|Filtered to|After per-source|OpenAI Engineering)"
```

Expected output pattern:
- `Fetching RSS: https://openai.com/news/rss.xml`
- `Fetched X articles from https://openai.com/news/rss.xml` (X >= 1, X <= 3)
- `Filtered to Y articles` (Y should increase compared to before)

**Step 2: Verify articles in output**

```bash
ls -la docs/daily/ai-news-$(date +%Y-%m-%d).html | head -20
```

Expected: HTML file exists and contains articles from OpenAI Engineering

**Step 3: Commit success log**

```bash
git add docs/daily/ai-news-$(date +%Y-%m-%d).html
git commit -m "feat: enable OpenAI Engineering RSS source with daily report output"
```

---

## Verification Steps

### Verify category filtering works

Test with a mock RSS feed locally:

```typescript
import { RSSFetcher } from '../src/agents/daily-reporter/fetchers/rss-fetcher';

const mockRSS = `
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>OpenAI News</title>
    <item>
      <title>AI Research Breakthrough</title>
      <link>https://openai.com/research</link>
      <category>Research</category>
    </item>
    <item>
      <title>Engineering Scaling System</title>
      <link>https://openai.com/engineering</link>
      <category>Engineering</category>
    </item>
  </channel>
</rss>`;

// Should only return the Engineering article
const filteredArticles = await fetcher.parseRSSFeed(mockRSS, ['Engineering']);
expect(filteredArticles.length).toBe(1);
expect(filteredArticles[0].title).toBe('Engineering Scaling System');
```

**Run:** `npm test tests/rss-fetcher.test.ts -- --testNamePattern="category filter"`

Expected: Only Engineering articles returned

---

## Success Criteria

1. ✅ RSSFetcher parses `<category>` elements from RSS items
2. ✅ RSSFetcher filters articles based on `filter_categories` config
3. ✅ OpenAI Engineering RSS source configured with category filter
4. ✅ Build passes without TypeScript errors
5. ✅ Integration test fetches 1-3 Engineering articles from OpenAI RSS
6. ✅ E2E smoke test shows OpenAI Engineering in daily report output
7. ✅ Articles appear in generated HTML with correct category "AI框架"
8. ✅ No regressions in existing RSS sources

---

## Notes

- OpenAI RSS feed has multiple categories: Research, Engineering, Safety, etc.
- filter_categories supports multiple values: `["Engineering", "Safety"]` would fetch both
- If filter_categories is not specified or empty, all articles are included (backward compatible)
- RSS sources can now use either or both of:
  - `category`: assigns a fixed category to all articles (existing behavior)
  - `filter_categories`: only includes items matching these RSS-level categories (new feature)