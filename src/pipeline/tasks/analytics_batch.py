# src/pipeline/tasks/analytics_batch.py
from datetime import datetime
from src.db.sqlite import get_connection

def run_analytics_batch():
    """
    Example: roll up engagement totals by campaign into a summary table.
    You can extend this with real logic later.
    """
    conn = get_connection()
    cur = conn.cursor()

    # Create summary table if missing
    cur.execute("""
    CREATE TABLE IF NOT EXISTS campaign_summary (
        campaign_id TEXT PRIMARY KEY,
        total_engagement INTEGER,
        updated_ts TEXT
    )
    """)

    # Rollup
    cur.execute("""
    INSERT INTO campaign_summary(campaign_id, total_engagement, updated_ts)
    SELECT campaign_id, SUM(engagement_count), ?
    FROM engagement_metrics
    GROUP BY campaign_id
    ON CONFLICT(campaign_id)
    DO UPDATE SET
        total_engagement = excluded.total_engagement,
        updated_ts = excluded.updated_ts
    """, (datetime.utcnow().isoformat(),))

    conn.commit()
    conn.close()
