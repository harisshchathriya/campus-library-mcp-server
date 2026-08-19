from pathlib import Path
import sqlite3


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "library.db"


def get_connection() -> sqlite3.Connection:
    """Create a connection to the library SQLite database."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    """Create the required database tables if they do not exist."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                category TEXT NOT NULL,
                isbn TEXT NOT NULL UNIQUE,
                total_copies INTEGER NOT NULL CHECK (total_copies >= 0),
                available_copies INTEGER NOT NULL CHECK (
                    available_copies >= 0
                    AND available_copies <= total_copies
                )
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                student_id TEXT NOT NULL,
                reserved_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL DEFAULT 'reserved',
                FOREIGN KEY (book_id) REFERENCES books(id)
            )
            """
        )

        connection.commit()


def search_books(query: str) -> list[dict[str, int | str]]:
    """Return books whose title, author, or category contains ``query``."""
    search_pattern = f"%{query}%"

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, title, author, category, total_copies, available_copies
            FROM books
            WHERE LOWER(title) LIKE LOWER(?)
               OR LOWER(author) LIKE LOWER(?)
               OR LOWER(category) LIKE LOWER(?)
            ORDER BY id
            """,
            (search_pattern, search_pattern, search_pattern),
        ).fetchall()

    return [dict(row) for row in rows]
