#!/usr/bin/env node

/**
 * OpenClaw Collaborative Blackboard (Orchestration 3.0)
 * 
 * Provides a shared state and communication bus for agents.
 */

const fs = require('fs');
const path = require('path');

class Blackboard {
  constructor(workspacePath = '/Users/henry/openclaw-system/workspace') {
    this.missionsDir = path.join(workspacePath, 'active_missions');
    if (!fs.existsSync(this.missionsDir)) {
      fs.mkdirSync(this.missionsDir, { recursive: true });
    }
  }

  /**
   * Start a new collective mission
   */
  startMission(missionId, task) {
    const mission = {
      id: missionId,
      startTime: new Date().toISOString(),
      task,
      status: 'active',
      sharedContext: {},
      entries: [],
      messages: [],
      proposals: [] // Agentic Thinking: Suggestions for future improvements
    };
    this.saveMission(mission);
    return mission;
  }

  /**
   * Submit a strategic proposal
   */
  submitProposal(missionId, agentId, title, description) {
    const mission = this.getMission(missionId);
    if (!mission) return null;

    mission.proposals.push({
      id: `prop_${Date.now()}`,
      timestamp: new Date().toISOString(),
      agentId,
      title,
      description,
      status: 'pending' // pending, approved, rejected
    });

    this.saveMission(mission);
    console.log(`[Blackboard] 💡 Proposal from ${agentId}: ${title}`);
    return mission;
  }

  /**
   * Post a finding or artifact to the blackboard
   */
  postEntry(missionId, agentId, data) {
    const mission = this.getMission(missionId);
    if (!mission) return null;

    mission.entries.push({
      timestamp: new Date().toISOString(),
      agentId,
      data
    });
    
    // Auto-update shared context based on key findings
    if (data.keyFacts) {
      mission.sharedContext = { ...mission.sharedContext, ...data.keyFacts };
    }

    this.saveMission(mission);
    console.log(`[Blackboard] ${agentId} posted an entry to Mission ${missionId}`);

    // --- Orchestration 5.1: Auto-Fix Trigger ---
    if (agentId === 'testagent' && (data.status === 'failed' || data.finding?.includes('Bug detected'))) {
      console.log(`\n🔧 Blackboard: Failure detected! Automatically triggering DevAgent for repair...`);
      this.sendMessage(missionId, 'system_watchdog', 'devagent', 
        `【自动修复指令】TestAgent 报告了失败点：${data.finding}。请立即分析并提交修复版本。`
      );
    }

    return mission;
  }

  /**
   * Send a message from one agent to another
   */
  sendMessage(missionId, from, to, body) {
    const mission = this.getMission(missionId);
    if (!mission) return null;

    mission.messages.push({
      timestamp: new Date().toISOString(),
      from,
      to,
      body,
      status: 'unread'
    });

    this.saveMission(mission);
    console.log(`[Blackboard] Message: ${from} -> ${to}: "${body.substring(0, 30)}..."`);
    return mission;
  }

  getMission(missionId) {
    const file = path.join(this.missionsDir, `${missionId}.json`);
    if (fs.existsSync(file)) {
      return JSON.parse(fs.readFileSync(file, 'utf8'));
    }
    return null;
  }

  saveMission(mission) {
    const file = path.join(this.missionsDir, `${mission.id}.json`);
    fs.writeFileSync(file, JSON.stringify(mission, null, 2));
  }
}

module.exports = { Blackboard };
