# Architecture Diagram

```mermaid
flowchart LR
  %% ============ Clients ============
  U[Client / curl / external app] -->|POST /conversations| API[FastAPI API]

  %% ============ Ingestion ============
  API -->|Insert document| M[(MongoDB\nconversations)]
  API -->|XADD conversation_stream\n{data: JSON}| RS[(Redis Streams\nconversation_stream)]

  %% ============ Stream Processing ============
  RS -->|XREADGROUP embedding_group| W[Pipeline Worker\n(worker_1)]

  %% Worker internal steps
  W -->|Generate embedding\n(all-MiniLM-L6-v2)| E[EmbeddingModel]
  W -->|Insert embedding| V[(Milvus\nuser_embeddings)]
  W -->|Detect intent| INT[Intent Detector]
  W -->|Upsert graph\nUser-Session-Message-Intent| G[(Neo4j)]
  W -->|Update metrics\nuser_daily_metrics,\nintent_metrics| S[(SQLite\nmarketing.db)]
  W -->|Assign campaign| C[Campaign Assigner]
  W -->|Link campaign| G
  W -->|Increment engagement| S
  W -->|XACK message| RS

  %% ============ Recommendation Serving ============
  UI[Streamlit UI] -->|GET /recommendations/{user_id}| API
  API -->|Fetch user embedding| V
  API -->|Similarity search topK users| V
  API -->|Fetch campaign scores| S
  API --> UI

  %% ============ Orchestration / Maintenance ============
  ORCH[Orchestrator\n(periodic runner)] -->|runs| DLQ[Dead Letter Handler]
  ORCH -->|runs| BATCH[Analytics Batch]
  ORCH -->|init DB tables| S

  %% Notes
  subgraph "Storage"
    M
    V
    G
    S
  end

  subgraph "Compute"
    API
    W
    ORCH
  end

