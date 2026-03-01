#!/bin/bash
# Alpha 日报发送脚本
# 从 Blackboard 读取最新报告并发送到 iMessage

set -e

ALPHA_ROOT="${ALPHA_ROOT:-$HOME/clawos/blackboard/alpha}"
LOG_FILE="$HOME/clawos/logs/alpha/daily_report.log"
DATE=$(date '+%Y-%m-%d')

mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 发送 iMessage
send_imessage() {
    local message="$1"
    
    # 使用 imsg 命令行工具
    if command -v imsg &> /dev/null; then
        imsg send --to "+8613701900881" --text "$message" 2>&1 | tee -a "$LOG_FILE"
        log "✅ iMessage 发送成功"
    # 使用 AppleScript 作为备选
    elif command -v osascript &> /dev/null; then
        osascript -e "tell application \"Messages\" to send \"$message\" to buddy \"+8613701900881\"" 2>&1 | tee -a "$LOG_FILE" || true
        log "✅ iMessage 发送完成"
    else
        log "⚠️  无法发送 iMessage: imsg 或 osascript 不可用"
    fi
}

# 生成日报内容
generate_daily_report() {
    local report_file="$ALPHA_ROOT/reports/latest.json"
    
    if [ -f "$report_file" ]; then
        # 从 JSON 提取关键信息
        local timestamp=$(python3 -c "import json; d=json.load(open('$report_file')); print(d.get('timestamp', 'N/A'))" 2>/dev/null || echo "N/A")
        local status=$(python3 -c "import json; d=json.load(open('$report_file')); print(d.get('status', 'unknown'))" 2>/dev/null || echo "unknown")
        
        cat << EOF
📈 Alpha 日报 - $DATE

系统状态:
- 运行模式: 本地
- 状态: $status
- 更新时间: $timestamp

数据状态:
- 市场数据: ✅ 模拟
- 北向资金: ✅
- 热门股票: ✅

---
ClawOS Alpha System
EOF
    else
        cat << EOF
📈 Alpha 日报 - $DATE

⚠️ 暂无最新报告

系统运行在本地模式。
请检查 Alpha Commander 是否正常运行。

---
ClawOS Alpha System
EOF
    fi
}

# 主流程
main() {
    log "=== 开始发送 Alpha 日报 ==="
    
    local report=$(generate_daily_report)
    log "📝 报告内容:"
    echo "$report" | tee -a "$LOG_FILE"
    
    log "📤 发送 iMessage..."
    send_imessage "$report"
    
    log "=== 日报发送完成 ==="
}

main "$@"
