# 🔧 ClawOS 技术实现规范

> 本文档定义 ClawOS 的技术细节，可直接用于开发

---

## 一、目录结构

```
clawos/
├── core/                          # 通用内核
│   ├── gateway/                   # Gateway API 服务
│   │   ├── index.ts              # 入口
│   │   ├── router.ts             # API 路由
│   │   ├── scheduler.ts          # 任务调度器
│   │   └── permissions.ts        # 权限管理
│   │
│   ├── registry/                  # Agent Registry
│   │   ├── index.ts              # 注册表入口
│   │   ├── templates.ts          # 模板管理
│   │   ├── instances.ts          # 实例管理
│   │   └── categories.ts         # 分类索引
│   │
│   ├── agents/                    # 核心 Agents
│   │   ├── gm/                   # GM Agent
│   │   │   ├── index.ts
│   │   │   ├── decision.ts       # 决策逻辑
│   │   │   └── router.ts         # 任务路由
│   │   │
│   │   ├── assistant/            # Assistant Agent
│   │   │   ├── index.ts
│   │   │   ├── interaction.ts    # 交互逻辑
│   │   │   └── reporter.ts       # 主动汇报
│   │   │
│   │   └── platform-pm/          # Platform PM
│   │       ├── index.ts
│   │       ├── builder.ts        # Agent 构建器
│   │       └── importer.ts       # GitHub 导入
│   │
│   ├── communication/             # 通信层
│   │   ├── bus.ts                # 消息总线
│   │   ├── protocol.ts           # 通信协议
│   │   └── groups.ts             # 群组/会议
│   │
│   └── knowledge/                 # 知识库
│       ├── store.ts              # 存储层
│       ├── retrieval.ts          # 检索层
│       └── embedding.ts          # 向量化
│
├── ecosystems/                    # 垂直生态
│   └── coding/                    # Coding 领域
│       ├── pm/                    # Dev PM
│       │   ├── index.ts
│       │   ├── planner.ts        # 任务规划
│       │   ├── coordinator.ts    # 团队协调
│       │   └── reviewer.ts       # 质量把关
│       │
│       ├── agents/                # 执行 Agents
│       │   ├── product/          # 产品 Agent
│       │   ├── architect/        # 架构 Agent
│       │   ├── frontend/         # 前端 Agent
│       │   ├── backend/          # 后端 Agent
│       │   ├── test/             # 测试 Agent
│       │   ├── review/           # 代码审查 Agent
│       │   ├── devops/           # 运维 Agent
│       │   └── github/           # GitHub Agent
│       │
│       ├── skills/                # 专用 Skills
│       │   ├── languages/        # 语言技能
│       │   ├── frameworks/       # 框架技能
│       │   ├── tools/            # 工具技能
│       │   └── analysis/         # 分析技能
│       │
│       └── knowledge/             # 领域知识库
│           ├── patterns/         # 设计模式
│           ├── practices/        # 最佳实践
│           ├── security/         # 安全规范
│           └── project/          # 项目特定
│
├── integrations/                  # 集成层
│   ├── openclaw/                  # OpenClaw 适配
│   │   ├── adapter.ts            # 适配器
│   │   ├── node.ts               # Node 调用
│   │   └── skills.ts             # Skills 桥接
│   │
│   └── github/                    # GitHub 集成
│       ├── client.ts             # API 客户端
│       ├── sync.ts               # 双向同步
│       └── events.ts             # 事件处理
│
├── docs/                          # 文档
│   ├── architecture.md
│   ├── api.md
│   └── deployment.md
│
├── tests/                         # 测试
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── config/                        # 配置
│   ├── agents.yaml               # Agent 配置
│   ├── models.yaml               # 模型配置
│   └── permissions.yaml          # 权限配置
│
└── package.json
```

---

## 二、核心接口定义

### 2.1 Agent 基础接口

```typescript
// core/types/agent.ts

interface Agent {
  id: string;
  type: AgentType;
  status: 'idle' | 'busy' | 'error';
  
  // 核心能力
  execute(task: Task): Promise<Result>;
  
  // 通信
  send(to: AgentID, message: Message): void;
  receive(message: Message): void;
  
  // 生命周期
  initialize(): Promise<void>;
  shutdown(): Promise<void>;
}

interface AgentConfig {
  // 八件套
  llm: LLMConfig;
  skills: SkillRef[];
  tools: ToolRef[];
  knowledge: KnowledgeRef[];
  memory: MemoryConfig;
  hooks: Hook[];
  permissions: Permission[];
  
  // 元数据
  name: string;
  description: string;
  version: string;
}

type AgentType = 
  | 'gm'           // 总经理
  | 'assistant'    // 助理
  | 'platform-pm'  // 平台 PM
  | 'project-pm'   // 项目 PM
  | 'worker';      // 执行层
```

### 2.2 GM Agent 接口

```typescript
// core/agents/gm/index.ts

interface GMAgent extends Agent {
  // 决策
  analyzeTask(task: Task): TaskAnalysis;
  routeTask(task: Task): PMType;
  
  // PM 管理
  appointPM(type: PMType, config: PMConfig): Promise<PMAgent>;
  dismissPM(pmId: AgentID): void;
  
  // 资源授权
  authorizeResources(pm: PMAgent, resources: ResourceGrant): void;
  
  // 验收
  reviewResult(result: TaskResult): ReviewDecision;
}

interface TaskAnalysis {
  type: 'coding' | 'legal' | 'video' | 'finance' | 'unknown';
  complexity: 'low' | 'medium' | 'high' | 'critical';
  estimatedTime: number;  // 小时
  requiredSkills: string[];
  requiredResources: Resource[];
}

interface ReviewDecision {
  approved: boolean;
  feedback?: string;
  requireRework?: string[];
}
```

### 2.3 PM Agent 接口

```typescript
// core/agents/pm/index.ts

interface PMAgent extends Agent {
  // 团队管理
  buildTeam(requirements: TeamRequirements): Promise<Team>;
  assignTasks(team: Team, tasks: Task[]): void;
  
  // 进度管理
  getProgress(): ProjectProgress;
  reportToGM(): ProjectReport;
  
  // 质量管理
  reviewWork(agent: AgentID, work: Work): ReviewResult;
  requestRework(agent: AgentID, feedback: string): void;
}

interface Team {
  id: string;
  members: {
    agent: Agent;
    role: string;
    tasks: Task[];
  }[];
  
  // 会议
  holdMeeting(topic: string, participants: AgentID[]): MeetingResult;
}

interface ProjectProgress {
  total: number;
  completed: number;
  blocked: Task[];
  percentComplete: number;
}
```

### 2.4 Assistant Agent 接口

```typescript
// core/agents/assistant/index.ts

interface AssistantAgent extends Agent {
  // 人机交互
  receiveUserInput(input: UserInput): void;
  sendUserResponse(response: Response): void;
  
  // 主动汇报
  reportProgress(progress: Progress): void;
  reportCompletion(result: Result): void;
  reportBlocker(blocker: Blocker): void;
  
  // 情绪与体验
  adjustTone(context: Context): void;
  generateFriendlyMessage(content: string): string;
}

interface ReportStrategy {
  onMilestone: boolean;      // 里程碑完成
  onBlocker: boolean;        // 遇到阻塞
  periodicHours: number;     // 定期汇报
  onCompletion: boolean;     // 任务完成
}
```

### 2.5 Agent Registry 接口

```typescript
// core/registry/index.ts

interface AgentRegistry {
  // 模板管理
  registerTemplate(template: AgentTemplate): void;
  getTemplate(id: string): AgentTemplate;
  listTemplates(filter?: TemplateFilter): AgentTemplate[];
  
  // 实例管理
  createInstance(templateId: string, config?: Partial<AgentConfig>): Agent;
  getInstance(id: string): Agent;
  destroyInstance(id: string): void;
  
  // 分类
  getByCategory(category: string): AgentTemplate[];
  search(query: string): AgentTemplate[];
  
  // 导入导出
  importFromGitHub(repo: string): Promise<AgentTemplate[]>;
  exportToGitHub(template: AgentTemplate): Promise<void>;
}

interface AgentTemplate {
  id: string;
  name: string;
  category: string;
  description: string;
  
  // 八件套配置
  config: AgentConfig;
  
  // 元数据
  version: string;
  author: string;
  rating: number;
  downloads: number;
  tags: string[];
}
```

### 2.6 通信协议

```typescript
// core/communication/protocol.ts

interface Message {
  id: string;
  from: AgentID;
  to: AgentID | 'broadcast';
  type: MessageType;
  payload: any;
  timestamp: Date;
  priority: 'low' | 'normal' | 'high' | 'critical';
}

type MessageType = 
  | 'task'           // 任务分配
  | 'result'         // 结果返回
  | 'query'          // 查询请求
  | 'response'       // 查询响应
  | 'notification'   // 通知
  | 'error'          // 错误
  | 'heartbeat';     // 心跳

// 群组通信
interface AgentGroup {
  id: string;
  name: string;
  members: AgentID[];
  topic: string;
  
  // 操作
  broadcast(message: Message): void;
  getHistory(): Message[];
}

// 会议机制
interface Meeting {
  id: string;
  topic: string;
  host: AgentID;  // PM
  participants: AgentID[];
  agenda: string[];
  minutes?: MeetingMinutes;
}

interface MeetingMinutes {
  decisions: string[];
  actionItems: {
    agent: AgentID;
    task: string;
    deadline: Date;
  }[];
  nextMeeting?: Date;
}
```

---

## 三、Coding 领域实现

### 3.1 Dev PM 实现

```typescript
// ecosystems/coding/pm/index.ts

class DevPMAgent implements PMAgent {
  private team: Team;
  private project: Project;
  
  async buildTeam(requirements: TeamRequirements): Promise<Team> {
    const team: Team = { id: generateId(), members: [] };
    
    // 根据项目类型选择成员
    if (requirements.needsFrontend) {
      const frontend = await registry.createInstance('frontend-agent');
      team.members.push({ agent: frontend, role: 'frontend', tasks: [] });
    }
    
    if (requirements.needsBackend) {
      const backend = await registry.createInstance('backend-agent');
      team.members.push({ agent: backend, role: 'backend', tasks: [] });
    }
    
    // ... 其他成员
    
    return team;
  }
  
  async executeProject(project: Project): Promise<ProjectResult> {
    // 1. 产品需求分析
    const requirements = await this.getProductRequirements(project);
    
    // 2. 架构设计
    const architecture = await this.designArchitecture(requirements);
    
    // 3. 任务拆分
    const tasks = this.splitTasks(architecture);
    
    // 4. 分配任务
    this.assignTasks(this.team, tasks);
    
    // 5. 并行开发
    const results = await this.runParallel(tasks);
    
    // 6. 代码审查
    const reviewResult = await this.reviewCode(results);
    
    // 7. 测试验证
    const testResult = await this.runTests(results);
    
    // 8. 提交 GitHub
    await this.submitToGitHub(results);
    
    return { requirements, architecture, code: results, review: reviewResult, tests: testResult };
  }
  
  async reportToGM(): Promise<ProjectReport> {
    return {
      projectId: this.project.id,
      progress: this.getProgress(),
      blockers: this.getBlockers(),
      estimatedCompletion: this.getETA(),
      risks: this.getRisks(),
    };
  }
}
```

### 3.2 执行 Agents 实现

```typescript
// ecosystems/coding/agents/backend/index.ts

class BackendAgent implements Agent {
  private llm: LLMClient;
  private skills: Skill[];
  
  async execute(task: Task): Promise<Result> {
    switch (task.type) {
      case 'api-design':
        return this.designAPI(task);
      case 'api-impl':
        return this.implementAPI(task);
      case 'database':
        return this.designDatabase(task);
      case 'business-logic':
        return this.implementLogic(task);
      default:
        throw new Error(`Unknown task type: ${task.type}`);
    }
  }
  
  private async implementAPI(task: Task): Promise<Result> {
    // 1. 理解需求
    const spec = await this.llm.analyze(task.description);
    
    // 2. 生成代码
    const code = await this.llm.generate(`
      你是后端开发专家。
      根据以下规格实现 API：
      ${JSON.stringify(spec)}
      
      要求：
      - RESTful 设计
      - 完整的错误处理
      - 输入验证
      - 单元测试
    `);
    
    // 3. 代码检查
    const review = await this.reviewCode(code);
    
    return { code, review, tests: await this.generateTests(code) };
  }
}
```

### 3.3 GitHub Agent 实现

```typescript
// ecosystems/coding/agents/github/index.ts

class GitHubAgent implements Agent {
  private client: GitHubClient;
  
  async execute(task: Task): Promise<Result> {
    switch (task.type) {
      case 'create-repo':
        return this.createRepo(task);
      case 'create-pr':
        return this.createPR(task);
      case 'merge-pr':
        return this.mergePR(task);
      case 'create-release':
        return this.createRelease(task);
      case 'handle-issue':
        return this.handleIssue(task);
      default:
        throw new Error(`Unknown task type: ${task.type}`);
    }
  }
  
  async createPR(task: Task): Promise<Result> {
    const { repo, branch, changes, title, description } = task.payload;
    
    // 1. 创建分支
    await this.client.createBranch(repo, branch);
    
    // 2. 提交更改
    for (const change of changes) {
      await this.client.createOrUpdateFile(
        repo,
        branch,
        change.path,
        change.content,
        change.message
      );
    }
    
    // 3. 创建 PR
    const pr = await this.client.createPullRequest(repo, {
      title,
      head: branch,
      base: 'main',
      body: description,
    });
    
    // 4. 触发 CI
    await this.client.triggerWorkflow(repo, 'ci.yml', { ref: branch });
    
    return { prUrl: pr.html_url, prNumber: pr.number };
  }
}
```

---

## 四、配置文件

### 4.1 Agent 配置

```yaml
# config/agents.yaml

gm:
  model: claude-opus-4-6-thinking
  maxConcurrentPMs: 5
  decisionTimeout: 60s
  
assistant:
  model: glm-5
  reportStrategy:
    onMilestone: true
    onBlocker: true
    periodicHours: 2
    onCompletion: true
  tone: friendly_professional

platform_pm:
  model: claude-sonnet-4-5
  autoImportFromGitHub: true
  syncInterval: 24h

dev_pm:
  model: claude-sonnet-4-5
  teamSize:
    min: 3
    max: 10
  qualityGates:
    - codeReview
    - testPass
    - securityScan

agents:
  frontend:
    model: gpt-5.3-codex
    skills:
      - react-dev
      - typescript-expert
      - testing-frameworks
    knowledge:
      - clean-code
      - solid-principles
      
  backend:
    model: gpt-5.3-codex
    skills:
      - python-expert
      - fastapi-dev
      - database-design
    knowledge:
      - api-design-patterns
      - security-best-practices
      
  test:
    model: gemini-3-flash
    skills:
      - pytest
      - jest
      - e2e-testing
    coverageThreshold: 80%
    
  github:
    model: claude-sonnet-4-5
    permissions:
      - repo:read
      - repo:write
      - workflow:trigger
```

### 4.2 权限配置

```yaml
# config/permissions.yaml

roles:
  gm:
    can:
      - create_pm
      - destroy_pm
      - authorize_resources
      - access_all_gateways
      - final_approval
      
  platform_pm:
    can:
      - create_agent
      - destroy_agent
      - import_from_github
      - access_registry
      
  project_pm:
    can:
      - build_team
      - assign_tasks
      - review_work
      - access_gateway
      
  worker:
    can:
      - execute_task
      - access_assigned_tools
      - report_result
    cannot:
      - create_agent
      - access_registry
      
  assistant:
    can:
      - receive_user_input
      - send_user_response
      - report_progress
    cannot:
      - execute_technical_task
      - access_gateway
```

---

## 五、测试用例

### 5.1 端到端测试：URL 缩短服务

```typescript
// tests/e2e/url-shortener.test.ts

describe('URL Shortener Development', () => {
  it('should develop a URL shortener from natural language', async () => {
    // 1. 用户输入
    const userRequest = '帮我开发一个 URL 缩短服务，包含 API 和简单的前端页面';
    
    // 2. Assistant 接收
    const assistant = new AssistantAgent();
    await assistant.receiveUserInput({ text: userRequest });
    
    // 3. GM 路由到 Dev PM
    const gm = new GMAgent();
    const analysis = gm.analyzeTask({ description: userRequest });
    expect(analysis.type).toBe('coding');
    
    // 4. Dev PM 组建团队
    const devPM = await gm.appointPM('dev', { project: 'url-shortener' });
    const team = await devPM.buildTeam({
      needsFrontend: true,
      needsBackend: true,
      needsTest: true,
    });
    expect(team.members.length).toBeGreaterThanOrEqual(3);
    
    // 5. 执行开发
    const result = await devPM.executeProject({
      name: 'url-shortener',
      requirements: userRequest,
    });
    
    // 6. 验证结果
    expect(result.code).toBeDefined();
    expect(result.tests.passed).toBe(true);
    expect(result.review.approved).toBe(true);
    
    // 7. 验证 GitHub 提交
    expect(result.github.prUrl).toBeDefined();
    expect(result.github.prNumber).toBeGreaterThan(0);
    
    // 8. Assistant 通知用户
    const notification = await assistant.getLastNotification();
    expect(notification.status).toBe('completed');
    expect(notification.message).toContain('GitHub');
  });
});
```

---

## 六、与 OpenClaw 的集成

### 6.1 适配器实现

```typescript
// integrations/openclaw/adapter.ts

class OpenClawAdapter {
  private openclaw: OpenClawClient;
  
  // 复用 sessions_spawn
  async spawnAgent(config: AgentConfig): Promise<Agent> {
    const session = await this.openclaw.sessions.spawn({
      agentId: config.llm.model,
      task: '',
      mode: 'session',
    });
    
    return new OpenClawAgentWrapper(session, config);
  }
  
  // 复用 Node 通信
  async callNode(nodeId: string, command: string): Promise<Result> {
    return this.openclaw.nodes.invoke({
      node: nodeId,
      invokeCommand: command,
    });
  }
  
  // 复用 Skills
  async callSkill(skillId: string, params: any): Promise<Result> {
    // 调用 OpenClaw 的 skill 系统
    return this.openclaw.skills.execute(skillId, params);
  }
}
```

### 6.2 依赖声明

```json
// package.json
{
  "name": "clawos",
  "version": "1.0.0",
  "dependencies": {
    "openclaw": ">=2026.2.19",
    "@octokit/rest": "^20.0.0",
    "pg": "^8.11.0",
    "clickhouse-client": "^0.2.0"
  }
}
```

---

## 七、部署方案

### 7.1 开发环境

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  clawos:
    build: .
    volumes:
      - .:/app
    environment:
      - NODE_ENV=development
      - OPENCLAW_URL=ws://openclaw:18789
    depends_on:
      - postgres
      - openclaw
      
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: clawos
      
  openclaw:
    image: openclaw/openclaw:latest
    ports:
      - "18789:18789"
```

### 7.2 生产环境

```yaml
# kubernetes/clawos.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: clawos
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: clawos
        image: clawos/clawos:1.0.0
        env:
        - name: OPENCLAW_URL
          valueFrom:
            secretKeyRef:
              name: clawos-secrets
              key: openclaw-url
```

---

*文档版本: v1.0*
*创建时间: 2026-02-23*
