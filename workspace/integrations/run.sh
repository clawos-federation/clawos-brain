#!/bin/bash
# OpenClaw Enterprise System - Quick Start

set -e

WORKSPACE="/Users/henry/openclaw-system/workspace"
INTEGRATIONS="$WORKSPACE/integrations"

echo "🚀 OpenClaw Enterprise System"
echo "========================================"
echo ""

# 检查参数
if [ $# -eq 0 ]; then
    echo "Usage:"
    echo "  ./run.sh demo              # 运行演示"
    echo "  ./run.sh test              # 运行测试套件"
    echo "  ./run.sh 'your task'       # 处理单个任务"
    echo ""
    echo "Examples:"
    echo "  ./run.sh 'write a README file'"
    echo "  ./run.sh 'build a customer portal'"
    exit 1
fi

# 切换目录
cd "$INTEGRATIONS"

# 根据参数执行
if [ "$1" == "demo" ]; then
    echo "🎯 Running Demo..."
    python3 test_suite.py --demo
elif [ "$1" == "test" ]; then
    echo "🧪 Running Test Suite..."
    python3 test_suite.py --test
else
    # 处理单个任务
    TASK="$@"
    echo "📩 Processing: $TASK"
    echo ""
    python3 coordinator.py "$TASK"
fi

echo ""
echo "✅ Done!"
