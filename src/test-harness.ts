import * as fs from 'fs';
import * as path from 'path';
import { HarnessController } from './harness/controller.js';
import { ReportGenerator } from './generator.js';
import { Summarizer } from './summarizer.js';
import { RSSFetcher } from './fetchers/rss-fetcher.js';
import { HTMLFetcher } from './fetchers/html-fetcher.js';
import { Logger } from './utils/config.js';

interface TestResult {
  name: string;
  passed: boolean;
  message: string;
  duration: number;
}

class TestHarness {
  private logger: Logger;
  private results: TestResult[] = [];

  constructor() {
    this.logger = new Logger('TestHarness');
  }

  async runAll(): Promise<void> {
    console.log('🧪 Running Test Harness...\n');

    // Test configuration
    await this.test('configuration_loads', () => this.testConfigLoads());
    await this.test('harness_initializes', () => this.testHarnessInit());

    // Test fetchers
    await this.test('rss_fetcher_creates', () => this.testRSSFetcher());
    await this.test('html_fetcher_creates', () => this.testHTMLFetcher());

    // Test summarizer (requires API key)
    if (process.env.OPENROUTER_API_KEY) {
      await this.test('summarizer_creates', () => this.testSummarizer());
    } else {
      this.logger.warn('Skipping summarizer tests - no API key');
    }

    // Test generator
    await this.test('generator_creates', () => this.testGenerator());

    // Test file operations
    await this.test('output_directory_creates', () => this.testOutputDir());

    // Test harness validation
    await this.test('harness_validates_html', () => this.testHarnessValidation());

    this.printResults();
  }

  private async test(name: string, testFn: () => Promise<any> | any): Promise<void> {
    const startTime = Date.now();

    try {
      const result = await testFn();
      const duration = Date.now() - startTime;

      this.results.push({
        name,
        passed: true,
        message: 'Test passed',
        duration,
      });

      this.logger.log(`✓ ${name} (${duration}ms)`);
    } catch (error) {
      const duration = Date.now() - startTime;
      const message = error instanceof Error ? error.message : 'Unknown error';

      this.results.push({
        name,
        passed: false,
        message,
        duration,
      });

      this.logger.error(`✗ ${name} (${duration}ms): ${message}`);
    }
  }

  private testConfigLoads(): void {
    const configPath = './config/sources.yaml';

    if (!fs.existsSync(configPath)) {
      throw new Error(`Config file not found: ${configPath}`);
    }

    const configContent = fs.readFileSync(configPath, 'utf8');
    const config = require('js-yaml').load(configContent);

    if (!config || (!config.rss_sources && !config.html_sources)) {
      throw new Error('Invalid config format');
    }
  }

  private async testHarnessInit(): Promise<void> {
    const harness = HarnessController.getInstance();
    await harness.initialize();

    const styles = harness.getStyles();
    if (!styles.colors || !styles.fonts) {
      throw new Error('Harness failed to initialize properly');
    }

    const config = harness.validateConfig();
    if (config.errors.length > 0) {
      throw new Error(`Config validation failed: ${config.errors.join(', ')}`);
    }
  }

  private testRSSFetcher(): void {
    const fetcher = new RSSFetcher();
    if (!fetcher) {
      throw new Error('Failed to create RSS fetcher');
    }
  }

  private testHTMLFetcher(): void {
    const fetcher = new HTMLFetcher();
    if (!fetcher) {
      throw new Error('Failed to create HTML fetcher');
    }
  }

  private testSummarizer(): void {
    if (!process.env.OPENROUTER_API_KEY) {
      throw new Error('OPENROUTER_API_KEY not set');
    }

    const summarizer = new Summarizer(
      process.env.OPENROUTER_API_KEY,
      process.env.OPENROUTER_BASE_URL
    );

    if (!summarizer) {
      throw new Error('Failed to create summarizer');
    }
  }

  private testGenerator(): void {
    const generator = new ReportGenerator();

    // Check if output directory is accessible
    const outputDir = path.join(process.cwd(), 'output');
    path.resolve(outputDir); // Will throw if path issues
  }

  private testOutputDir(): void {
    const outputDir = path.join(process.cwd(), 'output');

    // Ensure it can be created
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    // Test write
    const testFile = path.join(outputDir, '.test');
    fs.writeFileSync(testFile, 'test', 'utf8');
    fs.unlinkSync(testFile);
  }

  private testHarnessValidation(): void {
    const harness = HarnessController.getInstance();

    // Test HTML validation
    const testHTML = `
      <!DOCTYPE html>
      <html>
        <head>
          <title>Test</title>
          <meta charset="UTF-8">
        </head>
        <body>
          <h1>Test</h1>
          <p>Content</p>
        </body>
      </html>
    `;

    const validation = harness.validateDocument(testHTML);
    if (!validation.valid) {
      throw new Error(`HTML validation failed: ${validation.errors.join(', ')}`);
    }

    // Test summary validation
    const testSummary = 'This is a test summary that is long enough to pass validation.';
    const summaryValidation = harness.validateSummary(testSummary);
    if (!summaryValidation.valid) {
      throw new Error(`Summary validation failed: ${summaryValidation.errors.join(', ')}`);
    }
  }

  private printResults(): void {
    const passed = this.results.filter(r => r.passed).length;
    const failed = this.results.filter(r => !r.passed).length;
    const totalDuration = this.results.reduce((sum, r) => sum + r.duration, 0);

    console.log('\n=== Test Results ===\n');

    // Group by status
    this.results
      .sort((a, b) => {
        if (a.passed !== b.passed) {
          return a.passed ? 1 : -1;
        }
        return a.name.localeCompare(b.name);
      })
      .forEach((result) => {
        const status = result.passed ? '✓' : '✗';
        const color = result.passed ? '' : '';
        console.log(`${status} ${result.name} (${result.duration}ms)`);

        if (!result.passed) {
          console.log(`  Error: ${result.message}`);
        }
      });

    console.log(`\n=== Summary ===`);
    console.log(`Total tests: ${this.results.length}`);
    console.log(`✅ Passed: ${passed}`);
    console.log(`❌ Failed: ${failed}`);
    console.log(`⏱️  Total time: ${totalDuration}ms`);

    if (failed > 0) {
      console.log('\n❌ Some tests failed');
      process.exit(1);
    } else {
      console.log('\n✅ All tests passed!');
    }
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const test = new TestHarness();
  test.runAll().catch((error) => {
    console.error('Failed to run tests:', error);
    process.exit(1);
  });
}

export { TestHarness };