from fastapi import FastAPI
from src.api.routes import router
from src.pipeline.lineage import init_lineage_db
from src.db.sqlite import initialize_tables 
app = FastAPI()

@app.on_event("startup")
def startup_event():
    initialize_tables()      # ✅ creates engagement_metrics etc
    init_lineage_db()        # ✅ creates lineage etc

app.include_router(router)
