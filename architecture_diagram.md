flowchart LR

  %% Clients
  U[Client / curl / external app] -->|POST conversations| API[FastAPI API]

  %% Ingestion
  API -->|Insert document| M[(MongoDB)]
  API -->|XADD conversation_stream data JSON| RS[(Redis Streams)]

  %% Stream Processing
  RS -->|XREADGROUP embedding_group| W[Pipeline Worker]

  %% Worker steps
  W -->|Generate embedding| E[Embedding Model]
  W -->|Insert embedding| V[(Milvus)]
  W -->|Detect intent| INT[Intent Detector]
  W -->|Upsert graph| G[(Neo4j)]
  W -->|Update metrics| S[(SQLite)]
  W -->|Assign campaign| C[Campaign Assigner]
  W -->|Link campaign| G
  W -->|Increment engagement| S
  W -->|XACK message| RS

  %% Recommendation Serving
  UI[Streamlit UI] -->|GET recommendations| API
  API -->|Fetch embedding| V
  API -->|Similarity search| V
  API -->|Fetch campaign scores| S
  API --> UI

  %% Orchestration
  ORCH[Pipeline Orchestrator] --> DLQ[Dead Letter Handler]
  ORCH --> BATCH[Analytics Batch]
  ORCH --> S

  subgraph Storage
    M
    V
    G
    S
  end

  subgraph Compute
    API
    W
    ORCH
  end
