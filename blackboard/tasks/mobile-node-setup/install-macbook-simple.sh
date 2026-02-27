#!/bin/bash
# ClawOS MacBook 节点一键配置（简化版）

echo "🦞 ClawOS MacBook 节点配置"
echo "==========================="

# 检查 OpenClaw
if ! command -v openclaw &> /dev/null; then
    echo "📦 安装 OpenClaw..."
    brew install openclaw
fi

# 创建目录
echo "📁 创建目录..."
mkdir -p ~/clawos/{workspaces,config,blackboard/{tasks,gm,shared,roles},memory,logs}

# 创建 IDENTITY.md
echo "📝 创建 IDENTITY.md..."
cat > ~/clawos/workspaces/IDENTITY.md << 'EOF'
# IDENTITY.md

- **Name:** ClawOS Mobile
- **Node ID:** mobile
- **Device:** MacBook
- **Role:** 移动办公节点
- **Federation:** ClawOS
- **Emoji:** 📱
EOF

# 创建 USER.md
cat > ~/clawos/workspaces/USER.md << 'EOF'
# USER.md

- **Name:** Dongsheng Lu
- **What to call them:** dongsheng
- **Timezone:** Asia/Shanghai
EOF

# 创建 MEMORY.md
cat > ~/clawos/workspaces/MEMORY.md << 'EOF'
# MEMORY.md

## 关于人类
- **名字:** Dongsheng Lu
- **称呼:** dongsheng

## 关于我
- **名字:** ClawOS Mobile
- **身份:** 移动办公节点

## 黄金规则
1. 随时沟通
2. 子任务不等待
3. 不沉默
EOF

echo ""
echo "✅ 基础配置完成！"
echo ""
echo "📋 下一步："
echo "1. 在主脑生成 token:"
echo "   openclaw federation token generate --node mobile"
echo ""
echo "2. 创建 federation.json（将 token 粘贴进去）"
echo ""
echo "3. 测试连接:"
echo "   openclaw federation ping"
echo ""
