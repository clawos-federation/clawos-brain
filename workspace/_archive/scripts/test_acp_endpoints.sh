#!/bin/bash
# 测试 ACP 服务器的端点

ACPPID=""
trap 'kill $ACPPID 2>/dev/null; exit' EXIT

# 启动 ACP 服务器
~/.opencode/bin/opencode acp --port 4101 2>&1 &
ACPPID=$!
echo "ACP Server PID: $ACPPID"

# 等待服务器启动
echo "Waiting for server to start..."
sleep 5

# 测试端点
echo ""
echo "=== Testing ACP Endpoints ==="
echo ""

echo "1. GET /global/event"
curl -s -i http://127.0.0.1:4101/global/event
echo ""
echo ""

echo "2. GET /"
curl -s -i http://127.0.0.1:4101/ 2>&1 | head -20
echo ""

echo "3. GET /health"
curl -s -i http://127.0.0.1:4101/health 2>&1
echo ""

echo "4. GET /api"
curl -s -i http://127.0.0.1:4101/api 2>&1 | head -20
echo ""

echo "5. GET /v1"
curl -s -i http://127.0.0.1:4101/v1 2>&1 | head -20
echo ""

echo "6. GET /sessions"
curl -s -i http://127.0.0.1:4101/sessions 2>&1 | head -20
echo ""

echo "7. GET /agents"
curl -s -i http://127.0.0.1:4101/agents 2>&1 | head -20
echo ""

echo "8. OPTIONS /*"
curl -s -i -X OPTIONS http://127.0.0.1:4101/ 2>&1 | head -20
echo ""

echo "Done"
