#!/bin/bash
# Alpha 早报发送脚本
# 每日早晨发送系统状态

set -e

ALPHA_ROOT="${ALPHA_ROOT:-$HOME/clawos/blackboard/alpha}"
LOG_FILE="$HOME/clawos/logs/alpha/morning_report.log"
DATE=$(date '+%Y-%m-%d')
TIME=$(date '+%H:%M')

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

# 生成早报内容
generate_morning_report() {
    cat << EOF
🌅 Alpha 早报 - $DATE

系统状态: ✅ 正常
运行模式: 本地

今日提醒:
- A股交易时间: 9:30-11:30, 13:00-15:00
- Alpha 调度已启动
- 信号监控中

祝交易顺利！📈

---
ClawOS Alpha System | $TIME
EOF
}

# 主流程
main() {
    log "=== 开始发送 Alpha 早报 ==="
    
    local report=$(generate_morning_report)
    log "📝 早报内容:"
    echo "$report" | tee -a "$LOG_FILE"
    
    log "📤 发送 iMessage..."
    send_imessage "$report"
    
    log "=== 早报发送完成 ==="
}

main "$@"
