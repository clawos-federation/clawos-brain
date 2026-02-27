# ClawOS Browser 能力优化规划方案

**研究时间**: 2026-02-25 19:40 UTC  
**范围**: Browser Worker Agent 设计 + Gateway 架构 + 实施计划

---

## 📊 现状分析

### 当前 Browser 能力分布

| 组件 | 位置 | 能力 | 问题 |
|------|------|------|------|
| **openclaw browser CLI** | OpenClaw 核心 | 40+ 命令，功能完整 | 需要中继连接（断裂点） |
| **Browser Relay 扩展** | Chrome 扩展 | 中继通信 | 需手动点击连接 |
| **browser-use-bridge.py** | workspace/agents | AI 驱动浏览器自动化 | 游离在体系外，未纳入 16 Agents |
| **browser-logic-driver.js** | workspace/agents | Playwright 执行 | 独立运行，无协调 |

### 核心问题

1. **断裂点**: Browser Relay 需手动点击才能连接
2. **体系外**: browser-use-bridge 和 browser-logic-driver 未纳入 Agent 体系
3. **协调缺失**: 没有统一的 Browser Worker 来协调这些能力
4. **接口分散**: CLI、Python、JavaScript 三种接口，无统一网关

---

## 🎯 设计方案

### 方案 1: Browser Worker Agent

#### 职责定义

**做什么**:
- ✅ 协调 openclaw browser CLI 命令
- ✅ 管理浏览器会话生命周期
- ✅ 处理 AI 驱动的浏览器自动化任务
- ✅ 提供统一的 Browser API 接口
- ✅ 处理浏览器中继连接（自动化）
- ✅ 记录浏览器操作日志和截图

**不做什么**:
- ❌ 不直接执行 JavaScript（通过 CLI 委托）
- ❌ 不管理浏览器进程（由 OpenClaw 管理）
- ❌ 不处理网络代理或 VPN
- ❌ 不存储浏览器数据（临时存储）

#### 架构位置

```
16 Agents 体系
├── assistant (主助手)
├── gm (全局管理)
├── platform-pm (平台管理)
├── coding-pm (开发管理)
├── writing-pm (写作管理)
├── validator (验证)
├── [新增] browser-worker ← Browser Worker Agent
│   ├── 依赖: openclaw browser CLI
│   ├── 依赖: Browser Relay 扩展
│   ├── 集成: browser-use-bridge.py
│   └── 集成: browser-logic-driver.js
└── ... (其他 Agents)
```

#### 核心职责

```javascript
// Browser Worker 的核心职责

class BrowserWorker {
  // 1. 会话管理
  async initSession(profile = 'default') {
    // 启动浏览器，自动处理中继连接
  }
  
  // 2. 命令执行
  async executeCommand(command, args) {
    // 通过 openclaw browser CLI 执行命令
    // 支持: navigate, click, fill, screenshot, etc.
  }
  
  // 3. AI 驱动自动化
  async runAITask(task, url) {
    // 使用 browser-use-bridge 执行 AI 驱动任务
  }
  
  // 4. 精确执行
  async runPreciseTask(task, url) {
    // 使用 browser-logic-driver 执行精确任务
  }
  
  // 5. 日志和证据
  async captureEvidence() {
    // 截���、记录操作日志
  }
}
```

---

### 方案 2: Browser Gateway 架构

#### 设计目标

统一三种接口（CLI、Python、JavaScript）为单一网关，消除断裂点。

#### 架构图

```
┌─────────────────────────────────────────┐
│         Browser Gateway (统一接口)       │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   Browser Worker Agent           │  │
│  │  (协调和管理)                    │  │
│  └──────────────────────────────────┘  │
│           ↓                             │
│  ┌──────────────────────────────────┐  │
│  │   Gateway Router                 │  │
│  │  (路由请求到合适的执行器)        │  │
│  └──────────────────────────────────┘  │
│      ↙        ↓        ↘               │
│  ┌────┐  ┌────┐  ┌────┐              │
│  │CLI │  │AI  │  │Prec│              │
│  │Exec│  │Task│  │ise │              │
│  └────┘  └────┘  └────┘              │
│                                         │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│      OpenClaw Browser Infrastructure    │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  openclaw browser CLI (40+ cmd)  │  │
│  └──────────────────────────────────┘  │
│           ↓                             │
│  ┌──────────────────────────────────┐  │
│  │  Browser Relay 扩展              │  │
│  │  (自动连接，无需手动点击)        │  │
│  └──────────────────────────────────┘  │
│           ↓                             │
│  ┌──────────────────────────────────┐  │
│  │  Chrome/Chromium 浏览器          │  │
│  └──────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
```

#### 关键改进

1. **自动中继连接**: Browser Worker 启动时自动处理中继连接
2. **统一 API**: 所有请求通过 Gateway Router 路由
3. **智能执行器选择**: 根据任务类型选择合适的执行器
4. **完整日志**: 所有操作都被记录和追踪

---

### 方案 3: 与现有 PM 层的协作

#### Browser Worker 与各 PM 的关系

```
┌─────────────────────────────────────────┐
│           Browser Worker                │
└─────────────────────────────────────────┘
    ↙          ↓          ↘
┌────────┐ ┌────────┐ ┌────────┐
│coding- │ │writing-│ │platform│
│pm      │ │pm      │ │pm      │
└────────┘ └────────┘ └────────┘

协作方式：
- coding-pm: 测试自动化、UI 测试、E2E 测试
- writing-pm: 内容采集、网页截图、文档生成
- platform-pm: 系统监控、性能测试、基础设施验证
```

#### 调用模式

```
coding-pm 需要 E2E 测试
  ↓
请求 browser-worker 执行测试任务
  ↓
browser-worker 通过 Gateway 执行
  ↓
返回测试结果 + 截图证据
  ↓
coding-pm 验证并报告
```

---

## 📋 实施计划

### Phase 1: 基础集成（1-2 周）

**目标**: 创建 Browser Worker Agent，集成现有能力

**任务**:
1. 创建 browser-worker Agent 定义
   - 在 openclaw.json 中注册
   - 定义基本职责和权限
   - 配置与其他 Agents 的关系

2. 实现 Browser Gateway Router
   - 统一 CLI、Python、JavaScript 接口
   - 实现请求路由逻辑
   - 添加错误处理和重试

3. 自动化中继连接
   - 修改 Browser Relay 扩展
   - 实现自动连接机制
   - 消除手动点击需求

4. 集成现有能力
   - 集成 browser-use-bridge.py
   - 集成 browser-logic-driver.js
   - 统一日志和证据收集

**交付物**:
- browser-worker Agent 定义
- Browser Gateway 实现
- 集成测试

---

### Phase 2: PM 协作集成（2-3 周）

**目标**: 与 coding-pm、writing-pm、platform-pm 集成

**任务**:
1. 定义 PM 调用接口
   - coding-pm: E2E 测试接口
   - writing-pm: 内容采集接口
   - platform-pm: 系统监控接口

2. 实现协作工作流
   - 任务分配和调度
   - 结果收集和报告
   - 证据管理

3. 添加监控和告警
   - 浏览器会话监控
   - 性能指标收集
   - 异常告警

**交付物**:
- PM 协作接口
- 工作流实现
- 监控系统

---

### Phase 3: 高级功能（3-4 周）

**目标**: 添加高级功能和优化

**任务**:
1. 实现浏览器池管理
   - 多会话管理
   - 资源优化
   - 负载均衡

2. 添加 AI 驱动功能
   - 智能任务分解
   - 自适应执行策略
   - 学习和优化

3. 性能优化
   - 缓存机制
   - 并行执行
   - 资源清理

**交付物**:
- 浏览器池管理
- AI 驱动功能
- 性能优化

---

## 🔧 技术细节

### Browser Worker Agent 定义

```json
{
  "id": "browser-worker",
  "name": "Browser Worker",
  "description": "浏览器自动化和交互协调",
  "model": {
    "primary": "zai/glm-5"
  },
  "capabilities": [
    "browser-automation",
    "ai-driven-tasks",
    "precise-execution",
    "evidence-collection"
  ],
  "permissions": [
    "browser-control",
    "screenshot",
    "file-write",
    "network-access"
  ],
  "subagents": {
    "allowAgents": []
  },
  "heartbeat": {
    "every": "1h",
    "prompt": "检查浏览器会话状态，清理过期会话，生成运行报告"
  }
}
```

### Gateway Router 实现

```javascript
class BrowserGateway {
  async route(request) {
    const { type, task, url, args } = request;
    
    switch(type) {
      case 'cli':
        return await this.executeCLI(task, args);
      case 'ai-task':
        return await this.executeAITask(task, url);
      case 'precise':
        return await this.executePrecise(task, url);
      default:
        throw new Error(`Unknown task type: ${type}`);
    }
  }
  
  async executeCLI(command, args) {
    // 通过 openclaw browser CLI 执行
  }
  
  async executeAITask(task, url) {
    // 通过 browser-use-bridge 执行
  }
  
  async executePrecise(task, url) {
    // 通过 browser-logic-driver 执行
  }
}
```

---

## 📊 优先级和风险

### 优先级

1. **高**: Phase 1 基础集成（消除断裂点）
2. **中**: Phase 2 PM 协作（提高可用性）
3. **低**: Phase 3 高级功能（性能优化）

### 风险

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| 中继连接自动化失败 | 中 | 高 | 保留手动回退 |
| 性能下降 | 低 | 中 | 添加缓存和优化 |
| 兼容性问题 | 低 | 中 | 充分测试 |

---

## ✅ 成功指标

- ✅ Browser Worker 成功注册到 16 Agents 体系
- ✅ 中继连接自动化（无需手动点击）
- ✅ 三种接口统一到单一 Gateway
- ✅ PM 层成功集成
- ✅ 浏览器操作日志完整
- ✅ 证据收集自动化

---

**规划完成**: ✅ 2026-02-25 19:40 UTC  
**下一步**: 启动 Phase 1 实施
