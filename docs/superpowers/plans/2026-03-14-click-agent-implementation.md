# Click Agent Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python CLI agent that coaches founders through the Click methodology (Foundation Sprint + Design Sprints) via interactive dialogue, with SQLite persistence and markdown output.

**Architecture:** Single Claude Agent SDK agent with custom tools registered via SDK MCP server. Typer CLI dispatches commands that launch the agent with the appropriate system prompt and context. SQLite stores all artifacts; Pydantic validates JSON fields.

**Tech Stack:** Python 3.11+, claude-agent-sdk, anthropic, typer, pydantic, sqlite3 (stdlib)

---

## File Structure

```
click/
├── pyproject.toml
├── src/
│   └── click_agent/
│       ├── __init__.py
│       ├── cli.py                  # Typer CLI entry point
│       ├── agent.py                # Agent setup, system prompt, tool registration
│       ├── db.py                   # Database init, connection, queries
│       ├── models.py               # Pydantic models for JSON validation + data
│       ├── prompts.py              # System prompt text
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── foundation.py       # Foundation Sprint tools
│       │   ├── design_sprint.py    # Design Sprint tools
│       │   ├── scorecard.py        # Scorecard tools
│       │   └── context.py          # Cross-cutting tools (learnings, context, docs)
│       └── docs_generator.py       # Markdown document generation
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Shared fixtures (tmp db, etc.)
│   ├── test_db.py
│   ├── test_models.py
│   ├── test_tools_foundation.py
│   ├── test_tools_design_sprint.py
│   ├── test_tools_scorecard.py
│   ├── test_tools_context.py
│   ├── test_docs_generator.py
│   └── test_cli.py
```

---

## Chunk 1: Project Setup + Database + Models

### Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `src/click_agent/__init__.py`

- [ ] **Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "click-agent"
version = "0.1.0"
description = "CLI product coach using the Click methodology"
requires-python = ">=3.11"
dependencies = [
    "claude-agent-sdk",
    "anthropic",
    "typer>=0.9.0",
    "pydantic>=2.0.0",
]

[project.scripts]
click-coach = "click_agent.cli:app"

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-asyncio>=0.21",
]

[tool.hatch.build.targets.wheel]
packages = ["src/click_agent"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

Note: The CLI entry point is `click-coach` (not `click`) to avoid collision with the `click` Python library.

- [ ] **Step 2: Create src/click_agent/__init__.py**

```python
"""Click Agent - CLI product coach using the Click methodology."""
```

- [ ] **Step 3: Create tests/__init__.py**

```python
```

- [ ] **Step 4: Install the project in dev mode**

Run: `pip install -e ".[dev]"`
Expected: Successfully installed click-agent and dependencies

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/click_agent/__init__.py tests/__init__.py
git commit -m "feat: initial project scaffolding with pyproject.toml"
```

---

### Task 2: Pydantic Models for JSON Validation

**Files:**
- Create: `src/click_agent/models.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_models.py`:

```python
import pytest
from pydantic import ValidationError
from click_agent.models import (
    Alternatives,
    Diff2x2Axes,
    Principles,
    LensEvaluation,
    LensEvaluations,
    CustomerReaction,
    CustomerReactions,
    ScorecardAnswer,
    FoundationStep,
)


class TestAlternatives:
    def test_valid_alternatives(self):
        alts = Alternatives(items=["Google Maps", "Apple Maps", "do nothing"])
        assert len(alts.items) == 3

    def test_empty_alternatives(self):
        alts = Alternatives(items=[])
        assert alts.items == []

    def test_serializes_to_json(self):
        alts = Alternatives(items=["A", "B"])
        data = alts.model_dump_json()
        assert '"A"' in data


class TestDiff2x2Axes:
    def test_valid_axes(self):
        axes = Diff2x2Axes(
            x_low="Slow", x_high="Fast", y_low="Expensive", y_high="Cheap"
        )
        assert axes.x_low == "Slow"

    def test_missing_field_raises(self):
        with pytest.raises(ValidationError):
            Diff2x2Axes(x_low="Slow", x_high="Fast", y_low="Expensive")


class TestPrinciples:
    def test_valid_three_principles(self):
        p = Principles(items=["Focus on user", "Fast is better", "Don't be evil"])
        assert len(p.items) == 3

    def test_wrong_count_raises(self):
        with pytest.raises(ValidationError):
            Principles(items=["Only one"])


class TestLensEvaluations:
    def test_valid_evaluations(self):
        evals = LensEvaluations(
            items=[
                LensEvaluation(approach_id=1, x_position="high", y_position="high"),
                LensEvaluation(approach_id=2, x_position="low", y_position="high"),
            ]
        )
        assert len(evals.items) == 2

    def test_invalid_position_raises(self):
        with pytest.raises(ValidationError):
            LensEvaluation(approach_id=1, x_position="middle", y_position="high")


class TestCustomerReactions:
    def test_valid_reactions(self):
        reactions = CustomerReactions(
            items=[
                CustomerReaction(
                    customer="Engineer A",
                    reaction="Leaned forward, asked to sign up",
                    is_reaction=True,
                ),
                CustomerReaction(
                    customer="Engineer B",
                    reaction="Said it looks nice but didn't engage",
                    is_reaction=False,
                ),
            ]
        )
        assert reactions.items[0].is_reaction is True


class TestScorecardAnswer:
    def test_valid_answers(self):
        for answer in ["yes", "maybe", "not_yet", "no"]:
            assert ScorecardAnswer(answer) == answer

    def test_invalid_answer_raises(self):
        with pytest.raises(ValueError):
            ScorecardAnswer("probably")


class TestFoundationStep:
    def test_valid_steps(self):
        steps = [
            "customer", "problem", "advantages", "competitors",
            "differentiation", "principles", "manifesto", "approaches",
            "lenses", "hypothesis", "scorecard", "complete",
        ]
        for step in steps:
            assert FoundationStep(step) == step

    def test_invalid_step_raises(self):
        with pytest.raises(ValueError):
            FoundationStep("invalid")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_models.py -v`
Expected: FAIL with import errors

- [ ] **Step 3: Write the models**

Create `src/click_agent/models.py`:

```python
"""Pydantic models for JSON field validation in SQLite."""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, field_validator


class ScorecardAnswer(StrEnum):
    YES = "yes"
    MAYBE = "maybe"
    NOT_YET = "not_yet"
    NO = "no"


class FoundationStep(StrEnum):
    CUSTOMER = "customer"
    PROBLEM = "problem"
    ADVANTAGES = "advantages"
    COMPETITORS = "competitors"
    DIFFERENTIATION = "differentiation"
    PRINCIPLES = "principles"
    MANIFESTO = "manifesto"
    APPROACHES = "approaches"
    LENSES = "lenses"
    HYPOTHESIS = "hypothesis"
    SCORECARD = "scorecard"
    COMPLETE = "complete"


class SourceType(StrEnum):
    FOUNDATION_SPRINT = "foundation_sprint"
    DESIGN_SPRINT = "design_sprint"
    PIVOT = "pivot"


class Alternatives(BaseModel):
    items: list[str]


class Diff2x2Axes(BaseModel):
    x_low: str
    x_high: str
    y_low: str
    y_high: str


class Principles(BaseModel):
    items: list[str]

    @field_validator("items")
    @classmethod
    def must_have_three(cls, v: list[str]) -> list[str]:
        if len(v) != 3:
            raise ValueError("Must have exactly 3 principles (differentiate, differentiate, safeguard)")
        return v


class LensEvaluation(BaseModel):
    approach_id: int
    x_position: Literal["high", "low"]
    y_position: Literal["high", "low"]


class LensEvaluations(BaseModel):
    items: list[LensEvaluation]


class CustomerReaction(BaseModel):
    customer: str
    reaction: str
    is_reaction: bool  # True = genuine reaction, False = just feedback


class CustomerReactions(BaseModel):
    items: list[CustomerReaction]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_models.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add src/click_agent/models.py tests/test_models.py
git commit -m "feat: add Pydantic models for JSON field validation"
```

---

### Task 3: Database Layer

**Files:**
- Create: `src/click_agent/db.py`
- Create: `tests/test_db.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Write conftest.py with shared fixtures**

Create `tests/conftest.py`:

```python
import os
import tempfile
from pathlib import Path

import pytest

from click_agent.db import init_db, get_connection


@pytest.fixture
def tmp_project(tmp_path):
    """Create a temporary project directory with .click/ initialized."""
    click_dir = tmp_path / ".click"
    click_dir.mkdir()
    output_dir = tmp_path / "click-output"
    output_dir.mkdir()
    db_path = click_dir / "click.db"
    init_db(str(db_path))
    return tmp_path


@pytest.fixture
def db_conn(tmp_project):
    """Return a database connection to a fresh test database."""
    db_path = tmp_project / ".click" / "click.db"
    conn = get_connection(str(db_path))
    yield conn
    conn.close()
```

- [ ] **Step 2: Write the failing tests**

Create `tests/test_db.py`:

```python
import sqlite3

import pytest

from click_agent.db import (
    init_db,
    get_connection,
    create_project,
    get_project,
    create_foundation_sprint,
    get_foundation_sprint,
    update_foundation_step,
)


class TestInitDb:
    def test_creates_all_tables(self, db_conn):
        cursor = db_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in cursor.fetchall()]
        expected = [
            "approaches",
            "design_sprints",
            "foundation_sprints",
            "hypotheses",
            "learnings",
            "magic_lenses",
            "pivots",
            "projects",
            "scorecard_entries",
        ]
        assert tables == expected

    def test_foreign_keys_enabled(self, db_conn):
        cursor = db_conn.execute("PRAGMA foreign_keys")
        assert cursor.fetchone()[0] == 1


class TestProjectCrud:
    def test_create_and_get_project(self, db_conn):
        project_id = create_project(db_conn, "My Startup")
        project = get_project(db_conn, project_id)
        assert project["name"] == "My Startup"
        assert project["current_hypothesis_id"] is None

    def test_create_project_returns_id(self, db_conn):
        project_id = create_project(db_conn, "Test")
        assert isinstance(project_id, int)
        assert project_id > 0


class TestFoundationSprintCrud:
    def test_create_foundation_sprint(self, db_conn):
        project_id = create_project(db_conn, "Test")
        sprint_id = create_foundation_sprint(db_conn, project_id)
        sprint = get_foundation_sprint(db_conn, sprint_id)
        assert sprint["project_id"] == project_id
        assert sprint["status"] == "in_progress"
        assert sprint["current_step"] == "customer"

    def test_update_foundation_step(self, db_conn):
        project_id = create_project(db_conn, "Test")
        sprint_id = create_foundation_sprint(db_conn, project_id)
        update_foundation_step(db_conn, sprint_id, "problem")
        sprint = get_foundation_sprint(db_conn, sprint_id)
        assert sprint["current_step"] == "problem"

    def test_invalid_status_raises(self, db_conn):
        project_id = create_project(db_conn, "Test")
        sprint_id = create_foundation_sprint(db_conn, project_id)
        with pytest.raises(sqlite3.IntegrityError):
            db_conn.execute(
                "UPDATE foundation_sprints SET status = ? WHERE id = ?",
                ("invalid", sprint_id),
            )
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `pytest tests/test_db.py -v`
Expected: FAIL with import errors

- [ ] **Step 4: Write the database module**

Create `src/click_agent/db.py`:

```python
"""SQLite database initialization and query functions."""

import sqlite3
from pathlib import Path

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


def update_foundation_step(
    conn: sqlite3.Connection, sprint_id: int, step: str
) -> None:
    """Update the current step of a Foundation Sprint."""
    conn.execute(
        "UPDATE foundation_sprints SET current_step = ? WHERE id = ?",
        (step, sprint_id),
    )
    conn.commit()
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_db.py -v`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add src/click_agent/db.py tests/conftest.py tests/test_db.py
git commit -m "feat: add database layer with schema and CRUD operations"
```

---

## Chunk 2: Foundation Sprint Tools

### Task 4: Save Basics Tool

**Files:**
- Create: `src/click_agent/tools/__init__.py`
- Create: `src/click_agent/tools/foundation.py`
- Create: `tests/test_tools_foundation.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_tools_foundation.py`:

```python
import json

import pytest

from click_agent.db import (
    create_project,
    create_foundation_sprint,
    get_foundation_sprint,
    get_connection,
)
from click_agent.tools.foundation import (
    save_basics,
    save_differentiation,
    save_approach,
    save_founding_hypothesis,
)


class TestSaveBasics:
    def test_saves_customer_and_problem(self, db_conn):
        project_id = create_project(db_conn, "Test")
        sprint_id = create_foundation_sprint(db_conn, project_id)
        result = save_basics(
            db_conn,
            sprint_id,
            customer="solo founders",
            problem="validating product ideas takes too long",
            capability="software engineering",
            insight="how startups fail",
            motivation="help founders succeed",
            gorilla="Y Combinator",
            alternatives=["books", "mentors", "consulting firms"],
        )
        sprint = get_foundation_sprint(db_conn, sprint_id)
        assert sprint["customer"] == "solo founders"
        assert sprint["problem"] == "validating product ideas takes too long"
        assert sprint["gorilla"] == "Y Combinator"
        assert json.loads(sprint["alternatives"]) == ["books", "mentors", "consulting firms"]
        assert sprint["current_step"] == "differentiation"

    def test_returns_success_message(self, db_conn):
        project_id = create_project(db_conn, "Test")
        sprint_id = create_foundation_sprint(db_conn, project_id)
        result = save_basics(
            db_conn, sprint_id,
            customer="founders", problem="slow validation",
            capability="eng", insight="failure", motivation="help",
            gorilla="YC", alternatives=["books"],
        )
        assert "saved" in result.lower()


class TestSaveDifferentiation:
    def test_saves_differentiators_and_principles(self, db_conn):
        project_id = create_project(db_conn, "Test")
        sprint_id = create_foundation_sprint(db_conn, project_id)
        result = save_differentiation(
            db_conn,
            sprint_id,
            differentiator_1="AI-guided",
            differentiator_2="evidence-based",
            diff_2x2_axes={
                "x_low": "Generic", "x_high": "Personalized",
                "y_low": "Slow", "y_high": "Fast",
            },
            principles=["Guide with AI", "Evidence over opinions", "Empower don't replace"],
        )
        sprint = get_foundation_sprint(db_conn, sprint_id)
        assert sprint["differentiator_1"] == "AI-guided"
        axes = json.loads(sprint["diff_2x2_axes"])
        assert axes["x_high"] == "Personalized"
        principles = json.loads(sprint["principles"])
        assert len(principles) == 3
        assert sprint["current_step"] == "manifesto"

    def test_rejects_wrong_principle_count(self, db_conn):
        project_id = create_project(db_conn, "Test")
        sprint_id = create_foundation_sprint(db_conn, project_id)
        result = save_differentiation(
            db_conn, sprint_id,
            differentiator_1="A", differentiator_2="B",
            diff_2x2_axes={"x_low": "a", "x_high": "b", "y_low": "c", "y_high": "d"},
            principles=["Only one"],
        )
        assert "error" in result.lower()


class TestSaveApproach:
    def test_saves_approach(self, db_conn):
        project_id = create_project(db_conn, "Test")
        sprint_id = create_foundation_sprint(db_conn, project_id)
        result = save_approach(
            db_conn, sprint_id,
            title="CLI Tool",
            summary="Build a command-line product coach",
            how_it_works="User runs commands, agent guides them",
            is_top_bet=True,
            is_backup=False,
        )
        cursor = db_conn.execute(
            "SELECT * FROM approaches WHERE foundation_id = ?", (sprint_id,)
        )
        approach = cursor.fetchone()
        assert approach["title"] == "CLI Tool"
        assert approach["is_top_bet"] == 1


class TestSaveFoundingHypothesis:
    def test_saves_hypothesis_and_updates_project(self, db_conn):
        project_id = create_project(db_conn, "Test")
        sprint_id = create_foundation_sprint(db_conn, project_id)
        result = save_founding_hypothesis(
            db_conn, sprint_id, project_id,
            customer="solo founders",
            problem="slow validation",
            approach="AI product coach CLI",
            competitors="books and mentors",
            differentiation="AI-guided and evidence-based",
        )
        cursor = db_conn.execute("SELECT * FROM hypotheses WHERE foundation_id = ?", (sprint_id,))
        hyp = cursor.fetchone()
        assert hyp["customer"] == "solo founders"
        assert hyp["version"] == 1
        # Check project updated
        project = db_conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        assert project["current_hypothesis_id"] == hyp["id"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_tools_foundation.py -v`
Expected: FAIL with import errors

- [ ] **Step 3: Write the foundation tools**

Create `src/click_agent/tools/__init__.py`:

```python
```

Create `src/click_agent/tools/foundation.py`:

```python
"""Foundation Sprint tools for the Click agent."""

import json
import sqlite3

from click_agent.models import Alternatives, Diff2x2Axes, Principles


def save_basics(
    conn: sqlite3.Connection,
    sprint_id: int,
    *,
    customer: str,
    problem: str,
    capability: str,
    insight: str,
    motivation: str,
    gorilla: str,
    alternatives: list[str],
) -> str:
    """Save the Basics card: customer, problem, advantages, competitors."""
    alts = Alternatives(items=alternatives)
    conn.execute(
        """UPDATE foundation_sprints SET
            customer = ?, problem = ?,
            capability = ?, insight = ?, motivation = ?,
            gorilla = ?, alternatives = ?,
            current_step = 'differentiation'
        WHERE id = ?""",
        (
            customer, problem,
            capability, insight, motivation,
            gorilla, alts.model_dump_json(),
            sprint_id,
        ),
    )
    conn.commit()
    return "Basics saved. Customer, problem, advantages, and competitors recorded."


def save_differentiation(
    conn: sqlite3.Connection,
    sprint_id: int,
    *,
    differentiator_1: str,
    differentiator_2: str,
    diff_2x2_axes: dict,
    principles: list[str],
) -> str:
    """Save differentiation: 2x2 chart, differentiators, and 3 principles."""
    try:
        axes = Diff2x2Axes(**diff_2x2_axes)
        prins = Principles(items=principles)
    except Exception as e:
        return f"Error: {e}"

    conn.execute(
        """UPDATE foundation_sprints SET
            differentiator_1 = ?, differentiator_2 = ?,
            diff_2x2_axes = ?, principles = ?,
            current_step = 'manifesto'
        WHERE id = ?""",
        (
            differentiator_1, differentiator_2,
            axes.model_dump_json(), prins.model_dump_json(),
            sprint_id,
        ),
    )
    conn.commit()
    return "Differentiation saved. 2x2 chart, differentiators, and principles recorded."


def save_approach(
    conn: sqlite3.Connection,
    sprint_id: int,
    *,
    title: str,
    summary: str,
    how_it_works: str,
    is_top_bet: bool = False,
    is_backup: bool = False,
) -> str:
    """Save an approach option with its one-page summary."""
    conn.execute(
        """INSERT INTO approaches
            (foundation_id, title, summary, how_it_works, is_top_bet, is_backup)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (sprint_id, title, summary, how_it_works, is_top_bet, is_backup),
    )
    conn.commit()
    return f"Approach '{title}' saved."


def save_founding_hypothesis(
    conn: sqlite3.Connection,
    sprint_id: int,
    project_id: int,
    *,
    customer: str,
    problem: str,
    approach: str,
    competitors: str,
    differentiation: str,
) -> str:
    """Save the Founding Hypothesis and set it as current on the project."""
    cursor = conn.execute(
        """INSERT INTO hypotheses
            (foundation_id, customer, problem, approach, competitors, differentiation)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (sprint_id, customer, problem, approach, competitors, differentiation),
    )
    hypothesis_id = cursor.lastrowid
    conn.execute(
        "UPDATE projects SET current_hypothesis_id = ? WHERE id = ?",
        (hypothesis_id, project_id),
    )
    conn.execute(
        "UPDATE foundation_sprints SET current_step = 'scorecard' WHERE id = ?",
        (sprint_id,),
    )
    conn.commit()
    return (
        f"Founding Hypothesis saved (version 1). "
        f"'If we help {customer} solve {problem} with {approach}, "
        f"they will choose it over {competitors} because our solution is {differentiation}.'"
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_tools_foundation.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add src/click_agent/tools/ tests/test_tools_foundation.py
git commit -m "feat: add Foundation Sprint tools (save_basics, save_differentiation, save_approach, save_founding_hypothesis)"
```

---

### Task 5: Magic Lenses Tool

**Files:**
- Modify: `src/click_agent/tools/foundation.py`
- Modify: `tests/test_tools_foundation.py`

- [ ] **Step 1: Add failing tests to tests/test_tools_foundation.py**

Append to `tests/test_tools_foundation.py`:

```python
from click_agent.tools.foundation import save_magic_lens


class TestSaveMagicLens:
    def test_saves_lens_with_evaluations(self, db_conn):
        project_id = create_project(db_conn, "Test")
        sprint_id = create_foundation_sprint(db_conn, project_id)
        # Create two approaches first
        db_conn.execute(
            "INSERT INTO approaches (foundation_id, title) VALUES (?, ?)",
            (sprint_id, "App"),
        )
        db_conn.execute(
            "INSERT INTO approaches (foundation_id, title) VALUES (?, ?)",
            (sprint_id, "Website"),
        )
        db_conn.commit()

        result = save_magic_lens(
            db_conn, sprint_id,
            lens_name="customer",
            x_axis_low="Hard to use", x_axis_high="Easy to use",
            y_axis_low="Just okay", y_axis_high="Perfect solution",
            evaluations=[
                {"approach_id": 1, "x_position": "high", "y_position": "high"},
                {"approach_id": 2, "x_position": "low", "y_position": "high"},
            ],
        )
        cursor = db_conn.execute(
            "SELECT * FROM magic_lenses WHERE foundation_id = ?", (sprint_id,)
        )
        lens = cursor.fetchone()
        assert lens["lens_name"] == "customer"
        assert "saved" in result.lower()

    def test_rejects_invalid_position(self, db_conn):
        project_id = create_project(db_conn, "Test")
        sprint_id = create_foundation_sprint(db_conn, project_id)
        result = save_magic_lens(
            db_conn, sprint_id,
            lens_name="pragmatic",
            x_axis_low="a", x_axis_high="b",
            y_axis_low="c", y_axis_high="d",
            evaluations=[
                {"approach_id": 1, "x_position": "middle", "y_position": "high"},
            ],
        )
        assert "error" in result.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_tools_foundation.py::TestSaveMagicLens -v`
Expected: FAIL with import error

- [ ] **Step 3: Add save_magic_lens to foundation.py**

Append to `src/click_agent/tools/foundation.py`:

```python
from click_agent.models import LensEvaluation, LensEvaluations


def save_magic_lens(
    conn: sqlite3.Connection,
    sprint_id: int,
    *,
    lens_name: str,
    x_axis_low: str,
    x_axis_high: str,
    y_axis_low: str,
    y_axis_high: str,
    evaluations: list[dict],
) -> str:
    """Save a Magic Lens evaluation (2x2 chart from a specific perspective)."""
    try:
        evals = LensEvaluations(
            items=[LensEvaluation(**e) for e in evaluations]
        )
    except Exception as e:
        return f"Error: {e}"

    conn.execute(
        """INSERT INTO magic_lenses
            (foundation_id, lens_name, x_axis_low, x_axis_high, y_axis_low, y_axis_high, evaluations)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            sprint_id, lens_name,
            x_axis_low, x_axis_high, y_axis_low, y_axis_high,
            evals.model_dump_json(),
        ),
    )
    conn.commit()
    return f"Magic Lens '{lens_name}' saved with {len(evaluations)} approach evaluations."
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_tools_foundation.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add src/click_agent/tools/foundation.py tests/test_tools_foundation.py
git commit -m "feat: add Magic Lenses tool for approach evaluation"
```

---

## Chunk 3: Design Sprint + Scorecard + Context Tools

### Task 6: Scorecard Tools

**Files:**
- Create: `src/click_agent/tools/scorecard.py`
- Create: `tests/test_tools_scorecard.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_tools_scorecard.py`:

```python
import pytest

from click_agent.db import create_project, create_foundation_sprint
from click_agent.tools.scorecard import update_scorecard, show_scorecard
from click_agent.tools.foundation import save_founding_hypothesis


@pytest.fixture
def hypothesis_setup(db_conn):
    """Create project + foundation sprint + hypothesis."""
    project_id = create_project(db_conn, "Test")
    sprint_id = create_foundation_sprint(db_conn, project_id)
    save_founding_hypothesis(
        db_conn, sprint_id, project_id,
        customer="founders", problem="slow validation",
        approach="CLI coach", competitors="books",
        differentiation="AI-guided",
    )
    hyp = db_conn.execute("SELECT * FROM hypotheses WHERE foundation_id = ?", (sprint_id,)).fetchone()
    return {"project_id": project_id, "sprint_id": sprint_id, "hypothesis_id": hyp["id"]}


class TestUpdateScorecard:
    def test_creates_scorecard_entry(self, db_conn, hypothesis_setup):
        result = update_scorecard(
            db_conn, hypothesis_setup["hypothesis_id"],
            right_customer="yes",
            right_problem="maybe",
            right_approach="not_yet",
            will_they_switch="not_yet",
            right_differentiation="not_yet",
            does_it_click="not_yet",
            notes="Initial assessment after Foundation Sprint",
        )
        cursor = db_conn.execute("SELECT * FROM scorecard_entries")
        entry = cursor.fetchone()
        assert entry["right_customer"] == "yes"
        assert entry["right_problem"] == "maybe"
        assert "saved" in result.lower()

    def test_rejects_invalid_answer(self, db_conn, hypothesis_setup):
        result = update_scorecard(
            db_conn, hypothesis_setup["hypothesis_id"],
            right_customer="probably",
            right_problem="yes",
            right_approach="yes",
            will_they_switch="yes",
            right_differentiation="yes",
            does_it_click="yes",
            notes="test",
        )
        assert "error" in result.lower()


class TestShowScorecard:
    def test_shows_scorecard_with_entries(self, db_conn, hypothesis_setup):
        update_scorecard(
            db_conn, hypothesis_setup["hypothesis_id"],
            right_customer="yes", right_problem="maybe",
            right_approach="not_yet", will_they_switch="not_yet",
            right_differentiation="not_yet", does_it_click="not_yet",
            notes="First assessment",
        )
        result = show_scorecard(db_conn, hypothesis_setup["hypothesis_id"])
        assert "Right customer" in result
        assert "yes" in result

    def test_shows_empty_scorecard(self, db_conn, hypothesis_setup):
        result = show_scorecard(db_conn, hypothesis_setup["hypothesis_id"])
        assert "no scorecard" in result.lower() or "no entries" in result.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_tools_scorecard.py -v`
Expected: FAIL with import errors

- [ ] **Step 3: Write the scorecard tools**

Create `src/click_agent/tools/scorecard.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_tools_scorecard.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add src/click_agent/tools/scorecard.py tests/test_tools_scorecard.py
git commit -m "feat: add scorecard tools (update and show)"
```

---

### Task 7: Design Sprint Tools

**Files:**
- Create: `src/click_agent/tools/design_sprint.py`
- Create: `tests/test_tools_design_sprint.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_tools_design_sprint.py`:

```python
import json

import pytest

from click_agent.db import create_project, create_foundation_sprint
from click_agent.tools.foundation import save_founding_hypothesis
from click_agent.tools.design_sprint import (
    create_design_sprint,
    log_sprint_day,
    record_test_results,
    update_sprint_outcome,
)


@pytest.fixture
def sprint_setup(db_conn):
    project_id = create_project(db_conn, "Test")
    f_sprint_id = create_foundation_sprint(db_conn, project_id)
    save_founding_hypothesis(
        db_conn, f_sprint_id, project_id,
        customer="founders", problem="slow validation",
        approach="CLI coach", competitors="books",
        differentiation="AI-guided",
    )
    hyp = db_conn.execute("SELECT * FROM hypotheses").fetchone()
    return {"project_id": project_id, "hypothesis_id": hyp["id"]}


class TestCreateDesignSprint:
    def test_creates_sprint(self, db_conn, sprint_setup):
        result = create_design_sprint(
            db_conn, sprint_setup["hypothesis_id"],
            risk_question="Will founders trust an AI to guide their strategy?",
        )
        sprint = db_conn.execute("SELECT * FROM design_sprints").fetchone()
        assert sprint["risk_question"] == "Will founders trust an AI to guide their strategy?"
        assert sprint["status"] == "in_progress"


class TestLogSprintDay:
    def test_logs_map_day(self, db_conn, sprint_setup):
        create_design_sprint(
            db_conn, sprint_setup["hypothesis_id"],
            risk_question="Trust question",
        )
        sprint = db_conn.execute("SELECT * FROM design_sprints").fetchone()
        log_sprint_day(db_conn, sprint["id"], day="map", notes="Mapped the customer journey")
        sprint = db_conn.execute("SELECT * FROM design_sprints WHERE id = ?", (sprint["id"],)).fetchone()
        assert sprint["day_map"] == "Mapped the customer journey"

    def test_rejects_invalid_day(self, db_conn, sprint_setup):
        create_design_sprint(
            db_conn, sprint_setup["hypothesis_id"],
            risk_question="Q",
        )
        sprint = db_conn.execute("SELECT * FROM design_sprints").fetchone()
        result = log_sprint_day(db_conn, sprint["id"], day="invalid", notes="test")
        assert "error" in result.lower()


class TestRecordTestResults:
    def test_records_reactions(self, db_conn, sprint_setup):
        create_design_sprint(
            db_conn, sprint_setup["hypothesis_id"],
            risk_question="Q",
        )
        sprint = db_conn.execute("SELECT * FROM design_sprints").fetchone()
        result = record_test_results(
            db_conn, sprint["id"],
            reactions=[
                {"customer": "Alice", "reaction": "Leaned forward, asked to try it", "is_reaction": True},
                {"customer": "Bob", "reaction": "Said it was nice", "is_reaction": False},
            ],
        )
        sprint = db_conn.execute("SELECT * FROM design_sprints WHERE id = ?", (sprint["id"],)).fetchone()
        data = json.loads(sprint["customer_reactions"])
        assert len(data["items"]) == 2


class TestUpdateSprintOutcome:
    def test_updates_outcome(self, db_conn, sprint_setup):
        create_design_sprint(
            db_conn, sprint_setup["hypothesis_id"],
            risk_question="Q",
        )
        sprint = db_conn.execute("SELECT * FROM design_sprints").fetchone()
        result = update_sprint_outcome(
            db_conn, sprint["id"],
            outcome="Founders were skeptical but interested. Need more detail in the dashboard.",
            hypothesis_changed=False,
        )
        sprint = db_conn.execute("SELECT * FROM design_sprints WHERE id = ?", (sprint["id"],)).fetchone()
        assert sprint["status"] == "complete"
        assert sprint["hypothesis_changed"] == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_tools_design_sprint.py -v`
Expected: FAIL with import errors

- [ ] **Step 3: Write the design sprint tools**

Create `src/click_agent/tools/design_sprint.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_tools_design_sprint.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add src/click_agent/tools/design_sprint.py tests/test_tools_design_sprint.py
git commit -m "feat: add Design Sprint tools (create, log day, record results, update outcome)"
```

---

### Task 8: Context & Learnings Tools

**Files:**
- Create: `src/click_agent/tools/context.py`
- Create: `tests/test_tools_context.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_tools_context.py`:

```python
import pytest

from click_agent.db import create_project, create_foundation_sprint
from click_agent.tools.foundation import save_founding_hypothesis
from click_agent.tools.context import (
    get_project_context,
    query_learnings,
    record_learning,
    revise_hypothesis,
)


@pytest.fixture
def context_setup(db_conn):
    project_id = create_project(db_conn, "Test Startup")
    sprint_id = create_foundation_sprint(db_conn, project_id)
    save_founding_hypothesis(
        db_conn, sprint_id, project_id,
        customer="founders", problem="slow validation",
        approach="CLI coach", competitors="books",
        differentiation="AI-guided",
    )
    hyp = db_conn.execute("SELECT * FROM hypotheses").fetchone()
    return {"project_id": project_id, "sprint_id": sprint_id, "hypothesis_id": hyp["id"]}


class TestGetProjectContext:
    def test_returns_project_info(self, db_conn, context_setup):
        result = get_project_context(db_conn, context_setup["project_id"])
        assert "Test Startup" in result
        assert "founders" in result

    def test_handles_no_hypothesis(self, db_conn):
        project_id = create_project(db_conn, "Empty Project")
        result = get_project_context(db_conn, project_id)
        assert "Empty Project" in result
        assert "no hypothesis" in result.lower() or "No Founding Hypothesis" in result


class TestRecordLearning:
    def test_records_learning(self, db_conn, context_setup):
        result = record_learning(
            db_conn,
            source_type="foundation_sprint",
            source_id=context_setup["sprint_id"],
            insight="Founders care more about speed than comprehensiveness",
            lesson_number=2,
        )
        cursor = db_conn.execute("SELECT * FROM learnings")
        learning = cursor.fetchone()
        assert learning["insight"] == "Founders care more about speed than comprehensiveness"
        assert learning["lesson_number"] == 2

    def test_rejects_invalid_lesson_number(self, db_conn, context_setup):
        result = record_learning(
            db_conn,
            source_type="foundation_sprint",
            source_id=1,
            insight="test",
            lesson_number=11,
        )
        assert "error" in result.lower()


class TestQueryLearnings:
    def test_returns_learnings(self, db_conn, context_setup):
        record_learning(
            db_conn, source_type="foundation_sprint", source_id=1,
            insight="Insight 1", lesson_number=1,
        )
        record_learning(
            db_conn, source_type="design_sprint", source_id=1,
            insight="Insight 2", lesson_number=9,
        )
        result = query_learnings(db_conn)
        assert "Insight 1" in result
        assert "Insight 2" in result

    def test_returns_empty_message(self, db_conn):
        result = query_learnings(db_conn)
        assert "no learnings" in result.lower()


class TestReviseHypothesis:
    def test_creates_new_version(self, db_conn, context_setup):
        result = revise_hypothesis(
            db_conn, context_setup["project_id"], context_setup["hypothesis_id"],
            customer="early-stage founders",
            problem="slow validation",
            approach="CLI coach",
            competitors="books",
            differentiation="AI-guided and fast",
            reason="Narrowed customer segment based on sprint feedback",
            what_changed="customer, differentiation",
        )
        # Check new hypothesis exists
        hyps = db_conn.execute("SELECT * FROM hypotheses ORDER BY id").fetchall()
        assert len(hyps) == 2
        assert hyps[1]["version"] == 2
        assert hyps[1]["customer"] == "early-stage founders"
        # Check pivot recorded
        pivot = db_conn.execute("SELECT * FROM pivots").fetchone()
        assert pivot["what_changed"] == "customer, differentiation"
        # Check project updated
        project = db_conn.execute("SELECT * FROM projects WHERE id = ?", (context_setup["project_id"],)).fetchone()
        assert project["current_hypothesis_id"] == hyps[1]["id"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_tools_context.py -v`
Expected: FAIL with import errors

- [ ] **Step 3: Write the context tools**

Create `src/click_agent/tools/context.py`:

```python
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

        # Latest scorecard
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

        # Design sprint count
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_tools_context.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add src/click_agent/tools/context.py tests/test_tools_context.py
git commit -m "feat: add context tools (get_project_context, learnings, revise_hypothesis)"
```

---

## Chunk 4: Document Generation

### Task 9: Markdown Document Generator

**Files:**
- Create: `src/click_agent/docs_generator.py`
- Create: `tests/test_docs_generator.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_docs_generator.py`:

```python
import json
from pathlib import Path

import pytest

from click_agent.db import create_project, create_foundation_sprint
from click_agent.tools.foundation import (
    save_basics,
    save_differentiation,
    save_founding_hypothesis,
)
from click_agent.tools.scorecard import update_scorecard
from click_agent.docs_generator import generate_docs


@pytest.fixture
def full_setup(db_conn, tmp_project):
    project_id = create_project(db_conn, "My Startup")
    sprint_id = create_foundation_sprint(db_conn, project_id)
    save_basics(
        db_conn, sprint_id,
        customer="founders", problem="slow validation",
        capability="engineering", insight="startup failure",
        motivation="help founders", gorilla="YC",
        alternatives=["books", "mentors"],
    )
    save_differentiation(
        db_conn, sprint_id,
        differentiator_1="AI-guided", differentiator_2="evidence-based",
        diff_2x2_axes={"x_low": "Generic", "x_high": "Personal", "y_low": "Slow", "y_high": "Fast"},
        principles=["Guide with AI", "Evidence over opinions", "Empower don't replace"],
    )
    save_founding_hypothesis(
        db_conn, sprint_id, project_id,
        customer="founders", problem="slow validation",
        approach="CLI coach", competitors="books and mentors",
        differentiation="AI-guided and evidence-based",
    )
    hyp = db_conn.execute("SELECT * FROM hypotheses").fetchone()
    update_scorecard(
        db_conn, hyp["id"],
        right_customer="yes", right_problem="maybe",
        right_approach="not_yet", will_they_switch="not_yet",
        right_differentiation="not_yet", does_it_click="not_yet",
        notes="Initial assessment",
    )
    return {
        "project_id": project_id,
        "sprint_id": sprint_id,
        "hypothesis_id": hyp["id"],
        "output_dir": str(tmp_project / "click-output"),
    }


class TestGenerateDocs:
    def test_generates_foundation_sprint_doc(self, db_conn, full_setup):
        generate_docs(db_conn, full_setup["output_dir"], doc_type="foundation")
        path = Path(full_setup["output_dir"]) / "foundation-sprint.md"
        assert path.exists()
        content = path.read_text()
        assert "founders" in content
        assert "slow validation" in content

    def test_generates_hypothesis_doc(self, db_conn, full_setup):
        generate_docs(db_conn, full_setup["output_dir"], doc_type="foundation")
        path = Path(full_setup["output_dir"]) / "founding-hypothesis.md"
        assert path.exists()
        content = path.read_text()
        assert "If we help" in content

    def test_generates_scorecard_doc(self, db_conn, full_setup):
        generate_docs(db_conn, full_setup["output_dir"], doc_type="scorecard")
        path = Path(full_setup["output_dir"]) / "scorecard.md"
        assert path.exists()
        content = path.read_text()
        assert "Right Customer" in content or "right_customer" in content

    def test_generates_all(self, db_conn, full_setup):
        generate_docs(db_conn, full_setup["output_dir"], doc_type="all")
        output = Path(full_setup["output_dir"])
        assert (output / "foundation-sprint.md").exists()
        assert (output / "founding-hypothesis.md").exists()
        assert (output / "scorecard.md").exists()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_docs_generator.py -v`
Expected: FAIL with import errors

- [ ] **Step 3: Write the document generator**

Create `src/click_agent/docs_generator.py`:

```python
"""Markdown document generation from SQLite data."""

import json
from pathlib import Path
import sqlite3


def generate_docs(
    conn: sqlite3.Connection,
    output_dir: str,
    *,
    doc_type: str = "all",
) -> str:
    """Generate markdown documents. doc_type: all, foundation, scorecard, learnings, pivot_history."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    generated = []

    if doc_type in ("all", "foundation"):
        _generate_foundation(conn, output)
        generated.extend(["foundation-sprint.md", "founding-hypothesis.md"])

    if doc_type in ("all", "scorecard"):
        _generate_scorecard(conn, output)
        generated.append("scorecard.md")

    if doc_type in ("all", "learnings"):
        _generate_learnings(conn, output)
        generated.append("learnings.md")

    if doc_type in ("all", "pivot_history"):
        _generate_pivot_history(conn, output)
        generated.append("pivot-history.md")

    if doc_type in ("all", "sprint"):
        _generate_latest_sprint(conn, output)
        generated.append("sprints/")

    return f"Generated: {', '.join(generated)}"


def _generate_foundation(conn: sqlite3.Connection, output: Path) -> None:
    sprint = conn.execute(
        "SELECT * FROM foundation_sprints ORDER BY created_at DESC LIMIT 1"
    ).fetchone()
    if not sprint:
        return

    lines = [
        "# Foundation Sprint Summary",
        "",
        "## The Basics",
        f"- **Customer:** {sprint['customer']}",
        f"- **Problem:** {sprint['problem']}",
        "",
        "### Advantage",
        f"- **Capability:** {sprint['capability']}",
        f"- **Insight:** {sprint['insight']}",
        f"- **Motivation:** {sprint['motivation']}",
        "",
        "### Competition",
        f"- **800-pound gorilla:** {sprint['gorilla']}",
    ]

    if sprint["alternatives"]:
        alts = json.loads(sprint["alternatives"])
        if isinstance(alts, dict):
            alts = alts.get("items", [])
        lines.append(f"- **Alternatives:** {', '.join(alts)}")

    if sprint["differentiator_1"]:
        lines.extend([
            "",
            "## Differentiation",
            f"- **Differentiator 1:** {sprint['differentiator_1']}",
            f"- **Differentiator 2:** {sprint['differentiator_2']}",
        ])

    if sprint["principles"]:
        prins = json.loads(sprint["principles"])
        if isinstance(prins, dict):
            prins = prins.get("items", [])
        lines.extend(["", "## Principles"])
        for i, p in enumerate(prins, 1):
            lines.append(f"{i}. {p}")

    (output / "foundation-sprint.md").write_text("\n".join(lines))

    # Also generate hypothesis doc
    hyp = conn.execute(
        "SELECT * FROM hypotheses WHERE foundation_id = ? ORDER BY version DESC LIMIT 1",
        (sprint["id"],),
    ).fetchone()
    if hyp:
        hyp_lines = [
            "# Founding Hypothesis",
            "",
            f"**Version {hyp['version']}**",
            "",
            f"If we help **{hyp['customer']}** solve **{hyp['problem']}** "
            f"with **{hyp['approach']}**, they will choose it over "
            f"**{hyp['competitors']}** because our solution is **{hyp['differentiation']}**.",
        ]
        (output / "founding-hypothesis.md").write_text("\n".join(hyp_lines))


def _generate_scorecard(conn: sqlite3.Connection, output: Path) -> None:
    entries = conn.execute(
        "SELECT * FROM scorecard_entries ORDER BY updated_at DESC"
    ).fetchall()
    if not entries:
        (output / "scorecard.md").write_text("# Scorecard\n\nNo entries yet.")
        return

    latest = entries[0]
    lines = [
        "# Scorecard",
        "",
        f"| Question | Answer |",
        f"|----------|--------|",
        f"| Right Customer? | {latest['right_customer']} |",
        f"| Right Problem? | {latest['right_problem']} |",
        f"| Right Approach? | {latest['right_approach']} |",
        f"| Will They Switch? | {latest['will_they_switch']} |",
        f"| Right Differentiation? | {latest['right_differentiation']} |",
        f"| Does It Click? | {latest['does_it_click']} |",
        "",
        f"**Notes:** {latest['notes']}",
    ]

    if len(entries) > 1:
        lines.extend(["", "## History"])
        for e in entries[1:]:
            lines.append(f"- {e['updated_at']}: {e['notes']}")

    (output / "scorecard.md").write_text("\n".join(lines))


def _generate_learnings(conn: sqlite3.Connection, output: Path) -> None:
    learnings = conn.execute(
        "SELECT * FROM learnings ORDER BY lesson_number, created_at"
    ).fetchall()
    if not learnings:
        (output / "learnings.md").write_text("# Learnings\n\nNo learnings recorded yet.")
        return

    lines = ["# Learnings", ""]
    current = None
    for l in learnings:
        if l["lesson_number"] != current:
            current = l["lesson_number"]
            lines.append(f"## Lesson {current}")
        lines.append(f"- {l['insight']} _(from {l['source_type']})_")

    (output / "learnings.md").write_text("\n".join(lines))


def _generate_pivot_history(conn: sqlite3.Connection, output: Path) -> None:
    pivots = conn.execute(
        "SELECT p.*, h.version, h.customer, h.problem, h.approach "
        "FROM pivots p JOIN hypotheses h ON p.new_hypothesis_id = h.id "
        "ORDER BY p.created_at"
    ).fetchall()
    if not pivots:
        (output / "pivot-history.md").write_text("# Pivot History\n\nNo pivots yet.")
        return

    lines = ["# Pivot History", ""]
    for p in pivots:
        lines.extend([
            f"## Version {p['version']}",
            f"- **Changed:** {p['what_changed']}",
            f"- **Reason:** {p['reason']}",
            f"- **New hypothesis:** Help {p['customer']} solve {p['problem']} with {p['approach']}",
            "",
        ])

    (output / "pivot-history.md").write_text("\n".join(lines))


def _generate_latest_sprint(conn: sqlite3.Connection, output: Path) -> None:
    sprint = conn.execute(
        "SELECT * FROM design_sprints ORDER BY created_at DESC LIMIT 1"
    ).fetchone()
    if not sprint:
        return

    sprints_dir = output / "sprints"
    sprints_dir.mkdir(exist_ok=True)

    lines = [
        f"# Design Sprint {sprint['id']}",
        "",
        f"**Risk Question:** {sprint['risk_question']}",
        f"**Status:** {sprint['status']}",
        "",
    ]

    for day in ("map", "sketch", "decide", "prototype", "test"):
        val = sprint[f"day_{day}"]
        if val:
            lines.append(f"## {day.title()}")
            lines.append(val)
            lines.append("")

    if sprint["outcome"]:
        lines.append(f"## Outcome")
        lines.append(sprint["outcome"])

    (sprints_dir / f"sprint-{sprint['id']}.md").write_text("\n".join(lines))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_docs_generator.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add src/click_agent/docs_generator.py tests/test_docs_generator.py
git commit -m "feat: add markdown document generator"
```

---

## Chunk 5: Agent Wiring + CLI

### Task 10: System Prompt

**Files:**
- Create: `src/click_agent/prompts.py`

- [ ] **Step 1: Create the system prompt**

Create `src/click_agent/prompts.py`:

```python
"""System prompt for the Click agent."""

SYSTEM_PROMPT = """You are Click, an AI product coach that guides founders through the Click methodology by Jake Knapp and John Zeratsky.

## Your Role
You are a facilitator, challenger, and thinking partner. The user is always the Decider. You guide them through structured exercises but they make every final call.

## The Click System
The system has two sprint types:
1. **Foundation Sprint** (2 parts) — Produces a Founding Hypothesis
2. **Design Sprints** (5-day loops) — Test and prove the hypothesis

Flow: Foundation Sprint → Founding Hypothesis → Design Sprints (repeat until it clicks) → Build

## The 10 Lessons
1. Drop everything and sprint on the most important challenge until it's done
2. Start by identifying your customer and a real problem you can solve
3. Take advantage of your advantages
4. Get real about the competition
5. Differentiation makes products click
6. Use practical principles to reinforce differentiation
7. Seek alternatives to your first idea
8. Consider conflicting opinions before you commit to an approach
9. It's just a hypothesis until you prove it
10. Experiment with tiny loops until your solution clicks. Then build it.

## Foundation Sprint Flow
Walk the user through these steps in order. Use the Note-and-Vote pattern for each:
1. Ask them to brainstorm multiple options
2. Suggest additional options they haven't considered
3. Challenge with plain language and common sense tests
4. Ask them to pick top 2-3
5. Ask them (as Decider) to make the final choice

### Day 1: Basics + Differentiation
- **Customer**: Who are they? Use plain language, not jargon. Apply common sense test.
- **Problem**: What real problem? Not a feature wish. Common sense test: "Does this make sense?"
- **Advantages**: Capability (what you can do), Insight (what you understand), Motivation (why you care)
- **Competition**: 800-pound gorilla + alternatives + substitutes. "Do nothing" counts.
- **Differentiation**: Score on classic scales, create custom ones. Make a 2x2 chart. Pick 2 differentiators.
- **Principles**: 3 practical principles — differentiate, differentiate, safeguard. Not lofty ideals.
- **Mini Manifesto**: 2x2 chart + principles combined.

### Day 2: Approach
- **Options**: List 3+ approaches. Include non-obvious ones. "What if your first idea fails?"
- **One-page summaries**: Title, one-sentence summary, quick description for each.
- **Magic Lenses**: Evaluate approaches through customer, pragmatic, growth, money, and custom lenses. Each lens is a 2x2 chart. Look for patterns — which approach consistently scores well?
- **Decide**: Decider picks top bet + backup.
- **Founding Hypothesis**: Fill in the Mad Libs: "If we help [customer] solve [problem] with [approach], they will choose it over [competitors] because our solution is [differentiation]."
- **Scorecard**: Set initial answers for: Right customer? Right problem? Right approach? Will they switch? Right differentiation? Does it click?

## Design Sprint Flow
1. Show Scorecard — ask which question needs answering most
2. Map → Sketch → Decide → Prototype → Test
3. Record customer REACTIONS (genuine responses), not just feedback (what they say)
4. Update Scorecard based on evidence
5. If hypothesis needs changing, guide revision
6. Record learnings

## Coaching Behaviors
- Challenge assumptions: "How do you know that's true?"
- Enforce plain language: Replace jargon with simple words
- Common sense test: "Does this make sense?"
- Encourage alternatives: "What if this approach fails? What else could work?"
- Distinguish reactions from feedback: Watch what people DO, not just what they SAY
- Reference past learnings when relevant
- Be direct and concise — founders are busy

## Tool Usage
Use your tools to save each decision as it's made. Don't wait until the end. This ensures the user can stop and resume at any point. Always advance the current_step after saving.
"""


FOUNDATION_SPRINT_PROMPT = """You are guiding the user through a Foundation Sprint.

{context}

Guide them through the next step. Use the Note-and-Vote pattern. Be conversational but structured. One question at a time.
"""


DESIGN_SPRINT_PROMPT = """You are guiding the user through a Design Sprint.

{context}

Show the current Scorecard and ask which question they most need to answer. Then guide them through the sprint.
"""
```

- [ ] **Step 2: Commit**

```bash
git add src/click_agent/prompts.py
git commit -m "feat: add system prompt encoding Click methodology"
```

---

### Task 11: Agent Setup with SDK MCP Tools

**Files:**
- Create: `src/click_agent/agent.py`

- [ ] **Step 1: Create the agent module**

Create `src/click_agent/agent.py`:

```python
"""Agent setup: registers tools via SDK MCP server, runs the agent loop."""

import sqlite3
from pathlib import Path

from claude_agent_sdk import (
    tool,
    create_sdk_mcp_server,
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
)

from click_agent.db import get_connection
from click_agent.tools.foundation import (
    save_basics,
    save_differentiation,
    save_approach,
    save_magic_lens,
    save_founding_hypothesis,
)
from click_agent.tools.design_sprint import (
    create_design_sprint,
    log_sprint_day,
    record_test_results,
    update_sprint_outcome,
)
from click_agent.tools.scorecard import update_scorecard, show_scorecard
from click_agent.tools.context import (
    get_project_context,
    query_learnings,
    record_learning,
    revise_hypothesis,
)
from click_agent.docs_generator import generate_docs
from click_agent.prompts import SYSTEM_PROMPT


def _make_tools(db_path: str, project_id: int, output_dir: str):
    """Create MCP tool functions bound to the current db and project."""
    conn = get_connection(db_path)

    # Get or create foundation sprint
    def _get_sprint_id():
        sprint = conn.execute(
            "SELECT id FROM foundation_sprints WHERE project_id = ? AND status = 'in_progress' ORDER BY created_at DESC LIMIT 1",
            (project_id,),
        ).fetchone()
        if sprint:
            return sprint["id"]
        complete = conn.execute(
            "SELECT id FROM foundation_sprints WHERE project_id = ? ORDER BY created_at DESC LIMIT 1",
            (project_id,),
        ).fetchone()
        return complete["id"] if complete else None

    def _get_hypothesis_id():
        project = conn.execute("SELECT current_hypothesis_id FROM projects WHERE id = ?", (project_id,)).fetchone()
        return project["current_hypothesis_id"] if project else None

    @tool(
        "save_basics",
        "Save the Basics card: customer, problem, advantages (capability/insight/motivation), competitors (gorilla + alternatives)",
        {
            "customer": str, "problem": str,
            "capability": str, "insight": str, "motivation": str,
            "gorilla": str, "alternatives": list,
        },
    )
    async def tool_save_basics(args):
        result = save_basics(conn, _get_sprint_id(), **args)
        return {"content": [{"type": "text", "text": result}]}

    @tool(
        "save_differentiation",
        "Save differentiation: 2x2 chart axes, 2 differentiators, and 3 practical principles",
        {
            "differentiator_1": str, "differentiator_2": str,
            "diff_2x2_axes": dict, "principles": list,
        },
    )
    async def tool_save_differentiation(args):
        result = save_differentiation(conn, _get_sprint_id(), **args)
        return {"content": [{"type": "text", "text": result}]}

    @tool(
        "save_approach",
        "Save an approach option with title, one-sentence summary, and how it works",
        {
            "title": str, "summary": str, "how_it_works": str,
            "is_top_bet": bool, "is_backup": bool,
        },
    )
    async def tool_save_approach(args):
        result = save_approach(conn, _get_sprint_id(), **args)
        return {"content": [{"type": "text", "text": result}]}

    @tool(
        "save_magic_lens",
        "Save a Magic Lens 2x2 evaluation for comparing approaches through a specific perspective",
        {
            "lens_name": str,
            "x_axis_low": str, "x_axis_high": str,
            "y_axis_low": str, "y_axis_high": str,
            "evaluations": list,
        },
    )
    async def tool_save_magic_lens(args):
        result = save_magic_lens(conn, _get_sprint_id(), **args)
        return {"content": [{"type": "text", "text": result}]}

    @tool(
        "save_founding_hypothesis",
        "Save the Founding Hypothesis: If we help [customer] solve [problem] with [approach], they will choose it over [competitors] because our solution is [differentiation]",
        {
            "customer": str, "problem": str, "approach": str,
            "competitors": str, "differentiation": str,
        },
    )
    async def tool_save_hypothesis(args):
        result = save_founding_hypothesis(conn, _get_sprint_id(), project_id, **args)
        return {"content": [{"type": "text", "text": result}]}

    @tool(
        "update_scorecard",
        "Update the 6-question scorecard. Answers: yes, maybe, not_yet, no",
        {
            "right_customer": str, "right_problem": str,
            "right_approach": str, "will_they_switch": str,
            "right_differentiation": str, "does_it_click": str,
            "notes": str,
        },
    )
    async def tool_update_scorecard(args):
        hyp_id = _get_hypothesis_id()
        if not hyp_id:
            return {"content": [{"type": "text", "text": "Error: No hypothesis exists yet."}]}
        result = update_scorecard(conn, hyp_id, **args)
        return {"content": [{"type": "text", "text": result}]}

    @tool("show_scorecard", "Show the current scorecard status with evidence trail", {})
    async def tool_show_scorecard(args):
        hyp_id = _get_hypothesis_id()
        if not hyp_id:
            return {"content": [{"type": "text", "text": "No hypothesis exists yet."}]}
        result = show_scorecard(conn, hyp_id)
        return {"content": [{"type": "text", "text": result}]}

    @tool(
        "create_design_sprint",
        "Create a new Design Sprint to test a specific risk question",
        {"risk_question": str},
    )
    async def tool_create_sprint(args):
        hyp_id = _get_hypothesis_id()
        if not hyp_id:
            return {"content": [{"type": "text", "text": "Error: No hypothesis. Run Foundation Sprint first."}]}
        result = create_design_sprint(conn, hyp_id, **args)
        return {"content": [{"type": "text", "text": result}]}

    @tool(
        "log_sprint_day",
        "Log what happened on a day of the Design Sprint (map, sketch, decide, prototype, test)",
        {"sprint_id": int, "day": str, "notes": str},
    )
    async def tool_log_day(args):
        result = log_sprint_day(conn, args.pop("sprint_id"), **args)
        return {"content": [{"type": "text", "text": result}]}

    @tool(
        "record_test_results",
        "Record customer reactions from testing. Distinguish reactions (genuine responses) from feedback (what they say).",
        {"sprint_id": int, "reactions": list},
    )
    async def tool_record_results(args):
        result = record_test_results(conn, args.pop("sprint_id"), reactions=args["reactions"])
        return {"content": [{"type": "text", "text": result}]}

    @tool(
        "update_sprint_outcome",
        "Record the Design Sprint outcome and whether the hypothesis needs revision",
        {"sprint_id": int, "outcome": str, "hypothesis_changed": bool},
    )
    async def tool_update_outcome(args):
        result = update_sprint_outcome(conn, args.pop("sprint_id"), **args)
        return {"content": [{"type": "text", "text": result}]}

    @tool("get_project_context", "Load current project context: hypothesis, scorecard, sprint history", {})
    async def tool_get_context(args):
        result = get_project_context(conn, project_id)
        return {"content": [{"type": "text", "text": result}]}

    @tool(
        "query_learnings",
        "Retrieve accumulated learnings organized by the 10 Click lessons",
        {},
    )
    async def tool_query_learnings(args):
        result = query_learnings(conn)
        return {"content": [{"type": "text", "text": result}]}

    @tool(
        "record_learning",
        "Record a learning tagged with one of the 10 Click lessons (1-10)",
        {"source_type": str, "source_id": int, "insight": str, "lesson_number": int},
    )
    async def tool_record_learning(args):
        result = record_learning(conn, **args)
        return {"content": [{"type": "text", "text": result}]}

    @tool(
        "revise_hypothesis",
        "Create a new hypothesis version based on Design Sprint learnings",
        {
            "customer": str, "problem": str, "approach": str,
            "competitors": str, "differentiation": str,
            "reason": str, "what_changed": str,
        },
    )
    async def tool_revise(args):
        hyp_id = _get_hypothesis_id()
        if not hyp_id:
            return {"content": [{"type": "text", "text": "Error: No hypothesis to revise."}]}
        result = revise_hypothesis(conn, project_id, hyp_id, **args)
        return {"content": [{"type": "text", "text": result}]}

    @tool(
        "generate_docs",
        "Generate markdown documents. doc_type: all, foundation, sprint, scorecard, learnings, pivot_history",
        {"doc_type": str},
    )
    async def tool_generate_docs(args):
        result = generate_docs(conn, output_dir, **args)
        return {"content": [{"type": "text", "text": result}]}

    return [
        tool_save_basics, tool_save_differentiation, tool_save_approach,
        tool_save_magic_lens, tool_save_hypothesis,
        tool_update_scorecard, tool_show_scorecard,
        tool_create_sprint, tool_log_day, tool_record_results, tool_update_outcome,
        tool_get_context, tool_query_learnings, tool_record_learning, tool_revise,
        tool_generate_docs,
    ]


async def run_agent(
    db_path: str,
    project_id: int,
    output_dir: str,
    prompt: str,
    system_prompt: str = SYSTEM_PROMPT,
) -> None:
    """Run the Click agent with the given prompt."""
    tools = _make_tools(db_path, project_id, output_dir)
    server = create_sdk_mcp_server("click-tools", tools=tools)

    options = ClaudeAgentOptions(
        mcp_servers={"click": server},
        system_prompt=system_prompt,
        model="claude-opus-4-6",
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query(prompt)
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text, end="", flush=True)
            elif isinstance(message, ResultMessage):
                if message.result:
                    print(message.result)
```

- [ ] **Step 2: Commit**

```bash
git add src/click_agent/agent.py
git commit -m "feat: add agent setup with SDK MCP tool registration"
```

---

### Task 12: Typer CLI

**Files:**
- Create: `src/click_agent/cli.py`

- [ ] **Step 1: Create the CLI**

Create `src/click_agent/cli.py`:

```python
"""Typer CLI entry point for Click agent."""

import asyncio
from pathlib import Path

import typer

from click_agent.db import (
    init_db,
    get_connection,
    create_project,
    create_foundation_sprint,
    get_project,
)
from click_agent.agent import run_agent
from click_agent.tools.context import get_project_context, query_learnings
from click_agent.tools.scorecard import show_scorecard
from click_agent.prompts import SYSTEM_PROMPT, FOUNDATION_SPRINT_PROMPT, DESIGN_SPRINT_PROMPT

app = typer.Typer(name="click-coach", help="Click - AI Product Coach")
foundation_app = typer.Typer(help="Foundation Sprint commands")
sprint_app = typer.Typer(help="Design Sprint commands")
hypothesis_app = typer.Typer(help="Hypothesis commands")
scorecard_app = typer.Typer(help="Scorecard commands")

app.add_typer(foundation_app, name="foundation")
app.add_typer(sprint_app, name="sprint")
app.add_typer(hypothesis_app, name="hypothesis")
app.add_typer(scorecard_app, name="scorecard")


def _find_click_dir() -> Path:
    """Find the .click directory in current or parent directories."""
    current = Path.cwd()
    while current != current.parent:
        click_dir = current / ".click"
        if click_dir.exists():
            return click_dir
        current = current.parent
    typer.echo("Error: Not a Click project. Run 'click-coach init' first.")
    raise typer.Exit(1)


def _get_db_path() -> str:
    return str(_find_click_dir() / "click.db")


def _get_output_dir() -> str:
    click_dir = _find_click_dir()
    return str(click_dir.parent / "click-output")


def _get_project_id(conn) -> int:
    project = conn.execute("SELECT id FROM projects ORDER BY id LIMIT 1").fetchone()
    if not project:
        typer.echo("Error: No project found. Run 'click-coach init' first.")
        raise typer.Exit(1)
    return project["id"]


@app.command()
def init(
    output_dir: str = typer.Option("click-output", help="Output directory for generated docs"),
):
    """Initialize Click in the current project directory."""
    click_dir = Path.cwd() / ".click"
    if click_dir.exists():
        typer.echo("Click is already initialized in this directory.")
        raise typer.Exit(0)

    name = typer.prompt("Project name")

    click_dir.mkdir()
    db_path = str(click_dir / "click.db")
    init_db(db_path)

    conn = get_connection(db_path)
    project_id = create_project(conn, name)
    conn.close()

    out = Path.cwd() / output_dir
    out.mkdir(exist_ok=True)

    typer.echo(f"Initialized Click for '{name}'.")
    typer.echo(f"  Database: {db_path}")
    typer.echo(f"  Output: {out}")


@foundation_app.callback(invoke_without_command=True)
def foundation(ctx: typer.Context):
    """Start or resume a Foundation Sprint."""
    if ctx.invoked_subcommand is not None:
        return

    db_path = _get_db_path()
    conn = get_connection(db_path)
    project_id = _get_project_id(conn)

    # Check for in-progress sprint or create new one
    sprint = conn.execute(
        "SELECT * FROM foundation_sprints WHERE project_id = ? AND status = 'in_progress' ORDER BY created_at DESC LIMIT 1",
        (project_id,),
    ).fetchone()

    if not sprint:
        sprint_id = create_foundation_sprint(conn, project_id)
        typer.echo("Starting a new Foundation Sprint...")
    else:
        typer.echo(f"Resuming Foundation Sprint (currently on: {sprint['current_step']})...")

    context = get_project_context(conn, project_id)
    conn.close()

    prompt = FOUNDATION_SPRINT_PROMPT.format(context=context)
    asyncio.run(run_agent(db_path, project_id, _get_output_dir(), prompt))


@foundation_app.command("show")
def foundation_show():
    """Show the current/most recent Foundation Sprint results."""
    conn = get_connection(_get_db_path())
    project_id = _get_project_id(conn)
    typer.echo(get_project_context(conn, project_id))
    conn.close()


@foundation_app.command("list")
def foundation_list():
    """List all Foundation Sprints."""
    conn = get_connection(_get_db_path())
    project_id = _get_project_id(conn)
    sprints = conn.execute(
        "SELECT id, status, current_step, created_at FROM foundation_sprints WHERE project_id = ?",
        (project_id,),
    ).fetchall()
    for s in sprints:
        typer.echo(f"  #{s['id']} [{s['status']}] step: {s['current_step']} ({s['created_at']})")
    conn.close()


@sprint_app.callback(invoke_without_command=True)
def sprint(ctx: typer.Context):
    """Start a Design Sprint."""
    if ctx.invoked_subcommand is not None:
        return

    db_path = _get_db_path()
    conn = get_connection(db_path)
    project_id = _get_project_id(conn)

    project = get_project(conn, project_id)
    if not project["current_hypothesis_id"]:
        typer.echo("No Founding Hypothesis yet. Run 'click-coach foundation' first.")
        raise typer.Exit(1)

    context = get_project_context(conn, project_id)
    conn.close()

    prompt = DESIGN_SPRINT_PROMPT.format(context=context)
    asyncio.run(run_agent(db_path, project_id, _get_output_dir(), prompt))


@sprint_app.command("show")
def sprint_show(sprint_id: int):
    """Show a Design Sprint's details."""
    conn = get_connection(_get_db_path())
    sprint = conn.execute("SELECT * FROM design_sprints WHERE id = ?", (sprint_id,)).fetchone()
    if not sprint:
        typer.echo(f"Sprint #{sprint_id} not found.")
        raise typer.Exit(1)
    typer.echo(f"Sprint #{sprint['id']} [{sprint['status']}]")
    typer.echo(f"  Question: {sprint['risk_question']}")
    if sprint["outcome"]:
        typer.echo(f"  Outcome: {sprint['outcome']}")
    conn.close()


@sprint_app.command("list")
def sprint_list():
    """List all Design Sprints for the current hypothesis."""
    conn = get_connection(_get_db_path())
    project_id = _get_project_id(conn)
    project = get_project(conn, project_id)
    hyp_id = project["current_hypothesis_id"]
    if not hyp_id:
        typer.echo("No hypothesis yet.")
        raise typer.Exit(0)
    sprints = conn.execute(
        "SELECT id, risk_question, status, created_at FROM design_sprints WHERE hypothesis_id = ?",
        (hyp_id,),
    ).fetchall()
    for s in sprints:
        typer.echo(f"  #{s['id']} [{s['status']}] {s['risk_question']}")
    conn.close()


@hypothesis_app.callback(invoke_without_command=True)
def hypothesis(ctx: typer.Context):
    """Show current Founding Hypothesis + Scorecard."""
    if ctx.invoked_subcommand is not None:
        return
    conn = get_connection(_get_db_path())
    project_id = _get_project_id(conn)
    typer.echo(get_project_context(conn, project_id))
    conn.close()


@hypothesis_app.command("update")
def hypothesis_update():
    """Revise hypothesis based on learnings."""
    db_path = _get_db_path()
    conn = get_connection(db_path)
    project_id = _get_project_id(conn)
    context = get_project_context(conn, project_id)
    conn.close()

    prompt = f"The user wants to revise their Founding Hypothesis based on learnings.\n\n{context}\n\nGuide them through what to change and why."
    asyncio.run(run_agent(db_path, project_id, _get_output_dir(), prompt))


@scorecard_app.callback(invoke_without_command=True)
def scorecard(ctx: typer.Context):
    """Show current scorecard."""
    if ctx.invoked_subcommand is not None:
        return
    conn = get_connection(_get_db_path())
    project_id = _get_project_id(conn)
    project = get_project(conn, project_id)
    hyp_id = project["current_hypothesis_id"]
    if not hyp_id:
        typer.echo("No hypothesis yet. Run 'click-coach foundation' first.")
        raise typer.Exit(0)
    typer.echo(show_scorecard(conn, hyp_id))
    conn.close()


@scorecard_app.command("update")
def scorecard_update():
    """Update scorecard with new evidence."""
    db_path = _get_db_path()
    conn = get_connection(db_path)
    project_id = _get_project_id(conn)
    context = get_project_context(conn, project_id)
    conn.close()

    prompt = f"The user wants to update their Scorecard based on new evidence.\n\n{context}\n\nAsk what they learned and update the scorecard."
    asyncio.run(run_agent(db_path, project_id, _get_output_dir(), prompt))


@app.command()
def learnings():
    """Show accumulated learnings across all sprints."""
    conn = get_connection(_get_db_path())
    typer.echo(query_learnings(conn))
    conn.close()
```

- [ ] **Step 2: Verify CLI loads**

Run: `click-coach --help`
Expected: Shows help with all commands

- [ ] **Step 3: Commit**

```bash
git add src/click_agent/cli.py
git commit -m "feat: add Typer CLI with all commands"
```

---

### Task 13: Run All Tests

- [ ] **Step 1: Run the full test suite**

Run: `pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 2: Final commit**

```bash
git add -A
git commit -m "feat: Click agent v0.1.0 - complete implementation"
```
