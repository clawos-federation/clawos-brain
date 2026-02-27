# GM 优化方案 - 层级调度 + 摘要机制

**时间**: 2026-02-26 08:24
**来源**: assistant + dongsheng
**类型**: 系统优化
**优先级**: high

---

## 问题

| 问题 | 现状 |
|------|------|
| GM 读取量过大 | 150k tokens |
| GM 超时 | 60s/120s 都不够 |
| 模型浪费 | Opus 用来读文件 |

---

## 优化方案

### 1. 严格层级调度

```
GM (Opus) → 只做决策
    ↓
PM Layer → 调度 Workers
    ↓
Workers → 执行具体任务（读文件等）
```

**规则**：
- GM 禁止直接读文件
- GM 只看 PM 返回的摘要
- GM 只指挥 PM，不直接指挥 Workers

### 2. 摘要机制（方案 D）

**写入流**：
```
Worker 完成任务
    ↓
写 summary.md 到 blackboard/tasks/{id}/
    ↓
PM 审核 + 汇报 GM
```

**查询流**：
```
GM 需要信息
    ↓
指派 research-pm
    ↓
research-pm 先读 summary.md
    ↓
不够？派 research worker 读原文件
    ↓
返回摘要给 GM（<5k tokens）
```

### 3. 职责分工

| 角色 | 职责 | 模型建议 |
|------|------|----------|
| GM | 决策 + 调度 PM | Opus |
| research-pm | 信息收集协调 | 中等模型 |
| research worker | 读文件 + 整理 | 便宜模型 |
| coding-pm | 开发任务协调 | 中等模型 |
| code worker | 编码实现 | 便宜模型 |

---

## 实施步骤

### Phase 1: 配置修改
- [x] 更新 GM SOUL，明确"只调度 PM"
- [x] 更新 research-pm SOUL，增加"信息收集"职责
- [x] 检查 research worker 配置

### Phase 2: 摘要机制
- [x] 创建 summary.md 模板
- [x] 为现有任务创建 summary.md
- [ ] 修改 Worker 任务完成流程（自动生成 summary）

### Phase 3: 测试验证
- [x] 提交测试任务给 GM
- [ ] 验证 GM token 消耗降低
- [ ] 验证响应时间 <60s

---

## 预期效果

| 指标 | 优化前 | 优化后 |
|------|--------|--------|
| GM token 消耗 | 150k | <5k |
| GM 响应时间 | 超时 | <30s |
| 模型成本 | 高 | 低 |

---

**Status**: ✅ Implemented (2026-02-26 22:05)

## Implementation Log

- Added `research-pm` agent with `researcher-web` and `researcher-file` workers
- Added `researcher-file` worker for file reading tasks
- GM subagents now include `research-pm`
- Created summary.md template at `~/clawos/blackboard/tasks/TEMPLATE/summary.md`
- Note: `constraints` key not supported by OpenClaw, using agent structure only
- Constraints enforced via SOUL.md instructions instead of config
