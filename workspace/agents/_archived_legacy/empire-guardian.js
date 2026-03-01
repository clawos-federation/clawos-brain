/**
 * OpenClaw Empire Guardian - Evolution 7.6 [Tyrion]
 * 
 * Purpose: Enforce physical layer isolation.
 * Logic: Low-tier agents cannot modify Core Logic without Titan Sign-off.
 */
const path = require('path');

class EmpireGuardian {
  constructor() {
    this.restrictedZones = [
      'workspace/agents/vanguard-engine.js',
      'workspace/agents/agent-router.js',
      'workspace/agents/dispatch.js',
      'workspace/agents/empire-guardian.js'
    ];
  }

  auditFileAccess(filePath, agentId, intent) {
    // 1. Convert to relative path for checking
    const relPath = path.relative('/Users/henry/openclaw-system', filePath);
    
    // 2. Check if target is a RESTRICTED ZONE
    const isRestricted = this.restrictedZones.some(zone => relPath.includes(zone));

    if (isRestricted && agentId !== 'gm') {
      console.error(`[Guardian 7.6] 🛑 ACCESS DENIED. Agent '${agentId}' tried to modify Core Logic: ${relPath}`);
      throw new Error(`Layer Violation: Low-tier agent cannot modify System Core. Request GM intervention.`);
    }

    // 3. Log access for audit trail
    console.log(`[Guardian 7.6] ✅ Access granted to ${relPath} for ${agentId}`);
    return true;
  }
}

module.exports = { EmpireGuardian };
