#!/bin/bash
# Package AI News Daily as a Claude Code Skill

set -e

echo "📦 Packaging AI News Daily Skill..."
echo "====================================="

# Create temporary packaging directory
PKG_DIR="/tmp/ai-news-daily-skill-$$"
mkdir -p "$PKG_DIR"

# Copy project files
echo "📁 Copying project files..."

cp -r config "$PKG_DIR/" 2>/dev/null || mkdir -p "$PKG_DIR/config"
cp -r src "$PKG_DIR/"
cp -r templates "$PKG_DIR/" 2>/dev/null || mkdir -p "$PKG_DIR/templates"

cp requirements.txt "$PKG_DIR/"
cp .env.example "$PKG_DIR/" 2>/dev/null || touch "$PKG_DIR/.env.example"
cp skill-package/install.sh "$PKG_DIR/"
cp skill-package/README.md "$PKG_DIR/"
cp skill-package/skill.json "$PKG_DIR/"

# Create SKILL.md
cp skill-package/SKILL.md "$PKG_DIR/"

# Create tarball
echo "📦 Creating tarball..."
cd /tmp
tar -czf ai-news-daily-skill.tar.gz ai-news-daily-skill-$$

# Move to project directory
mv ai-news-daily-skill.tar.gz "$OLDPWD/"

# Cleanup
rm -rf "$PKG_DIR"

echo ""
echo "✅ Packaging complete!"
echo ""
echo "Skill package: ai-news-daily-skill.tar.gz"
echo ""
echo "To install the skill:"
echo "1. Extract: tar -xzf ai-news-daily-skill.tar.gz"
echo "2. Install: cd ai-news-daily-skill-* && ./install.sh"
echo ""
echo "Or manually install to Claude Code:"
echo "cp -r ai-news-daily-skill-* ~/.claude/skills/ai-news-daily/"

# Create zip as well
echo ""
echo "📦 Creating zip archive..."
cd "$OLDPWD"
cd /tmp
cp -r ai-news-daily-skill-$$ ai-news-daily-skill
zip -rq ai-news-daily-skill.zip ai-news-daily-skill
rm -rf ai-news-daily-skill
mv ai-news-daily-skill.zip "$OLDPWD/"

echo ""
echo "✅ Zip package created: ai-news-daily-skill.zip"
