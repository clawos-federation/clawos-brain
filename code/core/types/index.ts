/**
 * ClawOS Core Types
 * 
 * 基于 OpenClaw 的 Agent 八件套定义
 */

// ============================================
// Agent 角色与层级
// ============================================

export type AgentRole = 
  | 'gm'           // 总经理 - 唯一管理权限
  | 'assistant'    // 助理 - 唯一人机入口
  | 'platform-pm'  // 平台 PM - 永久存在，造 Agent
  | 'project-pm'   // 项目 PM - 临时创建，带队执行
  | 'worker';      // 执行层 - 专业执行

export type AgentTier = 'L1' | 'L2' | 'L3' | 'worker';

export type AgentStatus = 'idle' | 'busy' | 'error' | 'offline';

// ============================================
// Agent 八件套
// ============================================

/**
 * Agent 八件套配置
 * 存储在 OpenClaw Node.metadata 中
 */
export interface AgentConfig {
  // ① 身份角色
  id: string;
  name: string;
  role: AgentRole;
  tier: AgentTier;
  teamId?: string;
  parentPm?: string;
  
  // ② 绑定 LLM（大脑）
  llm: LLMConfig;
  
  // ③ 工具集
  tools: ToolRef[];
  
  // ④ 技能集
  skills: SkillRef[];
  
  // ⑤ 知识库
  knowledge: KnowledgeRef[];
  
  // ⑥ 记忆
  memory: MemoryConfig;
  
  // ⑦ 触发器/Hooks
  hooks: Hook[];
  
  // ⑧ 权限边界
  permissions: Permission[];
  
  // 元数据
  version: string;
  createdAt: Date;
  createdBy: string;
}

// ============================================
// ② LLM 配置
// ============================================

export interface LLMConfig {
  model: string;              // claude-opus-4-6-thinking | gpt-5.3-codex | glm-5 | ...
  endpoint?: string;          // 自定义端点
  
  // 配额
  quota: {
    maxTokensPerRequest: number;
    maxTokensPerDay: number;
    maxRequestsPerMinute: number;
  };
  
  // 策略
  fallback?: string;          // 降级模型
  temperature?: number;
  retryPolicy?: {
    maxRetries: number;
    backoffMs: number;
  };
}

// ============================================
// ③ 工具集
// ============================================

export type ToolType = 'shell' | 'browser' | 'file' | 'http' | 'database' | 'custom';

export interface ToolRef {
  id: string;
  name: string;
  type: ToolType;
  
  // 权限配置
  permissions?: {
    sandboxLevel: 'none' | 'restricted' | 'isolated';
    allowedPaths?: string[];
    deniedPaths?: string[];
    networkAccess?: boolean;
  };
  
  // 限流
  rateLimit?: {
    callsPerMinute: number;
  };
}

// ============================================
// ④ 技能集
// ============================================

export interface SkillRef {
  id: string;
  name: string;
  version: string;
  
  // 来源
  source: 'builtin' | 'clawhub' | 'github' | 'custom';
  
  // 分类
  category: string;
  tags: string[];
}

export interface Skill extends SkillRef {
  // 核心
  promptTemplate: string;
  dependencies: string[];
  requiredTools: string[];
  
  // 执行
  execute: (context: SkillContext) => Promise<any>;
  
  // 元数据
  rating: number;
  author: string;
  downloads: number;
}

export interface SkillContext {
  agent: AgentConfig;
  task: Task;
  input: any;
  knowledge?: any[];
  memory?: any[];
}

// ============================================
// ⑤ 知识库
// ============================================

export type KnowledgeType = 'vector' | 'document' | 'structured';

export interface KnowledgeRef {
  id: string;
  name: string;
  type: KnowledgeType;
  
  // 访问权限
  access: 'read' | 'write' | 'admin';
  
  // 命名空间隔离
  namespace?: string;
  prefix?: string;
}

// ============================================
// ⑥ 记忆
// ============================================

export interface MemoryConfig {
  // 短时记忆
  shortTerm: {
    maxContextSize: number;       // token 数
    strategy: 'fifo' | 'priority' | 'semantic';
  };
  
  // 长时记忆
  longTerm: {
    enabled: boolean;
    knowledgeNodeId?: string;
    namespace: string;
    
    // 记忆类型
    types: ('episodic' | 'semantic' | 'procedural')[];
  };
  
  // 跨任务持久化
  persistence: {
    enabled: boolean;
    autoSave: boolean;
    selectiveMemories: boolean;
  };
}

// ============================================
// ⑦ 触发器/Hooks
// ============================================

export type EventType = 
  // 任务事件
  | 'task.created'
  | 'task.started'
  | 'task.progress'
  | 'task.completed'
  | 'task.failed'
  // Agent 事件
  | 'node.started'
  | 'node.stopped'
  | 'node.failed'
  // 质量事件
  | 'quality.rejected'
  | 'quality.approved'
  // 资源事件
  | 'resource.exhausted'
  | 'resource.available';

export type HookAction = 'notify' | 'trigger' | 'callback';

export interface Hook {
  id: string;
  eventType: EventType;
  action: HookAction;
  
  // 过滤条件
  filter?: {
    field: string;
    operator: 'eq' | 'ne' | 'gt' | 'lt' | 'contains';
    value: any;
  };
  
  // 回调
  callback?: string;          // 函数名或 URL
  
  // 限流
  throttle?: {
    maxTriggers: number;
    perMinutes: number;
  };
}

// ============================================
// ⑧ 权限边界
// ============================================

export interface Permission {
  // 连接权限
  connection: {
    canConnectTo: string[];       // Agent ID 列表，['*'] 表示全部
    cannotConnectTo?: string[];
  };
  
  // 资源权限
  resources: {
    llm: string[];                // 可用的 LLM
    tools: string[];              // 可用的工具
    knowledge: string[];          // 可访问的知识库
    skills: string[];             // 可使用的技能
  };
  
  // 配额限制
  limits: {
    maxConcurrentTasks: number;
    maxTokensPerDay: number;
    maxExecutionTimeMs: number;
    maxMemoryMB: number;
  };
}

// ============================================
// Task 相关
// ============================================

export type TaskType = 
  | 'coding' 
  | 'writing' 
  | 'research' 
  | 'review'
  | 'deployment'
  | 'analysis';

export type TaskStatus = 
  | 'created'
  | 'assigned'
  | 'planned'
  | 'running'
  | 'reviewing'
  | 'approved'
  | 'rejected'
  | 'completed';

export type TaskPriority = 'low' | 'normal' | 'high' | 'critical';

export interface Task {
  id: string;
  type: TaskType;
  description: string;
  priority: TaskPriority;
  status: TaskStatus;
  
  // 层级
  parentTaskId?: string;
  subtaskIds: string[];
  
  // 分配
  assignee?: string;
  teamId?: string;
  
  // 执行
  plan?: TaskPlan;
  progress?: TaskProgress;
  result?: TaskResult;
  
  // 检查点
  checkpoints: Checkpoint[];
  
  // 审核
  reviews: Review[];
  
  // 时间
  createdAt: Date;
  startedAt?: Date;
  completedAt?: Date;
  deadline?: Date;
  
  // 元数据
  createdBy: string;
  tags: string[];
}

export interface TaskPlan {
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

export interface TaskProgress {
  percent: number;           // 0-100
  currentStep: string;
  completedSteps: string[];
  blocked?: {
    reason: string;
    since: Date;
  };
}

export interface TaskResult {
  taskId: string;
  status: 'success' | 'partial' | 'failed';
  output: any;
  artifacts: {
    type: string;
    path: string;
    checksum: string;
  }[];
  metrics: {
    tokensUsed: number;
    executionTimeMs: number;
    retryCount: number;
  };
}

export interface Checkpoint {
  id: string;
  taskId: string;
  timestamp: Date;
  status: TaskStatus;
  progress: TaskProgress;
  artifacts: {
    type: string;
    path: string;
    checksum: string;
  }[];
  recoveryInfo: {
    resumeFrom: string;
    requiredState: any;
  };
}

export interface Review {
  id: string;
  reviewer: string;
  timestamp: Date;
  decision: 'approved' | 'rejected' | 'needs-revision';
  feedback?: string;
  checks?: {
    name: string;
    passed: boolean;
    details?: string;
  }[];
}

// ============================================
// 通信协议
// ============================================

export type MessageType = 
  // 任务
  | 'task.assign'
  | 'task.progress'
  | 'task.result'
  | 'task.error'
  // 协作
  | 'collab.request'
  | 'collab.response'
  | 'collab.sync'
  // 管理
  | 'mgmt.create'
  | 'mgmt.destroy'
  | 'mgmt.authorize'
  // 通知
  | 'notify.info'
  | 'notify.warning'
  | 'notify.critical';

export interface AgentMessage {
  id: string;
  from: string;
  to: string | 'broadcast' | 'team';
  teamId?: string;
  
  type: MessageType;
  payload: any;
  
  priority: 'low' | 'normal' | 'high' | 'critical';
  requiresAck: boolean;
  timeout?: number;
  
  timestamp: Date;
  hops: string[];
}

// ============================================
// 团队
// ============================================

export interface Team {
  id: string;
  name: string;
  pmId: string;              // Project PM ID
  members: {
    agentId: string;
    role: string;
    tasks: string[];
  }[];
  
  // 会议
  activeMeeting?: Meeting;
}

export interface Meeting {
  id: string;
  teamId: string;
  host: string;
  participants: string[];
  
  status: 'pending' | 'active' | 'ended';
  topic: string;
  
  messages: AgentMessage[];
  decisions: {
    description: string;
    decidedBy: string;
    timestamp: Date;
  }[];
  actionItems: {
    agentId: string;
    task: string;
    deadline: Date;
  }[];
  
  startTime?: Date;
  endTime?: Date;
}

// ============================================
// OpenClaw Adapter Interface
// ============================================

/**
 * OpenClaw 适配器接口
 * 用于与 OpenClaw 底层系统交互
 */
export interface OpenClawAdapter {
  // Node 管理
  registerNode(options: { id: string; metadata: AgentConfig }): Promise<string>;
  unregisterNode(nodeId: string): Promise<void>;

  // Tunnel 通信
  sendViaTunnel(from: string, to: string, message: AgentMessage): Promise<void>;
}

// ============================================
// 意图解析相关类型
// ============================================

export type IntentType = 'task' | 'query' | 'feedback' | 'greeting' | 'unknown';

export interface ParsedIntent {
  type: IntentType;
  payload?: {
    description?: string;
    query?: string;
    feedback?: string;
  };
}

// ============================================
// 进度汇报相关类型
// ============================================

export interface ProgressInfo {
  taskId: string;
  percentComplete: number;
  currentStep: string;
  estimatedTimeRemaining?: number;
}

export interface CompletionResult {
  taskId: string;
  summary: string;
  artifacts: string[];
}

export interface BlockerInfo {
  taskId: string;
  reason: string;
  suggestedActions?: string[];
}

// ============================================
// Agent Registry
// ============================================

export interface AgentTemplate {
  id: string;
  name: string;
  category: string;
  description: string;
  
  // 八件套配置模板
  configTemplate: Partial<AgentConfig>;
  
  // 元数据
  version: string;
  author: string;
  rating: number;
  downloads: number;
  tags: string[];
  
  createdAt: Date;
  updatedAt: Date;
}

export interface AgentInstance {
  id: string;
  templateId?: string;
  config: AgentConfig;
  status: AgentStatus;
  
  // 运行时
  currentNodeId?: string;    // OpenClaw Node ID
  activeTaskId?: string;
  
  // 统计
  metrics: {
    totalTasks: number;
    completedTasks: number;
    failedTasks: number;
    avgCompletionTime: number;
    totalTokensUsed: number;
  };
  
  createdAt: Date;
  lastActiveAt: Date;
}
