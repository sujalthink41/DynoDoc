"""Integration: the ADK course-generation pipeline against real SQLite + a fake LLM."""

from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.course.dtos import Roadmap, RoadmapLecture
from app.domains.course.repository import list_lectures
from app.processes.course_generation.pipeline import generate_course
from tests.fixtures.fakes import FakeLlm

PROFILE = {
    "experience_level": "beginner",
    "background": "none",
    "goal": "build small scripts",
    "weekly_time": "5 hours",
}

ROADMAP = Roadmap(
    title="Python for Beginners",
    lectures=[
        RoadmapLecture(title="Basics", summary="Vars & types", topics=["variables", "types"]),
        RoadmapLecture(title="Control Flow", summary="if/for", topics=["if", "loops"]),
    ],
)


async def test_generate_course_creates_ordered_lectures(db_session: AsyncSession) -> None:
    model = FakeLlm(responses=[ROADMAP.model_dump_json()])

    course = await generate_course(
        db_session,
        model=model,
        owner_user_id=uuid4(),
        intake_session_id=uuid4(),
        goal="Learn Python",
        profile=PROFILE,
    )

    assert course.title == "Python for Beginners"
    assert course.status == "ready"

    lectures = await list_lectures(db_session, course.id)
    assert [lecture.position for lecture in lectures] == [1, 2]
    assert lectures[0].title == "Basics"
    assert lectures[0].topics == ["variables", "types"]
