
import os
import sqlite3
from pathlib import Path

DB_PATH = os.getenv("DATABASE_PATH", "data/jd4.sqlite3")


def get_connection():
    """Create a database connection and ensure its directory exists."""
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Create the required tables if they do not exist."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                url TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                active INTEGER DEFAULT 1
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS expert_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                expert_answer TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()


def save_article(url: str, title: str, content: str):
    """Insert or update an article using its URL."""
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO articles (
                url, title, content, updated_at, active
            )
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, 1)
            ON CONFLICT(url) DO UPDATE SET
                title = excluded.title,
                content = excluded.content,
                updated_at = CURRENT_TIMESTAMP,
                active = 1
        """, (url, title, content))
        conn.commit()


def get_articles():
    """Return all active help-center articles."""
    with get_connection() as conn:
        return conn.execute("""
            SELECT url, title, content
            FROM articles
            WHERE active = 1
            ORDER BY title
        """).fetchall()


def find_article_by_url(url: str):
    """Find an active article by its exact URL."""
    with get_connection() as conn:
        return conn.execute("""
            SELECT url, title, content
            FROM articles
            WHERE url = ? AND active = 1
        """, (url,)).fetchone()


def save_expert_feedback(
    question: str,
    expert_answer: str,
) -> int:
    """Save an expert answer pending review and return its ID."""
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO expert_feedback (question, expert_answer)
            VALUES (?, ?)
        """, (question, expert_answer))
        conn.commit()
        return cursor.lastrowid


def get_expert_feedback(status: str = "pending"):
    """Return feedback filtered by review status."""
    allowed_statuses = {"pending", "approved", "rejected"}

    if status not in allowed_statuses:
        raise ValueError(
            "Status must be 'pending', 'approved', or 'rejected'."
        )

    with get_connection() as conn:
        return conn.execute("""
            SELECT id, question, expert_answer, status, created_at
            FROM expert_feedback
            WHERE status = ?
            ORDER BY created_at DESC, id DESC
        """, (status,)).fetchall()


def update_feedback_status(feedback_id: int, status: str) -> bool:
    """Approve or reject feedback and report whether it exists."""
    allowed_statuses = {"pending", "approved", "rejected"}

    if status not in allowed_statuses:
        raise ValueError(
            "Status must be 'pending', 'approved', or 'rejected'."
        )

    with get_connection() as conn:
        cursor = conn.execute("""
            UPDATE expert_feedback
            SET status = ?
            WHERE id = ?
        """, (status, feedback_id))
        conn.commit()
        return cursor.rowcount > 0
