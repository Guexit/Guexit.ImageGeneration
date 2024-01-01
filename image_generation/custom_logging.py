import logging
import os
import sys

from rich.console import Console
from rich.logging import RichHandler

LOGGER_LEVEL = os.getenv("LOGGER_LEVEL", logging.WARNING)

stderr = Console(file=sys.stderr)
logging.basicConfig(
    level=LOGGER_LEVEL,
    format="%(message)s",
    datefmt=".",
    handlers=[RichHandler(console=stderr)],
)


def set_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(LOGGER_LEVEL)
    return logger
