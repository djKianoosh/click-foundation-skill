"""Design Sprint tools for running tiny loops."""

import sqlite3
from click_agent.models import CustomerReaction, CustomerReactions

VALID_DAYS = ("map", "sketch", "decide", "prototype", "test")


def create_design_sprint(
    conn: sqlite3.Connection,
    hypothesis_id: int,
    *,
    risk_question: str,
) -> str:
    """Create a new Design Sprint linked to the current hypothesis."""
    conn.execute(
        """INSERT INTO design_sprints (hypothesis_id, risk_question, status)
        VALUES (?, ?, 'in_progress')""",
        (hypothesis_id, risk_question),
    )
    conn.commit()
    return f"Design Sprint created. Testing: '{risk_question}'"


def log_sprint_day(
    conn: sqlite3.Connection,
    sprint_id: int,
    *,
    day: str,
    notes: str,
) -> str:
    """Record what happened on a specific day of the Design Sprint."""
    if day not in VALID_DAYS:
        return f"Error: '{day}' is not a valid day. Use: {', '.join(VALID_DAYS)}"

    column = f"day_{day}"
    conn.execute(
        f"UPDATE design_sprints SET {column} = ? WHERE id = ?",
        (notes, sprint_id),
    )
    conn.commit()
    return f"Day '{day}' logged."


def record_test_results(
    conn: sqlite3.Connection,
    sprint_id: int,
    *,
    reactions: list[dict],
) -> str:
    """Record customer reactions from Friday testing."""
    try:
        validated = CustomerReactions(
            items=[CustomerReaction(**r) for r in reactions]
        )
    except Exception as e:
        return f"Error: {e}"

    conn.execute(
        "UPDATE design_sprints SET customer_reactions = ? WHERE id = ?",
        (validated.model_dump_json(), sprint_id),
    )
    conn.commit()
    genuine = sum(1 for r in validated.items if r.is_reaction)
    return f"Recorded {len(reactions)} observations ({genuine} genuine reactions, {len(reactions) - genuine} feedback)."


def update_sprint_outcome(
    conn: sqlite3.Connection,
    sprint_id: int,
    *,
    outcome: str,
    hypothesis_changed: bool,
) -> str:
    """Record the Design Sprint outcome and mark it complete."""
    conn.execute(
        """UPDATE design_sprints SET
            outcome = ?, hypothesis_changed = ?, status = 'complete'
        WHERE id = ?""",
        (outcome, hypothesis_changed, sprint_id),
    )
    conn.commit()
    status = "Hypothesis needs revision." if hypothesis_changed else "Hypothesis unchanged."
    return f"Sprint complete. {status} Outcome: {outcome}"
