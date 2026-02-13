# import os

# class Settings:
#     MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
#     REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
#     NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
#     NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
#     NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
#     MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
#     MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
#     SQLITE_DB_PATH = "analytics.db"

# settings = Settings()


from pydantic import BaseSettings
# from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Mongo
    MONGO_URI: str = "mongodb://mongodb:27017"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Milvus
    MILVUS_HOST: str = "milvus"
    MILVUS_PORT: int = 19530

    # SQLite file
    SQLITE_DB_PATH: str = "marketing.db"

    # Neo4j
    NEO4J_URI: str = "bolt://neo4j:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"


    class Config:
        env_file = ".env"


settings = Settings()

