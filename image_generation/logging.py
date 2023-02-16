import logging
import os
from rich.logging import RichHandler
from rich.console import Console
import sys


stderr = Console(file=sys.stderr)
logging.basicConfig(
    level=os.getenv("LOGGER_LEVEL", logging.WARNING),
    format="%(message)s",
    datefmt=".",
    handlers=[RichHandler(console=stderr)],
)


def set_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(os.getenv("LOGGER_LEVEL", logging.WARNING))
    return logger
