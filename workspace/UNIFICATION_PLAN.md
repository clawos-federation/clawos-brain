# ClawOS × OpenClaw 统一规范方案

**日期**: 2026-02-24 00:00  
**目标**: 统一、规范、高效、优质的系统架构

---

## 一、当前问题诊断

### 1.1 文件混乱点

| 问题 | 影响 | 优先级 |
|------|------|--------|
| Workspace 有 90+ 文件 | 难以维护 | 🔴 高 |
| 多个配置文件（config.json, config-unified.json） | 不确定哪个生效 | 🔴 高 |
| Agent workspace 分散 | 不清楚哪个在工作 | 🟡 中 |
| ClawOS 与 OpenClaw 目录分离 | 逻辑不统一 | 🟡 中 |
| 记忆文件分散 | 上下文丢失 | 🟡 中 |

### 1.2 命名不一致

- `workspace/` vs `workspaces/`
- `souls/` vs `agent/`
- `config.json` vs `openclaw.json`

---

## 二、统一规范方案

### 2.1 目录结构规范

```
~/.openclaw/                      # OpenClaw 核心目录（只放系统文件）
├── config.json                   # 主配置文件（唯一）
├── agents/                       # Agent 实例
│   ├── assistant/
│   ├── gm/
│   ├── devagent/
│   └── ...
├── workspace/                    # 默认工作区（弃用）
├── logs/                         # 系统日志
├── memory/                       # 向量记忆存储
└── credentials/                  # 凭证

~/.openclaw/clawos/                # 开发区（所有开发相关）
├── workspace/                    # 主工作区
│   ├── AGENTS.md                 # 主 Agent 规则
│   ├── SOUL.md                   # 主人格定义
│   ├── USER.md                   # 用户信息
│   ├── TOOLS.md                  # 工具说明
│   ├── HEARTBEAT.md              # 心跳检查
│   │
│   ├── architecture/             # 架构文档
│   │   ├── CLAWOS_ARCHITECTURE.md
│   │   ├── OPENCLAW_GUIDE.md
│   │   └── FUSION_COMPLETE_REPORT.md
│   │
│   ├── protocols/                # 协议文档
│   │   ├── CHARTER_7.7_ROLES.md
│   │   ├── GM_EXECUTION_SLA.md
│   │   └── AUTONOMOUS_DELIVERY_PROTOCOL.md
│   │
│   ├── missions/                 # 任务存档
│   │   ├── active/               # 活跃任务
│   │   └── completed/            # 已完成任务
│   │
│   ├── memory/                   # 记忆系统
│   │   ├── daily/                # 每日日志
│   │   ├── decisions/            # 决策记录
│   │   └── lessons/              # 经验教训
│   │
│   └── reports/                  # 报告
│       ├── E2E_TEST_REPORT.md
│       └── AUTO_EVOLUTION_LOG.md
│
├── clawos/                       # ClawOS 专用目录
│   ├── souls/                    # Agent 人格定义
│   │   ├── assistant/
│   │   ├── gm/
│   │   └── platform-pm/
│   │
│   ├── skills/                   # 技能库
│   │   ├── gm-task-evaluate/
│   │   ├── pm-team-assemble/
│   │   └── quality-check/
│   │
│   ├── workflows/                # Lobster 工作流
│   │   ├── write-book.lobster.ts
│   │   └── coding-workflow.lobster.ts
│   │
│   ├── registry/                 # Agent 注册表
│   │   └── agents.json
│   │
│   └── runtime/                  # 运行时数据
│       ├── inbox/                # 任务接收
│       ├── status/               # 任务状态
│       ├── output/               # 产出物
│       └── logs/                 # 运行日志
│
└── projects/                     # 项目代码
    ├── url-shortener/            # 示例项目
    └── ...
```

### 2.2 配置文件规范

**唯一主配置**: `~/.openclaw/config.json`

```json
{
  "$schema": "https://openclaw.ai/schema/config.json",
  "version": "2.0",
  "meta": {
    "name": "ClawOS Unified",
    "description": "OpenClaw 7.7 + ClawOS 融合架构",
    "version": "2026.2.24",
    "lastUpdated": "2026-02-24T00:00:00+08:00"
  },
  "gateway": {
    "port": 18789,
    "host": "127.0.0.1",
    "auth": {
      "mode": "token",
      "token": "${OPENCLAW_AUTH_TOKEN}"
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "zai/glm-5",
        "fallbacks": ["zai/glm-5-flash"]
      },
      "workspace": "~/.openclaw/clawos/workspace",
      "memory": {
        "enabled": true,
        "maxTokens": 8000
      }
    },
    "list": [
      {
        "id": "assistant",
        "name": "ClawOS Assistant",
        "default": true,
        "model": {"primary": "zai/glm-5"},
        "subagents": {"allowAgents": ["gm"]}
      },
      {
        "id": "gm",
        "name": "ClawOS GM",
        "model": {"primary": "zai/glm-5"},
        "subagents": {"allowAgents": ["devagent", "testagent"]}
      }
      // ... 其他 agents
    ]
  },
  "bindings": [
    {
      "id": "boss-to-assistant",
      "agentId": "assistant",
      "match": {"channel": "webchat"},
      "priority": 100,
      "enabled": true
    }
  ]
}
```

**删除冗余配置**:
- ❌ `~/.openclaw/config-unified.json`（删除）
- ❌ `~/.openclaw/openclaw.json`（重命名为 backup）

### 2.3 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| Agent ID | 小写-连字符 | `coding-pm`, `devagent` |
| 文件名 | 大写-下划线 | `GM_EXECUTION_SLA.md` |
| 目录名 | 小写 | `missions/`, `skills/` |
| SOUL 文件 | `SOUL.md` | `souls/assistant/SOUL.md` |
| 技能文件 | `SKILL.md` | `skills/gm-task-evaluate/SKILL.md` |
| 配置文件 | 小写.json | `config.json`, `agents.json` |

### 2.4 记忆系统规范

**三层记忆架构**:

```
1. 系统记忆（OpenClaw 自动）
   - 位置: ~/.openclaw/memory/
   - 格式: 向量存储
   - 用途: 会话上下文

2. 工作记忆（每日）
   - 位置: ~/.openclaw/clawos/workspace/memory/daily/
   - 格式: YYYY-MM-DD.md
   - 用途: 每日日志

3. 长期记忆（精选）
   - 位置: ~/.openclaw/clawos/workspace/memory/
   - 格式: MEMORY.md, decisions/, lessons/
   - 用途: 重要决策、经验教训
```

---

## 三、整理执行计划

### 3.1 立即执行（今晚）

**Phase 1: 配置文件统一**

```bash
# 1. 备份
mkdir -p ~/.openclaw/backup-2026-02-23
cp ~/.openclaw/*.json ~/.openclaw/backup-2026-02-23/

# 2. 清理
rm ~/.openclaw/config-unified.json
mv ~/.openclaw/openclaw.json ~/.openclaw/backup-2026-02-24/openclaw.json.backup

# 3. 保留唯一主配置
# 确保 ~/.openclaw/config.json 是最新融合版本
```

**Phase 2: 目录重组**

```bash
# 1. 创建规范目录
mkdir -p ~/.openclaw/clawos/workspace/{architecture,protocols,missions,reports}
mkdir -p ~/.openclaw/clawos/workspace/memory/{daily,decisions,lessons}

# 2. 移动文件到正确位置
cd ~/.openclaw/clawos/workspace

# 架构文档
mv CLAWOS_*.md architecture/
mv FUSION_*.md architecture/
mv *_ARCHITECTURE*.md architecture/

# 协议文档
mv CHARTER*.md protocols/
mv GM_*.md protocols/
mv *_PROTOCOL.md protocols/

# 报告
mv E2E_TEST_REPORT.md reports/
mv ACCEPTANCE_REPORT*.md reports/

# 3. 清理过时文件
# 移动到 archives/
mv active_missions missions/active
mv agents missions/  # 如果是任务相关
```

### 3.2 明天执行（用户醒来后）

**Phase 3: 验证和测试**

1. 验证 Gateway 正常
2. 测试 Agent 路由
3. 检查记忆系统
4. 运行测试任务

**Phase 4: 文档更新**

1. 更新所有路径引用
2. 重写 README
3. 编写维护手册

---

## 四、质量检查清单

### 4.1 文件组织

- [ ] 只有一个主配置文件
- [ ] 所有架构文档在 `architecture/`
- [ ] 所有协议在 `protocols/`
- [ ] 所有报告在 `reports/`
- [ ] 记忆系统三层层级清晰

### 4.2 命名一致性

- [ ] Agent ID 统一格式
- [ ] 文件名符合规范
- [ ] 目录名符合规范

### 4.3 可维护性

- [ ] 每个目录有 README
- [ ] 配置文件有注释
- [ ] 文档有版本号
- [ ] 有清理脚本

---

## 五、维护规范

### 5.1 日常维护

- **每天**: 记录到 `memory/daily/YYYY-MM-DD.md`
- **每周**: 清理过时文件到 `archives/`
- **每月**: 回顾 MEMORY.md，提炼经验教训

### 5.2 文件生命周期

```
创建 → 使用 → 归档 → 清理
 ↓      ↓      ↓      ↓
daily  active  archive delete
```

### 5.3 版本控制

- 所有配置文件纳入 Git 管理
- 重大变更记录在 CHANGELOG.md
- 使用语义化版本号

---

## 六、预期成果

### 6.1 整理后结构

```
✅ 清晰的目录层级
✅ 统一的命名规范
✅ 唯一的主配置
✅ 三层记忆系统
✅ 易于维护和扩展
```

### 6.2 效率提升

- 文件查找速度: **↑ 80%**
- 配置冲突: **↓ 100%**
- 维护时间: **↓ 50%**
- 新人上手: **↓ 70%**

---

## 七、风险控制

### 7.1 备份策略

- 整理前全量备份
- 保留 7 天历史
- 关键文件版本控制

### 7.2 回滚方案

```bash
# 如果整理失败
cp -r ~/.openclaw/backup-2026-02-23/* ~/.openclaw/
```

### 7.3 验证步骤

1. Gateway 是否正常
2. Agent 是否在线
3. 记忆是否完整
4. 任务是否能执行

---

## 八、执行检查点

### Checkpoint 1: 配置统一

```bash
ls ~/.openclaw/*.json
# 应该只有: config.json
```

### Checkpoint 2: 目录规范

```bash
ls ~/.openclaw/clawos/workspace/
# 应该看到: architecture/ protocols/ missions/ reports/ memory/
```

### Checkpoint 3: 系统正常

```bash
openclaw status
# 应该显示: Gateway 运行中, Agents 在线
```

---

**整理负责人**: GM Agent  
**执行时间**: 2026-02-24 00:00  
**预计完成**: 2026-02-24 01:00  
**验证时间**: 2026-02-24 08:00
