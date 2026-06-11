"""Course generation pipeline — orchestrated with Google ADK agents.

Increment 1: a `SequentialAgent` whose first stage is the curriculum architect.
The next increment adds a per-lecture writer fanned out via `ParallelAgent`.
The model is injected (LiteLlm in prod, a fake BaseLlm in tests), so the agent
pipeline runs offline + deterministically under test.
"""

from typing import Any
from uuid import UUID, uuid4

from google.adk.models.base_llm import BaseLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.course.dtos import Roadmap
from app.domains.course.models import Course
from app.domains.course.repository import add_lecture, create_course
from app.platform.ai.agents.architect import build_architect_agent

_APP_NAME = "dynodoc"
_USER_ID = "system"


def _user_prompt(goal: str, profile: dict[str, Any]) -> str:
    profile_lines = "\n".join(f"- {key}: {value}" for key, value in profile.items())
    return f"Goal: {goal}\n\nLearner profile:\n{profile_lines}"


def _extract_json(text: str) -> str:
    start, end = text.find("{"), text.rfind("}")
    return text[start : end + 1] if start != -1 and end > start else text


async def _run_pipeline(model: BaseLlm, goal: str, profile: dict[str, Any]) -> Roadmap:
    # Single architect agent for now. When we add the per-lecture writer, we'll
    # compose them with ADK's current multi-agent construct (ADK 2.2 deprecated
    # SequentialAgent/ParallelAgent in favour of its Workflow API).
    architect = build_architect_agent(model)
    session_service = InMemorySessionService()  # type: ignore[no-untyped-call]
    session_id = uuid4().hex
    await session_service.create_session(
        app_name=_APP_NAME, user_id=_USER_ID, session_id=session_id
    )
    runner = Runner(agent=architect, app_name=_APP_NAME, session_service=session_service)
    content = types.Content(role="user", parts=[types.Part(text=_user_prompt(goal, profile))])

    final_text = ""
    async for event in runner.run_async(
        user_id=_USER_ID, session_id=session_id, new_message=content
    ):
        if event.is_final_response() and event.content and event.content.parts:
            part_text = event.content.parts[0].text
            if part_text:
                final_text = part_text

    return Roadmap.model_validate_json(_extract_json(final_text))


async def generate_course(
    session: AsyncSession,
    *,
    model: BaseLlm,
    owner_user_id: UUID,
    intake_session_id: UUID,
    goal: str,
    profile: dict[str, Any],
) -> Course:
    roadmap = await _run_pipeline(model, goal, profile)

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
