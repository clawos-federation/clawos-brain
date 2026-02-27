# MacBook 配置指南（实际方案）

**时间**: 2026-02-26 20:05
**方案**: 独立节点 + 手动同步

---

## 方案说明

**ClawOS Federation 架构**：
- 每个节点独立运行 OpenClaw
- 通过共享 Blackboard 同步数据
- 通过 GitHub 同步记忆

**不需要 token**：直接使用文件同步

---

## 配置步骤（5 分钟）

### 步骤 1: 在 MacBook 上安装 OpenClaw（1 分钟）

```bash
# 安装
brew install openclaw

# 初始化
openclaw init
```

---

### 步骤 2: 创建基础文件（2 分钟）

在 MacBook 上执行：

```bash
# 创建目录
mkdir -p ~/clawos/{workspaces,blackboard/{tasks,gm,shared,roles},memory}

# 创建 IDENTITY.md
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

echo "✅ 基础配置完成"
```

---

### 步骤 3: 同步 Blackboard（2 分钟）

**方法 A: 使用云同步（推荐）**

如果使用 iCloud/Dropbox：

```bash
# 在 MacBook 上
# 假设 Mac mini 的 clawos 在 iCloud 中
ln -s ~/Library/Mobile\ Documents/com~apple~CloudDocs/clawos/blackboard ~/clawos/blackboard
```

**方法 B: 手动复制关键文件**

```bash
# 从 Mac mini 复制到 MacBook
# 在 MacBook 上执行：
scp -r dongsheng@dongsheng-mac-mini.local:~/clawos/blackboard/shared ~/clawos/blackboard/
```

**方法 C: 使用 Git（最佳）**

```bash
# 在 MacBook 上
cd ~/clawos
git clone https://github.com/your-username/clawos-blackboard.git blackboard
```

---

### 步骤 4: 测试（1 分钟）

在 MacBook 上：

```bash
# 检查 OpenClaw
openclaw status

# 测试 assistant
# 对 assistant 说："你好"
```

---

## 同步策略

### Blackboard 同步

**推荐**: 使用 Git

```bash
# 在 Mac mini 上（主脑）
cd ~/clawos/blackboard
git init
git add .
git commit -m "Initial blackboard"
git remote add origin https://github.com/your-username/clawos-blackboard.git
git push -u origin main

# 在 MacBook 上
cd ~/clawos
git clone https://github.com/your-username/clawos-blackboard.git blackboard

# 日常同步（在 MacBook 上）
cd ~/clawos/blackboard
git pull  # 拉取主脑更新
git add .
git commit -m "Mobile updates"
git push  # 推送到主脑
```

---

### 记忆同步

**自动**: 通过 MEMORY.md（在 Git 中）

**手动**: 复制文件

```bash
# 在 MacBook 上
scp dongsheng@dongsheng-mac-mini.local:~/clawos/workspaces/MEMORY.md ~/clawos/workspaces/
```

---

## 使用场景

### MacBook 独立使用

- 随时和 assistant 对话
- 处理轻量级任务
- 信息收集和汇总

### 与主脑协作

- 读取主脑的 Blackboard 数据
- 提交任务到主脑（通过 Git）
- 接收主脑的结果

---

## 简化版（最快）

如果只想快速测试，只需：

```bash
# 1. 安装
brew install openclaw

# 2. 初始化
openclaw init

# 3. 创建最小配置
mkdir -p ~/clawos/workspaces
cat > ~/clawos/workspaces/IDENTITY.md << 'EOF'
- **Name:** ClawOS Mobile
- **Node ID:** mobile
EOF

# 4. 测试
# 对 assistant 说："你好"
```

---

## 下一步

1. 选择同步方式（Git/iCloud/手动）
2. 在 MacBook 上执行配置
3. 测试对话
4. 验证同步

---

**方案**: 独立节点 + 文件同步
**预计时间**: 5 分钟
**难度**: 低
