#!/usr/bin/env node
/**
 * System Manager - Ultimate Edition
 * 
 * Features:
 * - Advanced flock file locking with process identity
 * - Automatic crash detection and restart (Watchdog)
 * - Dynamic path resolution (no hardcoding)
 * - Exponential backoff for restarts
 * - Process group isolation
 * - Clean shutdown handling
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

// =============================================================================
// DYNAMIC PATH RESOLUTION (No Hardcoding)
// =============================================================================

const WORKSPACE = __dirname;
const CONFIG_DIR = path.join(WORKSPACE, '.manager-config');
const PID_DIR = path.join(WORKSPACE, '.pids');
const LOG_DIR = path.join(WORKSPACE, '.manager-logs');

// Ensure directories exist
[CONFIG_DIR, PID_DIR, LOG_DIR].forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
});

// Process identity for lock files (includes hostname + timestamp)
const PROCESS_ID = `${os.hostname()}-${process.pid}-${Date.now()}`;

// =============================================================================
// ADVANCED FILE LOCK MECHANISM (Enhanced Flock)
// =============================================================================

class FileLock {
  constructor(lockName, options = {}) {
    this.lockName = lockName;
    this.lockFile = path.join(PID_DIR, `${lockName}.lock`);
    this.identityFile = path.join(PID_DIR, `${lockName}.identity`);
    this.maxAge = options.maxAge || 5 * 60 * 1000; // 5 minutes default
    this.held = false;
  }

  /**
   * Acquire lock with enhanced safety
   * Returns: { acquired: boolean, stale: boolean, identity: string }
   */
  acquire() {
    try {
      // Step 1: Check for stale lock
      if (fs.existsSync(this.identityFile)) {
        try {
          const identity = fs.readFileSync(this.identityFile, 'utf8');
          const [hostname, pid, timestamp] = identity.split('-');
          const lockAge = Date.now() - parseInt(timestamp);
          
          if (lockAge > this.maxAge) {
            console.log(`[Lock] ${this.lockName}: Found stale lock (${lockAge}ms old), cleaning...`);
            this.release();
          } else {
            // Check if process is actually alive
            const alive = this._isProcessAlive(parseInt(pid));
            if (alive) {
              console.log(`[Lock] ${this.lockName}: Active instance running (pid:${pid})`);
              return { acquired: false, stale: false, identity };
            }
            // Stale: process not running but lock exists
            console.log(`[Lock] ${this.lockName}: Process ${pid} died, cleaning stale lock`);
            this.release();
          }
        } catch (e) {
          console.warn(`[Lock] ${this.lockName}: Failed to read identity: ${e.message}`);
          this.release();
        }
      }

      // Step 2: Try atomic lock creation
      const fd = fs.openSync(this.lockFile, 'wx'); // 'wx' = exclusive create
      fs.writeSync(fd, PROCESS_ID);
      fs.closeSync(fd);

      // Step 3: Write identity file for tracking
      fs.writeFileSync(this.identityFile, PROCESS_ID);

      this.held = true;
      console.log(`[Lock] ${this.lockName}: Acquired (${PROCESS_ID})`);
      return { acquired: true, stale: false, identity: PROCESS_ID };

    } catch (e) {
      if (e.code === 'EEXIST') {
        console.log(`[Lock] ${this.lockName}: Lock contested, waiting...`);
        return { acquired: false, stale: false };
      }
      console.error(`[Lock] ${this.lockName}: Error:`, e.message);
      return { acquired: false, stale: false, error: e.message };
    }
  }

  /**
   * Release lock safely
   */
  release() {
    if (!this.held) return;

    try {
      if (fs.existsSync(this.lockFile)) {
        fs.unlinkSync(this.lockFile);
      }
    } catch (e) {
      console.warn(`[Lock] ${this.lockName}: Cleanup error: ${e.message}`);
    }

    try {
      if (fs.existsSync(this.identityFile)) {
        fs.unlinkSync(this.identityFile);
      }
    } catch (e) {
      console.warn(`[Lock] ${this.lockName}: Identity cleanup error: ${e.message}`);
    }

    this.held = false;
    console.log(`[Lock] ${this.lockName}: Released`);
  }

  /**
   * Check if process is alive (cross-platform)
   */
  _isProcessAlive(pid) {
    try {
      process.kill(pid, 0); // Signal 0 doesn't kill, just check
      return true;
    } catch (e) {
      return false;
    }
  }
}

// =============================================================================
// WATCHDOG - Automatic Crash Detection & Restart
// =============================================================================

class Watchdog {
  constructor(daemon, options = {}) {
    this.daemon = daemon;
    this.child = null;
    this.pidFile = path.join(PID_DIR, `${daemon.name.toLowerCase()}.pid`);
    this.lock = new FileLock(daemon.name, { maxAge: options.maxAge });
    this.maxRestarts = options.maxRestarts || 5;
    this.backoffMs = options.initialBackoff || 5000;
    this.maxBackoffMs = options.maxBackoff || 60000;
    this.restartCount = 0;
    this.crashThreshold = options.crashThreshold || 30000; // 30 seconds
    this.startTime = null;
    this.checkInterval = options.checkInterval || 5000;
    this.monitor = null;
    this.running = false;
  }

  /**
   * Start daemon with watchdog
   */
  start() {
    if (this.running) {
      console.warn(`[Watchdog] ${this.daemon.name}: Already running`);
      return;
    }

    // Try to acquire lock
    const lockResult = this.lock.acquire();
    if (!lockResult.acquired) {
      console.warn(`[Watchdog] ${this.daemon.name}: Skipping (lock not acquired)`);
      return false;
    }

    // Check for stale PID
    this._handleStalePid();

    // Start the daemon
    this._spawnDaemon();
    this.running = true;

    // Start monitoring
    this._startMonitoring();
    
    return true;
  }

  /**
   * Stop daemon and watchdog
   */
  stop() {
    this.running = false;
    
    // Stop monitoring
    if (this.monitor) {
      clearInterval(this.monitor);
      this.monitor = null;
    }

    // Kill child process
    if (this.child) {
      console.log(`[Watchdog] ${this.daemon.name}: Stopping child (pid:${this.child.pid})...`);
      try {
        // Kill process group
        process.kill(-this.child.pid, 'SIGTERM');
      } catch (e) {
        // Already dead
      }
      
      // Clean PID file
      this._cleanPid();
    }

    // Release lock
    this.lock.release();
  }

  /**
   * Spawn daemon process
   */
  _spawnDaemon() {
    this.startTime = Date.now();
    
    try {
      console.log(`[Watchdog] ${this.daemon.name}: Spawning (attempt ${this.restartCount + 1})...`);
      
      this.child = spawn(this.daemon.command, this.daemon.args, {
        cwd: WORKSPACE,
        detached: true,
        stdio: 'ignore',
        env: { ...process.env, OPENCLAW_DAEMON: this.daemon.name }
      });

      // Wait a bit and verify it's alive
      setTimeout(() => {
        if (!this._isChildAlive()) {
          console.error(`[Watchdog] ${this.daemon.name}: Failed to start, cleaning up.`);
          this._handleCrash();
          return;
        }

        // Child is alive, write PID
        fs.writeFileSync(this.pidFile, this.child.pid.toString());
        this.child.unref();
        
        console.log(`[Watchdog] ${this.daemon.name}: Started (pid:${this.child.pid})`);
        this.restartCount = 0; // Reset restart count on success
        this.backoffMs = 5000; // Reset backoff
        
      }, 500); // 500ms verification window

    } catch (e) {
      console.error(`[Watchdog] ${this.daemon.name}: Spawn error:`, e.message);
      this._handleCrash();
    }
  }

  /**
   * Start monitoring interval
   */
  _startMonitoring() {
    this.monitor = setInterval(() => {
      if (!this.running) return;
      this._checkHealth();
    }, this.checkInterval);
  }

  /**
   * Check daemon health
   */
  _checkHealth() {
    if (!this._isChildAlive()) {
      console.warn(`[Watchdog] ${this.daemon.name}: Process died (pid:${this.child?.pid})`);
      this._handleCrash();
    }
  }

  /**
   * Handle daemon crash
   */
  _handleCrash() {
    if (this.restartCount >= this.maxRestarts) {
      console.error(`[Watchdog] ${this.daemon.name}: Max restarts (${this.maxRestarts}) reached, stopping.`);
      this.stop();
      return;
    }

    const uptime = this.startTime ? (Date.now() - this.startTime) : 0;
    
    // If uptime is too short (< crashThreshold), it's likely a crash
    if (uptime < this.crashThreshold) {
      console.error(`[Watchdog] ${this.daemon.name}: Detected crash (uptime:${uptime}ms)`);
    } else {
      // Normal exit
      console.log(`[Watchdog] ${this.daemon.name}: Process exited normally (uptime:${uptime}ms)`);
    }

    this.restartCount++;
    
    // Apply exponential backoff
    const backoffDelay = Math.min(this.backoffMs * Math.pow(2, this.restartCount - 1), this.maxBackoffMs);
    console.log(`[Watchdog] ${this.daemon.name}: Restarting in ${backoffDelay}ms...`);

    this._cleanPid();
    
    setTimeout(() => {
      if (this.running) {
        this._spawnDaemon();
      }
    }, backoffDelay);
  }

  /**
   * Clean PID file
   */
  _cleanPid() {
    try {
      if (fs.existsSync(this.pidFile)) {
        fs.unlinkSync(this.pidFile);
      }
    } catch (e) {
      console.warn(`[Watchdog] PID cleanup error: ${e.message}`);
    }
  }

  /**
   * Handle stale PID files
   */
  _handleStalePid() {
    if (fs.existsSync(this.pidFile)) {
      try {
        const oldPid = parseInt(fs.readFileSync(this.pidFile, 'utf8'));
        const alive = this._isProcessAlive(oldPid);
        
        if (!alive) {
          console.log(`[Watchdog] ${this.daemon.name}: Found stale PID file (pid:${oldPid}), cleaning...`);
          this._cleanPid();
        }
      } catch (e) {
        console.warn(`[Watchdog] ${this.daemon.name}: Stale PID check failed: ${e.message}`);
        this._cleanPid();
      }
    }
  }

  /**
   * Check if child process is alive
   */
  _isChildAlive() {
    if (!this.child || !this.child.pid) return false;
    
    try {
      process.kill(this.child.pid, 0);
      return true;
    } catch (e) {
      return false;
    }
  }
}

// =============================================================================
// DAEMON CONFIGURATION
// =============================================================================

const DAEMONS = [
  {
    name: 'Pulse',
    command: 'node',
    args: ['./memory-daemon.js'],
    options: {
      maxRestarts: 10,
      initialBackoff: 3000,
      crashThreshold: 5000,
      checkInterval: 3000
    }
  },
  {
    name: 'Voice',
    command: 'node',
    args: ['./henry-broadcaster.js'],
    options: {
      maxRestarts: 5,
      initialBackoff: 5000,
      crashThreshold: 10000,
      checkInterval: 5000
    }
  },
  {
    name: 'Guardian',
    command: 'node',
    args: ['./empire-guardian.js'],
    options: {
      maxRestarts: 3,
      initialBackoff: 10000,
      crashThreshold: 30000,
      checkInterval: 10000
    }
  }
];

// =============================================================================
// CLEAN SHUTDOWN HANDLING
// =============================================================================

const watchdogs = [];

function shutdown() {
  console.log('\n[System Manager] Received shutdown signal, stopping all daemons...');
  
  watchdogs.forEach(w => {
    if (w.running) {
      console.log(`  - Stopping ${w.daemon.name}...`);
      w.stop();
    }
  });

  setTimeout(() => {
    console.log('[System Manager] All daemons stopped. Goodbye!');
    process.exit(0);
  }, 2000);
}

process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);
process.on('SIGHUP', shutdown);

// =============================================================================
// INITIALIZATION
// =============================================================================

console.log('╔══════════════════════════════════════════════════════════════════╗');
console.log('║        SYSTEM MANAGER v2.0 - ULTIMATE EDITION                        ║');
console.log('║  Features: Enhanced Flock | Watchdog | Dynamic Paths                    ║');
console.log('╚══════════════════════════════════════════════════════════════════╝');
console.log(`Workspace: ${WORKSPACE}`);
console.log(`Process ID: ${PROCESS_ID}`);
console.log('');

// Start all daemons
DAEMONS.forEach(daemon => {
  const watchdog = new Watchdog(daemon, daemon.options);
  
  if (watchdog.start()) {
    watchdogs.push(watchdog);
  }
});

console.log(`\n✅ System Manager Started (${watchdogs.length} daemons active)`);
console.log('   Type: Process-isolated with Watchdog');
console.log(`   PID Directory: ${PID_DIR}`);
console.log(`   Log Directory: ${LOG_DIR}`);
console.log('   Press Ctrl+C to stop');
console.log('');
