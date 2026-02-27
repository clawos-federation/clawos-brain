# MacBook 配置 - 快速调整

**前提**: 已复制 `/Users/dongshenglu/openclaw-system`
**需要做的**: 3 个小调整（2 分钟）

---

## 在 MacBook 上执行：

### 1. 修改 IDENTITY（标识为 mobile 节点）

```bash
cd ~/openclaw-system/clawos/workspaces

cat > IDENTITY.md << 'EOF'
# IDENTITY.md

- **Name:** ClawOS Mobile
- **Node ID:** mobile
- **Device:** MacBook
- **Role:** 移动办公节点
- **Federation:** ClawOS
- **Emoji:** 📱
EOF

echo "✅ IDENTITY 已更新"
```

---

### 2. 检查 OpenClaw 是否正常运行

```bash
# 测试
openclaw status
```

**预期输出**：应该显示 OpenClaw 正在运行

---

### 3. 测试对话

对 assistant 说：
```
"你好，我是移动节点"
```

**预期响应**：
```
你好！我是 ClawOS Mobile（移动节点）。
当前运行在 MacBook 上。
```

---

## ✅ 就这么简单！

因为你已经复制了整个系统，所以：
- ✅ 所有 SOUL 文件都在
- ✅ 所有配置都在
- ✅ 所有脚本都在
- ✅ Blackboard 结构都在

**只需要**：
1. 修改 IDENTITY（标识为 mobile）
2. 测试

---

## 🔄 同步（可选）

### 如果想保持两台机器同步：

```bash
# 方法 1: 使用 iCloud
# 将 openclaw-system 放到 iCloud 目录

# 方法 2: 使用 Git
cd ~/openclaw-system
git init
git add .
git commit -m "Initial"
# push 到 GitHub，然后在 Mac mini 上 pull

# 方法 3: 定期手动同步
# 需要更新时，从 Mac mini scp 过来
```

---

## 🎯 测试清单

- [ ] `openclaw status` 正常
- [ ] 对话测试成功
- [ ] 能读取 Blackboard
- [ ] MEMORY.md 正常

---

**预计时间**: 2 分钟
**难度**: 极低
