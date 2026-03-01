#!/usr/bin/env node

/**
 * OpenClaw Agents Skill - Main Entry Point
 * 
 * 这个 skill 提供智能 agent 路由和执行功能
 * 将用户的任务自动路由到最合适的专业 agent
 */

const path = require('path');
const fs = require('fs');

/**
 * Validate that a target path is within the allowed base path
 * Prevents path traversal attacks (e.g., ../../../etc/passwd)
 *
 * @param {string} basePath - The allowed directory (must be absolute)
 * @param {string} targetPath - The path to validate (relative or absolute)
 * @returns {string} - The resolved absolute path if valid
 * @throws {Error} - If path escapes the base directory
 */
function validatePath(basePath, targetPath) {
  // Normalize and resolve both paths to absolute paths
  const normalizedBase = path.resolve(basePath);
  const normalizedTarget = path.resolve(basePath, targetPath);

  // Check if the resolved target path starts with the base path
  // Use path.normalize to handle trailing slashes consistently
  const baseWithSep = path.normalize(normalizedBase + path.sep);
  const normalizedTargetWithCheck = path.normalize(normalizedTarget + path.sep);

  if (!normalizedTargetWithCheck.startsWith(baseWithSep) && normalizedTarget !== normalizedBase) {
    throw new Error(`Path traversal detected: '${targetPath}' escapes allowed directory`);
  }

  return normalizedTarget;
}

/**
 * Get allowed workspace roots (whitelist)
 * Only these directories are allowed for file operations
 */
function getAllowedWorkspaceRoots() {
  const homeDir = process.env.HOME || process.env.USERPROFILE || '.';
  return [
    path.resolve(homeDir, 'openclaw-system', 'workspace'),
    path.resolve(process.cwd(), 'workspace'),
  ];
}

/**
 * Validate and resolve workspace path from environment variable
 * Ensures the path is within allowed roots
 */
function getSecureWorkspacePath() {
  const envWorkspace = process.env.OPENCLAW_WORKSPACE;
  const allowedRoots = getAllowedWorkspaceRoots();

  if (envWorkspace) {
    // Resolve the environment path
    const resolvedEnvPath = path.resolve(envWorkspace);

    // Check if it's within any allowed root
    const isAllowed = allowedRoots.some(root => {
      const rootWithSep = path.normalize(root + path.sep);
      const checkPath = path.normalize(resolvedEnvPath + path.sep);
      return checkPath.startsWith(rootWithSep) || resolvedEnvPath === root;
    });

    if (!isAllowed) {
      console.warn(`⚠️ OPENCLAW_WORKSPACE '${envWorkspace}' is outside allowed roots, using default`);
      return allowedRoots[0];
    }

    return resolvedEnvPath;
  }

  // Default to first allowed root
  return allowedRoots[0];
}

// Agents workspace path (securely resolved)
const AGENTS_WORKSPACE = path.join(getSecureWorkspacePath(), 'agents');

// Load utilities from workspace
const loadModule = (moduleName) => {
  const modulePath = path.join(AGENTS_WORKSPACE, moduleName);
  if (fs.existsSync(modulePath + '.js')) {
    return require(modulePath);
  }
  console.warn(`Warning: ${moduleName} not found at ${modulePath}.js`);
  return null;
};

// Lazy load agent utilities
let agentRouter = null;
let taskDispatcher = null;
let agentMonitor = null;

function getAgentRouter() {
  if (!agentRouter) {
    agentRouter = loadModule('agent-router');
    if (!agentRouter) throw new Error('agent-router.js not found. Please run from workspace/agents/ directory.');
  }
  return agentRouter;
}

function getTaskDispatcher() {
  if (!taskDispatcher) {
    taskDispatcher = loadModule('task-dispatcher');
    if (!taskDispatcher) throw new Error('task-dispatcher.js not found.');
  }
  return taskDispatcher;
}

function getAgentMonitor() {
  if (!agentMonitor) {
    agentMonitor = loadModule('agent-monitor');
    if (!agentMonitor) throw new Error('agent-monitor.js not found.');
  }
  return agentMonitor;
}

/**
 * Parse command from user input
 * Examples:
 *   /agent review contract
 *   /agent legal check compliance
 *   /agent status
 *   /agent list
 */
function parseCommand(input) {
  const trimmed = input.trim();
  
  // Check for list/status commands
  if (trimmed === '/agent status' || trimmed === '/agent list') {
    return { type: 'status', task: null, agentId: null };
  }
  
  // Check for health check
  if (trimmed.match(/^\/agent\s+health\s+(\w+)/)) {
    const match = trimmed.match(/^\/agent\s+health\s+(\w+)/);
    return { type: 'health', task: null, agentId: match[1] };
  }
  
  // Check for agent-specific command
  if (trimmed.match(/^\/agent\s+(dev|legal|research)\s+/i)) {
    const match = trimmed.match(/^\/agent\s+(dev|legal|research)\s+(.*)$/i);
    return {
      type: 'execute',
      task: match[2],
      agentId: match[1].toLowerCase() + 'agent' // dev → devagent
    };
  }
  
  // Check for mode modifiers
  let mode = 'single';
  let actualTask = trimmed;
  
  if (actualTask.includes('[vote]') || actualTask.includes('[parallel]')) {
    mode = 'parallel-voting';
    actualTask = actualTask.replace(/\[vote\]|\[parallel\]/gi, '').trim();
  } else if (actualTask.includes('[chain]') || actualTask.includes('[sequential]')) {
    mode = 'sequential-chain';
    actualTask = actualTask.replace(/\[chain\]|\[sequential\]/gi, '').trim();
  }
  
  // Default: auto route
  if (trimmed.startsWith('/agent ')) {
    return {
      type: 'execute',
      task: actualTask.replace('/agent ', ''),
      mode,
      agentId: null
    };
  }
  
  return null;
}

/**
 * Format agent list for display
 */
function formatAgentList(agents) {
  const lines = [
    '📋 Available Agents:',
    ''
  ];
  
  agents.forEach(agent => {
    const statusEmoji = agent.status === 'active' ? '🟢' : '⚪';
    lines.push(`  ${statusEmoji} ${agent.id.padEnd(15)} v${agent.version.padEnd(6)} [${agent.status}]`);
    lines.push(`     ${agent.name}`);
    lines.push('');
  });
  
  return lines.join('\n');
}

/**
 * Format health status for display
 */
function formatHealthStatus(health) {
  const lines = [
    '🏥 Agent Health Status:',
    '',
    `   Status: ${health.status === 'HEALTHY' ? '✅ HEALTHY' : '⚠️ ' + health.status}`,
    `   Success Rate: ${(health.successRate * 100).toFixed(1)}%`,
    `   Total Executions: ${health.totalExecutions}`,
    `   Avg Duration: ${health.avgDuration}ms`,
    '',
    '   Top Agents:'
  ];
  
  health.topAgents.forEach(item => {
    lines.push(`     ${item.agent.padEnd(15)} ${item.count}x (${(item.rate * 100).toFixed(1)}%)`);
  });
  
  return lines.join('\n');
}

/**
 * Main handler for agent commands
 */
async function handleAgentCommand(input) {
  const command = parseCommand(input);
  
  if (!command) {
    return null; // Not an agent command
  }
  
  try {
    switch (command.type) {
      case 'status':
        // Show agent list and health
        const router = getAgentRouter();
        const monitor = getAgentMonitor();
        const agents = router.listAgents();
        const health = monitor.getHealth();
        
        return formatAgentList(agents) + '\n\n' + formatHealthStatus(health);
      
      case 'health':
        // Show specific agent health
        if (command.agentId) {
          const monitor = getAgentMonitor();
          const agentStats = monitor.getAgentStats(command.agentId);
          if (agentStats) {
            return `📊 ${command.agentId} Stats:\n\n` +
                   `   Total: ${agentStats.total}\n` +
                   `   Success: ${agentStats.success}\n` +
                   `   Avg Duration: ${agentStats.avgDuration}ms\n` +
                   `   Success Rate: ${(agentStats.successRate * 100).toFixed(1)}%`;
          } else {
            return `❌ Agent '${command.agentId}' not found or no data yet.`;
          }
        }
        break;
      
      case 'execute':
        // Execute task
        const dispatcher = getTaskDispatcher();
        
        if (command.agentId) {
          // Specific agent
          return await dispatcher.execute(command.task, {
            mode: 'single',
            agents: [command.agentId]
          });
        } else {
          // Auto route
          const result = await dispatcher.routeAndExecute(command.task, {
            mode: command.mode
          });
          return result;
        }
      
      default:
        return `❌ Unknown command type: ${command.type}`;
    }
  } catch (error) {
    console.error('Agent command error:', error);
    return `❌ Error executing agent command: ${error.message}`;
  }
}

/**
 * OpenClaw tool handler
 * Called when skill is invoked via OpenClaw
 */
module.exports = {
  name: 'openclaw-agents',
  version: '1.0.0',
  description: 'Professional agent routing and execution system',
  
  /**
   * Handle command input
   * Returns response text or null (not handled)
   */
  handle: async (input, context) => {
    // Check if this is an agent command
    if (!input || !input.toString().trim().startsWith('/agent')) {
      return null;
    }
    
    return await handleAgentCommand(input.toString().trim());
  },
  
  /**
   * Get help text
   */
  help: () => {
    return `
🤖 OpenClaw Agents - Professional Agent Routing System

Usage:
  /agent <task>              Auto-route to best agent
  /agent dev <task>           Use DevAgent
  /agent legal <task>         Use LegalAgent  
  /agent research <task>        Use ResearchAgent
  /agent status               List all agents + health
  /agent health <agentId>      Check specific agent

Collaboration Modes:
  /agent [vote] <task>       Parallel voting (3 agents)
  /agent [chain] <task>      Sequential chain

Examples:
  /agent 审查服务合同
  /agent dev 创建一个 API
  /agent research 研究 AI 趋势
  /agent [vote] 评估技术方案
  /agent [chain] 开发并审查系统

Agents:
  🟢 DevAgent      - Code generation, bug fixing
  🟢 LegalAgent    - Legal analysis, contract review
  🟢 ResearchAgent - Deep research, data analysis
`;
  }
};
