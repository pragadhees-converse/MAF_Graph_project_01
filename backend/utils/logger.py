# backend/utils/logger.py
import sys

from loguru import logger as _logger

_logger.remove()
_logger.add(
    sys.stdout,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{extra[name]}</cyan> | {message}"
    ),
    level="INFO",
)


def get_logger(name: str):
    """
    Returns a loguru logger bound with a module name, so existing
    calls like get_logger(__name__) work unchanged everywhere else
    in the codebase.
    """
    return _logger.bind(name=name)