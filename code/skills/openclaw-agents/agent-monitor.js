#!/usr/bin/env node

/**
 * OpenClaw Agent Monitor
 *
 * Provides logging, metrics, and quality tracking for agent executions.
 */

const fs = require('fs');
const path = require('path');

class AgentMonitor {
  constructor(workspacePath = process.env.OPENCLAW_WORKSPACE || path.join(process.env.HOME || process.env.USERPROFILE || '.', 'openclaw-system', 'workspace')) {
    this.workspacePath = workspacePath;
    this.logsDir = path.join(workspacePath, 'agents', 'logs');
    this.metricsFile = path.join(workspacePath, 'agents', 'metrics.json');
    
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

    // Load existing metrics
    this.loadMetrics();
  }

  /**
   * Log execution
   */
  async logExecution(executionId, task, result, metadata = {}) {
    const execution = {
      executionId,
      timestamp: new Date().toISOString(),
      task: this.truncateTask(task),
      result: this.sanitizeResult(result),
      metadata,
      success: result.success !== false
    };

    // Add to in-memory history
    this.executionHistory.push(execution);
    
    // Keep only last 1000 in memory
    if (this.executionHistory.length > 1000) {
      this.executionHistory.shift();
    }

    // Update metrics
    this.updateMetrics(execution);

    // Write to log file
    const logFile = path.join(this.logsDir, `exec_${executionId}.log`);
    fs.writeFileSync(logFile, JSON.stringify(execution, null, 2));

    console.log(`\n📊 Execution logged: ${executionId}`);
    console.log(`   Success: ${execution.success}`);
    console.log(`   Mode: ${metadata.mode || 'unknown'}`);
    console.log(`   Duration: ${metadata.duration || 0}ms`);

    return execution;
  }

  /**
   * Update metrics
   */
  updateMetrics(execution) {
    this.metrics.totalExecutions++;

    if (execution.success) {
      this.metrics.successfulExecutions++;
    } else {
      this.metrics.failedExecutions++;
    }

    // Update duration
    const duration = execution.metadata.duration || 0;
    const count = this.metrics.totalExecutions;
    this.metrics.avgDuration = 
      ((this.metrics.avgDuration * (count - 1)) + duration) / count;

    // Update confidence (if available)
    if (execution.result.confidence) {
      const conf = execution.result.confidence;
      this.metrics.avgConfidence =
        ((this.metrics.avgConfidence * (count - 1)) + conf) / count;
    }

    // Update agent usage
    const agentIds = execution.metadata.agents || [];
    for (const agentId of agentIds) {
      if (!this.metrics.agentUsage[agentId]) {
        this.metrics.agentUsage[agentId] = {
          executions: 0,
          successes: 0
        };
      }
      this.metrics.agentUsage[agentId].executions++;
      if (execution.success) {
        this.metrics.agentUsage[agentId].successes++;
      }
    }

    // Update mode usage
    const mode = execution.metadata.mode || 'unknown';
    if (!this.metrics.modeUsage[mode]) {
      this.metrics.modeUsage[mode] = 0;
    }
    this.metrics.modeUsage[mode]++;

    // Save metrics to file
    this.saveMetrics();
  }

  /**
   * Save metrics to file
   */
  saveMetrics() {
    try {
      fs.writeFileSync(this.metricsFile, JSON.stringify(this.metrics, null, 2));
    } catch (error) {
      console.error('Failed to save metrics:', error.message);
    }
  }

  /**
   * Load metrics from file
   */
  loadMetrics() {
    try {
      if (fs.existsSync(this.metricsFile)) {
        const data = fs.readFileSync(this.metricsFile, 'utf8');
        const loaded = JSON.parse(data);
        
        // Merge with default metrics
        this.metrics = {
          ...this.metrics,
          ...loaded,
          startTime: loaded.startTime || this.metrics.startTime
        };

        console.log(`📊 Loaded metrics (${this.metrics.totalExecutions} executions)`);
      }
    } catch (error) {
      console.warn('No existing metrics found, starting fresh');
    }
  }

  /**
   * Get execution history
   */
  getRecentExecutions(limit = 10) {
    return this.executionHistory.slice(-limit);
  }

  /**
   * Get execution by ID
   */
  getExecution(executionId) {
    // Check memory first
    const inMemory = this.executionHistory.find(
      e => e.executionId === executionId
    );
    if (inMemory) return inMemory;

    // Check file
    const logFile = path.join(this.logsDir, `exec_${executionId}.log`);
    if (fs.existsSync(logFile)) {
      const data = fs.readFileSync(logFile, 'utf-8');
      return JSON.parse(data);
    }

    return null;
  }

  /**
   * Get metrics
   */
  getMetrics() {
    return {
      ...this.metrics,
      uptime: Date.now() - new Date(this.metrics.startTime).getTime()
    };
  }

  /**
   * Get health status
   */
  getHealthStatus() {
    const metrics = this.getMetrics();
    const successRate = metrics.totalExecutions > 0
      ? (metrics.successfulExecutions / metrics.totalExecutions) * 100
      : 0;

    let status = 'healthy';
    if (successRate < 80) status = 'degraded';
    if (successRate < 50) status = 'unhealthy';

    return {
      status,
      metrics: {
        successRate: `${successRate.toFixed(1)}%`,
        totalExecutions: metrics.totalExecutions,
        avgDuration: `${metrics.avgDuration.toFixed(0)}ms`,
        avgConfidence: `${(metrics.avgConfidence * 100).toFixed(1)}%`
      },
      topAgents: this.getTopAgents(5),
      topModes: this.getTopModes(5)
    };
  }

  /**
   * Get top agents by usage
   */
  getTopAgents(limit = 5) {
    const usage = Object.entries(this.metrics.agentUsage);
    const sorted = usage.sort((a, b) => b[1].executions - a[1].executions);
    return sorted.slice(0, limit).map(([agentId, data]) => ({
      agentId,
      executions: data.executions,
      successRate: data.executions > 0
        ? `${((data.successes / data.executions) * 100).toFixed(1)}%`
        : 'N/A'
    }));
  }

  /**
   * Get top modes by usage
   */
  getTopModes(limit = 5) {
    const usage = Object.entries(this.metrics.modeUsage);
    const sorted = usage.sort((a, b) => b[1] - a[1]);
    return sorted.slice(0, limit).map(([mode, count]) => ({
      mode,
      count
    }));
  }

  /**
   * Get agent statistics
   */
  getAgentStats(agentId) {
    const usage = this.metrics.agentUsage[agentId];
    if (!usage) {
      return null;
    }

    const executions = this.executionHistory.filter(
      e => e.metadata.agents?.includes(agentId)
    );

    const durations = executions
      .map(e => e.metadata.duration)
      .filter(Boolean);

    const avgDuration = durations.length > 0
      ? durations.reduce((a, b) => a + b, 0) / durations.length
      : 0;

    return {
      agentId,
      totalExecutions: usage.executions,
      successfulExecutions: usage.successes,
      successRate: usage.executions > 0
        ? ((usage.successes / usage.executions) * 100).toFixed(1) + '%'
        : 'N/A',
      avgDuration: `${avgDuration.toFixed(0)}ms`
    };
  }

  /**
   * Truncate task for logging
   */
  truncateTask(task, maxLength = 100) {
    if (task.length <= maxLength) return task;
    return task.substring(0, maxLength) + '...';
  }

  /**
   * Sanitize result for logging
   */
  sanitizeResult(result) {
    if (!result) return null;

    // Remove potentially sensitive data
    const sanitized = { ...result };
    delete sanitized.response; // Full response can be large
    delete sanitized.subResults;

    return {
      success: sanitized.success !== false,
      confidence: sanitized.confidence,
      agentId: sanitized.agentId,
      agentName: sanitized.agentName,
      mode: sanitized.mode
    };
  }

  /**
   * Export metrics as CSV
   */
  exportMetricsCSV(outputPath) {
    const metrics = this.getMetrics();
    
    let csv = 'Timestamp,ExecutionId,Task,Success,Duration,Mode,Agents\n';

    for (const exec of this.executionHistory) {
      const row = [
        exec.timestamp,
        exec.executionId,
        `"${exec.task.replace(/"/g, '""')}"`,
        exec.success,
        exec.metadata.duration || 0,
        exec.metadata.mode || 'unknown',
        exec.metadata.agents?.join(';') || ''
      ].join(',');
      csv += row + '\n';
    }

    if (!outputPath) {
      outputPath = path.join(this.workspacePath, 'agents', 'metrics_export.csv');
    }

    fs.writeFileSync(outputPath, csv);
    console.log(`\n📊 Metrics exported to: ${outputPath}`);

    return outputPath;
  }

  /**
   * Reset metrics (careful!)
   */
  resetMetrics() {
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

    this.executionHistory = [];
    this.saveMetrics();

    console.log('\n🗑️  Metrics reset');
  }
}

// CLI interface
if (require.main === module) {
  const monitor = new AgentMonitor();
  const command = process.argv[2];

  (async () => {
    switch (command) {
      case 'health':
        const health = monitor.getHealthStatus();
        console.log('\n🏥 Agent Health Status:\n');
        console.log(`   Status: ${health.status.toUpperCase()}`);
        console.log(`   Success Rate: ${health.metrics.successRate}`);
        console.log(`   Total Executions: ${health.metrics.totalExecutions}`);
        console.log(`   Avg Duration: ${health.metrics.avgDuration}`);
        console.log(`   Avg Confidence: ${health.metrics.avgConfidence}`);
        console.log('\n   Top Agents:');
        health.topAgents.forEach(a => {
          console.log(`     ${a.agentId.padEnd(15)} ${a.executions}x (${a.successRate})`);
        });
        console.log('\n   Top Modes:');
        health.topModes.forEach(m => {
          console.log(`     ${m.mode.padEnd(20)} ${m.count}x`);
        });
        break;

      case 'metrics':
        const metrics = monitor.getMetrics();
        console.log('\n📊 Metrics:\n');
        console.log(JSON.stringify(metrics, null, 2));
        break;

      case 'history':
        const limit = parseInt(process.argv[3]) || 10;
        const history = monitor.getRecentExecutions(limit);
        console.log(`\n📜 Recent Executions (${history.length}):\n`);
        history.forEach(exec => {
          const icon = exec.success ? '✅' : '❌';
          console.log(`   ${icon} ${exec.executionId} - ${exec.task}`);
        });
        break;

      case 'agent':
        const agentId = process.argv[3];
        if (!agentId) {
          console.error('Usage: node agent-monitor.js agent <agent-id>');
          process.exit(1);
        }

        const agentStats = monitor.getAgentStats(agentId);
        if (agentStats) {
          console.log('\n🤖 Agent Statistics:\n');
          console.log(JSON.stringify(agentStats, null, 2));
        } else {
          console.log(`\n⚠️  No data for agent: ${agentId}`);
        }
        break;

      case 'export':
        const exportPath = process.argv[3];
        const path = monitor.exportMetricsCSV(exportPath);
        console.log(`\n✅ Exported to: ${path}`);
        break;

      case 'reset':
        monitor.resetMetrics();
        break;

      default:
        console.log(`
OpenClaw Agent Monitor

Usage:
  node agent-monitor.js health           - Show health status
  node agent-monitor.js metrics          - Show full metrics
  node agent-monitor.js history [n]      - Show recent executions
  node agent-monitor.js agent <id>       - Show agent stats
  node agent-monitor.js export [path]    - Export metrics as CSV
  node agent-monitor.js reset            - Reset all metrics (careful!)
        `);
    }
  })().catch(console.error);
}

module.exports = { AgentMonitor };
