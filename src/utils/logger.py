import logging
import os
import sys
from typing import Optional


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Consistent logger for API/worker/orchestrator.
    LOG_LEVEL env can be: DEBUG, INFO, WARNING, ERROR
    """
    logger = logging.getLogger(name)

    # avoid duplicate handlers when module reloads
    if logger.handlers:
        return logger

    log_level = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt='[%(name)s] %(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S',
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.propagate = False
    return logger
