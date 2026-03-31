#!/usr/bin/env node

import { Command } from 'commander';
import { format, subDays } from 'date-fns';
import * as child_process from 'child_process';
import { TeamCoordinator } from './team/coordinator.js';
import { HarnessController } from './harness/controller.js';
import { DailyReporter } from './agents/daily-reporter.js';
import { ResearchManager } from './agents/research-manager.js';
import { ThinkingSystem } from './agents/thinking-system.js';
import { HomepageBuilder } from './agents/homepage-builder.js';
import { Logger } from './utils/config.js';

const program = new Command();
const logger = new Logger('CLI');

program
  .name('growth-website')
  .description('Growth Website System - 个人自主成长网站系统')
  .version('1.0.0');

// Daily reporter commands
const dailyCmd = program
  .command('daily')
  .description('Generate AI daily news report');

dailyCmd
  .option('-d, --date <date>', 'Date (YYYY-MM-DD)', format(new Date(), 'yyyy-MM-dd'))
  .option('--no-summarize', 'Skip AI summarization')
  .option('-o, --output <path>', 'Output file path')
  .option('-v, --verbose', 'Enable verbose logging')
  .action(async (options) => {
    try {
      console.log('🤖 Starting Daily Reporter...');
      const stdout = child_process.execSync('npm run build', { stdio: 'inherit' });

      const coordinator = new TeamCoordinator();
      const relativeDate = options.date === 'yesterday' ? subDays(new Date(), 1) : new Date(options.date);
      const filePath = await coordinator.executeDaily({
        date: relativeDate,
        noSummarize: options.noSummarize,
        verbose: options.verbose,
      });

      console.log('✅ Daily report generated:', filePath);
    } catch (error) {
      console.error('❌ Error:', error);
      process.exit(1);
    }
  });

// Research manager commands
const researchCmd = program
  .command('research')
  .description('Manage research reports');

researchCmd
  .command('add')
  .description('Add research report')
  .requiredOption('-f, --file <path>', 'HTML file path')
  .requiredOption('-c, --category <category>', 'Report category')
  .option('-t, --tags <tags>', 'Comma-separated tags')
  .action(async (options) => {
    try {
      console.log('📊 Adding research report...');
      const coordinator = new TeamCoordinator();
      const result = await coordinator.executeResearch('add', {
        file: options.file,
        category: options.category,
        tags: options.tags ? options.tags.split(',') : [],
      });

      if (result.success) {
        console.log('✅ Report added:', result.message);
      } else {
        console.error('❌ Error:', result.message);
      }
    } catch (error) {
      console.error('❌ Error:', error);
      process.exit(1);
    }
  });

researchCmd
  .command('stats')
  .description('Show research stats')
  .option('-c, --category <category>', 'Filter by category')
  .action(async (options) => {
    try {
      console.log('📈 Research stats:');
      const coordinator = new TeamCoordinator();
      const result = await coordinator.executeResearch('stats', { category: options.category });

      if (result.success && result.data) {
        console.log('✅ Stats:', result.data);
      } else {
        console.error('❌ Error:', result.message);
      }
    } catch (error) {
      console.error('❌ Error:', error);
      process.exit(1);
    }
  });

// Thinking system commands
const thinkingCmd = program
  .command('thinking')
  .description('Manage thinking models');

thinkingCmd
  .command('create')
  .description('Create thinking model')
  .requiredOption('-t, --topic <topic>', 'Model topic')
  .option('-f, --file <path>', 'Content file path')
  .option('--model-type <type>', 'Model type (framework, methodology, pattern, concept)')
  .option('--tags <tags>', 'Comma-separated tags')
  .action(async (options) => {
    try {
      console.log('💭 Creating thinking model...');
      const coordinator = new TeamCoordinator();
      const result = await coordinator.executeThinking('create', {
        topic: options.topic,
        file: options.file,
        modelType: options.modelType,
        tags: options.tags ? options.tags.split(',') : [],
      });

      if (result.success) {
        console.log('✅ Model created:', result.message);
      } else {
        console.error('❌ Error:', result.message);
      }
    } catch (error) {
      console.error('❌ Error:', error);
      process.exit(1);
    }
  });

// Homepage commands
const homepageCmd = program
  .command('homepage')
  .description('Build homepage');

homepageCmd
  .command('build')
  .description('Build homepage')
  .option('--optimize', 'Enable optimization')
  .action(async (options) => {
    try {
      console.log('🏠 Building homepage...');
      const coordinator = new TeamCoordinator();
      const result = await coordinator.executeHomepage({ optimize: options.optimize });

      if (result.success) {
        console.log('✅ Homepage built:', result.message);
      } else {
        console.error('❌ Error:', result.message);
      }
    } catch (error) {
      console.error('❌ Error:', error);
      process.exit(1);
    }
  });

// Stats command
program
  .command('stats')
  .description('Show system statistics')
  .option('--json', 'Output as JSON')
  .option('--agent <agent>', 'Show specific agent stats')
  .action(async (options) => {
    try {
      console.log('📊 Collecting stats...');
      const coordinator = new TeamCoordinator();
      const result = await coordinator.getStats();

      if (result.success && result.data) {
        if (options.json) {
          console.log(JSON.stringify(result.data, null, 2));
        } else if (options.agent) {
          console.log(`✅ ${options.agent} stats:`, result.data[options.agent]);
        } else {
          console.log('✅ System stats:');
          console.log(JSON.stringify(result.data, null, 2));
        }
      } else {
        console.error('❌ Error:', result.message);
      }
    } catch (error) {
      console.error('❌ Error:', error);
      process.exit(1);
    }
  });

// Harness commands
const harnessCmd = program
  .command('harness')
  .description('Content quality control');

harnessCmd
  .command('check')
  .description('Check file quality')
  .requiredOption('-f, --file <path>', 'File to check')
  .action(async (options) => {
    try {
      console.log('🔍 Checking file quality...');
      const coordinator = new TeamCoordinator();
      const result = coordinator.executeHarnessCheck(options.file);

      if (result.success) {
        console.log('✅ File passed validation');
      } else {
        console.error('❌ File failed validation:', result.message);
      }

      if (result.data) {
        console.log('📋 Validation details:', result.data);
      }
    } catch (error) {
      console.error('❌ Error:', error);
      process.exit(1);
    }
  });

harnessCmd
  .command('info')
  .description('Show harness information')
  .action(async () => {
    try {
      const harness = HarnessController.getInstance();
      await harness.initialize();
      const info = harness.getInfo();
      console.log('🔧 Harness Info:', info);
    } catch (error) {
      console.error('❌ Error:', error);
      process.exit(1);
    }
  });

// All command
program
  .command('all')
  .description('Execute all agents')
  .option('--push', 'Push changes to git after execution')
  .action(async (options) => {
    try {
      console.log('🚀 Running all agents...');
      const coordinator = new TeamCoordinator();
      const result = await coordinator.executeAll();

      if (result.success) {
        console.log('✅ All agents completed successfully');

        if (options.push) {
          console.log('🔄 Pushing changes...');
          // Execute npm run git-push
          const { execSync } = await import('child_process');
          execSync('npm run git-push', { stdio: 'inherit' });
        }
      } else {
        console.error('⚠️  Some agents completed with warnings:', result.message);
      }
    } catch (error) {
      console.error('❌ Error:', error);
      process.exit(1);
    }
  });

// Git commands
const gitCmd = program
  .command('git')
  .description('Git operations');

gitCmd
  .command('push')
  .description('Push changes to git')
  .argument('[message]', 'Commit message')
  .action(async (message) => {
    try {
      console.log('🔄 Pushing to git...');
      const { execSync } = await import('child_process');

      const commitMessage = message || `Update: ${new Date().toISOString()}`;

      execSync('git add .', { stdio: 'inherit' });
      try {
        execSync(`git commit -m "${commitMessage}"`, { stdio: 'inherit' });
      } catch (e) {
        console.log('⚠️  No changes to commit');
      }
      execSync('git push', { stdio: 'inherit' });
      console.log('✅ Changes pushed successfully');
    } catch (error) {
      console.error('❌ Error:', error);
      process.exit(1);
    }
  });

program.parse();
