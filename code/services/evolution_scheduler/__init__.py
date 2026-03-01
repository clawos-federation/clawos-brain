#!/usr/bin/env python3
"""
Evolution Scheduler Module - ClawOS Self-Improvement System

This module provides automated self-improvement scheduling:
- P1: Knowledge updates (15-min idle)
- P2: Capability training (1-hour idle)
- P3: Domain exploration (2-hour idle)
- P4: SOUL drafts (4-hour idle)

Usage:
    from scheduler import EvolutionScheduler

    scheduler = EvolutionScheduler()
    scheduler.start()
"""

from .scheduler import EvolutionScheduler

__all__ = ["EvolutionScheduler"]
__version__ = "1.0.0"
