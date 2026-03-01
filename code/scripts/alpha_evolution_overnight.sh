#!/bin/bash
# Alpha 夜间进化脚本
# 每小时运行一次，执行进化任务

set -e

ALPHA_ROOT="${ALPHA_ROOT:-$HOME/clawos/blackboard/alpha}"
LOG_FILE="${LOG_FILE:-$HOME/clawos/evolution/logs/overnight.log}"
DATE=$(date '+%Y-%m-%d')
HOUR=$(date '+%H')

mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 进化任务
run_evolution() {
    log "🧬 执行进化任务..."
    
    # 1. 清理过期数据
    log "  🧹 清理过期数据..."
    find "$ALPHA_ROOT/reports" -name "*.json" -mtime +7 -delete 2>/dev/null || true
    find "$ALPHA_ROOT/signals" -name "*.json" -mtime +3 -delete 2>/dev/null || true
    log "    ✅ 清理完成"
    
    # 2. 更新心跳
    log "  🫀 更新心跳..."
    if [ -f "$HOME/openclaw-system/clawos/scripts/ping-and-learn.sh" ]; then
        "$HOME/openclaw-system/clawos/scripts/ping-and-learn.sh" >> "$LOG_FILE" 2>&1 || true
    fi
    log "    ✅ 心跳更新完成"
    
    # 3. 记录状态
    log "  📊 记录系统状态..."
    local status_file="$ALPHA_ROOT/reports/evolution-$DATE-$HOUR.json"
    cat > "$status_file" << EOF
{
  "timestamp": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')",
  "type": "evolution",
  "hour": "$HOUR",
  "status": "ok"
}
EOF
    log "    ✅ 状态已记录"
}

# 主流程
main() {
    log "=== Alpha 夜间进化 开始 ==="
    
    run_evolution
    
    log "=== Alpha 夜间进化 完成 ==="
}

main "$@"
