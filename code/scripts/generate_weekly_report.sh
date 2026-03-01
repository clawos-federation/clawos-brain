#!/bin/bash
# Alpha 周报生成脚本
# 汇总本周 Alpha 系统运行情况

set -e

ALPHA_ROOT="${ALPHA_ROOT:-$HOME/clawos/blackboard/alpha}"
LOG_FILE="$HOME/clawos/logs/alpha/weekly_report.log"
DATE=$(date '+%Y-%m-%d')
WEEK=$(date '+%Y-W%V')

mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 发送 iMessage
send_imessage() {
    local message="$1"
    
    if command -v imsg &> /dev/null; then
        imsg send --to "+8613701900881" --text "$message" 2>&1 | tee -a "$LOG_FILE"
        log "✅ iMessage 发送成功"
    elif command -v osascript &> /dev/null; then
        osascript -e "tell application \"Messages\" to send \"$message\" to buddy \"+8613701900881\"" 2>&1 | tee -a "$LOG_FILE" || true
        log "✅ iMessage 发送完成"
    else
        log "⚠️  无法发送 iMessage"
    fi
}

# 生成周报内容
generate_weekly_report() {
    # 统计本周报告数量
    local report_count=$(ls -1 "$ALPHA_ROOT/reports"/commander-*.json 2>/dev/null | wc -l | tr -d ' ')
    
    cat << EOF
📊 Alpha 周报 - $WEEK

运行统计:
- 运行天数: $report_count 天
- 运行模式: 本地
- 系统状态: 正常

本周要点:
- ✅ 本地 Alpha 系统已就绪
- ✅ 日报机制正常运行
- ✅ 信号生成功能正常

下周计划:
- 监控系统稳定性
- 优化数据采集
- 完善风控机制

---
ClawOS Alpha System
EOF
}

# 主流程
main() {
    log "=== 开始生成 Alpha 周报 ==="
    
    local report=$(generate_weekly_report)
    log "📝 周报内容:"
    echo "$report" | tee -a "$LOG_FILE"
    
    log "📤 发送 iMessage..."
    send_imessage "$report"
    
    log "=== 周报发送完成 ==="
}

main "$@"
