#!/usr/bin/env python3
"""Utility Scorer - Calculate and update agent utility scores

This module calculates composite utility scores for agents based on
validation feedback. Scores are used to:
1. Determine task routing priority
2. Qualify agents for federation memory nomination
3. Track agent performance over time

Score Scale: 0.0 - 1.0
- 0.85+: Eligible for federation memory nomination
- 0.50-0.85: Normal operation
- <0.50: Review required

Usage:
    from scorer import UtilityScorer

    scorer = UtilityScorer()
    score = scorer.calculate_score("coder-frontend")
    if scorer.check_nomination("coder-frontend"):
        print("Agent is eligible for nomination!")
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class ScoreWeights:
    """Weights for utility score calculation."""

    quality: float = 0.30
    completeness: float = 0.25
    efficiency: float = 0.20
    consistency: float = 0.15
    autonomy: float = 0.10


class UtilityScorer:
    """Calculates and manages agent utility scores."""

    # Class-level constants
    WEIGHTS = ScoreWeights()
    NOMINATION_THRESHOLD = 0.85
    WARNING_THRESHOLD = 0.50

    # Score update deltas
    UPDATE_DELTA_HIGH = 0.05  # score >= 8.5 (on 0-10 scale)
    UPDATE_DELTA_LOW = -0.02  # score < 6
    UPDATE_DELTA_NEUTRAL = 0  # 6 <= score < 8.5

    def __init__(
        self, feedback_dir: Optional[Path] = None, scores_dir: Optional[Path] = None
    ):
        """
        Initialize the UtilityScorer.

        Args:
            feedback_dir: Optional custom feedback directory
            scores_dir: Optional custom scores directory
        """
        self.feedback_dir = feedback_dir or Path.home() / "clawos/blackboard/feedback"
        self.scores_dir = scores_dir or Path.home() / "clawos/blackboard/utility-scores"
        self.scores_dir.mkdir(parents=True, exist_ok=True)

    def calculate_score(self, agent_id: str, days: int = 30) -> float:
        """
        Calculate composite utility score from recent feedback.

        The score is calculated as a weighted average of:
        - Quality score (30%)
        - Completeness score (25%)
        - Efficiency score (20%)
        - Pass rate/consistency (15%)
        - Autonomy factor (10% - derived from issue count)

        Args:
            agent_id: Agent identifier to score
            days: Number of days to include (default 30)

        Returns:
            Composite utility score (0.0 - 1.0)
        """
        feedback = self._get_recent_feedback(agent_id, days)

        if not feedback:
            return 0.5  # Default neutral score for new agents

        total = len(feedback)

        # Calculate average scores (normalize from 0-10 to 0-1)
        avg_quality = sum(f["scores"]["quality"] for f in feedback) / total / 10
        avg_complete = sum(f["scores"]["completeness"] for f in feedback) / total / 10
        avg_efficiency = sum(f["scores"]["efficiency"] for f in feedback) / total / 10

        # Pass rate represents consistency
        pass_rate = sum(1 for f in feedback if f["passed"]) / total

        # Autonomy factor: fewer issues = higher autonomy
        avg_issues = sum(len(f.get("issues", [])) for f in feedback) / total
        autonomy = max(0, 1 - (avg_issues * 0.1))  # Each issue reduces autonomy by 0.1

        # Calculate weighted composite score
        score = (
            avg_quality * self.WEIGHTS.quality
            + avg_complete * self.WEIGHTS.completeness
            + avg_efficiency * self.WEIGHTS.efficiency
            + pass_rate * self.WEIGHTS.consistency
            + autonomy * self.WEIGHTS.autonomy
        )

        return round(score, 2)

    def update_score(self, agent_id: str, validation_score: float) -> float:
        """
        Update agent score based on single validation result.

        Uses delta-based updates:
        - Score >= 8.5: +0.05
        - Score < 6: -0.02
        - Otherwise: no change

        Args:
            agent_id: Agent identifier to update
            validation_score: Validation score (0-10 scale)

        Returns:
            New utility score (0.0 - 1.0)
        """
        current = self.get_current_score(agent_id)

        # Determine delta based on validation score
        if validation_score >= 8.5:
            delta = self.UPDATE_DELTA_HIGH
        elif validation_score < 6:
            delta = self.UPDATE_DELTA_LOW
        else:
            delta = self.UPDATE_DELTA_NEUTRAL

        # Apply delta and clamp to valid range
        new_score = max(0.0, min(1.0, current + delta))

        self._save_score(agent_id, new_score)
        return new_score

    def check_nomination(self, agent_id: str) -> bool:
        """
        Check if agent qualifies for auto-nomination to federation memory.

        Args:
            agent_id: Agent identifier to check

        Returns:
            True if agent qualifies for nomination
        """
        return self.calculate_score(agent_id) >= self.NOMINATION_THRESHOLD

    def check_warning(self, agent_id: str) -> bool:
        """
        Check if agent score is in warning zone.

        Args:
            agent_id: Agent identifier to check

        Returns:
            True if agent score is below warning threshold
        """
        return self.get_current_score(agent_id) < self.WARNING_THRESHOLD

    def get_current_score(self, agent_id: str) -> float:
        """
        Get the current stored utility score for an agent.

        Args:
            agent_id: Agent identifier to query

        Returns:
            Current utility score (0.5 if no score exists)
        """
        file_path = self.scores_dir / f"{agent_id}.json"

        if file_path.exists():
            try:
                data = json.loads(file_path.read_text())
                return data.get("utilityScore", 0.5)
            except json.JSONDecodeError:
                return 0.5

        return 0.5

    def get_score_details(self, agent_id: str) -> dict:
        """
        Get detailed score information for an agent.

        Args:
            agent_id: Agent identifier to query

        Returns:
            Dictionary with full score details
        """
        file_path = self.scores_dir / f"{agent_id}.json"

        if file_path.exists():
            try:
                return json.loads(file_path.read_text())
            except json.JSONDecodeError:
                pass

        # Return default structure if no score exists
        return {
            "agentId": agent_id,
            "utilityScore": 0.5,
            "lastUpdated": None,
            "nominationEligible": False,
            "history": [],
        }

    def _save_score(self, agent_id: str, score: float, notes: str = "") -> None:
        """
        Save agent score to file.

        Args:
            agent_id: Agent identifier
            score: Utility score to save
            notes: Optional notes about the update
        """
        file_path = self.scores_dir / f"{agent_id}.json"

        # Load existing data or create new
        if file_path.exists():
            try:
                data = json.loads(file_path.read_text())
            except json.JSONDecodeError:
                data = {"agentId": agent_id, "history": []}
        else:
            data = {"agentId": agent_id, "history": []}

        # Update data
        old_score = data.get("utilityScore", 0.5)
        data["utilityScore"] = score
        data["lastUpdated"] = datetime.now().isoformat()
        data["nominationEligible"] = score >= self.NOMINATION_THRESHOLD

        # Add to history (keep last 30 entries)
        if "history" not in data:
            data["history"] = []

        data["history"].append(
            {
                "timestamp": datetime.now().isoformat(),
                "oldScore": old_score,
                "newScore": score,
                "notes": notes,
            }
        )

        data["history"] = data["history"][-30:]

        file_path.write_text(json.dumps(data, indent=2))

    def _get_recent_feedback(self, agent_id: str, days: int) -> list[dict]:
        """
        Get recent feedback entries for an agent.

        Args:
            agent_id: Agent identifier
            days: Number of days to look back

        Returns:
            List of feedback dictionaries
        """
        cutoff = datetime.now() - timedelta(days=days)
        feedback = []

        for file_path in self.feedback_dir.glob("feedback-*.jsonl"):
            try:
                with open(file_path, "r") as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            if entry.get("agentId") == agent_id:
                                entry_time = datetime.fromisoformat(entry["timestamp"])
                                if entry_time >= cutoff:
                                    feedback.append(entry)
                        except (json.JSONDecodeError, ValueError):
                            continue
            except FileNotFoundError:
                continue

        return feedback

    def get_all_scores(self) -> list[dict]:
        """
        Get scores for all agents with stored scores.

        Returns:
            List of score dictionaries
        """
        scores = []

        for file_path in self.scores_dir.glob("*.json"):
            try:
                data = json.loads(file_path.read_text())
                scores.append(data)
            except json.JSONDecodeError:
                continue

        return sorted(scores, key=lambda x: x.get("utilityScore", 0), reverse=True)

    def get_nomination_candidates(self) -> list[dict]:
        """
        Get all agents eligible for federation memory nomination.

        Returns:
            List of agent dictionaries with nominationEligible=True
        """
        return [s for s in self.get_all_scores() if s.get("nominationEligible", False)]

    def get_warning_agents(self) -> list[dict]:
        """
        Get all agents with scores in warning zone.

        Returns:
            List of agent dictionaries with score < 0.50
        """
        return [
            s
            for s in self.get_all_scores()
            if s.get("utilityScore", 1.0) < self.WARNING_THRESHOLD
        ]


# CLI interface for testing
if __name__ == "__main__":
    import sys

    scorer = UtilityScorer()

    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            scores = scorer.get_all_scores()
            print(json.dumps(scores, indent=2))
        elif sys.argv[1] == "candidates":
            candidates = scorer.get_nomination_candidates()
            print(json.dumps(candidates, indent=2))
        elif sys.argv[1] == "warnings":
            warnings = scorer.get_warning_agents()
            print(json.dumps(warnings, indent=2))
        elif sys.argv[1] == "score":
            agent_id = sys.argv[2] if len(sys.argv) > 2 else "validator"
            score = scorer.calculate_score(agent_id)
            details = scorer.get_score_details(agent_id)
            print(json.dumps(details, indent=2))
        elif sys.argv[1] == "update":
            agent_id = sys.argv[2] if len(sys.argv) > 2 else "coder-frontend"
            val_score = float(sys.argv[3]) if len(sys.argv) > 3 else 8.5
            new_score = scorer.update_score(agent_id, val_score)
            print(f"Updated {agent_id}: {new_score}")
    else:
        # Demo: show all scores
        print("Current agent scores:")
        for score_data in scorer.get_all_scores():
            eligible = "★" if score_data.get("nominationEligible") else " "
            print(
                f"  {eligible} {score_data['agentId']}: {score_data.get('utilityScore', 0):.2f}"
            )
