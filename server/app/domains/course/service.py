"""Intake use cases: turn a goal + a short Q&A into a learner profile.

Depends only on the `TextGenerator` port, so it's fully testable with a fake.
The conversation is deliberately guard-railed: DynoDoc only plans *technical*
learning, and the assistant asks ONE focused question at a time.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.course.dtos import IntakeStep
from app.domains.course.models import IntakeSession
from app.domains.course.repository import create_intake_session
from app.platform.ai import prompts
from app.shared.contracts.llm import Message, TextGenerator

_SYSTEM_PROMPT = prompts.INTAKE_SYSTEM


class IntakeService:
    def __init__(self, generator: TextGenerator) -> None:
        self._generator = generator

    async def start(
        self, session: AsyncSession, *, owner_user_id: UUID, goal: str
    ) -> IntakeSession:
        intake = await create_intake_session(session, owner_user_id=owner_user_id, goal=goal)
        intake.transcript = [{"role": "user", "content": goal}]
        step = await self._next_step(intake.transcript)
        self._apply_step(intake, step)
        return intake

    async def answer(
        self, session: AsyncSession, *, intake: IntakeSession, answer: str
    ) -> IntakeSession:
        intake.transcript = [*intake.transcript, {"role": "user", "content": answer}]
        step = await self._next_step(intake.transcript)
        self._apply_step(intake, step)
        return intake

    async def _next_step(self, transcript: list[dict[str, str]]) -> IntakeStep:
        messages = [Message(role="system", content=_SYSTEM_PROMPT)]
        messages.extend(Message(role=turn["role"], content=turn["content"]) for turn in transcript)
        return await self._generator.generate_structured(messages, schema=IntakeStep)

    def _apply_step(self, intake: IntakeSession, step: IntakeStep) -> None:
        if step.message:
            intake.transcript = [
                *intake.transcript,
                {"role": "assistant", "content": step.message},
            ]
        if step.on_topic and step.is_complete and step.profile is not None:
            intake.status = "ready"
            intake.profile = step.profile.model_dump()
        else:
            intake.status = "in_progress"
