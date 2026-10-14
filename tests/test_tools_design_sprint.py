import json

import pytest
from db import create_foundation_sprint, create_project
from tools import (
    create_design_sprint,
    log_sprint_day,
    record_test_results,
    save_founding_hypothesis,
    update_sprint_outcome,
)


@pytest.fixture
def sprint_setup(db_conn):
    project_id = create_project(db_conn, "Test")
    f_sprint_id = create_foundation_sprint(db_conn, project_id)
    save_founding_hypothesis(
        db_conn,
        f_sprint_id,
        project_id,
        customer="founders",
        problem="slow validation",
        approach="CLI coach",
        competitors="books",
        differentiation="AI-guided",
    )
    hyp = db_conn.execute("SELECT * FROM hypotheses").fetchone()
    return {"project_id": project_id, "hypothesis_id": hyp["id"]}


class TestCreateDesignSprint:
    def test_creates_sprint(self, db_conn, sprint_setup):
        create_design_sprint(
            db_conn,
            sprint_setup["hypothesis_id"],
            risk_question="Will founders trust an AI to guide their strategy?",
        )
        sprint = db_conn.execute("SELECT * FROM design_sprints").fetchone()
        assert sprint["risk_question"] == "Will founders trust an AI to guide their strategy?"
        assert sprint["status"] == "in_progress"


class TestLogSprintDay:
    def test_logs_map_day(self, db_conn, sprint_setup):
        create_design_sprint(
            db_conn,
            sprint_setup["hypothesis_id"],
            risk_question="Trust question",
        )
        sprint = db_conn.execute("SELECT * FROM design_sprints").fetchone()
        log_sprint_day(db_conn, sprint["id"], day="map", notes="Mapped the customer journey")
        sprint = db_conn.execute(
            "SELECT * FROM design_sprints WHERE id = ?", (sprint["id"],)
        ).fetchone()
        assert sprint["day_map"] == "Mapped the customer journey"

    def test_rejects_invalid_day(self, db_conn, sprint_setup):
        create_design_sprint(
            db_conn,
            sprint_setup["hypothesis_id"],
            risk_question="Q",
        )
        sprint = db_conn.execute("SELECT * FROM design_sprints").fetchone()
        result = log_sprint_day(db_conn, sprint["id"], day="invalid", notes="test")
        assert "error" in result.lower()


class TestRecordTestResults:
    def test_records_reactions(self, db_conn, sprint_setup):
        create_design_sprint(
            db_conn,
            sprint_setup["hypothesis_id"],
            risk_question="Q",
        )
        sprint = db_conn.execute("SELECT * FROM design_sprints").fetchone()
        record_test_results(
            db_conn,
            sprint["id"],
            reactions=[
                {
                    "customer": "Alice",
                    "reaction": "Leaned forward, asked to try it",
                    "is_reaction": True,
                },
                {
                    "customer": "Bob",
                    "reaction": "Said it was nice",
                    "is_reaction": False,
                },
            ],
        )
        sprint = db_conn.execute(
            "SELECT * FROM design_sprints WHERE id = ?", (sprint["id"],)
        ).fetchone()
        data = json.loads(sprint["customer_reactions"])
        assert len(data["items"]) == 2


class TestUpdateSprintOutcome:
    def test_updates_outcome(self, db_conn, sprint_setup):
        create_design_sprint(
            db_conn,
            sprint_setup["hypothesis_id"],
            risk_question="Q",
        )
        sprint = db_conn.execute("SELECT * FROM design_sprints").fetchone()
        update_sprint_outcome(
            db_conn,
            sprint["id"],
            outcome="Founders were skeptical but interested. Need more detail in the dashboard.",
            hypothesis_changed=False,
        )
        sprint = db_conn.execute(
            "SELECT * FROM design_sprints WHERE id = ?", (sprint["id"],)
        ).fetchone()
        assert sprint["status"] == "complete"
        assert sprint["hypothesis_changed"] == 0
