#!/bin/bash
# ClawOS 自动收割脚本

DAILY_DIR=~/clawos/blackboard/harvest/$(date +%Y-%m-%d)
mkdir -p $DAILY_DIR

echo "🌾 ClawOS 每日收割 - $(date)"

# 1. 收割任务摘要
echo "📋 收割任务摘要..."
find ~/clawos/blackboard/tasks -name "summary.md" -newer ~/clawos/blackboard/harvest/last-run 2>/dev/null | while read file; do
    task_id=$(basename $(dirname $file))
    cp $file $DAILY_DIR/task-$task_id.md
done

# 2. 收割 GM 决策
echo "🧠 收割 GM 决策..."
if [ -f ~/clawos/blackboard/gm/decisions.md ]; then
    tail -100 ~/clawos/blackboard/gm/decisions.md > $DAILY_DIR/gm-decisions.md
fi

# 3. 收割优化记录
echo "⚡ 收割优化记录..."
find ~/clawos/blackboard/proposals -name "*.md" -newer ~/clawos/blackboard/harvest/last-run 2>/dev/null | while read file; do
    cp $file $DAILY_DIR/
done

# 4. 生成摘要
echo "📝 生成摘要..."
cat > $DAILY_DIR/README.md << EOF
# 每日收割 - $(date +%Y-%m-%d)

## 收割内容

- 任务摘要: $(ls $DAILY_DIR/task-*.md 2>/dev/null | wc -l) 个
- GM 决策: $(test -f $DAILY_DIR/gm-decisions.md && echo "✅" || echo "❌")
- 优化记录: $(ls $DAILY_DIR/*optimization*.md 2>/dev/null | wc -l) 个

## 提取精华

$(grep -h "## 建议\|## 下一步\|## 核心发现" $DAILY_DIR/*.md 2>/dev/null | head -20)

---
收割时间: $(date)
EOF

# 5. 更新最后运行时间
touch ~/clawos/blackboard/harvest/last-run

echo "✅ 收割完成: $DAILY_DIR"
