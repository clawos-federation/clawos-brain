/**
 * Message Bus
 * 
 * Agent 间通信总线
 * 基于 OpenClaw Tunnel 实现
 */

import { v4 as uuidv4 } from 'uuid';
import { AgentMessage, MessageType, OpenClawAdapter } from '../types';

export interface MessageHandler {
  (message: AgentMessage): Promise<void>;
}

export interface MessageFilter {
  from?: string;
  to?: string;
  type?: MessageType | MessageType[];
  priority?: string;
}

export class MessageBus {
  private openclawAdapter: OpenClawAdapter;
  
  private subscribers: Map<string, MessageHandler> = new Map();
  
  private messageQueues: {
    critical: AgentMessage[];
    high: AgentMessage[];
    normal: AgentMessage[];
    low: AgentMessage[];
  } = {
    critical: [],
    high: [],
    normal: [],
    low: [],
  };
  
  private messageHistory: AgentMessage[] = [];
  private maxHistorySize = 1000;
  
  private pendingAcks: Map<string, {
    resolve: (ack: AgentMessage['payload']) => void;
    reject: (error: Error) => void;
    timeout: NodeJS.Timeout;
  }> = new Map();

  constructor(openclawAdapter: OpenClawAdapter) {
    this.openclawAdapter = openclawAdapter;
  }

  // ============================================
  // 发送消息
  // ============================================

  /**
   * 发送消息
   */
  async send(message: AgentMessage): Promise<void> {
    // 验证
    this.validateMessage(message);
    
    // 填充元数据
    message.timestamp = message.timestamp || new Date();
    message.hops = message.hops || [];
    
    // 保存历史
    this.addToHistory(message);
    
    // 广播
    if (message.to === 'broadcast') {
      await this.broadcast(message);
      return;
    }
    
    // 团队广播
    if (message.to === 'team' && message.teamId) {
      await this.broadcastToTeam(message.teamId, message);
      return;
    }
    
    // 点对点
    await this.sendDirect(message.to as string, message);
  }

  /**
   * 发送并等待确认
   */
  async sendWithAck(
    message: AgentMessage,
    timeoutMs: number = 30000
  ): Promise<any> {
    message.requiresAck = true;
    
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        this.pendingAcks.delete(message.id);
        reject(new Error(`Message ${message.id} ack timeout`));
      }, timeoutMs);
      
      this.pendingAcks.set(message.id, { resolve, reject, timeout });
      
      this.send(message).catch(error => {
        clearTimeout(timeout);
        this.pendingAcks.delete(message.id);
        reject(error);
      });
    });
  }

  /**
   * 点对点发送
   */
  private async sendDirect(to: string, message: AgentMessage): Promise<void> {
    const handler = this.subscribers.get(to);

    if (!handler) {
      console.warn(`No subscriber found for: ${to}`);
      return;
    }

    // 通过 OpenClaw Tunnel 发送
    try {
      await this.openclawAdapter.sendViaTunnel(
        message.from,
        to,
        message
      );
    } catch (error) {
      // 降级：直接调用处理器
      console.error(`[MessageBus] Tunnel send failed for ${to}, falling back to direct handler:`, error);
      try {
        await handler(message);
      } catch (handlerError) {
        console.error(`[MessageBus] Direct handler also failed for ${to}:`, handlerError);
        throw handlerError;
      }
    }
  }

  /**
   * 广播
   */
  private async broadcast(message: AgentMessage): Promise<void> {
    const promises: Promise<void>[] = [];

    for (const [agentId, handler] of this.subscribers) {
      if (agentId !== message.from) {
        promises.push(handler({ ...message, to: agentId }));
      }
    }

    const results = await Promise.allSettled(promises);

    let rejectedCount = 0;
    results.forEach((result, index) => {
      if (result.status === 'rejected') {
        rejectedCount++;
        const agentIds = Array.from(this.subscribers.keys()).filter(id => id !== message.from);
        console.error(`[MessageBus] Broadcast failed for agent ${agentIds[index]}:`, result.reason);
      }
    });

    if (rejectedCount > 0) {
      console.warn(`[MessageBus] Broadcast completed with ${rejectedCount} failures out of ${promises.length} recipients`);
    }
  }

  /**
   * 团队广播
   */
  private async broadcastToTeam(teamId: string, message: AgentMessage): Promise<void> {
    // TODO: 从 Team Registry 获取团队成员
    // 目前简化为广播
    await this.broadcast(message);
  }

  // ============================================
  // 接收消息
  // ============================================

  /**
   * 订阅
   */
  subscribe(agentId: string, handler: MessageHandler): void {
    this.subscribers.set(agentId, handler);
  }

  /**
   * 取消订阅
   */
  unsubscribe(agentId: string): void {
    this.subscribers.delete(agentId);
  }

  /**
   * 处理接收到的消息
   */
  async receiveMessage(message: AgentMessage): Promise<void> {
    const handler = this.subscribers.get(message.to as string);
    
    if (!handler) {
      console.warn(`No handler for message to: ${message.to}`);
      return;
    }
    
    // 处理 ACK
    if (message.type === 'task.result' || message.type === 'collab.response') {
      const pending = this.pendingAcks.get(message.id);
      if (pending) {
        clearTimeout(pending.timeout);
        this.pendingAcks.delete(message.id);
        pending.resolve(message.payload);
      }
    }
    
    // 调用处理器
    await handler(message);
  }

  // ============================================
  // 消息队列
  // ============================================

  /**
   * 入队
   */
  enqueue(message: AgentMessage): void {
    const priority = message.priority || 'normal';
    this.messageQueues[priority].push(message);
  }

  /**
   * 出队（按优先级）
   */
  dequeue(): AgentMessage | null {
    for (const priority of ['critical', 'high', 'normal', 'low'] as const) {
      const message = this.messageQueues[priority].shift();
      if (message) {
        return message;
      }
    }
    return null;
  }

  /**
   * 获取队列长度
   */
  getQueueLength(): { critical: number; high: number; normal: number; low: number } {
    return {
      critical: this.messageQueues.critical.length,
      high: this.messageQueues.high.length,
      normal: this.messageQueues.normal.length,
      low: this.messageQueues.low.length,
    };
  }

  // ============================================
  // 消息历史
  // ============================================

  /**
   * 查询历史
   */
  getHistory(filter?: MessageFilter): AgentMessage[] {
    let results = this.messageHistory;
    
    if (filter) {
      if (filter.from) {
        results = results.filter(m => m.from === filter.from);
      }
      if (filter.to) {
        results = results.filter(m => m.to === filter.to);
      }
      if (filter.type) {
        const types = Array.isArray(filter.type) ? filter.type : [filter.type];
        results = results.filter(m => types.includes(m.type));
      }
    }
    
    return results;
  }

  /**
   * 添加到历史
   */
  private addToHistory(message: AgentMessage): void {
    this.messageHistory.push(message);
    
    // 限制大小
    if (this.messageHistory.length > this.maxHistorySize) {
      this.messageHistory.shift();
    }
  }

  // ============================================
  // 验证
  // ============================================

  private validateMessage(message: AgentMessage): void {
    if (!message.id) {
      throw new Error('Message must have an id');
    }
    if (!message.from) {
      throw new Error('Message must have a from field');
    }
    if (!message.to) {
      throw new Error('Message must have a to field');
    }
    if (!message.type) {
      throw new Error('Message must have a type');
    }
  }

  // ============================================
  // 统计
  // ============================================

  getStats(): {
    totalMessages: number;
    subscribers: number;
    pendingAcks: number;
    queueLengths: ReturnType<MessageBus['getQueueLength']>;
  } {
    return {
      totalMessages: this.messageHistory.length,
      subscribers: this.subscribers.size,
      pendingAcks: this.pendingAcks.size,
      queueLengths: this.getQueueLength(),
    };
  }
}
