"""Answer a learner's question about a single lesson, grounded in its content.

The lesson must already be generated (a `Doc` exists). The tutor agent receives
the course goal, lecture, lesson topic, the lesson Markdown, and the short
conversation so far, then returns a grounded, on-topic answer.
"""

from google.adk.models.base_llm import BaseLlm
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.course.dtos import TutorReply, TutorTurn
from app.domains.course.models import Lecture
from app.domains.course.repository import get_course, list_docs
from app.platform.ai.agents.tutor import build_tutor_agent
from app.platform.ai.run import run_agent_structured
from app.shared.errors import ValidationError


def _tutor_prompt(
    *,
    course_goal: str,
    lecture: Lecture,
    topic: str,
    content: str,
    history: list[TutorTurn],
    question: str,
) -> str:
    convo = (
        "\n".join(
            f"{'Learner' if turn.role == 'user' else 'Tutor'}: {turn.content}" for turn in history
        )
        or "(no earlier messages)"
    )
    return (
        f"Course goal: {course_goal}\n"
        f"Lecture: {lecture.title} — {lecture.summary}\n"
        f"Lesson topic: {topic}\n\n"
        f"Lesson content (Markdown):\n{content}\n\n"
        f"Conversation so far:\n{convo}\n\n"
        f"Learner's question: {question}"
    )


async def answer_lesson_question(
    session: AsyncSession,
    *,
    model: BaseLlm,
    lecture: Lecture,
    topic_index: int,
    question: str,
    history: list[TutorTurn],
) -> TutorReply:
    docs = await list_docs(session, lecture.id)
    doc = next((d for d in docs if d.position == topic_index + 1), None)
    if doc is None:
        raise ValidationError(
            "Generate the lesson before asking about it", code="lesson_not_generated"
        )

    course = await get_course(session, lecture.course_id)
    prompt = _tutor_prompt(
        course_goal=course.goal if course else "",
        lecture=lecture,
        topic=lecture.topics[topic_index],
        content=doc.content,
        history=history,
        question=question,
    )
    reply = await run_agent_structured(build_tutor_agent(model), prompt, TutorReply)
    logger.bind(lecture_id=str(lecture.id), topic_index=topic_index).info("tutor answered")
    return reply
