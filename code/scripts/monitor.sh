#!/bin/bash
# ClawOS 自动监控脚本

LOG_FILE=~/clawos/logs/monitor.log

echo "🔍 ClawOS 监控 - $(date)" | tee -a $LOG_FILE

# 1. 检查 OpenClaw 状态
echo "📊 OpenClaw 状态:" | tee -a $LOG_FILE
openclaw status 2>&1 | tee -a $LOG_FILE

# 2. 检查节点状态
echo -e "\n🌐 Federation 节点:" | tee -a $LOG_FILE
openclaw federation status 2>&1 | tee -a $LOG_FILE

# 3. 检查 Agent 运行
echo -e "\n🤖 运行中的 Agents:" | tee -a $LOG_FILE
openclaw agent list 2>&1 | tee -a $LOG_FILE

# 4. 检查 token 消耗
echo -e "\n💰 Token 消耗统计:" | tee -a $LOG_FILE
openclaw stats tokens 2>&1 | head -10 | tee -a $LOG_FILE

# 5. 检查 Blackboard
echo -e "\n📋 Blackboard 状态:" | tee -a $LOG_FILE
echo "  任务数: $(ls ~/clawos/blackboard/tasks 2>/dev/null | wc -l)" | tee -a $LOG_FILE
echo "  报告数: $(ls ~/clawos/blackboard/reports 2>/dev/null | wc -l)" | tee -a $LOG_FILE

# 6. 检查磁盘空间
echo -e "\n💾 磁盘空间:" | tee -a $LOG_FILE
df -h ~/clawos 2>&1 | tee -a $LOG_FILE

# 7. 检查最近错误
echo -e "\n⚠️  最近错误 (如果有):" | tee -a $LOG_FILE
tail -20 ~/clawos/logs/*.log 2>/dev/null | grep -i "error\|fail" | tail -5 | tee -a $LOG_FILE

echo -e "\n✅ 监控完成 - $(date)" | tee -a $LOG_FILE
