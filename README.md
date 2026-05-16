# 第二号 — AI 新闻与研究

个人数字分身，每日追踪 AI 行业动态，系统化构建知识体系。静态 HTML 站点，通过 GitHub Pages 部署。

## 内容体系

- **AI 日报** (`docs/daily/`) — 每日 AI Builder 动态、播客精选、GitHub 热门项目
- **深度调研** (`docs/research/`) — Agent 架构、多智能体系统、AI 工程组织等主题的长文分析
- **思维模型** (`docs/thinking/`) — 认知、沟通、决策、产品四个维度的思维框架
- **首页** (`docs/index.html`) — 聚合最新日报和调研报告

## 设计系统

Bento 风格：4 列网格布局，`#5e6ad2` 强调色，`#f5f5f4` 背景，Inter 字体，14px 圆角。共享样式表 `docs/styles.css` 作为唯一设计真理来源。

## 目录结构

```
docs/
  styles.css                  # 共享 Bento 设计系统
  index.html                  # 首页
  daily/                      # 日报 + 媒体资源 + 归档
  research/                   # 调研报告 + 截图 + 归档
  thinking/                   # 思维模型页面
scripts/
  fetch-daily-media.sh        # 下载 X/Twitter 图片 + YouTube 缩略图
  generate-daily-html.sh      # URL → HTML embed 流水线
  update-homepage.py          # 通过注释标记更新首页调研区域
.github/
  style-check.sh              # 部署前完整性 + 风格检查
  workflows/pages.yml         # GitHub Pages 自动部署
```

## 工作流

1. 每日日报通过 Claude Code session 生成，直接写入 `docs/daily/ai-news-YYYY-MM-DD.html`
2. 调研报告手动编写为静态 HTML
3. 首页调研区域通过 `python3 scripts/update-homepage.py` 自动更新
4. Push 到 `main` 或 `malcolmyu/auckland` 分支触发 GitHub Pages 部署
5. `style-check.sh` 在部署前运行完整性验证

## 内容约定

详见 [CONTEXT.md](CONTEXT.md)。
