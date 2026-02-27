# ClawOS 最佳实践

---

## 🎯 核心原则

### 1. 好钢用在刀刃上

**Opus 使用场景**：
- ✅ 关键决策
- ✅ 质检验收
- ✅ 风险判断
- ❌ 日常任务
- ❌ 信息收集
- ❌ 代码执行

**模型选择**：
| 任务类型 | 推荐模型 | 原因 |
|----------|----------|------|
| 决策、质检 | Opus | 需要高智商 |
| 代码任务 | Codex | 代码专长 |
| 通用任务 | GLM-5 | 便宜、够用 |

---

### 2. 不要等待，继续工作

**Assistant 黄金规则**：
1. 随时和 Boss 沟通
2. 子任务不等待
3. 不沉默

**示例**：
```
❌ 错误:
你: "查系统状态"
assistant: "好，等 GM 查完告诉你"
[沉默 2 分钟]
assistant: "GM 查完了，状态是..."

✅ 正确:
你: "查系统状态"
assistant: "好，已提交给 GM。对了，你想看看今天的天气吗？"
你: "好啊"
[继续聊天]
[2 分钟后 GM 自动通知]
assistant: "系统状态：5个节点在线..."
```

---

### 3. 分工明确，层级清晰

**架构原则**：
```
Command (Opus) → 决策
    ↓
PM (GLM-5) → 协调
    ↓
Workers (混合) → 执行
```

**禁止越级**：
- ❌ GM 直接调用 Workers
- ❌ Workers 跳过 PM 汇报
- ❌ assistant 自己执行任务

---

## 📊 成本优化

### Prompt Cache（优先级最高）

**效果**: 减少 90% token 消耗

**配置**:
```json
{
  "cache": {
    "enabled": true,
    "ttl": 3600,
    "type": "ephemeral"
  }
}
```

**预期节省**: $150/月 → $15/月

---

### SOUL 精简

**原则**:
- 用表格代替长文本
- 删除示例和模板
- 使用链接

**效果**: SOUL 文件 5k → 2k tokens

**预期节省**: 60%

---

### 动态模型选择

**writing-pm 示例**:
```markdown
| 任务等级 | 模型 | 场景 |
|----------|------|------|
| Critical | Opus | 对外公告 |
| High | GLM-5 | 重要文档 |
| Normal | GLM-5 | 日常邮件 |
```

**效果**: Opus 使用率 100% → <10%

**预期节省**: 5x

---

## 🔧 运维最佳实践

### 每日检查

```bash
# 早上运行
~/openclaw-system/clawos/scripts/health-check.sh

# 检查输出
# 确保所有项 ✅
```

### 每周收割

```bash
# 周日运行
~/openclaw-system/clawos/scripts/daily-harvest.sh

# 检查产出
ls ~/clawos/blackboard/harvest/$(date +%Y-%m-%d)/
```

### 每月优化

- [ ] 查看成本报告
- [ ] 识别高消耗任务
- [ ] 优化 SOUL 文件
- [ ] 更新模型配置

---

## 🚀 性能优化

### 响应速度

**目标**: <30s

**方法**:
1. 启用缓存
2. 使用本地模型（可选）
3. 批处理任务

**验证**:
```bash
time openclaw agent run gm --task "测试"
# 预期: <30s
```

---

### Token 消耗

**目标**: GM <5k

**方法**:
1. Prompt Cache
2. 精简 SOUL
3. 只读 summary.md

**验证**:
```bash
openclaw stats tokens | grep gm
# 预期: <5k
```

---

### 可靠性

**目标**: 99.9% 可用

**方法**:
1. 健康检查 cron
2. 自动重启
3. 监控告警

**配置**:
```bash
# 每 5 分钟检查
*/5 * * * * ~/openclaw-system/clawos/scripts/health-check.sh
```

---

## 📝 文档最佳实践

### Summary.md

**每个任务必须有 summary.md**

**模板**:
```markdown
# {任务} - 摘要

**任务ID**: {id}
**完成时间**: {time}
**状态**: ✅/❌

## 一句话总结

{50 字以内}

## 关键产出

| 产出物 | 路径 |
|--------|------|

## 下一步

1. {建议1}
```

---

### Blackboard 组织

**结构**:
```
blackboard/
├── tasks/         # 任务数据
│   └── {task-id}/
│       ├── task.md
│       ├── summary.md  ← 必须有
│       └── status.md
├── gm/            # GM 决策
├── reports/       # 报告
├── proposals/     # 提案
└── shared/        # 共享
```

---

## 🔒 安全最佳实践

### Token 管理

- [ ] 定期更换 token（每月）
- [ ] 不同节点使用不同 token
- [ ] Token 加密存储

### 权限控制

- [ ] GM 不能直接操作 Worker
- [ ] Workers 限制命令执行
- [ ] 外部访问需要认证

---

## 📈 监控最佳实践

### 关键指标

| 指标 | 目标 | 告警阈值 |
|------|------|----------|
| 响应时间 | <30s | >60s |
| Token 消耗 | <5k | >10k |
| 可用性 | 99.9% | <99% |
| 成本 | <$1/天 | >$2/天 |

### 告警配置

```bash
# 配置 iMessage 告警
openclaw alert config imessage --enable

# 设置阈值
openclaw alert set --metric "gm_tokens" --threshold 10000
```

---

## 🎓 学习路径

### 初级

- [ ] 完成第一次对话
- [ ] 查看系统状态
- [ ] 理解架构

### 中级

- [ ] 添加新节点
- [ ] 优化成本
- [ ] 自定义工作流

### 高级

- [ ] 开发新 Agent
- [ ] 扩展 Federation
- [ ] 优化架构

---

**版本**: 1.0
**最后更新**: 2026-02-26
