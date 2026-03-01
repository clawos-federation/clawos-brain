#!/bin/bash
# iMessage 通道健康检查脚本
# 用途: 验证 iMessage 通道的可用性
# 使用: ./scripts/check-imessage.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================="
echo "iMessage 通道健康检查"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================="
echo

# 检查项计数器
PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

# 函数：检查通过
pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    ((PASS_COUNT++))
}

# 函数：检查失败
fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    ((FAIL_COUNT++))
}

# 函数：警告
warn() {
    echo -e "${YELLOW}⚠ WARN${NC}: $1"
    ((WARN_COUNT++))
}

# 1. 检查 imsg CLI 是否存在
echo "--- 检查 1: imsg CLI ---"
if command -v imsg &> /dev/null; then
    VERSION=$(imsg --version 2>&1)
    pass "imsg CLI 已安装 (版本: $VERSION)"
else
    fail "imsg CLI 未安装"
    exit 1
fi
echo

# 2. 检查 OpenClaw iMessage 通道状态
echo "--- 检查 2: OpenClaw 通道配置 ---"
if openclaw status 2>&1 | grep -q "iMessage.*ON.*OK"; then
    pass "OpenClaw iMessage 通道状态正常"
else
    fail "OpenClaw iMessage 通道状态异常"
fi
echo

# 3. 检查数据库访问权限
echo "--- 检查 3: 数据库访问 ---"
DB_PATH="$HOME/Library/Messages/chat.db"
if [ -r "$DB_PATH" ]; then
    pass "Messages 数据库可读 ($DB_PATH)"
else
    fail "Messages 数据库不可读 (需要 Full Disk Access)"
fi
echo

# 4. 测试读取最近对话
echo "--- 检查 4: 读取对话历史 ---"
if imsg chats --limit 1 --json &> /dev/null; then
    CHAT_COUNT=$(imsg chats --limit 10 --json 2>/dev/null | wc -l)
    pass "成功读取对话历史 (最近 $CHAT_COUNT 条)"
else
    fail "无法读取对话历史"
fi
echo

# 5. 测试发送功能（可选）
echo "--- 检查 5: 发送功能测试 ---"
read -p "是否测试发送功能？(y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "输入测试收件人 (邮箱/手机号): " RECIPIENT
    TEST_MSG="[OpenClaw健康检查] 测试消息 $(date '+%H:%M:%S')"
    
    if imsg send --to "$RECIPIENT" --text "$TEST_MSG" 2>&1 | grep -q "sent"; then
        pass "消息发送成功"
        echo "  收件人: $RECIPIENT"
        echo "  内容: $TEST_MSG"
    else
        fail "消息发送失败"
    fi
else
    warn "跳过发送功能测试"
fi
echo

# 6. 检查配对状态
echo "--- 检查 6: OpenClaw 配对状态 ---"
PAIRING_FILE="$HOME/.openclaw/pairings.json"
if [ -f "$PAIRING_FILE" ]; then
    PAIRED_COUNT=$(grep -c "imessage" "$PAIRING_FILE" 2>/dev/null || echo "0")
    if [ "$PAIRED_COUNT" -gt 0 ]; then
        pass "已配对 $PAIRED_COUNT 个 iMessage 发送者"
    else
        warn "未找到 iMessage 配对记录"
    fi
else
    warn "配对文件不存在"
fi
echo

# 总结
echo "========================================="
echo "检查结果汇总"
echo "========================================="
echo -e "${GREEN}通过: $PASS_COUNT${NC}"
echo -e "${RED}失败: $FAIL_COUNT${NC}"
echo -e "${YELLOW}警告: $WARN_COUNT${NC}"
echo

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}✓ iMessage 通道健康状态良好${NC}"
    exit 0
else
    echo -e "${RED}✗ iMessage 通道存在问题，请检查失败项${NC}"
    exit 1
fi
