#!/usr/bin/env python3
"""Feedback Collector - Collect and process validator feedback

This module handles the collection and storage of validation feedback
from the ClawOS multi-agent system. Feedback is stored as JSONL for
efficient append-only operations.

Usage:
    from feedback import FeedbackCollector

    collector = FeedbackCollector()
    feedback = collector.collect(task_id, agent_id, validation_result)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional


class FeedbackCollector:
    """Collects and persists validation feedback for agents."""

    def __init__(self, feedback_dir: Optional[Path] = None):
        """
        Initialize the FeedbackCollector.

        Args:
            feedback_dir: Optional custom directory for feedback storage.
                         Defaults to ~/clawos/blackboard/feedback/
        """
        self.feedback_dir = feedback_dir or Path.home() / "clawos/blackboard/feedback"
        self.feedback_dir.mkdir(parents=True, exist_ok=True)

    def collect(
        self,
        task_id: str,
        agent_id: str,
        validation_result: dict,
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        Collect feedback from task validation.

        Args:
            task_id: Unique identifier for the task
            agent_id: Agent identifier (e.g., 'coder-frontend', 'validator')
            validation_result: Validation result dictionary with:
                - qualityScore: int (0-10)
                - completenessScore: int (0-10)
                - efficiencyScore: int (0-10)
                - issues: list of issue descriptions
                - notes: validator notes
                - pass: boolean
            metadata: Optional additional metadata

        Returns:
            The constructed feedback dictionary
        """
        feedback = {
            "taskId": task_id,
            "agentId": agent_id,
            "timestamp": datetime.now().isoformat(),
            "scores": {
                "quality": validation_result.get("qualityScore", 0),
                "completeness": validation_result.get("completenessScore", 0),
                "efficiency": validation_result.get("efficiencyScore", 0),
            },
            "issues": validation_result.get("issues", []),
            "validatorNotes": validation_result.get("notes", ""),
            "passed": validation_result.get("pass", False),
        }

        if metadata:
            feedback["metadata"] = metadata

        self._write_feedback(feedback)
        return feedback

    def _write_feedback(self, feedback: dict) -> None:
        """
        Write feedback to JSONL file (append-only).

        Args:
            feedback: The feedback dictionary to write
        """
        date_str = datetime.now().strftime("%Y-%m-%d")
        file_path = self.feedback_dir / f"feedback-{date_str}.jsonl"

        with open(file_path, "a") as f:
            f.write(json.dumps(feedback) + "\n")

    def get_feedback_for_agent(
        self, agent_id: str, days: int = 30, limit: Optional[int] = None
    ) -> list[dict]:
        """
        Retrieve recent feedback for a specific agent.

        Args:
            agent_id: Agent identifier to query
            days: Number of days to look back (default 30)
            limit: Optional limit on number of results

        Returns:
            List of feedback dictionaries, newest first
        """
        feedback = []
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)

        # Read all feedback files from the period
        for file_path in sorted(
            self.feedback_dir.glob("feedback-*.jsonl"), reverse=True
        ):
            try:
                with open(file_path, "r") as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            if entry.get("agentId") == agent_id:
                                entry_time = datetime.fromisoformat(
                                    entry["timestamp"]
                                ).timestamp()
                                if entry_time >= cutoff:
                                    feedback.append(entry)
                        except json.JSONDecodeError:
                            continue
            except FileNotFoundError:
                continue

        if limit:
            feedback = feedback[:limit]

        return feedback

    def get_feedback_for_task(self, task_id: str) -> list[dict]:
        """
        Retrieve all feedback for a specific task.

        Args:
            task_id: Task identifier to query

        Returns:
            List of feedback dictionaries for the task
        """
        feedback = []

        for file_path in self.feedback_dir.glob("feedback-*.jsonl"):
            try:
                with open(file_path, "r") as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            if entry.get("taskId") == task_id:
                                feedback.append(entry)
                        except json.JSONDecodeError:
                            continue
            except FileNotFoundError:
                continue

        return feedback

    def get_summary(self, agent_id: str, days: int = 30) -> dict:
        """
        Get a summary of feedback for an agent.

        Args:
            agent_id: Agent identifier to summarize
            days: Number of days to include

        Returns:
            Summary dictionary with aggregated metrics
        """
        feedback = self.get_feedback_for_agent(agent_id, days)

        if not feedback:
            return {
                "agentId": agent_id,
                "period": f"{days} days",
                "totalTasks": 0,
                "avgQuality": 0,
                "avgCompleteness": 0,
                "avgEfficiency": 0,
                "passRate": 0,
                "totalIssues": 0,
            }

        total = len(feedback)
        avg_quality = sum(f["scores"]["quality"] for f in feedback) / total
        avg_complete = sum(f["scores"]["completeness"] for f in feedback) / total
        avg_efficiency = sum(f["scores"]["efficiency"] for f in feedback) / total
        pass_rate = sum(1 for f in feedback if f["passed"]) / total
        total_issues = sum(len(f.get("issues", [])) for f in feedback)

        return {
            "agentId": agent_id,
            "period": f"{days} days",
            "totalTasks": total,
            "avgQuality": round(avg_quality, 2),
            "avgCompleteness": round(avg_complete, 2),
            "avgEfficiency": round(avg_efficiency, 2),
            "passRate": round(pass_rate, 2),
            "totalIssues": total_issues,
        }


# CLI interface for testing
if __name__ == "__main__":
    import sys

    collector = FeedbackCollector()

    if len(sys.argv) > 1:
        if sys.argv[1] == "summary":
            agent_id = sys.argv[2] if len(sys.argv) > 2 else "validator"
            days = int(sys.argv[3]) if len(sys.argv) > 3 else 30
            summary = collector.get_summary(agent_id, days)
            print(json.dumps(summary, indent=2))
        elif sys.argv[1] == "list":
            agent_id = sys.argv[2] if len(sys.argv) > 2 else None
            if agent_id:
                feedback = collector.get_feedback_for_agent(agent_id)
            else:
                print("Usage: python feedback.py list <agent_id>")
                sys.exit(1)
            print(json.dumps(feedback, indent=2))
    else:
        # Demo: collect sample feedback
        sample_result = {
            "qualityScore": 8,
            "completenessScore": 9,
            "efficiencyScore": 7,
            "issues": ["Minor formatting issue"],
            "notes": "Good work overall",
            "pass": True,
        }
        feedback = collector.collect("demo-task-001", "coder-frontend", sample_result)
        print("Collected feedback:")
        print(json.dumps(feedback, indent=2))
