#!/usr/bin/env node

/**
 * OpenClaw Task Dispatcher
 *
 * Handles task execution and orchestration across multiple agents.
 */

const { ContextManager } = require('./context-manager');
const { AgentMonitor } = require('./agent-monitor');

class TaskDispatcher {
  constructor(workspacePath = '/Users/henry/openclaw-system/workspace') {
    this.contextManager = new ContextManager(workspacePath);
    this.monitor = new AgentMonitor(workspacePath);
    this.executions = new Map();
  }

  /**
   * Execute a task based on routing plan
   */
  async execute(task, routingPlan, options = {}) {
    const { mode, agents, strategy } = routingPlan;
    const executionId = `exec_${Date.now()}`;

    console.log(`\n🚀 Starting Task Execution [${executionId}]`);
    console.log(`   Strategy: ${strategy}`);
    console.log(`   Mode: ${mode}`);

    const startTime = Date.now();

    try {
      let result;

      switch (mode) {
        case 'single-agent':
          result = await this.executeSingleAgent(task, agents[0], executionId, options);
          break;

        case 'parallel-voting':
          result = await this.executeParallelVoting(task, agents, executionId, options);
          break;

        case 'sequential-chain':
          result = await this.executeSequentialChain(task, agents, executionId, options);
          break;

        case 'hierarchy':
          result = await this.executeHierarchy(task, agents, executionId, options);
          break;

        default:
          throw new Error(`Unknown execution mode: ${mode}`);
      }

      const endTime = Date.now();
      const duration = endTime - startTime;

      console.log(`\n✅ Task Execution Complete [${executionId}]`);
      console.log(`   Duration: ${duration}ms`);

      // Log execution
      await this.monitor.logExecution(executionId, task, result, {
        mode,
        duration,
        agents: agents.map(a => a.id)
      });

      return {
        executionId,
        result,
        metrics: {
          duration,
          mode,
          agentCount: agents.length
        },
        success: true
      };

    } catch (error) {
      console.error(`\n❌ Task Execution Failed [${executionId}]`);
      console.error(`   Error: ${error.message}`);

      return {
        executionId,
        error: error.message,
        metrics: { mode, agentCount: agents.length },
        success: false
      };
    }
  }

  /**
   * Single agent execution
   */
  async executeSingleAgent(task, agent, executionId, options) {
    console.log(`\n🤖 Executing with: ${agent.name} (${agent.id})`);

    const context = await this.contextManager.pack(task, [], {
      agentId: agent.id,
      executionId
    });

    // Simulate agent execution (in real implementation, this would call the LLM)
    const startTime = Date.now();
    
    // Placeholder for actual execution
    const result = {
      agentId: agent.id,
      agentName: agent.name,
      response: `[Simulated response from ${agent.name}]`,
      confidence: 0.85,
      timestamp: new Date().toISOString()
    };

    const duration = Date.now() - startTime;

    console.log(`   ✅ Completed in ${duration}ms`);
    console.log(`   Confidence: ${result.confidence * 100}%`);

    return {
      mode: 'single',
      results: [result],
      final: result
    };
  }

  /**
   * Parallel voting execution
   */
  async executeParallelVoting(task, agents, executionId, options) {
    console.log(`\n🗳️  Parallel Voting with ${agents.length} agents`);

    // Execute all agents in parallel
    const startTime = Date.now();
    const promises = agents.map(agent =>
      this.executeAgentTask(task, agent, executionId)
    );

    const results = await Promise.all(promises);
    const duration = Date.now() - startTime;

    console.log(`   ✅ All ${agents.length} agents completed in ${duration}ms`);

    // Vote on best result
    const votedResult = this.voteOnResults(results);

    console.log(`\n🗳️  Voting Results:`);
    results.forEach(r => {
      console.log(`   ${r.agentName.padEnd(20)} Score: ${r.score || 0}`);
    });
    console.log(`   🏆 Winner: ${votedResult.agentName}`);

    return {
      mode: 'parallel-voting',
      results,
      final: votedResult,
      voting: {
        participants: agents.length,
        winner: votedResult.agentId
      }
    };
  }

  /**
   * Sequential chain execution
   */
  async executeSequentialChain(task, agents, executionId, options) {
    console.log(`\n🔗 Sequential Chain with ${agents.length} agents`);

    let currentTask = task;
    const chainResults = [];

    for (let i = 0; i < agents.length; i++) {
      const agent = agents[i];
      console.log(`\n🔗 Step ${i + 1}/${agents.length}: ${agent.name}`);

      const result = await this.executeAgentTask(currentTask, agent, executionId);
      chainResults.push(result);

      // Pass result to next agent
      if (i < agents.length - 1) {
        currentTask = result.response || JSON.stringify(result);
        console.log(`   → Output passed to next agent`);
      }
    }

    console.log(`\n✅ Chain completed`);
    chainResults.forEach((r, i) => {
      console.log(`   Step ${i + 1}: ${r.agentName}`);
    });

    return {
      mode: 'sequential-chain',
      results: chainResults,
      final: chainResults[chainResults.length - 1],
      steps: agents.length
    };
  }

  /**
   * Hierarchy execution (GM Agent + sub-agents)
   */
  async executeHierarchy(task, agents, executionId, options) {
    console.log(`\n👔 Hierarchy Mode (GM Agent coordinating)`);

    // Find GM Agent (highest quality threshold)
    const sortedAgents = [...agents].sort((a, b) => 
      (b.quality?.threshold || 0) - (a.quality?.threshold || 0)
    );
    const gmAgent = sortedAgents[0];
    const subAgents = sortedAgents.slice(1);

    console.log(`   GM Agent: ${gmAgent.name}`);
    console.log(`   Sub-agents: ${subAgents.map(a => a.name).join(', ')}`);

    // GM Agent plans and delegates
    const plan = {
      tasks: subAgents.map(agent => ({
        agentId: agent.id,
        task: `[Sub-task delegated by ${gmAgent.name}]`
      }))
    };

    console.log(`\n📋 GM Agent Plan:`);
    plan.tasks.forEach((t, i) => {
      console.log(`   ${i + 1}. ${t.agentId}`);
    });

    // Execute sub-tasks
    const subResults = await Promise.all(
      plan.tasks.map(t =>
        this.executeAgentTask(t.task, subAgents.find(a => a.id === t.agentId), executionId)
      )
    );

    // GM Agent synthesizes results
    const synthesis = {
      agentId: gmAgent.id,
      agentName: gmAgent.name,
      response: `[Synthesis by ${gmAgent.name} from ${subResults.length} sub-results]`,
      subResults
    };

    console.log(`\n✅ Hierarchy execution complete`);

    return {
      mode: 'hierarchy',
      results: [...subResults, synthesis],
      final: synthesis,
      gmAgent: gmAgent.id,
      subAgentCount: subAgents.length
    };
  }

  /**
   * Execute task with a single agent (Compute Reservoir - Latency-based Fallback)
   */
  async executeAgentTask(task, agent, executionId) {
    const startTime = Date.now();
    
    // Simulate primary execution (can be slow)
    let simulatedDelay = Math.random() * 3000; // 0-3s
    await new Promise(resolve => setTimeout(resolve, simulatedDelay));
    
    let duration = Date.now() - startTime;
    let usedModel = agent.model?.primary || 'default';
    let isFallback = false;

    // Compute Reservoir: Hot-switch if latency > 2s
    if (duration > 2000 && agent.model?.fallback?.length > 0) {
      console.warn(`   ⚠️ Latency Spike (${duration}ms) - Activating Compute Reservoir for ${agent.id}...`);
      usedModel = agent.model.fallback[0];
      isFallback = true;
      // Fast fallback simulation
      await new Promise(resolve => setTimeout(resolve, 200)); 
      duration = Date.now() - startTime;
    }

    // Generate simulated score
    const score = 0.7 + Math.random() * 0.3; // 0.7-1.0

    return {
      agentId: agent.id,
      agentName: agent.name,
      task,
      response: `[Response from ${agent.name}]`,
      score: parseFloat(score.toFixed(2)),
      confidence: parseFloat(score.toFixed(2)),
      timestamp: new Date().toISOString(),
      metrics: {
        duration,
        model: usedModel,
        isFallback
      }
    };
  }

  /**
   * Vote on best result from multiple agents
   */
  voteOnResults(results) {
    // Simple voting: highest score wins
    // In real implementation, could use:
    // - Majority voting
    // - Weighted voting (by quality threshold)
    // - Consensus-based voting

    return results.reduce((best, current) => 
      (current.score || 0) > (best.score || 0) ? current : best
    );
  }

  /**
   * Get execution history
   */
  getExecutionHistory(limit = 10) {
    return this.monitor.getRecentExecutions(limit);
  }

  /**
   * Get execution by ID
   */
  getExecution(executionId) {
    return this.executions.get(executionId);
  }
}

// CLI interface
if (require.main === module) {
  const { AgentRouter } = require('./agent-router');
  
  const dispatcher = new TaskDispatcher();
  const router = new AgentRouter();
  const command = process.argv[2];

  (async () => {
    switch (command) {
      case 'execute':
        const task = process.argv.slice(3).join(' ');
        if (!task) {
          console.error('Usage: node task-dispatcher.js execute "<task>"');
          process.exit(1);
        }

        // Route task first
        const routing = await router.route(task);
        
        if (routing.agents.length === 0) {
          console.error('❌ No agents available for this task');
          process.exit(1);
        }

        // Execute task
        const result = await dispatcher.execute(task, routing);
        console.log('\n✅ Execution complete');
        break;

      case 'history':
        const history = dispatcher.getExecutionHistory();
        console.log('\n📜 Execution History:\n');
        history.forEach(exec => {
          console.log(`   ${exec.executionId.padEnd(20)} ${exec.timestamp}`);
          console.log(`     Task: ${exec.task.substring(0, 50)}...`);
          console.log(`     Agents: ${exec.agents?.join(', ') || 'N/A'}`);
          console.log();
        });
        break;

      default:
        console.log(`
OpenClaw Task Dispatcher

Usage:
  node task-dispatcher.js execute "<task>"  - Execute a task
  node task-dispatcher.js history           - Show execution history
        `);
    }
  })().catch(console.error);
}

module.exports = { TaskDispatcher };
