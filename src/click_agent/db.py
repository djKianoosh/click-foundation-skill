"""SQLite database initialization and query functions."""

import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    current_hypothesis_id INTEGER REFERENCES hypotheses(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS foundation_sprints (
    id INTEGER PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    customer TEXT,
    problem TEXT,
    capability TEXT,
    insight TEXT,
    motivation TEXT,
    gorilla TEXT,
    alternatives TEXT,
    differentiator_1 TEXT,
    differentiator_2 TEXT,
    diff_2x2_axes TEXT,
    principles TEXT,
    current_step TEXT DEFAULT 'customer',
    status TEXT DEFAULT 'in_progress' CHECK(status IN ('in_progress', 'complete')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS approaches (
    id INTEGER PRIMARY KEY,
    foundation_id INTEGER REFERENCES foundation_sprints(id),
    title TEXT NOT NULL,
    summary TEXT,
    how_it_works TEXT,
    is_top_bet BOOLEAN DEFAULT FALSE,
    is_backup BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS magic_lenses (
    id INTEGER PRIMARY KEY,
    foundation_id INTEGER REFERENCES foundation_sprints(id),
    lens_name TEXT NOT NULL,
    x_axis_low TEXT,
    x_axis_high TEXT,
    y_axis_low TEXT,
    y_axis_high TEXT,
    evaluations TEXT
);

CREATE TABLE IF NOT EXISTS hypotheses (
    id INTEGER PRIMARY KEY,
    foundation_id INTEGER REFERENCES foundation_sprints(id),
    customer TEXT NOT NULL,
    problem TEXT NOT NULL,
    approach TEXT NOT NULL,
    competitors TEXT NOT NULL,
    differentiation TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scorecard_entries (
    id INTEGER PRIMARY KEY,
    hypothesis_id INTEGER REFERENCES hypotheses(id),
    right_customer TEXT CHECK(right_customer IN ('yes', 'maybe', 'not_yet', 'no')),
    right_problem TEXT CHECK(right_problem IN ('yes', 'maybe', 'not_yet', 'no')),
    right_approach TEXT CHECK(right_approach IN ('yes', 'maybe', 'not_yet', 'no')),
    will_they_switch TEXT CHECK(will_they_switch IN ('yes', 'maybe', 'not_yet', 'no')),
    right_differentiation TEXT CHECK(right_differentiation IN ('yes', 'maybe', 'not_yet', 'no')),
    does_it_click TEXT CHECK(does_it_click IN ('yes', 'maybe', 'not_yet', 'no')),
    notes TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS design_sprints (
    id INTEGER PRIMARY KEY,
    hypothesis_id INTEGER REFERENCES hypotheses(id),
    risk_question TEXT,
    day_map TEXT,
    day_sketch TEXT,
    day_decide TEXT,
    day_prototype TEXT,
    day_test TEXT,
    customer_reactions TEXT,
    outcome TEXT,
    hypothesis_changed BOOLEAN DEFAULT FALSE,
    status TEXT DEFAULT 'planned',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS learnings (
    id INTEGER PRIMARY KEY,
    source_type TEXT NOT NULL CHECK(source_type IN ('foundation_sprint', 'design_sprint', 'pivot')),
    source_id INTEGER,
    insight TEXT NOT NULL,
    lesson_number INTEGER CHECK(lesson_number BETWEEN 1 AND 10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pivots (
    id INTEGER PRIMARY KEY,
    old_hypothesis_id INTEGER REFERENCES hypotheses(id),
    new_hypothesis_id INTEGER REFERENCES hypotheses(id),
    reason TEXT,
    what_changed TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def init_db(db_path: str) -> None:
    """Initialize the database with the schema."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def get_connection(db_path: str) -> sqlite3.Connection:
    """Get a database connection with row_factory set."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_project(conn: sqlite3.Connection, name: str) -> int:
    """Create a new project and return its ID."""
    cursor = conn.execute("INSERT INTO projects (name) VALUES (?)", (name,))
    conn.commit()
    return cursor.lastrowid


def get_project(conn: sqlite3.Connection, project_id: int) -> sqlite3.Row:
    """Get a project by ID."""
    cursor = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    return cursor.fetchone()


def create_foundation_sprint(conn: sqlite3.Connection, project_id: int) -> int:
    """Create a new Foundation Sprint and return its ID."""
    cursor = conn.execute(
        "INSERT INTO foundation_sprints (project_id) VALUES (?)", (project_id,)
    )
    conn.commit()
    return cursor.lastrowid


def get_foundation_sprint(conn: sqlite3.Connection, sprint_id: int) -> sqlite3.Row:
    """Get a Foundation Sprint by ID."""
    cursor = conn.execute(
        "SELECT * FROM foundation_sprints WHERE id = ?", (sprint_id,)
    )
    return cursor.fetchone()


def update_foundation_step(conn: sqlite3.Connection, sprint_id: int, step: str) -> None:
    """Update the current step of a Foundation Sprint."""
    conn.execute(
        "UPDATE foundation_sprints SET current_step = ? WHERE id = ?",
        (step, sprint_id),
    )
    conn.commit()
