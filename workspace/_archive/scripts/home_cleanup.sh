#!/bin/bash
#
# HOME 根目录深度清理脚本 - 方案B（深度清理）
# 直接删除临时文件，不归档
# 包含确认步骤和日志
#

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
HOME_DIR="${HOME:-$(eval echo ~)}"
LOG_FILE="$HOME_DIR/openclaw-system/workspace/cleanup_log_$(date +%Y%m%d_%H%M%S).txt"

# 日志函数
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# 显示横幅
banner() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}  $HOME_DIR 根目录深度清理脚本${NC}"
    echo -e "${BLUE}  方案B: 深度清理${NC}"
    echo -e "${BLUE}  清理时间: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo ""
}

# 显示将要清理的内容
show_cleanup_plan() {
    echo -e "${YELLOW}=== 清理计划 ===${NC}"
    echo ""
    echo -e "${GREEN}1. 系统缓存清理 (~9.9GB)${NC}"
    echo "   - 清理 .cache/ 目录"
    echo "   - 可重新构建，无风险"
    echo ""

    echo -e "${GREEN}2. macOS 系统文件清理${NC}"
    echo "   - 清理所有 .DS_Store 文件"
    echo "   - macOS 会自动重建"
    echo ""

    echo -e "${GREEN}3. 历史文件清理${NC}"
    echo "   - 删除 .Rhistory"
    echo "   - 删除 .autodarwin_history"
    echo "   - 删除 .cooragent_history"
    echo "   - 删除 .claude.json.backup"
    echo ""

    echo -e "${RED}4. 临时文件直接删除${NC}"
    echo "   - 删除第四次开物革命相关文件"
    echo "   - 删除临时脚本（*.py, *.txt, *.csv）"
    echo ""

    echo -e "${GREEN}5. 不再使用的工具清理${NC}"
    echo "   - 删除 .EasyOCR"
    echo "   - 删除 .antigravity"
    echo "   - 删除 .cherrystudio"
    echo "   - 删除 .codex"
    echo "   - 删除 .crawl4ai"
    echo "   - 删除 .doppler"
    echo "   - 删除 .eva_cache"
    echo "   - 删除 .expo"
    echo ""

    echo -e "${GREEN}6. 空项目目录清理${NC}"
    echo "   - 删除 workspace/（空或已迁移）"
    echo "   - 删除 react-demo/"
    echo "   - 删除 metagpt_output/"
    echo "   - 删除 cookiecutters/"
    echo "   - 删除 embedchain/"
    echo ""

    echo -e "${YELLOW}=== 预计节省空间: ~10.1GB ===${NC}"
    echo ""
}

# 询问确认
ask_confirmation() {
    echo -e "${RED}⚠️  警告：此操作将删除文件！${NC}"
    echo ""
    echo -e "${YELLOW}请确认：${NC}"
    echo "  1. 已备份重要文件？"
    echo "  2. 已检查临时脚本是否有用的代码？"
    echo "  3. 确认要执行清理？"
    echo ""
    read -p "输入 'yes' 继续清理，或按 Ctrl+C 取消: " confirmation

    if [ "$confirmation" != "yes" ]; then
        log "用户取消清理"
        exit 0
    fi
}

# 1. 清理系统缓存
cleanup_cache() {
    log "开始清理系统缓存..."
    CACHE_DIR="$HOME_DIR/.cache"

    if [ -d "$CACHE_DIR" ]; then
        cache_size=$(du -sh "$CACHE_DIR" | cut -f1)
        log "当前缓存大小: $cache_size"
        log "清理前备份缓存列表..."
        ls -lah "$CACHE_DIR" >> "$LOG_FILE"

        rm -rf "$CACHE_DIR/"*
        log "✅ 缓存清理完成（节省 $cache_size）"
    else
        warn ".cache/ 目录不存在，跳过"
    fi
}

# 2. 清理 .DS_Store 文件
cleanup_ds_store() {
    log "开始清理 .DS_Store 文件..."

    ds_store_count=$(find "$HOME_DIR" -name ".DS_Store" -type f 2>/dev/null | wc -l)
    log "找到 $ds_store_count 个 .DS_Store 文件"

    if [ "$ds_store_count" -gt 0 ]; then
        find "$HOME_DIR" -name ".DS_Store" -delete 2>/dev/null
        log "✅ .DS_Store 文件清理完成（删除 $ds_store_count 个文件）"
    else
        log "未找到 .DS_Store 文件"
    fi
}

# 3. 清理历史文件
cleanup_history() {
    log "开始清理历史文件..."

    files_to_delete=(
        "$HOME_DIR/.Rhistory"
        "$HOME_DIR/.autodarwin_history"
        "$HOME_DIR/.cooragent_history"
        "$HOME_DIR/.claude.json.backup"
    )

    deleted_count=0
    for file in "${files_to_delete[@]}"; do
        if [ -f "$file" ]; then
            log "删除: $file"
            rm "$file"
            deleted_count=$((deleted_count + 1))
        fi
    done

    log "✅ 历史文件清理完成（删除 $deleted_count 个文件）"
}

# 4. 删除临时文件
delete_temp_files() {
    log "开始删除临时文件..."

    # 删除 PDF 文件（第四次开物革命）
    pdf_count=0
    for pdf_file in "$HOME_DIR"/第四次开物革命*; do
        if [ -f "$pdf_file" ]; then
            log "删除: $(basename "$pdf_file")"
            rm "$pdf_file"
            pdf_count=$((pdf_count + 1))
        fi
    done
    log "✅ PDF 文件删除完成（删除 $pdf_count 个文件）"

    # 删除临时脚本
    script_count=0
    for script_file in "$HOME_DIR"/*.py "$HOME_DIR"/*.txt "$HOME_DIR"/*.csv; do
        if [ -f "$script_file" ]; then
            filename=$(basename "$script_file")

            # 跳过特殊文件
            case "$filename" in
                implementation_plan.md|project-kickoff-checklist.md|第四次开物革命*)
                    continue
                    ;;
            esac

            log "删除: $filename"
            rm "$script_file"
            script_count=$((script_count + 1))
        fi
    done
    log "✅ 临时脚本删除完成（删除 $script_count 个文件）"
}

# 5. 清理不再使用的工具
cleanup_old_tools() {
    log "开始清理不再使用的工具..."

    tools_to_delete=(
        "$HOME_DIR/.EasyOCR"
        "$HOME_DIR/.antigravity"
        "$HOME_DIR/.cherrystudio"
        "$HOME_DIR/.codex"
        "$HOME_DIR/.crawl4ai"
        "$HOME_DIR/.doppler"
        "$HOME_DIR/.eva_cache"
        "$HOME_DIR/.expo"
    )

    deleted_count=0
    for tool_dir in "${tools_to_delete[@]}"; do
        if [ -d "$tool_dir" ]; then
            tool_size=$(du -sh "$tool_dir" | cut -f1)
            log "删除: $(basename "$tool_dir") ($tool_size)"
            rm -rf "$tool_dir"
            deleted_count=$((deleted_count + 1))
        fi
    done

    log "✅ 旧工具清理完成（删除 $deleted_count 个目录）"
}

# 6. 清理空项目目录
cleanup_empty_dirs() {
    log "开始清理空项目目录..."

    empty_dirs=(
        "$HOME_DIR/workspace"
        "$HOME_DIR/react-demo"
        "$HOME_DIR/metagpt_output"
        "$HOME_DIR/cookiecutters"
        "$HOME_DIR/embedchain"
        "$HOME_DIR/nltk_data"
    )

    deleted_count=0
    for dir_path in "${empty_dirs[@]}"; do
        if [ -d "$dir_path" ]; then
            # 检查目录是否为空
            file_count=$(find "$dir_path" -type f | wc -l)
            if [ "$file_count" -eq 0 ]; then
                log "删除空目录: $(basename "$dir_path")"
                rm -rf "$dir_path"
                deleted_count=$((deleted_count + 1))
            else
                warn "目录 $(basename "$dir_path") 不为空（$file_count 个文件），跳过"
            fi
        fi
    done

    log "✅ 空目录清理完成（删除 $deleted_count 个目录）"
}

# 生成清理报告
generate_report() {
    echo ""
    echo -e "${GREEN}=== 清理完成 ===${NC}"
    echo ""
    echo "清理时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "日志文件: $LOG_FILE"
    echo ""

    # 显示清理后的目录大小
    echo "清理后目录大小："
    for dir in .claude .cursor .cache; do
        if [ -d "$HOME_DIR/$dir" ]; then
            size=$(du -sh "$HOME_DIR/$dir" | cut -f1)
            echo "  $dir: $size"
        fi
    done
}

# 主函数
main() {
    banner

    # 检查是否在正确的目录
    if [ "$HOME" != "$HOME_DIR" ]; then
        error "脚本配置的 HOME_DIR 与实际 HOME 不匹配"
        error "请检查脚本中的 HOME_DIR 配置"
        exit 1
    fi

    show_cleanup_plan
    ask_confirmation

    log "开始执行清理..."
    echo ""

    cleanup_cache
    echo ""

    cleanup_ds_store
    echo ""

    cleanup_history
    echo ""

    delete_temp_files
    echo ""

    cleanup_old_tools
    echo ""

    cleanup_empty_dirs
    echo ""

    generate_report

    log "清理完成！"
}

# 执行主函数
main "$@"
