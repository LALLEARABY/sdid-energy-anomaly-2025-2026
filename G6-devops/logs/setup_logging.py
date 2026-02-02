import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging(name: str = "sdid", level: int = logging.INFO, logfile: str = "app.log"):
    log_dir = Path(__file__).resolve().parent
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    # Console
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(fmt)

    # File (rotation)
    fh = RotatingFileHandler(log_dir / logfile, maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(fmt)

    # Avoid duplicate handlers
    if not logger.handlers:
        logger.addHandler(ch)
        logger.addHandler(fh)

    return logger
