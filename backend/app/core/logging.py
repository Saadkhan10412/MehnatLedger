"""Logging configuration.

Logging rules for this project:

* Never log credentials, tokens, raw audio or full transcripts.
* Keep log records useful for diagnosing provider failures by category only.
"""

from __future__ import annotations

import logging
import sys

from app.core.config import Settings

_LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s %(message)s"


def configure_logging(settings: Settings) -> None:
    """Configure root logging for the API process.

    Safe to call more than once (for example from tests): handlers are replaced
    rather than appended, so log lines are not duplicated.
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT))

    root = logging.getLogger()
    for existing in list(root.handlers):
        root.removeHandler(existing)
    root.addHandler(handler)
    root.setLevel(settings.log_level)

    # uvicorn installs its own handlers; align them with our level.
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logging.getLogger(name).setLevel(settings.log_level)


def log_startup_diagnostics(settings: Settings) -> None:
    """Log non-sensitive startup diagnostics.

    Note: ``settings.model_dump()`` and ``repr(settings)`` both mask
    ``SecretStr`` values, but we deliberately log only selected non-secret
    fields plus the warning strings to keep that guarantee obvious.
    """
    logger = logging.getLogger("mehnatledger.startup")
    logger.info(
        "Starting %s (environment=%s, log_level=%s)",
        settings.app_name,
        settings.environment.value,
        settings.log_level,
    )
    for warning in settings.configuration_warnings():
        logger.warning("Configuration warning: %s", warning)
