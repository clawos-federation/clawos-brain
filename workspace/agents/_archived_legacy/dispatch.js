/**
 * OpenClaw Dispatch Engine - Evolution 7.4 (Compiler-Driven)
 * 
 * Logic:
 * 1. Physical Execution (Shell/Node)
 * 2. Error Trace Capture
 * 3. Semantic Repair Loop
 */
const { execSync } = require('child_process');
const { PromptEvolver } = require('./prompt-evolver');

class TaskDispatcher {
  constructor(workspacePath = '/Users/henry/openclaw-system/workspace') {
    this.workspacePath = workspacePath;
    this.evolver = new PromptEvolver(workspacePath);
  }

  async dispatch(agent, task) {
    console.log(`[Dispatch 7.4] 🚀 Launching agent: ${agent.id}...`);
    
    let attempts = 0;
    let success = false;
    let lastError = null;

    while (attempts < 3 && !success) {
      attempts++;
      try {
        // In real scenario, this executes the agent's LLM chain
        const result = await agent.run(task);
        
        // Simulate checking for physical errors (e.g. file not created)
        if (result.status === 'ERROR') throw new Error(result.error);
        
        console.log(`[Dispatch 7.4] ✅ Task success on attempt ${attempts}.`);
        success = true;
        return result;

      } catch (e) {
        lastError = e.message;
        console.log(`[Dispatch 7.4] ⚠️ Error on attempt ${attempts}: ${lastError}`);
        
        // 🧬 Semantic Repair: Evolve the agent's prompt based on the error
        await this.evolver.evolve(
          agent.id, 
          'Current Prompt...', 
          lastError, 
          'Fix this specific error logic.'
        );
      }
    }

    console.log(`[Dispatch 7.4] 🔴 Task failed after 3 attempts.`);
    return { status: 'FAILED', error: lastError };
  }
}

module.exports = { TaskDispatcher };
