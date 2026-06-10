"""Domain events emitted by the user context.

Defined now; published once the event outbox lands (slice 0.3).
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class UserRegistered:
    user_id: UUID
    email: str
    occurred_at: datetime
