"""DuckDB connection factory for SeasonXI."""

from pathlib import Path

import duckdb

DEFAULT_DB_PATH = Path("data/db/seasonxi.duckdb")
_SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_connection(db_path: Path | str | None = None) -> duckdb.DuckDBPyConnection:
    """Create or open a DuckDB connection."""
    path = Path(db_path) if db_path else DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(path))


def init_schema(conn: duckdb.DuckDBPyConnection | None = None) -> None:
    """Execute schema.sql to create all tables."""
    own_conn = conn is None
    if own_conn:
        conn = get_connection()

    schema_sql = _SCHEMA_PATH.read_text(encoding="utf-8")
    conn.execute(schema_sql)

    if own_conn:
        conn.close()
