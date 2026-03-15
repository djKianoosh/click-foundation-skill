"""Cross-cutting tools: project context, learnings, hypothesis revision."""

import sqlite3
from click_agent.models import SourceType

THE_10_LESSONS = [
    "Drop everything and sprint on the most important challenge until it's done",
    "Start by identifying your customer and a real problem you can solve",
    "Take advantage of your advantages",
    "Get real about the competition",
    "Differentiation makes products click",
    "Use practical principles to reinforce differentiation",
    "Seek alternatives to your first idea",
    "Consider conflicting opinions before you commit to an approach",
    "It's just a hypothesis until you prove it",
    "Experiment with tiny loops until your solution clicks. Then build it.",
]


def get_project_context(conn: sqlite3.Connection, project_id: int) -> str:
    """Load current project context: hypothesis, scorecard, sprint history."""
    project = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    if not project:
        return "Error: Project not found."

    lines = [f"## Project: {project['name']}"]

    hyp_id = project["current_hypothesis_id"]
    if not hyp_id:
        lines.append("\nNo Founding Hypothesis yet. Run a Foundation Sprint first.")
    else:
        hyp = conn.execute("SELECT * FROM hypotheses WHERE id = ?", (hyp_id,)).fetchone()
        lines.append(f"\n### Founding Hypothesis (v{hyp['version']})")
        lines.append(
            f"If we help **{hyp['customer']}** solve **{hyp['problem']}** "
            f"with **{hyp['approach']}**, they will choose it over **{hyp['competitors']}** "
            f"because our solution is **{hyp['differentiation']}**."
        )

        entry = conn.execute(
            "SELECT * FROM scorecard_entries WHERE hypothesis_id = ? ORDER BY updated_at DESC LIMIT 1",
            (hyp_id,),
        ).fetchone()
        if entry:
            lines.append("\n### Scorecard")
            for field in ["right_customer", "right_problem", "right_approach",
                          "will_they_switch", "right_differentiation", "does_it_click"]:
                label = field.replace("_", " ").title()
                lines.append(f"- {label}: **{entry[field]}**")

        count = conn.execute(
            "SELECT COUNT(*) FROM design_sprints WHERE hypothesis_id = ?", (hyp_id,)
        ).fetchone()[0]
        if count:
            lines.append(f"\n{count} Design Sprint(s) completed for this hypothesis.")

    return "\n".join(lines)


def record_learning(
    conn: sqlite3.Connection,
    *,
    source_type: str,
    source_id: int,
    insight: str,
    lesson_number: int,
) -> str:
    """Record a learning tagged with one of the 10 Click lessons."""
    try:
        SourceType(source_type)
    except ValueError:
        return f"Error: '{source_type}' is not valid. Use: foundation_sprint, design_sprint, pivot"

    if not 1 <= lesson_number <= 10:
        return f"Error: lesson_number must be between 1 and 10, got {lesson_number}"

    conn.execute(
        "INSERT INTO learnings (source_type, source_id, insight, lesson_number) VALUES (?, ?, ?, ?)",
        (source_type, source_id, insight, lesson_number),
    )
    conn.commit()
    return f"Learning recorded (Lesson #{lesson_number}: {THE_10_LESSONS[lesson_number - 1]})"


def query_learnings(conn: sqlite3.Connection) -> str:
    """Retrieve all accumulated learnings organized by lesson number."""
    learnings = conn.execute(
        "SELECT * FROM learnings ORDER BY lesson_number, created_at"
    ).fetchall()

    if not learnings:
        return "No learnings recorded yet."

    lines = ["## Accumulated Learnings"]
    current_lesson = None
    for l in learnings:
        if l["lesson_number"] != current_lesson:
            current_lesson = l["lesson_number"]
            lines.append(f"\n### Lesson {current_lesson}: {THE_10_LESSONS[current_lesson - 1]}")
        lines.append(f"- {l['insight']} (from {l['source_type']})")

    return "\n".join(lines)


def revise_hypothesis(
    conn: sqlite3.Connection,
    project_id: int,
    old_hypothesis_id: int,
    *,
    customer: str,
    problem: str,
    approach: str,
    competitors: str,
    differentiation: str,
    reason: str,
    what_changed: str,
) -> str:
    """Create a new hypothesis version and record the pivot."""
    old = conn.execute("SELECT * FROM hypotheses WHERE id = ?", (old_hypothesis_id,)).fetchone()
    new_version = old["version"] + 1

    cursor = conn.execute(
        """INSERT INTO hypotheses
            (foundation_id, customer, problem, approach, competitors, differentiation, version)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (old["foundation_id"], customer, problem, approach, competitors, differentiation, new_version),
    )
    new_id = cursor.lastrowid

    conn.execute(
        "INSERT INTO pivots (old_hypothesis_id, new_hypothesis_id, reason, what_changed) VALUES (?, ?, ?, ?)",
        (old_hypothesis_id, new_id, reason, what_changed),
    )
    conn.execute(
        "UPDATE projects SET current_hypothesis_id = ? WHERE id = ?",
        (new_id, project_id),
    )
    conn.commit()
    return (
        f"Hypothesis revised to v{new_version}. Changed: {what_changed}. "
        f"Reason: {reason}"
    )
