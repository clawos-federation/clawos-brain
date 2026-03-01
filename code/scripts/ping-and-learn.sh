#!/bin/bash
# ClawOS Heartbeat & Health Check Script
# Runs every 20 minutes via crontab
# Updates heartbeat-state.json and runs health checks

set -e

CLAWOS_ROOT="${CLAWOS_ROOT:-$HOME/openclaw-system/clawos}"
BLACKBOARD_ROOT="${BLACKBOARD_ROOT:-$HOME/clawos/blackboard}"
LOG_FILE="$HOME/clawos/logs/heartbeat.log"
HEARTBEAT_FILE="$BLACKBOARD_ROOT/heartbeat-state.json"
SCRIPTS_DIR="$CLAWOS_ROOT/scripts"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$BLACKBOARD_ROOT"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Get current Unix timestamp
NOW=$(date +%s)
NOW_ISO=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

# Update heartbeat state
update_heartbeat() {
    log "🫀 Updating heartbeat..."
    
    if [ -f "$HEARTBEAT_FILE" ]; then
        # Update existing file preserving other fields
        python3 -c "
import json
from pathlib import Path
import time

hb_file = Path('$HEARTBEAT_FILE')
now = int(time.time())
now_iso = '$NOW_ISO'

try:
    data = json.loads(hb_file.read_text())
except:
    data = {'version': '1.0.0'}

data['lastChecks'] = {
    'blackboard': now,
    'workflows': now,
    'health': now
}
data['lastUpdated'] = now_iso
data['status'] = 'active'

hb_file.write_text(json.dumps(data, indent=2) + '\n')
print('OK')
"
        log "✅ Heartbeat updated: $NOW_ISO"
    else
        # Create new heartbeat file
        cat > "$HEARTBEAT_FILE" << EOF
{
  "lastChecks": {
    "blackboard": $NOW,
    "workflows": $NOW,
    "health": $NOW
  },
  "version": "1.0.0",
  "initializedAt": "$NOW_ISO",
  "lastUpdated": "$NOW_ISO",
  "status": "active"
}
EOF
        log "✅ Heartbeat file created: $NOW_ISO"
    fi
}

# Run health checks
run_health_checks() {
    log "🏥 Running health checks..."
    
    # Run Python health checks if available
    if [ -f "$SCRIPTS_DIR/check_blackboard.py" ]; then
        python3 "$SCRIPTS_DIR/check_blackboard.py" >> "$LOG_FILE" 2>&1 || true
    fi
    
    if [ -f "$SCRIPTS_DIR/check_nodes.py" ]; then
        python3 "$SCRIPTS_DIR/check_nodes.py" >> "$LOG_FILE" 2>&1 || true
    fi
    
    if [ -f "$SCRIPTS_DIR/check_timeouts.py" ]; then
        python3 "$SCRIPTS_DIR/check_timeouts.py" >> "$LOG_FILE" 2>&1 || true
    fi
    
    # Generate health report
    if [ -f "$SCRIPTS_DIR/generate_health_report.py" ]; then
        python3 "$SCRIPTS_DIR/generate_health_report.py" >> "$LOG_FILE" 2>&1 || true
    fi
    
    log "✅ Health checks completed"
}

# Check for critical escalations
check_escalations() {
    ESCALATION_FILE="$BLACKBOARD_ROOT/gm/escalations.md"
    if [ -f "$ESCALATION_FILE" ]; then
        # Check if file has content beyond header
        CONTENT=$(grep -v "^#" "$ESCALATION_FILE" | grep -v "^$" | grep -v "^|" | head -5)
        if [ -n "$CONTENT" ]; then
            log "⚠️  Escalations detected! Check $ESCALATION_FILE"
        fi
    fi
}

# Main
main() {
    log "=== ClawOS Heartbeat Start ==="
    
    update_heartbeat
    run_health_checks
    check_escalations
    
    log "=== ClawOS Heartbeat End ==="
}

main "$@"
