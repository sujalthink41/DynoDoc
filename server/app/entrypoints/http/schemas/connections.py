"""Request schema for the Connections game."""

from pydantic import BaseModel


class ConnectionsAttemptRequest(BaseModel):
    """The learner's four guessed groups + how long the solve took (seconds)."""

    groups: list[list[str]]
    duration_seconds: int = 0
