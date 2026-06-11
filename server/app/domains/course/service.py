"""Intake use cases: turn a goal + a short Q&A into a learner profile.

Depends only on the `TextGenerator` port, so it's fully testable with a fake.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.course.dtos import IntakeStep
from app.domains.course.models import IntakeSession
from app.domains.course.repository import create_intake_session
from app.shared.contracts.llm import Message, TextGenerator

_SYSTEM_PROMPT = (
    "You are DynoDoc's onboarding assistant. The learner wants to learn something. "
    "Ask up to 5 short, specific questions to understand their current level, "
    "relevant background, concrete goal, and weekly time. When you have enough to "
    "build a personalized plan, set is_complete=true and fill in the profile; "
    "otherwise set is_complete=false and return the next questions."
)


class IntakeService:
    def __init__(self, generator: TextGenerator) -> None:
        self._generator = generator

    async def start(
        self, session: AsyncSession, *, owner_user_id: UUID, goal: str
    ) -> IntakeSession:
        intake = await create_intake_session(session, owner_user_id=owner_user_id, goal=goal)
        step = await self._next_step(goal, intake.transcript)
        self._apply_step(intake, step)
        return intake

    async def answer(
        self, session: AsyncSession, *, intake: IntakeSession, answer: str
    ) -> IntakeSession:
        intake.transcript = [*intake.transcript, {"role": "user", "content": answer}]
        step = await self._next_step(intake.goal, intake.transcript)
        self._apply_step(intake, step)
        return intake

    async def _next_step(self, goal: str, transcript: list[dict[str, str]]) -> IntakeStep:
        messages = [
            Message(role="system", content=_SYSTEM_PROMPT),
            Message(role="user", content=f"I want to learn: {goal}"),
        ]
        messages.extend(Message(role=turn["role"], content=turn["content"]) for turn in transcript)
        return await self._generator.generate_structured(messages, schema=IntakeStep)

    def _apply_step(self, intake: IntakeSession, step: IntakeStep) -> None:
        if step.is_complete and step.profile is not None:
            intake.status = "ready"
            intake.profile = step.profile.model_dump()
            intake.pending_questions = []
        else:
            intake.status = "in_progress"
            intake.pending_questions = step.questions
            intake.transcript = [
                *intake.transcript,
                {"role": "assistant", "content": "\n".join(step.questions)},
            ]
