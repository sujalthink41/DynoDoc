"""Structured logging via loguru.

- **development**: pretty, colourised lines (easy to read), with the request id.
- **otherwise**: one JSON object per line (structured + parseable), with the
  request id and any bound fields.

Standard-library logging (uvicorn, sqlalchemy, ...) is routed through loguru via
an intercept handler, so everything shares one consistent format. The request id
is injected automatically from the per-request context.
"""

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from loguru import logger

from app.runtime.request_context import get_request_id
from app.runtime.settings import Settings


def _patch_request_id(record: Any) -> None:
    record["extra"].setdefault("request_id", get_request_id() or "-")


def _format_time(value: datetime) -> str:
    timestamp = value.astimezone(UTC) if value.tzinfo else value.replace(tzinfo=UTC)
    return timestamp.isoformat().replace("+00:00", "Z")


# Fields promoted to GCP "labels" (indexed/searchable in Cloud Logging).
_INDEXED_LABEL_FIELDS: frozenset[str] = frozenset(
    {"request_id", "user_id", "correlation_id", "tenant_id"}
)


def _json_sink(message: Any) -> None:
    record = message.record
    payload: dict[str, Any] = {
        "severity": record["level"].name,
        "message": record["message"],
        "time": _format_time(record["time"]),
        "logger": record["name"],
        "module": record["module"],
        "function": record["function"],
        "line": record["line"],
        "process": {"id": record["process"].id, "name": record["process"].name},
        "thread": {"id": record["thread"].id, "name": record["thread"].name},
        "logging.googleapis.com/sourceLocation": {
            "file": record["file"].path,
            "line": record["line"],
            "function": record["function"],
        },
    }

    extra = {k: v for k, v in record["extra"].items() if v not in (None, "-")}

    labels = {key: str(extra.pop(key)) for key in list(extra) if key in _INDEXED_LABEL_FIELDS}
    if labels:
        payload["logging.googleapis.com/labels"] = labels
    if extra:
        payload["extra"] = extra

    exception = record["exception"]
    if exception is not None:
        payload["exception"] = {
            "type": exception.type.__name__ if exception.type else None,
            "value": str(exception.value) if exception.value else None,
        }

    sys.stderr.write(json.dumps(payload, ensure_ascii=False, default=str) + "\n")


class _InterceptHandler(logging.Handler):
    """Route stdlib logging records into loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame: Any = logging.currentframe()
        depth = 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


_PRETTY_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{extra[request_id]}</cyan> | "
    "<level>{message}</level>"
)


def setup_logging(settings: Settings) -> None:
    """Configure loguru. Idempotent — safe to call again (e.g. on reload)."""
    logger.remove()
    logger.configure(patcher=_patch_request_id)

    use_json = settings.log_json or settings.environment != "development"
    if use_json:
        logger.add(_json_sink, level=settings.log_level, format="{message}")
    else:
        logger.add(sys.stderr, level=settings.log_level, format=_PRETTY_FORMAT, colorize=True)

    # Route stdlib logging (uvicorn, sqlalchemy, ...) through loguru.
    logging.basicConfig(handlers=[_InterceptHandler()], level=logging.INFO, force=True)
    for name in ("uvicorn", "uvicorn.access", "uvicorn.error", "sqlalchemy.engine"):
        std_logger = logging.getLogger(name)
        std_logger.handlers = []
        std_logger.propagate = True
