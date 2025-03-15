import logging
from typing import cast


__debug: bool = False
__logger: None | logging.Logger = None


def __init() -> None:
    """Initialize the logger."""
    global __logger, __debug
    logging.basicConfig(
        format="[%(levelname)s] %(message)s",
    )
    __logger = logging.getLogger(__name__)
    __logger.setLevel(logging.DEBUG if __debug else logging.INFO)


def __get() -> logging.Logger:
    global __logger
    if __logger is None:
        __init()
    return cast(logging.Logger, __logger)


def debug() -> None:
    """Enable debug log."""
    global __debug
    __debug = True


def log() -> logging.Logger:
    """Return the logger instance."""
    return __get()
