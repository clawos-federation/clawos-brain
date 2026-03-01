/**
 * Assistant Agent (助理)
 * 
 * 唯一人机交互入口
 * 
 * 职责：
 * 1. 接收用户输入，理解意图
 * 2. 转发任务给 GM
 * 3. 主动汇报进度、异常、完成
 * 4. 情绪友好、心理学优化
 * 
 * 不做的事：
 * - 不直接调用 Gateway
 * - 不执行技术任务
 * - 只和 GM 通信
 */

import { v4 as uuidv4 } from 'uuid';
import {
  AgentConfig,
  Task,
  TaskPriority,
  AgentMessage,
  TaskType,
  ParsedIntent,
  ProgressInfo,
  CompletionResult,
  BlockerInfo,
} from '../../types';
import { MessageBus } from '../../communication';

export interface UserInput {
  text: string;
  metadata?: {
    channel?: string;      // webchat / telegram / discord / ...
    userId?: string;
    timestamp?: Date;
  };
}

export interface UserResponse {
  text: string;
  type: 'ack' | 'progress' | 'completion' | 'error' | 'query';
  metadata?: {
    taskId?: string;
    percentComplete?: number;
    estimatedTimeRemaining?: number;
  };
}

export interface ReportStrategy {
  onMilestone: boolean;      // 里程碑完成时汇报
  onBlocker: boolean;        // 遇到阻塞时汇报
  periodicHours: number;     // 定期汇报间隔（0 = 不定期）
  onCompletion: boolean;     // 完成时汇报
}

export interface AssistantState {
  lastReportTime: Date | null;
  activeTasks: Map<string, Task>;
  userContext: {
    name?: string;
    preferences: Record<string, unknown>;
    conversationHistory: string[];
  };
}

export class AssistantAgent {
  private id: string;
  private config: AgentConfig;
  private messageBus: MessageBus;
  private gmId: string;

  private state: AssistantState = {
    lastReportTime: null,
    activeTasks: new Map(),
    userContext: {
      preferences: {},
      conversationHistory: [],
    },
  };

  private reportStrategy: ReportStrategy;

  // 用户消息回调
  private userResponseCallback?: (response: UserResponse) => void;

  constructor(
    config: AgentConfig,
    messageBus: MessageBus,
    gmId: string,
    reportStrategy?: Partial<ReportStrategy>
  ) {
    this.id = config.id;
    this.config = config;
    this.messageBus = messageBus;
    this.gmId = gmId;

    this.reportStrategy = {
      onMilestone: true,
      onBlocker: true,
      periodicHours: 2,
      onCompletion: true,
      ...reportStrategy,
    };
  }

  // ============================================
  // 用户交互
  // ============================================

  /**
   * 接收用户输入
   */
  async receiveUserInput(input: UserInput): Promise<UserResponse> {
    if (!input || !input.text || typeof input.text !== 'string') {
      console.warn('[Assistant] Invalid input received:', input);
      return {
        text: '抱歉，我没有收到有效的输入。请再说一次？',
        type: 'error',
      };
    }

    // 保存到对话历史
    this.state.userContext.conversationHistory.push(input.text);
    if (this.state.userContext.conversationHistory.length > 50) {
      this.state.userContext.conversationHistory.shift();
    }

    // 理解用户意图
    const intent = this.parseIntent(input.text);

    try {
      switch (intent.type) {
        case 'task':
          return await this.handleTaskIntent(input, intent);
        case 'query':
          return await this.handleQueryIntent(input, intent);
        case 'feedback':
          return await this.handleFeedbackIntent(input, intent);
        case 'greeting':
          return await this.handleGreeting(input);
        default:
          return await this.handleUnknownIntent(input);
      }
    } catch (error) {
      console.error('[Assistant] Error processing user input:', error);
      return {
        text: '抱歉，处理你的请求时遇到了问题。请稍后再试。',
        type: 'error',
      };
    }
  }

  /**
   * 设置用户响应回调
   */
  setUserResponseCallback(callback: (response: UserResponse) => void): void {
    this.userResponseCallback = callback;
  }

  /**
   * 发送响应给用户
   */
  private async sendToUser(response: UserResponse): Promise<void> {
    // 应用友好化处理
    const friendlyResponse = this.makeFriendly(response);

    if (this.userResponseCallback) {
      this.userResponseCallback(friendlyResponse);
    }
  }

  // ============================================
  // 意图解析
  // ============================================

  private parseIntent(text: string): ParsedIntent {
    const lower = text.toLowerCase();

    // 任务意图
    if (
      lower.includes('帮我') ||
      lower.includes('开发') ||
      lower.includes('写') ||
      lower.includes('做') ||
      lower.includes('创建') ||
      lower.includes('实现')
    ) {
      return {
        type: 'task',
        payload: { description: text },
      };
    }

    // 查询意图
    if (
      lower.includes('进度') ||
      lower.includes('状态') ||
      lower.includes('怎么样') ||
      lower.includes('完成')
    ) {
      return {
        type: 'query',
        payload: { query: text },
      };
    }

    // 反馈意图
    if (
      lower.includes('不对') ||
      lower.includes('修改') ||
      lower.includes('重做') ||
      lower.includes('好') ||
      lower.includes('满意')
    ) {
      return {
        type: 'feedback',
        payload: { feedback: text },
      };
    }

    // 问候
    if (
      lower.includes('你好') ||
      lower.includes('hi') ||
      lower.includes('hello') ||
      lower.includes('早上') ||
      lower.includes('晚上')
    ) {
      return { type: 'greeting' };
    }

    return { type: 'unknown' };
  }

  // ============================================
  // 意图处理
  // ============================================

  private async handleTaskIntent(input: UserInput, intent: ParsedIntent): Promise<UserResponse> {
    // 创建任务
    const task: Task = {
      id: uuidv4(),
      type: this.inferTaskType(input.text),
      description: input.text,
      priority: this.inferPriority(input.text),
      status: 'created',
      subtaskIds: [],
      checkpoints: [],
      reviews: [],
      createdAt: new Date(),
      createdBy: 'user',
      tags: [],
    };

    // 保存任务
    this.state.activeTasks.set(task.id, task);

    // 发送给 GM
    try {
      await this.messageBus.send({
        id: uuidv4(),
        from: this.id,
        to: this.gmId,
        type: 'task.assign',
        payload: { task },
        priority: 'normal',
        requiresAck: true,
        timestamp: new Date(),
        hops: [this.id],
      });
    } catch (error) {
      console.error('[Assistant] Failed to send task to GM:', error);
      this.state.activeTasks.delete(task.id);
      return {
        text: '抱歉，任务提交失败。请稍后再试。',
        type: 'error',
      };
    }

    return {
      text: this.generateAckMessage(task),
      type: 'ack',
      metadata: { taskId: task.id },
    };
  }

  private async handleQueryIntent(input: UserInput, intent: ParsedIntent): Promise<UserResponse> {
    // 查询活跃任务状态
    if (this.state.activeTasks.size === 0) {
      return {
        text: '目前没有正在进行的任务。有什么我可以帮你的吗？',
        type: 'query',
      };
    }

    // 汇报所有活跃任务
    const taskStatuses = Array.from(this.state.activeTasks.values()).map(task => {
      return `- ${task.description.slice(0, 50)}... (状态: ${this.translateStatus(task.status)})`;
    });

    return {
      text: `当前有 ${this.state.activeTasks.size} 个任务在进行中：\n${taskStatuses.join('\n')}`,
      type: 'query',
    };
  }

  private async handleFeedbackIntent(input: UserInput, intent: ParsedIntent): Promise<UserResponse> {
    // TODO: 将反馈转发给 GM/PM
    return {
      text: '收到你的反馈，我会传达给执行团队。还有其他需要调整的吗？',
      type: 'ack',
    };
  }

  private async handleGreeting(input: UserInput): Promise<UserResponse> {
    const hour = new Date().getHours();
    let greeting: string;

    if (hour < 6) {
      greeting = '这么晚还在工作，辛苦了！';
    } else if (hour < 12) {
      greeting = '早上好！';
    } else if (hour < 18) {
      greeting = '下午好！';
    } else {
      greeting = '晚上好！';
    }

    return {
      text: `${greeting} 有什么我可以帮你的吗？`,
      type: 'ack',
    };
  }

  private async handleUnknownIntent(input: UserInput): Promise<UserResponse> {
    return {
      text: '我不太理解你的意思，能再说清楚一点吗？或者告诉我你想做什么任务？',
      type: 'query',
    };
  }

  // ============================================
  // 主动汇报
  // ============================================

  /**
   * 汇报进度（由 GM 触发）
   */
  async reportProgress(progress: {
    taskId: string;
    percentComplete: number;
    currentStep: string;
    estimatedTimeRemaining?: number;
  }): Promise<void> {
    const task = this.state.activeTasks.get(progress.taskId);
    if (!task) {
      return;
    }

    const message = this.generateProgressMessage(progress);
    
    await this.sendToUser({
      text: message,
      type: 'progress',
      metadata: {
        taskId: progress.taskId,
        percentComplete: progress.percentComplete,
        estimatedTimeRemaining: progress.estimatedTimeRemaining,
      },
    });

    this.state.lastReportTime = new Date();
  }

  /**
   * 汇报完成
   */
  async reportCompletion(result: {
    taskId: string;
    summary: string;
    artifacts: string[];
  }): Promise<void> {
    const task = this.state.activeTasks.get(result.taskId);
    if (!task) {
      return;
    }

    // 更新任务状态
    task.status = 'completed';

    const message = this.generateCompletionMessage(result);

    await this.sendToUser({
      text: message,
      type: 'completion',
      metadata: { taskId: result.taskId },
    });

    // 移除已完成任务
    this.state.activeTasks.delete(result.taskId);
  }

  /**
   * 汇报阻塞
   */
  async reportBlocker(blocker: {
    taskId: string;
    reason: string;
    suggestedActions?: string[];
  }): Promise<void> {
    const task = this.state.activeTasks.get(blocker.taskId);
    if (!task) {
      return;
    }

    const message = this.generateBlockerMessage(blocker);

    await this.sendToUser({
      text: message,
      type: 'error',
      metadata: { taskId: blocker.taskId },
    });
  }

  // ============================================
  // 消息处理
  // ============================================

  async handleMessage(message: AgentMessage): Promise<void> {
    switch (message.type) {
      case 'notify.info':
        await this.handleInfoNotification(message);
        break;
      case 'notify.warning':
        await this.handleWarningNotification(message);
        break;
      case 'notify.critical':
        await this.handleCriticalNotification(message);
        break;
      default:
        console.log(`Assistant received unhandled message type: ${message.type}`);
    }
  }

  private async handleInfoNotification(message: AgentMessage): Promise<void> {
    const payload = message.payload;

    if (payload.type === 'task.completed') {
      await this.reportCompletion({
        taskId: payload.taskId,
        summary: payload.result?.summary || '任务完成',
        artifacts: payload.result?.artifacts || [],
      });
    } else if (payload.type === 'task.progress') {
      await this.reportProgress(payload);
    }
  }

  private async handleWarningNotification(message: AgentMessage): Promise<void> {
    const payload = message.payload;

    await this.sendToUser({
      text: `⚠️ 提醒：${payload.message}`,
      type: 'progress',
      metadata: payload,
    });
  }

  private async handleCriticalNotification(message: AgentMessage): Promise<void> {
    const payload = message.payload;

    if (payload.type === 'task.failed') {
      await this.sendToUser({
        text: `❌ 任务执行遇到问题：${payload.error}\n\n需要我帮你重新安排吗？`,
        type: 'error',
        metadata: { taskId: payload.taskId },
      });

      this.state.activeTasks.delete(payload.taskId);
    } else {
      await this.reportBlocker({
        taskId: payload.taskId,
        reason: payload.reason || payload.message,
        suggestedActions: payload.suggestedActions,
      });
    }
  }

  // ============================================
  // 友好化处理
  // ============================================

  private makeFriendly(response: UserResponse): UserResponse {
    // 添加表情
    let text = response.text;

    if (response.type === 'completion') {
      text = `🎉 ${text}`;
    } else if (response.type === 'error') {
      text = `😅 ${text}`;
    } else if (response.type === 'ack' && !text.includes('好')) {
      text = `好的！${text}`;
    }

    return { ...response, text };
  }

  private generateAckMessage(task: Task): string {
    const timeEstimate = this.estimateTime(task);
    
    return `收到！我来帮你${this.getTaskAction(task.type)}。${
      timeEstimate ? `预计需要 ${timeEstimate}。` : ''
    }我会持续跟进进度，完成后第一时间通知你。`;
  }

  private generateProgressMessage(progress: ProgressInfo): string {
    const progressBar = this.createProgressBar(progress.percentComplete);
    const timeRemaining = progress.estimatedTimeRemaining
      ? `，预计还需 ${this.formatTime(progress.estimatedTimeRemaining)}`
      : '';

    return `📊 进度更新：${progressBar} ${progress.percentComplete}%${timeRemaining}\n当前步骤：${progress.currentStep}`;
  }

  private generateCompletionMessage(result: CompletionResult): string {
    let message = `✅ 任务完成！\n\n${result.summary}`;

    if (result.artifacts && result.artifacts.length > 0) {
      message += `\n\n产出：\n${result.artifacts.map((a: string) => `- ${a}`).join('\n')}`;
    }

    message += '\n\n还有其他需要我帮忙的吗？';

    return message;
  }

  private generateBlockerMessage(blocker: BlockerInfo): string {
    let message = `🚧 任务遇到了一点问题：${blocker.reason}`;

    if (blocker.suggestedActions && blocker.suggestedActions.length > 0) {
      message += '\n\n建议的处理方式：\n';
      message += blocker.suggestedActions.map((a: string) => `- ${a}`).join('\n');
    }

    message += '\n\n你希望我怎么处理？';

    return message;
  }

  // ============================================
  // 辅助方法
  // ============================================

  private inferTaskType(text: string): TaskType {
    const lower = text.toLowerCase();

    if (lower.includes('开发') || lower.includes('代码') || lower.includes('api')) {
      return 'coding';
    }
    if (lower.includes('写') || lower.includes('文章') || lower.includes('书')) {
      return 'writing';
    }
    if (lower.includes('调研') || lower.includes('分析')) {
      return 'research';
    }

    return 'coding'; // 默认
  }

  private inferPriority(text: string): TaskPriority {
    const lower = text.toLowerCase();

    if (lower.includes('紧急') || lower.includes('立即') || lower.includes('尽快')) {
      return 'critical';
    }
    if (lower.includes('重要') || lower.includes('优先')) {
      return 'high';
    }

    return 'normal';
  }

  private translateStatus(status: string): string {
    const statusMap: Record<string, string> = {
      created: '已创建',
      assigned: '已分配',
      planned: '规划中',
      running: '执行中',
      reviewing: '审核中',
      approved: '已通过',
      rejected: '已打回',
      completed: '已完成',
    };
    return statusMap[status] || status;
  }

  private estimateTime(task: Task): string | null {
    // 简单估算
    if (task.type === 'coding') {
      return '几小时到一天';
    }
    if (task.type === 'writing') {
      return '几个小时';
    }
    return null;
  }

  private getTaskAction(type: string): string {
    const actionMap: Record<string, string> = {
      coding: '开发',
      writing: '写作',
      research: '调研',
      review: '审核',
      deployment: '部署',
      analysis: '分析',
    };
    return actionMap[type] || '处理';
  }

  private createProgressBar(percent: number): string {
    const filled = Math.floor(percent / 10);
    const empty = 10 - filled;
    return '█'.repeat(filled) + '░'.repeat(empty);
  }

  private formatTime(ms: number): string {
    const hours = Math.floor(ms / (1000 * 60 * 60));
    const minutes = Math.floor((ms % (1000 * 60 * 60)) / (1000 * 60));

    if (hours > 0) {
      return `${hours}小时${minutes > 0 ? ` ${minutes}分钟` : ''}`;
    }
    return `${minutes}分钟`;
  }

  // ============================================
  // 生命周期
  // ============================================

  async start(): Promise<void> {
    this.messageBus.subscribe(this.id, this.handleMessage.bind(this));
    console.log(`Assistant Agent ${this.id} started`);
  }

  async stop(): Promise<void> {
    this.messageBus.unsubscribe(this.id);
    console.log(`Assistant Agent ${this.id} stopped`);
  }
}
