"""Integration: IntakeService against real SQLite + a fake LLM."""

from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.course.dtos import IntakeStep, LearnerProfile
from app.domains.course.service import IntakeService
from tests.fixtures.fakes import FakeTextGenerator


async def test_start_returns_questions_and_stays_in_progress(db_session: AsyncSession) -> None:
    generator = FakeTextGenerator()
    generator.queue(
        IntakeStep(is_complete=False, questions=["What's your level?", "Hours per week?"])
    )

    intake = await IntakeService(generator).start(
        db_session, owner_user_id=uuid4(), goal="Learn Python"
    )

    assert intake.status == "in_progress"
    assert intake.pending_questions == ["What's your level?", "Hours per week?"]
    assert intake.profile is None


async def test_answer_completes_with_profile(db_session: AsyncSession) -> None:
    generator = FakeTextGenerator()
    generator.queue(IntakeStep(is_complete=False, questions=["What's your level?"]))
    generator.queue(
        IntakeStep(
            is_complete=True,
            profile=LearnerProfile(
                experience_level="beginner",
                background="some JavaScript",
                goal="automate spreadsheets",
                weekly_time="5 hours",
            ),
        )
    )
    service = IntakeService(generator)

    intake = await service.start(db_session, owner_user_id=uuid4(), goal="Learn Python")
    intake = await service.answer(db_session, intake=intake, answer="beginner, 5h/week, know JS")

    assert intake.status == "ready"
    assert intake.profile is not None
    assert intake.profile["experience_level"] == "beginner"
    assert intake.pending_questions == []
    # transcript captured the assistant question + the user's answer
    roles = [turn["role"] for turn in intake.transcript]
    assert "assistant" in roles
    assert "user" in roles
