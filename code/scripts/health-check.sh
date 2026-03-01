#!/bin/bash
# ClawOS 快速健康检查

echo "🏥 ClawOS 健康检查"
echo "=================="

# 1. OpenClaw 状态
echo -e "\n1️⃣ OpenClaw 状态"
openclaw status 2>&1 | head -10

# 2. Federation 节点
echo -e "\n2️⃣ Federation 节点"
openclaw federation status 2>&1 | grep -E "server|coding|writing|quant|mobile" | head -10

# 3. Blackboard
echo -e "\n3️⃣ Blackboard 状态"
echo "  任务目录: $(ls ~/clawos/blackboard/tasks 2>/dev/null | wc -l) 个"
echo "  报告目录: $(ls ~/clawos/blackboard/reports 2>/dev/null | wc -l) 个"
echo "  共享目录: $(ls ~/clawos/blackboard/shared 2>/dev/null | wc -l) 个"

# 4. 记忆系统
echo -e "\n4️⃣ 记忆系统"
echo "  MEMORY.md: $(test -f ~/clawos/workspaces/MEMORY.md && echo "✅" || echo "❌")"
echo "  每日记忆: $(ls ~/clawos/workspaces/memory/*.md 2>/dev/null | wc -l) 个"

# 5. 脚本
echo -e "\n5️⃣ 自动化脚本"
echo "  daily-harvest.sh: $(test -f ~/.openclaw/clawos/clawos/scripts/daily-harvest.sh && echo "✅" || echo "❌")"
echo "  monitor.sh: $(test -f ~/.openclaw/clawos/clawos/scripts/monitor.sh && echo "✅" || echo "❌")"
echo "  generate-summary.sh: $(test -f ~/.openclaw/clawos/clawos/scripts/generate-summary.sh && echo "✅" || echo "❌")"

# 6. 配置
echo -e "\n6️⃣ 配置文件"
echo "  meta.json: $(test -f ~/.openclaw/clawos/clawos/config/meta.json && echo "✅" || echo "❌")"
echo "  model-mapping.json: $(test -f ~/.openclaw/clawos/clawos/config/model-mapping.json && echo "✅" || echo "❌")"

# 7. SOUL 文件
echo -e "\n7️⃣ SOUL 文件"
echo "  GM: $(test -f ~/.openclaw/clawos/clawos/souls/command/gm.soul.md && echo "✅" || echo "❌")"
echo "  validator: $(test -f ~/.openclaw/clawos/clawos/souls/command/validator.soul.md && echo "✅" || echo "❌")"
echo "  assistant: $(test -f ~/.openclaw/clawos/clawos/souls/command/assistant.soul.md && echo "✅" || echo "❌")"

# 8. 最近活动
echo -e "\n8️⃣ 最近活动"
echo "  最近任务: $(ls -t ~/clawos/blackboard/tasks 2>/dev/null | head -3)"
echo "  最近报告: $(ls -t ~/clawos/blackboard/reports 2>/dev/null | head -3)"

echo -e "\n✅ 检查完成"
