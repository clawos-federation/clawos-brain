# OpenClaw Agents - 3 分钟快速入门

在 3 分钟内掌握 OpenClaw Professional Agents 的核心使用方法。

---

## ⏱️ 时间线

- **第 1 分钟**: 环境检查和首次运行
- **第 2 分钟**: 路由你的第一个任务
- **第 3 分钟**: 查看结果和更多探索

---

## 第 1 分钟：环境检查 🚀

### 检查安装

```bash
# 进入 agents 目录
cd /Users/henry/openclaw-system/workspace/agents

# 列出可用的 agents
node agent-factory.js list
```

**预期输出**：
```
✅ Loaded agent registry (v1.0.0)

📋 Available Agents:

🟢 devagent             v0.1.0    [active]
🟢 legalagent           v0.1.0    [active]
🟢 researchagent        v0.1.0    [active]
```

### 如果看到错误

```bash
# 确认 Node.js 版本
node --version  # 应该 >= 18

# 确认在正确的目录
pwd  # 应该显示 .../agents
```

---

## 第 2 分钟：路由任务 🎯

### 尝试不同的任务类型

#### 开发任务

```bash
node agent-router.js route "创建一个用户登录 API"
```

**预期**：路由到 `devagent` (代码专家)

#### 法律任务

```bash
node agent-router.js route "审查服务合同中的责任条款"
```

**预期**：路由到 `legalagent` (法律专家)

#### 研究任务

```bash
node agent-router.js route "研究人工智能在医疗领域的应用"
```

**预期**：路由到 `researchagent` (研究专家)

### 理解输出

```
🔍 Task Analysis:
   Keywords: 创建, API
   Capabilities: code-generation
   Complexity: low
   Risk: low

📊 Agent Scoring:
   devagent        ██████████ 100%

🎯 Routing Strategy:
   Mode: single-agent
   Description: 单 agent 执行
   Agents: devagent

✅ Routing complete
```

---

## 第 3 分钟：查看结果和探索 📊

### 运行集成测试

```bash
node integration-test.js
```

**预期**：
```
============================================================
🧪 OpenClaw Agents Integration Test
============================================================

📋 Test: Agent Router ✅ PASS
📋 Test: Context Manager ✅ PASS
📋 Test: Task Dispatcher (Single) ✅ PASS
📋 Test: Task Dispatcher (Parallel) ✅ PASS
📋 Test: Task Dispatcher (Sequential) ✅ PASS
📋 Test: Agent Monitor ✅ PASS
📋 Test: End-to-End ✅ PASS

============================================================
📊 Results: 7 passed, 0 skipped, 0 failed
============================================================

🎉 All tests passed!
```

### 查看健康状态

```bash
node agent-monitor.js health
```

**预期**：
```
📊 Loaded metrics (X executions)

🏥 Agent Health Status:

   Status: HEALTHY
   Success Rate: 100.0%
   Total Executions: X
   Avg Duration: XXXms
```

### 查看完整指标

```bash
node agent-monitor.js metrics
```

---

## 🎓 接下来学什么

### 1. 深入理解 Agent 能力

查看每个 agent 的详细信息：

```bash
# DevAgent
cat devagent/agent.json
cat devagent/prompt.md

# LegalAgent
cat legalagent/agent.json
cat legalagent/prompt.md

# ResearchAgent
cat researchagent/agent.json
cat researchagent/prompt.md
```

### 2. 尝试多 Agent 协作

虽然目前是模拟执行，但可以测试协作模式：

```bash
# 触发并行投票（高风险任务）
node task-dispatcher.js execute "设计符合 GDPR 的数据收集系统"

# 触发顺序链（复杂任务）
node task-dispatcher.js execute "开发电商平台，包含研究和代码"
```

### 3. 自定义你的任务

尝试各种类型的任务：

| 类型 | 示例命令 |
|------|----------|
| 开发 | `node agent-router.js route "实现一个 WebSocket 服务器"` |
| 调试 | `node agent-router.js route "修复内存泄漏问题"` |
| 重构 | `node agent-router.js route "优化数据库查询性能"` |
| 法律 | `node agent-router.js route "检查雇佣合同的竞业限制条款"` |
| 合规 | `node agent-router.js route "评估产品是否符合 COPPA"` |
| 研究 | `node agent-router.js route "分析 Web3 技术的发展趋势"` |
| 竞品 | `node agent-router.js route "研究竞争对手的定价策略"` |

---

## 🆘 快速故障排除

### 问题：找不到命令

```bash
# 错误：command not found: node
# 解决：安装 Node.js
# macOS: brew install node
# Linux: sudo apt install nodejs
```

### 问题：No matching agents

```bash
# 症状：⚠️ No matching agents found
# 解决：尝试更具体的描述
# ❌ node agent-router.js route "帮我"
# ✅ node agent-router.js route "帮我创建一个 API"
```

### 问题：测试失败

```bash
# 症状：某些测试失败
# 解决：检查文件权限和路径
ls -la
chmod +x *.js
```

---

## 📚 更多资源

- **完整文档**: `README.md`
- **API 参考**: `API.md`
- **使用示例**: `EXAMPLES.md`
- **架构设计**: `README.md` - 架构设计章节

---

## ⚡ 常用命令速查

```bash
# 列出 agents
node agent-factory.js list

# 路由任务
node agent-router.js route "<任务>"

# 运行测试
node integration-test.js

# 健康检查
node agent-monitor.js health

# 查看指标
node agent-monitor.js metrics

# 查看历史
node task-dispatcher.js history
```

---

**完成！** 🎉 你已经掌握了 OpenClaw Agents 的基本使用方法。

下一步？查看 [README.md](./README.md) 了解更多高级特性。
