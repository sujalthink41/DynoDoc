"""Lecture content generation — one topic at a time.

Each topic is drafted on demand by an ADK writer LlmAgent and stored as a `Doc`
whose position matches the topic's index (1-based), so the frontend can map
topics ↔ generated lessons.
"""

from typing import Any

from google.adk.models.base_llm import BaseLlm
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.course.dtos import DocDraft
from app.domains.course.models import Doc, Lecture
from app.domains.course.repository import add_doc
from app.platform.ai.agents.writer import build_writer_agent
from app.platform.ai.run import run_agent_structured


def _writer_prompt(lecture: Lecture, topic: str, profile: dict[str, Any]) -> str:
    profile_lines = "\n".join(f"- {key}: {value}" for key, value in profile.items())
    return (
        f"Lecture: {lecture.title}\n"
        f"Lecture summary: {lecture.summary}\n"
        f"Write the lesson for this topic: {topic}\n\n"
        f"Learner profile:\n{profile_lines}"
    )


async def generate_topic_doc(
    session: AsyncSession,
    *,
    model: BaseLlm,
    lecture: Lecture,
    topic_index: int,
    profile: dict[str, Any],
) -> Doc:
    """Write the lesson doc for a single topic (position = topic_index + 1)."""
    topic = lecture.topics[topic_index]
    draft = await run_agent_structured(
        build_writer_agent(model), _writer_prompt(lecture, topic, profile), DocDraft
    )
    doc = await add_doc(
        session,
        lecture_id=lecture.id,
        position=topic_index + 1,
        title=draft.title,
        content=draft.content,
    )

    logger.bind(lecture_id=str(lecture.id), topic_index=topic_index).info("topic lesson generated")
    return doc
