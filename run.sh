#!/bin/bash
"
AI 日报生成系统运行脚本

使用方法:
    ./run.sh                    # 生成当天的日报
    ./run.sh --date 2026-03-25  # 生成指定日期的日报
    ./run.sh --verbose          # 显示详细日志
    ./run.sh --no-summarize     # 跳过摘要生成
    ./run.sh --check            # 检查所有信源
"

# 设置项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助
show_help() {
    cat << EOF
AI 日报生成系统

使用方法:
    $0 [选项]

选项:
    --date DATE         指定日期 (YYYY-MM-DD)，默认为今天
    --verbose, -v       显示详细日志
    --no-summarize      跳过摘要生成（仅抓取）
    --check             检查所有信源是否有效
    --help, -h          显示此帮助信息

示例:
    $0                              # 生成今天的日报
    $0 --date 2026-03-25            # 生成指定日期的日报
    $0 --verbose                    # 显示详细执行日志
    $0 --no-summarize               # 快速运行，不生成摘要
    $0 --check                      # 检查所有信源

配置文件:
    配置文件: config/sources.yaml
    环境变量: .env
    输出目录: output/

EOF
}

# 检查环境
check_environment() {
    log_info "检查环境..."

    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        log_error "未找到 python3 命令"
        exit 1
    fi

    # 检查配置文件
    if [ ! -f "config/sources.yaml" ]; then
        log_error "未找到配置文件: config/sources.yaml"
        exit 1
    fi

    # 检查 .env 文件
    if [ ! -f ".env" ]; then
        log_warning "未找到 .env 文件，将使用系统环境变量"
        log_info "如需配置，请复制 .env.example 到 .env 并填写相关信息"
    fi

    # 检查依赖
    if [ ! -d "venv" ] && ! python3 -c "import yaml" &> /dev/null; then
        log_warning "未检测到虚拟环境或依赖未安装"
        read -p "是否安装依赖? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_dependencies
        fi
    fi

    log_success "环境检查通过"
}

# 安装依赖
install_dependencies() {
    log_info "安装 Python 依赖..."

    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        log_info "创建虚拟环境..."
        python3 -m venv venv
    fi

    # 激活虚拟环境
    source venv/bin/activate

    # 安装依赖
    pip install -r requirements.txt

    if [ $? -eq 0 ]; then
        log_success "依赖安装成功"
    else
        log_error "依赖安装失败"
        exit 1
    fi
}

# 运行主程序
run_main() {
    local extra_args="$1"

    log_info "启动 AI 日报生成系统..."

    # 检查是否在虚拟环境中
    if [ -d "venv" ] && [ -z "$VIRTUAL_ENV" ]; then
        log_info "激活虚拟环境..."
        source venv/bin/activate
    fi

    # 运行主程序
    python3 src/main.py $extra_args

    if [ $? -eq 0 ]; then
        log_success "AI 日报生成成功"

        # 显示生成的文件
        today=$(date +%Y-%m-%d)
        if [ -f "output/ai-news-$today.html" ]; then
            log_info "生成的文件: output/ai-news-$today.html"
        fi
    else
        log_error "AI 日报生成失败"
        exit 1
    fi
}

# 检查信源
check_sources() {
    log_info "检查所有信源..."

    if [ -d "venv" ] && [ -z "$VIRTUAL_ENV" ]; then
        source venv/bin/activate
    fi

    python3 -c "
import sys
import yaml
from src.fetchers import RSSFetcher, HTMLFetcher, validate_rss_sources, validate_html_sources

# 加载配置
with open('config/sources.yaml', 'r') as f:
    config = yaml.safe_load(f)

rss_sources = config.get('rss_sources', [])
html_sources = config.get('html_sources', [])

print(f'\n检查 {len(rss_sources)} 个 RSS 源...')
rss_results = validate_rss_sources(rss_sources)

for source, is_valid, error in rss_results:
    status = '✓' if is_valid else '✗'
    print(f'  {status} {source[\"name\"]} ({source[\"url\"]})')
    if not is_valid:
        print(f'    错误: {error}')

print(f'\n检查 {len(html_sources)} 个 HTML 源...')
html_results = validate_html_sources(html_sources)

for source, is_valid, error in html_results:
    status = '✓' if is_valid else '✗'
    print(f'  {status} {source[\"name\"]} ({source[\"url\"]})')
    if not is_valid:
        print(f'    错误: {error}')

valid_rss = sum(1 for _, is_valid, _ in rss_results if is_valid)
valid_html = sum(1 for _, is_valid, _ in html_results if is_valid)

print(f'\n总结:')
print(f'  RSS 源: {valid_rss}/{len(rss_sources)} 有效')
print(f'  HTML 源: {valid_html}/{len(html_sources)} 有效')

if valid_rss + valid_html == 0:
    print('\n⚠  警告: 没有有效的信源！')
    sys.exit(1)
elif valid_rss + valid_html < len(rss_sources) + len(html_sources):
    print('\n⚠  警告: 部分信源无效，请检查配置')
    sys.exit(1)
else:
    print('\n✓ 所有信源都有效')
"

    if [ $? -ne 0 ]; then
        exit 1
    fi
}

# 主逻辑
main() {
    # 默认参数
    EXTRA_ARGS=""

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --date)
                EXTRA_ARGS="$EXTRA_ARGS --date $2"
                shift 2
                ;;
            --verbose|-v)
                EXTRA_ARGS="$EXTRA_ARGS --verbose"
                shift
                ;;
            --no-summarize)
                EXTRA_ARGS="$EXTRA_ARGS --no-summarize"
                shift
                ;;
            --check)
                check_environment
                check_sources
                exit 0
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # 检查环境
    check_environment

    # 运行主程序
    run_main "$EXTRA_ARGS"
}

# 脚本入口
main "$@"
