# 第二号 — AI 新闻与研究

个人数字分身，每日追踪 AI 行业动态，系统化构建知识体系。静态 HTML 站点，通过 GitHub Pages 部署。

## 内容体系

- **AI 日报** (`docs/daily/`) — 每日 AI Builder 动态、播客精选、GitHub 热门项目
- **深度调研** (`docs/research/`) — Agent 架构、多智能体系统、AI 工程组织等主题的长文分析
- **思维模型** (`docs/thinking/`) — 认知、沟通、决策、产品四个维度的思维框架
- **首页** (`docs/index.html`) — 聚合最新日报和调研报告

## 设计系统

Bento 风格：4 列网格布局，`#2563eb` 强调色，`#f5f5f4` 背景，Inter 字体，14px 圆角。共享样式表 `docs/styles.css` 作为唯一设计真理来源。

## 目录结构

```
docs/
  styles.css                  # 共享 Bento 设计系统
  index.html                  # 首页
  agents/                     # 项目内 Hermes/Codex 生产 skills
  daily/                      # 日报 + 媒体资源 + 归档
  research/                   # 调研报告 + 截图 + 归档
  thinking/                   # 思维模型页面
scripts/
  python.sh                    # Python runtime resolver for harness scripts
  fetch-daily-media.sh        # 下载 X/Twitter 图片 + YouTube 缩略图
  generate-daily-html.sh      # URL → HTML embed 流水线
  site_harness.py             # 内容索引、首页/归档生成、结构校验
  update-homepage.py          # 兼容 wrapper，实际调用 site_harness.py
.github/
  style-check.sh              # 部署前完整性 + 风格检查
  workflows/pages.yml         # GitHub Pages 自动部署
```

## 工作流

1. Hermes 根据 `docs/agents/` 中的项目内 skill 调度日报或调研报告任务
2. Codex 执行文件编辑、媒体处理、浏览器验收和 git 操作
3. 每日日报写入 `docs/daily/ai-news-YYYY-MM-DD.html`，媒体写入 `docs/daily/assets/YYYY-MM-DD/`
4. 调研报告按 `docs/agents/skills/ai-news-research-report/` 的项目内流程生成
5. 首页与归档页通过 `npm run site:update` 从内容文件自动生成
6. `npm run site:validate`、`bash .github/style-check.sh .`、必要时 `npm run build:search` 在发布前运行完整性验证
7. Push 到 `main` 或 `malcolmyu/auckland` 分支触发 GitHub Pages 部署

## 内容约定

详见 [CONTEXT.md](CONTEXT.md)。

## Harness 架构

详见 [docs/agents/architecture.md](docs/agents/architecture.md) 和 [docs/adr/0002-hermes-codex-production-harness.md](docs/adr/0002-hermes-codex-production-harness.md)。
