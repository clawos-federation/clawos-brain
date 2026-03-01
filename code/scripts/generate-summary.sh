#!/bin/bash
# 自动生成 summary.md

TASK_DIR=$1

if [ -z "$TASK_DIR" ]; then
    echo "用法: $0 <task-directory>"
    exit 1
fi

TASK_ID=$(basename $TASK_DIR)
SUMMARY_FILE="$TASK_DIR/summary.md"

# 检查是否已有 summary
if [ -f "$SUMMARY_FILE" ]; then
    echo "✅ Summary 已存在: $SUMMARY_FILE"
    exit 0
fi

# 检查任务文件
if [ ! -d "$TASK_DIR" ]; then
    echo "❌ 任务目录不存在: $TASK_DIR"
    exit 1
fi

# 生成 summary
cat > "$SUMMARY_FILE" << EOF
# ${TASK_ID} - 摘要

**任务ID**: ${TASK_ID}
**生成时间**: $(date '+%Y-%m-%d %H:%M')
**状态**: $(test -f "$TASK_DIR/status.md" && grep -i "complete\|done\|✅" "$TASK_DIR/status.md" > /dev/null && echo "✅ 完成" || echo "🚧 进行中")

---

## 一句话总结

$(test -f "$TASK_DIR/task.md" && head -5 "$TASK_DIR/task.md" || echo "任务描述待补充")

---

## 关键产出

$(find "$TASK_DIR" -name "*.md" -o -name "*.json" -o -name "*.py" -o -name "*.sh" | grep -v summary.md | while read file; do
    echo "| $(basename $file) | $file |"
done)

---

## 核心发现/变更

- {自动生成，待补充}

---

## 下一步建议

1. {自动生成，待补充}

---

## 完整报告

详见: $(ls $TASK_DIR/*.md | grep -v summary.md | head -1 || echo "待生成")

---
**自动生成 by ClawOS**
EOF

echo "✅ Summary 已生成: $SUMMARY_FILE"
