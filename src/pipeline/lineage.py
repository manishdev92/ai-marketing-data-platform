from src.db.sqlite import get_connection
import json
from datetime import datetime
import sqlite3
from src.utils.config import settings

def init_lineage_db():
    conn = sqlite3.connect(settings.SQLITE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lineage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT,
        conversation_id TEXT,
        timestamp TEXT,
        metadata TEXT
    )
""")

    conn.commit()
    conn.close()

def track_event(event_type: str, metadata: dict):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO lineage (event_type, metadata, timestamp)
        VALUES (?, ?, ?)
    """, (
        event_type,
        json.dumps(metadata),
        datetime.utcnow().isoformat()
    ))

    conn.commit()
