"""Unit: request-id context helpers."""

from app.runtime.request_context import get_request_id, set_request_id


def test_generates_id_when_none_supplied() -> None:
    request_id = set_request_id(None)

    assert request_id
    assert get_request_id() == request_id


def test_uses_supplied_id() -> None:
    request_id = set_request_id("abc123")

    assert request_id == "abc123"
    assert get_request_id() == "abc123"
