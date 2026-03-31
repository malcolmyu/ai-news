#!/usr/bin/env bash
# AI News Harness — 环境验证入口
# 运行方式: bash .agent/init.sh
# 目标: 快速确认当前环境可以正常工作（< 30 秒）
set -euo pipefail

echo "=== AI News Harness: Environment Check ==="

# 1. 工作目录确认
echo "  [CWD] $(pwd)"

# 2. Node.js 版本检查（要求 >= 18）
NODE_VERSION=$(node --version 2>/dev/null || echo "not found")
NODE_MAJOR=$(echo "$NODE_VERSION" | sed 's/v//' | cut -d. -f1)
if [[ "$NODE_MAJOR" -lt 18 ]]; then
  echo "FAIL: Node.js >= 18 required (found $NODE_VERSION)"
  exit 1
fi
echo "  [OK] Node.js $NODE_VERSION"

# 3. 依赖检查（不安装，只检查 node_modules 是否存在）
if [[ ! -d node_modules ]]; then
  echo "  Installing dependencies..."
  npm install --silent
fi
echo "  [OK] node_modules present"

# 4. TypeScript 编译（Babel 转译 + tsc 类型检查）
echo "  Running build (Babel + tsc --noEmit)..."
if ! npm run build > /tmp/ai-news-init-build.log 2>&1; then
  echo "FAIL: npm run build failed. Details:"
  cat /tmp/ai-news-init-build.log
  exit 1
fi
echo "  [OK] Build passed"

# 5. Playwright Chromium 可用性（非致命，只警告）
if node -e "import('playwright').then(m => m.chromium.launch({headless:true}).then(b => b.close()))" > /dev/null 2>&1; then
  echo "  [OK] Playwright chromium available"
else
  echo "  [WARN] Playwright chromium not available — run: npx playwright install chromium"
fi

echo ""
echo "=== Harness init complete. Ready to work. ==="
echo ""
echo "  Harness files:"
echo "  - .agent/claude-progress.md   : 上次会话做了什么，下一步是什么"
echo "  - .agent/feature_list.json    : 各 pipeline 健康状态"
echo "  - .agent/clean-state-checklist.md : 会话结束前的清单"
