import logging
import os
from datetime import datetime


def setup_logger():
    """Configure logging for the application."""
    logger = logging.getLogger("leaderboard")
    logger.setLevel(logging.INFO)

    log_dir = "log"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    file_handler = logging.FileHandler(
        f"{log_dir}/api_{datetime.now().strftime('%Y%m%d')}.log"
    )
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger
