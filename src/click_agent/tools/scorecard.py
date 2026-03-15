"""Scorecard tools for tracking hypothesis validation."""

import sqlite3
from click_agent.models import ScorecardAnswer


def update_scorecard(
    conn: sqlite3.Connection,
    hypothesis_id: int,
    *,
    right_customer: str,
    right_problem: str,
    right_approach: str,
    will_they_switch: str,
    right_differentiation: str,
    does_it_click: str,
    notes: str,
) -> str:
    """Update the scorecard with new answers and evidence."""
    answers = {
        "right_customer": right_customer,
        "right_problem": right_problem,
        "right_approach": right_approach,
        "will_they_switch": will_they_switch,
        "right_differentiation": right_differentiation,
        "does_it_click": does_it_click,
    }
    for field, value in answers.items():
        try:
            ScorecardAnswer(value)
        except ValueError:
            return f"Error: '{value}' is not a valid answer for {field}. Use: yes, maybe, not_yet, no"

    conn.execute(
        """INSERT INTO scorecard_entries
            (hypothesis_id, right_customer, right_problem, right_approach,
             will_they_switch, right_differentiation, does_it_click, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            hypothesis_id, right_customer, right_problem, right_approach,
            will_they_switch, right_differentiation, does_it_click, notes,
        ),
    )
    conn.commit()
    return "Scorecard saved with evidence notes."


def show_scorecard(
    conn: sqlite3.Connection,
    hypothesis_id: int,
) -> str:
    """Show the current scorecard state with evidence trail."""
    cursor = conn.execute(
        """SELECT * FROM scorecard_entries
        WHERE hypothesis_id = ?
        ORDER BY updated_at DESC LIMIT 1""",
        (hypothesis_id,),
    )
    entry = cursor.fetchone()
    if not entry:
        return "No scorecard entries yet. Run a Design Sprint to start validating."

    lines = [
        "## Scorecard",
        f"- Right customer? **{entry['right_customer']}**",
        f"- Right problem? **{entry['right_problem']}**",
        f"- Right approach? **{entry['right_approach']}**",
        f"- Will they switch? **{entry['will_they_switch']}**",
        f"- Right differentiation? **{entry['right_differentiation']}**",
        f"- Does it click? **{entry['does_it_click']}**",
        f"\nNotes: {entry['notes']}",
    ]
    return "\n".join(lines)
