/**
 * GM Agent (总经理)
 * 
 * 系统最高决策中枢，唯一持有 Gateway 管理权限
 * 
 * 职责：
 * 1. 判断任务可行性
 * 2. 任命 PM 并授权资源
 * 3. 最终验收成果
 */

import { v4 as uuidv4 } from 'uuid';
import {
  AgentConfig,
  Task,
  TaskType,
  TaskStatus,
  AgentMessage,
  AgentInstance,
  Review,
  OpenClawAdapter,
  TaskPriority,
} from '../../types';
import { AgentRegistry } from '../../registry';
import { MessageBus } from '../../communication';

export interface TaskAnalysis {
  type: TaskType | 'unknown';
  complexity: 'low' | 'medium' | 'high' | 'critical';
  estimatedTime: number;  // 小时
  requiredSkills: string[];
  requiredResources: string[];
  canDo: boolean;
  reason?: string;
}

export interface PMAppointment {
  pmId: string;
  pmType: 'platform-pm' | 'project-pm';
  domain: string;
  authorizedResources: {
    llm: string[];
    tools: string[];
    knowledge: string[];
    skills: string[];
    budget: {
      maxTokens: number;
      maxTimeMs: number;
    };
  };
}

export interface ReviewDecision {
  approved: boolean;
  feedback?: string;
  requireRework?: string[];
}

export class GMAgent {
  private id: string;
  private config: AgentConfig;
  private registry: AgentRegistry;
  private messageBus: MessageBus;
  private openclawAdapter: OpenClawAdapter;

  private activePMs: Map<string, PMAppointment> = new Map();

  private pendingReviews: Map<string, Task> = new Map();

  constructor(config: AgentConfig, registry: AgentRegistry, messageBus: MessageBus, openclawAdapter: OpenClawAdapter) {
    this.id = config.id;
    this.config = config;
    this.registry = registry;
    this.messageBus = messageBus;
    this.openclawAdapter = openclawAdapter;
  }

  // ============================================
  // 核心职责 1: 分析任务
  // ============================================

  async analyzeTask(task: Task): Promise<TaskAnalysis> {
    // 识别任务类型
    const type = this.identifyTaskType(task.description);
    
    // 评估复杂度
    const complexity = this.assessComplexity(task.description, type);
    
    // 估算时间
    const estimatedTime = this.estimateTime(complexity, task.description);
    
    // 确定所需技能
    const requiredSkills = this.identifyRequiredSkills(type, task.description);
    
    // 确定所需资源
    const requiredResources = this.identifyRequiredResources(type, complexity);
    
    // 判断可行性
    const canDo = this.checkFeasibility(type, requiredSkills);
    
    return {
      type,
      complexity,
      estimatedTime,
      requiredSkills,
      requiredResources,
      canDo,
      reason: canDo ? undefined : `No available skills for ${type} tasks`,
    };
  }

  private identifyTaskType(description: string): TaskType | 'unknown' {
    const lower = description.toLowerCase();
    
    if (lower.includes('开发') || lower.includes('代码') || lower.includes('api') || lower.includes('网站') || lower.includes('coding')) {
      return 'coding';
    }
    if (lower.includes('写') || lower.includes('文章') || lower.includes('书') || lower.includes('博客') || lower.includes('writing')) {
      return 'writing';
    }
    if (lower.includes('调研') || lower.includes('分析') || lower.includes('研究') || lower.includes('research')) {
      return 'research';
    }
    if (lower.includes('审查') || lower.includes('审核') || lower.includes('review')) {
      return 'review';
    }
    if (lower.includes('部署') || lower.includes('发布') || lower.includes('deploy')) {
      return 'deployment';
    }
    
    return 'unknown';
  }

  private assessComplexity(description: string, type: TaskType): 'low' | 'medium' | 'high' | 'critical' {
    // 简单规则评估
    const wordCount = description.split(/\s+/).length;
    
    // 关键复杂度指标
    const complexIndicators = [
      '系统', '架构', '分布式', '微服务', '大规模',
      '高可用', '多语言', '跨平台', '集成', '迁移',
    ];
    
    const criticalIndicators = [
      '生产环境', '紧急', '关键', '核心', '不可中断',
    ];
    
    const lower = description.toLowerCase();
    
    if (criticalIndicators.some(ind => lower.includes(ind.toLowerCase()))) {
      return 'critical';
    }
    
    if (complexIndicators.some(ind => lower.includes(ind.toLowerCase()))) {
      return 'high';
    }
    
    if (wordCount > 100 || description.includes('多个') || description.includes('复杂')) {
      return 'medium';
    }
    
    return 'low';
  }

  private estimateTime(complexity: string, description: string): number {
    const baseTime: Record<string, number> = {
      low: 2,
      medium: 8,
      high: 24,
      critical: 72,
    };
    
    return baseTime[complexity] || 8;
  }

  private identifyRequiredSkills(type: TaskType, description: string): string[] {
    const skillMap: Record<string, string[]> = {
      coding: ['coding', 'testing', 'git'],
      writing: ['writing', 'editing'],
      research: ['research', 'analysis'],
      review: ['review', 'analysis'],
      deployment: ['devops', 'ci-cd'],
      analysis: ['analysis', 'data-processing'],
    };
    
    return skillMap[type] || [];
  }

  private identifyRequiredResources(type: TaskType, complexity: string): string[] {
    const resources: string[] = [];
    
    // 所有任务都需要 LLM
    resources.push('llm');
    
    if (type === 'coding') {
      resources.push('shell', 'file', 'browser');
    }
    
    if (complexity === 'high' || complexity === 'critical') {
      resources.push('database');
    }
    
    return resources;
  }

  private checkFeasibility(type: TaskType, requiredSkills: string[]): boolean {
    // 检查 Registry 中是否有对应能力的 Worker 模板
    const templates = this.registry.matchWorker({ skills: requiredSkills });
    return templates.length > 0;
  }

  // ============================================
  // 核心职责 2: 任命 PM 并授权
  // ============================================

  async appointPM(task: Task, analysis: TaskAnalysis): Promise<string> {
    // 根据 domain 选择 PM 类型
    const domain = this.mapTypeToDomain(analysis.type);

    // 查找或创建 PM
    let pmInstance: AgentInstance | undefined;

    // Platform PM 是永久的，直接使用
    if (domain === 'platform') {
      pmInstance = this.registry.listInstances({ status: 'idle' })
        .find(i => i.config.role === 'platform-pm');
    }

    // Project PM 需要动态创建
    if (!pmInstance && domain !== 'platform') {
      // 从模板创建
      const templates = this.registry.listTemplates({ category: domain });
      const pmTemplate = templates.find(t => t.configTemplate.role === 'project-pm');

      if (!pmTemplate) {
        console.error(`[GM] No PM template found for domain: ${domain}`);
        throw new Error(`No PM template found for domain: ${domain}`);
      }

      try {
        const pmId = await this.registry.createInstance(pmTemplate.id, {
          createdBy: this.id,
        });

        pmInstance = this.registry.getInstance(pmId);
      } catch (error) {
        console.error(`[GM] Failed to create PM instance for domain ${domain}:`, error);
        throw new Error(`Failed to create PM instance: ${error instanceof Error ? error.message : String(error)}`);
      }
    }

    if (!pmInstance) {
      console.error('[GM] Failed to create or find PM');
      throw new Error('Failed to create or find PM');
    }

    // 授权资源
    const appointment: PMAppointment = {
      pmId: pmInstance.id,
      pmType: pmInstance.config.role === 'platform-pm' ? 'platform-pm' : 'project-pm',
      domain,
      authorizedResources: {
        llm: this.authorizeLLMs(analysis),
        tools: this.authorizeTools(analysis),
        knowledge: this.authorizeKnowledge(analysis),
        skills: this.authorizeSkills(analysis),
        budget: {
          maxTokens: this.calculateTokenBudget(analysis),
          maxTimeMs: analysis.estimatedTime * 60 * 60 * 1000,
        },
      },
    };

    this.activePMs.set(pmInstance.id, appointment);

    // 发送任务给 PM
    try {
      await this.messageBus.send({
        id: uuidv4(),
        from: this.id,
        to: pmInstance.id,
        type: 'task.assign',
        payload: {
          task,
          analysis,
          authorization: appointment.authorizedResources,
        },
        priority: this.mapPriority(task.priority),
        requiresAck: true,
        timestamp: new Date(),
        hops: [this.id],
      });
    } catch (error) {
      console.error(`[GM] Failed to send task to PM ${pmInstance.id}:`, error);
      this.activePMs.delete(pmInstance.id);
      throw new Error(`Failed to send task to PM: ${error instanceof Error ? error.message : String(error)}`);
    }

    return pmInstance.id;
  }

  private mapTypeToDomain(type: TaskType | 'unknown'): string {
    const domainMap: Record<string, string> = {
      coding: 'coding',
      writing: 'writing',
      research: 'research',
      review: 'review',
      deployment: 'coding',
      analysis: 'research',
      unknown: 'platform',
    };
    return domainMap[type] || 'platform';
  }

  private authorizeLLMs(analysis: TaskAnalysis): string[] {
    if (analysis.type === 'coding') {
      return ['gpt-5.3-codex', 'claude-sonnet-4-5'];
    }
    return ['claude-sonnet-4-5', 'glm-5'];
  }

  private authorizeTools(analysis: TaskAnalysis): string[] {
    return analysis.requiredResources.filter(r => ['shell', 'file', 'browser', 'database', 'http'].includes(r));
  }

  private authorizeKnowledge(analysis: TaskAnalysis): string[] {
    const knowledgeMap: Record<string, string[]> = {
      coding: ['coding-patterns', 'api-docs'],
      writing: ['style-guide'],
      research: ['web-search'],
    };
    return knowledgeMap[analysis.type] || [];
  }

  private authorizeSkills(analysis: TaskAnalysis): string[] {
    return analysis.requiredSkills;
  }

  private calculateTokenBudget(analysis: TaskAnalysis): number {
    const baseBudget = 1000000; // 1M tokens
    const multiplier: Record<string, number> = {
      low: 1,
      medium: 3,
      high: 10,
      critical: 50,
    };
    return baseBudget * (multiplier[analysis.complexity] || 1);
  }

  private mapPriority(priority: TaskPriority): 'low' | 'normal' | 'high' | 'critical' {
    const priorityMap: Record<TaskPriority, 'low' | 'normal' | 'high' | 'critical'> = {
      low: 'low',
      normal: 'normal',
      high: 'high',
      critical: 'critical',
    };
    return priorityMap[priority];
  }

  // ============================================
  // 核心职责 3: 验收成果
  // ============================================

  async reviewResult(result: { taskId: string; pmId: string; output: any }): Promise<ReviewDecision> {
    const { taskId, pmId, output } = result;
    
    // 基本检查
    if (!output || !output.artifacts || output.artifacts.length === 0) {
      return {
        approved: false,
        feedback: 'No output artifacts produced',
        requireRework: ['output'],
      };
    }
    
    // 检查任务状态
    if (output.status === 'failed') {
      return {
        approved: false,
        feedback: output.error || 'Task execution failed',
        requireRework: ['execution'],
      };
    }
    
    // 检查质量指标
    if (output.metrics) {
      if (output.metrics.testCoverage && output.metrics.testCoverage < 0.8) {
        return {
          approved: false,
          feedback: `Test coverage ${output.metrics.testCoverage * 100}% is below 80% threshold`,
          requireRework: ['testing'],
        };
      }
    }
    
    // 通过验收
    return { approved: true };
  }

  // ============================================
  // PM 管理
  // ============================================

  async dismissPM(pmId: string): Promise<void> {
    const appointment = this.activePMs.get(pmId);
    if (!appointment) {
      return;
    }
    
    // 通知 PM 停止
    await this.messageBus.send({
      id: uuidv4(),
      from: this.id,
      to: pmId,
      type: 'mgmt.destroy',
      payload: { reason: 'task_completed' },
      priority: 'normal',
      requiresAck: false,
      timestamp: new Date(),
      hops: [this.id],
    });
    
    // 如果是 Project PM，销毁实例
    if (appointment.pmType === 'project-pm') {
      await this.registry.destroyInstance(pmId);
    }
    
    this.activePMs.delete(pmId);
  }

  getActivePMs(): PMAppointment[] {
    return Array.from(this.activePMs.values());
  }

  // ============================================
  // 消息处理
  // ============================================

  async handleMessage(message: AgentMessage): Promise<void> {
    switch (message.type) {
      case 'task.result':
        await this.handleTaskResult(message);
        break;
      case 'task.error':
        await this.handleTaskError(message);
        break;
      case 'notify.critical':
        await this.handleCriticalNotification(message);
        break;
      default:
        console.log(`GM received unhandled message type: ${message.type}`);
    }
  }

  private async handleTaskResult(message: AgentMessage): Promise<void> {
    const { taskId, pmId, output } = message.payload;

    if (!taskId || !pmId) {
      console.error('[GM] handleTaskResult received invalid payload: missing taskId or pmId');
      return;
    }

    try {
      // 验收
      const decision = await this.reviewResult({ taskId, pmId, output });

      if (decision.approved) {
        // 通知 Assistant 任务完成
        try {
          await this.notifyAssistant({
            type: 'task.completed',
            taskId,
            result: output,
          });
        } catch (notifyError) {
          console.error(`[GM] Failed to notify assistant for task ${taskId}:`, notifyError);
          // 继续执行，不阻塞后续流程
        }

        // 解散 PM（如果是临时的）
        try {
          await this.dismissPM(pmId);
        } catch (dismissError) {
          console.error(`[GM] Failed to dismiss PM ${pmId}:`, dismissError);
          // 继续执行，不阻塞
        }
      } else {
        // 打回重做
        try {
          await this.messageBus.send({
            id: uuidv4(),
            from: this.id,
            to: pmId,
            type: 'task.assign',
            payload: {
              taskId,
              feedback: decision.feedback,
              requireRework: decision.requireRework,
            },
            priority: 'high',
            requiresAck: true,
            timestamp: new Date(),
            hops: [this.id],
          });
        } catch (sendError) {
          console.error(`[GM] Failed to send rework request to PM ${pmId}:`, sendError);
        }
      }
    } catch (error) {
      console.error(`[GM] Error in handleTaskResult for task ${taskId}:`, error);
    }
  }

  private async handleTaskError(message: AgentMessage): Promise<void> {
    const { taskId, pmId, error } = message.payload;
    
    // 通知 Assistant 任务失败
    await this.notifyAssistant({
      type: 'task.failed',
      taskId,
      error,
    });
    
    // 解散 PM
    await this.dismissPM(pmId);
  }

  private async handleCriticalNotification(message: AgentMessage): Promise<void> {
    // 转发给 Assistant
    await this.notifyAssistant({
      type: 'notify.critical',
      from: message.from,
      payload: message.payload,
    });
  }

  // ============================================
  // Assistant 通信
  // ============================================

  async notifyAssistant(notification: any): Promise<void> {
    // 找到 Assistant
    const assistants = this.registry.listInstances()
      .filter(i => i.config.role === 'assistant');
    
    for (const assistant of assistants) {
      await this.messageBus.send({
        id: uuidv4(),
        from: this.id,
        to: assistant.id,
        type: 'notify.info',
        payload: notification,
        priority: 'normal',
        requiresAck: false,
        timestamp: new Date(),
        hops: [this.id],
      });
    }
  }

  // ============================================
  // 入口：处理用户任务
  // ============================================

  async handleUserTask(task: Task): Promise<{ accepted: boolean; pmId?: string; reason?: string }> {
    // 1. 分析任务
    const analysis = await this.analyzeTask(task);
    
    if (!analysis.canDo) {
      return {
        accepted: false,
        reason: analysis.reason,
      };
    }
    
    // 2. 任命 PM
    const pmId = await this.appointPM(task, analysis);
    
    return {
      accepted: true,
      pmId,
    };
  }

  // ============================================
  // 生命周期
  // ============================================

  async start(): Promise<void> {
    // 注册消息处理器
    this.messageBus.subscribe(this.id, this.handleMessage.bind(this));
    
    console.log(`GM Agent ${this.id} started`);
  }

  async stop(): Promise<void> {
    // 解散所有 PM
    for (const pmId of this.activePMs.keys()) {
      await this.dismissPM(pmId);
    }
    
    this.messageBus.unsubscribe(this.id);
    
    console.log(`GM Agent ${this.id} stopped`);
  }
}
