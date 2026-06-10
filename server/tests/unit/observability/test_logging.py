"""Unit tests for structured logging setup."""

from collections.abc import Iterator

import pytest
from loguru import logger

from app.platform.observability.logging import setup_logging
from app.runtime.settings import Settings


@pytest.fixture(autouse=True)
def _reset_logging() -> Iterator[None]:
    yield
    logger.remove()


def test_pretty_mode_runs_without_error() -> None:
    setup_logging(Settings(environment="development"))
    logger.info("a development log line")  # must not raise


def test_json_mode_emits_structured_line(capsys: pytest.CaptureFixture[str]) -> None:
    setup_logging(Settings(environment="production"))

    logger.bind(request_id="req-123", user_id="u-1").info("structured line")

    err = capsys.readouterr().err
    assert '"message": "structured line"' in err
    assert '"severity": "INFO"' in err
    assert '"logging.googleapis.com/sourceLocation"' in err
    # Indexed fields are promoted into GCP labels.
    assert '"request_id": "req-123"' in err
    assert '"user_id": "u-1"' in err


def test_log_json_forces_json_in_development(capsys: pytest.CaptureFixture[str]) -> None:
    setup_logging(Settings(environment="development", log_json=True))

    logger.info("forced json")

    assert '"message": "forced json"' in capsys.readouterr().err
