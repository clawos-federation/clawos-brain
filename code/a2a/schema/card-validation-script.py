#!/usr/bin/env python3
"""
ClawOS A2A Agent Card Validator

Validates agent cards against the ClawOS A2A Agent Card JSON Schema.

Usage:
    python card-validation-script.py <card-file.json>
    python card-validation-script.py --all
    python card-validation-script.py --dir ./cards/
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime

try:
    import jsonschema
    from jsonschema import validate, ValidationError, Draft202012Validator

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    print("Warning: jsonschema not installed. Install with: pip install jsonschema")


# Schema path
SCRIPT_DIR = Path(__file__).parent
SCHEMA_PATH = SCRIPT_DIR / "agent-card-schema.json"


def load_schema() -> Dict[str, Any]:
    """Load the agent card JSON schema."""
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema not found: {SCHEMA_PATH}")

    with open(SCHEMA_PATH, "r") as f:
        return json.load(f)


def load_card(card_path: str) -> Dict[str, Any]:
    """Load an agent card from file."""
    path = Path(card_path)
    if not path.exists():
        raise FileNotFoundError(f"Card not found: {card_path}")

    with open(path, "r") as f:
        return json.load(f)


def validate_card(
    card: Dict[str, Any], schema: Dict[str, Any]
) -> Tuple[bool, List[str]]:
    """
    Validate a card against the schema.

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    if not HAS_JSONSCHEMA:
        return False, ["jsonschema library not installed"]

    errors = []

    try:
        # Create validator with format checker
        validator = Draft202012Validator(schema)

        # Validate
        for error in validator.iter_errors(card):
            path = " -> ".join(str(p) for p in error.absolute_path)
            errors.append(f"{path}: {error.message}")

    except Exception as e:
        errors.append(f"Validation error: {str(e)}")

    return len(errors) == 0, errors


def validate_clawos_rules(card: Dict[str, Any]) -> List[str]:
    """
    Validate ClawOS-specific rules not covered by JSON Schema.

    Returns:
        List of rule violations
    """
    violations = []

    # Rule 1: Tier must match humanReadableId
    hr_id = card.get("humanReadableId", "")
    identity = card.get("identity", {})
    tier = identity.get("tier", "")

    if hr_id and tier:
        if f"/{tier}/" not in hr_id:
            violations.append(
                f"Tier '{tier}' doesn't match humanReadableId pattern: {hr_id}"
            )

    # Rule 2: Command tier must have pmAppointment capability
    if tier == "command":
        caps = card.get("capabilities", {})
        if not caps.get("pmAppointment", False):
            violations.append("Command tier agents must have pmAppointment capability")

    # Rule 3: PM tier must have taskEvaluation capability
    if tier == "pm":
        caps = card.get("capabilities", {})
        if not caps.get("taskEvaluation", False):
            violations.append("PM tier agents should have taskEvaluation capability")

    # Rule 4: Active agents must have heartbeat within 5 minutes
    status = card.get("status", {})
    if status.get("state") == "active":
        last_heartbeat = status.get("lastHeartbeat")
        if last_heartbeat:
            try:
                hb_time = datetime.fromisoformat(last_heartbeat.replace("Z", "+00:00"))
                age = (datetime.now(hb_time.tzinfo) - hb_time).total_seconds()
                if age > 300:  # 5 minutes
                    violations.append(
                        f"Agent marked active but last heartbeat was {int(age)}s ago"
                    )
            except Exception:
                pass

    # Rule 5: Worker tier should have parent defined
    if tier == "worker":
        if not identity.get("parent"):
            violations.append("Worker tier agents should have parent PM defined")

    return violations


def format_result(
    card_path: str, is_valid: bool, errors: List[str], violations: List[str]
) -> str:
    """Format validation result for display."""
    lines = []

    status = "✅ VALID" if is_valid and not violations else "❌ INVALID"
    lines.append(f"\n{'=' * 60}")
    lines.append(f"Card: {card_path}")
    lines.append(f"Status: {status}")
    lines.append(f"{'=' * 60}")

    if errors:
        lines.append("\nSchema Errors:")
        for err in errors:
            lines.append(f"  • {err}")

    if violations:
        lines.append("\nClawOS Rule Violations:")
        for v in violations:
            lines.append(f"  ⚠️  {v}")

    if is_valid and not violations:
        lines.append("\n  All checks passed!")

    return "\n".join(lines)


def main():
    """Main entry point."""
    if not HAS_JSONSCHEMA:
        print(
            "Error: jsonschema library required. Install with: pip install jsonschema"
        )
        sys.exit(1)

    # Load schema
    try:
        schema = load_schema()
        print(f"Loaded schema: {SCHEMA_PATH}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    cards_to_validate = []

    # Parse arguments
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        sys.exit(0)

    if "--all" in args:
        # Find all card files in registry
        registry_path = SCRIPT_DIR.parent / "registry" / "cards"
        if registry_path.exists():
            cards_to_validate = list(registry_path.glob("*.json"))
        else:
            print(f"Registry not found: {registry_path}")
            sys.exit(1)

    elif "--dir" in args:
        # Validate all cards in directory
        try:
            dir_idx = args.index("--dir")
            dir_path = Path(args[dir_idx + 1])
            cards_to_validate = list(dir_path.glob("*.json"))
        except (IndexError, ValueError):
            print("Error: --dir requires a directory path")
            sys.exit(1)

    else:
        # Validate specific file(s)
        cards_to_validate = [Path(arg) for arg in args if arg.endswith(".json")]

    if not cards_to_validate:
        print("No card files found to validate")
        sys.exit(1)

    # Validate each card
    all_valid = True
    results = []

    for card_path in cards_to_validate:
        try:
            card = load_card(str(card_path))
            is_valid, errors = validate_card(card, schema)
            violations = validate_clawos_rules(card)

            result = format_result(str(card_path), is_valid, errors, violations)
            results.append(result)

            if not is_valid or violations:
                all_valid = False

        except Exception as e:
            results.append(f"\n❌ Error loading {card_path}: {e}")
            all_valid = False

    # Print results
    for r in results:
        print(r)

    # Summary
    print(f"\n{'=' * 60}")
    print(f"Summary: Validated {len(cards_to_validate)} card(s)")
    print(f"Result: {'✅ All valid' if all_valid else '❌ Some cards have issues'}")
    print(f"{'=' * 60}\n")

    sys.exit(0 if all_valid else 1)


if __name__ == "__main__":
    main()
