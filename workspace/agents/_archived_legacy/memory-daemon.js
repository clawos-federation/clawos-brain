#!/usr/bin/env node

/**
 * OpenClaw Memory & Evolution Daemon (Orchestration 5.0)
 * 
 * Capabilities:
 * 1. Sync Memory (Every 30 mins)
 * 2. Weekly Evolution Pulse (Every Monday or on Demand)
 */

const { exec } = require('child_process');
const path = require('path');

const SYNC_SCRIPT = path.join(__dirname, 'sync-memory.js');
const SCOUT_SCRIPT = path.join(__dirname, 'weekly-scout.js');
const INTERVAL = 30 * 60 * 1000; // 30 minutes

let lastScoutRun = 0;

function runHeartbeat() {
  const now = new Date();
  console.log(`[${now.toLocaleTimeString()}] 💓 System Heartbeat...`);

  // 1. Memory Sync (Always)
  exec(`node "${SYNC_SCRIPT}"`, (error, stdout) => {
    if (stdout && stdout.trim().length > 0) console.log(stdout.trim());
  });

  // 2. Evolution Pulse (Weekly on Monday 9AM, or if forced via ENV)
  const isMondayMorning = now.getDay() === 1 && now.getHours() === 9;
  const isForced = process.env.FORCE_EVOLUTION === 'true';
  
  if ((isMondayMorning || isForced) && (now.getTime() - lastScoutRun > 3600000)) {
    console.log(`[${now.toLocaleTimeString()}] 🧬 Triggering Evolution Pulse...`);
    exec(`node "${SCOUT_SCRIPT}"`, (error, stdout) => {
      if (stdout) console.log(stdout.trim());
    });
    lastScoutRun = now.getTime();
  }
}

// Initial run
runHeartbeat();

// Set interval
setInterval(runHeartbeat, INTERVAL);

console.log('🚀 Orchestration 5.0 Daemon started. Pulse active.');
