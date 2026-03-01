#!/usr/bin/env node

/**
 * OpenClaw Tool Discovery Engine (Orchestration 4.0)
 * 
 * Enables agents to discover and learn how to use system tools dynamically.
 */

const { execSync } = require('child_process');

class ToolManager {
  constructor() {}

  /**
   * Check if a tool exists in the system path
   */
  hasTool(toolName) {
    try {
      execSync(`which ${toolName}`, { stdio: 'ignore' });
      return true;
    } catch (e) {
      return false;
    }
  }

  /**
   * Introspect a tool to learn its usage
   */
  inspectTool(toolName) {
    if (!this.hasTool(toolName)) {
      return { exists: false };
    }

    let helpText = '';
    try {
      try {
        helpText = execSync(`${toolName} --help`, { encoding: 'utf8', timeout: 2000 });
      } catch (e) {
        helpText = execSync(`${toolName} -h`, { encoding: 'utf8', timeout: 2000 });
      }
    } catch (e) {
      return { exists: true, error: 'Could not fetch help text' };
    }

    // Fixed split logic
    const summary = helpText.split('\n').slice(0, 50).join('\n');
    
    return {
      exists: true,
      path: execSync(`which ${toolName}`, { encoding: 'utf8' }).trim(),
      usagePreview: summary,
      suggestion: `You can use '${toolName}' to perform this task.`
    };
  }
}

module.exports = { ToolManager };
