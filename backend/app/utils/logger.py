import logging
import sys
from typing import Any
import structlog


def setup_logger(debug: bool = True) -> None:
    """
    Configures structlog for JSON structured logging in production and colored console in debug mode.
    Ensures timestamp, trace_id, and level appear uniformly across services.
    """
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if debug:
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    else:
        processors = shared_processors + [
            structlog.processors.JSONRenderer()
        ]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(name)s - %(message)s",
        stream=sys.stdout,
        level=logging.INFO,
        force=True
    )

    if debug:
        # Enable DEBUG explicitly for our internal application loggers
        logging.getLogger("scraper").setLevel(logging.DEBUG)
        logging.getLogger("agents").setLevel(logging.DEBUG)
        logging.getLogger("app").setLevel(logging.DEBUG)
        logging.getLogger("idx_intel").setLevel(logging.DEBUG)


def get_logger(name: str = "idx_intel") -> structlog.stdlib.BoundLogger:
    """
    Returns a structlog logger bound with the specified name.
    """
    return structlog.get_logger(name)


setup_logging = setup_logger
