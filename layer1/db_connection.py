"""Database connection utilities for H2."""

from pathlib import Path

H2_JAR = Path(__file__).resolve().parents[1] / 'h2_db' / 'h2-2.x.x.jar'
SCHEMA_SQL = Path(__file__).resolve().parents[1] / 'h2_db' / 'schema.sql'

def get_connection_string(database_path: str) -> str:
    """Return a JDBC connection string for the H2 database."""
    return f"jdbc:h2:{database_path}"
