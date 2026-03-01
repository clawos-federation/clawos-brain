#!/usr/bin/env python3
"""Evolution Scheduler - 15-minute check loop for evolution tasks

This scheduler runs periodically to check for evolution tasks that can be
executed during system idle time. It respects the priority order P1 > P2 > P3 > P4
and supports preemption by real tasks.

Usage:
    python scheduler.py [--once] [--daemon]

Options:
    --once    Run single check cycle and exit
    --daemon  Run as background daemon with 15-min intervals
"""
import json
import os
import signal
import sys
import time
import subprocess

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List

# Add project root to path for clawos imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


from clawos.services.memory import MemoryManager


class EvolutionScheduler:
    """Manages the evolution task queue and scheduling logic.

    The scheduler checks for idle time and processes evolution tasks
    in priority order: P1 (Knowledge) > P2 (Training) > P3 (Exploration) > P4 (SOUL).
    """

    CHECK_INTERVAL = 900  # 15 minutes in seconds
    IDLE_THRESHOLD = 900  # 15 minutes in seconds

    # Priority to filename mapping
    PRIORITY_FILES = {
        "P1": "p1-knowledge.json",
        "P2": "p2-training.json",
        "P3": "p3-exploration.json",
        "P4": "p4-soul-drafts.json",
    }

    def __init__(self, queue_dir: Optional[Path] = None):
        """Initialize the scheduler.

        Args:
            queue_dir: Optional custom queue directory path
        """
        self.queue_dir = (
            queue_dir or Path.home() / "clawos/blackboard/federation/evolution-queue"
        )
        self.state_file = self.queue_dir / "scheduler-state.json"
        self.schema_file = self.queue_dir / "schema.json"
        self.scheduler_state = self._load_state()
        self.schema = self._load_schema()

    def _load_state(self) -> Dict[str, Any]:
        """Load scheduler state from disk."""
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text())
            except json.JSONDecodeError:
                pass
        return {
            "version": "1.0.0",
            "status": "active",
            "lastCheck": None,
            "lastActivity": datetime.now().isoformat(),
            "currentTasks": [],
            "idleThresholdMinutes": 15,
            "checkIntervalMinutes": 15,
            "stats": {
                "totalTasksProcessed": 0,
                "p1Completed": 0,
                "p2Completed": 0,
                "p3Completed": 0,
                "p4Completed": 0,
            },
        }

    def _load_schema(self) -> Dict[str, Any]:
        """Load queue schema from disk."""
        if self.schema_file.exists():
            try:
                return json.loads(self.schema_file.read_text())
            except json.JSONDecodeError:
                pass
        return {"priorityOrder": ["P1", "P2", "P3", "P4"]}

    def _save_state(self) -> None:
        """Persist scheduler state to disk."""
        self.state_file.write_text(json.dumps(self.scheduler_state, indent=2))

    def check_idle(self) -> bool:
        """Check if system has been idle long enough for evolution tasks.

        Returns:
            True if system is idle, False otherwise
        """
        last_activity = self.scheduler_state.get("lastActivity")
        if not last_activity:
            return True

        try:
            last = datetime.fromisoformat(last_activity)
            idle_seconds = (datetime.now() - last).total_seconds()
            idle_threshold = self.scheduler_state.get("idleThresholdMinutes", 15) * 60
            return idle_seconds > idle_threshold
        except (ValueError, TypeError):
            return True

    def get_queue_file(self, priority: str) -> Optional[Path]:
        """Get the queue file path for a priority level.

        Args:
            priority: Priority level (P1, P2, P3, P4)

        Returns:
            Path to queue file or None if not found
        """
        filename = self.PRIORITY_FILES.get(priority)
        if filename:
            return self.queue_dir / filename
        return None

    def load_queue(self, priority: str) -> Dict[str, Any]:
        """Load a priority queue from disk.

        Args:
            priority: Priority level (P1, P2, P3, P4)

        Returns:
            Queue data structure
        """
        queue_file = self.get_queue_file(priority)
        if queue_file and queue_file.exists():
            try:
                return json.loads(queue_file.read_text())
            except json.JSONDecodeError:
                pass
        return {"priority": priority, "tasks": [], "processing": [], "completed": []}

    def save_queue(self, priority: str, queue: Dict[str, Any]) -> None:
        """Save a priority queue to disk.

        Args:
            priority: Priority level (P1, P2, P3, P4)
            queue: Queue data structure
        """
        queue_file = self.get_queue_file(priority)
        if queue_file:
            queue["lastUpdated"] = datetime.now().isoformat()
            queue_file.write_text(json.dumps(queue, indent=2))

    def get_next_task(self, priority: str) -> Optional[Dict[str, Any]]:
        """Get next pending task from a priority queue.

        Args:
            priority: Priority level (P1, P2, P3, P4)

        Returns:
            Next pending task or None if queue is empty
        """
        queue = self.load_queue(priority)
        pending_tasks = queue.get("tasks", [])

        for task in pending_tasks:
            if task.get("status") == "pending":
                return task

        return None

    def move_to_processing(self, priority: str, task_id: str) -> bool:
        """Move a task from pending to processing.

        Args:
            priority: Priority level
            task_id: Task identifier

        Returns:
            True if successful, False otherwise
        """
        queue = self.load_queue(priority)

        # Find and remove from pending
        task = None
        for i, t in enumerate(queue.get("tasks", [])):
            if t.get("id") == task_id:
                task = queue["tasks"].pop(i)
                break

        if not task:
            return False

        # Update task status
        task["status"] = "processing"
        task["assignedTo"] = "evolution-scheduler"
        task["startedAt"] = datetime.now().isoformat()

        # Add to processing
        queue.setdefault("processing", []).append(task)

        # Save queue
        self.save_queue(priority, queue)
        return True

    def complete_task(
        self, priority: str, task_id: str, result: Dict[str, Any]
    ) -> bool:
        """Mark a task as completed.

        Args:
            priority: Priority level
            task_id: Task identifier
            result: Task execution result

        Returns:
            True if successful, False otherwise
        """
        queue = self.load_queue(priority)

        # Find and remove from processing
        task = None
        for i, t in enumerate(queue.get("processing", [])):
            if t.get("id") == task_id:
                task = queue["processing"].pop(i)
                break

        if not task:
            return False

        # Update task status
        task["status"] = "completed"
        task["completedAt"] = datetime.now().isoformat()
        task["result"] = result

        # Add to completed
        queue.setdefault("completed", []).append(task)

        # Save queue
        self.save_queue(priority, queue)

        # Update stats
        self.scheduler_state["stats"]["totalTasksProcessed"] += 1
        stat_key = f"{priority.lower()}Completed"
        self.scheduler_state["stats"][stat_key] = (
            self.scheduler_state["stats"].get(stat_key, 0) + 1
        )
        self._save_state()

        return True

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task by calling the appropriate agent.

        Args:
            task: Task dictionary with type, id, payload, etc.

        Returns:
            Result dictionary with success status and output
        """
        # Map task type to agent
        task_type = task.get("type", "")
        agent_mapping = {
            "knowledge-update": "platform-pm",
            "skill-training": "coding-pm",
            "capability-training": "coding-pm",
            "domain-exploration": "research-pm",
            "soul-draft": "platform-pm",
        }
        agent = agent_mapping.get(task_type, "gm")

        # Build detailed task message from payload
        payload = task.get("payload", {})
        task_id = task.get("id", "unknown")
        action = payload.get("action", "execute")
        target = payload.get("target", "")
        source = payload.get("source", "")
        
        # Construct descriptive message for the agent
        description = f"""[Evolution Task: {task_id}]
Type: {task_type}
Action: {action}
Target: {target or 'not specified'}
Source: {source or 'not specified'}

Please perform the '{action}' action for the evolution system.
{f'Focus on: {target}' if target else ''}"""

        try:
            # Call openclaw agent command
            result = subprocess.run(
                ["openclaw", "agent", "--agent", agent, "--message", description, "--json"],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            result_dict = {
                "success": result.returncode == 0,
                "agent": agent,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "executedAt": datetime.now().isoformat(),
            }

            # Store result in memory
            try:
                memory = MemoryManager(session_id=f"evolution-{task['id']}")
                memory.store_task_result(
                    task={"id": task["id"], "agent_id": agent, "description": description, "type": task_type},
                    result={"status": "completed" if result.returncode == 0 else "failed", "output": result.stdout[:500] if result.stdout else None}
                )
            except Exception as e:
                print(f"[scheduler] Warning: Failed to store in memory: {e}")

            return result_dict
        except subprocess.TimeoutExpired:
            result_dict = {
                "success": False,
                "agent": agent,
                "error": "Task execution timed out (300s)",
                "executedAt": datetime.now().isoformat(),
            }

            # Store result in memory
            try:
                memory = MemoryManager(session_id=f"evolution-{task['id']}")
                memory.store_task_result(
                    task={"id": task["id"], "agent_id": agent, "description": description, "type": task_type},
                    result={"status": "failed", "error": "Task execution timed out (300s)"}
                )
            except Exception as e:
                print(f"[scheduler] Warning: Failed to store in memory: {e}")

            return result_dict
        except Exception as e:
            result_dict = {
                "success": False,
                "agent": agent,
                "error": str(e),
                "executedAt": datetime.now().isoformat(),
            }

            # Store result in memory
            try:
                memory = MemoryManager(session_id=f"evolution-{task['id']}")
                memory.store_task_result(
                    task={"id": task["id"], "agent_id": agent, "description": description, "type": task_type},
                    result={"status": "failed", "error": str(e)}
                )
            except Exception as me:
                print(f"[scheduler] Warning: Failed to store in memory: {me}")

            return result_dict


    def run_cycle(self) -> Optional[Dict[str, Any]]:
        """Run a single scheduler cycle.

        Checks for idle time and returns the next task to process
        based on priority order.

        Returns:
            Next task to process or None if no tasks available
        """
        # Update last check time
        self.scheduler_state["lastCheck"] = datetime.now().isoformat()
        self._save_state()

        # Check if system is idle
        if not self.check_idle():
            return None

        # Get priority order from schema
        priority_order = self.schema.get("priorityOrder", ["P1", "P2", "P3", "P4"])

        # Find next task in priority order
        for priority in priority_order:
            task = self.get_next_task(priority)
            if task:
                # Move to processing
                if self.move_to_processing(priority, task["id"]):
                    task["priority"] = priority
                    return task

        return None

    def get_queue_stats(self) -> Dict[str, Any]:
        """Get statistics for all queues.

        Returns:
            Dictionary with queue statistics
        """
        stats = {"scheduler": self.scheduler_state.get("stats", {}), "queues": {}}

        for priority, filename in self.PRIORITY_FILES.items():
            queue = self.load_queue(priority)
            stats["queues"][priority] = {
                "pending": len(queue.get("tasks", [])),
                "processing": len(queue.get("processing", [])),
                "completed": len(queue.get("completed", [])),
            }

        return stats


def main():
    """Main entry point for the scheduler."""
    import argparse

    parser = argparse.ArgumentParser(description="Evolution Task Scheduler")
    parser.add_argument("--once", action="store_true", help="Run single check cycle")
    parser.add_argument("--stats", action="store_true", help="Show queue statistics")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon with 15-min intervals")
    args = parser.parse_args()

    scheduler = EvolutionScheduler()

    if args.stats:
        stats = scheduler.get_queue_stats()
        print(json.dumps(stats, indent=2))
        return 0

    if args.once:
        task = scheduler.run_cycle()
        if task:
            priority = task.get('priority', 'unknown')
            print(f"Found task: {task['id']}")
            print(f"Priority: {priority}")
            print(f"Type: {task.get('type', 'unknown')}")
            print(f"Payload: {json.dumps(task.get('payload', {}), indent=2)}")
            print("\nExecuting task...")
            result = scheduler.execute_task(task)
            print(f"Execution result: success={result.get('success', False)}")
            if scheduler.complete_task(priority, task['id'], result):
                print(f"Task {task['id']} marked as completed")
        else:
            print("No idle or no pending tasks")
        return 0
    if args.daemon:
        # Daemon mode: run continuous loop with signal handling
        shutdown = False

        def handle_signal(signum, frame):
            nonlocal shutdown
            sig_name = signal.Signals(signum).name
            print(f"[daemon] Received {sig_name}, shutting down...")
            shutdown = True

        signal.signal(signal.SIGTERM, handle_signal)
        signal.signal(signal.SIGINT, handle_signal)

        print(f"[daemon] Starting evolution scheduler (interval: {scheduler.CHECK_INTERVAL}s)")
        print("[daemon] Press Ctrl+C to stop")

        cycle_count = 0
        while not shutdown:
            cycle_count += 1
            try:
                print(f"[daemon] Cycle {cycle_count}: checking for tasks...")
                task = scheduler.run_cycle()
                if task:
                    priority = task.get('priority', 'unknown')
                    print(f"[daemon] Found task: {task['id']} (priority: {priority})")
                    # Execute the task
                    print(f"[daemon] Executing task via openclaw agent...")
                    result = scheduler.execute_task(task)
                    print(f"[daemon] Execution result: success={result.get('success', False)}")
                    # Mark task as completed
                    if scheduler.complete_task(priority, task['id'], result):
                        print(f"[daemon] Task {task['id']} marked as completed")
                    else:
                        print(f"[daemon] Warning: Failed to mark task {task['id']} as completed")
                else:
                    print(f"[daemon] No pending tasks or system not idle")
            except Exception as e:
                print(f"[daemon] Error during cycle: {e}")

            if not shutdown:
                # Sleep in small increments to respond to signals quickly
                for _ in range(scheduler.CHECK_INTERVAL):
                    if shutdown:
                        break
                    time.sleep(1)

        print("[daemon] Shutdown complete")
        return 0

    # Default: show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
