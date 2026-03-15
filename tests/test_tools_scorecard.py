import pytest
from click_agent.db import create_project, create_foundation_sprint
from click_agent.tools.scorecard import update_scorecard, show_scorecard
from click_agent.tools.foundation import save_founding_hypothesis


@pytest.fixture
def hypothesis_setup(db_conn):
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
