#!/bin/bash

# OpenClaw Orchestration 6.1 - One-Click Coronation Script
# Created by GM (General Manager)

set -e

echo "🏛️  Welcome to the OpenClaw Empire (Orchestration 6.1)"
echo "----------------------------------------------------"

# 1. Establish the Single Source of Truth (Symlink)
echo "🔗 Harmonizing directory structure..."
if [ -d "$HOME/openclaw-system/agents" ] && [ ! -L "$HOME/openclaw-system/agents" ]; then
    echo "   ⚠️ Found legacy agents directory. Backing it up..."
    mv "$HOME/openclaw-system/agents" "$HOME/openclaw-system/agents_legacy_$(date +%s)"
fi
ln -sfn "$HOME/openclaw-system/workspace/agents" "$HOME/openclaw-system/agents"
echo "   ✅ Symlink established: agents -> workspace/agents"

# 2. Reconstruct the Power Grid (Dependencies)
echo "📦 Reconstructing the environment..."
cd "$HOME/openclaw-system/workspace/agents"
npm install --no-audit --no-fund
npx playwright install chromium
echo "   ✅ Node.js environment restored."

# 3. Ignite the Pulse (Daemons)
echo "💓 Starting background guardians..."
node system-manager.js
echo "   ✅ Heartbeat, Voice, and Guardian are now ACTIVE."

# 4. Final Verification
echo "🛡️  Running Imperial Self-Audit..."
node agent-router.js stats
echo "----------------------------------------------------"
echo "🎉 SUCCESS: Your Empire has been restored to Orchestration 6.1."
echo "Henry is waiting for you in the WebUI. Command at will."
