#!/bin/bash
# AI News Daily Skill Installer

set -e

SKILL_NAME="ai-news-daily"
SKILL_DIR="$HOME/.claude/skills/$SKILL_NAME"
PROJECT_DIR="$(pwd)"

echo "Installing AI News Daily Skill..."
echo "=================================="

# Check if skill directory exists
if [ -d "$SKILL_DIR" ]; then
    echo "⚠️  Skill already exists at $SKILL_DIR"
    read -p "Do you want to overwrite it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 1
    fi
    rm -rf "$SKILL_DIR"
fi

# Create skill directory
echo "📁 Creating skill directory..."
mkdir -p "$SKILL_DIR"

# Copy project files
echo "📦 Copying project files..."
cp -r "$PROJECT_DIR"/* "$SKILL_DIR/"

# Remove unnecessary files
rm -f "$SKILL_DIR/install.sh"
rm -rf "$SKILL_DIR/skill-package"

# Create references directory
mkdir -p "$SKILL_DIR/references"

# Copy config example
cp "$PROJECT_DIR/config/sources.yaml" "$SKILL_DIR/references/sources.example.yaml"

# Make scripts executable
chmod +x "$SKILL_DIR/src/main.py"

# Create activation script
cat > "$SKILL_DIR/run.sh" << 'EOF'
#!/bin/bash
# AI News Daily Runner

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Run with all arguments
python src/main.py "$@"
EOF

chmod +x "$SKILL_DIR/run.sh"

echo ""
echo "✅ Installation complete!"
echo ""
echo "To use the skill:"
echo "1. cd $SKILL_DIR"
echo "2. Configure sources in config/sources.yaml"
echo "3. Set up .env with your OpenRouter API key"
echo "4. Run: ./run.sh"
echo ""
echo "Or activate manually:"
echo "cd $SKILL_DIR"
echo "source venv/bin/activate"
echo "python src/main.py"
echo ""
echo "For daily cron job:"
echo "0 9 * * * cd $SKILL_DIR && ./run.sh"
