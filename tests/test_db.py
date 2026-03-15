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
