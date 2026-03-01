# 使用示例 (Examples)

本文件提供 OpenClaw Professional Agents 在各种实际场景下的详细使用示例。

---

## 📖 目录

- [1. 简单任务 (Simple Tasks)](#1-简单任务-simple-tasks)
- [2. 法律与合规 (Legal & Compliance)](#2-法律与合规-legal--compliance)
- [3. 深度研究 (Deep Research)](#3-深度研究-deep-research)
- [4. 并行协作 (Parallel Collaboration)](#4-并行协作-parallel-collaboration)
- [5. 顺序链编排 (Sequential Chain)](#5-顺序链编排-sequential-chain)
- [6. 复杂项目 (Complex Projects)](#6-复杂项目-complex-projects)

---

## 1. 简单任务 (Simple Tasks)

适用于明确属于单一领域的日常任务。

### 场景：编写 API 接口
**输入**：`node agent-router.js route "用 Node.js 实现一个简单的待办事项 API，包含增删改查功能"`

**内部逻辑**：
1. **关键词提取**：`Node.js`, `API`, `增删改查`
2. **能力匹配**：`code-generation` (100% 匹配)
3. **路由决策**：`devagent` (Score: 1.0)
4. **执行模式**：`single-agent`

**输出示例**：
```javascript
// Express API for TODOs
const express = require('express');
const app = express();
app.use(express.json());

let todos = [];

app.get('/todos', (req, res) => res.json(todos));
app.post('/todos', (req, res) => {
  const todo = { id: Date.now(), text: req.body.text, completed: false };
  todos.push(todo);
  res.status(201).json(todo);
});
// ... (PUT/DELETE logic)
app.listen(3000, () => console.log('Server running on port 3000'));
```

---

## 2. 法律与合规 (Legal & Compliance)

利用 `legalagent` 处理专业的法律文书和风险评估。

### 场景：审查保密协议 (NDA)
**输入**：`node agent-router.js route "审查这份保密协议，特别注意违约金条款和有效期"`

**内部逻辑**：
1. **分析**：识别为 `contract-review` 和 `risk-assessment`
2. **匹配**：`legalagent` 具有最高的法律背景分
3. **决策**：由 `legalagent` 独立处理

**输出示例**（法律审查报告）：
> ### 合同审查报告
> **关键风险点：**
> 1. **违约金条款**：第 5.2 条规定的违约金过高（100万美元），在某些管辖区可能被法院认定为惩罚性条款而无效。
> 2. **有效期**：协议规定保密义务为“永久”，建议修改为“合同终止后 3-5 年”，以符合商业惯例。
> **建议修改：**
> - 将第 5.2 条修改为“根据实际损失赔偿”。
> - 将第 8.1 条有效期明确。

---

## 3. 深度研究 (Deep Research)

利用 `researchagent` 的 ToT (Tree of Thoughts) 规划能力处理复杂信息搜集。

### 场景：行业趋势分析
**输入**：`node agent-router.js route "分析 2026 年生成式 AI 在自动驾驶领域的应用趋势"`

**内部逻辑**：
1. **规划**：采用 `tree_of_thoughts` 分支探索
2. **搜索**：调用 `web_search` 获取最新研报和新闻
3. **分析**：提取关键技术（端到端大模型、世界模型）

**输出示例**：
> # 2026 AI 自动驾驶研究简报
> **核心发现：**
> - **端到端模型主流化**：从感知到决策的单一模型取代了传统的模块化架构。
> - **世界模型 (World Models)**：用于模拟极端工况（Long-tail events）的生成式模拟器成为训练标配。
> **领先厂商动态：**
> - Tesla FSD v13 部署情况...
> - Waymo 在新城市的扩张数据...

---

## 4. 并行协作 (Parallel Collaboration)

针对高风险或需要多重视角的任务，触发 `parallel-voting`。

### 场景：评估数据隐私设计
**输入**：`node task-dispatcher.js execute "设计一个面向全球用户的用户画像系统，需平衡营销精准度和隐私合规"`

**内部逻辑**：
1. **风险识别**：识别为 `high-risk` (涉及全球隐私法规)
2. **策略**：`parallel-voting` (devagent + legalagent + researchagent)
3. **执行**：
   - `devagent`: 提供技术实现方案（差异隐私、联邦学习）
   - `legalagent`: 提供 GDPR/CCPA 合规性检查
   - `researchagent`: 提供行业最佳实践调研
4. **聚合**：`ContextManager` 投票并汇总最佳方案。

---

## 5. 顺序链编排 (Sequential Chain)

处理具有严格前后依赖关系的复杂任务。

### 场景：从调研到代码实现
**任务**：`"调研最新的加密支付网关 API，并给出一个集成示例"`

**执行链**：
1. **Step 1 (`researchagent`)**: 搜索并对比 Stripe, PayPal, Coinbase Commerce 的最新 API。
2. **Context Passing**: 将调研结果传递给下一个 Agent。
3. **Step 2 (`devagent`)**: 根据 Step 1 选出的最适合方案（如 Stripe），编写完整的集成代码。

---

## 6. 复杂项目 (Complex Projects)

层级模式 (Hierarchy) 应对大型工程。

### 场景：构建企业级合规监控平台
**编排方式**：
- **Manager (GM)**: 拆分项目为子模块。
- **Research**: 调研不同国家的合规要求。
- **Legal**: 定义平台的自动化审查逻辑基准。
- **Dev**: 实现核心后端架构和前端看板。
- **QA (DevAgent)**: 编写集成测试确保逻辑严密。

---

## 🛠️ 如何运行这些示例？

你可以使用项目自带的集成测试脚本来模拟这些场景：

```bash
# 运行内置场景测试
node integration-test.js
```

或者手动测试路由器对特定描述的反应：

```bash
node agent-router.js route "你的任务描述"
```

---

**想查看更多？** 请参考 [API 参考文档](./API.md) 了解如何通过代码自定义这些场景。
