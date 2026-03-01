/**
 * GM Agent Integration Patch for Agent Router
 * 
 * This patch adds GM Agent trigger logic to the route method.
 * Apply this to agent-router.js by inserting after line 280 (before async route method).
 */

const GM_INTEGRATION_PATCH = `
    // GM Agent Trigger Check (P1 Feature)
    const triggerResult = this.gmTrigger.shouldTriggerGM(task, analysis);
    
    if (triggerResult.triggered) {
      console.log('\\n🎯 GM Agent Triggered!');
      console.log('   Reasons:');
      triggerResult.reasons.forEach(r => {
        console.log('      - ' + r.reason);
      });
      console.log('\\n   Workflow: GM Agent takes control');
      
      // Route to GM Agent instead of direct agents
      const gmAgent = this.agents.find(a => a.id === 'gmanager' || a.id === 'gmanager' || a.role === 'strategic');
      
      if (gmAgent) {
        return {
          mode: 'gm-coordination',
          agents: [gmAgent, ...candidates],
          strategy: 'GM Agent coordinating specialized agents',
          requirements: {
            ...analysis,
            gmTriggered: true,
            triggerReasons: triggerResult.reasons
          },
          scores: [
            { id: gmAgent.id, score: 100, isGM: true },
            ...scoredAgents.map(s => ({ id: s.agent.id, score: s.score, isGM: false }))
          ]
        };
      }
    }
    
    // Original routing logic continues if not triggered
`;

// Usage instructions:
// 1. Read agent-router.js
// 2. Insert the GM_INTEGRATION_PATCH constant at line ~10 (after this.taskKeywords = {...})
// 3. Insert trigger check in route method at line ~283 (before task analysis):
//    const triggerResult = this.gmTrigger.shouldTriggerGM(task, {});
//    if (triggerResult.triggered) { /* route to GM Agent */ }
// 4. Add GM Agent to agents list in loadAgents method
