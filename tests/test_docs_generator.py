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
