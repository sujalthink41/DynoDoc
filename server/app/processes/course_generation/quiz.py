"""Quiz generation — one AI-written multiple-choice quiz per lesson.

The quiz is drafted from the lesson's already-generated `Doc` (so a lesson must
be generated before its quiz exists) and cached: re-requesting returns the stored
quiz instead of spending tokens again.
"""

from google.adk.models.base_llm import BaseLlm
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.course.dtos import QuizSpec
from app.domains.course.models import Lecture, Quiz
from app.domains.course.repository import add_quiz, get_quiz, list_docs
from app.platform.ai.agents.quizzer import build_quiz_agent
from app.platform.ai.run import run_agent_structured
from app.shared.errors import ValidationError


def _quiz_prompt(lecture: Lecture, topic: str, content: str) -> str:
    return (
        f"Lecture: {lecture.title}\nLesson topic: {topic}\n\nLesson content (Markdown):\n{content}"
    )


async def generate_quiz(
    session: AsyncSession, *, model: BaseLlm, lecture: Lecture, topic_index: int
) -> Quiz:
    """Return the cached quiz for a lesson, drafting it from the lesson doc if absent."""
    existing = await get_quiz(session, lecture.id, topic_index)
    if existing is not None:
        return existing

    docs = await list_docs(session, lecture.id)
    doc = next((d for d in docs if d.position == topic_index + 1), None)
    if doc is None:
        raise ValidationError("Generate the lesson before its quiz", code="lesson_not_generated")

    topic = lecture.topics[topic_index]
    spec = await run_agent_structured(
        build_quiz_agent(model), _quiz_prompt(lecture, topic, doc.content), QuizSpec
    )
    quiz = await add_quiz(
        session,
        lecture_id=lecture.id,
        topic_index=topic_index,
        questions=[q.model_dump() for q in spec.questions],
    )
    logger.bind(lecture_id=str(lecture.id), topic_index=topic_index).info("quiz generated")
    return quiz
