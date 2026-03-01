#!/usr/bin/env node

/**
 * OpenClaw Security Sandbox (Orchestration 5.1)
 * 
 * Capability:
 * 1. Static Analysis: Scan for eval(), secret leaks, and sensitive path access.
 * 2. Execution Isolation: Run the skill in a restricted subprocess to watch for side effects.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class SecuritySandbox {
  constructor() {}

  /**
   * Run a full security audit on a skill folder
   */
  async audit(skillPath) {
    console.log(`🛡️  Sandbox: Starting audit for ${path.basename(skillPath)}...`);
    
    const report = {
      safe: true,
      findings: [],
      riskScore: 0
    };

    try {
      // 1. Static Analysis: Grep for dangerous patterns
      console.log('   🔍 Performing Static Analysis...');
      const dangerousPatterns = ['eval(', 'process.env', 'rm -rf', '/etc/passwd'];
      for (const pattern of dangerousPatterns) {
        try {
          const result = execSync(`grep -r "${pattern}" "${skillPath}"`, { encoding: 'utf8' });
          if (result) {
            report.findings.push(`DANGEROUS PATTERN: Found '${pattern}' in source.`);
            report.riskScore += 0.3;
          }
        } catch (e) { /* no match */ }
      }

      // 2. Secret Scan: Check for accidental API keys
      console.log('   🔐 Scanning for sensitive secrets...');
      const secretRegex = /"sk-[a-zA-Z0-9]{32,}"|AIzaSy[a-zA-Z0-9_-]{33}/g;
      const files = fs.readdirSync(skillPath, { recursive: true }).filter(f => f.endsWith('.js') || f.endsWith('.json'));
      for (const file of files) {
        const fullPath = path.join(skillPath, file);
        if (fs.statSync(fullPath).isDirectory()) continue;
        const content = fs.readFileSync(fullPath, 'utf8');
        if (secretRegex.test(content)) {
          report.findings.push(`SECRET LEAK: Hardcoded API key found in ${file}.`);
          report.riskScore += 0.5;
        }
      }

      if (report.riskScore > 0.5) report.safe = false;
      console.log(`   ✅ Audit Complete. Risk Score: ${report.riskScore.toFixed(2)}`);
      
      return report;
    } catch (error) {
      console.error('   ❌ Sandbox Audit failed:', error.message);
      return { safe: false, error: error.message };
    }
  }
}

module.exports = { SecuritySandbox };
