#!/usr/bin/env node

/**
 * OpenClaw Agent Monitor (v7.1 Evolution)
 *
 * Provides logging, metrics, and mandatory physical verification for agent executions.
 * Hardened by OpenClaw GM - Orchestration 7.1
 */

const fs = require('fs');
const path = require('path');

class AgentMonitor {
  constructor(workspacePath) {
    // Evolution: Dynamic path resolution to support multi-machine alignment
    const defaultHome = process.env.HOME || '/Users/dongshenglu';
    this.workspacePath = workspacePath || path.join(defaultHome, 'openclaw-system/workspace');
    
    this.logsDir = path.join(this.workspacePath, 'agents', 'logs');
    this.metricsFile = path.join(this.workspacePath, 'agents', 'metrics.json');
    
    this.executionHistory = [];
    this.metrics = {
      totalExecutions: 0,
      successfulExecutions: 0,
      failedExecutions: 0,
      avgDuration: 0,
      avgConfidence: 0,
      agentUsage: {},
      modeUsage: {},
      startTime: new Date().toISOString()
    };

    // Ensure logs directory exists
    if (!fs.existsSync(this.logsDir)) {
      fs.mkdirSync(this.logsDir, { recursive: true });
    }

    this.loadMetrics();
  }

  /**
   * Iron Gate Logic: Mandatory Physical Verification
   * @param {Object} result - The result returned by the Agent
   */
  verifyPhysicalDeliverables(result) {
    const artifacts = result.artifacts || [];
    if (artifacts.length === 0) return { verified: true };

    console.log(`🛡️ [Iron Gate] Verifying ${artifacts.length} artifacts...`);
    
    for (const art of artifacts) {
      if (!art.path) continue;
      
      const absolutePath = path.isAbsolute(art.path) 
        ? art.path 
        : path.join(this.workspacePath, art.path);

      if (!fs.existsSync(absolutePath)) {
        return { 
          verified: false, 
          error: `PHYSICAL_EVIDENCE_MISSING: ${art.path}` 
        };
      }

      const stats = fs.statSync(absolutePath);
      if (stats.size === 0) {
        return { 
          verified: false, 
          error: `EMPTY_ARTIFACT_REJECTION: ${art.path}` 
        };
      }
    }

    return { verified: true };
  }

  /**
   * Log execution with enforced verification
   */
  async logExecution(executionId, task, result, metadata = {}) {
    // Evolution: Intercept results and verify physical evidence
    let finalSuccess = result.success !== false;
    let verificationError = null;

    if (finalSuccess) {
      const vCheck = this.verifyPhysicalDeliverables(result);
      if (!vCheck.verified) {
        console.error(`🚨 [Iron Gate] REJECTION: Agent claimed success but evidence failed validation.`);
        finalSuccess = false;
        verificationError = vCheck.error;
      }
    }

    const execution = {
      executionId,
      timestamp: new Date().toISOString(),
      task: this.truncateTask(task),
      result: {
        ...this.sanitizeResult(result),
        verificationError
      },
      metadata,
      success: finalSuccess
    };

    this.executionHistory.push(execution);
    if (this.executionHistory.length > 1000) this.executionHistory.shift();

    this.updateMetrics(execution);

    const logFile = path.join(this.logsDir, `exec_${executionId}.log`);
    fs.writeFileSync(logFile, JSON.stringify(execution, null, 2));

    console.log(`\n📊 Execution logged: ${executionId}`);
    console.log(`   Success: ${execution.success}${verificationError ? ` (${verificationError})` : ''}`);
    console.log(`   Duration: ${metadata.duration || 0}ms`);

    return execution;
  }

  updateMetrics(execution) {
    this.metrics.totalExecutions++;
    if (execution.success) {
      this.metrics.successfulExecutions++;
    } else {
      this.metrics.failedExecutions++;
    }

    const duration = execution.metadata.duration || 0;
    const count = this.metrics.totalExecutions;
    this.metrics.avgDuration = ((this.metrics.avgDuration * (count - 1)) + duration) / count;

    const agentIds = execution.metadata.agents || [];
    for (const agentId of agentIds) {
      if (!this.metrics.agentUsage[agentId]) {
        this.metrics.agentUsage[agentId] = { executions: 0, successes: 0 };
      }
      this.metrics.agentUsage[agentId].executions++;
      if (execution.success) this.metrics.agentUsage[agentId].successes++;
    }

    const mode = execution.metadata.mode || 'unknown';
    if (!this.metrics.modeUsage[mode]) this.metrics.modeUsage[mode] = 0;
    this.metrics.modeUsage[mode]++;

    this.saveMetrics();
  }

  saveMetrics() {
    try {
      fs.writeFileSync(this.metricsFile, JSON.stringify(this.metrics, null, 2));
    } catch (error) {
      console.error('Failed to save metrics:', error.message);
    }
  }

  loadMetrics() {
    try {
      if (fs.existsSync(this.metricsFile)) {
        const data = fs.readFileSync(this.metricsFile, 'utf8');
        const loaded = JSON.parse(data);
        this.metrics = { ...this.metrics, ...loaded };
        console.log(`📊 Loaded metrics (${this.metrics.totalExecutions} executions)`);
      }
    } catch (error) {
      console.warn('No existing metrics found, starting fresh');
    }
  }

  getRecentExecutions(limit = 10) { return this.executionHistory.slice(-limit); }

  getHealthStatus() {
    const metrics = this.metrics;
    const successRate = metrics.totalExecutions > 0
      ? (metrics.successfulExecutions / metrics.totalExecutions) * 100
      : 0;

    return {
      status: successRate > 80 ? 'healthy' : 'degraded',
      metrics: {
        successRate: `${successRate.toFixed(1)}%`,
        totalExecutions: metrics.totalExecutions
      }
    };
  }

  truncateTask(task, maxLength = 100) {
    if (!task) return '';
    return task.length <= maxLength ? task : task.substring(0, maxLength) + '...';
  }

  sanitizeResult(result) {
    if (!result) return null;
    return {
      success: result.success !== false,
      confidence: result.confidence,
      agentId: result.agentId,
      agentName: result.agentName
    };
  }
}

if (require.main === module) {
  const monitor = new AgentMonitor();
  console.log(`🛡️ OpenClaw Monitor Active on: ${monitor.workspacePath}`);
}

module.exports = { AgentMonitor };
