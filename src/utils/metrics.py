import time
from contextlib import contextmanager
from typing import Dict, Optional

from src.utils.logger import get_logger

log = get_logger("metrics")


def incr(name: str, value: int = 1, tags: Optional[Dict[str, str]] = None) -> None:
    """
    Lightweight metric emitter (logs only).
    Later you can replace with Prometheus/StatsD.
    """
    tags_str = f" tags={tags}" if tags else ""
    log.info(f"METRIC incr {name} +{value}{tags_str}")


@contextmanager
def timer(name: str, tags: Optional[Dict[str, str]] = None):
    start = time.time()
    try:
        yield
    finally:
        ms = int((time.time() - start) * 1000)
        tags_str = f" tags={tags}" if tags else ""
        log.info(f"METRIC timer {name} {ms}ms{tags_str}")
