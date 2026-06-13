"""Integration: IntakeService against real SQLite + a fake LLM."""

from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.course.dtos import IntakeStep, LearnerProfile
from app.domains.course.service import IntakeService
from tests.fixtures.fakes import FakeTextGenerator


async def test_start_asks_one_question_and_stays_in_progress(db_session: AsyncSession) -> None:
    generator = FakeTextGenerator()
    generator.queue(
        IntakeStep(on_topic=True, is_complete=False, message="What's your experience with Python?")
    )

    intake = await IntakeService(generator).start(
        db_session, owner_user_id=uuid4(), goal="Learn Python"
    )

    assert intake.status == "in_progress"
    assert intake.profile is None
    # Transcript: the goal (user) then the single assistant question.
    assert intake.transcript == [
        {"role": "user", "content": "Learn Python"},
        {"role": "assistant", "content": "What's your experience with Python?"},
    ]


async def test_answer_completes_with_profile(db_session: AsyncSession) -> None:
    generator = FakeTextGenerator()
    generator.queue(IntakeStep(on_topic=True, is_complete=False, message="What's your level?"))
    generator.queue(
        IntakeStep(
            on_topic=True,
            is_complete=True,
            message="Great — building your plan now!",
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
    roles = [turn["role"] for turn in intake.transcript]
    assert "assistant" in roles
    assert "user" in roles


async def test_off_topic_request_is_refused(db_session: AsyncSession) -> None:
    generator = FakeTextGenerator()
    generator.queue(
        IntakeStep(
            on_topic=False,
            is_complete=False,
            message="DynoDoc only builds technical learning courses — share a tech topic!",
        )
    )

    intake = await IntakeService(generator).start(
        db_session, owner_user_id=uuid4(), goal="Teach me to cook pasta"
    )

    # Off-topic never completes and never produces a profile.
    assert intake.status == "in_progress"
    assert intake.profile is None
    assert intake.transcript[-1]["role"] == "assistant"
