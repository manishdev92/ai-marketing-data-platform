## 👤 Author

## Manish Tiwari
## Senior Data Engineer / AI Systems Architect

---

# System Architecture

## 1. Ingestion Layer

FastAPI exposes:

POST /conversations

Stores raw conversation in MongoDB.
Publishes event to Redis Stream.

---

## 2. Event Backbone

Redis Streams:

conversation_stream

Acts as durable event queue.
Worker uses consumer group.

---

## 3. Processing Layer (Worker)

For each event:

1. Generate embedding (SentenceTransformer)
2. Store embedding in Milvus
3. Detect intent
4. Upsert graph in Neo4j
5. Update analytics tables (SQLite)
6. Assign campaign
7. Increment campaign engagement
8. ACK event

---

## 4. Storage Layer

| System | Purpose |
|--------|---------|
| MongoDB | Raw conversations |
| Milvus | Vector similarity |
| Neo4j | User-intent graph |
| SQLite | Analytics & campaign scores |

---

## 5. Recommendation Flow

GET /recommendations/{user_id}

1. Fetch user embedding from Milvus
2. Search similar users
3. Fetch campaign scores
4. Return ranked campaigns

---

## 6. Orchestration Layer

Custom orchestrator runs:

- dead_letter_handler
- analytics_batch

Periodic scheduling loop.

---

## 7. UI Layer

Streamlit:
- Input user_id
- Display similar users
- Display recommended campaigns
