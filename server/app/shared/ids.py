"""ID generation. UUIDv7 when available (time-ordered → better index locality)."""

import uuid
from uuid import UUID


def new_uuid7() -> UUID:
    candidate = getattr(uuid, "uuid7", uuid.uuid4)()
    if not isinstance(candidate, UUID):  # pragma: no cover - defensive
        raise TypeError("UUID factory returned a non-UUID value")
    return candidate
