# ClawOS 快速参考卡片

## 🦞 核心概念

### 架构层级

```
Command (Opus) → PM (GLM-5) → Workers (GLM-5/Codex)
```

| 层级 | 角色 | 模型 | 职责 |
|------|------|------|------|
| Command | GM, validator | Opus | 决策、质检 |
| PM | coding/writing/research-pm | GLM-5 | 协调、整理 |
| Workers | analyst/creator/critic/executor | 混合 | 执行任务 |

---

## 🚨 Opus 铁律

**适用于 GM 和 validator**

| 限制 | 值 |
|------|-----|
| 单次输入 | <5k tokens |
| 输出 | <2k (GM), <1k (validator) |
| 禁止 | 读原始文件 |
| 只能读 | summary.md + decisions.md |

---

## 🔄 工作流

### Assistant 黄金规则

1. **随时沟通** - 不"忙碌不理用户"
2. **不等待** - 子任务提交后继续聊天
3. **不沉默** - 上传下达后保持沟通

### GM 工作流

```
任务 → GM → PM → Workers → PM → GM → assistant
      (决策) (协调) (执行) (汇报) (验收) (通知)
```

---

## 📁 关键目录

```
~/openclaw-system/clawos/
├── config/          # 配置文件
│   ├── meta.json           # Federation 配置
│   └── model-mapping.json  # 模型分配
├── souls/           # Agent SOUL 文件
│   ├── command/           # Command 层
│   └── pm/                # PM 层
├── scripts/         # 脚本
│   ├── daily-harvest.sh   # 每日收割
│   └── monitor.sh         # 自动监控
└── blackboard/      # 共享黑板
    ├── tasks/             # 任务数据
    ├── gm/                # GM 决策
    └── shared/            # 跨节点共享

~/clawos/workspaces/
├── MEMORY.md        # 长期记忆
├── IDENTITY.md      # 节点身份
└── USER.md          # 用户信息
```

---

## 🛠️ 常用命令

### OpenClaw 管理

```bash
# 查看状态
openclaw status

# 重启
openclaw gateway restart

# 查看日志
openclaw logs --tail 100
```

### Federation 管理

```bash
# 查看节点状态
openclaw federation status

# 生成 token
openclaw federation token generate --node mobile

# 测试连接
openclaw federation ping
```

### Agent 管理

```bash
# 启动 agent
openclaw agent start assistant

# 查看运行状态
openclaw agent list

# 查看 agent 详情
openclaw agent show gm
```

---

## 📊 监控指标

### 成本监控

| 角色 | 目标 | 实际 | 状态 |
|------|------|------|------|
| GM tokens | <5k | - | 🟡 |
| validator tokens | <5k | - | 🟡 |
| 每日成本 | <$1 | - | 🟢 |

### 运行脚本

```bash
# 监控系统
~/openclaw-system/clawos/scripts/monitor.sh

# 每日收割
~/openclaw-system/clawos/scripts/daily-harvest.sh
```

---

## 🚀 快速启动

### 新节点配置

1. 安装 OpenClaw: `brew install openclaw`
2. 初始化: `openclaw init --node {node-id}`
3. 配置 Federation: 编辑 `~/clawos/config/federation.json`
4. 测试连接: `openclaw federation ping`

### 新任务流程

1. 用户 → assistant: "做 xxx"
2. assistant → Blackboard: 写入任务
3. assistant → GM: 通知
4. GM → PM: 指派
5. PM → Workers: 执行
6. Workers → PM: 汇报
7. PM → GM: 验收请求
8. GM → validator: 验收
9. validator → GM: 结果
10. GM → assistant: 通知用户

---

## 🆘 故障排查

### GM 超时

- 检查 tokens: `openclaw stats tokens`
- 检查 summary.md 是否存在
- 检查 research-pm 是否在 allowAgents

### 节点连接失败

- 检查网络: `ping {主脑IP}`
- 检查端口: `nc -zv {主脑IP} 3000`
- 检查 token: `openclaw federation token show`

### 记忆不同步

- 检查 Blackboard: `ls ~/clawos/blackboard/`
- 手动同步: `openclaw blackboard sync`
- 检查权限: `ls -la ~/clawos/`

---

**版本**: ClawOS 2026.2.26
**最后更新**: 2026-02-26 09:55
