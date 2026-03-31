import * as fs from 'fs';
import * as path from 'path';
import * as yaml from 'js-yaml';
import dotenv from 'dotenv';
import type { Config, SourceConfig } from '../types/index.js';

dotenv.config();

const configFile = path.join(process.cwd(), 'config/sources.yaml');
const harnessFile = path.join(process.cwd(), 'config/harness.yaml');

function loadYamlFile(filePath: string): any {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    return yaml.load(content) || {};
  } catch (error) {
    console.error(`Failed to load YAML file ${filePath}:`, error);
    return {};
  }
}

export function loadConfig(): Config {
  const sourcesConfig = loadYamlFile(configFile);
  const harnessConfig = loadYamlFile(harnessFile);

  return {
    openRouter: {
      apiKey: process.env.OPENROUTER_API_KEY || '',
      baseUrl: process.env.OPENROUTER_BASE_URL || 'https://openrouter.ai/api/v1',
      model: process.env.OPENROUTER_MODEL || 'anthropic/claude-sonnet',
    },
    rssSources: (sourcesConfig.rss_sources || []) as SourceConfig[],
    htmlSources: (sourcesConfig.html_sources || []) as SourceConfig[],
    harness: harnessConfig,
  };
}

export function ensureDir(dirPath: string): void {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

export function writeJSONFile(filePath: string, data: any): void {
  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf8');
}

export function readJSONFile(filePath: string): any {
  if (!fs.existsSync(filePath)) {
    return null;
  }
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    return JSON.parse(content);
  } catch (error) {
    console.error(`Failed to read JSON file ${filePath}:`, error);
    return null;
  }
}

export function formatDate(date: Date = new Date()): string {
  return date.toISOString().split('T')[0];
}

export class Logger {
  private prefix: string;

  constructor(prefix: string = 'App') {
    this.prefix = prefix;
  }

  log(message: string, ...args: any[]): void {
    console.log(`[${this.prefix}] ${new Date().toISOString()} - ${message}`, ...args);
  }

  error(message: string, error?: Error): void {
    console.error(`[${this.prefix}] ${new Date().toISOString()} - ERROR: ${message}`);
    if (error) {
      console.error(error.stack || error.message);
    }
  }

  warn(message: string, error?: Error): void {
    console.warn(`[${this.prefix}] ${new Date().toISOString()} - WARN: ${message}`);
    if (error) {
      console.warn(error.stack || error.message);
    }
  }

  info(message: string, ...args: any[]): void {
    this.log(`INFO: ${message}`, ...args);
  }

  debug(message: string, ...args: any[]): void {
    if (process.env.DEBUG) {
      this.log(`DEBUG: ${message}`, ...args);
    }
  }
}
