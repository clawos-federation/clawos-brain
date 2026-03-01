#!/usr/bin/env python3
"""
ClawOS Node Health Checker
Checks the status of all registered agents/nodes in the system.

Output: JSON report to stdout and clawos/blackboard/persistence/health-reports/
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


# Configuration
CLAWOS_ROOT = Path(os.environ.get("CLAWOS_ROOT", Path(__file__).parent.parent))
BLACKBOARD_ROOT = CLAWOS_ROOT / "blackboard"
REPORTS_DIR = BLACKBOARD_ROOT / "persistence" / "health-reports"

# All registered nodes/agents in ClawOS
REGISTERED_NODES = {
    # Command Layer
    "assistant": {"tier": "command", "model": "glm-5", "required_dirs": ["assistant"]},
    "gm": {"tier": "command", "model": "opus-4-6", "required_dirs": ["gm"]},
    "validator": {
        "tier": "command",
        "model": "opus-4-6",
        "required_dirs": [],
    },  # No dedicated dir
    # PM Layer
    "platform-pm": {"tier": "pm", "model": "glm-5", "required_dirs": ["platform-pm"]},
    "coding-pm": {"tier": "pm", "model": "glm-5", "required_dirs": ["coding-pm"]},
    "writing-pm": {"tier": "pm", "model": "glm-5", "required_dirs": ["writing-pm"]},
    # Workers - Development Group
    "coder-frontend": {"tier": "worker", "group": "dev", "model": "codex-oauth"},
    "coder-backend": {"tier": "worker", "group": "dev", "model": "codex-oauth"},
    "tester-auto": {"tier": "worker", "group": "dev", "model": "codex-oauth"},
    # Workers - Writing Group
    "writer-general": {"tier": "worker", "group": "writing", "model": "glm-5"},
    "researcher-web": {"tier": "worker", "group": "writing", "model": "glm-5"},
    "reviewer-content": {"tier": "worker", "group": "writing", "model": "glm-5"},
    # Workers - System Group
    "sreagent": {"tier": "worker", "group": "system", "model": "codex-oauth"},
    "securityagent": {"tier": "worker", "group": "system", "model": "codex-oauth"},
    "github-ops": {"tier": "worker", "group": "system", "model": "codex-oauth"},
    "alpha-bridge": {"tier": "worker", "group": "system", "model": "glm-5"},
    # Workers - Service Group
    "browser-worker": {"tier": "worker", "group": "service", "model": "glm-5"},
}

# Required status files for each agent
REQUIRED_STATUS_FILES = {
    "gm": ["status.md", "decisions.md"],
    "platform-pm": ["status.md", "decisions.md"],
    "coding-pm": ["status.md", "decisions.md", "team-assignments.json"],
    "writing-pm": ["status.md", "decisions.md", "team-assignments.json"],
}


def check_node_dir(node_name: str, node_config: dict[str, Any]) -> dict[str, Any]:
    """Check if node's required directories exist."""
    result = {
        "name": node_name,
        "tier": node_config.get("tier", "unknown"),
        "model": node_config.get("model", "unknown"),
        "dir_exists": True,
        "status_files": [],
        "missing_files": [],
        "last_updated": None,
        "healthy": True,
    }

    required_dirs = node_config.get("required_dirs", [])
    for dir_name in required_dirs:
        dir_path = BLACKBOARD_ROOT / dir_name
        if not dir_path.exists():
            result["dir_exists"] = False
            result["healthy"] = False
            continue

        # Check required status files
        if dir_name in REQUIRED_STATUS_FILES:
            for status_file in REQUIRED_STATUS_FILES[dir_name]:
                file_path = dir_path / status_file
                if file_path.exists():
                    result["status_files"].append(status_file)
                    mtime = datetime.fromtimestamp(
                        file_path.stat().st_mtime, tz=timezone.utc
                    )
                    if result["last_updated"] is None:
                        result["last_updated"] = mtime
                    elif (
                        isinstance(result["last_updated"], datetime)
                        and mtime > result["last_updated"]
                    ):
                        result["last_updated"] = mtime
                else:
                    result["missing_files"].append(status_file)
                    result["healthy"] = False

    return result


def check_heartbeat() -> dict[str, Any]:
    """Check heartbeat state file."""
    heartbeat_path = BLACKBOARD_ROOT / "heartbeat-state.json"

    result = {
        "exists": False,
        "healthy": False,
        "last_checks": None,
        "stale": False,
    }

    if heartbeat_path.exists():
        result["exists"] = True
        try:
            data = json.loads(heartbeat_path.read_text())
            result["last_checks"] = data.get("lastChecks", {})
            result["version"] = data.get("version", "unknown")
            result["initialized_at"] = data.get("initializedAt")

            # Check if heartbeat is stale (older than 1 hour)
            if result["last_checks"]:
                latest_check = max(result["last_checks"].values())
                now = datetime.now(tz=timezone.utc).timestamp()
                if now - latest_check > 3600:
                    result["stale"] = True
                else:
                    result["healthy"] = True
        except (json.JSONDecodeError, KeyError) as e:
            result["error"] = str(e)
    else:
        result["error"] = "Heartbeat file not found"

    return result


def check_nodes() -> dict[str, Any]:
    """Main function to check all nodes."""
    now = datetime.now(tz=timezone.utc)

    results = {
        "timestamp": now.isoformat(),
        "check_type": "nodes",
        "total_nodes": len(REGISTERED_NODES),
        "healthy_count": 0,
        "unhealthy_count": 0,
        "nodes": [],
        "heartbeat": check_heartbeat(),
        "tier_summary": {
            "command": {"total": 0, "healthy": 0},
            "pm": {"total": 0, "healthy": 0},
            "worker": {"total": 0, "healthy": 0},
        },
    }

    for node_name, node_config in REGISTERED_NODES.items():
        node_result = check_node_dir(node_name, node_config)
        results["nodes"].append(node_result)

        tier = node_result["tier"]
        if tier in results["tier_summary"]:
            results["tier_summary"][tier]["total"] += 1
            if node_result["healthy"]:
                results["tier_summary"][tier]["healthy"] += 1

        if node_result["healthy"]:
            results["healthy_count"] += 1
        else:
            results["unhealthy_count"] += 1

    # Overall health
    results["healthy"] = (
        results["unhealthy_count"] == 0 and results["heartbeat"]["healthy"]
    )

    # Critical issues
    results["critical_issues"] = []
    if not results["heartbeat"]["exists"]:
        results["critical_issues"].append("Heartbeat file missing")
    if results["heartbeat"]["stale"]:
        results["critical_issues"].append("Heartbeat is stale (>1 hour old)")
    if results["unhealthy_count"] > len(REGISTERED_NODES) // 2:
        results["critical_issues"].append(
            f"Majority of nodes unhealthy: {results['unhealthy_count']}/{results['total_nodes']}"
        )

    return results


def main():
    """Run node health check and output results."""
    # Ensure reports directory exists
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    results = check_nodes()

    # Write JSON report
    report_path = REPORTS_DIR / "nodes-check.json"
    report_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2, cls=DateTimeEncoder) + "\n"
    )

    # Output to stdout
    print(
        json.dumps(
            {
                "ok": results["healthy"],
                "check_type": "nodes",
                "timestamp": results["timestamp"],
                "healthy_count": results["healthy_count"],
                "unhealthy_count": results["unhealthy_count"],
                "total_nodes": results["total_nodes"],
                "heartbeat_healthy": results["heartbeat"]["healthy"],
                "heartbeat_stale": results["heartbeat"].get("stale", False),
                "critical_issues": results["critical_issues"],
            },
            ensure_ascii=False,
        )
    )

    # Exit with error if unhealthy
    if not results["healthy"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
