"""Course request schemas."""

from uuid import UUID

from pydantic import BaseModel


class CreateCourseRequest(BaseModel):
    intake_id: UUID
