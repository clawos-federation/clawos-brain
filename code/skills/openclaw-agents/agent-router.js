#!/usr/bin/env node

/**
 * OpenClaw Agent Router
 *
 * Routes tasks to the most appropriate agent(s) based on capability matching.
 */

const path = require('path');
const { AgentFactory } = require('./agent-factory');

class AgentRouter {
  constructor(workspacePath = process.env.OPENCLAW_WORKSPACE || path.join(process.env.HOME || process.env.USERPROFILE || '.', 'openclaw-system', 'workspace')) {
    this.factory = new AgentFactory(workspacePath);
    this.taskKeywords = {
      // Code-related
      'code': ['code', 'programming', 'function', 'class', 'implement', 'api', 'developer', 'software', 'system', 'service', 'module', 'component', 'codebase', 'repository', 'git', '开发', '编码', '代码', '创建', '生成', '实现', 'build', '功能', '模块', '组件'],
      'bug': ['bug', 'error', 'fix', 'debug', 'issue', 'problem', 'crash', 'exception', 'failure', '修复', '调试', '错误', '问题'],
      'test': ['test', 'testing', 'unit test', 'coverage', 'assert', 'mock', 'stub', 'spec', 'integration test', 'e2e', '测试', '单元测试', '集成测试'],
      'review': ['review', 'code review', 'audit', 'inspect', 'check', 'verify', 'validate', '审查', '审核', '检查', '验证'],
      'refactor': ['refactor', 'clean', 'optimize', 'improve', 'rewrite', 'restructure', 'reorganize', '重构', '优化', '改进'],
      'deploy': ['deploy', 'deployment', 'release', 'production', 'ci/cd', 'pipeline', '部署', '发布'],
      
      // Legal-related
      'legal': ['legal', 'law', 'lawyer', 'attorney', 'lawful', 'lawsuit', 'litigation', '法律', '律师', '诉讼'],
      'contract': ['contract', 'agreement', 'terms', 'clause', 'provision', 'covenant', '条款', '合同', '协议'],
      'compliance': ['compliance', 'regulation', 'regulatory', 'governance', '合规', '规范', '监管', '法规', '检查', '符合'],
      'policy': ['policy', 'policy', 'terms of service', 'privacy policy', 'tos', 'eula', '政策', '条款', '隐私政策'],
      'ip': ['patent', 'trademark', 'copyright', 'intellectual property', '知识产权', '专利', '商标', '著作权'],
      'risk': ['risk', 'liability', 'liability', 'indemnity', 'warranty', 'disclaimer', '风险', '责任', '赔偿', '免责'],
      'labor': ['labor', 'employment', 'employee', 'employer', 'work', 'job', 'hr', '人力资源', '劳动', '雇佣'],
      
      // Research-related
      'research': ['research', 'investigate', 'study', 'find', 'search', 'lookup', 'explore', '调研', '研究', '查找', '探索'],
      'analyze': ['analyze', 'analysis', 'evaluate', 'assess', 'examine', 'analysis', '分析', '评估', '考察'],
      'data': ['data', 'statistics', 'analytics', 'metrics', 'report', '数据', '统计', '指标', '报告'],
      'market': ['market', 'market research', 'competitor', 'competition', 'trend', 'market', '市场', '竞争对手', '趋势', '竞争'],
      'insight': ['insight', 'finding', 'discovery', 'observation', 'insight', '洞察', '发现', '观察'],
      
      // General
      'explain': ['explain', 'how', 'what is', 'why', 'describe', 'explain', '解释', '描述', '说明'],
      'write': ['write', 'generate', 'create', 'draft', 'write', '生成', '创建', '起草', '撰写'],
      'design': ['design', 'architecture', 'plan', 'structure', 'blueprint', 'design', '架构', '设计', '规划', '结构'],
      'plan': ['plan', 'strategy', 'roadmap', 'milestone', 'plan', '计划', '策略', '路线图'],
    };

    this._compileKeywordRegex();
  }

  _compileKeywordRegex() {
    const allKeywords = [];
    this.keywordToCategory = new Map();

    for (const [category, keywords] of Object.entries(this.taskKeywords)) {
      for (const keyword of keywords) {
        const escapedKeyword = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        allKeywords.push(escapedKeyword);
        this.keywordToCategory.set(keyword.toLowerCase(), category);
      }
    }

    allKeywords.sort((a, b) => b.length - a.length);
    this.keywordRegex = new RegExp(allKeywords.join('|'), 'gi');
  }

  _getKeywordCategory(keyword) {
    return this.keywordToCategory.get(keyword.toLowerCase());
  }

  /**
   * Load all agents for routing
   */
  async loadAgents() {
    this.agents = await this.factory.loadAllAgents();
    return this.agents;
  }

  /**
   * Analyze task to extract requirements
   */
  analyzeTask(task) {
    const taskLower = task.toLowerCase();
    const requirements = {
      keywords: [],
      capabilities: [],
      complexity: 'low',
      risk: 'low'
    };

    const capabilityMap = {
      'code': 'code-generation',
      'bug': 'bug-fixing',
      'test': 'testing',
      'review': 'code-review',
      'refactor': 'refactoring',
      'deploy': 'deployment',
      'legal': 'legal-analysis',
      'contract': 'contract-review',
      'compliance': 'compliance-check',
      'policy': 'policy-interpretation',
      'ip': 'legal-analysis',
      'risk': 'risk-assessment',
      'labor': 'legal-analysis',
      'research': 'research',
      'analyze': 'data-analysis',
      'data': 'data-analysis',
      'market': 'research',
      'insight': 'research',
      'explain': 'explanation',
      'write': 'content-generation',
      'design': 'technical-design',
      'plan': 'technical-design',
    };

    const matchedCategories = new Set();
    let match;
    this.keywordRegex.lastIndex = 0;

    while ((match = this.keywordRegex.exec(taskLower)) !== null) {
      const keyword = match[0];
      if (!requirements.keywords.includes(keyword)) {
        requirements.keywords.push(keyword);
      }
      const category = this._getKeywordCategory(keyword);
      if (category) {
        matchedCategories.add(category);
      }
    }

    for (const category of matchedCategories) {
      const capability = capabilityMap[category];
      if (capability && !requirements.capabilities.includes(capability)) {
        requirements.capabilities.push(capability);
      }
    }

    const complexityIndicators = ['multi', 'complex', 'system', 'architecture', 'integrate', 'deploy'];
    if (complexityIndicators.some(i => taskLower.includes(i))) {
      requirements.complexity = 'high';
    } else if (task.length > 200 || task.split('.').length > 3) {
      requirements.complexity = 'medium';
    }

    const riskIndicators = ['critical', 'production', 'security', 'payment', 'legal', 'compliance'];
    if (riskIndicators.some(i => taskLower.includes(i))) {
      requirements.risk = 'high';
    }

    return requirements;
  }

  /**
   * Score agent capability match
   */
  scoreAgentMatch(agent, requirements) {
    let score = 0;
    const maxScore = requirements.capabilities.length * 10;

    // Capability matching (primary factor)
    for (const cap of requirements.capabilities) {
      if (agent.capabilities.includes(cap)) {
        score += 10;
      }
    }

    // Bonus for keyword match in description
    const agentDesc = agent.description.toLowerCase();
    for (const keyword of requirements.keywords) {
      if (agentDesc.includes(keyword)) {
        score += 5;
      }
    }

    // Quality threshold bonus
    if (agent.quality && agent.quality.threshold >= 8) {
      score += 3;
    }

    // Normalize to 0-100
    return Math.min(100, Math.round((score / maxScore) * 100));
  }

  /**
   * Select collaboration mode
   */
  selectCollaborationMode(requirements, candidates) {
    const { complexity, risk } = requirements;

    // High risk + multiple candidates → Parallel voting
    if (risk === 'high' && candidates.length >= 2) {
      return {
        mode: 'parallel-voting',
        description: '并行投票（多 agent 验证）',
        minAgents: Math.min(candidates.length, 3)
      };
    }

    // High complexity + multiple candidates → Sequential chain
    if (complexity === 'high' && candidates.length >= 2) {
      return {
        mode: 'sequential-chain',
        description: '顺序链（流水线处理）',
        agents: candidates.slice(0, 2)
      };
    }

    // Low complexity → Single agent
    return {
      mode: 'single-agent',
      description: '单 agent 执行',
      agents: [candidates[0]]
    };
  }

  /**
   * Route task to appropriate agent(s)
   */
  async route(task, options = {}) {
    // Load agents if not already loaded
    if (!this.agents) {
      await this.loadAgents();
    }

    // Analyze task
    const requirements = this.analyzeTask(task);

    console.log('\n🔍 Task Analysis:');
    console.log(`   Keywords: ${requirements.keywords.join(', ') || 'none'}`);
    console.log(`   Capabilities: ${requirements.capabilities.join(', ') || 'none'}`);
    console.log(`   Complexity: ${requirements.complexity}`);
    console.log(`   Risk: ${requirements.risk}`);

    // Score and sort agents
    const scoredAgents = this.agents
      .map(agent => ({
        agent,
        score: this.scoreAgentMatch(agent, requirements)
      }))
      .filter(({ score }) => score > 0)
      .sort((a, b) => b.score - a.score);

    console.log('\n📊 Agent Scoring:');
    if (scoredAgents.length === 0) {
      console.log('   ⚠️  No matching agents found');
      return {
        mode: 'single-agent',
        agents: [],
        strategy: 'no-match',
        requirements
      };
    }

    scoredAgents.forEach(({ agent, score }) => {
      const bar = '█'.repeat(Math.floor(score / 10));
      console.log(`   ${agent.id.padEnd(15)} ${bar.padEnd(10)} ${score}%`);
    });

    // Select collaboration mode
    const candidates = scoredAgents.map(s => s.agent);
    const collaboration = this.selectCollaborationMode(requirements, candidates);

    console.log('\n🎯 Routing Strategy:');
    console.log(`   Mode: ${collaboration.mode}`);
    console.log(`   Description: ${collaboration.description}`);

    if (collaboration.mode === 'parallel-voting') {
      collaboration.agents = candidates.slice(0, collaboration.minAgents);
    }

    if (collaboration.agents) {
      console.log(`   Agents: ${collaboration.agents.map(a => a.id).join(', ')}`);
    }

    return {
      mode: collaboration.mode,
      agents: collaboration.agents || candidates,
      strategy: collaboration.description,
      requirements,
      scores: scoredAgents.map(s => ({ id: s.agent.id, score: s.score }))
    };
  }

  /**
   * Get routing statistics
   */
  async getStats() {
    if (!this.agents) {
      await this.loadAgents();
    }

    return {
      totalAgents: this.agents.length,
      agents: this.agents.map(a => ({
        id: a.id,
        name: a.name,
        capabilities: a.capabilities,
        qualityThreshold: a.quality?.threshold || 0,
        model: a.model?.primary || 'unknown'
      }))
    };
  }
}

// CLI interface
if (require.main === module) {
  const router = new AgentRouter();
  const command = process.argv[2];

  (async () => {
    switch (command) {
      case 'route':
        const task = process.argv.slice(3).join(' ');
        if (!task) {
          console.error('Usage: node agent-router.js route "<task>"');
          process.exit(1);
        }
        const result = await router.route(task);
        console.log('\n✅ Routing complete');
        break;

      case 'stats':
        const stats = await router.getStats();
        console.log('\n📊 Agent Registry Stats:');
        console.log(`   Total Agents: ${stats.totalAgents}\n`);
        stats.agents.forEach(a => {
          console.log(`   ${a.id.padEnd(15)} - ${a.name}`);
          console.log(`     Capabilities: ${a.capabilities.join(', ') || 'none'}`);
          console.log(`     Quality: ${a.qualityThreshold}/10 | Model: ${a.model}`);
          console.log();
        });
        break;

      default:
        console.log(`
OpenClaw Agent Router

Usage:
  node agent-router.js route "<task>"    - Route a task to agents
  node agent-router.js stats            - Show agent statistics
        `);
    }
  })().catch(console.error);
}

module.exports = { AgentRouter };
