/**
 * OpenClaw GM Agent Auto-Trigger
 * 
 * 自动判断何时需要触发 GM Agent 进行深度战略规划
 */

class GMTrigger {
  constructor() {
    this.triggers = {
      complexity: {
        enabled: true,
        threshold: 3  // steps > 3
      },
      multiDomain: {
        enabled: true,
        minDomains: 2
      },
      highRisk: {
        enabled: true
      },
      strategicDecision: {
        enabled: true,
        types: ['legal', 'architectural', 'strategic', 'financial']
      },
      largeBudget: {
        enabled: false,  // 暂未实现成本估算
        threshold: 1000
      }
    };
  }

  /**
   * 判断是否应该触发 GM Agent
   */
  shouldTriggerGM(task, analysis) {
    console.log('\n🎯 GM Agent Trigger Analysis');
    
    const reasons = [];
    let triggered = false;
    
    // 1. 复杂度检查
    if (this.triggers.complexity.enabled) {
      const complexity = this.analyzeComplexity(task, analysis);
      
      if (complexity.steps > this.triggers.complexity.threshold) {
        triggered = true;
        reasons.push({
          type: 'complexity',
          reason: `任务复杂度高（${complexity.steps} 步 > ${this.triggers.complexity.threshold} 步）`,
          details: complexity
        });
      }
    }
    
    // 2. 多领域检查
    if (this.triggers.multiDomain.enabled) {
      const domains = this.identifyDomains(analysis);
      
      if (domains.length >= this.triggers.multiDomain.minDomains) {
        triggered = true;
        reasons.push({
          type: 'multi-domain',
          reason: `跨多个领域（${domains.join(', ')}）`,
          details: { domains }
        });
      }
    }
    
    // 3. 高风险检查
    if (this.triggers.highRisk.enabled && analysis.risk === 'high') {
      triggered = true;
      reasons.push({
        type: 'high-risk',
        reason: '高风险任务，需要深度风险评估',
        details: { risk: analysis.risk }
      });
    }
    
    // 4. 战略决策检查
    if (this.triggers.strategicDecision.enabled) {
      const isStrategic = this.isStrategicDecision(task, analysis);
      
      if (isStrategic.match) {
        triggered = true;
        reasons.push({
          type: 'strategic-decision',
          reason: `战略性决策（${isStrategic.type}）`,
          details: isStrategic
        });
      }
    }
    
    console.log(`   Triggered: ${triggered ? '✅ YES' : '❌ NO'}`);
    
    if (triggered) {
      console.log('   Reasons:');
      reasons.forEach(r => {
        console.log(`   - ${r.reason}`);
      });
    }
    
    return {
      triggered,
      reasons,
      recommendation: triggered ? 
        'Use GM Agent for strategic planning and quality assurance' :
        'Henry can handle this task directly'
    };
  }

  /**
   * 分析任务复杂度
   */
  analyzeComplexity(task, analysis) {
    let steps = 1;
    
    // 基于关键词估算步骤数
    const multiStepIndicators = [
      '然后', '接着', '之后', '最后', '第一', '第二', '第三',
      'then', 'next', 'after', 'finally', 'first', 'second', 'third',
      '包含', 'including', 'with', 'and'
    ];
    
    multiStepIndicators.forEach(indicator => {
      if (task.toLowerCase().includes(indicator)) {
        steps++;
      }
    });
    
    // 基于能力数量估算
    if (analysis.capabilities) {
      steps += Math.floor(analysis.capabilities.length / 2);
    }
    
    // 基于复杂度标记
    if (analysis.complexity === 'high') {
      steps += 2;
    } else if (analysis.complexity === 'medium') {
      steps += 1;
    }
    
    return {
      steps,
      complexity: analysis.complexity || 'low',
      estimatedDuration: steps * 1000  // 粗略估算（ms）
    };
  }

  /**
   * 识别涉及的领域
   */
  identifyDomains(analysis) {
    const domains = new Set();
    
    const domainMap = {
      'code-generation': 'development',
      'bug-fixing': 'development',
      'refactoring': 'development',
      'testing': 'development',
      
      'legal-analysis': 'legal',
      'contract-review': 'legal',
      'compliance-check': 'legal',
      
      'research': 'research',
      'data-analysis': 'research',
      
      'technical-design': 'architecture',
      'system-design': 'architecture'
    };
    
    if (analysis.capabilities) {
      analysis.capabilities.forEach(cap => {
        const domain = domainMap[cap];
        if (domain) {
          domains.add(domain);
        }
      });
    }
    
    return Array.from(domains);
  }

  /**
   * 判断是否为战略性决策
   */
  isStrategicDecision(task, analysis) {
    const taskLower = task.toLowerCase();
    
    const strategicKeywords = {
      legal: ['法律', '合同', '合规', 'legal', 'contract', 'compliance'],
      architectural: ['架构', '系统设计', '技术选型', 'architecture', 'system design', 'tech stack'],
      strategic: ['战略', '规划', '路线图', 'strategy', 'roadmap', 'planning'],
      financial: ['财务', '预算', '成本', 'financial', 'budget', 'cost']
    };
    
    for (const [type, keywords] of Object.entries(strategicKeywords)) {
      if (!this.triggers.strategicDecision.types.includes(type)) {
        continue;
      }
      
      for (const keyword of keywords) {
        if (taskLower.includes(keyword)) {
          return {
            match: true,
            type,
            keyword
          };
        }
      }
    }
    
    return { match: false };
  }

  /**
   * 生成 GM Agent 触发报告
   */
  generateTriggerReport(triggerResult) {
    if (!triggerResult.triggered) {
      return null;
    }
    
    return {
      triggered: true,
      timestamp: new Date().toISOString(),
      reasons: triggerResult.reasons,
      recommendation: triggerResult.recommendation,
      suggestedWorkflow: this.suggestWorkflow(triggerResult.reasons)
    };
  }

  /**
   * 根据触发原因建议工作流
   */
  suggestWorkflow(reasons) {
    const reasonTypes = reasons.map(r => r.type);
    
    // 高风险 + 多领域 → 并行投票
    if (reasonTypes.includes('high-risk') && reasonTypes.includes('multi-domain')) {
      return {
        mode: 'parallel-voting',
        description: '高风险跨领域任务，建议多 Agent 并行投票验证'
      };
    }
    
    // 复杂度高 → 顺序链
    if (reasonTypes.includes('complexity')) {
      return {
        mode: 'sequential-chain',
        description: '复杂任务，建议分阶段顺序执行'
      };
    }
    
    // 战略决策 → 层级模式
    if (reasonTypes.includes('strategic-decision')) {
      return {
        mode: 'hierarchy',
        description: '战略决策，GM Agent 协调专业 Agents'
      };
    }
    
    // 默认
    return {
      mode: 'hierarchy',
      description: 'GM Agent 主导的层级模式'
    };
  }

  /**
   * 更新触发配置
   */
  updateConfig(config) {
    Object.assign(this.triggers, config);
  }

  /**
   * 获取当前配置
   */
  getConfig() {
    return { ...this.triggers };
  }
}

module.exports = { GMTrigger };
