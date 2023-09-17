import logging
from logging.handlers import SysLogHandler
import os


def initialize_papertrail():
    """Initialize papertrail logging."""
    logger = logging.getLogger("first_logger")
    logger.setLevel(logging.DEBUG)
    syslog = SysLogHandler(
        address=(os.getenv("PAPERTRAIL_HOST"), int(os.getenv("PAPERTRAIL_PORT")))
    )
    logger.addHandler(syslog)

    logger.debug("Logger setup complete.")
