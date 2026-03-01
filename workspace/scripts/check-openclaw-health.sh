#!/bin/bash
# OpenClaw 系统健康检查脚本
# 用途: 全面检查 OpenClaw 系统状态
# 使用: ./scripts/check-openclaw-health.sh [--deep]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

DEEP_MODE=false
if [ "$1" == "--deep" ]; then
    DEEP_MODE=true
fi

echo "========================================="
echo "OpenClaw 系统健康检查"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
[ "$DEEP_MODE" = true ] && echo "模式: 深度检查"
echo "========================================="
echo

# 检查项计数器
PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    ((PASS_COUNT++))
}

fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    ((FAIL_COUNT++))
}

warn() {
    echo -e "${YELLOW}⚠ WARN${NC}: $1"
    ((WARN_COUNT++))
}

info() {
    echo -e "${BLUE}ℹ INFO${NC}: $1"
}

# 1. 检查 OpenClaw 安装
echo "--- 检查 1: OpenClaw 安装 ---"
if command -v openclaw &> /dev/null; then
    VERSION=$(openclaw --version 2>&1 | head -n1)
    pass "OpenClaw 已安装 ($VERSION)"
else
    fail "OpenClaw 未安装"
    exit 1
fi
echo

# 2. 检查 Gateway 服务
echo "--- 检查 2: Gateway 服务 ---"
if openclaw status 2>&1 | grep -q "running"; then
    PID=$(openclaw status 2>&1 | grep -oP 'pid \K[0-9]+')
    pass "Gateway 服务运行中 (PID: $PID)"
else
    fail "Gateway 服务未运行"
fi
echo

# 3. 检查配置文件
echo "--- 检查 3: 配置文件 ---"
CONFIG_FILE="$HOME/.openclaw/openclaw.json"
if [ -f "$CONFIG_FILE" ]; then
    pass "配置文件存在 ($CONFIG_FILE)"
    
    # 检查配置是否有效
    if openclaw config get &> /dev/null; then
        pass "配置文件格式正确"
    else
        fail "配置文件格式错误"
    fi
else
    fail "配置文件不存在"
fi
echo

# 4. 检查 Agent 状态
echo "--- 检查 4: Agent 状态 ---"
AGENT_COUNT=$(openclaw status 2>&1 | grep -oP 'Agents.*?\K[0-9]+' || echo "0")
if [ "$AGENT_COUNT" -gt 0 ]; then
    pass "已配置 $AGENT_COUNT 个 Agent"
    
    # 列出活跃的 agents
    ACTIVE_AGENTS=$(openclaw status 2>&1 | grep "agent:" | awk '{print $1}' | sed 's/agent://' | head -5)
    if [ -n "$ACTIVE_AGENTS" ]; then
        info "活跃 Agents: $(echo $ACTIVE_AGENTS | tr '\n' ' ')"
    fi
else
    warn "未配置任何 Agent"
fi
echo

# 5. 检查安全状态
echo "--- 检查 5: 安全状态 ---"
SECURITY_OUTPUT=$(openclaw security audit 2>&1)
CRITICAL_COUNT=$(echo "$SECURITY_OUTPUT" | grep -oP 'critical.*?\K[0-9]+' | head -1 || echo "0")
WARN_SECURITY=$(echo "$SECURITY_OUTPUT" | grep -oP 'warn.*?\K[0-9]+' | head -1 || echo "0")

if [ "$CRITICAL_COUNT" -eq 0 ]; then
    pass "无严重安全问题"
else
    fail "发现 $CRITICAL_COUNT 个严重安全问题"
fi

if [ "$WARN_SECURITY" -gt 0 ]; then
    warn "发现 $WARN_SECURITY 个安全警告"
fi
echo

# 6. 检查通道状态
echo "--- 检查 6: 通道状态 ---"
CHANNELS_OUTPUT=$(openclaw status 2>&1 | grep -A20 "Channels")
ENABLED_CHANNELS=$(echo "$CHANNELS_OUTPUT" | grep "ON" | awk '{print $2}')

if [ -n "$ENABLED_CHANNELS" ]; then
    pass "启用的通道: $ENABLED_CHANNELS"
else
    info "未启用任何通道"
fi
echo

# 7. 检查 Memory 系统
echo "--- 检查 7: Memory 系统 ---"
MEMORY_STATUS=$(openclaw status 2>&1 | grep -A2 "Memory" | head -3)
if echo "$MEMORY_STATUS" | grep -q "enabled"; then
    if echo "$MEMORY_STATUS" | grep -q "unavailable"; then
        warn "Memory 已启用但不可用 (可能需要配置 API key)"
    else
        pass "Memory 系统正常"
    fi
else
    info "Memory 系统未启用"
fi
echo

# 8. 深度检查（可选）
if [ "$DEEP_MODE" = true ]; then
    echo "--- 深度检查: 详细诊断 ---"
    
    # 检查 Node 版本
    NODE_VERSION=$(node --version 2>&1)
    info "Node 版本: $NODE_VERSION"
    
    # 检查磁盘空间
    DISK_USAGE=$(df -h "$HOME/.openclaw" | tail -1 | awk '{print $5}')
    info "磁盘使用率: $DISK_USAGE"
    
    # 检查最近的日志错误
    if openclaw logs --tail 50 2>&1 | grep -qi "error"; then
        warn "最近日志中存在错误"
    else
        pass "最近日志无明显错误"
    fi
    
    echo
fi

# 9. 检查更新
echo "--- 检查 8: 系统更新 ---"
if openclaw status 2>&1 | grep -q "Update available"; then
    warn "有可用更新"
    info "运行 'openclaw update' 进行更新"
else
    pass "已是最新版本"
fi
echo

# 总结
echo "========================================="
echo "健康检查结果汇总"
echo "========================================="
echo -e "${GREEN}通过: $PASS_COUNT${NC}"
echo -e "${RED}失败: $FAIL_COUNT${NC}"
echo -e "${YELLOW}警告: $WARN_COUNT${NC}"
echo

# 生成报告
REPORT_FILE="docs/health-check-$(date +%Y%m%d-%H%M%S).txt"
{
    echo "OpenClaw 健康检查报告"
    echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "通过: $PASS_COUNT | 失败: $FAIL_COUNT | 警告: $WARN_COUNT"
    echo "---"
    openclaw status
} > "$REPORT_FILE"

info "详细报告已保存到: $REPORT_FILE"
echo

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}✓ OpenClaw 系统健康状态良好${NC}"
    exit 0
else
    echo -e "${RED}✗ 发现 $FAIL_COUNT 个问题，请检查失败项${NC}"
    exit 1
fi
