#!/bin/bash

# OpenClaw System Activator (Orchestration 5.3)
# Ensures background daemons survive shell exit.

WORKSPACE="/Users/henry/openclaw-system/workspace/agents"

echo "💓 Activating Memory Daemon..."
nohup node "$WORKSPACE/memory-daemon.js" > /tmp/openclaw_memory_daemon.log 2>&1 &

echo "🎙️ Activating Henry Broadcaster (Async)..."
nohup node "$WORKSPACE/henry-broadcaster.js" > /tmp/henry_broadcast.log 2>&1 &

echo "✅ System Activated. Processes are running in the background."
ps aux | grep -E "memory-daemon|henry-broadcaster" | grep -v grep
