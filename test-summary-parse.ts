
import { RSSFetcher } from './src/agents/daily-reporter/fetchers/rss-fetcher.js';
import { Summarizer } from './src/agents/daily-reporter/summarizer.js';
import { loadConfig } from './src/utils/config.js';

console.log('Testing GitHub Trending summary parsing...\n');

// 先获取GitHub Trending的文章
async function test() {
  const fetcher = new RSSFetcher(60000);
  const articles = await fetcher.fetchFromURL(
    'https://mshibanami.github.io/GitHubTrendingRSS/daily/all.xml',
    'GitHub Trending Daily',
    '开源项目',
    undefined,
    1
  );

  console.log('Fetched article:', articles[0]?.title);
  console.log('Article summary/content:', articles[0]?.summary?.substring(0, 200), '...\n');

  // 如果有API key，测试摘要生成
  const config = loadConfig();
  if (config.llm?.apiKey) {
    console.log('Testing summarizer...');
    const summarizer = new Summarizer(config.llm.apiKey, config.llm.baseUrl, {
      model: config.llm.model
    });

    const result = await summarizer.summarizeArticle(articles[0]);
    console.log('Raw summary result:', JSON.stringify(result, null, 2));
  }
}

test().catch(console.error);
