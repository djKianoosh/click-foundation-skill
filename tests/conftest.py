import sys
from pathlib import Path

# Ensure skill scripts directory is on sys.path for test execution
_scripts_dir = Path(__file__).parent.parent / "skills" / "click-foundation" / "scripts"
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

import pytest
from db import get_connection, init_db


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
