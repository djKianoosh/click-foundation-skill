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
