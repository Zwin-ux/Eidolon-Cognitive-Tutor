"""Simple conversation history storage using SQLite."""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

DB_PATH = os.getenv("HISTORY_DB_PATH", "conversation_history.db")


def init_db():
    """Initialize the conversation history database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            prompt TEXT NOT NULL,
            response TEXT NOT NULL,
            source TEXT DEFAULT 'demo',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_conversation(session_id: str, prompt: str, response: str, source: str = "demo"):
    """Save a conversation turn to the database."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conversations (session_id, prompt, response, source) VALUES (?, ?, ?, ?)",
        (session_id, prompt, response, source),
    )
    conn.commit()
    conn.close()


def get_conversation_history(session_id: str, limit: int = 10) -> List[Dict]:
    """Retrieve conversation history for a session."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT prompt, response, source, timestamp FROM conversations WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
        (session_id, limit),
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "prompt": row[0],
            "response": row[1],
            "source": row[2],
            "timestamp": row[3],
        }
        for row in reversed(rows)
    ]
