"""Composition root — wires ports (shared/contracts) to platform adapters.

This is the ONLY place where concrete adapters meet the abstractions that
domains and processes depend on. It is intentionally a no-op for Phase 0 and
grows one binding at a time as each slice introduces a port + adapter.
"""

from fastapi import FastAPI

from app.runtime.settings import Settings


def wire(_app: FastAPI, _settings: Settings) -> None:
    """Bind dependency providers onto the app. No-op for Phase 0."""
