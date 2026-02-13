import sqlite3
from datetime import datetime
from src.utils.config import settings


def get_connection():
    return sqlite3.connect(settings.SQLITE_DB_PATH, check_same_thread=False)


def initialize_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Per-user daily metrics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_daily_metrics (
            user_id TEXT,
            day TEXT,
            message_count INTEGER DEFAULT 0,
            last_seen_ts TEXT,
            PRIMARY KEY (user_id, day)
        )
    """)

    # Per-user intent metrics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS intent_metrics (
            user_id TEXT,
            intent TEXT,
            count INTEGER DEFAULT 0,
            last_seen_ts TEXT,
            PRIMARY KEY (user_id, intent)
        )
    """)

    # Lineage (already used)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lineage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT,
            metadata TEXT,
            timestamp TEXT
        )
    """)

    # engagement_metrics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS engagement_metrics (
            user_id TEXT,
            campaign_id TEXT,
            engagement_count INTEGER,
            PRIMARY KEY (user_id, campaign_id)
        )
    """)


    conn.commit()
    conn.close()


def update_user_metrics(user_id: str, intent: str):
    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.utcnow().isoformat()
    day = now[:10]

    # Daily metrics
    cursor.execute("""
        INSERT INTO user_daily_metrics(user_id, day, message_count, last_seen_ts)
        VALUES (?, ?, 1, ?)
        ON CONFLICT(user_id, day)
        DO UPDATE SET
            message_count = message_count + 1,
            last_seen_ts = excluded.last_seen_ts
    """, (user_id, day, now))

    # Intent metrics
    cursor.execute("""
        INSERT INTO intent_metrics(user_id, intent, count, last_seen_ts)
        VALUES (?, ?, 1, ?)
        ON CONFLICT(user_id, intent)
        DO UPDATE SET
            count = count + 1,
            last_seen_ts = excluded.last_seen_ts
    """, (user_id, intent, now))

    conn.commit()
    conn.close()

def increment_campaign_engagement(user_id: str, campaign_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO engagement_metrics(user_id, campaign_id, engagement_count)
        VALUES (?, ?, 1)
        ON CONFLICT(user_id, campaign_id)
        DO UPDATE SET engagement_count = engagement_count + 1
    """, (user_id, campaign_id))

    conn.commit()
    conn.close()


def get_campaign_scores(campaign_ids: list[str]) -> dict:
    """
    Returns {campaign_id: total_engagement_count_across_users}
    """
    if not campaign_ids:
        return {}

    placeholders = ",".join(["?"] * len(campaign_ids))
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT campaign_id, SUM(engagement_count) AS score
        FROM engagement_metrics
        WHERE campaign_id IN ({placeholders})
        GROUP BY campaign_id
    """, campaign_ids)

    rows = cursor.fetchall()
    conn.close()

    return {cid: score for cid, score in rows}
