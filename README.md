# AI 日报生成系统

自动抓取 RSS 订阅源和 HTML 页面，使用 OpenRouter API 生成摘要，并生成格式化的 HTML 日报。

## 功能特性

- 📰 支持 RSS/Atom 订阅源抓取
- 🌐 支持 HTML 页面内容抓取
- 🤖 使用 OpenRouter AI 生成文章摘要
- 📊 自动生成格式化的 HTML 日报
- ⚙️ 通过 YAML 配置文件管理信源
- 📝 支持文章分类和统计
- 🔗 保留原文链接方便查阅

## 安装

1. 克隆项目：
```bash
git clone <repository-url>
cd ai-news
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
```bash
cp .env.example .env
```

4. 编辑 `.env` 文件，添加你的 OpenRouter API Key：
```env
OPENROUTER_API_KEY=your_api_key_here
```

## 配置信源

编辑 `config/sources.yaml` 文件来管理订阅源：

### RSS 源配置
```yaml
rss_sources:
  - name: "信源名称"
    url: "https://example.com/feed.xml"
    category: "分类名称"
    enabled: true
```

### HTML 源配置
```yaml
html_sources:
  - name: "网站名称"
    url: "https://example.com/blog"
    selector: ".article-list"  # 文章列表容器选择器
    article_selector: ".article-item"  # 文章元素选择器
    title_selector: "h2"  # 标题选择器
    link_selector: "a"  # 链接选择器
    date_selector: ".pub-date"  # 日期选择器（可选）
    category: "分类名称"
    enabled: true
```

## 使用

### 生成日报

运行主程序生成当天的 AI 日报：

```bash
python src/main.py
```

生成的 HTML 文件将保存在 `output/` 目录下，文件名格式为 `ai-news-YYYY-MM-DD.html`。

### 查看生成的日报

在浏览器中打开生成的 HTML 文件：

```bash
open output/ai-news-2026-03-25.html
```

## 定时任务

### 使用 cron（Linux/macOS）

编辑 crontab：
```bash
crontab -e
```

添加定时任务（每天上午 9 点执行）：
```cron
0 9 * * * cd /path/to/ai-news && python src/main.py
```

### 使用系统服务

也可以配置为系统服务或使用定时任务管理工具如 systemd timer、launchd 等。

## 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `OPENROUTER_API_KEY` | OpenRouter API 密钥 | 必填 |
| `OPENROUTER_BASE_URL` | OpenRouter API 基础 URL | `https://openrouter.ai/api/v1` |
| `OPENROUTER_MODEL` | 使用的 AI 模型 | `anthropic/claude-3-sonnet` |
| `API_TIMEOUT` | API 请求超时时间（秒） | `60` |
| `MAX_ARTICLES_PER_SOURCE` | 每个源最多处理的文章数 | `20` |
| `OUTPUT_DIR` | 输出目录 | `output` |

## 项目结构

```
ai-news/
├── config/
│   └── sources.yaml          # 信源配置文件
├── src/
│   ├── fetchers/
│   │   ├── __init__.py
│   │   ├── rss_fetcher.py    # RSS 抓取模块
│   │   └── html_fetcher.py   # HTML 抓取模块
│   ├── summarizer.py         # OpenRouter 摘要模块
│   ├── generator.py          # HTML 生成模块
│   └── main.py               # 主程序入口
├── output/                   # 生成的 HTML 输出目录
├── requirements.txt          # Python 依赖
├── .env.example             # 环境变量示例
└── README.md                # 使用说明（本文件）
```

## 支持的 RSS 源

系统支持大多数标准的 RSS 和 Atom 订阅源，包括但不限于：
- WordPress RSS
- Medium RSS
- GitHub Releases
- Atom Feed
- 自定义 RSS

## 故障排查

### 1. RSS 源无法访问

- 检查 RSS 源 URL 是否正确
- 验证网络连接
- 检查是否为有效的 RSS/Atom 格式

### 2. HTML 抓取失败

- 验证 CSS 选择器是否正确
- 检查网站是否有反爬虫机制
- 尝试使用不同的选择器

### 3. OpenRouter API 错误

- 检查 API Key 是否正确
- 验证账户余额是否充足
- 检查 API 速率限制
- 查看错误日志获取详细信息

### 4. 生成的摘要不准确

- 尝试更换 AI 模型
- 调整摘要 prompt 模板
- 检查文章内容提取是否完整

## 注意事项

1. **API 费用**: 使用 OpenRouter API 会产生费用，请注意监控使用量
2. **知识产权**: 请遵守各信源网站的内容使用规则
3. **频率限制**: 建议每天运行一次，避免对信源服务器造成过大压力
4. **错误处理**: 程序会跳过失效的信源，但建议定期检查并更新配置

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 致谢

- 使用 [OpenRouter](https://openrouter.ai/) 提供 AI 摘要服务
- 参考示例样式设计