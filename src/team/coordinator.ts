import { AgentResult } from '../types/index.js';
import { DailyReporter } from '../agents/daily-reporter.js';
import { ResearchManager } from '../agents/research-manager.js';
import { ThinkingSystem } from '../agents/thinking-system.js';
import { HomepageBuilder } from '../agents/homepage-builder.js';
import { HarnessController } from '../harness/controller.js';
import { Logger } from '../utils/config.js';

export interface TaskOptions {
  daily?: {
    date?: Date;
    noSummarize?: boolean;
    verbose?: boolean;
  };
  research?: any;
  thinking?: any;
  homepage?: {
    optimize?: boolean;
  };
  harness?: {
    file?: string;
  };
}

export class TeamCoordinator {
  private logger: Logger;
  private agents = {
    daily: new DailyReporter(),
    research: new ResearchManager(),
    thinking: new ThinkingSystem(),
    homepage: new HomepageBuilder(),
    harness: HarnessController.getInstance(),
  };

  constructor() {
    this.logger = new Logger('TeamCoordinator');
  }

  async executeAll(options?: TaskOptions): Promise<AgentResult> {
    const results: Record<string, AgentResult> = {};

    this.logger.log('Starting all agents execution...');

    try {
      // Execute agents in order
      results.daily = await this.executeDaily(options?.daily);
      results.research = await this.executeResearch(options?.research);
      results.thinking = await this.executeThinking(options?.thinking);
      results.homepage = await this.executeHomepage(options?.homepage);

      // Optional harness check
      if (options?.harness?.file) {
        results.harness = this.executeHarnessCheck(options.harness.file);
      }

      this.logger.log('All agents executed successfully');

      return {
        success: true,
        message: 'All agents executed successfully',
        data: results,
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      this.logger.error('Failed to execute all agents:', error instanceof Error ? error : new Error(errorMessage));

      return {
        success: false,
        message: `Some agents failed: ${errorMessage}`,
        data: results,
      };
    }
  }

  async executeDaily(options?: TaskOptions['daily']): Promise<AgentResult> {
    try {
      const filePath = await this.agents.daily.generateDailyReport(
        options?.date,
        {
          noSummarize: options?.noSummarize,
          verbose: options?.verbose,
        }
      );

      return {
        success: true,
        message: 'Daily report generated',
        data: { filePath },
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      return {
        success: false,
        message: `Daily reporter failed: ${errorMessage}`,
      };
    }
  }

  async executeResearch(action: string, options?: any): Promise<AgentResult> {
    try {
      switch (action) {
        case 'add':
          return await this.agents.research.addReport(options.file, options.category, options);
        case 'stats':
          return await this.agents.research.getStats(options.category);
        case 'list':
          return await this.agents.research.listReports(options.category);
        case 'search':
          return await this.agents.research.searchReports(options.query);
        default:
          return {
            success: false,
            message: `Unknown research action: ${action}`,
          };
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      return {
        success: false,
        message: `Research manager failed: ${errorMessage}`,
      };
    }
  }

  async executeThinking(action: string, options?: any): Promise<AgentResult> {
    try {
      switch (action) {
        case 'create':
          return await this.agents.thinking.createModel({
            topic: options.topic,
            file: options.file,
            modelType: options.modelType,
            tags: options.tags,
          });
        case 'list':
          return await this.agents.thinking.listModels({
            type: options?.type,
            tags: options?.tags,
          });
        case 'get':
          return await this.agents.thinking.getModel(options.id);
        case 'search':
          return await this.agents.thinking.searchModels(options.query);
        case 'relationships':
          return await this.agents.thinking.getRelationships(options.id);
        default:
          return {
            success: false,
            message: `Unknown thinking action: ${action}`,
          };
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      return {
        success: false,
        message: `Thinking system failed: ${errorMessage}`,
      };
    }
  }

  async executeHomepage(options?: TaskOptions['homepage']): Promise<AgentResult> {
    try {
      return await this.agents.homepage.buildHomepage(options);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      return {
        success: false,
        message: `Homepage builder failed: ${errorMessage}`,
      };
    }
  }

  executeHarnessCheck(filePath: string): AgentResult {
    try {
      const result = this.agents.harness.checkFile(filePath);

      return {
        success: result.valid,
        message: result.valid ? 'File validation passed' : 'File validation failed',
        data: result,
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      return {
        success: false,
        message: `Harness check failed: ${errorMessage}`,
      };
    }
  }

  async getStats(): Promise<AgentResult> {
    try {
      const results = {
        daily: await this.agents.daily.getStats(),
        research: await this.agents.research.getStats(),
        thinking: await this.agents.thinking.listModels(),
        homepage: await this.agents.homepage.getStats(),
      };

      return {
        success: true,
        message: 'Stats collected',
        data: results,
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      return {
        success: false,
        message: `Failed to collect stats: ${errorMessage}`,
      };
    }
  }
}