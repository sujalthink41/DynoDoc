"""Course progression — strictly sequential lesson unlocking + progress-aware views.

A course is one ordered list of lessons: lectures by position, topics by index.
Only the first lesson is open; each next lesson unlocks once the previous lesson's
quiz is passed (best score >= PASS_THRESHOLD).
"""

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.course import repository as repo
from app.domains.course.dtos import (
    CourseSummary,
    CourseView,
    LectureDetailView,
    LectureView,
    LessonState,
)
from app.domains.course.models import Course, Lecture
from app.domains.gamification import repository as game_repo

PASS_THRESHOLD = 80


@dataclass
class LessonInfo:
    """Computed state for one lesson (lecture + topic) within a course."""

    lecture_id: UUID
    topic_index: int
    topic: str
    generated: bool
    attempted: bool
    passed: bool
    score: int
    unlocked: bool


async def compute_lessons(
    session: AsyncSession, course_id: UUID, user_id: UUID
) -> list[LessonInfo]:
    """Flatten a course into its ordered lessons with unlock/pass/score state."""
    lectures = await repo.list_lectures(session, course_id)
    progress = await repo.list_lesson_progress_for_course(session, user_id, course_id)
    prog_map = {(p.lecture_id, p.topic_index): p for p in progress}
    purchased = await game_repo.list_unlocked_lessons(session, user_id, course_id)

    lessons: list[LessonInfo] = []
    for lecture in lectures:
        docs = await repo.list_docs(session, lecture.id)
        generated_positions = {doc.position for doc in docs}
        for topic_index, topic in enumerate(lecture.topics):
            record = prog_map.get((lecture.id, topic_index))
            lessons.append(
                LessonInfo(
                    lecture_id=lecture.id,
                    topic_index=topic_index,
                    topic=topic,
                    generated=(topic_index + 1) in generated_positions,
                    attempted=record is not None,
                    passed=bool(record and record.passed),
                    score=record.best_score if record else 0,
                    unlocked=False,
                )
            )

    # A lesson is readable if it's sequentially unlocked OR coin-purchased; a
    # purchase grants read access only — it never advances the gate for the next.
    previous_passed = True
    for lesson in lessons:
        lesson.unlocked = previous_passed or (lesson.lecture_id, lesson.topic_index) in purchased
        previous_passed = lesson.passed
    return lessons


def _aggregates(lessons: list[LessonInfo]) -> tuple[int, int]:
    """Course completion % (passed / total) and average best score over attempts."""
    total = len(lessons)
    passed = sum(1 for lesson in lessons if lesson.passed)
    attempted = [lesson for lesson in lessons if lesson.attempted]
    completion = round(passed / total * 100) if total else 0
    average = round(sum(lesson.score for lesson in attempted) / len(attempted)) if attempted else 0
    return completion, average


async def build_course_view(session: AsyncSession, *, user_id: UUID, course: Course) -> CourseView:
    lectures = await repo.list_lectures(session, course.id)
    lessons = await compute_lessons(session, course.id, user_id)
    completion, average = _aggregates(lessons)

    by_lecture: dict[UUID, list[LessonInfo]] = {}
    for lesson in lessons:
        by_lecture.setdefault(lesson.lecture_id, []).append(lesson)

    lecture_views = [
        LectureView(
            id=lecture.id,
            position=lecture.position,
            title=lecture.title,
            summary=lecture.summary,
            topics=lecture.topics,
            status=lecture.status,
            lessons_total=len(by_lecture.get(lecture.id, [])),
            lessons_passed=sum(1 for x in by_lecture.get(lecture.id, []) if x.passed),
        )
        for lecture in lectures
    ]
    return CourseView(
        id=course.id,
        title=course.title,
        goal=course.goal,
        status=course.status,
        completion_percent=completion,
        average_score=average,
        lectures=lecture_views,
    )


async def build_course_summary(
    session: AsyncSession, *, user_id: UUID, course: Course
) -> CourseSummary:
    lessons = await compute_lessons(session, course.id, user_id)
    completion, average = _aggregates(lessons)
    return CourseSummary(
        id=course.id,
        title=course.title,
        goal=course.goal,
        status=course.status,
        completion_percent=completion,
        average_score=average,
    )


async def build_lecture_detail_view(
    session: AsyncSession, *, user_id: UUID, lecture: Lecture
) -> LectureDetailView:
    lessons = await compute_lessons(session, lecture.course_id, user_id)
    docs = await repo.list_docs(session, lecture.id)
    references = await repo.list_references(session, lecture.id)
    course = await repo.get_course(session, lecture.course_id)

    lesson_states = [
        LessonState(
            index=lesson.topic_index,
            topic=lesson.topic,
            generated=lesson.generated,
            unlocked=lesson.unlocked,
            attempted=lesson.attempted,
            passed=lesson.passed,
            mastered=lesson.score >= 100,
            score=lesson.score,
        )
        for lesson in lessons
        if lesson.lecture_id == lecture.id
    ]
    return LectureDetailView(
        id=lecture.id,
        position=lecture.position,
        title=lecture.title,
        summary=lecture.summary,
        status=lecture.status,
        course_id=lecture.course_id,
        course_title=course.title if course else "Course",
        lessons=lesson_states,
        docs=[repo.to_doc_view(doc) for doc in docs],
        references=[repo.to_reference_view(ref) for ref in references],
    )


async def is_lesson_unlocked(
    session: AsyncSession, *, user_id: UUID, lecture: Lecture, topic_index: int
) -> bool:
    lessons = await compute_lessons(session, lecture.course_id, user_id)
    return any(
        lesson.unlocked
        for lesson in lessons
        if lesson.lecture_id == lecture.id and lesson.topic_index == topic_index
    )
