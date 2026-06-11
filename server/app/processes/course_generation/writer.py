"""Lecture content generation — fan out writer agents (one per topic) in parallel.

Each topic is drafted by its own ADK writer LlmAgent; `asyncio.gather` runs them
concurrently and we persist the resulting docs in topic order.
"""

import asyncio
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


async def _write_doc(
    model: BaseLlm, lecture: Lecture, topic: str, profile: dict[str, Any]
) -> DocDraft:
    return await run_agent_structured(
        build_writer_agent(model), _writer_prompt(lecture, topic, profile), DocDraft
    )


async def generate_lecture_docs(
    session: AsyncSession, *, model: BaseLlm, lecture: Lecture, profile: dict[str, Any]
) -> list[Doc]:
    drafts = await asyncio.gather(
        *(_write_doc(model, lecture, topic, profile) for topic in lecture.topics)
    )

    docs: list[Doc] = []
    for position, draft in enumerate(drafts, start=1):
        docs.append(
            await add_doc(
                session,
                lecture_id=lecture.id,
                position=position,
                title=draft.title,
                content=draft.content,
            )
        )
    lecture.status = "ready"

    logger.bind(lecture_id=str(lecture.id), docs=len(docs)).info("lecture docs generated")
    return docs
