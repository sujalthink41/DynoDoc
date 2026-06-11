"""Course generation pipeline (orchestrated here, not by ADK workflow agents).

Increment 1: the *architect* step — turn a goal + learner profile into a roadmap
of ordered lectures. Each step is one structured call through the TextGenerator
port (ADK-backed), so the whole pipeline is testable with a fake and we keep
explicit control over sequencing, errors, and cost. Lecture *content* generation
(the next step) will fan out per-lecture with asyncio.
"""

from typing import Any
from uuid import UUID

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.course.dtos import Roadmap
from app.domains.course.models import Course
from app.domains.course.repository import add_lecture, create_course
from app.shared.contracts.llm import Message, TextGenerator

_ARCHITECT_SYSTEM = (
    "You are an expert curriculum architect for DynoDoc. Given a learner's goal "
    "and profile, design a focused, well-sequenced roadmap of 4 to 8 lectures that "
    "takes them from their current level to their goal. Each lecture needs a clear "
    "title, a 1-2 sentence summary, and 2-5 concrete topics. Tailor depth and "
    "pacing to the learner's experience level and weekly time. Also give the course "
    "a concise title."
)


def _architect_messages(goal: str, profile: dict[str, Any]) -> list[Message]:
    profile_lines = "\n".join(f"- {key}: {value}" for key, value in profile.items())
    return [
        Message(role="system", content=_ARCHITECT_SYSTEM),
        Message(
            role="user",
            content=f"Goal: {goal}\n\nLearner profile:\n{profile_lines}",
        ),
    ]


async def generate_course(
    session: AsyncSession,
    *,
    generator: TextGenerator,
    owner_user_id: UUID,
    intake_session_id: UUID,
    goal: str,
    profile: dict[str, Any],
) -> Course:
    roadmap = await generator.generate_structured(
        _architect_messages(goal, profile), schema=Roadmap
    )

    course = await create_course(
        session,
        owner_user_id=owner_user_id,
        intake_session_id=intake_session_id,
        title=roadmap.title,
        goal=goal,
        learner_profile=profile,
    )
    for position, lecture in enumerate(roadmap.lectures, start=1):
        await add_lecture(
            session,
            course_id=course.id,
            position=position,
            title=lecture.title,
            summary=lecture.summary,
            topics=lecture.topics,
        )

    logger.bind(course_id=str(course.id), lectures=len(roadmap.lectures)).info(
        "course roadmap generated"
    )
    return course
