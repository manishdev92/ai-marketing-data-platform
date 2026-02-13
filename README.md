# 🚀 AI Marketing Data Platform

An end-to-end event-driven AI marketing recommendation system built with:

- FastAPI (API layer)
- Redis Streams (event backbone)
- MongoDB (raw storage)
- Milvus (vector database)
- Neo4j (graph intelligence)
- SQLite (analytics store)
- Custom Worker (embedding + campaign assignment)
- Orchestrator (batch jobs)
- Streamlit (UI demo)

---

## 🎯 What This Project Demonstrates

This project simulates a real-world AI-driven marketing system:

1. User conversations are ingested via API
2. Conversations are stored in MongoDB
3. Events are published to Redis Stream
4. Worker consumes events:
   - Generates embeddings
   - Stores vectors in Milvus
   - Updates user-intent graph in Neo4j
   - Updates analytics in SQLite
   - Assigns campaign
5. Recommendation API returns:
   - Similar users (vector similarity)
   - Campaigns ranked by engagement score
6. Streamlit UI displays recommendations

---

## 🏗️ Architecture Overview

See:
- `architecture.md`
- `architecture_diagram.md`

---

## 🧠 Core Capabilities

- Real-time embedding generation
- Vector similarity search (Milvus)
- Intent-based graph modeling (Neo4j)
- Campaign scoring via collaborative signals
- Event-driven processing (Redis Streams)
- Batch orchestration loop

---

## 🐳 Run the System

```bash
docker-compose up -d --build
```
```
| Service   | Port  |
| --------- | ----- |
| FastAPI   | 8000  |
| Streamlit | 8501  |
| Neo4j     | 7474  |
| Milvus    | 19530 |
| Redis     | 6379  |
| MongoDB   | 27017 |
```

## 📥 Ingest a Conversation
```
curl -X POST http://localhost:8000/conversations \
-H "Content-Type: application/json" \
-d '{
  "user_id": "user_1",
  "session_id": "sess_1",
  "messages": [{"role":"user","content":"recommend me running shoes"}],
  "timestamp": "2026-02-12T10:00:00"
}'
```

## 🎯 Get Recommendations
```
curl http://localhost:8000/recommendations/user_1
```

## 📊 Streamlit UI
```
http://localhost:8501
```

## 📂 Project Structure
src/
 ├── api/
 ├── db/
 ├── models/
 ├── pipeline/
 ├── ui/
 └── utils/




