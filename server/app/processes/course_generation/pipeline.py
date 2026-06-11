"""Course generation pipeline — orchestrated with Google ADK agents.

The architect (an ADK `LlmAgent`) turns a goal + learner profile into a roadmap
of ordered lectures. The per-lecture writer step lives in `writer.py` and fans
out real ADK writer agents with `asyncio.gather`. The model is injected (LiteLlm
in prod, a fake BaseLlm in tests), so the agents run offline + deterministically
under test.
"""

from typing import Any
from uuid import UUID

from google.adk.models.base_llm import BaseLlm
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.course.dtos import Roadmap
from app.domains.course.models import Course
from app.domains.course.repository import add_lecture, create_course
from app.platform.ai.agents.architect import build_architect_agent
from app.platform.ai.run import run_agent_structured


def _architect_prompt(goal: str, profile: dict[str, Any]) -> str:
    profile_lines = "\n".join(f"- {key}: {value}" for key, value in profile.items())
    return f"Goal: {goal}\n\nLearner profile:\n{profile_lines}"


async def generate_course(
    session: AsyncSession,
    *,
    model: BaseLlm,
    owner_user_id: UUID,
    intake_session_id: UUID,
    goal: str,
    profile: dict[str, Any],
) -> Course:
    roadmap = await run_agent_structured(
        build_architect_agent(model), _architect_prompt(goal, profile), Roadmap
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
