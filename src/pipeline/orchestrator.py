# src/pipeline/orchestrator.py
import time
import traceback
from datetime import datetime

from src.db.sqlite import initialize_tables
from src.pipeline.tasks.analytics_batch import run_analytics_batch
from src.pipeline.tasks.dead_letter_handler import run_dead_letter_handler

SCHEDULE_SECONDS = {
    "dead_letter_handler": 60,      # every 1 min
    "analytics_batch": 300,         # every 5 mins (demo); later daily/hourly
}

def log(msg: str):
    print(f"[orchestrator] {datetime.utcnow().isoformat()} | {msg}", flush=True)

def safe_run(name, fn):
    try:
        log(f"START {name}")
        fn()
        log(f"END   {name}")
    except Exception as e:
        log(f"ERROR {name}: {e}")
        traceback.print_exc()

def main():
    log("Initializing DB...")
    initialize_tables()

    last_run = {k: 0 for k in SCHEDULE_SECONDS}

    log("Orchestrator running...")
    while True:
        now = time.time()

        for job, interval in SCHEDULE_SECONDS.items():
            if now - last_run[job] >= interval:
                if job == "dead_letter_handler":
                    safe_run(job, run_dead_letter_handler)
                elif job == "analytics_batch":
                    safe_run(job, run_analytics_batch)

                last_run[job] = now

        time.sleep(2)

if __name__ == "__main__":
    main()
