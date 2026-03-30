# Growth Website System - 个人自主成长网站系统

## 项目概述

基于 Agent-Team 架构的个人自主成长网站系统，集成 AI 日报生成、深度调研报告管理、思考模型沉淀和主页展示四大核心功能。

![Architecture](docs/architecture-diagram.png)

## 🚀 快速开始

### 1. 安装

```bash
# 克隆项目
git clone <repository-url>
cd auckland

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，添加 OpenRouter API Key
```

### 2. 基础配置

编辑 `config/sources.yaml` 配置 RSS/HTML 源：

```yaml
rss_sources:
  - name: "Example RSS"
    url: "https://example.com/feed.xml"
    category: "tech"
    enabled: true

html_sources:
  - name: "Example Website"
    url: "https://example.com/blog"
    selector: ".articles"
    title_selector: "h2"
    link_selector: "a"
    enabled: true
```

### 3. 首次运行

```bash
# 生成今日日报
python run.py daily

# 更新首页
python run.py homepage build

# 查看统计信息
python run.py stats
```

## 🏗️ 系统架构

### Agent Team 组成

```
Growth Website System
├── Team Coordinator (中央协调器)
├── Daily Reporter Agent (AI日报生成)
├── Research Manager Agent (调研报告管理)
├── Thinking System Agent (思考模型沉淀)
├── Homepage Builder Agent (主页构建)
└── Harness Controller (约束控制层)
```

### 各 Agent 职责

| Agent | 职责 | 主要接口 |
|-------|------|----------|
| **Daily Reporter** | RSS/HTML 抓取、AI 摘要、日报 HTML 生成 | `daily --date YYYY-MM-DD` |
| **Research Manager** | 报告元数据提取、分类归档、索引管理 | `research add --file report.html` |
| **Thinking System** | 思考模型创建、关系分析、图谱生成 | `thinking create --topic "主题" --file content.md` |
| **Homepage Builder** | 内容聚合、统计生成、SEO 优化 | `homepage build` |
| **Harness Controller** | 样式约束、内容验证、质量控制 | `harness check --file output.html` |

## 💻 命令行接口

### 日报操作

```bash
# 生成今日日报
python run.py daily

# 生成指定日期日报
python run.py daily --date 2026-03-30

# 跳过 AI 摘要（快速模式）
python run.py daily --no-summarize

# 生成后自动推送到 git
python run.py daily --push
```

### 调研报告管理

```bash
# 添加调研报告
python run.py research add --file report.html --category tech

# 查看调研统计
python run.py research stats

**支持的分类：** tech, product, business, methodology, ai, data, design, strategy
```

### 思考模型管理

```bash
# 创建思考模型
python run.py thinking create --topic "决策框架" --file content.md

# 支持模型类型：framework, methodology, pattern, concept
python run.py thinking create --topic "AI 伦理" --file content.md --model-type methodology

# 创建带标签的模型
python run.py thinking create --topic "决策框架" --file content.md --tags "decision-making,business,strategy"
```

### 首页管理

```bash
# 构建首页
python run.py homepage build

# 启用性能优化
python run.py homepage build --optimize
```

### 系统操作

```bash
# 执行所有 Agent
python run.py all

# 执行后推送更新
python run.py all --push

# 查看系统统计
python run.py stats

# 查看 JSON 格式统计
python run.py stats --json

# 查看特定 Agent 状态
python run.py stats --agent daily

# 检查文件质量
python run.py harness check --file output/index.html

# 查看 Harness 信息
python run.py harness info
```

### Git 操作

```bash
# 推送更改
python run.py git push -m "更新内容"

# 生成默认消息
python run.py git push
```

### 帮助信息

```bash
# 查看所有命令
python run.py --help

# 查看特定命令帮助
python run.py daily --help
python run.py research --help
python run.py thinking --help
```

## 📁 数据目录结构

```
data/
├── daily/                     # 日报数据
│   ├── archives.json         # 日报归档索引
│   └── stats.json            # 日报统计
├── research/                  # 调研报告数据
│   ├── index.json            # 报告元数据索引
│   └── categories/           # 分类存储
├── thinking/                  # 思考模型数据
│   ├── models.json           # 模型索引
│   ├── relationships/        # 概念关系
│   └── versions/            # 模型版本历史
└── homepage/
    └── feed.json            # 聚合内容提要

output/                        # 输出文件
├── ai-daily-YYYY-MM-DD.html # 生成的日报
└── index.html              # 首页

docs/                         # 静态站点输出
└── index.html             # 发布的首页

config/
├── sources.yaml            # RSS/HTML 源配置
└── harness.yaml           # 约束配置
```

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `OPENROUTER_API_KEY` | OpenRouter API 密钥 | 必填 |
| `OPENROUTER_BASE_URL` | API 基础 URL | `https://openrouter.ai/api/v1` |
| `OPENROUTER_MODEL` | AI 模型 | `anthropic/claude-3-sonnet` |

### 约束配置 (config/harness.yaml)

```yaml
styles:
  colors:
    primary: "#3b82f6"
    secondary: "#f8fafc"
  fonts:
    heading: "'Inter', sans-serif"
    body: "'Inter', sans-serif"

constraints:
  summary:
    min_length: 50
    max_length: 300
    quality_threshold: 0.7

  report:
    required_sections: ["summary", "insights", "references"]

  thinking_model:
    required_elements: ["concepts", "relationships", "examples"]
```

## 🧪 测试与验证

### 基础功能测试

```bash
# 测试 Daily Reporter
python run.py daily --no-summarize --verbose

# 测试 Research Manager
echo "<html><head><title>Test</title></head><body><h1>Test Report</h1></body></html>" > test-report.html
python run.py research add --file test-report.html --category test
rm test-report.html

# 测试 Thinking System
echo "## Test Model\n\n**Core Concept**: Test content here.\n\n### Example\nThis is an example." > test-model.md
python run.py thinking create --topic "Test" --file test-model.md
rm test-model.md

# 测试 Homepage Builder
python run.py homepage build

# 运行测试套件
python test_harness.py
```

## 🚀 自动化部署

### 使用 Cron (Linux/macOS)

```bash
# 编辑 crontab
crontab -e

# 每天 9:00 AM 生成日报并推送
0 9 * * * cd /path/to/auckland && python run.py daily --push

# 每小时检查调研报告
0 * * * * cd /path/to/auckland && python run.py research stats
```

### 使用 GitHub Actions

```yaml
# .github/workflows/daily-update.yml
name: Daily Update
on:
  schedule:
    - cron: '0 9 * * *'  # 每天 UTC 9:00

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: python run.py all --push
        env:
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
```

## 📊 监控与日志

### 操作日志

```bash
# 查看操作日志
cat data/system/operation_log.json | python -m json.tool
```

### 性能监控

```bash
# 查看处理时间统计
python run.py stats | grep "duration"

# 监控 Agent 性能
python run.py stats --agent daily
```

## 🔍 故障排查

### 常见问题

| 问题 | 解决方案 |
|------|----------|
| API Key 错误 | 检查 `.env` 文件和 OPENROUTER_API_KEY |
| RSS 源无法访问 | 验证 URL 和网络连接，检查配置格式 |
| HTML 抓取失败 | 检查 CSS 选择器，查看网站反爬虫措施 |
| 生成摘要不准确 | 考虑更换 AI 模型或调整 prompt |
| 首页样式错乱 | 检查 Harness 约束配置文件 |

### 调试模式

```bash
# 启用详细日志
python run.py daily --verbose

# 测试 Harness 验证
python run.py harness check --file output/index.html

# 查看系统信息
python run.py harness info
```

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📄 许可证

MIT License

## 🙏 致谢

- [OpenRouter](https://openrouter.ai/) - AI 摘要服务
- [Anthropic Claude](https://anthropic.com/) - 核心 AI 模型
- [Growth Website System](https://github.com/your-username/auckland) - 项目架构

## 📞 联系信息

- 项目管理: [GitHub Issues](https://github.com/your-username/auckland/issues)
- 问题反馈: 创建 Issue 或联系维护者

---

**Happy Coding!** 🎉
