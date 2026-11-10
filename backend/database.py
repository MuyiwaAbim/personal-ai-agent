
import sqlite3
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "assistant.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():

    with get_connection() as db:

        # Conversation table
        db.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                created_at TEXT
            )
        """)

        # Message table
        db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER,
                role TEXT,
                content TEXT,
                created_at TEXT
            )
        """)

        # Personal memory table
        db.execute("""
            CREATE TABLE IF NOT EXISTS personal_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note TEXT UNIQUE,
                created_at TEXT
            )
        """)


def create_conversation():

    with get_connection() as db:

        cursor = db.execute(
            """
            INSERT INTO conversations (title, created_at)
            VALUES (?, ?)
            """,
            ("New Conversation", datetime.now().isoformat())
        )

        return cursor.lastrowid


def save_message(conversation_id, role, content):

    with get_connection() as db:

        db.execute(
            """
            INSERT INTO messages
            (conversation_id, role, content, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                conversation_id,
                role,
                content,
                datetime.now().isoformat()
            )
        )


def get_messages(conversation_id):

    with get_connection() as db:

        cursor = db.execute(
            """
            SELECT role, content
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id ASC
            """,
            (conversation_id,)
        )

        return [dict(row) for row in cursor.fetchall()]


def save_personal_note(note):

    with get_connection() as db:

        db.execute(
            """
            INSERT OR IGNORE INTO personal_notes
            (note, created_at)
            VALUES (?, ?)
            """,
            (note, datetime.now().isoformat())
        )


def get_personal_notes():

    with get_connection() as db:

        cursor = db.execute(
            """
            SELECT note
            FROM personal_notes
            ORDER BY id DESC
            """
        )

        return [row["note"] for row in cursor.fetchall()]
