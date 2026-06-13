"""Lecture routes — read a lecture, generate one gated topic at a time, quizzes."""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from google.adk.models.base_llm import BaseLlm
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.course.dtos import (
    LectureDetailView,
    QuizQuestionView,
    QuizResult,
    QuizResultItem,
    QuizView,
    TutorReply,
)
from app.domains.course.models import Lecture
from app.domains.course.progress import (
    PASS_THRESHOLD,
    build_lecture_detail_view,
    is_lesson_unlocked,
)
from app.domains.course.repository import (
    get_course,
    get_lecture,
    get_lesson_progress,
    get_quiz,
    list_docs,
    list_references,
    record_quiz_score,
)
from app.domains.user.models import User
from app.entrypoints.http.deps import (
    db_session,
    get_llm_model,
    get_resource_curator,
    require_principal,
)
from app.entrypoints.http.schemas.quiz import QuizAttemptRequest
from app.entrypoints.http.schemas.tutor import AskRequest
from app.processes.course_generation.curation import generate_lecture_references
from app.processes.course_generation.quiz import generate_quiz
from app.processes.course_generation.writer import generate_topic_doc
from app.processes.tutoring.answer import answer_lesson_question
from app.shared.contracts.curation import ResourceCurator
from app.shared.errors import (
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)

MASTERY_SCORE = 100

router = APIRouter(prefix="/lectures", tags=["lectures"])


async def _load_owned_lecture(session: AsyncSession, lecture_id: UUID, user: User) -> Lecture:
    lecture = await get_lecture(session, lecture_id)
    if lecture is not None:
        course = await get_course(session, lecture.course_id)
        if course is not None and course.owner_user_id == user.id:
            return lecture
    raise NotFoundError("Lecture not found", code="lecture_not_found")


def _ensure_topic_in_range(lecture: Lecture, topic_index: int) -> None:
    if topic_index < 0 or topic_index >= len(lecture.topics):
        raise NotFoundError("Topic not found", code="topic_not_found")


async def _detail(session: AsyncSession, *, user: User, lecture: Lecture) -> LectureDetailView:
    return await build_lecture_detail_view(session, user_id=user.id, lecture=lecture)


@router.get("/{lecture_id}", response_model=LectureDetailView)
async def get_lecture_route(
    lecture_id: UUID,
    user: User = Depends(require_principal),
    session: AsyncSession = Depends(db_session),
) -> LectureDetailView:
    lecture = await _load_owned_lecture(session, lecture_id, user)
    return await _detail(session, user=user, lecture=lecture)


@router.post("/{lecture_id}/topics/{topic_index}", response_model=LectureDetailView)
async def generate_topic_route(
    lecture_id: UUID,
    topic_index: int,
    user: User = Depends(require_principal),
    session: AsyncSession = Depends(db_session),
    model: BaseLlm = Depends(get_llm_model),
) -> LectureDetailView:
    lecture = await _load_owned_lecture(session, lecture_id, user)
    _ensure_topic_in_range(lecture, topic_index)

    docs = await list_docs(session, lecture.id)
    if any(doc.position == topic_index + 1 for doc in docs):  # already generated — idempotent
        return await _detail(session, user=user, lecture=lecture)

    if not await is_lesson_unlocked(
        session, user_id=user.id, lecture=lecture, topic_index=topic_index
    ):
        raise PermissionDeniedError(
            "Pass the previous lesson's quiz to unlock this one", code="lesson_locked"
        )

    course = await get_course(session, lecture.course_id)
    profile = (course.learner_profile if course else None) or {}
    await generate_topic_doc(
        session, model=model, lecture=lecture, topic_index=topic_index, profile=profile
    )

    docs = await list_docs(session, lecture.id)
    lecture.status = "ready" if len(docs) >= len(lecture.topics) else "in_progress"
    return await _detail(session, user=user, lecture=lecture)


@router.post("/{lecture_id}/references", response_model=LectureDetailView)
async def generate_references_route(
    lecture_id: UUID,
    user: User = Depends(require_principal),
    session: AsyncSession = Depends(db_session),
    curator: ResourceCurator = Depends(get_resource_curator),
) -> LectureDetailView:
    lecture = await _load_owned_lecture(session, lecture_id, user)
    if not await list_references(session, lecture.id):  # idempotent
        await generate_lecture_references(session, curator=curator, lecture=lecture)
    return await _detail(session, user=user, lecture=lecture)


def _answer_indices(questions: list[dict[str, Any]]) -> list[int]:
    return [int(q["answer_index"]) for q in questions]


@router.post("/{lecture_id}/topics/{topic_index}/quiz", response_model=QuizView)
async def generate_quiz_route(
    lecture_id: UUID,
    topic_index: int,
    user: User = Depends(require_principal),
    session: AsyncSession = Depends(db_session),
    model: BaseLlm = Depends(get_llm_model),
) -> QuizView:
    lecture = await _load_owned_lecture(session, lecture_id, user)
    _ensure_topic_in_range(lecture, topic_index)
    quiz = await generate_quiz(session, model=model, lecture=lecture, topic_index=topic_index)

    progress = await get_lesson_progress(session, user.id, lecture.id, topic_index)
    best_score = progress.best_score if progress else 0
    mastered = best_score >= MASTERY_SCORE
    return QuizView(
        lecture_id=lecture.id,
        topic_index=topic_index,
        questions=[
            QuizQuestionView(question=q["question"], options=q["options"]) for q in quiz.questions
        ],
        best_score=best_score,
        mastered=mastered,
        # Reveal the correct answers only once the lesson is mastered (review mode).
        answers=_answer_indices(quiz.questions) if mastered else None,
    )


@router.post("/{lecture_id}/topics/{topic_index}/quiz/attempt", response_model=QuizResult)
async def attempt_quiz_route(
    lecture_id: UUID,
    topic_index: int,
    body: QuizAttemptRequest,
    user: User = Depends(require_principal),
    session: AsyncSession = Depends(db_session),
) -> QuizResult:
    lecture = await _load_owned_lecture(session, lecture_id, user)
    _ensure_topic_in_range(lecture, topic_index)

    quiz = await get_quiz(session, lecture.id, topic_index)
    if quiz is None:
        raise ValidationError("Generate the quiz first", code="quiz_not_generated")

    existing = await get_lesson_progress(session, user.id, lecture.id, topic_index)
    if existing is not None and existing.best_score >= MASTERY_SCORE:
        raise ConflictError("You've already mastered this quiz", code="quiz_mastered")

    total = len(quiz.questions)
    correct_flags = [
        (body.answers[i] if i < len(body.answers) else -1) == int(q["answer_index"])
        for i, q in enumerate(quiz.questions)
    ]
    correct_count = sum(correct_flags)

    score = round(correct_count / total * 100) if total else 0
    passed = score >= PASS_THRESHOLD
    progress = await record_quiz_score(
        session, user_id=user.id, lecture_id=lecture.id, topic_index=topic_index, score=score
    )
    mastered = progress.best_score >= MASTERY_SCORE

    # Correct answers are revealed only on mastery — never on a failing/partial pass.
    answers = _answer_indices(quiz.questions)
    results = [
        QuizResultItem(correct=flag, answer_index=answers[i] if mastered else None)
        for i, flag in enumerate(correct_flags)
    ]
    return QuizResult(
        score=score,
        passed=passed,
        total=total,
        correct_count=correct_count,
        mastered=mastered,
        can_retake=not mastered,
        results=results,
        unlocked_next=passed,
    )


@router.post("/{lecture_id}/topics/{topic_index}/ask", response_model=TutorReply)
async def ask_tutor_route(
    lecture_id: UUID,
    topic_index: int,
    body: AskRequest,
    user: User = Depends(require_principal),
    session: AsyncSession = Depends(db_session),
    model: BaseLlm = Depends(get_llm_model),
) -> TutorReply:
    lecture = await _load_owned_lecture(session, lecture_id, user)
    _ensure_topic_in_range(lecture, topic_index)
    if not body.question.strip():
        raise ValidationError("Ask a question", code="empty_question")
    return await answer_lesson_question(
        session,
        model=model,
        lecture=lecture,
        topic_index=topic_index,
        question=body.question,
        history=body.history,
    )
