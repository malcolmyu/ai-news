# CloakBrowser + 中文平台内容提取工作流

## 背景

中文内容平台（知乎、微信公众号等）有严格的机器人检测，普通 browser 工具（Playwright/Puppeteer/CDP）经常被 Cloudflare Turnstile 或反爬拦截。

## 工具

**CloakBrowser** — stealth Chromium 二进制，C++ 源码层 patch 32 处指纹（Canvas/WebGL/GPU/字体/音频），非 JS 注入。免费，MIT 协议。

- 网站：https://cloakbrowser.dev/
- GitHub：https://github.com/CloakHQ/CloakBrowser
- Python 安装：`pip install cloakbrowser`
- 当前版本（2026/5）：v0.3.28，Chromium v145

## 已验证通过的平台

- **知乎** — 文章页（zhuanlan.zhihu.com/p/xxx）完整提取，Turnstile 无感通过
- **微信公众号** — 待验证

## 完整提取工作流（Python + Hermes execute_code）

```python
from hermes_tools import terminal

result = terminal(
    command="""python3 -c "
from cloakbrowser import launch

browser = launch(headless=True)
page = browser.new_page()
page.goto('URL', timeout=30000)

# Wait for content to load (5s safe — JS rendering on Chinese sites is slower)
page.wait_for_timeout(5000)

# Get title
title = page.title()

# Get article body — try standard selectors first
try:
    article = page.locator('.Post-RichText').first.inner_text(timeout=5000)
except:
    article = page.inner_text('body')[:5000]

print('=== TITLE ===')
print(title)
print()
print('=== ARTICLE ===')
print(article)

browser.close()
" 2>&1""",
    timeout=60
)
```

## 关键注意事项

1. **headless=True 可以** — 知乎对 headless Chrome 不敏感，因为 CloakBrowser 在 C++ 层消除了 headless 检测特征
2. **wait_for_timeout(5000)** — 中文 JS 渲染慢，需要足够的等待时间。比 `wait_for_load_state('networkidle')` 更可靠
3. **内容可能被截断** — `page.content()` / `inner_text()` 有默认截断限制。长文需要分块提取或使用 `locator` 精确抓取
4. **分块策略** — 文章超过 5000 字时，用 offset 分两次提取剩余内容
5. **不要用 browser_navigate** — Hermes 的 browser_navigate 也经过 CDP，但某些中文平台有 CDP 检测。CloakBrowser 的 stealth driver 消除了 CDP 检测特征，比 browser_navigate 更隐蔽

## 竞品对比

| 方案 | 方式 | 中文平台 | 成本 |
|------|------|---------|------|
| CloakBrowser | C++ 源码 patch | ✅ 知乎 | 免费 |
| Playwright stealth | JS 注入 | ❌ 知乎 | 免费 |
| browser_navigate (Hermes) | CDP | ⚠️ 部分 | 免费 |
| 商业反检测浏览器 (Multilogin等) | JS 注入 | ✅ | $29-199/月 |

## 本 session 验证

- URL: https://zhuanlan.zhihu.com/p/2037479092090622773
- 标题: "Agent 系统正在重新走一遍 OS 和 Cloud Runtime 的老路"
- 内容完整性: ✅ 全文 10 个章节完整提取（~8000 字）
- 反爬状态: Cloudflare Turnstile 无触发，页面加载无任何验证
