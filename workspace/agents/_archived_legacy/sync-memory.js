#!/usr/bin/env node

/**
 * OpenClaw Memory Sync Engine (Orchestration 2.2+)
 * 
 * Automatically scans recent logs, extracts key facts,
 * and appends them to durable memory files.
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = '/Users/henry/openclaw-system/workspace';
const LOGS_DIR = path.join(WORKSPACE, 'agents', 'logs');
const MEMORY_DIR = path.join(process.cwd(), 'memory');
const SYNC_STATE_FILE = path.join(WORKSPACE, 'agents', 'sync_state.json');

// Ensure directory exists
if (!fs.existsSync(MEMORY_DIR)) fs.mkdirSync(MEMORY_DIR, { recursive: true });

function loadSyncState() {
  if (fs.existsSync(SYNC_STATE_FILE)) {
    try {
      return JSON.parse(fs.readFileSync(SYNC_STATE_FILE, 'utf8'));
    } catch (e) {
      return { lastProcessedTime: 0 };
    }
  }
  return { lastProcessedTime: 0 };
}

function saveSyncState(state) {
  fs.writeFileSync(SYNC_STATE_FILE, JSON.stringify(state, null, 2));
}

async function sync() {
  console.log('🔄 Starting Memory Sync...');
  const state = loadSyncState();
  const now = Date.now();
  
  if (!fs.existsSync(LOGS_DIR)) {
    console.log('⚠️ No logs found to sync.');
    return;
  }

  const files = fs.readdirSync(LOGS_DIR)
    .filter(f => f.endsWith('.log'))
    .map(f => ({
      name: f,
      path: path.join(LOGS_DIR, f),
      mtime: fs.statSync(path.join(LOGS_DIR, f)).mtimeMs
    }))
    .filter(f => f.mtime > state.lastProcessedTime)
    .sort((a, b) => a.mtime - b.mtime);

  if (files.length === 0) {
    console.log('✅ Memory is already up to date.');
    return;
  }

  console.log(`📝 Processing ${files.length} new log entries...`);
  
  let facts = [];
  for (const file of files) {
    try {
      const data = JSON.parse(fs.readFileSync(file.path, 'utf8'));
      if (data.success && data.task) {
        facts.push(`- [${new Date(data.timestamp).toLocaleTimeString()}] **Task**: ${data.task}`);
        if (data.metadata?.model) facts.push(`  - *Model*: ${data.metadata.model}`);
        if (data.metadata?.agents) facts.push(`  - *Agents*: ${data.metadata.agents.join(', ')}`);
      }
    } catch (e) { /* skip */ }
  }

  if (facts.length > 0) {
    const today = new Date().toISOString().split('T')[0];
    const memoryFile = path.join(MEMORY_DIR, `${today}.md`);
    const header = `\n\n### 自动同步记忆 (${new Date().toLocaleTimeString()})\n`;
    fs.appendFileSync(memoryFile, header + facts.join('\n') + '\n');
    console.log(`💾 Persisted ${facts.length} facts to ${memoryFile}`);
  }

  saveSyncState({ lastProcessedTime: now });
  console.log('✨ Sync complete.');
}

sync().catch(console.error);
