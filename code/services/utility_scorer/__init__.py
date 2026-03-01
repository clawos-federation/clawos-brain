#!/usr/bin/env python3
"""
Utility Scorer Module - ClawOS Agent Performance Tracking

This module provides utilities for:
1. Collecting validation feedback from agents
2. Calculating composite utility scores
3. Managing federation memory nominations

Components:
- FeedbackCollector: Collects and stores validation feedback
- UtilityScorer: Calculates and updates agent scores
- NominationManager: Handles federation memory nominations

Usage:
    from feedback import FeedbackCollector
    from scorer import UtilityScorer
    from nomination import NominationManager

    # Collect feedback
    collector = FeedbackCollector()
    feedback = collector.collect(task_id, agent_id, validation_result)

    # Calculate scores
    scorer = UtilityScorer()
    score = scorer.calculate_score(agent_id)

    # Check nominations
    manager = NominationManager()
    candidates = manager.check_candidates()

Score Scale: 0.0 - 1.0
- 0.85+: Eligible for federation memory nomination
- 0.50-0.85: Normal operation
- <0.50: Review required
"""

from .feedback import FeedbackCollector
from .scorer import UtilityScorer
from .nomination import NominationManager

__all__ = ["FeedbackCollector", "UtilityScorer", "NominationManager"]
__version__ = "1.0.0"
