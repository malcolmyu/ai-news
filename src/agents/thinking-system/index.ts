import * as fs from 'fs';
import * as path from 'path';
import { marked } from 'marked';
import { ThinkingModel, ModelRelationship, AgentResult, ThinkingCategory } from '../../types/index.js';
import { readJSONFile, writeJSONFile, Logger } from '../../utils/config.js';
import { ThinkingGenerator } from './generator.js';
import { HomepageBuilder } from '../homepage-builder/index.js';

interface ModelIndex {
  models: Record<string, Omit<ThinkingModel, 'id'>>;
  relationships: ModelRelationship[];
}

export class ThinkingSystem {
  private logger: Logger;
  private dataDir: string;

  constructor() {
    this.logger = new Logger('ThinkingSystem');
    this.dataDir = path.join(process.cwd(), 'data', 'thinking');
    this.ensureDataDir();
  }

  private ensureDataDir(): void {
    const dirs = [
      this.dataDir,
      path.join(this.dataDir, 'relationships'),
      path.join(this.dataDir, 'versions'),
    ];

    for (const dir of dirs) {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    }
  }

  async createModel(input: {
    topic: string;
    file?: string;
    content?: string;
    modelType?: string;
    tags?: string[];
  }): Promise<AgentResult> {
    try {
      const { topic, file, content, modelType, tags } = input;

      let modelContent = content || '';
      let fileName = '';

      if (file && !content) {
        if (!fs.existsSync(file)) {
          return {
            success: false,
            message: `File not found: ${file}`,
          };
        }

        modelContent = fs.readFileSync(file, 'utf8');
        fileName = path.basename(file);
      }

      if (!modelContent.trim()) {
        return {
          success: false,
          message: 'Model content cannot be empty',
        };
      }

      const id = this.generateModelId(topic);
      const timestamp = new Date().toISOString();

      const model: ThinkingModel = {
        id,
        topic,
        type: (modelType as any) || 'framework',
        content: modelContent,
        tags: tags || [],
        createdDate: timestamp,
        updatedDate: timestamp,
        version: 1,
      };

      // Save model content
      const modelFile = path.join(this.dataDir, 'models', `${id}.md`);
      fs.writeFileSync(modelFile, modelContent, 'utf8');

      // Update index
      const indexPath = path.join(this.dataDir, 'models.json');
      const index = this.loadIndex(indexPath);
      const { id: modelId, ...modelData } = model;
      index.models[modelId] = modelData;
      this.saveIndex(indexPath, index);

      // Analyze and create relationships
      await this.analyzeRelationships(model);

      this.logger.log(`Thinking model created: ${topic} (${modelType || 'framework'})`);

      // Regenerate static pages
      await this.regeneratePages();

      return {
        success: true,
        message: `Thinking model created: ${topic}`,
        data: model,
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      this.logger.error('Failed to create thinking model:', error instanceof Error ? error : new Error(errorMessage));

      return {
        success: false,
        message: `Failed to create thinking model: ${errorMessage}`,
      };
    }
  }

  async regeneratePages(): Promise<void> {
    try {
      this.logger.log('Regenerating thinking pages...');
      const seedPath = path.join(this.dataDir, 'seed-data.json');
      if (!fs.existsSync(seedPath)) return;

      const seedData = readJSONFile(seedPath);
      if (!seedData?.categories) return;

      const categories: ThinkingCategory[] = seedData.categories;
      const generator = new ThinkingGenerator();

      for (const category of categories) {
        generator.generateThinkingPage(category, categories);
      }

      this.logger.log('Rebuilding homepage...');
      const hpBuilder = new HomepageBuilder();
      await hpBuilder.buildHomepage();
    } catch (err) {
      this.logger.error('Failed to regenerate thinking pages', err as Error);
    }
  }

  private generateModelId(topic: string): string {
    const normalized = topic.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
    const timestamp = Date.now().toString(36);
    return `${normalized}-${timestamp}`;
  }

  private async analyzeRelationships(newModel: ThinkingModel): Promise<void> {
    try {
      const indexPath = path.join(this.dataDir, 'models.json');
      const index = this.loadIndex(indexPath);

      const relationships: ModelRelationship[] = [];
      const existingModels = Object.entries(index.models);

      for (const [id, existingModel] of existingModels) {
        const relatedness = this.calculateRelatedness(newModel, existingModel as ThinkingModel);

        if (relatedness > 0.3) {
          const relationship: ModelRelationship = {
            from: newModel.id,
            to: id,
            type: this.determineRelationshipType(relatedness),
            strength: relatedness,
          };
          relationships.push(relationship);
        }
      }

      // Save relationships
      const relationshipsFile = path.join(this.dataDir, 'relationships', `${newModel.id}.json`);
      writeJSONFile(relationshipsFile, relationships);
    } catch (error) {
      this.logger.warn('Failed to analyze relationships:', error instanceof Error ? error : undefined);
    }
  }

  private calculateRelatedness(model1: ThinkingModel, model2: ThinkingModel): number {
    // Calculate based on common words, tags, and topics
    const topic1Words = model1.topic.toLowerCase().split(/\s+/);
    const topic2Words = model2.topic.toLowerCase().split(/\s+/);

    const commonTopicWords = topic1Words.filter((word) => topic2Words.includes(word));
    const topicSimilarity = commonTopicWords.length / Math.min(topic1Words.length, topic2Words.length);

    const commonTags = model1.tags.filter((tag) => model2.tags.includes(tag));
    const tagSimilarity = model1.tags.length > 0 && model2.tags.length > 0
      ? commonTags.length / Math.min(model1.tags.length, model2.tags.length)
      : 0;

    // Extract key terms from content using simple heuristics
    const content1Words = model1.content.toLowerCase().match(/\b[a-z]{4,}\b/g) || [];
    const content2Words = model2.content.toLowerCase().match(/\b[a-z]{4,}\b/g) || [];

    const wordFreq1 = this.getWordFrequencies(content1Words);
    const wordFreq2 = this.getWordFrequencies(content2Words);

    const commonWords = Object.keys(wordFreq1).filter((word) => wordFreq2[word]);
    const contentSimilarity = commonWords.length / Math.min(Object.keys(wordFreq1).length || 1, Object.keys(wordFreq2).length || 1);

    // Weighted average
    return (topicSimilarity * 0.3 + tagSimilarity * 0.4 + contentSimilarity * 0.3);
  }

  private getWordFrequencies(words: string[]): Record<string, number> {
    const frequencies: Record<string, number> = {};

    for (const word of words) {
      frequencies[word] = (frequencies[word] || 0) + 1;
    }

    return frequencies;
  }

  private determineRelationshipType(strength: number): ModelRelationship['type'] {
    if (strength > 0.7) {
      return 'extends';
    } else if (strength > 0.5) {
      return 'implements';
    } else if (strength > 0.3) {
      return 'related';
    }
    return 'uses';
  }

  async getModel(id: string): Promise<AgentResult> {
    try {
      const indexPath = path.join(this.dataDir, 'models.json');
      const index = this.loadIndex(indexPath);

      const model = index.models[id];
      if (!model) {
        return {
          success: false,
          message: `Model not found: ${id}`,
        };
      }

      // Load full content
      const modelFile = path.join(this.dataDir, 'models', `${id}.md`);
      const content = fs.existsSync(modelFile) ? fs.readFileSync(modelFile, 'utf8') : model.content;

      const thinkingModel: ThinkingModel = {
        id,
        ...model,
        content,
      };

      return {
        success: true,
        data: thinkingModel,
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      return {
        success: false,
        message: `Failed to get model: ${errorMessage}`,
      };
    }
  }

  async listModels(options?: { type?: string; tags?: string[] }): Promise<AgentResult> {
    try {
      const indexPath = path.join(this.dataDir, 'models.json');
      const index = this.loadIndex(indexPath);

      let models = Object.entries(index.models).map(([id, data]) => ({ id, ...data })) as ThinkingModel[];

      if (options?.type) {
        models = models.filter((model) => model.type === (options.type as any));
      }

      if (options?.tags && options.tags.length > 0) {
        models = models.filter((model) => options.tags!.some((tag) => model.tags.includes(tag)));
      }

      models.sort((a, b) => new Date(b.updatedDate).getTime() - new Date(a.updatedDate).getTime());

      return {
        success: true,
        data: models,
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      return {
        success: false,
        message: `Failed to list models: ${errorMessage}`,
      };
    }
  }

  async searchModels(query: string): Promise<AgentResult> {
    try {
      const indexPath = path.join(this.dataDir, 'models.json');
      const index = this.loadIndex(indexPath);

      const models = Object.entries(index.models).map(([id, data]) => ({ id, ...data })) as ThinkingModel[];
      const lowerQuery = query.toLowerCase();

      const results = models.filter((model) =>
        model.topic.toLowerCase().includes(lowerQuery) ||
        model.content.toLowerCase().includes(lowerQuery) ||
        model.tags.some((tag) => tag.toLowerCase().includes(lowerQuery))
      );

      results.sort((a, b) => new Date(b.updatedDate).getTime() - new Date(a.updatedDate).getTime());

      return {
        success: true,
        data: results,
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      return {
        success: false,
        message: `Failed to search models: ${errorMessage}`,
      };
    }
  }

  async getRelationships(modelId: string): Promise<AgentResult> {
    try {
      const relationshipsFile = path.join(this.dataDir, 'relationships', `${modelId}.json`);

      if (!fs.existsSync(relationshipsFile)) {
        return {
          success: true,
          data: [],
        };
      }

      const relationships = readJSONFile(relationshipsFile) || [];

      return {
        success: true,
        data: relationships,
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      return {
        success: false,
        message: `Failed to get relationships: ${errorMessage}`,
      };
    }
  }

  private loadIndex(indexPath: string): ModelIndex {
    if (!fs.existsSync(indexPath)) {
      return { models: {}, relationships: [] };
    }

    const data = readJSONFile(indexPath);
    return {
      models: data?.models || {},
      relationships: data?.relationships || [],
    };
  }

  private saveIndex(indexPath: string, index: ModelIndex): void {
    writeJSONFile(indexPath, index);
  }
}
