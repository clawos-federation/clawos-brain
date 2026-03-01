/**
 * Agent Registry
 * 
 * Agent 模板库和实例管理
 * 底层使用 OpenClaw Node Registry
 */

import { v4 as uuidv4 } from 'uuid';
import {
  AgentTemplate,
  AgentInstance,
  AgentConfig,
  AgentStatus,
  OpenClawAdapter,
} from '../types';

export interface RegistryFilter {
  category?: string;
  tags?: string[];
  minRating?: number;
  role?: string;
}

export class AgentRegistry {
  private templates: Map<string, AgentTemplate> = new Map();
  private instances: Map<string, AgentInstance> = new Map();
  private openclawAdapter: OpenClawAdapter;

  constructor(openclawAdapter: OpenClawAdapter) {
    this.openclawAdapter = openclawAdapter;
  }

  // ============================================
  // 模板管理
  // ============================================

  /**
   * 注册 Agent 模板
   */
  async registerTemplate(template: Omit<AgentTemplate, 'id' | 'createdAt' | 'updatedAt'>): Promise<string> {
    const id = `template-${uuidv4()}`;
    const now = new Date();

    const fullTemplate: AgentTemplate = {
      ...template,
      id,
      createdAt: now,
      updatedAt: now,
    };

    this.templates.set(id, fullTemplate);
    
    // 持久化到数据库
    await this.persistTemplate(fullTemplate);

    return id;
  }

  /**
   * 获取模板
   */
  getTemplate(id: string): AgentTemplate | undefined {
    return this.templates.get(id);
  }

  /**
   * 列出所有模板
   */
  listTemplates(filter?: RegistryFilter): AgentTemplate[] {
    let results = Array.from(this.templates.values());

    if (filter) {
      if (filter.category) {
        results = results.filter(t => t.category === filter.category);
      }
      if (filter.minRating) {
        results = results.filter(t => t.rating >= filter.minRating!);
      }
      if (filter.tags && filter.tags.length > 0) {
        results = results.filter(t => 
          filter.tags!.some(tag => t.tags.includes(tag))
        );
      }
    }

    return results.sort((a, b) => b.rating - a.rating);
  }

  /**
   * 搜索模板
   */
  searchTemplates(query: string): AgentTemplate[] {
    const lowerQuery = query.toLowerCase();
    
    return Array.from(this.templates.values())
      .filter(t => 
        t.name.toLowerCase().includes(lowerQuery) ||
        t.description.toLowerCase().includes(lowerQuery) ||
        t.tags.some(tag => tag.toLowerCase().includes(lowerQuery))
      )
      .sort((a, b) => b.rating - a.rating);
  }

  /**
   * 更新模板
   */
  async updateTemplate(id: string, updates: Partial<AgentTemplate>): Promise<void> {
    const template = this.templates.get(id);
    if (!template) {
      throw new Error(`Template not found: ${id}`);
    }

    const updated = {
      ...template,
      ...updates,
      id, // 不允许修改 id
      updatedAt: new Date(),
    };

    this.templates.set(id, updated);
    await this.persistTemplate(updated);
  }

  // ============================================
  // 实例管理
  // ============================================

  /**
   * 从模板创建实例
   */
  async createInstance(
    templateId: string,
    overrides?: Partial<AgentConfig>
  ): Promise<string> {
    const template = this.templates.get(templateId);
    if (!template) {
      throw new Error(`Template not found: ${templateId}`);
    }

    const instanceId = `agent-${uuidv4()}`;
    const configId = `config-${uuidv4()}`;

    // 合并配置
    const config: AgentConfig = {
      id: configId,
      name: template.name,
      role: template.configTemplate.role || 'worker',
      tier: template.configTemplate.tier || 'worker',
      teamId: overrides?.teamId,
      parentPm: overrides?.parentPm,
      
      llm: overrides?.llm || template.configTemplate.llm || {
        model: 'glm-5',
        quota: {
          maxTokensPerRequest: 8000,
          maxTokensPerDay: 100000,
          maxRequestsPerMinute: 10,
        },
      },
      
      tools: overrides?.tools || template.configTemplate.tools || [],
      skills: overrides?.skills || template.configTemplate.skills || [],
      knowledge: overrides?.knowledge || template.configTemplate.knowledge || [],
      
      memory: overrides?.memory || template.configTemplate.memory || {
        shortTerm: {
          maxContextSize: 8000,
          strategy: 'fifo',
        },
        longTerm: {
          enabled: false,
          namespace: `${instanceId}:memory`,
          types: ['episodic'],
        },
        persistence: {
          enabled: false,
          autoSave: false,
          selectiveMemories: false,
        },
      },
      
      hooks: overrides?.hooks || template.configTemplate.hooks || [],
      permissions: overrides?.permissions || template.configTemplate.permissions || {
        connection: { canConnectTo: [] },
        resources: { llm: [], tools: [], knowledge: [], skills: [] },
        limits: {
          maxConcurrentTasks: 1,
          maxTokensPerDay: 100000,
          maxExecutionTimeMs: 300000,
          maxMemoryMB: 512,
        },
      },
      
      version: '1.0.0',
      createdAt: new Date(),
      createdBy: overrides?.createdBy || 'system',
    };

    const instance: AgentInstance = {
      id: instanceId,
      templateId,
      config,
      status: 'idle',
      metrics: {
        totalTasks: 0,
        completedTasks: 0,
        failedTasks: 0,
        avgCompletionTime: 0,
        totalTokensUsed: 0,
      },
      createdAt: new Date(),
      lastActiveAt: new Date(),
    };

    let nodeId: string;
    try {
      nodeId = await this.openclawAdapter.registerNode({
        id: instanceId,
        metadata: config,
      });
    } catch (error) {
      console.error(`[AgentRegistry] Failed to register node for instance ${instanceId}:`, error);
      throw new Error(`Failed to register node: ${error instanceof Error ? error.message : String(error)}`);
    }

    instance.currentNodeId = nodeId;
    this.instances.set(instanceId, instance);

    try {
      await this.persistInstance(instance);
    } catch (error) {
      console.error(`[AgentRegistry] Failed to persist instance ${instanceId}:`, error);
      // 不抛出错误，因为实例已在内存中
    }

    return instanceId;
  }

  /**
   * 直接创建实例（不从模板）
   */
  async createDirectInstance(config: AgentConfig): Promise<string> {
    const instanceId = `agent-${uuidv4()}`;

    const instance: AgentInstance = {
      id: instanceId,
      config,
      status: 'idle',
      metrics: {
        totalTasks: 0,
        completedTasks: 0,
        failedTasks: 0,
        avgCompletionTime: 0,
        totalTokensUsed: 0,
      },
      createdAt: new Date(),
      lastActiveAt: new Date(),
    };

    let nodeId: string;
    try {
      nodeId = await this.openclawAdapter.registerNode({
        id: instanceId,
        metadata: config,
      });
    } catch (error) {
      console.error(`[AgentRegistry] Failed to register node for direct instance ${instanceId}:`, error);
      throw new Error(`Failed to register node: ${error instanceof Error ? error.message : String(error)}`);
    }

    instance.currentNodeId = nodeId;
    this.instances.set(instanceId, instance);

    try {
      await this.persistInstance(instance);
    } catch (error) {
      console.error(`[AgentRegistry] Failed to persist direct instance ${instanceId}:`, error);
      // 不抛出错误，因为实例已在内存中
    }

    return instanceId;
  }

  /**
   * 获取实例
   */
  getInstance(id: string): AgentInstance | undefined {
    return this.instances.get(id);
  }

  /**
   * 列出所有实例
   */
  listInstances(filter?: { status?: AgentStatus; teamId?: string }): AgentInstance[] {
    let results = Array.from(this.instances.values());

    if (filter) {
      if (filter.status) {
        results = results.filter(i => i.status === filter.status);
      }
      if (filter.teamId) {
        results = results.filter(i => i.config.teamId === filter.teamId);
      }
    }

    return results;
  }

  /**
   * 更新实例状态
   */
  async updateInstanceStatus(id: string, status: AgentStatus): Promise<void> {
    const instance = this.instances.get(id);
    if (!instance) {
      throw new Error(`Instance not found: ${id}`);
    }

    instance.status = status;
    instance.lastActiveAt = new Date();
    
    await this.persistInstance(instance);
  }

  /**
   * 销毁实例
   */
  async destroyInstance(id: string): Promise<void> {
    const instance = this.instances.get(id);
    if (!instance) {
      return;
    }

    // 从 OpenClaw 注销 Node
    if (instance.currentNodeId) {
      await this.openclawAdapter.unregisterNode(instance.currentNodeId);
    }

    this.instances.delete(id);
    await this.deleteInstancePersist(id);
  }

  /**
   * 匹配最佳 Worker
   */
  matchWorker(requirements: {
    skills?: string[];
    minRating?: number;
    excludeIds?: string[];
  }): AgentTemplate[] {
    let candidates = this.listTemplates({
      category: 'worker',
      minRating: requirements.minRating,
    });

    if (requirements.skills && requirements.skills.length > 0) {
      candidates = candidates.filter(t => 
        requirements.skills!.some(skill => 
          t.tags.includes(skill) || 
          t.configTemplate.skills?.some(s => s.name === skill)
        )
      );
    }

    if (requirements.excludeIds && requirements.excludeIds.length > 0) {
      candidates = candidates.filter(t => !requirements.excludeIds!.includes(t.id));
    }

    return candidates;
  }

  // ============================================
  // 持久化（简化版，后续接入数据库）
  // ============================================

  private async persistTemplate(template: AgentTemplate): Promise<void> {
    // TODO: 写入 PostgreSQL
    // 目前仅内存存储
  }

  private async persistInstance(instance: AgentInstance): Promise<void> {
    // TODO: 写入 PostgreSQL
    // 目前仅内存存储
  }

  private async deleteInstancePersist(id: string): Promise<void> {
    // TODO: 从 PostgreSQL 删除
    // 目前仅内存删除
  }

  // ============================================
  // 初始化：加载内置模板
  // ============================================

  async initialize(): Promise<void> {
    // 加载内置 Agent 模板
    await this.loadBuiltinTemplates();
    
    // 从数据库加载已保存的模板和实例
    await this.loadFromDatabase();
  }

  private async loadBuiltinTemplates(): Promise<void> {
    // GM 模板
    await this.registerTemplate({
      name: 'GM Agent',
      category: 'core',
      description: '总经理 Agent，系统最高决策中枢',
      configTemplate: {
        role: 'gm',
        tier: 'L3',
        llm: {
          model: 'claude-opus-4-6-thinking',
          quota: {
            maxTokensPerRequest: 100000,
            maxTokensPerDay: 10000000,
            maxRequestsPerMinute: 100,
          },
        },
        permissions: {
          connection: { canConnectTo: ['*'] },
          resources: { llm: ['*'], tools: ['*'], knowledge: ['*'], skills: ['*'] },
          limits: {
            maxConcurrentTasks: 10,
            maxTokensPerDay: 10000000,
            maxExecutionTimeMs: 3600000,
            maxMemoryMB: 2048,
          },
        },
      },
      version: '1.0.0',
      author: 'clawos',
      rating: 5.0,
      downloads: 0,
      tags: ['core', 'management', 'decision'],
    });

    // Assistant 模板
    await this.registerTemplate({
      name: 'Assistant Agent',
      category: 'core',
      description: '助理 Agent，唯一人机交互入口',
      configTemplate: {
        role: 'assistant',
        tier: 'L1',
        llm: {
          model: 'glm-5',
          quota: {
            maxTokensPerRequest: 8000,
            maxTokensPerDay: 500000,
            maxRequestsPerMinute: 30,
          },
        },
        skills: [{ id: 'interaction', name: 'User Interaction', version: '1.0.0', source: 'builtin', category: 'core', tags: [] }],
        permissions: {
          connection: { canConnectTo: ['gm-*'] },
          resources: { llm: ['glm-5'], tools: [], knowledge: [], skills: ['interaction'] },
          limits: {
            maxConcurrentTasks: 1,
            maxTokensPerDay: 500000,
            maxExecutionTimeMs: 60000,
            maxMemoryMB: 256,
          },
        },
      },
      version: '1.0.0',
      author: 'clawos',
      rating: 5.0,
      downloads: 0,
      tags: ['core', 'interaction', 'user-facing'],
    });

    // Platform PM 模板
    await this.registerTemplate({
      name: 'Platform PM',
      category: 'core',
      description: '平台 PM，负责造 Agent、建 Skill、维护生态',
      configTemplate: {
        role: 'platform-pm',
        tier: 'L2',
        llm: {
          model: 'claude-sonnet-4-5',
          quota: {
            maxTokensPerRequest: 50000,
            maxTokensPerDay: 5000000,
            maxRequestsPerMinute: 50,
          },
        },
        skills: [
          { id: 'agent-builder', name: 'Agent Builder', version: '1.0.0', source: 'builtin', category: 'platform', tags: [] },
          { id: 'skill-importer', name: 'Skill Importer', version: '1.0.0', source: 'builtin', category: 'platform', tags: [] },
        ],
        permissions: {
          connection: { canConnectTo: ['gm-*', 'registry'] },
          resources: { llm: ['*'], tools: ['*'], knowledge: ['*'], skills: ['*'] },
          limits: {
            maxConcurrentTasks: 5,
            maxTokensPerDay: 5000000,
            maxExecutionTimeMs: 1800000,
            maxMemoryMB: 1024,
          },
        },
      },
      version: '1.0.0',
      author: 'clawos',
      rating: 5.0,
      downloads: 0,
      tags: ['core', 'platform', 'builder'],
    });

    // Project PM (Dev) 模板
    await this.registerTemplate({
      name: 'Dev PM',
      category: 'coding',
      description: '开发项目经理，负责组建开发团队、推进开发任务',
      configTemplate: {
        role: 'project-pm',
        tier: 'L2',
        llm: {
          model: 'claude-sonnet-4-5',
          quota: {
            maxTokensPerRequest: 50000,
            maxTokensPerDay: 3000000,
            maxRequestsPerMinute: 30,
          },
        },
        skills: [
          { id: 'team-builder', name: 'Team Builder', version: '1.0.0', source: 'builtin', category: 'management', tags: [] },
          { id: 'code-review', name: 'Code Review', version: '1.0.0', source: 'builtin', category: 'coding', tags: [] },
        ],
        permissions: {
          connection: { canConnectTo: ['gm-*', 'worker-*'] },
          resources: { llm: ['claude-sonnet-4-5', 'gpt-5.3-codex'], tools: ['shell', 'file'], knowledge: ['coding-patterns'], skills: ['*'] },
          limits: {
            maxConcurrentTasks: 3,
            maxTokensPerDay: 3000000,
            maxExecutionTimeMs: 1800000,
            maxMemoryMB: 1024,
          },
        },
      },
      version: '1.0.0',
      author: 'clawos',
      rating: 5.0,
      downloads: 0,
      tags: ['coding', 'management', 'pm'],
    });

    // Worker 模板：Frontend
    await this.registerTemplate({
      name: 'Frontend Worker',
      category: 'worker',
      description: '前端开发 Worker',
      configTemplate: {
        role: 'worker',
        tier: 'worker',
        llm: {
          model: 'gpt-5.3-codex',
          quota: {
            maxTokensPerRequest: 16000,
            maxTokensPerDay: 500000,
            maxRequestsPerMinute: 20,
          },
        },
        tools: [
          { id: 'shell', name: 'Shell', type: 'shell' },
          { id: 'file', name: 'File System', type: 'file' },
          { id: 'browser', name: 'Browser', type: 'browser' },
        ],
        skills: [
          { id: 'react-dev', name: 'React Development', version: '1.0.0', source: 'builtin', category: 'frontend', tags: ['react', 'javascript'] },
          { id: 'typescript-expert', name: 'TypeScript Expert', version: '1.0.0', source: 'builtin', category: 'language', tags: ['typescript'] },
        ],
        knowledge: [{ id: 'frontend-patterns', name: 'Frontend Patterns', type: 'vector', access: 'read' }],
        permissions: {
          connection: { canConnectTo: ['project-pm-*'] },
          resources: { llm: ['gpt-5.3-codex'], tools: ['shell', 'file', 'browser'], knowledge: ['frontend-patterns'], skills: ['react-dev', 'typescript-expert'] },
          limits: {
            maxConcurrentTasks: 1,
            maxTokensPerDay: 500000,
            maxExecutionTimeMs: 600000,
            maxMemoryMB: 512,
          },
        },
      },
      version: '1.0.0',
      author: 'clawos',
      rating: 4.5,
      downloads: 0,
      tags: ['worker', 'frontend', 'react', 'typescript'],
    });

    // Worker 模板：Backend
    await this.registerTemplate({
      name: 'Backend Worker',
      category: 'worker',
      description: '后端开发 Worker',
      configTemplate: {
        role: 'worker',
        tier: 'worker',
        llm: {
          model: 'gpt-5.3-codex',
          quota: {
            maxTokensPerRequest: 16000,
            maxTokensPerDay: 500000,
            maxRequestsPerMinute: 20,
          },
        },
        tools: [
          { id: 'shell', name: 'Shell', type: 'shell' },
          { id: 'file', name: 'File System', type: 'file' },
          { id: 'database', name: 'Database', type: 'database' },
        ],
        skills: [
          { id: 'python-expert', name: 'Python Expert', version: '1.0.0', source: 'builtin', category: 'language', tags: ['python'] },
          { id: 'fastapi-dev', name: 'FastAPI Development', version: '1.0.0', source: 'builtin', category: 'backend', tags: ['fastapi', 'api'] },
        ],
        knowledge: [{ id: 'backend-patterns', name: 'Backend Patterns', type: 'vector', access: 'read' }],
        permissions: {
          connection: { canConnectTo: ['project-pm-*'] },
          resources: { llm: ['gpt-5.3-codex'], tools: ['shell', 'file', 'database'], knowledge: ['backend-patterns'], skills: ['python-expert', 'fastapi-dev'] },
          limits: {
            maxConcurrentTasks: 1,
            maxTokensPerDay: 500000,
            maxExecutionTimeMs: 600000,
            maxMemoryMB: 512,
          },
        },
      },
      version: '1.0.0',
      author: 'clawos',
      rating: 4.5,
      downloads: 0,
      tags: ['worker', 'backend', 'python', 'fastapi'],
    });

    // Worker 模板：Test
    await this.registerTemplate({
      name: 'Test Worker',
      category: 'worker',
      description: '测试 Worker',
      configTemplate: {
        role: 'worker',
        tier: 'worker',
        llm: {
          model: 'gemini-3-flash',
          quota: {
            maxTokensPerRequest: 8000,
            maxTokensPerDay: 300000,
            maxRequestsPerMinute: 30,
          },
        },
        tools: [
          { id: 'shell', name: 'Shell', type: 'shell' },
          { id: 'file', name: 'File System', type: 'file' },
        ],
        skills: [
          { id: 'pytest', name: 'Pytest', version: '1.0.0', source: 'builtin', category: 'testing', tags: ['pytest', 'python'] },
          { id: 'jest', name: 'Jest', version: '1.0.0', source: 'builtin', category: 'testing', tags: ['jest', 'javascript'] },
        ],
        permissions: {
          connection: { canConnectTo: ['project-pm-*'] },
          resources: { llm: ['gemini-3-flash'], tools: ['shell', 'file'], knowledge: [], skills: ['pytest', 'jest'] },
          limits: {
            maxConcurrentTasks: 1,
            maxTokensPerDay: 300000,
            maxExecutionTimeMs: 300000,
            maxMemoryMB: 256,
          },
        },
      },
      version: '1.0.0',
      author: 'clawos',
      rating: 4.0,
      downloads: 0,
      tags: ['worker', 'testing', 'pytest', 'jest'],
    });

    // Worker 模板：GitHub
    await this.registerTemplate({
      name: 'GitHub Worker',
      category: 'worker',
      description: 'GitHub 协作 Worker',
      configTemplate: {
        role: 'worker',
        tier: 'worker',
        llm: {
          model: 'claude-sonnet-4-5',
          quota: {
            maxTokensPerRequest: 8000,
            maxTokensPerDay: 200000,
            maxRequestsPerMinute: 10,
          },
        },
        tools: [
          { id: 'http', name: 'HTTP Client', type: 'http' },
        ],
        skills: [
          { id: 'git-operations', name: 'Git Operations', version: '1.0.0', source: 'builtin', category: 'github', tags: ['git'] },
          { id: 'pr-management', name: 'PR Management', version: '1.0.0', source: 'builtin', category: 'github', tags: ['pr'] },
        ],
        permissions: {
          connection: { canConnectTo: ['project-pm-*'] },
          resources: { llm: ['claude-sonnet-4-5'], tools: ['http'], knowledge: [], skills: ['git-operations', 'pr-management'] },
          limits: {
            maxConcurrentTasks: 1,
            maxTokensPerDay: 200000,
            maxExecutionTimeMs: 120000,
            maxMemoryMB: 128,
          },
        },
      },
      version: '1.0.0',
      author: 'clawos',
      rating: 4.5,
      downloads: 0,
      tags: ['worker', 'github', 'git', 'pr'],
    });
  }

  private async loadFromDatabase(): Promise<void> {
    // TODO: 从 PostgreSQL 加载
  }
}

// 单例
let registryInstance: AgentRegistry | null = null;

export function getRegistry(openclawAdapter?: OpenClawAdapter): AgentRegistry {
  if (!registryInstance && openclawAdapter) {
    registryInstance = new AgentRegistry(openclawAdapter);
  }
  if (!registryInstance) {
    throw new Error('Registry not initialized. Call getRegistry with openclawAdapter first.');
  }
  return registryInstance;
}
