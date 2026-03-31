import { Styles, defaultStyles, validateStyles } from './styles.js';
import { ContentValidator, ValidationResult } from './validators.js';
import { loadConfig } from '../utils/config.js';
import * as yaml from 'js-yaml';
import * as fs from 'fs';
import * as path from 'path';

export interface HarnessConfig {
  styles: Styles;
  constraints: {
    summary?: {
      min_length: number;
      max_length: number;
      quality_threshold: number;
    };
    report?: {
      required_sections: string[];
    };
    thinking_model?: {
      required_elements: string[];
    };
  };
}

export class HarnessController {
  private static instance: HarnessController;
  private config: HarnessConfig;
  private validator: ContentValidator;
  private initialized: boolean = false;

  constructor() {
    this.validator = new ContentValidator();
    this.config = {
      styles: defaultStyles,
      constraints: {}
    };
  }

  static getInstance(): HarnessController {
    if (!HarnessController.instance) {
      HarnessController.instance = new HarnessController();
    }
    return HarnessController.instance;
  }

  async initialize(): Promise<void> {
    if (this.initialized) {
      return;
    }

    try {
      const configPath = path.join(process.cwd(), 'config/harness.yaml');
      if (fs.existsSync(configPath)) {
        const content = fs.readFileSync(configPath, 'utf8');
        const loadedConfig = (yaml.load(content) || {}) as any;

        this.config = {
          styles: { ...defaultStyles, ...(loadedConfig.styles || {}) },
          constraints: loadedConfig.constraints || {}
        };
      } else {
        this.config = {
          styles: defaultStyles,
          constraints: {}
        };
      }

      this.initialized = true;
    } catch (error) {
      console.error('Failed to load Harness config:', error);
      throw error;
    }
  }

  getStyles(): Styles {
    return this.config.styles;
  }

  getConstraints(): HarnessConfig['constraints'] {
    return this.config.constraints;
  }

  validateDocument(html: string): ValidationResult {
    return this.validator.validateDocument(html);
  }

  validateSummary(summary: string): ValidationResult {
    return this.validator.validateSummary(summary);
  }

  validateResearchReport(content: string): ValidationResult {
    return this.validator.validateResearchReport(content);
  }

  validateThinkingModel(content: string): ValidationResult {
    return this.validator.validateThinkingModel(content);
  }

  checkFile(filePath: string): ValidationResult {
    try {
      if (!fs.existsSync(filePath)) {
        return {
          valid: false,
          errors: [`File not found: ${filePath}`],
          warnings: []
        };
      }

      const content = fs.readFileSync(filePath, 'utf8');

      // Determine file type and validate accordingly
      if (filePath.endsWith('.html')) {
        return this.validateDocument(content);
      } else if (filePath.includes('ai-daily')) {
        // Assume HTML report
        return this.validateDocument(content);
      } else if (filePath.includes('research')) {
        return this.validator.validateResearchReport(content);
      } else if (filePath.includes('thinking')) {
        return this.validator.validateThinkingModel(content);
      } else {
        return {
          valid: true,
          errors: [],
          warnings: [`Unknown file type: ${filePath}, performing basic validation`]
        };
      }
    } catch (error: any) {
      return {
        valid: false,
        errors: [`Failed to check file ${filePath}: ${error.message}`],
        warnings: []
      };
    }
  }

  async applyConstraints(data: any, type: 'summary' | 'report' | 'thinking_model'): Promise<[boolean, string[]]> {
    const constraints = this.config.constraints[type] as any;
    if (!constraints) {
      return [true, []];
    }

    const warnings: string[] = [];
    let valid = true;

    switch (type) {
      case 'summary': {
        const summary: string = data.summary || data as string || '';

        if (constraints.min_length && summary.length < constraints.min_length) {
          warnings.push(`Summary below minimum length: ${summary.length}/${constraints.min_length}`);
          valid = false;
        }

        if (constraints.max_length && summary.length > constraints.max_length) {
          warnings.push(`Summary exceeds maximum length: ${summary.length}/${constraints.max_length}`);
        }

        if (constraints.quality_threshold && data.summaryQuality !== undefined) {
          if (data.summaryQuality < constraints.quality_threshold) {
            warnings.push(`Summary quality below threshold: ${data.summaryQuality}/${constraints.quality_threshold}`);
          }
        }
        break;
      }

      case 'report': {
        const requiredSections: string[] = constraints.required_sections || [];
        for (const section of requiredSections) {
          if (!data[section] && !data.content?.includes(section)) {
            warnings.push(`Missing required section: ${section}`);
            valid = false;
          }
        }
        break;
      }

      case 'thinking_model': {
        const requiredElements: string[] = constraints.required_elements || [];
        for (const element of requiredElements) {
          if (!data[element] && !data.content?.includes(element)) {
            warnings.push(`Missing required element: ${element}`);
            valid = false;
          }
        }
        break;
      }
    }

    return [valid, warnings];
  }

  getStylesCSS(): string {
    const { colors, fonts, layout } = this.config.styles;

    return `
:root {
  --color-primary: ${colors.primary};
  --color-secondary: ${colors.secondary};
  --color-accent: ${colors.accent};
  --color-background: ${colors.background};
  --color-surface: ${colors.surface};
  --color-text: ${colors.text};
  --color-text-secondary: ${colors.textSecondary};
  --color-border: ${colors.border};

  --font-heading: ${fonts.heading};
  --font-body: ${fonts.body};
  --font-code: ${fonts.code};

  --layout-max-width: ${layout.maxWidth};
  --layout-spacing: ${layout.spacing};
  --layout-border-radius: ${layout.borderRadius};
}

body {
  font-family: var(--font-body);
  color: var(--color-text);
  background-color: var(--color-background);
  line-height: 1.6;
}

h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-heading);
}

.container {
  max-width: var(--layout-max-width);
  margin: 0 auto;
  padding: var(--layout-spacing);
}

.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--layout-border-radius);
  padding: var(--layout-spacing);
}

.btn-primary {
  background: var(--color-primary);
  color: var(--color-surface);
  border: none;
  border-radius: var(--layout-border-radius);
  padding: 0.75rem 1.5rem;
  cursor: pointer;
}

.btn-primary:hover {
  background: var(--color-accent);
}
    `.trim();
  }

  validateConfig(): ValidationResult {
    const result: ValidationResult = {
      valid: true,
      errors: [],
      warnings: []
    };

    // Validate styles
    const stylesResult = validateStyles(this.config.styles);
    if (!stylesResult.valid) {
      result.errors.push(...stylesResult.errors);
      result.valid = false;
    }

    // Validate constraints structure
    const constraints = this.config.constraints;
    if (constraints.summary) {
      if (constraints.summary.min_length && constraints.summary.min_length < 10) {
        result.warnings.push('Minimum summary length very short');
      }
      if (constraints.summary.quality_threshold && constraints.summary.quality_threshold > 1) {
        result.warnings.push('Quality threshold should be between 0-1');
      }
    }

    return result;
  }

  getInfo(): any {
    return {
      version: '1.0.0',
      configPath: path.join(process.cwd(), 'config/harness.yaml'),
      initialized: this.initialized,
      styles: this.config.styles,
      constraints: this.config.constraints
    };
  }
}
