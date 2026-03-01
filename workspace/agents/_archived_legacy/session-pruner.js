#!/usr/bin/env node

/**
 * OpenClaw Session Pruner (WebUI Taming)
 * 
 * Logic: Moves large or old session files to an archive to keep the UI snappy.
 */

const fs = require('fs');
const path = require('path');

const SESSION_DIR = '/Users/henry/openclaw-system/agents/main/sessions';
const ARCHIVE_DIR = '/Users/henry/openclaw-system/archive/sessions';

if (!fs.existsSync(ARCHIVE_DIR)) fs.mkdirSync(ARCHIVE_DIR, { recursive: true });

function prune() {
  console.log('✂️  Session Pruner: Scanning for bloat...');
  
  if (!fs.existsSync(SESSION_DIR)) return;

  const files = fs.readdirSync(SESSION_DIR).filter(f => f.endsWith('.jsonl') || f.endsWith('.json'));
  
  files.forEach(file => {
    const fullPath = path.join(SESSION_DIR, file);
    const stats = fs.statSync(fullPath);
    const sizeMB = stats.size / (1024 * 1024);
    const ageDays = (Date.now() - stats.mtimeMs) / (1000 * 60 * 60 * 24);

    // Prune if session is > 5MB OR older than 3 days
    if (sizeMB > 5 || ageDays > 3) {
      console.log(`   📦 Archiving ${file} (${sizeMB.toFixed(2)} MB, ${ageDays.toFixed(1)} days old)`);
      fs.renameSync(fullPath, path.join(ARCHIVE_DIR, file));
    }
  });

  console.log('✅ Pruning complete. WebUI load surface reduced.');
}

prune();
