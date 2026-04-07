export interface SourceConfig {
  name: string;
  url: string;
  category: string;
  enabled: boolean;
  type: 'rss' | 'html';
  selector?: string;
  title_selector?: string;
  link_selector?: string;
  content_selector?: string;
  /** HTML 源：相对每条链接元素，用于取发布日期的选择器（如 Anthropic 列表 `div[class*="__date"]`） */
  date_selector?: string;
  /** HTML 源：列表项无日期时是否打开文章页解析（如 Featured 卡片） */
  resolve_missing_article_date?: boolean;
  max_articles?: number;
  filter_categories?: string[];
}

export interface Article {
  title: string;
  link: string;
  summary?: string;
  published?: Date;
  content?: string;
  category?: string;
  categories?: string[];
  source?: string;
}

export interface StructuredSummary {
  summary: string;
  keyInsights?: string[];
  relatedModels?: string[];
  newModels?: string[];
}

export interface SummarizedArticle extends Article {
  summarized: boolean;
  summaryQuality?: number;
  structuredSummary?: StructuredSummary;
}

export interface DailyReport {
  date: string;
  articles: SummarizedArticle[];
  stats: {
    totalArticles: number;
    summarizedArticles: number;
    avgSummaryQuality: number;
  };
}

export interface ResearchMetadata {
  id: string;
  title: string;
  category: string;
  file: string;
  addedDate: string;
  summary?: string;
  tags: string[];
}

export interface ThinkingModel {
  id: string;
  topic: string;
  type: 'framework' | 'methodology' | 'pattern' | 'concept';
  content: string;
  tags: string[];
  createdDate: string;
  updatedDate: string;
  version: number;
}

export interface ThinkingModelDisplay {
  id: string;
  title: string;
  source: string;
  icon: string;
  category: string;
  tags: string[];
  definition: string;
  insights: string[];
  connections: string[];
}

export interface ThinkingCategory {
  name: string;
  icon: string;
  slug: string;
  description: string;
  models: ThinkingModelDisplay[];
}

export interface ModelRelationship {
  from: string;
  to: string;
  type: 'related' | 'extends' | 'implements' | 'uses';
  strength: number;
}

export interface ArchiveEntry {
  date: string;
  dateDisplay: string;
  file: string;
  articles: number;
}

export interface ResearchEntry {
  title: string;
  date: string;
  file: string;
  summary: string;
  icon: string;
  category: string;
}

export interface HomepageData {
  latestDaily: {
    date: string;
    file: string;
    articleCount: number;
  } | null;
  dailyArchiveCount: number;
  latestResearch: ResearchEntry | null;
  researchList: ResearchEntry[];
  thinkingCategories: Array<{
    name: string;
    icon: string;
    file: string;
    description: string;
    modelCount: number;
  }>;
  stats: {
    totalArticles: number;
    totalReports: number;
    totalModels: number;
    lastUpdated: string;
  };
}

export interface AgentResult {
  success: boolean;
  message?: string;
  data?: any;
  duration?: number;
}

export interface TaskPlan {
  id: string;
  taskType: 'daily' | 'research' | 'thinking' | 'homepage';
  description: string;
  createdAt: string;
  tasks: SubTask[];
  harnessChecks: HarnessCheck[];
  rollbackSteps: RollbackStep[];
  outputPath: string;
}

export interface SubTask {
  id: string;
  description: string;
  agent: string;
  dependencies: string[];
  parameters: Record<string, any>;
  estimatedDuration?: number;
}

export interface HarnessCheck {
  ruleId: string;
  description: string;
  validator: string;
  severity: 'error' | 'warning';
}

export interface RollbackStep {
  description: string;
  command?: string;
  fileActions?: Array<{
    action: 'delete' | 'restore';
    path: string;
  }>;
}

export interface ValidationResult {
  passed: boolean;
  errors: ValidationError[];
  warnings: ValidationError[];
  duration?: number;
}

export interface ValidationError {
  ruleId: string;
  severity: 'error' | 'warning';
  message: string;
  location: {
    file: string;
    line?: number;
    column?: number;
  };
  suggestion?: string;
}

export interface DraftFile {
  path: string;
  agent: string;
  createdAt: string;
  status: 'pending' | 'evaluating' | 'approved' | 'rejected';
  validationResult?: ValidationResult;
}

export interface Config {
  /** LLM 摘要：优先 ANTHROPIC_*（火山方舟 OpenAI 兼容），否则 OPENROUTER_* */
  llm: {
    apiKey: string;
    baseUrl: string;
    model: string;
  };
  rssSources: SourceConfig[];
  htmlSources: SourceConfig[];
  harness: {
    styles: any;
    constraints: any;
  };
}
