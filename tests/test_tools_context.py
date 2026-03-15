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
        hyps = db_conn.execute("SELECT * FROM hypotheses ORDER BY id").fetchall()
        assert len(hyps) == 2
        assert hyps[1]["version"] == 2
        assert hyps[1]["customer"] == "early-stage founders"
        pivot = db_conn.execute("SELECT * FROM pivots").fetchone()
        assert pivot["what_changed"] == "customer, differentiation"
        project = db_conn.execute("SELECT * FROM projects WHERE id = ?", (context_setup["project_id"],)).fetchone()
        assert project["current_hypothesis_id"] == hyps[1]["id"]
