#!/usr/bin/env python3
"""
ClawOS Task Timeout Checker
Scans for tasks that have exceeded their expected duration or have been
stuck in non-terminal states for too long.

Output: JSON report to stdout and clawos/blackboard/persistence/health-reports/
"""

import json
import os
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

# Configuration
CLAWOS_ROOT = Path(os.environ.get("CLAWOS_ROOT", Path(__file__).parent.parent))
BLACKBOARD_ROOT = CLAWOS_ROOT / "blackboard"
REPORTS_DIR = BLACKBOARD_ROOT / "persistence" / "health-reports"

# Timeout thresholds (in hours)
TIMEOUT_THRESHOLDS = {
    "P0": 1,  # P0 tasks should complete within 1 hour
    "P1": 4,  # P1 tasks should complete within 4 hours
    "P2": 24,  # P2 tasks should complete within 24 hours
    "P3": 72,  # P3 tasks should complete within 72 hours
}

# Default timeout for tasks without priority
DEFAULT_TIMEOUT_HOURS = 24

# Maximum stuck time for each status (in hours)
STUCK_THRESHOLDS = {
    "pending": 4,  # Tasks shouldn't be pending for more than 4 hours
    "planning": 2,  # Planning shouldn't take more than 2 hours
    "executing": 24,  # Execution shouldn't exceed 24 hours without update
    "validating": 4,  # Validation shouldn't take more than 4 hours
}

# Terminal states (not checked for timeout)
TERMINAL_STATES = {"completed", "failed", "cancelled", "archived"}


def parse_datetime(dt_str: str | None) -> datetime | None:
    """Parse various datetime formats."""
    if not dt_str:
        return None

    formats = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(dt_str, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue

    return None


def extract_frontmatter(content: str) -> dict[str, Any]:
    """Extract YAML frontmatter from markdown content."""
    frontmatter = {}

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            yaml_content = parts[1].strip()
            # Simple YAML parsing for common fields
            for line in yaml_content.split("\n"):
                if ":" in line:
                    key, _, value = line.partition(":")
                    frontmatter[key.strip()] = value.strip().strip("\"'")

    return frontmatter


def parse_status_md(content: str) -> dict[str, Any]:
    """Parse status.md content to extract task information."""
    info = {
        "status": None,
        "last_updated": None,
        "progress": None,
    }

    # Extract frontmatter
    frontmatter = extract_frontmatter(content)
    if "status" in frontmatter:
        info["status"] = frontmatter["status"].lower()
    if "last_updated" in frontmatter:
        info["last_updated"] = parse_datetime(frontmatter["last_updated"])

    # Try to extract status from markdown content
    status_match = re.search(r"\*\*Status\*\*:\s*(\w+)", content, re.IGNORECASE)
    if status_match and not info["status"]:
        info["status"] = status_match.group(1).lower()

    # Try to extract last updated from content
    updated_match = re.search(
        r"\*\*Last Updated\*\*:\s*(.+?)(?:\n|$)", content, re.IGNORECASE
    )
    if updated_match and not info["last_updated"]:
        info["last_updated"] = parse_datetime(updated_match.group(1).strip())

    # Extract progress percentage
    progress_match = re.search(
        r"(\d+)%\s*(?:complete|done|progress)", content, re.IGNORECASE
    )
    if progress_match:
        info["progress"] = int(progress_match.group(1))

    return info


def check_task_directory(task_dir: Path) -> dict[str, Any] | None:
    """Check a single task directory for timeout."""
    task_info = {
        "task_id": task_dir.name,
        "path": str(task_dir.relative_to(BLACKBOARD_ROOT)),
        "status": None,
        "priority": None,
        "created_at": None,
        "updated_at": None,
        "timed_out": False,
        "stuck": False,
        "timeout_hours": None,
        "elapsed_hours": None,
        "issues": [],
    }

    # Skip template directory
    if task_dir.name == "template":
        return None

    # Read task.json if exists
    task_json_path = task_dir / "task.json"
    if task_json_path.exists():
        try:
            task_data = json.loads(task_json_path.read_text())
            task_info["status"] = task_data.get("status", "").lower()
            task_info["priority"] = task_data.get("priority", "P2")
            task_info["created_at"] = parse_datetime(task_data.get("createdAt"))
            task_info["updated_at"] = parse_datetime(task_data.get("updatedAt"))
            task_info["title"] = task_data.get("title", "Untitled")
        except (json.JSONDecodeError, KeyError):
            task_info["issues"].append("Invalid task.json")

    # Read status.md for additional info
    status_path = task_dir / "status.md"
    if status_path.exists():
        status_info = parse_status_md(status_path.read_text())
        if status_info["status"] and not task_info["status"]:
            task_info["status"] = status_info["status"]
        if status_info["last_updated"] and not task_info["updated_at"]:
            task_info["updated_at"] = status_info["last_updated"]

    # Skip terminal states
    if task_info["status"] in TERMINAL_STATES:
        return None

    # Set defaults for missing data
    if not task_info["status"]:
        task_info["status"] = "unknown"
    if not task_info["priority"]:
        task_info["priority"] = "P2"

    # Calculate elapsed time
    now = datetime.now(tz=timezone.utc)
    reference_time = task_info["updated_at"] or task_info["created_at"]

    if reference_time:
        elapsed = now - reference_time
        task_info["elapsed_hours"] = elapsed.total_seconds() / 3600

        # Check for timeout based on priority
        timeout_hours = TIMEOUT_THRESHOLDS.get(
            task_info["priority"], DEFAULT_TIMEOUT_HOURS
        )
        task_info["timeout_hours"] = timeout_hours

        if task_info["elapsed_hours"] > timeout_hours:
            task_info["timed_out"] = True
            task_info["issues"].append(
                f"Task exceeded priority timeout ({task_info['priority']}: {timeout_hours}h)"
            )

        # Check for stuck status
        stuck_threshold = STUCK_THRESHOLDS.get(task_info["status"])
        if stuck_threshold and task_info["elapsed_hours"] > stuck_threshold:
            task_info["stuck"] = True
            task_info["issues"].append(
                f"Task stuck in '{task_info['status']}' for {task_info['elapsed_hours']:.1f}h (threshold: {stuck_threshold}h)"
            )

    return task_info


def check_pending_tasks() -> dict[str, Any]:
    """Check pending.md for tasks waiting too long."""
    result = {
        "exists": False,
        "stale_tasks": [],
        "total_pending": 0,
    }

    pending_path = BLACKBOARD_ROOT / "tasks" / "pending.md"
    if not pending_path.exists():
        return result

    result["exists"] = True
    content = pending_path.read_text()

    # Check last updated timestamp
    updated_match = re.search(
        r"\*\*Last Updated\*\*:\s*(.+?)(?:\n|$)", content, re.IGNORECASE
    )
    if updated_match:
        last_updated = parse_datetime(updated_match.group(1).strip())
        if last_updated:
            elapsed = datetime.now(tz=timezone.utc) - last_updated
            result["last_updated_hours_ago"] = elapsed.total_seconds() / 3600

            # Flag if pending.md hasn't been updated in 24 hours
            if elapsed.total_seconds() > 86400:
                result["stale"] = True

    # Count pending tasks (simple heuristic: count table rows)
    # Looking for patterns like | task-id | type | ...
    task_rows = re.findall(r"\|\s*[\w-]+\s*\|", content)
    result["total_pending"] = max(0, len(task_rows) // 4)  # Rough estimate

    return result


def check_timeouts() -> dict[str, Any]:
    """Main function to check for task timeouts."""
    now = datetime.now(tz=timezone.utc)
    tasks_dir = BLACKBOARD_ROOT / "tasks"

    results = {
        "timestamp": now.isoformat(),
        "check_type": "timeouts",
        "tasks_checked": 0,
        "timed_out_tasks": [],
        "stuck_tasks": [],
        "by_status": {},
        "by_priority": {},
        "pending_queue": check_pending_tasks(),
    }

    # Scan task directories
    if tasks_dir.exists():
        for task_dir in tasks_dir.iterdir():
            if not task_dir.is_dir():
                continue

            task_info = check_task_directory(task_dir)
            if task_info is None:
                continue

            results["tasks_checked"] += 1

            # Track by status
            status = task_info["status"]
            if status not in results["by_status"]:
                results["by_status"][status] = 0
            results["by_status"][status] += 1

            # Track by priority
            priority = task_info["priority"]
            if priority not in results["by_priority"]:
                results["by_priority"][priority] = 0
            results["by_priority"][priority] += 1

            # Collect issues
            if task_info["timed_out"]:
                results["timed_out_tasks"].append(
                    {
                        "task_id": task_info["task_id"],
                        "priority": task_info["priority"],
                        "elapsed_hours": round(task_info["elapsed_hours"], 1),
                        "timeout_hours": task_info["timeout_hours"],
                        "status": task_info["status"],
                    }
                )

            if task_info["stuck"]:
                results["stuck_tasks"].append(
                    {
                        "task_id": task_info["task_id"],
                        "status": task_info["status"],
                        "elapsed_hours": round(task_info["elapsed_hours"], 1),
                    }
                )

    # Overall health
    results["healthy"] = (
        len(results["timed_out_tasks"]) == 0
        and len(results["stuck_tasks"]) == 0
        and not results["pending_queue"].get("stale", False)
    )

    # Critical issues
    results["critical_issues"] = []

    if results["timed_out_tasks"]:
        results["critical_issues"].append(
            f"{len(results['timed_out_tasks'])} tasks have exceeded their timeout threshold"
        )

    if results["stuck_tasks"]:
        results["critical_issues"].append(
            f"{len(results['stuck_tasks'])} tasks are stuck in non-progressing states"
        )

    if results["pending_queue"].get("stale"):
        results["critical_issues"].append(
            "Pending queue hasn't been updated in over 24 hours"
        )

    return results


def main():
    """Run timeout check and output results."""
    # Ensure reports directory exists
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    results = check_timeouts()

    # Write JSON report
    report_path = REPORTS_DIR / "timeout-check.json"
    report_path.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n")

    # Output to stdout
    print(
        json.dumps(
            {
                "ok": results["healthy"],
                "check_type": "timeouts",
                "timestamp": results["timestamp"],
                "tasks_checked": results["tasks_checked"],
                "timed_out_count": len(results["timed_out_tasks"]),
                "stuck_count": len(results["stuck_tasks"]),
                "pending_stale": results["pending_queue"].get("stale", False),
                "critical_issues": results["critical_issues"],
                "status_distribution": results["by_status"],
            },
            ensure_ascii=False,
        )
    )

    # Exit with error if unhealthy
    if not results["healthy"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
