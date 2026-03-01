#!/usr/bin/env node

/**
 * OpenClaw Agent Factory
 * 
 * Handles agent loading, instantiation, and lifecycle management.
 */

const fs = require('fs');
const path = require('path');

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
  const normalizedBase = path.resolve(basePath);
  const normalizedTarget = path.resolve(basePath, targetPath);

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
 */
function getSecureWorkspacePath() {
  const envWorkspace = process.env.OPENCLAW_WORKSPACE;
  const allowedRoots = getAllowedWorkspaceRoots();

  if (envWorkspace) {
    const resolvedEnvPath = path.resolve(envWorkspace);

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

  return allowedRoots[0];
}

class AgentFactory {
  constructor(workspacePath) {
    this.workspacePath = workspacePath ? validatePath(getAllowedWorkspaceRoots()[0], workspacePath) : getSecureWorkspacePath();
    this.agentsPath = path.join(this.workspacePath, 'agents');
    this.registryPath = path.join(this.agentsPath, 'registry.json');
    this.schemaPath = path.join(this.agentsPath, 'agent-schema.json');
    
    this.registry = null;
    this.loadedAgents = new Map();
  }

  /**
   * Load the agent registry
   */
  async loadRegistry() {
    try {
      const data = fs.readFileSync(this.registryPath, 'utf8');
      this.registry = JSON.parse(data);
      console.log(`✅ Loaded agent registry (v${this.registry.version})`);
      return this.registry;
    } catch (error) {
      console.error('❌ Failed to load registry:', error.message);
      throw error;
    }
  }

  /**
   * Validate agent definition against schema
   */
  validateAgent(agentDef) {
    // Basic validation (would use JSON Schema validator in production)
    const required = ['id', 'version', 'name', 'description', 'profile', 'model', 'quality'];
    const missing = required.filter(field => !agentDef[field]);
    
    if (missing.length > 0) {
      throw new Error(`Missing required fields: ${missing.join(', ')}`);
    }

    if (agentDef.quality.threshold < 0 || agentDef.quality.threshold > 10) {
      throw new Error('Quality threshold must be between 0 and 10');
    }

    return true;
  }

  /**
   * Load an agent by ID
   */
  async loadAgent(agentId) {
    if (this.loadedAgents.has(agentId)) {
      console.log(`🔄 Agent '${agentId}' already loaded`);
      return this.loadedAgents.get(agentId);
    }

    if (!this.registry) {
      await this.loadRegistry();
    }

    const agentInfo = this.registry.agents[agentId];
    if (!agentInfo) {
      throw new Error(`Agent '${agentId}' not found in registry`);
    }

    const agentPath = validatePath(this.agentsPath, agentInfo.path);
    const agentData = fs.readFileSync(agentPath, 'utf8');
    const agentDef = JSON.parse(agentData);

    this.validateAgent(agentDef);

    if (agentDef.promptFile) {
      const promptPath = validatePath(path.join(this.agentsPath, agentId), agentDef.promptFile);
      if (fs.existsSync(promptPath)) {
        agentDef.systemPrompt = fs.readFileSync(promptPath, 'utf8');
      }
    }

    const agent = new Agent(agentDef);
    this.loadedAgents.set(agentId, agent);
    
    console.log(`✅ Loaded agent '${agentId}' (v${agentDef.version})`);
    return agent;
  }

  /**
   * Load all agents
   */
  async loadAllAgents() {
    await this.loadRegistry();
    
    const agentIds = Object.keys(this.registry.agents);
    const agents = [];
    
    for (const id of agentIds) {
      try {
        const agent = await this.loadAgent(id);
        agents.push(agent);
      } catch (error) {
        console.warn(`⚠️  Failed to load agent '${id}':`, error.message);
      }
    }
    
    return agents;
  }

  /**
   * Get agent by capability
   */
  async findAgentByCapability(capability) {
    await this.loadRegistry();
    
    for (const [id, info] of Object.entries(this.registry.agents)) {
      if (info.status === 'planned') continue;
      
      const agent = await this.loadAgent(id);
      if (agent.capabilities.includes(capability)) {
        return agent;
      }
    }
    
    return null;
  }

  /**
   * List all agents
   */
  async listAgents() {
    await this.loadRegistry();
    
    console.log('\n📋 Available Agents:\n');
    
    for (const [id, info] of Object.entries(this.registry.agents)) {
      const statusIcon = {
        'active': '🟢',
        'development': '🟡',
        'planned': '⚪'
      }[info.status] || '⚪';
      
      console.log(`${statusIcon} ${id.padEnd(20)} v${info.version.padEnd(8)} [${info.status}]`);
    }
    
    console.log();
  }

  /**
   * Register a new agent
   */
  async registerAgent(agentDef) {
    await this.loadRegistry();
    
    const agentId = agentDef.id;

    if (!agentId || typeof agentId !== 'string') {
      throw new Error('Agent ID is required and must be a string');
    }

    if (!/^[a-zA-Z0-9_-]+$/.test(agentId)) {
      throw new Error('Agent ID must contain only alphanumeric characters, hyphens, and underscores');
    }

    if (this.registry.agents[agentId]) {
      throw new Error(`Agent '${agentId}' already exists`);
    }

    this.validateAgent(agentDef);

    const agentDir = validatePath(this.agentsPath, agentId);
    const agentPath = path.join(agentDir, 'agent.json');
    
    if (!fs.existsSync(agentDir)) {
      fs.mkdirSync(agentDir, { recursive: true });
    }
    
    fs.writeFileSync(agentPath, JSON.stringify(agentDef, null, 2));

    // Update registry
    this.registry.agents[agentId] = {
      id: agentId,
      version: agentDef.version,
      status: 'development',
      path: `./${agentId}/agent.json`
    };
    
    this.registry.lastUpdated = new Date().toISOString();
    fs.writeFileSync(this.registryPath, JSON.stringify(this.registry, null, 2));
    
    console.log(`✅ Registered agent '${agentId}'`);
    return agentId;
  }

  /**
   * Update agent status
   */
  async updateAgentStatus(agentId, status) {
    await this.loadRegistry();
    
    if (!this.registry.agents[agentId]) {
      throw new Error(`Agent '${agentId}' not found`);
    }

    this.registry.agents[agentId].status = status;
    this.registry.lastUpdated = new Date().toISOString();
    fs.writeFileSync(this.registryPath, JSON.stringify(this.registry, null, 2));
    
    console.log(`✅ Updated '${agentId}' status to '${status}'`);
  }
}

/**
 * Agent Instance Class
 */
class Agent {
  constructor(definition) {
    this.definition = definition;
    this.id = definition.id;
    this.name = definition.name;
    this.version = definition.version;
    this.description = definition.description;
    this.capabilities = definition.capabilities || [];
    this.quality = definition.quality;
    this.model = definition.model;
    this.skills = definition.skills || [];
    this.guardrails = definition.guardrails || {};
    this.profile = definition.profile;
    this.systemPrompt = definition.systemPrompt || '';
  }

  /**
   * Get agent info
   */
  getInfo() {
    return {
      id: this.id,
      name: this.name,
      version: this.version,
      description: this.description,
      capabilities: this.capabilities,
      qualityThreshold: this.quality.threshold,
      model: this.model.primary,
      status: 'active'
    };
  }

  /**
   * Check if agent has a capability
   */
  hasCapability(capability) {
    return this.capabilities.includes(capability);
  }

  /**
   * Get agent system prompt
   */
  getSystemPrompt() {
    let prompt = this.systemPrompt;
    
    // Add profile info if not in prompt
    if (this.profile && !prompt.includes('You are')) {
      prompt = `You are a ${this.profile.role}.\n\n${prompt}`;
    }
    
    return prompt;
  }

  /**
   * Execute a task (placeholder - actual execution would be handled by OpenClaw)
   */
  async execute(task, context = {}) {
    console.log(`\n🤖 ${this.name} executing task...`);
    console.log(`📋 Task: ${task.substring(0, 100)}...`);
    console.log(`🎯 Using model: ${this.model.primary}`);
    
    // This would integrate with OpenClaw's actual execution
    return {
      agentId: this.id,
      timestamp: new Date().toISOString(),
      status: 'pending',
      task
    };
  }
}

// CLI interface
if (require.main === module) {
  const factory = new AgentFactory();
  const command = process.argv[2];
  
  (async () => {
    switch (command) {
      case 'list':
        await factory.listAgents();
        break;
      
      case 'load':
        const agentId = process.argv[3];
        if (!agentId) {
          console.error('Usage: node agent-factory.js load <agent-id>');
          process.exit(1);
        }
        const agent = await factory.loadAgent(agentId);
        console.log('\n📦 Agent Info:');
        console.log(JSON.stringify(agent.getInfo(), null, 2));
        break;
      
      case 'load-all':
        const agents = await factory.loadAllAgents();
        console.log(`\n✅ Loaded ${agents.length} agents`);
        break;
      
      default:
        console.log(`
OpenClaw Agent Factory

Usage:
  node agent-factory.js list          - List all registered agents
  node agent-factory.js load <id>      - Load a specific agent
  node agent-factory.js load-all       - Load all agents
        `);
    }
  })().catch(console.error);
}

module.exports = { AgentFactory, Agent };
