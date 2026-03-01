#!/usr/bin/env node

/**
 * OpenClaw Agent Runner
 * 
 * 这是一个包装脚本，用于通过 OpenClaw 执行专业 agents
 * 使用 Node.js 实现智能路由和 agent 执行
 */

const path = require('path');
const fs = require('fs');

// Workspace paths
const WORKSPACE = process.env.OPENCLAW_WORKSPACE || path.join(process.env.HOME || process.env.USERPROFILE || '.', 'openclaw-system', 'workspace');
const AGENTS_DIR = path.join(WORKSPACE, 'agents');

// Colors for output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  blue: '\x1b[34m',
  yellow: '\x1b[33m',
  red: '\x1b[31m'
};

function color(code, text) {
  return `${colors[code]}${text}${colors.reset}`;
}

/**
 * Parse command line arguments
 */
function parseArgs(args) {
  const parsed = {
    mode: 'auto',      // auto, dev, legal, research
    task: null,
    collaboration: null, // vote, chain
    verbose: false
  };
  
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    
    switch (arg) {
      case '-v':
      case '--verbose':
        parsed.verbose = true;
        break;
      case '--dev':
        parsed.mode = 'devagent';
        break;
      case '--legal':
        parsed.mode = 'legalagent';
        break;
      case '--research':
        parsed.mode = 'researchagent';
        break;
      case '--vote':
      case '--parallel':
        parsed.collaboration = 'parallel-voting';
        break;
      case '--chain':
      case '--sequential':
        parsed.collaboration = 'sequential-chain';
        break;
      default:
        if (!arg.startsWith('-')) {
          if (parsed.task) {
            parsed.task += ' ' + arg;
          } else {
            parsed.task = arg;
          }
        }
    }
  }
  
  return parsed;
}

/**
 * Load registry
 */
function loadRegistry() {
  const registryPath = path.join(AGENTS_DIR, 'registry.json');
  if (!fs.existsSync(registryPath)) {
    console.error(color('red', `❌ Registry not found at ${registryPath}`));
    process.exit(1);
  }
  
  try {
    const data = fs.readFileSync(registryPath, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.error(color('red', `❌ Failed to load registry: ${error.message}`));
    process.exit(1);
  }
}

/**
 * Simple keyword-based routing (without requiring modules)
 */
function routeTask(task, mode) {
  if (mode !== 'auto') {
    return mode;
  }
  
  const taskLower = task.toLowerCase();
  
  // DevAgent keywords
  const devKeywords = [
    'code', 'programming', 'function', 'class', 'implement', 'api', 
    'bug', 'error', 'fix', 'debug', 'issue', 'problem',
    'test', 'testing', 'unit test', 'coverage',
    'review', 'code review',
    'refactor', 'clean', 'optimize', 'improve', 'rewrite',
    '代码', '编码', 'bug', '修复', '调试', '测试', '重构', '优化'
  ];
  
  // LegalAgent keywords
  const legalKeywords = [
    'legal', 'law', 'contract', 'agreement', 'compliance', 'regulation', 'policy',
    '条款', '合同', '协议', '合规', '法规', '政策', '风险', '责任'
  ];
  
  // ResearchAgent keywords
  const researchKeywords = [
    'research', 'investigate', 'study', 'find', 'search', 'explore',
    'analyze', 'analysis', 'evaluate', 'assess',
    'data', 'statistics', 'analytics', 'metrics',
    'market', 'competitor', 'trend',
    '研究', '调研', '分析', '数据', '趋势', '竞争'
  ];
  
  // Score each agent
  const scores = {
    devagent: 0,
    legalagent: 0,
    researchagent: 0
  };
  
  const words = taskLower.split(/\s+/);
  words.forEach(word => {
    if (devKeywords.includes(word)) scores.devagent += 2;
    if (legalKeywords.includes(word)) scores.legalagent += 2;
    if (researchKeywords.includes(word)) scores.researchagent += 2;
  });
  
  // Find best match
  let bestAgent = 'devagent';
  let bestScore = scores.devagent;
  
  Object.entries(scores).forEach(([agent, score]) => {
    if (score > bestScore) {
      bestScore = score;
      bestAgent = agent;
    }
  });
  
  if (bestScore === 0) {
    // No clear match, default to research for general queries
    return 'researchagent';
  }
  
  return bestAgent;
}

/**
 * Display agent info
 */
function displayAgentInfo(agentId, registry, task) {
  const agent = registry.agents[agentId];
  if (!agent) {
    console.error(color('red', `❌ Agent '${agentId}' not found in registry`));
    return null;
  }
  
  const statusEmoji = agent.status === 'active' ? color('green', '🟢') : color('yellow', '⚪');
  
  console.log('');
  console.log(color('blue', '═════════════════════════════════════════'));
  console.log(`${statusEmoji} ${agent.name || agent.id} (${agent.id})`);
  console.log(color('blue', '═════════════════════════════════════════'));
  console.log('');
  console.log(`  Description: ${agent.description || 'N/A'}`);
  console.log(`  Version: ${agent.version}`);
  console.log(`  Status: ${agent.status}`);
  console.log(`  Capabilities: ${agent.capabilities ? agent.capabilities.join(', ') : 'N/A'}`);
  console.log('');
  console.log(color('bright', `  Task: ${task}`));
  console.log('');
  
  return agent;
}

/**
 * Display task routing result
 */
function displayRoutingResult(mode, task, collaboration = null) {
  const agentNames = {
    devagent: 'DevAgent',
    legalagent: 'LegalAgent',
    researchagent: 'ResearchAgent'
  };
  
  console.log(color('blue', '🧠 Agent Routing Result'));
  console.log(`   Mode: ${collaboration || 'Single Agent'}`);
  console.log(`   Agent: ${agentNames[mode]}`);
  console.log(`   Task: ${task}`);
  console.log('');
}

/**
 * Display help
 */
function displayHelp() {
  console.log('');
  console.log(color('bright', 'OpenClaw Agent Runner'));
  console.log('');
  console.log(color('blue', 'Usage:'));
  console.log('  openclaw-agent [options] <task>');
  console.log('');
  console.log(color('blue', 'Options:'));
  console.log('  --dev         Force use DevAgent');
  console.log('  --legal       Force use LegalAgent');
  console.log('  --research    Force use ResearchAgent');
  console.log('  --vote        Parallel voting mode (3 agents)');
  console.log('  --chain       Sequential chain mode');
  console.log('  -v, --verbose Verbose output');
  console.log('');
  console.log(color('blue', 'Examples:'));
  console.log('  openclaw-agent "审查服务合同"');
  console.log('  openclaw-agent "创建一个 API"');
  console.log('  openclaw-agent --dev "修复 bug"');
  console.log('  openclaw-agent --legal "检查合规性"');
  console.log('  openclaw-agent --vote "评估方案风险"');
  console.log('  openclaw-agent --chain "开发并审查"');
  console.log('');
}

/**
 * Main function
 */
async function main() {
  const args = parseArgs(process.argv.slice(2));
  
  // Display help if no task
  if (!args.task) {
    displayHelp();
    process.exit(0);
  }
  
  // Load registry
  const registry = loadRegistry();
  
  // Route task
  const mode = routeTask(args.task, args.mode);
  displayRoutingResult(mode, args.task, args.collaboration);
  
  // Display agent info
  const agent = displayAgentInfo(mode, registry);
  if (!agent) {
    process.exit(1);
  }
  
  // Note: For full integration, the task would be executed
  // by OpenClaw's agent runtime with the agent's configuration
  // For now, this script handles routing and displays information
  
  console.log(color('yellow', '⚠️  Note:'));
  console.log('   Full LLM execution requires integration with OpenClaw agent runtime.');
  console.log('   This script currently provides routing and agent information.');
  console.log('');
  console.log(color('green', '✅ Ready for integration!'));
}

main().catch(error => {
  console.error(color('red', `❌ Error: ${error.message}`));
  process.exit(1);
});
