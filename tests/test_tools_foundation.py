import json
import pytest
from click_agent.db import create_project, create_foundation_sprint, get_foundation_sprint
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
            db_conn, sprint_id,
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
        assert json.loads(sprint["alternatives"]) == {"items": ["books", "mentors", "consulting firms"]}
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
            db_conn, sprint_id,
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
        assert len(principles["items"]) == 3
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
        project = db_conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        assert project["current_hypothesis_id"] == hyp["id"]
