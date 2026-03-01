#!/usr/bin/env python3
"""
ClawOS Blackboard Integrity Checker
Validates the structure and integrity of the Blackboard system.

Output: JSON report to stdout and clawos/blackboard/persistence/health-reports/
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Configuration
CLAWOS_ROOT = Path(os.environ.get("CLAWOS_ROOT", Path(__file__).parent.parent))
BLACKBOARD_ROOT = CLAWOS_ROOT / "blackboard"
REPORTS_DIR = BLACKBOARD_ROOT / "persistence" / "health-reports"

# Required Blackboard structure
REQUIRED_DIRS = {
    # Core directories
    "tasks": "Task management and status",
    "gm": "GM decisions and escalations",
    "shared": "Shared context between agents",
    "persistence": "Persistent storage and snapshots",
    "errors": "Error logging",
    "logs": "System logs",
    "metrics": "Performance metrics",
    "audit": "Audit records",
    # PM directories
    "coding-pm": "Coding PM workspace",
    "writing-pm": "Writing PM workspace",
    "platform-pm": "Platform PM workspace",
    # Alpha integration
    "alpha": "Alpha quantitative data",
    # Proposals
    "proposals": "System improvement proposals",
}

REQUIRED_FILES = {
    "heartbeat-state.json": "System heartbeat state",
    "tasks/pending.md": "Pending tasks queue",
    "tasks/assigned.md": "Assigned tasks list",
    "tasks/template/task.json": "Task schema template",
    "tasks/template/status.md": "Task status template",
    "gm/status.md": "GM status board",
    "gm/decisions.md": "GM decision log",
    "gm/escalations.md": "GM escalation records",
    "gm/README.md": "GM blackboard documentation",
}

OPTIONAL_DIRS = {
    "assistant": "Assistant agent workspace",
    "alpha/signals": "Alpha trading signals",
    "alpha/reports": "Alpha analysis reports",
    "persistence/snapshots": "State snapshots",
    "persistence/archive": "Archived data",
    "persistence/history": "Historical records",
    "persistence/metrics": "Metrics storage",
    "proposals/self-improvement": "Self-improvement proposals",
    "proposals/skills-proposal": "Skills proposals",
    "proposals/temp-agents": "Temporary agent proposals",
    "proposals/skills-discovery": "Skills discovery proposals",
}

# File size limits (in bytes)
FILE_SIZE_LIMITS = {
    "tasks/pending.md": 100 * 1024,  # 100 KB
    "gm/decisions.md": 10 * 1024 * 1024,  # 10 MB
    "gm/escalations.md": 1 * 1024 * 1024,  # 1 MB
}


def check_directory_structure() -> dict[str, Any]:
    """Check if all required directories exist."""
    result = {
        "required": {},
        "optional": {},
        "missing_required": [],
        "total_required": len(REQUIRED_DIRS),
        "total_optional": len(OPTIONAL_DIRS),
    }

    for dir_name, description in REQUIRED_DIRS.items():
        dir_path = BLACKBOARD_ROOT / dir_name
        exists = dir_path.exists() and dir_path.is_dir()
        result["required"][dir_name] = {
            "exists": exists,
            "description": description,
        }
        if not exists:
            result["missing_required"].append(dir_name)

    for dir_name, description in OPTIONAL_DIRS.items():
        dir_path = BLACKBOARD_ROOT / dir_name
        exists = dir_path.exists() and dir_path.is_dir()
        result["optional"][dir_name] = {
            "exists": exists,
            "description": description,
        }

    result["healthy"] = len(result["missing_required"]) == 0
    return result


def check_required_files() -> dict[str, Any]:
    """Check if all required files exist and are valid."""
    result = {
        "files": {},
        "missing": [],
        "invalid": [],
        "oversized": [],
    }

    for file_path, description in REQUIRED_FILES.items():
        full_path = BLACKBOARD_ROOT / file_path
        file_info = {
            "exists": False,
            "valid": False,
            "size": 0,
            "description": description,
        }

        if full_path.exists() and full_path.is_file():
            file_info["exists"] = True
            file_info["size"] = full_path.stat().st_size

            # Check file size limits
            if file_path in FILE_SIZE_LIMITS:
                if file_info["size"] > FILE_SIZE_LIMITS[file_path]:
                    file_info["oversized"] = True
                    result["oversized"].append(
                        {
                            "path": file_path,
                            "size": file_info["size"],
                            "limit": FILE_SIZE_LIMITS[file_path],
                        }
                    )

            # Validate JSON files
            if file_path.endswith(".json"):
                try:
                    json.loads(full_path.read_text())
                    file_info["valid"] = True
                except json.JSONDecodeError as e:
                    file_info["error"] = str(e)
                    result["invalid"].append(file_path)
            else:
                file_info["valid"] = True
        else:
            result["missing"].append(file_path)

        result["files"][file_path] = file_info

    result["healthy"] = len(result["missing"]) == 0 and len(result["invalid"]) == 0
    return result


def check_json_schemas() -> dict[str, Any]:
    """Validate JSON files against expected schemas."""
    result = {
        "validated": [],
        "errors": [],
    }

    # Validate heartbeat-state.json
    heartbeat_path = BLACKBOARD_ROOT / "heartbeat-state.json"
    if heartbeat_path.exists():
        try:
            data = json.loads(heartbeat_path.read_text())
            required_fields = ["lastChecks", "version"]
            for field in required_fields:
                if field not in data:
                    result["errors"].append(
                        {
                            "file": "heartbeat-state.json",
                            "error": f"Missing required field: {field}",
                        }
                    )
            result["validated"].append("heartbeat-state.json")
        except json.JSONDecodeError as e:
            result["errors"].append(
                {
                    "file": "heartbeat-state.json",
                    "error": str(e),
                }
            )

    # Validate team-assignments.json files
    for pm in ["coding-pm", "writing-pm"]:
        assignments_path = BLACKBOARD_ROOT / pm / "team-assignments.json"
        if assignments_path.exists():
            try:
                data = json.loads(assignments_path.read_text())
                # Basic structure check
                if not isinstance(data, dict):
                    result["errors"].append(
                        {
                            "file": f"{pm}/team-assignments.json",
                            "error": "Expected dict structure",
                        }
                    )
                result["validated"].append(f"{pm}/team-assignments.json")
            except json.JSONDecodeError as e:
                result["errors"].append(
                    {
                        "file": f"{pm}/team-assignments.json",
                        "error": str(e),
                    }
                )

    result["healthy"] = len(result["errors"]) == 0
    return result


def check_write_permissions() -> dict[str, Any]:
    """Check if key directories are writable."""
    result = {
        "writable": [],
        "not_writable": [],
    }

    test_dirs = [
        BLACKBOARD_ROOT / "logs",
        BLACKBOARD_ROOT / "errors",
        BLACKBOARD_ROOT / "persistence",
        BLACKBOARD_ROOT / "tasks",
    ]

    for dir_path in test_dirs:
        if dir_path.exists():
            # Try to create a test file
            test_file = dir_path / ".write_test"
            try:
                test_file.touch()
                test_file.unlink()
                result["writable"].append(str(dir_path.relative_to(BLACKBOARD_ROOT)))
            except PermissionError:
                result["not_writable"].append(
                    str(dir_path.relative_to(BLACKBOARD_ROOT))
                )

    result["healthy"] = len(result["not_writable"]) == 0
    return result


def check_blackboard() -> dict[str, Any]:
    """Main function to check Blackboard integrity."""
    now = datetime.now(tz=timezone.utc)

    results = {
        "timestamp": now.isoformat(),
        "check_type": "blackboard",
        "blackboard_root": str(BLACKBOARD_ROOT),
        "directory_structure": check_directory_structure(),
        "required_files": check_required_files(),
        "json_schemas": check_json_schemas(),
        "write_permissions": check_write_permissions(),
    }

    # Collect critical issues
    results["critical_issues"] = []

    if results["directory_structure"]["missing_required"]:
        results["critical_issues"].append(
            f"Missing required directories: {', '.join(results['directory_structure']['missing_required'])}"
        )

    if results["required_files"]["missing"]:
        results["critical_issues"].append(
            f"Missing required files: {', '.join(results['required_files']['missing'][:3])}"
            + ("..." if len(results["required_files"]["missing"]) > 3 else "")
        )

    if results["required_files"]["invalid"]:
        results["critical_issues"].append(
            f"Invalid JSON files: {', '.join(results['required_files']['invalid'])}"
        )

    # Overall health
    results["healthy"] = (
        results["directory_structure"]["healthy"]
        and results["required_files"]["healthy"]
        and results["json_schemas"]["healthy"]
        and results["write_permissions"]["healthy"]
    )

    return results


def main():
    """Run Blackboard integrity check and output results."""
    # Ensure reports directory exists
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    results = check_blackboard()

    # Write JSON report
    report_path = REPORTS_DIR / "blackboard-check.json"
    report_path.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n")

    # Output to stdout
    print(
        json.dumps(
            {
                "ok": results["healthy"],
                "check_type": "blackboard",
                "timestamp": results["timestamp"],
                "directories_healthy": results["directory_structure"]["healthy"],
                "files_healthy": results["required_files"]["healthy"],
                "schemas_healthy": results["json_schemas"]["healthy"],
                "permissions_healthy": results["write_permissions"]["healthy"],
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
