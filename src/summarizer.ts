import OpenAI from 'openai';
import type { Article, SummarizedArticle } from './types/index.js';

export class Summarizer {
  private openai: OpenAI;
  private model: string;
  private maxRetries: number;
  private retryDelay: number;

  constructor(apiKey: string, baseUrl: string = 'https://openrouter.ai/api/v1', config?: { maxRetries?: number; retryDelay?: number; model?: string }) {
    this.openai = new OpenAI({
      apiKey: apiKey,
      baseURL: baseUrl,
    });
    this.model = config?.model || process.env.OPENROUTER_MODEL || 'anthropic/claude-sonnet-4-20250514';
    this.maxRetries = config?.maxRetries || 3;
    this.retryDelay = config?.retryDelay || 1000;
  }

  private async sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private async generateSummaryWithRetry(prompt: string): Promise<string> {
    let lastError: any;

    for (let attempt = 0; attempt < this.maxRetries; attempt++) {
      try {
        await this.sleep(attempt * this.retryDelay);

        const response = await this.openai.chat.completions.create({
          model: this.model,
          messages: [
            {
              role: 'user',
              content: prompt
            }
          ],
          max_tokens: 300,
          temperature: 0.3
        });

        const summary = response.choices[0]?.message?.content;
        if (!summary) {
          throw new Error('Empty summary generated');
        }

        return summary.trim();

      } catch (error) {
        console.warn(`Summary attempt ${attempt + 1} failed:`, error);
        lastError = error;

        if (attempt < this.maxRetries - 1) {
          await this.sleep(2000 * (attempt + 1));
        }
      }
    }

    throw lastError || new Error('All summarization attempts failed');
  }

  async summarizeArticle(article: Article): Promise<SummarizedArticle | null> {
    try {
      const prompt = this.buildSummaryPrompt(article);

      const summary = await this.generateSummaryWithRetry(prompt);

      if (!summary || summary.length < 50) {
        console.warn(`Summary too short for: ${article.title.substring(0, 50)}...`);
        return null;
      }

      const qualityScore = this.estimateQuality(summary);

      return {
        ...article,
        summary,
        summarized: true,
        summaryQuality: qualityScore
      };

    } catch (error) {
      console.error('Error summarizing article:', error);

      return {
        ...article,
        summary: article.content || article.summary || '',
        summarized: false,
        summaryQuality: 0.1
      };
    }
  }

  async summarizeBatch(articles: Article[]): Promise<SummarizedArticle[]> {
    const results: SummarizedArticle[] = [];

    // Process all articles (upstream already limits per source)
    for (let i = 0; i < articles.length; i++) {
      console.log(`Summarizing article ${i + 1}/${articles.length}`);

      try {
        const article = articles[i];
        const summarized = await this.summarizeArticle(article);
        if (summarized) {
          results.push(summarized);
        } else {
          results.push({
            ...article,
            summary: '',
            summarized: false,
            summaryQuality: 0
          });
        }
      } catch (error) {
        console.error(`Failed to summarize article ${i}:`, error);
      }
    }

    return results;
  }

  private buildSummaryPrompt(article: Article): string {
    const content = article.content || article.summary || '';

    return `Summarize the following article in ${this.getTargetLanguage()}:

Title: ${article.title}
Content: ${content.substring(0, 4000)}

Please provide a concise summary that captures:
1. Main topic and key points
2. Significant insights or findings
3. Practical implications if any

Summary (80-200 words):`;
  }

  private getTargetLanguage(): string {
    const lang = process.env.SUMMARY_LANGUAGE || 'Chinese';
    return lang === 'Chinese' ? 'Chinese' : lang;
  }

  private estimateQuality(summary: string): number {
    const lengthScore = Math.min(summary.length / 200, 1);
    const structureScore = summary.includes('\n') ? 0.8 : 0.3;
    const contentScore = summary.length > 50 ? 0.9 : 0.1;

    return Math.round(((lengthScore + structureScore + contentScore) / 3) * 100) / 100;
  }
}
