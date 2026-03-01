#!/usr/bin/env node

/**
 * OpenClaw Context Manager
 *
 * Manages context passing and state management between agents.
 */

const path = require('path');
const crypto = require('crypto');

class ContextManager {
  // Maximum number of contexts to prevent memory leak
  static MAX_CONTEXTS = 1000;

  constructor(workspacePath = process.env.OPENCLAW_WORKSPACE || path.join(process.env.HOME || process.env.USERPROFILE || '.', 'openclaw-system', 'workspace')) {
    this.workspacePath = workspacePath;
    this.contexts = new Map();
  }

  /**
   * Generate unique context ID
   */
  generateContextId() {
    return `ctx_${crypto.randomUUID()}`;
  }

  /**
   * Pack context for agent execution
   */
  async pack(task, history = [], state = {}) {
    const contextId = this.generateContextId();

    const context = {
      id: contextId,
      timestamp: new Date().toISOString(),
      task: {
        description: task,
        original: task
      },
      history: history.map(h => ({
        agentId: h.agentId,
        timestamp: h.timestamp,
        result: h.result
      })),
      state: {
        ...state,
        variables: state.variables || {},
        metadata: state.metadata || {}
      },
      metadata: {
        version: '1.0.0',
        encoding: 'utf-8'
      }
    };

    this.validateContext(context);

    if (this.contexts.size >= ContextManager.MAX_CONTEXTS) {
      this.evictOldestContext();
    }

    context.lastAccessed = Date.now();
    this.contexts.set(contextId, context);

    console.log(`\n📦 Context packed: ${contextId}`);
    console.log(`   Task length: ${task.length} chars`);
    console.log(`   History entries: ${history.length}`);
    console.log(`   State variables: ${Object.keys(state.variables || {}).length}`);

    return context;
  }

  /**
   * Unpack context for agent consumption
   */
  async unpack(contextId) {
    const context = this.contexts.get(contextId);

    if (!context) {
      throw new Error(`Context not found: ${contextId}`);
    }

    context.lastAccessed = Date.now();

    this.validateContext(context);

    console.log(`\n📦 Context unpacked: ${contextId}`);

    // Return consumable format
    return {
      task: context.task.description,
      history: context.history,
      state: context.state,
      metadata: context.metadata
    };
  }

  /**
   * Update context with execution result
   */
  async updateContext(contextId, result, agentId) {
    const context = this.contexts.get(contextId);

    if (!context) {
      throw new Error(`Context not found: ${contextId}`);
    }

    // Add to history
    context.history.push({
      agentId,
      timestamp: new Date().toISOString(),
      result
    });

    // Update state if provided
    if (result.state) {
      context.state.variables = {
        ...context.state.variables,
        ...result.state.variables
      };
    }

    console.log(`\n📦 Context updated: ${contextId}`);
    console.log(`   Added history entry from ${agentId}`);

    return context;
  }

  /**
   * Merge multiple contexts
   */
  async mergeContexts(contextIds, strategy = 'concatenate') {
    const contexts = contextIds.map(id => this.contexts.get(id)).filter(Boolean);

    if (contexts.length === 0) {
      throw new Error('No valid contexts to merge');
    }

    const mergedId = this.generateContextId();
    let merged;

    switch (strategy) {
      case 'concatenate':
        merged = this.concatenateContexts(contexts);
        break;

      case 'latest':
        merged = contexts[contexts.length - 1];
        break;

      case 'union':
        merged = this.unionContexts(contexts);
        break;

      default:
        throw new Error(`Unknown merge strategy: ${strategy}`);
    }

    merged.id = mergedId;
    merged.timestamp = new Date().toISOString();

    this.contexts.set(mergedId, merged);

    console.log(`\n📦 Contexts merged: ${mergedId}`);
    console.log(`   Strategy: ${strategy}`);
    console.log(`   Source contexts: ${contextIds.length}`);

    return merged;
  }

  /**
   * Concatenate contexts (append all history)
   */
  concatenateContexts(contexts) {
    const base = { ...contexts[0] };
    base.history = [];

    for (const ctx of contexts) {
      base.history = [...base.history, ...ctx.history];
    }

    return base;
  }

  /**
   * Union contexts (merge state variables)
   */
  unionContexts(contexts) {
    const base = { ...contexts[0] };
    base.state.variables = {};

    for (const ctx of contexts) {
      Object.assign(base.state.variables, ctx.state.variables);
    }

    return base;
  }

  /**
   * Aggregate results from multiple agents
   */
  async aggregateResults(results, mode) {
    console.log(`\n🔄 Aggregating results [mode: ${mode}]`);

    switch (mode) {
      case 'vote':
        return this.voteAggregate(results);

      case 'merge':
        return this.mergeAggregate(results);

      case 'consensus':
        return this.consensusAggregate(results);

      case 'best':
        return this.bestAggregate(results);

      case 'summary':
        return this.summaryAggregate(results);

      default:
        return results;
    }
  }

  /**
   * Vote aggregation (most common answer)
   */
  voteAggregate(results) {
    // Count occurrences of similar responses
    const counts = new Map();

    for (const result of results) {
      const key = this.normalizeResponse(result.response);
      counts.set(key, (counts.get(key) || 0) + 1);
    }

    // Find most common
    let maxCount = 0;
    let winner = results[0];

    for (const [key, count] of counts.entries()) {
      if (count > maxCount) {
        maxCount = count;
        winner = results.find(r => 
          this.normalizeResponse(r.response) === key
        );
      }
    }

    console.log(`   Winner: ${winner.agentName} (${maxCount}/${results.length} votes)`);

    return {
      mode: 'vote',
      winner,
      consensus: maxCount / results.length,
      results
    };
  }

  /**
   * Merge aggregation (combine all results)
   */
  mergeAggregate(results) {
    const merged = {
      mode: 'merge',
      combined: results.map(r => ({
        agent: r.agentName,
        content: r.response
      })),
      timestamp: new Date().toISOString()
    };

    console.log(`   Merged ${results.length} results`);

    return merged;
  }

  /**
   * Consensus aggregation (require majority agreement)
   */
  consensusAggregate(results) {
    const voteResult = this.voteAggregate(results);

    if (voteResult.consensus >= 0.5) {
      console.log(`   ✅ Consensus reached (${Math.round(voteResult.consensus * 100)}%)`);
      return voteResult;
    }

    console.log(`   ⚠️  No clear consensus`);
    return {
      mode: 'consensus',
      status: 'no-consensus',
      results,
      bestMatch: voteResult.winner
    };
  }

  /**
   * Best aggregation (highest score)
   */
  bestAggregate(results) {
    const best = results.reduce((a, b) =>
      (a.score || 0) > (b.score || 0) ? a : b
    );

    console.log(`   Best: ${best.agentName} (${best.score})`);

    return {
      mode: 'best',
      winner: best,
      results
    };
  }

  /**
   * Summary aggregation (generate summary of all)
   */
  summaryAggregate(results) {
    const summary = {
      mode: 'summary',
      agents: results.map(r => r.agentName),
      responses: results.map(r => r.response),
      summary: `[Summary of ${results.length} agent responses]`,
      timestamp: new Date().toISOString()
    };

    console.log(`   Generated summary`);

    return summary;
  }

  /**
   * Normalize response for comparison
   */
  normalizeResponse(response) {
    if (!response) return '';
    return response
      .toLowerCase()
      .replace(/\s+/g, ' ')
      .replace(/[^\w\s]/g, '')
      .trim()
      .substring(0, 100); // First 100 chars
  }

  /**
   * Validate context structure
   */
  validateContext(context) {
    const required = ['id', 'task', 'history', 'state'];
    const missing = required.filter(field => !context[field]);

    if (missing.length > 0) {
      throw new Error(`Invalid context: missing fields ${missing.join(', ')}`);
    }

    // Validate task
    if (!context.task.description) {
      throw new Error('Invalid context: task.description is required');
    }

    // Validate history array
    if (!Array.isArray(context.history)) {
      throw new Error('Invalid context: history must be an array');
    }

    return true;
  }

  /**
   * Evict the oldest context (LRU strategy)
   */
  evictOldestContext() {
    let oldestId = null;
    let oldestTime = Infinity;

    for (const [id, ctx] of this.contexts.entries()) {
      const lastAccessed = ctx.lastAccessed || new Date(ctx.timestamp).getTime();
      if (lastAccessed < oldestTime) {
        oldestTime = lastAccessed;
        oldestId = id;
      }
    }

    if (oldestId) {
      this.contexts.delete(oldestId);
      console.log(`\n🧹 LRU evicted context: ${oldestId}`);
    }
  }

  /**
   * Clear old contexts (memory management)
   */
  clearOldContexts(maxAgeMs = 3600000) { // Default 1 hour
    const now = Date.now();
    const cleared = [];

    for (const [id, ctx] of this.contexts.entries()) {
      const age = now - new Date(ctx.timestamp).getTime();

      if (age > maxAgeMs) {
        this.contexts.delete(id);
        cleared.push(id);
      }
    }

    if (cleared.length > 0) {
      console.log(`\n🧹 Cleared ${cleared.length} old contexts`);
    }

    return cleared;
  }

  /**
   * Get context by ID
   */
  getContext(contextId) {
    return this.contexts.get(contextId);
  }

  /**
   * Get all context IDs
   */
  getAllContextIds() {
    return Array.from(this.contexts.keys());
  }
}

// CLI interface
if (require.main === module) {
  const manager = new ContextManager();
  const command = process.argv[2];

  (async () => {
    switch (command) {
      case 'pack':
        const task = process.argv.slice(3).join(' ');
        if (!task) {
          console.error('Usage: node context-manager.js pack "<task>"');
          process.exit(1);
        }

        const ctx = await manager.pack(task);
        console.log(`\n✅ Context ID: ${ctx.id}`);
        break;

      case 'unpack':
        const unpackId = process.argv[3];
        if (!unpackId) {
          console.error('Usage: node context-manager.js unpack <context-id>');
          process.exit(1);
        }

        const unpacked = await manager.unpack(unpackId);
        console.log('\n📦 Unpacked Context:');
        console.log(JSON.stringify(unpacked, null, 2));
        break;

      case 'list':
        const ids = manager.getAllContextIds();
        console.log(`\n📦 Active Contexts (${ids.length}):\n`);
        ids.forEach(id => {
          console.log(`   ${id}`);
        });
        break;

      case 'clear':
        const cleared = manager.clearOldContexts();
        console.log(`\n✅ Cleared ${cleared.length} contexts`);
        break;

      default:
        console.log(`
OpenClaw Context Manager

Usage:
  node context-manager.js pack "<task>"      - Pack a new context
  node context-manager.js unpack <id>       - Unpack a context
  node context-manager.js list              - List all contexts
  node context-manager.js clear             - Clear old contexts
        `);
    }
  })().catch(console.error);
}

module.exports = { ContextManager };
