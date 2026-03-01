#!/usr/bin/env node

/**
 * OpenClaw Quota Sentry (Orchestration 6.6)
 * 
 * Logic: Monitor provider health and trigger horizontal drift.
 */

const fs = require('fs');
const path = require('path');

class QuotaSentry {
  constructor(workspacePath = '/Users/henry/openclaw-system/workspace') {
    this.stateFile = path.join(workspacePath, 'agents', 'provider_health.json');
    this.health = this.loadState();
  }

  loadState() {
    try {
      if (fs.existsSync(this.stateFile)) return JSON.parse(fs.readFileSync(this.stateFile, 'utf8'));
    } catch (e) {}
    return { 
      providers: { 
        'google-antigravity': { success: 0, fail: 0, lastLatency: 0 },
        'openai-codex': { success: 0, fail: 0, lastLatency: 0 },
        'zai': { success: 0, fail: 0, lastLatency: 0 }
      } 
    };
  }

  report(provider, success, latency) {
    if (!this.health.providers[provider]) return;
    
    if (success) {
      this.health.providers[provider].success++;
    } else {
      this.health.providers[provider].fail++;
    }
    this.health.providers[provider].lastLatency = latency;
    this.saveState();
  }

  saveState() {
    fs.writeFileSync(this.stateFile, JSON.stringify(this.health, null, 2));
  }

  getBestProvider() {
    // Logic: Pick provider with lowest failure rate and latency
    return Object.entries(this.health.providers)
      .sort((a, b) => (a[1].fail / (a[1].success || 1)) - (b[1].fail / (b[1].success || 1)))[0][0];
  }
}

module.exports = { QuotaSentry };
