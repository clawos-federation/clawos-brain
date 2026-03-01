# MESSAGE-PROTOCOL.md - ClawOS Agent 通信协议

**版本**: 1.0.0
**更新时间**: 2026-02-25
**状态**: ✅ 已定义

---

## 消息格式标准

### 基础结构

```json
{
  "version": "1.0",
  "id": "msg-uuid-v4",
  "traceId": "trace-uuid-v4",
  "from": {
    "agent": "agent-id",
    "tier": "command|pm|worker",
    "session": "session-key"
  },
  "to": {
    "agent": "agent-id|broadcast",
    "tier": "command|pm|worker"
  },
  "type": "request|response|notification|error",
  "priority": "low|normal|high|critical",
  "timestamp": "2026-02-25T18:50:00+08:00",
  "ttl": 3600,
  "payload": {},
  "metadata": {}
}
```

---

## 消息类型

### 1. Request (请求)

```json
{
  "type": "request",
  "payload": {
    "action": "task.assign|status.query|resource.request",
    "params": {},
    "deadline": "2026-02-25T20:00:00+08:00",
    "callback": "optional-callback-topic"
  }
}
```

**使用场景**:
- gm → PM: 分配任务
- PM → Worker: 执行指令
- assistant → gm: 提交用户请求

### 2. Response (响应)

```json
{
  "type": "response",
  "payload": {
    "requestId": "original-msg-id",
    "status": "success|failure|partial",
    "result": {},
    "error": null
  }
}
```

**使用场景**:
- PM → gm: 任务完成
- Worker → PM: 执行结果
- gm → assistant: 状态更新

### 3. Notification (通知)

```json
{
  "type": "notification",
  "payload": {
    "event": "progress|warning|completed|failed",
    "message": "人类可读的描述",
    "progress": {
      "current": 3,
      "total": 10,
      "percent": 30
    }
  }
}
```

**使用场景**:
- Worker → PM: 进度更新
- PM → gm: 状态汇报
- gm → assistant: 推送给用户

### 4. Error (错误)

```json
{
  "type": "error",
  "payload": {
    "requestId": "original-msg-id",
    "code": "E001|E002|E003...",
    "message": "错误描述",
    "recoverable": true,
    "suggestion": "建议的处理方式"
  }
}
```

**错误代码**:
| 代码 | 含义 | 可恢复 |
|------|------|--------|
| E001 | 权限不足 | 否 |
| E002 | 资源不可用 | 是 |
| E003 | 参数错误 | 是 |
| E004 | 超时 | 是 |
| E005 | 依赖失败 | 是 |
| E006 | 系统错误 | 视情况 |

---

## 通信渠道

### 1. Blackboard (黑板)

**用途**: 持久化、异步通信

**目录结构**:
```
~/clawos/blackboard/
├── inbox/           # 任务队列
├── tasks/           # 任务数据
├── gm/              # GM 专属
├── {agent-id}/      # Agent 专属
└── shared/          # 共享数据
```

**写入规则**:
```bash
# 发送消息
blackboard write {to-agent}/inbox/{msg-id}.json

# 读取消息
blackboard read {my-agent}/inbox/
```

### 2. Sessions (会话)

**用途**: 实时、同步通信

**使用方法**:
```
sessions_send(
  sessionKey: "target-session-key",
  message: "消息内容"
)
```

### 3. Heartbeat (心跳)

**用途**: 定期状态同步

**触发条件**:
- 每 15 分钟
- 任务状态变化
- 错误发生

---

## 通信规则

### 层级规则

```
Command ←→ Command  ✅ 允许
Command ←→ PM       ✅ 允许（上下级）
PM ←→ PM            ❌ 禁止（通过 Command）
PM ←→ Worker        ✅ 允许（上下级）
Worker ←→ Worker    ❌ 禁止（通过 PM）
```

### 优先级处理

| 优先级 | 响应时间 | 示例场景 |
|--------|----------|----------|
| critical | 立即 | 系统故障、安全事件 |
| high | 5 分钟内 | 用户紧急请求 |
| normal | 30 分钟内 | 常规任务 |
| low | 24 小时内 | 后台任务 |

### 消息追踪

所有消息必须包含 `traceId`，用于：
- 日志关联
- 问题排查
- 性能分析

---

## 实现指南

### 发送消息

```python
def send_message(to_agent, msg_type, payload, priority="normal"):
    msg = {
        "version": "1.0",
        "id": generate_uuid(),
        "traceId": get_trace_id(),
        "from": {
            "agent": MY_AGENT_ID,
            "tier": MY_TIER,
            "session": CURRENT_SESSION
        },
        "to": {
            "agent": to_agent,
            "tier": get_agent_tier(to_agent)
        },
        "type": msg_type,
        "priority": priority,
        "timestamp": iso_now(),
        "payload": payload
    }

    # 写入目标 agent 的 inbox
    write_to_blackboard(f"{to_agent}/inbox/{msg['id']}.json", msg)

    # 记录日志
    log_message(msg)

    return msg['id']
```

### 接收消息

```python
def check_inbox():
    messages = read_from_blackboard(f"{MY_AGENT_ID}/inbox/")

    for msg in messages:
        # 验证消息格式
        if not validate_message(msg):
            log_error(f"Invalid message: {msg}")
            continue

        # 检查是否过期
        if is_expired(msg):
            log_warning(f"Expired message: {msg['id']}")
            continue

        # 处理消息
        handle_message(msg)

        # 确认处理完成（移动到 processed）
        move_to_processed(msg)
```

---

## 监控与日志

### 消息日志格式

```json
{
  "timestamp": "2026-02-25T18:50:00+08:00",
  "level": "info|warn|error",
  "msgId": "msg-uuid",
  "traceId": "trace-uuid",
  "from": "agent-id",
  "to": "agent-id",
  "type": "request|response|...",
  "latencyMs": 150,
  "status": "sent|delivered|processed|failed"
}
```

### 监控指标

| 指标 | 说明 | 阈值 |
|------|------|------|
| 消息延迟 | 从发送到处理的时间 | < 5s |
| 队列深度 | inbox 中待处理消息数 | < 100 |
| 错误率 | 失败消息占比 | < 1% |

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-02-25 | 初始版本，定义标准消息格式 |

---

**ClawOS 2026.3 - Message Protocol**
