
import { RSSFetcher } from './src/agents/daily-reporter/fetchers/rss-fetcher.js';

console.log('Testing Baoyu RSS feed...');

async function test() {
  try {
    const fetcher = new RSSFetcher(60000);
    console.log('Starting fetch...');
    const articles = await fetcher.fetchFromURL(
      'https://s.baoyu.io/feed.xml',
      '宝玉',
      '综合资讯'
    );
    console.log('Fetched articles:', articles.length);
    console.log();
    if (articles.length > 0) {
      console.log('Articles:');
      articles.forEach((article, index) => {
        console.log(`${index + 1}. ${article.title}`);
        console.log(`   Link: ${article.link}`);
        if (article.published) {
          console.log(`   Date: ${article.published}`);
        }
        console.log();
      });
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

test();
