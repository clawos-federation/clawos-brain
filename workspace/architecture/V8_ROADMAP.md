# ClawOS v8 优化方案

> 版本: 2026.3.8
> 基于研究成果 + 架构分析 + 定位讨论

---

## 一、v8 核心变更

### 1.1 司令部架构重构

```
┌─────────────────────────────────────────────────────────────┐
│                      司令部 (Server)                         │
│                      mac-mini:18789                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Federation GM ═══ 总司令 (全局指挥·任务分发·向Boss汇报)     │
│                                                             │
│  Platform PM ════ 总参+总后+总装 (进化·DNA·资源·调度)        │
│                                                             │
│  Research PM ════ 情报局 (收集·分析·研判·简报) [NEW v8]      │
│  ├── researcher-web     网络情报收集                        │
│  ├── researcher-file    内部档案分析                        │
│  └── analyst-data       数据情报分析                        │
│                                                             │
│  assistant ══════ 通信处 (Boss专线·Telegram/WhatsApp)        │
│                                                             │
│  validator ══════ 督察处 (独立质量检查)                      │
│                                                             │
│  Local GM ═══════ 司令部直属队 (本地通用任务执行)            │
│                                                             │
└─────────────────────────────────────────────────────────────┘

方面军 (其他节点):
├── Alpha 节点 ═══ 量化作战部队 (专业·隔离·自主战术)
├── MacBook Air ══ 工程实验部队 (研发·测试·移动)
└── Cloud Node ═══ 后备部队 (24/7支援) [planned]
```

### 1.2 任务入口规则

| 任务类型 | 入口 | 示例 |
|---------|------|------|
| **战略级** | Federation GM | "Alpha 本季度目标：涨停股准确率 > 75%" |
| **跨节点** | Federation GM | "协调 Alpha + Air 研发交易插件" |
| **进化方向** | Federation GM | "本周重点研究 RAG 优化" |
| **单节点具体** | Local GM | "Alpha 回测这个策略" |
| **日常碎片** | assistant | "今天 Alpha 信号怎么样" |

### 1.3 Server 三不碰

```
❌ 不执行量化交易 (包括纸面交易)
❌ 不覆盖 risk-controller
❌ 不替代 Alpha 做策略决策
```

---

## 二、技术优化 (基于研究)

### 2.1 Event Sourcing (ESAA 论文)

**问题**: 当前无审计追踪，故障无法恢复

**方案**: 所有状态变更记录为不可变事件

```json
// blackboard/events/{event_id}.json
{
  "event_id": "evt_20260227_123456",
  "event_type": "task_assigned",
  "timestamp": "2026-02-27T12:34:56Z",
  "aggregate_id": "task_001",
  "payload": {...},
  "metadata": {
    "correlation_id": "corr_abc123",
    "causation_id": "evt_previous"
  }
}
```

**收益**: 审计追踪 + 故障恢复 + 事件重放

### 2.2 Versioned Capability Vectors (FoA 论文)

**问题**: 任务路由靠节点名，无语义匹配

**方案**: 节点声明能力向量

```json
// node-status/{node}.json
{
  "node_id": "alpha",
  "capability_vector": {
    "version": "2026.2.27",
    "dimensions": {
      "quantitative": 0.95,
      "code_generation": 0.30,
      "research": 0.50
    },
    "tools": ["python", "backtest", "trading"],
    "constraints": {
      "isolated": true,
      "max_concurrent_tasks": 2
    }
  }
}
```

**收益**: 智能语义路由 + 动态能力发现

### 2.3 agent:// URI Scheme

**问题**: 节点身份绑定网络位置，迁移困难

**方案**: 拓扑无关的身份标识

```
agent://clawos.federation/mac-mini/coding-pm
agent://clawos.federation/alpha?capability=quantitative
agent://clawos.federation/any?skill=python
```

**收益**: 节点迁移透明 + 能力查询

### 2.4 Durable Execution (LangGraph 模式)

**问题**: 长任务失败无法恢复

**方案**: Checkpoint/Resume 机制

```json
// checkpoints/{workflow_id}/{checkpoint_id}.json
{
  "workflow_id": "wf_001",
  "checkpoint_id": "cp_003",
  "state": {
    "current_step": "code_review",
    "completed_steps": ["planning", "coding"],
    "variables": {...}
  }
}
```

**收益**: 长任务容错 + 中断恢复

### 2.5 健康监控 (P0 优先)

**问题**: 无心跳机制，节点状态不可靠

**方案**: heartbeat + 超时检测

```json
// blackboard/federation/heartbeat/{node_id}.json
{
  "node_id": "alpha",
  "timestamp": "2026-02-27T12:34:56Z",
  "status": "healthy",
  "load": 0.3,
  "active_tasks": 1
}
```

**规则**: 
- 每 30 秒更新一次
- 超过 2 分钟无更新 → 标记 offline
- Federation GM 自动重路由任务

### 2.6 冲突解决

**问题**: 多节点可能同时抓取 "any" 任务

**方案**: 任务领取锁 + 乐观并发

```json
// task request 增加 lock 字段
{
  "id": "task_001",
  "status": "pending",
  "lock": {
    "locked_by": null,
    "locked_at": null,
    "version": 1
  }
}

// 领取时 CAS 更新
if task.lock.version == expected_version:
  task.lock = {"locked_by": "alpha", "version": version+1}
  return success
else:
  return conflict
```

---

## 三、新增组件

### 3.1 Research PM (情报局)

**职责**:
- 情报收集 (网络搜索、论文追踪、市场信息)
- 情报分析 (数据挖掘、趋势识别)
- 研究判断 (方向评估、噪音过滤)
- 简报产出 (每日/周情报摘要)

**产出路径**:
```
blackboard/intel/
├── daily/
│   ├── 2026-02-27_tech.md
│   ├── 2026-02-27_market.md
│   └── digest.md          ← Alpha 知识弹药
└── weekly/
    └── trend-analysis.md  ← 影响进化方向
```

**配合流程**:
```
Research PM 收集情报 → 发现新方向
        ↓
Platform PM 评估 → 纳入进化队列
        ↓
Alpha 接收目标 → 执行进化
```

### 3.2 Worker SOULs 填充

**问题**: `souls/workers/` 目录空，无角色模板

**方案**: 创建 12 个 Worker SOUL

```
souls/workers/
├── analyst-code/
│   └── analyst-code.soul.md    ← 代码分析员
├── creator-code/
│   └── creator-code.soul.md    ← 代码生成员
├── critic-code/
│   └── critic-code.soul.md     ← 代码审查员
├── executor-test/
│   └── executor-test.soul.md   ← 测试执行员
├── researcher-web/
│   └── researcher-web.soul.md  ← 网络情报员
├── researcher-file/
│   └── researcher-file.soul.md ← 文档分析员
├── writer-general/
│   └── writer-general.soul.md  ← 文档撰写员
├── reviewer-content/
│   └── reviewer-content.soul.md ← 内容审查员
└── ... (共12个)
```

---

## 四、架构差距修复

| 差距 | 优先级 | 解决方案 | 状态 |
|------|--------|---------|------|
| Worker SOULs 空白 | P0 | 创建角色模板 | 待做 |
| 无健康监控 | P0 | heartbeat + 超时检测 | 待做 |
| 单点故障 (GM) | P1 | 主备切换机制 | 待做 |
| 无冲突解决 | P1 | 任务锁 + CAS | 待做 |
| 无熔断器 | P1 | 失败计数 + 降级 | 待做 |
| 轮询延迟 | P2 | WebSocket 通知 | 待做 |
| 无 Event Sourcing | P2 | 事件日志 | 待做 |
| L3/L4 记忆 | P3 | Vector Store | 待做 |

---

## 五、目录结构更新

```
clawos-blackboard/
├── federation/
│   ├── node-status/          ← 节点状态 (增加 VCV)
│   ├── requests/             ← 任务请求 (增加 lock)
│   ├── results/              ← 任务结果
│   ├── evolution-queue/      ← 进化队列
│   ├── events/               ← [NEW] 事件日志
│   └── heartbeat/            ← [NEW] 心跳监控
├── shared/
│   ├── alpha-oversight.json
│   └── risk-limits.json
├── intel/                    ← [NEW] 情报产出
│   ├── daily/
│   └── weekly/
├── alpha/                    ← Alpha 报告
│   └── daily-report/
└── checkpoints/              ← [NEW] 执行检查点

clawos-brain/
├── souls/
│   ├── gm/
│   │   └── federation-gm.soul.md  ← 更新司令部职责
│   ├── pm/
│   │   ├── platform-pm.soul.md
│   │   └── research-pm.soul.md    ← [NEW]
│   └── workers/                   ← [NEW] 填充
│       ├── analyst-code/
│       ├── creator-code/
│       └── ...
├── schemas/
│   ├── task-request.schema.json   ← 增加 lock 字段
│   ├── task-result.schema.json
│   ├── node-status.schema.json    ← 增加 VCV 字段
│   ├── event.schema.json          ← [NEW]
│   └── heartbeat.schema.json      ← [NEW]
└── scripts/
    ├── dispatch-task.sh           ← 支持 VCV 路由
    ├── check-federation.sh
    ├── health-monitor.sh          ← [NEW]
    └── collect-intel.sh           ← [NEW]
```

---

## 六、实施路线图

### Phase 1: P0 修复 (本周)

| 任务 | 预估 | 产出 |
|------|------|------|
| 创建 12 个 Worker SOULs | 2h | souls/workers/*.md |
| heartbeat 机制 | 2h | scripts/health-monitor.sh |
| 更新 Federation GM SOUL | 1h | 司令部职责描述 |
| 创建 Research PM SOUL | 1h | souls/pm/research-pm.soul.md |

### Phase 2: P1 修复 (下周)

| 任务 | 预估 | 产出 |
|------|------|------|
| 任务锁机制 | 2h | task request + lock |
| 熔断器 | 2h | 失败计数 + 降级 |
| Event Sourcing 基础 | 3h | events/ + schema |
| GM 主备切换 | 4h | 高可用方案 |

### Phase 3: P2 优化 (2周内)

| 任务 | 预估 | 产出 |
|------|------|------|
| VCV 语义路由 | 3h | node-status + dispatch |
| agent:// URI | 2h | 身份解析 |
| Durable Execution | 4h | checkpoints/ |
| WebSocket 通知 | 3h | 实时推送 |

### Phase 4: P3 完善 (1月内)

| 任务 | 预估 | 产出 |
|------|------|------|
| Vector Store 集成 | 4h | L3 记忆 |
| GitHub 记忆同步 | 2h | L4 记忆 |
| 知识图谱 | 6h | el-agente-grafico 模式 |

---

## 七、v7 → v8 升级清单

### 配置文件更新

- [ ] server/profile.json - 添加 Research PM
- [ ] alpha/profile.json - 确认 oversight 边界
- [ ] node-status/*.json - 添加 VCV 字段
- [ ] task-request.schema.json - 添加 lock 字段

### SOUL 文件更新

- [ ] federation-gm.soul.md - 司令部职责
- [ ] research-pm.soul.md - 情报局职责 (新建)
- [ ] workers/*.soul.md - 12 个角色模板 (新建)

### 脚本更新

- [ ] dispatch-task.sh - VCV 路由 + 锁机制
- [ ] check-federation.sh - 心跳检测
- [ ] health-monitor.sh - 新建
- [ ] collect-intel.sh - 新建

### 目录创建

- [ ] blackboard/federation/events/
- [ ] blackboard/federation/heartbeat/
- [ ] blackboard/intel/daily/
- [ ] blackboard/intel/weekly/
- [ ] blackboard/checkpoints/

---

## 八、验收标准

### v8 完成标准

| 标准 | 验证方法 |
|------|---------|
| 所有 Worker 有 SOUL | `ls souls/workers/*/` 不为空 |
| 心跳正常 | 节点 offline 后任务自动重路由 |
| 无任务冲突 | 并发测试无重复执行 |
| 审计可追溯 | events/ 有完整记录 |
| 长任务可恢复 | checkpoint → resume 成功 |
| 情报自动化 | daily intel 每日产出 |

---

*方案完成于 2026-02-27*
