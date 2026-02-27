# ClawOS 新手指南

**适用**: 新节点、新用户、新 Agent

---

## 🚀 快速开始

### 1. 了解 ClawOS

**ClawOS 是什么？**

一个多节点协作的 AI Agent 系统：
- 多个节点（Mac mini, MacBook, Codespace 等）
- 每个 Agent 有专门角色（GM, PM, Workers）
- 通过 Blackboard 共享数据
- 通过 Federation 协调工作

**核心概念**：
- **Node**: 节点（一台设备）
- **Agent**: 代理（一个角色）
- **Blackboard**: 共享黑板（数据交换）
- **Federation**: 联邦（节点网络）

---

### 2. 理解架构

```
Federation (节点网络)
    ├── server (主脑)
    ├── coding (编程)
    ├── writing (写作)
    ├── quant (量化)
    └── mobile (移动)

每个节点：
    Command Layer (Opus) → PM Layer (GLM-5) → Workers (混合)
```

**层级职责**：
- **Command**: 决策、质检
- **PM**: 协调、整理
- **Workers**: 执行具体任务

---

### 3. 第一次对话

### 在主节点

```
你: "你好"
assistant: "早。有什么需要帮忙的？"

你: "查一下系统状态"
assistant: "好，我来查。正在提交给 GM..."
[继续聊天，不等待]
[GM 完成后自动通知]
```

### 在新节点（MacBook）

```
你: "测试移动节点连接"
assistant (mobile): "移动节点 (mobile) 已连接到 ClawOS Federation"
```

---

## 🎯 核心概念

### Assistant 黄金规则

1. **随时沟通** - 不"忙碌不理用户"
2. **不等待** - 子任务提交后继续聊天
3. **不沉默** - 保持沟通，不等结果

### Opus 铁律

适用于 GM 和 validator (Opus 角色)：

| 限制 | 值 |
|------|-----|
| 输入 | <5k tokens |
| 输出 | <2k (GM), <1k (validator) |
| 只读 | summary.md + decisions.md |

### 工作流程

```
用户 → assistant → GM → PM → Workers → PM → GM → assistant → 用户
```

---

## 📁 关键目录

```
~/openclaw-system/clawos/
├── config/          # 配置
├── souls/           # Agent 定义
├── scripts/         # 脚本
└── blackboard/      # 共享数据

~/clawos/workspaces/
├── MEMORY.md        # 长期记忆
├── IDENTITY.md      # 节点身份
└── USER.md          # 用户信息
```

---

## 🛠️ 常用操作

### 查看状态

```bash
# OpenClaw 状态
openclaw status

# Federation 节点
openclaw federation status

# Agent 列表
openclaw agent list

# 健康检查
~/openclaw-system/clawos/scripts/health-check.sh
```

### 重启服务

```bash
# 重启 OpenClaw
openclaw gateway restart

# 查看日志
openclaw logs --tail 100
```

### 查看成本

```bash
# Token 统计
openclaw stats tokens

# 成本监控
cat ~/clawos/blackboard/reports/cost-monitoring.md
```

---

## 🆘 常见问题

### Q1: Assistant 说"我在忙"

**问题**: 违反黄金规则

**解决**:
1. 检查 `souls/command/assistant.soul.md`
2. 确认有"黄金规则"
3. 重启 OpenClaw

### Q2: GM 超时

**问题**: Token 消耗过大

**解决**:
1. 检查 summary.md 是否存在
2. 启用 Prompt Cache
3. 精简 SOUL 文件

### Q3: 节点连接失败

**问题**: 无法连接主脑

**解决**:
1. 检查网络: `ping {主脑IP}`
2. 检查 token: `openclaw federation token show`
3. 检查端口: `nc -zv {主脑IP} 3000`

### Q4: 记忆不同步

**问题**: Blackboard 数据不一致

**解决**:
1. 手动同步: `openclaw blackboard sync`
2. 检查权限: `ls -la ~/clawos/`
3. 重新拉取: `openclaw blackboard pull`

---

## 📚 进阶主题

### 添加新节点

1. 选择节点定位（mobile, coding, writing 等）
2. 安装 OpenClaw
3. 配置 federation.json
4. 测试连接

详见: `blackboard/tasks/mobile-node-setup/`

### 添加新 Agent

1. 创建 SOUL 文件
2. 配置模型（model-mapping.json）
3. 注册到 meta.json
4. 重启 OpenClaw

### 自定义工作流

1. 编辑 `workflows/*.yml`
2. 定义步骤和条件
3. 测试工作流

---

## 📖 参考资料

### 文档

- 快速参考: `blackboard/shared/quick-reference.md`
- Blackboard 索引: `blackboard/INDEX.md`
- 时间线: `blackboard/shared/timeline-2026-02-26.md`

### 脚本

- 健康检查: `scripts/health-check.sh`
- 每日收割: `scripts/daily-harvest.sh`
- 自动监控: `scripts/monitor.sh`

### 外部资源

- OpenClaw 文档: https://docs.openclaw.ai
- ClawOS GitHub: https://github.com/openclaw/openclaw
- ClawHub (技能市场): https://clawhub.com

---

## 🎯 下一步

- [ ] 完成第一次对话
- [ ] 测试跨节点协作
- [ ] 查看成本报告
- [ ] 尝试添加新节点

---

**版本**: 1.0
**最后更新**: 2026-02-26
