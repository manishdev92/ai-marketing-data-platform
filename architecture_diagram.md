# Architecture Diagram

```mermaid
flowchart LR

User --> FastAPI
FastAPI --> MongoDB
FastAPI --> RedisStream

RedisStream --> Worker

Worker --> Milvus
Worker --> Neo4j
Worker --> SQLite

FastAPI --> Milvus
FastAPI --> SQLite

FastAPI --> StreamlitUI
