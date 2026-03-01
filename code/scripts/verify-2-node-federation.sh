#!/bin/bash
# 验证 2 节点协同

echo "🧪 ClawOS 2节点协同验证"
echo "========================"
echo ""

SERVER_IP="100.76.189.39"
CODING_IP="100.71.170.104"

echo "1️⃣ Tailscale 连接测试"
echo "--------------------"
tailscale status | grep -E "$SERVER_IP|$CODING_IP"
echo ""

echo "2️⃣ 网络连通性测试"
echo "--------------------"
echo "Mac mini → MacBook:"
nc -zv $CODING_IP 22 2>&1 | head -1

echo "MacBook → Mac mini:"
ssh dongshenglu@$CODING_IP "nc -zv $SERVER_IP 22" 2>&1 | head -1 || echo "  (需要密码认证)"
echo ""

echo "3️⃣ 节点状态"
echo "--------------------"
cat ~/clawos/blackboard/shared/node-status.json 2>/dev/null | python3 -c "
import sys, json
d = json.load(sys.stdin)
for nid, n in d.get('nodes', {}).items():
    status = n.get('status', 'unknown')
    ip = n.get('tailscaleIp', 'N/A')
    device = n.get('device', 'unknown')
    print(f'  {nid}: {status} ({device}) - {ip}')
" 2>/dev/null || echo "  读取失败"
echo ""

echo "4️⃣ 同步测试"
echo "--------------------"
echo "尝试 rsync dry-run..."
rsync -avn --delete dongshenglu@$CODING_IP:~/clawos/blackboard/ ~/clawos/blackboard/coding-sync/ 2>&1 | tail -5 || echo "  需要配置 SSH key"
echo ""

echo "✅ 验证完成"
echo ""
echo "下一步:"
echo "  1. 在 MacBook 运行: ~/clawos/scripts/start-coding-node.sh"
echo "  2. 提交代码任务测试路由"
