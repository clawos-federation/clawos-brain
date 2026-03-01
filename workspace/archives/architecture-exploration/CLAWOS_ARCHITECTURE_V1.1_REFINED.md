# 🏗️ ClawOS × OpenClaw 架构精修版

> **核心理念**: 不重写 Gateway，直接映射 OpenClaw 能力到 Agent 世界
> **版本**: v1.1 (基于深度理解后的精修版)

---

## 一、OpenClaw Gateway 本质再确认

### 1.1 Gateway 不是什么

| 误区 | 正确理解 |
|------|----------|
| ❌ API 网关 | ✅ 分布式节点网络的信任根 |
| ❌ 消息队列 | ✅ 隧道管理器（数据走 P2P，控制面走 Gateway）|
| ❌ 调度器 | ✅ 资源抽象层 + 策略执行器 |

### 1.2 Gateway 核心能力

```
┌─────────────────────────────────────────────────────────┐
│                 OpenClaw Gateway                         │
├─────────────────────────────────────────────────────────┤
│  Node Registry    │ 节点注册、发现、心跳、上下线        │
│  Tunnel Manager   │ 加密 P2P 隧道、信任根               │
│  Resource Pool    │ LLM/Tool/Skill/KB 抽象              │
│  Policy Engine    │ 权限、配额、流量控制                 │
│  Event Bus        │ 事件发布、订阅、Hook 触发           │
│  Task Queue       │ 任务队列、检查点、断点续跑           │
└─────────────────────────────────────────────────────────┘
```

---

## 二、概念映射（精确版）

### 2.1 一对一映射

```
OpenClaw 概念              ClawOS Agent 概念
────────────────────────────────────────────────────
Node                      Agent 实例（运行时）
Node.metadata             Agent 八件套配置
Node.status               Agent 状态（idle/busy/error）
Tunnel                    Agent 间通信信道
Resource                  LLM/Tool/Skill/KB
Policy                    Agent 权限边界
Event                     Hook 触发源
Task                      用户任务抽象
```

### 2.2 层级映射

```
OpenClaw 层级             ClawOS 角色层级
────────────────────────────────────────────────────
Gateway Admin             GM Agent（唯一管理权限）
Gateway User              PM/Worker/Assistant（使用权限）
Node                      Agent 实例
Node Group                项目团队（PM + Workers）
```

---

## 三、Agent 八件套 × OpenClaw 实现（精修版）

### 3.1 完整映射表

| # | 八件套 | OpenClaw 实现 | 配置位置 | 运行时可改 |
|---|--------|--------------|----------|-----------|
| 1 | 身份角色 | Node.metadata.role | 注册时写入 | ❌ |
| 2 | 绑定 LLM | Resource(llm) 挂载 | PM 任命时 | ✅ |
| 3 | 工具集 | Toolbox 调用权限 | Policy 定义 | ❌ |
| 4 | 技能集 | Skill 包注入 | Node 启动时 | ✅ |
| 5 | 知识库 | Knowledge Node 挂载 | Policy 定义 | ✅ |
| 6 | 记忆 | Context + Knowledge | 运行时管理 | ✅ |
| 7 | 触发器 | Event Bus 订阅 | PM 注册 | ✅ |
| 8 | 权限 | Policy Engine | GM 定义 | ❌ |

### 3.2 详细实现规范

#### ① 身份角色（Role）

```typescript
// OpenClaw Node 注册时的 metadata
interface AgentMetadata {
  // 基础信息
  id: string;           // 唯一标识
  name: string;         // 显示名称
  role: AgentRole;      // gm | assistant | platform-pm | project-pm | worker
  
  // 层级关系
  tier: 'L1' | 'L2' | 'L3' | 'worker';
  teamId?: string;      // 所属团队
  parentPm?: string;    // 上级 PM
  
  // 能力标签
  capabilities: string[];
  specializations: string[];
  
  // 元数据
  createdAt: Date;
  createdBy: string;    // 创建者 Agent ID
  version: string;
}

type AgentRole = 
  | 'gm'           // 总经理
  | 'assistant'    // 助理
  | 'platform-pm'  // 平台 PM（永久）
  | 'project-pm'   // 项目 PM（临时）
  | 'worker';      // 执行层
```

#### ② 绑定 LLM（大脑）

```typescript
// OpenClaw Resource 定义
interface LLMResource {
  type: 'llm';
  id: string;
  
  // 模型配置
  model: string;           // claude-opus-4-6-thinking | gpt-5.3-codex | ...
  endpoint: string;        // API 地址
  apiKey?: string;         // 密钥（由 Gateway 管理）
  
  // 配额
  quota: {
    maxTokensPerRequest: number;
    maxTokensPerDay: number;
    maxRequestsPerMinute: number;
  };
  
  // 策略
  fallback?: string;       // 降级模型
  retryPolicy: {
    maxRetries: number;
    backoffMs: number;
  };
}

// PM 任命 Worker 时绑定
interface LLMBinding {
  agentId: string;
  llmResourceId: string;
  quotaAllocation: {
    tokensPerTask: number;
    reserved: boolean;     // 是否独占
  };
}
```

#### ③ 工具集（Tools）

```typescript
// OpenClaw Toolbox
interface Tool {
  id: string;
  name: string;
  type: 'shell' | 'browser' | 'file' | 'http' | 'database' | 'custom';
  
  // 调用接口
  invoke(params: any): Promise<Result>;
  
  // 安全配置
  security: {
    sandboxLevel: 'none' | 'restricted' | 'isolated';
    allowedPaths?: string[];
    deniedPaths?: string[];
    networkAccess: boolean;
  };
}

// Policy 定义谁能调用什么
interface ToolPolicy {
  agentId: string;
  allowedTools: string[];
  deniedTools?: string[];
  rateLimit?: {
    callsPerMinute: number;
  };
}
```

#### ④ 技能集（Skills）

```typescript
// Skill 是 ClawOS 原创，存在 Platform PM 维护的 Registry
interface Skill {
  id: string;
  name: string;
  version: string;
  
  // 核心内容
  promptTemplate: string;     // Prompt 模板
  dependencies: string[];     // 依赖的其他 Skill
  tools: string[];            // 需要的工具
  
  // 执行逻辑
  execute: (context: SkillContext) => Promise<Result>;
  
  // 元数据
  category: string;
  tags: string[];
  rating: number;
  author: string;
}

// Node 启动时注入
interface SkillInjection {
  agentId: string;
  skills: string[];           // Skill ID 列表
  injectionTime: Date;
}
```

#### ⑤ 知识库（Knowledge）

```typescript
// OpenClaw Knowledge Node
interface KnowledgeNode {
  id: string;
  type: 'vector' | 'document' | 'structured';
  
  // 存储
  backend: 'pgvector' | 'pinecone' | 'local';
  namespace: string;
  
  // 访问接口
  query(query: string, options: QueryOptions): Promise<Chunk[]>;
  insert(documents: Document[]): Promise<void>;
  delete(ids: string[]): Promise<void>;
}

// 权限控制
interface KnowledgePolicy {
  agentId: string;
  knowledgeNodeId: string;
  permissions: ('read' | 'write' | 'admin')[];
  
  // 命名空间隔离
  namespace?: string;
  prefix?: string;
}
```

#### ⑥ 记忆（Memory）

```typescript
// 短时记忆：Node 内部 context window
interface ShortTermMemory {
  contextWindow: Message[];
  maxSize: number;
  strategy: 'fifo' | 'priority' | 'semantic';
}

// 长时记忆：Knowledge Node
interface LongTermMemory {
  agentId: string;
  knowledgeNodeId: string;
  namespace: `${agentId}:memory`;
  
  // 记忆类型
  types: ('episodic' | 'semantic' | 'procedural')[];
}

// 跨任务记忆：PM 决定是否持久化
interface MemoryPersistence {
  taskId: string;
  agentId: string;
  persistToKnowledge: boolean;
  selectedMemories: string[];
}
```

#### ⑦ 触发器/Hooks

```typescript
// OpenClaw Event Bus
interface Event {
  type: EventType;
  source: string;           // Agent ID
  payload: any;
  timestamp: Date;
}

type EventType = 
  | 'task.created'
  | 'task.started'
  | 'task.progress'
  | 'task.completed'
  | 'task.failed'
  | 'node.started'
  | 'node.stopped'
  | 'node.failed'
  | 'quality.rejected'
  | 'quality.approved'
  | 'resource.exhausted';

// Hook 注册
interface Hook {
  id: string;
  eventType: EventType;
  subscriber: string;       // Agent ID
  action: 'notify' | 'trigger' | 'callback';
  callback?: string;        // 回调函数
  filter?: EventFilter;     // 过滤条件
}

// PM 组建团队时注册 Hook
interface TeamHooks {
  teamId: string;
  hooks: Hook[];
  registeredBy: string;     // PM Agent ID
}
```

#### ⑧ 权限边界（Policy）

```typescript
// OpenClaw Policy Engine
interface AgentPolicy {
  agentId: string;
  
  // 三个维度
  connection: {
    canConnectTo: string[];      // 可连接的 Agent
    cannotConnectTo?: string[];  // 不可连接
  };
  
  resources: {
    llm: string[];               // 可用的 LLM
    tools: string[];             // 可用的工具
    knowledge: string[];         // 可访问的知识库
    skills: string[];            // 可使用的技能
  };
  
  limits: {
    maxConcurrentTasks: number;
    maxTokensPerDay: number;
    maxExecutionTimeMs: number;
    maxMemoryMB: number;
  };
}

// Policy 验证（Gateway 运行时执行）
interface PolicyEnforcement {
  checkConnection(from: string, to: string): boolean;
  checkResourceAccess(agent: string, resource: string): boolean;
  checkLimit(agent: string, type: LimitType): boolean;
  enforce(policy: AgentPolicy): void;
}
```

---

## 四、通信协议（基于 OpenClaw Tunnel）

### 4.1 消息格式

```typescript
interface AgentMessage {
  id: string;
  
  // 路由
  from: string;           // Agent ID
  to: string | 'broadcast' | 'team';
  teamId?: string;        // 团队广播时
  
  // 内容
  type: MessageType;
  payload: any;
  
  // 元数据
  priority: 'low' | 'normal' | 'high' | 'critical';
  requiresAck: boolean;
  timeout?: number;       // ms
  
  // 路由信息（Gateway 填充）
  timestamp: Date;
  hops: string[];         // 经过的节点
}

type MessageType =
  // 任务相关
  | 'task.assign'         // 分配任务
  | 'task.progress'       // 进度更新
  | 'task.result'         // 任务结果
  | 'task.error'          // 任务错误
  
  // 协作相关
  | 'collab.request'      // 请求协作
  | 'collab.response'     // 协作响应
  | 'collab.sync'         // 状态同步
  
  // 管理相关
  | 'mgmt.create'         // 创建 Agent
  | 'mgmt.destroy'        // 销毁 Agent
  | 'mgmt.authorize'      // 授权
  
  // 通知相关
  | 'notify.info'         // 信息通知
  | 'notify.warning'      // 警告
  | 'notify.critical';    // 紧急
```

### 4.2 通信模式

```typescript
// 1. 点对点（通过 Tunnel）
async function sendDirect(to: string, message: AgentMessage): Promise<void> {
  // Gateway 验证 Policy
  if (!policy.checkConnection(this.id, to)) {
    throw new Error('Connection not allowed');
  }
  
  // 通过 Tunnel 发送
  await tunnel.send(to, message);
}

// 2. 团队广播
async function broadcastToTeam(teamId: string, message: AgentMessage): Promise<void> {
  const members = await teamRegistry.getMembers(teamId);
  
  // 并行发送
  await Promise.all(
    members
      .filter(m => m.id !== message.from)
      .map(m => sendDirect(m.id, message))
  );
}

// 3. 会议机制
interface Meeting {
  id: string;
  teamId: string;
  host: string;           // PM Agent ID
  participants: string[];
  
  // 会议状态
  status: 'pending' | 'active' | 'ended';
  startTime?: Date;
  endTime?: Date;
  
  // 会议记录
  messages: AgentMessage[];
  decisions: Decision[];
  actionItems: ActionItem[];
}
```

---

## 五、任务生命周期（完整版）

### 5.1 任务状态机

```
                    ┌──────────┐
                    │ created  │
                    └────┬─────┘
                         │ GM 路由
                    ┌────▼─────┐
              ┌────►│ assigned │◄────┐
              │     └────┬─────┘     │
              │          │ PM 接收   │
              │     ┌────▼─────┐     │
              │     │ planned  │     │
              │     └────┬─────┘     │
              │          │ PM 分配   │ 打回重做
              │     ┌────▼─────┐     │
              │     │ running  │─────┘
              │     └────┬─────┘
              │          │ Worker 完成
              │     ┌────▼─────┐
              │     │reviewing │
              │     └────┬─────┘
              │          │ PM 审核
              │     ┌────▼─────┐
              │     │approved  │
              │     └────┬─────┘
              │          │ GM 验收
              │     ┌────▼─────┐
              └─────│ rejected │（可选）
              │     └────┬─────┘
              │          │
              │     ┌────▼─────┐
              └─────│completed │
                    └──────────┘
```

### 5.2 任务数据结构

```typescript
interface Task {
  id: string;
  
  // 基本信息
  type: TaskType;
  description: string;
  priority: 'low' | 'normal' | 'high' | 'critical';
  
  // 状态
  status: TaskStatus;
  assignee?: string;        // 当前负责人
  
  // 层级关系
  parentTaskId?: string;
  subtaskIds: string[];
  
  // 执行信息
  plan?: TaskPlan;
  progress?: TaskProgress;
  result?: TaskResult;
  
  // 检查点（支持断点续跑）
  checkpoints: Checkpoint[];
  
  // 审核记录
  reviews: Review[];
  
  // 时间
  createdAt: Date;
  startedAt?: Date;
  completedAt?: Date;
  deadline?: Date;
  
  // 元数据
  createdBy: string;        // Agent ID
  tags: string[];
}

interface TaskPlan {
  steps: {
    id: string;
    description: string;
    assignee: string;
    dependencies: string[];
    estimatedTime: number;
  }[];
  
  resources: {
    llm: string;
    tools: string[];
    skills: string[];
    knowledge: string[];
  };
}

interface Checkpoint {
  id: string;
  taskId: string;
  timestamp: Date;
  
  // 快照
  status: TaskStatus;
  progress: TaskProgress;
  artifacts: {
    type: string;
    path: string;
    checksum: string;
  }[];
  
  // 恢复信息
  recoveryInfo: {
    resumeFrom: string;     // Step ID
    requiredState: any;
  };
}

interface Review {
  id: string;
  reviewer: string;         // Agent ID
  timestamp: Date;
  
  decision: 'approved' | 'rejected' | 'needs-revision';
  feedback?: string;
  
  // 详细检查项
  checks?: {
    name: string;
    passed: boolean;
    details?: string;
  }[];
}
```

### 5.3 长任务管理

```typescript
interface LongTask extends Task {
  // 里程碑
  milestones: {
    id: string;
    name: string;
    status: 'pending' | 'in-progress' | 'completed' | 'failed';
    deadline: Date;
    completedAt?: Date;
  }[];
  
  // 汇报策略
  reportStrategy: {
    onMilestone: boolean;       // 里程碑完成
    onBlocker: boolean;         // 遇到阻塞
    periodicHours: number;      // 定期汇报
    onCompletion: boolean;      // 任务完成
  };
  
  // 资源预留
  resourceReservation: {
    llmQuota: number;           // Token 配额
    exclusiveTools: string[];   // 独占工具
    dedicatedAgents: string[];  // 专属 Agent
  };
  
  // 中断恢复
  interruptPolicy: {
    onInterruption: 'pause' | 'checkpoint' | 'continue';
    maxPauseTime: number;       // ms
    autoResume: boolean;
  };
}
```

---

## 六、改造路线图（三期，精修版）

### Phase 1: 最小闭环（2-3 周）

**目标**: 人说话 → 助理理解 → GM 任命 PM → PM 组队 → Writer 产出 → 助理通知

**要做的事**:

1. **注册四类固定 Node**
   ```typescript
   const nodes = [
     { id: 'assistant', role: 'assistant', tier: 'L1' },
     { id: 'gm', role: 'gm', tier: 'L3' },
     { id: 'platform-pm', role: 'platform-pm', tier: 'L2' },
     { id: 'writer', role: 'worker', tier: 'worker' },
   ];
   
   for (const node of nodes) {
     await openclaw.registerNode(node);
   }
   ```

2. **配置 Policy**
   ```typescript
   // GM 拥有管理权限
   await openclaw.setPolicy('gm', {
     connection: { canConnectTo: ['*'] },
     resources: { llm: ['*'], tools: ['*'], knowledge: ['*'], skills: ['*'] },
     limits: { maxConcurrentTasks: 10, maxTokensPerDay: 1000000, ... },
   });
   
   // Assistant 只有使用权限
   await openclaw.setPolicy('assistant', {
     connection: { canConnectTo: ['gm'] },
     resources: { llm: ['glm-5'], tools: [], knowledge: [], skills: ['interaction'] },
     limits: { maxConcurrentTasks: 1, ... },
   });
   ```

3. **实现消息路由**
   ```typescript
   // 基于 OpenClaw Tunnel
   async function routeMessage(message: AgentMessage): Promise<void> {
     const tunnel = await openclaw.getTunnel(message.from, message.to);
     await tunnel.send(message);
   }
   ```

4. **实现 Task 数据结构**

5. **跑通写书链路**

**不做的事**:
- ❌ 动态创建 Node
- ❌ 自动从 GitHub 拉 Skill
- ❌ 多 Worker 并发

### Phase 2: 动态团队与质量闭环（4-6 周）

**目标**: GM 能动态创建 Project PM Node，PM 能从 Registry 匹配 Worker，质量打回机制

**新增内容**:

1. **Node 动态注册 API**
   ```typescript
   async function createProjectPM(config: PMConfig): Promise<string> {
     const nodeId = generateId();
     
     await openclaw.registerNode({
       id: nodeId,
       role: 'project-pm',
       tier: 'L2',
       metadata: config,
     });
     
     await openclaw.setPolicy(nodeId, config.policy);
     await openclaw.bindResources(nodeId, config.resources);
     
     return nodeId;
   }
   ```

2. **Agent Registry 完整实现**
   ```typescript
   class AgentRegistry {
     private templates: Map<string, AgentTemplate>;
     
     async match(requirements: WorkerRequirements): Promise<AgentTemplate[]> {
       // 按能力、评分、可用性匹配
       return this.search({
         capabilities: requirements.skills,
         minRating: requirements.minRating,
         available: true,
       });
     }
     
     async instantiate(template: AgentTemplate): Promise<string> {
       const nodeId = await openclaw.registerNode({
         role: 'worker',
         tier: 'worker',
         metadata: template.config,
       });
       
       return nodeId;
     }
   }
   ```

3. **Hook 驱动的自动流转**
   ```typescript
   // PM 注册 Hook
   await openclaw.subscribe({
     eventType: 'task.completed',
     subscriber: pmId,
     action: 'trigger',
     callback: 'onWorkerCompleted',
   });
   ```

4. **质量打回闭环**
   ```typescript
   async function reviewAndDecide(taskResult: TaskResult): Promise<void> {
     const review = await pm.review(taskResult);
     
     if (review.decision === 'rejected') {
       // 打回重做
       await pm.requestRework(review.feedback);
       
       // 触发事件
       await openclaw.emit({
         type: 'quality.rejected',
         source: pm.id,
         payload: { taskId: taskResult.taskId, feedback: review.feedback },
       });
     }
   }
   ```

### Phase 3: 生态接入与自治进化（持续）

**目标**: Platform PM 自动从 GitHub 搜集能力，系统自我进化

**新增内容**:

1. **GitHub Adapter**
   ```typescript
   class GitHubAdapter {
     async searchSkills(query: string): Promise<Skill[]> {
       const repos = await github.search.code({
         q: `${query} skill agent`,
         language: 'typescript',
       });
       
       return repos.items.map(this.parseSkillRepo);
     }
     
     async importSkill(skillUrl: string): Promise<Skill> {
       const content = await github.repos.getContent({
         repo: skillUrl,
         path: 'skill.yaml',
       });
       
       const skill = this.parseSkillYaml(content);
       await platformPm.registerSkill(skill);
       
       return skill;
     }
   }
   ```

2. **自动质量评估**
   ```typescript
   async function evaluateSkill(skill: Skill): Promise<SkillRating> {
     // 运行测试
     const testResults = await runSkillTests(skill);
     
     // 评估性能
     const performance = await benchmarkSkill(skill);
     
     // 计算评分
     return {
       score: testResults.passRate * 0.6 + performance.score * 0.4,
       details: { testResults, performance },
     };
   }
   ```

3. **成功率统计**
   ```typescript
   interface AgentMetrics {
     agentId: string;
     
     // 统计
     totalTasks: number;
     completedTasks: number;
     failedTasks: number;
     avgCompletionTime: number;
     
     // 评分
     qualityScore: number;
     reliabilityScore: number;
     
     // 资源消耗
     totalTokensUsed: number;
     avgTokensPerTask: number;
   }
   ```

---

## 七、三个关键坑（精修版）

### 坑一：把 Gateway 当消息队列实现

**错误做法**:
```typescript
// ❌ 自己写消息中间件
class MessageQueue {
  private queue: Message[] = [];
  
  async send(message: Message): Promise<void> {
    this.queue.push(message);
  }
  
  async receive(): Promise<Message> {
    return this.queue.shift();
  }
}
```

**正确做法**:
```typescript
// ✅ 直接用 OpenClaw Tunnel
async function sendMessage(to: string, message: AgentMessage): Promise<void> {
  const tunnel = await openclaw.getTunnel(myId, to);
  await tunnel.send(message);
}

async function receiveMessage(): Promise<AgentMessage> {
  const tunnel = await openclaw.getActiveTunnel(myId);
  return tunnel.receive();
}
```

### 坑二：GM 持有太多业务逻辑

**错误做法**:
```typescript
// ❌ GM 理解业务细节
class GMAgent {
  async analyzeTask(task: Task): Promise<void> {
    // ❌ GM 不应该知道"第三章写什么"
    if (task.type === 'book') {
      const outline = await this.generateOutline(task);
      // ...
    }
  }
}
```

**正确做法**:
```typescript
// ✅ GM 只做三件事
class GMAgent {
  async handleTask(task: Task): Promise<void> {
    // 1. 判断任务可行性
    const feasibility = this.assessFeasibility(task);
    if (!feasibility.canDo) {
      await this.notifyAssistant({ status: 'rejected', reason: feasibility.reason });
      return;
    }
    
    // 2. 任命 PM 并授权
    const pm = await this.appointPM(feasibility.domain, task);
    await this.authorizeResources(pm, feasibility.requiredResources);
    
    // 3. 最终验收
    // (等待 PM 汇报后执行)
  }
  
  async reviewResult(result: TaskResult): Promise<void> {
    const decision = this.evaluateResult(result);
    if (decision.approved) {
      await this.notifyAssistant({ status: 'completed', result });
    } else {
      await this.requestRework(result.pmId, decision.feedback);
    }
  }
}
```

### 坑三：助理直接调用 Gateway

**错误做法**:
```typescript
// ❌ 助理直接查询 Gateway
class AssistantAgent {
  async checkProgress(taskId: string): Promise<void> {
    const status = await openclaw.getTaskStatus(taskId);  // ❌
    await this.notifyUser(status);
  }
}
```

**正确做法**:
```typescript
// ✅ 助理只和 GM 通信
class AssistantAgent {
  // 助理不知道任务状态，只接收 GM 推送
  private async onGMNotification(notification: GMNotification): Promise<void> {
    const userMessage = this.formatForUser(notification);
    await this.sendToUser(userMessage);
  }
  
  // 用户询问时，助理转发给 GM
  async handleUserQuery(query: string): Promise<void> {
    await this.sendToGM({
      type: 'user.query',
      payload: { query },
    });
  }
}
```

---

## 八、接口速查表

### 8.1 GM Agent 必备接口

```typescript
interface GMAgentAPI {
  // 任务处理
  handleTask(task: Task): Promise<void>;
  
  // PM 管理
  appointPM(domain: string, task: Task): Promise<string>;
  dismissPM(pmId: string): Promise<void>;
  
  // 资源授权
  authorizeResources(agentId: string, resources: ResourceGrant): Promise<void>;
  
  // 验收
  reviewResult(result: TaskResult): Promise<ReviewDecision>;
  
  // 通知助理
  notifyAssistant(notification: Notification): Promise<void>;
}
```

### 8.2 PM Agent 必备接口

```typescript
interface PMAgentAPI {
  // 团队管理
  buildTeam(requirements: TeamRequirements): Promise<Team>;
  
  // 任务管理
  planTask(task: Task): Promise<TaskPlan>;
  assignWork(team: Team, plan: TaskPlan): Promise<void>;
  
  // 进度管理
  getProgress(): Promise<ProjectProgress>;
  reportToGM(): Promise<ProjectReport>;
  
  // 质量管理
  reviewWork(work: Work): Promise<ReviewResult>;
  requestRework(agentId: string, feedback: string): Promise<void>;
}
```

### 8.3 Assistant Agent 必备接口

```typescript
interface AssistantAgentAPI {
  // 用户交互
  receiveUserInput(input: UserInput): Promise<void>;
  sendUserResponse(response: Response): Promise<void>;
  
  // GM 通信
  sendToGM(message: AssistantMessage): Promise<void>;
  onGMNotification(notification: GMNotification): Promise<void>;
  
  // 主动汇报（由 GM 触发）
  reportProgress(progress: Progress): Promise<void>;
  reportCompletion(result: Result): Promise<void>;
  reportBlocker(blocker: Blocker): Promise<void>;
}
```

### 8.4 Worker Agent 必备接口

```typescript
interface WorkerAgentAPI {
  // 任务执行
  execute(task: Task): Promise<TaskResult>;
  
  // PM 通信
  reportProgress(progress: number, message: string): Promise<void>;
  reportError(error: Error): Promise<void>;
  
  // 协作
  requestCollaboration(peer: string, request: CollabRequest): Promise<void>;
  respondToCollaboration(request: CollabRequest, response: CollabResponse): Promise<void>;
}
```

---

## 九、配置文件模板

### 9.1 Agent 配置

```yaml
# config/agents.yaml

gm:
  id: gm-main
  role: gm
  tier: L3
  
  llm:
    model: claude-opus-4-6-thinking
    quota:
      maxTokensPerRequest: 100000
      maxTokensPerDay: 10000000
      
  permissions:
    canConnectTo: ['*']
    canCreateAgents: true
    canDestroyAgents: true
    canAuthorizeResources: true
    
assistant:
  id: assistant-main
  role: assistant
  tier: L1
  
  llm:
    model: glm-5
    quota:
      maxTokensPerRequest: 8000
      
  permissions:
    canConnectTo: ['gm-main']
    
  reportStrategy:
    onMilestone: true
    onBlocker: true
    periodicHours: 2
    onCompletion: true

platform_pm:
  id: platform-pm
  role: platform-pm
  tier: L2
  permanent: true
  
  llm:
    model: claude-sonnet-4-5
    
  permissions:
    canCreateAgents: true
    canAccessRegistry: true
    canImportFromGitHub: true
    
# Worker 模板（由 Platform PM 管理）
worker_templates:
  writer:
    role: worker
    tier: worker
    llm: claude-sonnet-4-5
    skills: [writing, editing, formatting]
    
  coder:
    role: worker
    tier: worker
    llm: gpt-5.3-codex
    skills: [coding, testing, debugging]
    tools: [shell, file, browser]
```

### 9.2 Policy 配置

```yaml
# config/policies.yaml

gm_policy:
  agentId: gm-main
  connection:
    canConnectTo: ['*']
  resources:
    llm: ['*']
    tools: ['*']
    knowledge: ['*']
    skills: ['*']
  limits:
    maxConcurrentTasks: 10
    maxTokensPerDay: 10000000

assistant_policy:
  agentId: assistant-main
  connection:
    canConnectTo: ['gm-main']
  resources:
    llm: ['glm-5']
    tools: []
    knowledge: []
    skills: ['interaction']
  limits:
    maxConcurrentTasks: 1

worker_policy_template:
  connection:
    canConnectTo: ['${pm_id}']  # 动态填充
  resources:
    llm: ['${assigned_llm}']
    tools: ['${allowed_tools}']
    knowledge: ['${accessible_knowledge}']
    skills: ['${assigned_skills}']
  limits:
    maxConcurrentTasks: 1
    maxTokensPerDay: 500000
```

---

## 十、总结

### 10.1 核心原则

1. **Gateway 不是你写的** - 直接用 OpenClay 原生能力
2. **概念映射而非重造** - Node → Agent, Tunnel → 通信, Policy → 权限
3. **分层不变，实现映射** - GM/PM/Worker 架构不变，底层用 OpenClaw

### 10.2 关键洞察

- GM 唯一持有 Gateway 管理权限
- Assistant 只和 GM 通信，不碰底层
- PM 负责 Agent 生命周期管理
- Worker 只执行，不决策

### 10.3 实施路径

```
Phase 1 (2-3周): 最小闭环
  ↓
Phase 2 (4-6周): 动态团队 + 质量闭环
  ↓
Phase 3 (持续): 生态接入 + 自治进化
```

---

*文档版本: v1.1*
*创建时间: 2026-02-23*
*状态: 已优化*
