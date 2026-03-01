#!/usr/bin/env python3
"""
ClawOS Health Report Generator
Combines all health check results into a comprehensive report.

Output: JSON and Markdown reports to clawos/blackboard/persistence/health-reports/
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


def load_check_result(check_name: str) -> dict[str, Any] | None:
    """Load a previous check result from JSON file."""
    report_path = REPORTS_DIR / f"{check_name}.json"
    if report_path.exists():
        try:
            return json.loads(report_path.read_text())
        except json.JSONDecodeError:
            return None
    return None


def calculate_overall_health(
    nodes: dict[str, Any] | None,
    blackboard: dict[str, Any] | None,
    timeouts: dict[str, Any] | None,
) -> dict[str, Any]:
    """Calculate overall system health score."""

    health_score = 100.0
    issues = []

    # Nodes health (40% weight)
    if nodes:
        if not nodes.get("healthy", False):
            node_penalty = min(20, nodes.get("unhealthy_count", 0) * 5)
            health_score -= node_penalty
            issues.extend(nodes.get("critical_issues", []))

        if nodes.get("heartbeat", {}).get("stale"):
            health_score -= 10
            issues.append("Heartbeat is stale")
    else:
        health_score -= 20
        issues.append("Node check failed")

    # Blackboard health (30% weight)
    if blackboard:
        if not blackboard.get("healthy", False):
            health_score -= 15
            issues.extend(blackboard.get("critical_issues", []))
    else:
        health_score -= 15
        issues.append("Blackboard check failed")

    # Timeouts health (30% weight)
    if timeouts:
        if not timeouts.get("healthy", False):
            timeout_penalty = min(20, len(timeouts.get("timed_out_tasks", [])) * 5)
            stuck_penalty = min(10, len(timeouts.get("stuck_tasks", [])) * 3)
            health_score -= timeout_penalty + stuck_penalty
            issues.extend(timeouts.get("critical_issues", []))
    else:
        health_score -= 15
        issues.append("Timeout check failed")

    health_score = max(0, min(100, health_score))

    # Determine status
    if health_score >= 90:
        status = "healthy"
        status_emoji = "🟢"
    elif health_score >= 70:
        status = "degraded"
        status_emoji = "🟡"
    elif health_score >= 50:
        status = "warning"
        status_emoji = "🟠"
    else:
        status = "critical"
        status_emoji = "🔴"

    return {
        "score": round(health_score, 1),
        "status": status,
        "status_emoji": status_emoji,
        "issues": issues,
        "is_critical": health_score < 50,
    }


def generate_markdown_report(
    overall: dict[str, Any],
    nodes: dict[str, Any] | None,
    blackboard: dict[str, Any] | None,
    timeouts: dict[str, Any] | None,
) -> str:
    """Generate a Markdown formatted health report."""
    now = datetime.now(tz=timezone.utc)

    lines = [
        f"# ClawOS Health Report",
        f"",
        f"**Generated**: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"",
        f"## Overall Status: {overall['status_emoji']} {overall['status'].upper()}",
        f"",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Health Score | **{overall['score']}** / 100 |",
        f"| Status | {overall['status']} |",
        f"",
    ]

    # Issues section
    if overall["issues"]:
        lines.extend(
            [
                f"### ⚠️ Issues Detected",
                f"",
            ]
        )
        for issue in overall["issues"]:
            lines.append(f"- {issue}")
        lines.append("")

    # Nodes section
    lines.extend(
        [
            f"## 🤖 Nodes Status",
            f"",
        ]
    )

    if nodes:
        tier_summary = nodes.get("tier_summary", {})
        lines.extend(
            [
                f"| Tier | Healthy | Total |",
                f"|------|---------|-------|",
                f"| Command | {tier_summary.get('command', {}).get('healthy', 0)} | {tier_summary.get('command', {}).get('total', 0)} |",
                f"| PM | {tier_summary.get('pm', {}).get('healthy', 0)} | {tier_summary.get('pm', {}).get('total', 0)} |",
                f"| Worker | {tier_summary.get('worker', {}).get('healthy', 0)} | {tier_summary.get('worker', {}).get('total', 0)} |",
                f"",
                f"**Heartbeat**: {'✅ Active' if nodes.get('heartbeat', {}).get('healthy') else '❌ Stale/Missing'}",
                f"",
            ]
        )

        # List unhealthy nodes
        unhealthy_nodes = [n for n in nodes.get("nodes", []) if not n.get("healthy")]
        if unhealthy_nodes:
            lines.append("**Unhealthy Nodes**:")
            lines.append("")
            for node in unhealthy_nodes:
                missing = node.get("missing_files", [])
                lines.append(
                    f"- `{node['name']}`: missing {', '.join(missing) if missing else 'unknown issue'}"
                )
            lines.append("")
    else:
        lines.append("*Node check data not available*")
        lines.append("")

    # Blackboard section
    lines.extend(
        [
            f"## 📋 Blackboard Integrity",
            f"",
        ]
    )

    if blackboard:
        dir_status = (
            "✅" if blackboard.get("directory_structure", {}).get("healthy") else "❌"
        )
        file_status = (
            "✅" if blackboard.get("required_files", {}).get("healthy") else "❌"
        )
        schema_status = (
            "✅" if blackboard.get("json_schemas", {}).get("healthy") else "❌"
        )

        lines.extend(
            [
                f"| Check | Status |",
                f"|-------|--------|",
                f"| Directory Structure | {dir_status} |",
                f"| Required Files | {file_status} |",
                f"| JSON Schemas | {schema_status} |",
                f"",
            ]
        )

        missing = blackboard.get("required_files", {}).get("missing", [])
        if missing:
            lines.append(
                f"**Missing Files**: {', '.join(missing[:5])}{'...' if len(missing) > 5 else ''}"
            )
            lines.append("")
    else:
        lines.append("*Blackboard check data not available*")
        lines.append("")

    # Timeouts section
    lines.extend(
        [
            f"## ⏱️ Task Timeouts",
            f"",
        ]
    )

    if timeouts:
        timed_out = timeouts.get("timed_out_tasks", [])
        stuck = timeouts.get("stuck_tasks", [])

        lines.extend(
            [
                f"| Metric | Count |",
                f"|--------|-------|",
                f"| Tasks Checked | {timeouts.get('tasks_checked', 0)} |",
                f"| Timed Out | {len(timed_out)} |",
                f"| Stuck | {len(stuck)} |",
                f"",
            ]
        )

        if timed_out:
            lines.append("**Timed Out Tasks**:")
            lines.append("")
            for task in timed_out[:5]:
                lines.append(
                    f"- `{task['task_id']}`: {task['elapsed_hours']}h elapsed (limit: {task['timeout_hours']}h)"
                )
            if len(timed_out) > 5:
                lines.append(f"- ... and {len(timed_out) - 5} more")
            lines.append("")
    else:
        lines.append("*Timeout check data not available*")
        lines.append("")

    # Footer
    lines.extend(
        [
            "---",
            f"*ClawOS 2026.3 | Health Check System*",
        ]
    )

    return "\n".join(lines)


def generate_health_report() -> dict[str, Any]:
    """Main function to generate comprehensive health report."""
    now = datetime.now(tz=timezone.utc)

    # Load individual check results
    nodes = load_check_result("nodes-check")
    blackboard = load_check_result("blackboard-check")
    timeouts = load_check_result("timeout-check")

    # Calculate overall health
    overall = calculate_overall_health(nodes, blackboard, timeouts)

    # Build comprehensive report
    report = {
        "timestamp": now.isoformat(),
        "version": "2026.3",
        "overall": overall,
        "nodes": {
            "healthy": nodes.get("healthy", False) if nodes else None,
            "healthy_count": nodes.get("healthy_count", 0) if nodes else 0,
            "unhealthy_count": nodes.get("unhealthy_count", 0) if nodes else 0,
            "total_nodes": nodes.get("total_nodes", 0) if nodes else 0,
            "heartbeat_healthy": nodes.get("heartbeat", {}).get("healthy", False)
            if nodes
            else False,
            "tier_summary": nodes.get("tier_summary", {}) if nodes else {},
        }
        if nodes
        else None,
        "blackboard": {
            "healthy": blackboard.get("healthy", False) if blackboard else None,
            "directories_ok": blackboard.get("directory_structure", {}).get(
                "healthy", False
            )
            if blackboard
            else False,
            "files_ok": blackboard.get("required_files", {}).get("healthy", False)
            if blackboard
            else False,
            "schemas_ok": blackboard.get("json_schemas", {}).get("healthy", False)
            if blackboard
            else False,
        }
        if blackboard
        else None,
        "timeouts": {
            "healthy": timeouts.get("healthy", False) if timeouts else None,
            "tasks_checked": timeouts.get("tasks_checked", 0) if timeouts else 0,
            "timed_out_count": len(timeouts.get("timed_out_tasks", []))
            if timeouts
            else 0,
            "stuck_count": len(timeouts.get("stuck_tasks", [])) if timeouts else 0,
            "by_status": timeouts.get("by_status", {}) if timeouts else {},
        }
        if timeouts
        else None,
        "critical_issues": overall["issues"],
    }

    # Generate Markdown report
    markdown = generate_markdown_report(overall, nodes, blackboard, timeouts)

    return report, markdown, overall


def main():
    """Generate health report and save outputs."""
    # Ensure reports directory exists
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    report, markdown, overall = generate_health_report()

    # Save JSON report
    json_path = REPORTS_DIR / "latest.json"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")

    # Save Markdown report
    md_path = REPORTS_DIR / "latest.md"
    md_path.write_text(markdown)

    # Save timestamped copy
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d-%H%M%S")
    archived_json = REPORTS_DIR / f"health-{timestamp}.json"
    archived_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")

    # Output summary to stdout
    print(
        json.dumps(
            {
                "ok": overall["score"] >= 50,
                "health_score": overall["score"],
                "status": overall["status"],
                "status_emoji": overall["status_emoji"],
                "critical": overall["is_critical"],
                "critical_issues_count": len(overall["issues"]),
                "timestamp": report["timestamp"],
            },
            ensure_ascii=False,
        )
    )

    # Set GitHub Actions output
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"critical={str(overall['is_critical']).lower()}\n")
            f.write(f"health_score={overall['score']}\n")
            f.write(f"status={overall['status']}\n")

    # Exit with error if critical
    if overall["is_critical"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
