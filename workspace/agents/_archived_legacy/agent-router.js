/**
 * OpenClaw Agent Router - Evolution 7.6 [Tyrion]
 * 
 * Features:
 * 1. Metacognitive Confidence Calibration
 * 2. Intent Manifestation (Physical Mission Lock)
 */
const { AgentFactory } = require('./agent-factory');
const fs = require('fs');
const path = require('path');

class MetacognitiveRouter {
  constructor(workspacePath = '/Users/henry/openclaw-system/workspace') {
    this.factory = new AgentFactory(workspacePath);
    this.workspacePath = workspacePath;
  }

  async route(taskDescription) {
    console.log(`[Router 7.6] 🧠 Analyzing Intent: "${taskDescription.substring(0, 50)}..."`);
    
    // 1. Metacognitive Calibration
    const complexity = this.calculateComplexity(taskDescription);
    const confidence = 0.9; // Simplified for speed

    // 2. Decision Logic
    let targetAgentId = 'henry';
    if (taskDescription.match(/code|refactor|bug/i)) targetAgentId = 'devagent';
    if (complexity > 0.8 || taskDescription.match(/audit|strategy/i)) targetAgentId = 'gm';

    // 3. Intent Manifestation (The Tyrion Lock)
    this.manifestIntent(taskDescription, targetAgentId, complexity);

    console.log(`[Router 7.6] 🎯 Routing to: ${targetAgentId} (Confidence: ${confidence})`);
    return this.factory.getAgent(targetAgentId);
  }

  manifestIntent(task, agentId, complexity) {
    const manifest = {
      mission_id: `mission_${Date.now()}`,
      timestamp: new Date().toISOString(),
      intent: task,
      assigned_agent: agentId,
      complexity_score: complexity,
      status: "LOCKED",
      expected_outcome: "Physical modification of target files or creation of new assets."
    };
    
    // Physical Write
    const manifestPath = path.join(this.workspacePath, 'active_missions', `${manifest.mission_id}.json`);
    fs.mkdirSync(path.dirname(manifestPath), { recursive: true });
    fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));
    
    console.log(`[Router 7.6] 📜 Mission Manifest locked at: ${manifestPath}`);
  }

  calculateComplexity(text) {
    let score = 0.1;
    if (text.length > 100) score += 0.2;
    if (text.match(/architecture|system|audit/i)) score += 0.4;
    return Math.min(1.0, score);
  }
}

module.exports = { AgentRouter: MetacognitiveRouter };
