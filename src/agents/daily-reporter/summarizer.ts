import OpenAI from 'openai';
import * as fs from 'fs';
import * as path from 'path';
import type { Article, SummarizedArticle, StructuredSummary } from '../../types/index.js';

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
    this.model =
      config?.model ||
      process.env.ANTHROPIC_MODEL ||
      process.env.OPENROUTER_MODEL ||
      'anthropic/claude-sonnet-4-20250514';
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

        const sysPromptPath = path.join(process.cwd(), '.claude-skills/content-harness/SKILL.md');
        const systemPrompt = fs.existsSync(sysPromptPath) ? fs.readFileSync(sysPromptPath, 'utf8') : 'You are a helpful AI assistant. Summarize the following article.';

        const response = await this.openai.chat.completions.create({
          model: this.model,
          messages: [
            {
              role: 'system',
              content: systemPrompt
            },
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

  // 判断标题是否主要包含英文
  private isEnglishTitle(title: string): boolean {
    // 统计中文字符数量
    const chineseCount = (title.match(/[\u4e00-\u9fa5]/g) || []).length;
    // 统计英文和数字字符数量
    const englishCount = (title.match(/[a-zA-Z0-9]/g) || []).length;

    // 如果英文数字字符数量远多于中文字符，认为是英文标题
    return englishCount > chineseCount * 2;
  }

  async summarizeArticle(article: Article): Promise<SummarizedArticle | null> {
    try {
      // 处理英文标题翻译
      let translatedTitle = article.title;

      // 只对非 GitHub Trending 的自然语言标题进行翻译
      const isGitHubTrending = article.source === 'GitHub Trending Daily';
      const shouldTranslate = this.isEnglishTitle(article.title) && !isGitHubTrending;

      if (shouldTranslate) {
        try {
          console.log(`Translating English title: ${article.title}`);
          const translatePrompt = `Translate the following article title from English to Chinese. Return only the translated title, no other text: "${article.title}"`;
          const translateResult = await this.generateSummaryWithRetry(translatePrompt);
          if (translateResult && translateResult.trim() && translateResult.trim().length > 5) {
            translatedTitle = translateResult.trim();
            console.log(`Translated to: ${translatedTitle}`);
          }
        } catch (translateError) {
          console.warn(`Failed to translate title: ${article.title}`, translateError);
        }
      }

      const prompt = this.buildSummaryPrompt(article, translatedTitle);

      const summaryResult = await this.generateSummaryWithRetry(prompt);

      let structuredSummary: StructuredSummary | undefined;
      let plainSummary: string;

      // Try to parse structured JSON summary
      try {
        // 提取可能包含在文本中的JSON部分
        let jsonStr = summaryResult;
        const startIndex = jsonStr.indexOf('{');
        const endIndex = jsonStr.lastIndexOf('}');
        if (startIndex !== -1 && endIndex !== -1 && endIndex > startIndex) {
          jsonStr = jsonStr.substring(startIndex, endIndex + 1);
        }

        // 更简单的方法：只尝试解析，如果失败，手动提取字段
        let parsed: any = {};
        try {
          parsed = JSON.parse(jsonStr);
        } catch (jsonError) {
          // JSON解析失败，尝试手动解析摘要
          console.warn('JSON parsing failed, trying manual extraction');
          // 尝试提取summary字段
          const summaryMatch = jsonStr.match(/"summary":\s*"([^"]*)/);
          if (summaryMatch && summaryMatch[1]) {
            parsed.summary = summaryMatch[1];
          }
        }

        // 检查是否有summary字段
        if (parsed.summary) {
          structuredSummary = {
            summary: parsed.summary || '',
            keyInsights: Array.isArray(parsed.keyInsights) ? parsed.keyInsights : [],
            relatedModels: Array.isArray(parsed.relatedModels) ? parsed.relatedModels : [],
            newModels: Array.isArray(parsed.newModels) ? parsed.newModels : []
          };
          plainSummary = structuredSummary.summary;
        } else {
          // 没有有效的summary，使用普通文本
          throw new Error('No valid summary field found');
        }
      } catch (parseError) {
        // If JSON parsing fails, treat as plain text
        console.warn('Failed to parse structured summary, using plain text');
        plainSummary = summaryResult;
      }

      if (!plainSummary || plainSummary.length < 50) {
        console.warn(`Summary too short for: ${article.title.substring(0, 50)}...`);
        return null;
      }

      const qualityScore = this.estimateQuality(plainSummary);

      const result: SummarizedArticle = {
        ...article,
        title: translatedTitle,  // 使用翻译后的标题
        summary: plainSummary,
        summarized: true,
        summaryQuality: qualityScore
      };

      if (structuredSummary) {
        result.structuredSummary = structuredSummary;
      }

      return result;

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

  private buildSummaryPrompt(article: Article, translatedTitle?: string): string {
    const content = article.content || article.summary || '';
    const titleToUse = translatedTitle || article.title;

    return `Summarize the following article in ${this.getTargetLanguage()}:

Title: ${titleToUse}
Content: ${content.substring(0, 4000)}

Please provide a structured summary in JSON format with the following fields:
1. summary: A concise overall summary of the article (80-200 words)
2. keyInsights: 3-5 core points or key insights from the article
3. relatedModels: Any existing thinking models, frameworks, or concepts that this article relates to
4. newModels: Any new thinking models or approaches introduced or suggested in this article

Return ONLY valid JSON.`;
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
