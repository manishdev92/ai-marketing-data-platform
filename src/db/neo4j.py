from __future__ import annotations

from neo4j import GraphDatabase
from src.utils.config import settings


def get_driver():
    return GraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
    )


def init_constraints():
    """
    Create uniqueness constraints so MERGE is fast and safe.
    """
    driver = get_driver()
    with driver.session() as session:
        session.run("CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE")
        session.run("CREATE CONSTRAINT session_id IF NOT EXISTS FOR (s:Session) REQUIRE s.session_id IS UNIQUE")
        session.run("CREATE CONSTRAINT intent_name IF NOT EXISTS FOR (i:Intent) REQUIRE i.name IS UNIQUE")
        session.run("CREATE CONSTRAINT message_id IF NOT EXISTS FOR (m:Message) REQUIRE m.message_id IS UNIQUE")
        session.run("CREATE CONSTRAINT campaign_id IF NOT EXISTS FOR (c:Campaign) REQUIRE c.campaign_id IS UNIQUE")

    driver.close()


def upsert_conversation_graph(
    *,
    user_id: str,
    session_id: str,
    message_id: str,
    text: str,
    timestamp: str,
    intent: str,
):
    """
    Creates:
      (User)-[:HAS_SESSION]->(Session)
      (Session)-[:HAS_MESSAGE]->(Message)
      (User)-[:HAS_INTENT]->(Intent)
    """
    driver = get_driver()
    query = """
    MERGE (u:User {user_id: $user_id})
    MERGE (s:Session {session_id: $session_id})
    MERGE (u)-[:HAS_SESSION]->(s)

    MERGE (m:Message {message_id: $message_id})
    SET m.text = $text,
        m.timestamp = $timestamp
    MERGE (s)-[:HAS_MESSAGE]->(m)

    MERGE (i:Intent {name: $intent})
    MERGE (u)-[r:HAS_INTENT]->(i)
    ON CREATE SET r.count = 1
    ON MATCH SET r.count = coalesce(r.count, 0) + 1
    """
    with driver.session() as session:
        session.run(
            query,
            user_id=user_id,
            session_id=session_id,
            message_id=message_id,
            text=text,
            timestamp=timestamp,
            intent=intent,
        )
    driver.close()

def link_user_to_campaign(*, user_id: str, campaign_id: str):
    """
    (User)-[ENGAGED_WITH {count}]->(Campaign)
    """
    driver = get_driver()
    query = """
    MERGE (u:User {user_id: $user_id})
    MERGE (c:Campaign {campaign_id: $campaign_id})
    MERGE (u)-[r:ENGAGED_WITH]->(c)
    ON CREATE SET r.count = 1
    ON MATCH SET r.count = coalesce(r.count, 0) + 1
    """
    with driver.session() as session:
        session.run(query, user_id=user_id, campaign_id=campaign_id)
    driver.close()

def get_campaigns_for_users(user_ids: list[str]) -> list[dict]:
    """
    Returns list of {campaign_id, user_id, count}
    """
    driver = get_driver()
    query = """
    MATCH (u:User)-[r:ENGAGED_WITH]->(c:Campaign)
    WHERE u.user_id IN $user_ids
    RETURN u.user_id AS user_id, c.campaign_id AS campaign_id, r.count AS count
    """
    with driver.session() as session:
        result = session.run(query, user_ids=user_ids)
        rows = [dict(record) for record in result]
    driver.close()
    return rows
