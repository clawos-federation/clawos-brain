#!/bin/bash
#
# shenbao 相关目录清理脚本
# 专门清理 shenbao 和 shenbao_audit 项目的缓存和临时文件
#

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
HOME_DIR="/Users/henry"
LOG_FILE="$HOME_DIR/openclaw-system/workspace/shenbao_cleanup_log_$(date +%Y%m%d_%H%M%S).txt"

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
    echo -e "${BLUE}  shenbao 目录清理脚本${NC}"
    echo -e "${BLUE}  清理时间: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo ""
}

# 显示将要清理的内容
show_cleanup_plan() {
    echo -e "${YELLOW}=== 清理计划 ===${NC}"
    echo ""
    echo -e "${GREEN}1. shenbao 项目缓存清理${NC}"
    echo "   - 清理 .pytest_cache/"
    echo "   - 清理 .coverage"
    echo "   - 清理 src/**/__pycache__/"
    echo "   - 清理 tests/**/__pycache__/"
    echo ""
    echo -e "${GREEN}2. shenbao_audit 项目缓存清理${NC}"
    echo "   - 清理 .pytest_cache/"
    echo "   - 清理 .coverage"
    echo "   - 清理 src/**/__pycache__/"
    echo "   - 清理 tests/**/__pycache__/"
    echo ""
    echo -e "${GREEN}3. 日志文件清理${NC}"
    echo "   - 清理 src/logs/*.log (保留最近的)"
    echo "   - 清理空的日志文件"
    echo ""
    echo -e "${YELLOW}=== 预计节省空间: ~80KB ===${NC}"
    echo ""
    echo -e "${RED}⚠️  注意: 不会删除项目源代码、配置文件或重要文档${NC}"
    echo ""
}

# 询问确认
ask_confirmation() {
    echo -e "${RED}⚠️  警告：此操作将清理缓存文件！${NC}"
    echo ""
    echo -e "${YELLOW}请确认：${NC}"
    echo "  1. 已检查缓存清理内容？"
    echo "  2. 确认要执行清理？"
    echo ""
    read -p "输入 'yes' 继续清理，或按 Ctrl+C 取消: " confirmation

    if [ "$confirmation" != "yes" ]; then
        log "用户取消清理"
        exit 0
    fi
}

# 清理 shenbao 项目缓存
cleanup_shenbao() {
    log "开始清理 shenbao 项目缓存..."
    
    local deleted_count=0
    
    # 清理 Pytest 缓存
    if [ -d "$HOME_DIR/shenbao/.pytest_cache" ]; then
        log "删除 .pytest_cache/"
        rm -rf "$HOME_DIR/shenbao/.pytest_cache"
        deleted_count=$((deleted_count + 1))
    fi
    
    # 清理测试覆盖率
    if [ -f "$HOME_DIR/shenbao/.coverage" ]; then
        log "删除 .coverage"
        rm "$HOME_DIR/shenbao/.coverage"
        deleted_count=$((deleted_count + 1))
    fi
    
    # 清理 Python 编译缓存
    log "清理 __pycache__ 文件..."
    pycache_count=$(find "$HOME_DIR/shenbao" -type d -name "__pycache__" 2>/dev/null | wc -l)
    if [ "$pycache_count" -gt 0 ]; then
        find "$HOME_DIR/shenbao" -type d -name "__pycache__" -exec rm -rf {} \; 2>/dev/null
        deleted_count=$((deleted_count + 1))
    fi
    
    log "✅ shenbao 项目缓存清理完成（清理 $deleted_count 项）"
}

# 清理 shenbao_audit 项目缓存
cleanup_shenbao_audit() {
    log "开始清理 shenbao_audit 项目缓存..."
    
    local deleted_count=0
    
    # 清理 Pytest 缓存
    if [ -d "$HOME_DIR/shenbao_audit/.pytest_cache" ]; then
        log "删除 .pytest_cache/"
        rm -rf "$HOME_DIR/shenbao_audit/.pytest_cache"
        deleted_count=$((deleted_count + 1))
    fi
    
    # 清理测试覆盖率
    if [ -f "$HOME_DIR/shenbao_audit/.coverage" ]; then
        log "删除 .coverage"
        rm "$HOME_DIR/shenbao_audit/.coverage"
        deleted_count=$((deleted_count + 1))
    fi
    
    # 清理 Python 编译缓存
    log "清理 __pycache__ 文件..."
    pycache_count=$(find "$HOME_DIR/shenbao_audit" -type d -name "__pycache__" 2>/dev/null | wc -l)
    if [ "$pycache_count" -gt 0 ]; then
        find "$HOME_DIR/shenbao_audit" -type d -name "__pycache__" -exec rm -rf {} \; 2>/dev/null
        deleted_count=$((deleted_count + 1))
    fi
    
    log "✅ shenbao_audit 项目缓存清理完成（清理 $deleted_count 项）"
}

# 清理日志文件
cleanup_logs() {
    log "开始清理日志文件..."
    
    local deleted_count=0
    
    # 清理 shenbao 日志
    if [ -d "$HOME_DIR/shenbao/src/logs" ]; then
        log "清理 shenbao/src/logs/ 中的旧日志..."
        # 删除 7 天前的日志
        find "$HOME_DIR/shenbao/src/logs" -name "*.log" -type f -mtime +7 -delete 2>/dev/null
        # 删除空的日志文件
        find "$HOME_DIR/shenbao/src/logs" -name "*.log" -type f -size 0 -delete 2>/dev/null
        deleted_count=$(find "$HOME_DIR/shenbao/src/logs" -name "*.log" -type f 2>/dev/null | wc -l)
    fi
    
    # 清理 shenbao_audit 日志
    if [ -d "$HOME_DIR/shenbao_audit/src/logs" ]; then
        log "清理 shenbao_audit/src/logs/ 中的旧日志..."
        # 删除 7 天前的日志
        find "$HOME_DIR/shenbao_audit/src/logs" -name "*.log" -type f -mtime +7 -delete 2>/dev/null
        # 删除空的日志文件
        find "$HOME_DIR/shenbao_audit/src/logs" -name "*.log" -type f -size 0 -delete 2>/dev/null
        deleted_count=$(find "$HOME_DIR/shenbao_audit/src/logs" -name "*.log" -type f 2>/dev/null | wc -l)
    fi
    
    log "✅ 日志文件清理完成（保留 $deleted_count 个最近日志）"
}

# 显示清理后的统计
show_stats() {
    log "显示清理后统计..."
    
    shenbao_size=$(du -sh "$HOME_DIR/shenbao" 2>/dev/null)
    shenbao_audit_size=$(du -sh "$HOME_DIR/shenbao_audit" 2>/dev/null)
    
    echo ""
    echo -e "${BLUE}=== 清理后目录大小 ===${NC}"
    echo ""
    echo "shenbao:      $shenbao_size"
    echo "shenbao_audit: $shenbao_audit_size"
    echo ""
}

# 生成清理报告
generate_report() {
    echo ""
    echo -e "${GREEN}=== 清理完成 ===${NC}"
    echo ""
    echo "清理时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "日志文件: $LOG_FILE"
    echo ""
}

# 主函数
main() {
    banner
    
    # 检查目录是否存在
    if [ ! -d "$HOME_DIR/shenbao" ]; then
        error "shenbao 目录不存在: $HOME_DIR/shenbao"
        exit 1
    fi
    
    if [ ! -d "$HOME_DIR/shenbao_audit" ]; then
        error "shenbao_audit 目录不存在: $HOME_DIR/shenbao_audit"
        exit 1
    fi
    
    show_cleanup_plan
    ask_confirmation
    
    log "开始执行清理..."
    echo ""
    
    cleanup_shenbao
    echo ""
    
    cleanup_shenbao_audit
    echo ""
    
    cleanup_logs
    echo ""
    
    show_stats
    generate_report
    
    log "清理完成！"
}

# 执行主函数
main "$@"
