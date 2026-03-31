#!/usr/bin/env node

import { Command } from 'commander';
import { format, subDays } from 'date-fns';
import { DailyReporter } from './agents/daily-reporter/index.js';
import { ResearchManager } from './agents/research-manager/index.js';
import { ThinkingSystem } from './agents/thinking-system/index.js';
import { HomepageBuilder } from './agents/homepage-builder/index.js';

const program = new Command();

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
      const reporter = new DailyReporter();
      const relativeDate = options.date === 'yesterday' ? subDays(new Date(), 1) : new Date(options.date);
      const filePath = await reporter.generateDailyReport(relativeDate, {
        noSummarize: options.noSummarize,
        outputPath: options.output,
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
      const manager = new ResearchManager();
      const result = await manager.addReport(options.file, options.category, {
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
      const manager = new ResearchManager();
      const result = await manager.getStats(options.category);
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
      const system = new ThinkingSystem();
      const result = await system.createModel({
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
  .action(async () => {
    try {
      console.log('🏠 Building homepage...');
      const builder = new HomepageBuilder();
      const result = await builder.buildHomepage();
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
  .action(async (options) => {
    try {
      console.log('📊 Collecting stats...');
      const builder = new HomepageBuilder();
      const result = await builder.getStats();
      if (result.success && result.data) {
        if (options.json) {
          console.log(JSON.stringify(result.data, null, 2));
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

// All command - run all agents in sequence
program
  .command('all')
  .description('Execute all agents in sequence')
  .option('--push', 'Push changes to git after execution')
  .action(async (options) => {
    try {
      const reporter = new DailyReporter();
      const builder = new HomepageBuilder();

      console.log('\n📰 Daily Report:');
      const dailyPath = await reporter.generateDailyReport();
      console.log(`  ✅ Generated: ${dailyPath}`);

      console.log('\n🏠 Homepage:');
      const homepageResult = await builder.buildHomepage();
      if (homepageResult.success) {
        console.log('  ✅ Homepage built');
      } else {
        console.log(`  ❌ Homepage failed: ${homepageResult.message}`);
      }

      if (options.push) {
        console.log('\n🔄 Pushing changes...');
        const { execSync } = await import('child_process');
        execSync('npm run git-push', { stdio: 'inherit' });
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
