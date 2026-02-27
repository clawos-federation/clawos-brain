#!/bin/bash
# ClawOS MacBook 节点一键配置脚本

set -e

echo "🦞 ClawOS MacBook 节点配置"
echo "=========================="

# 检查是否已安装 OpenClaw
if ! command -v openclaw &> /dev/null; then
    echo "📦 安装 OpenClaw..."
    brew install openclaw
fi

# 检查 OpenClaw 版本
echo "✅ OpenClaw 版本: $(openclaw --version)"

# 初始化节点
echo "🔧 初始化节点..."
openclaw init --node mobile --federation ClawOS

# 创建工作空间
echo "📁 创建工作空间..."
mkdir -p ~/clawos/workspaces
mkdir -p ~/clawos/config
mkdir -p ~/clawos/blackboard/{tasks,gm,shared,roles}
mkdir -p ~/clawos/memory
mkdir -p ~/clawos/logs

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

---

## 特点

- 随身携带，随时在线
- 快速响应用户需求
- 轻量级任务处理

## 职责

- 用户交互
- 信息收集
- 跨节点协调
EOF

# 创建 USER.md
echo "📝 创建 USER.md..."
cat > ~/clawos/workspaces/USER.md << 'EOF'
# USER.md

- **Name:** Dongsheng Lu
- **What to call them:** dongsheng
- **Pronouns:** he/him
- **Timezone:** Asia/Shanghai
- **Notes:** ClawOS 创造者

## Context

- 正在进化 ClawOS 系统架构
- 开发各种功能节点
EOF

# 创建 MEMORY.md
echo "📝 创建 MEMORY.md..."
cat > ~/clawos/workspaces/MEMORY.md << 'EOF'
# MEMORY.md - 长期记忆

## 关于人类

- **名字:** Dongsheng Lu
- **称呼:** dongsheng
- **时区:** Asia/Shanghai
- **备注:** ClawOS 创造者

## 关于我

- **名字:** ClawOS Mobile
- **身份:** 移动办公节点
- **Federation:** ClawOS

---

## 工作模式

### Assistant 黄金规则

1. **随时和 Boss 沟通** —— 不能"忙碌不理用户"
2. **子任务不等待** —— 提交后继续聊天
3. **不上传下达后沉默** —— 保持沟通

---

_持续进化中..._
EOF

# 创建 Federation 配置
echo "🔗 配置 Federation 连接..."
read -p "请输入主脑地址 (默认: dongsheng-mac-mini.local): " BRAIN_URL
BRAIN_URL=${BRAIN_URL:-dongsheng-mac-mini.local}

read -p "请输入 Federation Token: " FED_TOKEN

cat > ~/clawos/config/federation.json << EOF
{
  "nodeId": "mobile",
  "federation": "ClawOS",
  "brain": {
    "url": "http://${BRAIN_URL}:3000",
    "token": "${FED_TOKEN}"
  },
  "sync": {
    "blackboard": "~/clawos/blackboard/",
    "memory": "~/clawos/memory/"
  },
  "agents": ["assistant", "platform-pm", "connector-research"],
  "model": "zai/glm-5"
}
EOF

# 测试连接
echo "🔌 测试连接..."
if ping -c 1 $BRAIN_URL &> /dev/null; then
    echo "✅ 网络连接成功"
else
    echo "⚠️  无法 ping 通主脑，请检查网络"
fi

# 同步 Blackboard（首次）
echo "📥 首次同步 Blackboard..."
if [ -d ~/clawos/blackboard ]; then
    echo "✅ Blackboard 已创建"
fi

# 完成
echo ""
echo "🎉 MacBook 节点配置完成！"
echo ""
echo "📋 下一步："
echo "1. 在主脑上生成 token: openclaw federation token generate --node mobile"
echo "2. 更新 federation.json 中的 token"
echo "3. 测试连接: openclaw federation ping"
echo "4. 启动 assistant: openclaw agent start assistant"
echo ""
echo "🦞 欢迎加入 ClawOS Federation！"
