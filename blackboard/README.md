# ClawOS Blackboard - 共享黑板

> Agent 间共享数据的核心机制。所有 Agent 通过统一的路径读写数据。

---

## 目录结构 (Phase 1 Complete)

```
~/clawos/blackboard/
├── tasks/                        # 任务目录
│   ├── {taskId}/                 # 单个任务
│   │   ├── task.json             # 任务基本信息
│   │   ├── status.md             # 实时状态
│   │   ├── plan.md               # 执行计划
│   │   ├── validation.md         # 验证结果
│   │   ├── checkpoints.json      # Lobster checkpoint
│   │   ├── escalation.md         # 上报记录（如有）
│   │   ├── chapters/             # 写作任务产出
│   │   └── output/               # 最终产出
│   ├── pending.md                # 待处理任务列表
│   ├── assigned.md               # 已分配任务
│   └── README.md                 # 任务目录说明
│
├── gm/                           # GM 决策中心
│   ├── status.md                 # GM 当前状态
│   ├── decisions.md              # 所有决策记录
│   └── escalations.md            # 上报处理记录
│
├── assistant/                    # Assistant 用户数据
│   ├── templates/                # 用户模板
│   │   ├── README.md             # 模板说明
│   │   ├── heartbeat-state.json  # 心跳状态模板
│   │   ├── notifications.json    # 通知模板
│   │   ├── preferences.json      # 偏好设置模板
│   │   └── user-template/        # 完整用户模板
│   └── {userId}/                 # 每用户独立目录
│       ├── tasks.json            # 用户任务列表
│       ├── notifications.json    # 通知队列
│       ├── preferences.json      # 用户偏好
│       └── heartbeat-state.json  # 心跳状态
│
├── platform-pm/                  # Platform PM 目录
│   ├── status.md                 # 当前状态
│   ├── decisions.md              # 决策记录
│   ├── active-workflows.md       # 活跃工作流
│   ├── team-assignments.json     # 团队分配
│   └── health-report-*.md        # 健康报告
│
├── coding-pm/                    # Coding PM 目录
│   ├── status.md                 # 当前状态
│   ├── decisions.md              # 决策记录
│   └── team-assignments.json     # 团队分配
│
├── writing-pm/                   # Writing PM 目录
│   ├── status.md                 # 当前状态
│   ├── decisions.md              # 决策记录
│   └── team-assignments.json     # 团队分配
│
├── shared/                       # 共享上下文
│   └── context.md                # 全局共享信息
│
├── persistence/                  # 持久化层
│   ├── README.md                 # 持久化说明
│   ├── archive/                  # 任务归档
│   │   ├── completed/            # 已完成任务
│   │   └── failed/               # 失败任务
│   ├── snapshots/                # 状态快照
│   │   ├── daily/                # 每日快照
│   │   └── hourly/               # 每小时快照
│   ├── history/                  # 历史日志
│   │   ├── tasks.jsonl           # 任务历史
│   │   └── decisions.jsonl       # 决策历史
│   └── metrics/                  # 统计指标
│       └── daily-report.json     # 日报数据
│
└── TEMPLATE/                     # 任务模板
    ├── task.json                 # 任务模板
    ├── status.md                 # 状态模板
    ├── validation.md             # 验证模板
    ├── escalation.md             # 上报模板
    └── checkpoints.json          # 检查点模板
```

---

## 使用方式

### 读取数据

```bash
blackboard read tasks/{taskId}/status.md
blackboard read gm/decisions.md
blackboard read coding-pm/status.md
```

### 写入数据

```bash
blackboard write tasks/{taskId}/status.md --mode overwrite --content "..."
blackboard write gm/decisions.md --mode append --content "..."
blackboard write persistence/history/tasks.jsonl --mode append --content "..."
```

---

## Agent 访问权限

| Agent | 读取 | 写入 |
|-------|------|------|
| assistant | 所有 | assistant/{userId}/ |
| gm | 所有 | gm/, tasks/, persistence/ |
| validator | 所有 | tasks/*/validation.md |
| coding-pm | 所有 | coding-pm/, tasks/ |
| writing-pm | 所有 | writing-pm/, tasks/ |
| platform-pm | 所有 | platform-pm/, tasks/, persistence/ |
| Workers | tasks/ | tasks/{assigned}/ |

---

## 命名约定

| 路径模式 | 用途 | 读写频率 |
|----------|------|----------|
| `tasks/{taskId}/status.md` | 任务状态 | 高频读写 |
| `tasks/{taskId}/validation.md` | 验证结果 | 中频写入 |
| `tasks/{taskId}/escalation.md` | 上报记录 | 低频写入 |
| `gm/decisions.md` | GM 决策日志 | 中频追加 |
| `coding-pm/status.md` | 开发PM状态 | 中频读写 |
| `writing-pm/status.md` | 写作PM状态 | 中频读写 |
| `shared/context.md` | 共享上下文 | 中频读写 |
| `persistence/history/*.jsonl` | 历史日志 | 低频追加 |

---

## 安全机制

1. **文件锁**: WRITE 操作使用 flock 防止并发冲突
2. **自动备份**: 每次写入前备份上一版本到 .bak
3. **权限控制**: 所有 Agent 可读取，只有授权 Agent 可写入
4. **审计日志**: 所有写入操作记录到 persistence/history/

---

## 版本

- **Version**: 2026.3.1 (Phase 1 Complete)
- **Updated**: 2026-02-24
- **Components**:
  - GM 决策中心
  - PM 专属目录 (coding-pm, writing-pm, platform-pm)
  - Per-user Assistant 模板
  - Persistence 持久化层
  - HEARTBEAT 状态追踪
