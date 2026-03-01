# REACT-ENHANCED.md - ClawOS 增强版 ReAct 循环

**版本**: 1.0.0
**更新时间**: 2026-02-25
**状态**: ✅ 已定义

---

## 传统 ReAct vs 增强版 ReAct

### 传统 ReAct (LangChain)

```
Thought → Action → Observation → (循环)
```

**问题**:
- ❌ 缺少反思机制
- ❌ 没有错误恢复能力
- ❌ 无法学习和改进

### 增强版 ReAct (ClawOS)

```
Think → Act → Observe → Reflect → Adapt → (循环)
```

**改进**:
- ✅ 添加 Reflect 阶段（反思）
- ✅ 添加 Adapt 阶段（适应）
- ✅ 支持错误恢复
- ✅ 支持经验积累

---

## 五阶段详解

### 1. Think (思考)

**目的**: 分析问题，制定计划

**输入**:
- 原始任务
- 上下文信息
- 历史经验

**输出**:
```json
{
  "phase": "think",
  "analysis": {
    "problem": "问题本质是什么",
    "constraints": ["约束1", "约束2"],
    "unknowns": ["未知1", "未知2"]
  },
  "options": [
    {
      "id": "option-1",
      "description": "方案描述",
      "pros": ["优点"],
      "cons": ["缺点"],
      "risk": "low|medium|high"
    }
  ],
  "selectedOption": "option-1",
  "reasoning": "为什么选择这个方案"
}
```

**检查点**:
- [ ] 问题理解是否正确？
- [ ] 约束是否完整？
- [ ] 选项是否足够？

---

### 2. Act (行动)

**目的**: 执行选定的方案

**输入**:
- Think 阶段的决策
- 可用工具列表

**输出**:
```json
{
  "phase": "act",
  "tool": "tool-name",
  "params": {
    "param1": "value1"
  },
  "expectedOutcome": "预期结果",
  "timeout": 30000,
  "fallback": {
    "tool": "backup-tool",
    "params": {}
  }
}
```

**检查点**:
- [ ] 工具是否可用？
- [ ] 参数是否正确？
- [ ] 是否有 fallback？

---

### 3. Observe (观察)

**目的**: 获取执行结果

**输入**:
- Act 阶段的执行结果

**输出**:
```json
{
  "phase": "observe",
  "result": {
    "success": true,
    "data": {},
    "error": null
  },
  "keyFindings": [
    "发现1",
    "发现2"
  ],
  "unexpectedFindings": [
    "意外发现1"
  ],
  "questions": [
    "需要进一步确认的问题"
  ]
}
```

**检查点**:
- [ ] 结果是否符合预期？
- [ ] 有没有意外发现？
- [ ] 有没有遗漏的信息？

---

### 4. Reflect (反思) ← **新增**

**目的**: 评估效果，识别问题

**输入**:
- 前三个阶段的所有数据

**输出**:
```json
{
  "phase": "reflect",
  "evaluation": {
    "success": true,
    "score": 0.85,
    "criteria": {
      "correctness": 0.9,
      "completeness": 0.8,
      "efficiency": 0.85
    }
  },
  "issues": [
    {
      "type": "error|inefficiency|gap",
      "description": "问题描述",
      "severity": "low|medium|high",
      "cause": "根本原因"
    }
  ],
  "lessons": [
    "学到的经验1",
    "学到的经验2"
  ],
  "improvements": [
    "改进建议1"
  ]
}
```

**检查点**:
- [ ] 评分是否合理？
- [ ] 问题根因是否找到？
- [ ] 经验是否值得记录？

---

### 5. Adapt (适应) ← **新增**

**目的**: 调整策略，准备下一轮

**输入**:
- Reflect 阶段的分析

**输出**:
```json
{
  "phase": "adapt",
  "decision": "continue|pivot|abort|complete",
  "nextAction": {
    "type": "retry|alternative|escalate|done",
    "reason": "原因说明",
    "params": {}
  },
  "strategyUpdate": {
    "newConstraints": [],
    "newOptions": [],
    "modifiedOption": null
  },
  "experienceRecorded": true,
  "experienceId": "exp-uuid"
}
```

**决策类型**:
| 决策 | 说明 | 触发条件 |
|------|------|----------|
| continue | 继续当前方案 | 进展顺利 |
| pivot | 切换到备选方案 | 当前方案受阻 |
| abort | 放弃任务 | 不可恢复的错误 |
| complete | 任务完成 | 目标达成 |

**检查点**:
- [ ] 决策是否合理？
- [ ] 经验是否记录？
- [ ] 下一轮准备是否就绪？

---

## 循环控制

### 最大循环次数

```json
{
  "maxIterations": 10,
  "onMaxIterations": "escalate"
}
```

### 超时控制

```json
{
  "timeoutPerPhase": {
    "think": 30000,
    "act": 60000,
    "observe": 10000,
    "reflect": 20000,
    "adapt": 10000
  },
  "totalTimeout": 300000
}
```

### 早停条件

```json
{
  "earlyStop": {
    "onComplete": true,
    "onAbort": true,
    "onMaxErrors": 3,
    "onUserCancel": true
  }
}
```

---

## 经验积累

### 经验记录格式

```json
{
  "id": "exp-uuid",
  "timestamp": "2026-02-25T18:50:00+08:00",
  "task": {
    "type": "task-type",
    "description": "任务描述"
  },
  "outcome": {
    "success": true,
    "score": 0.85
  },
  "lessons": [
    "经验1",
    "经验2"
  ],
  "patterns": [
    {
      "trigger": "触发条件",
      "action": "推荐行动",
      "confidence": 0.9
    }
  ]
}
```

### 经验检索

```python
def get_relevant_experience(task_description):
    """检索相关经验"""
    experiences = read_experiences()

    relevant = []
    for exp in experiences:
        similarity = calculate_similarity(task_description, exp.task.description)
        if similarity > 0.7:
            relevant.append({
                "experience": exp,
                "relevance": similarity
            })

    return sorted(relevant, key=lambda x: x["relevance"], reverse=True)
```

---

## 错误恢复

### 错误分类

| 类型 | 恢复策略 | 示例 |
|------|----------|------|
| 工具不可用 | 使用 fallback | API 限流 → 本地缓存 |
| 参数错误 | 自动修正 | 格式错误 → 自动转换 |
| 结果异常 | 重试或 pivot | 空结果 → 换查询方式 |
| 超时 | 分割任务 | 大任务 → 分批执行 |

### 恢复流程

```
Error → Classify → Select Recovery → Execute → Verify
         ↓              ↓
      (记录经验)    (通知上层)
```

---

## 监控指标

| 指标 | 说明 | 目标值 |
|------|------|--------|
| 平均循环次数 | 完成任务所需的迭代数 | < 5 |
| 反思有效率 | 反思后改进的比例 | > 60% |
| 错误恢复率 | 自动恢复成功的比例 | > 80% |
| 经验复用率 | 应用历史经验的比例 | > 30% |

---

## 实现示例

```python
class EnhancedReActAgent:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.iteration = 0
        self.max_iterations = 10

    def execute(self, task):
        context = {
            "task": task,
            "history": [],
            "experiences": get_relevant_experience(task)
        }

        while self.iteration < self.max_iterations:
            # 1. Think
            think_result = self.think(context)
            context["history"].append(("think", think_result))

            # 2. Act
            act_result = self.act(think_result)
            context["history"].append(("act", act_result))

            # 3. Observe
            observe_result = self.observe(act_result)
            context["history"].append(("observe", observe_result))

            # 4. Reflect
            reflect_result = self.reflect(context)
            context["history"].append(("reflect", reflect_result))

            # 5. Adapt
            adapt_result = self.adapt(reflect_result)
            context["history"].append(("adapt", adapt_result))

            # 记录经验
            if reflect_result["lessons"]:
                record_experience(context, reflect_result)

            # 检查是否完成
            if adapt_result["decision"] == "complete":
                return {"success": True, "result": observe_result}
            elif adapt_result["decision"] == "abort":
                return {"success": False, "reason": adapt_result["reason"]}

            self.iteration += 1

        return {"success": False, "reason": "max_iterations_exceeded"}
```

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-02-25 | 初始版本，添加 Reflect 和 Adapt 阶段 |

---

**ClawOS 2026.3 - Enhanced ReAct Framework**
