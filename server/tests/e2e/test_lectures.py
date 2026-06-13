"""E2E: gated per-topic generation, quizzes, and references — all with a fake LLM."""

from httpx import AsyncClient

from app.domains.course.dtos import (
    DocDraft,
    IntakeStep,
    LearnerProfile,
    QuizQuestion,
    QuizSpec,
    Roadmap,
    RoadmapLecture,
    TutorReply,
)
from app.shared.contracts.curation import ReferenceDraft
from tests.fixtures.fakes import FakeLlm, FakeResourceCurator, FakeTextGenerator


async def _make_course_with_lecture(
    client: AsyncClient, fake_text_generator: FakeTextGenerator, fake_llm: FakeLlm
) -> str:
    await client.post("/api/v1/auth/dev-login", json={"email": "learner@example.com"})
    fake_text_generator.queue(
        IntakeStep(
            is_complete=True,
            profile=LearnerProfile(
                experience_level="beginner", background="none", goal="scripts", weekly_time="3h"
            ),
        )
    )
    intake = await client.post("/api/v1/intake", json={"goal": "Learn Python"})
    intake_id = intake.json()["id"]

    fake_llm.responses.append(
        Roadmap(
            title="Python",
            lectures=[
                RoadmapLecture(title="Basics", summary="Core ideas", topics=["variables", "loops"])
            ],
        ).model_dump_json()
    )
    course = await client.post("/api/v1/courses", json={"intake_id": intake_id})
    return str(course.json()["lectures"][0]["id"])


def _quiz_json(answer_index: int = 0) -> str:
    question = QuizQuestion(question="Q?", options=["a", "b", "c", "d"], answer_index=answer_index)
    return QuizSpec(questions=[question] * 5).model_dump_json()


async def test_first_lesson_open_others_locked(
    client: AsyncClient, fake_text_generator: FakeTextGenerator, fake_llm: FakeLlm
) -> None:
    lecture_id = await _make_course_with_lecture(client, fake_text_generator, fake_llm)

    # The first lesson is open from the start.
    fake_llm.responses.append(DocDraft(title="Variables", content="# Variables").model_dump_json())
    response = await client.post(f"/api/v1/lectures/{lecture_id}/topics/0")
    assert response.status_code == 200
    body = response.json()
    assert [d["position"] for d in body["docs"]] == [1]
    assert body["status"] == "in_progress"
    lessons = body["lessons"]
    assert lessons[0]["generated"] is True
    assert lessons[0]["unlocked"] is True
    assert lessons[1]["unlocked"] is False  # locked until lesson 0's quiz is passed

    # Generating the second lesson is blocked.
    locked = await client.post(f"/api/v1/lectures/{lecture_id}/topics/1")
    assert locked.status_code == 403
    assert locked.json()["code"] == "lesson_locked"


async def test_quiz_pass_unlocks_next_lesson(
    client: AsyncClient, fake_text_generator: FakeTextGenerator, fake_llm: FakeLlm
) -> None:
    lecture_id = await _make_course_with_lecture(client, fake_text_generator, fake_llm)
    fake_llm.responses.append(DocDraft(title="Variables", content="# Variables").model_dump_json())
    await client.post(f"/api/v1/lectures/{lecture_id}/topics/0")

    # Generate the quiz for lesson 0 — 5 questions, answer is always index 1.
    fake_llm.responses.append(_quiz_json(answer_index=1))
    quiz = await client.post(f"/api/v1/lectures/{lecture_id}/topics/0/quiz")
    assert quiz.status_code == 200
    quiz_body = quiz.json()
    assert len(quiz_body["questions"]) == 5
    assert "answer_index" not in quiz_body["questions"][0]  # answers never sent to the client

    # All correct → 100% → mastered → next lesson unlocks, answers now revealed.
    attempt = await client.post(
        f"/api/v1/lectures/{lecture_id}/topics/0/quiz/attempt",
        json={"answers": [1, 1, 1, 1, 1]},
    )
    assert attempt.status_code == 200
    result = attempt.json()
    assert result["score"] == 100
    assert result["passed"] is True
    assert result["unlocked_next"] is True
    assert result["mastered"] is True
    assert result["can_retake"] is False
    assert result["results"][0]["answer_index"] == 1  # revealed on mastery

    # A mastered quiz cannot be retaken.
    retake = await client.post(
        f"/api/v1/lectures/{lecture_id}/topics/0/quiz/attempt",
        json={"answers": [1, 1, 1, 1, 1]},
    )
    assert retake.status_code == 409
    assert retake.json()["code"] == "quiz_mastered"

    # Now the second lesson generates.
    fake_llm.responses.append(DocDraft(title="Loops", content="# Loops").model_dump_json())
    response = await client.post(f"/api/v1/lectures/{lecture_id}/topics/1")
    assert response.status_code == 200
    body = response.json()
    assert [d["position"] for d in body["docs"]] == [1, 2]
    assert body["status"] == "ready"


async def test_passing_without_mastery_hides_answers_and_allows_retake(
    client: AsyncClient, fake_text_generator: FakeTextGenerator, fake_llm: FakeLlm
) -> None:
    lecture_id = await _make_course_with_lecture(client, fake_text_generator, fake_llm)
    fake_llm.responses.append(DocDraft(title="Variables", content="# Variables").model_dump_json())
    await client.post(f"/api/v1/lectures/{lecture_id}/topics/0")
    fake_llm.responses.append(_quiz_json(answer_index=1))
    await client.post(f"/api/v1/lectures/{lecture_id}/topics/0/quiz")

    # 4/5 correct → 80% → passes (next unlocks) but is NOT mastered.
    attempt = await client.post(
        f"/api/v1/lectures/{lecture_id}/topics/0/quiz/attempt",
        json={"answers": [1, 1, 1, 1, 0]},
    )
    result = attempt.json()
    assert result["score"] == 80
    assert result["passed"] is True
    assert result["mastered"] is False
    assert result["can_retake"] is True
    # Answers stay hidden so the learner can't just read them off.
    assert all(item["answer_index"] is None for item in result["results"])
    # The wrong answer is still flagged as incorrect.
    assert result["results"][4]["correct"] is False


async def test_failing_quiz_keeps_next_lesson_locked(
    client: AsyncClient, fake_text_generator: FakeTextGenerator, fake_llm: FakeLlm
) -> None:
    lecture_id = await _make_course_with_lecture(client, fake_text_generator, fake_llm)
    fake_llm.responses.append(DocDraft(title="Variables", content="# Variables").model_dump_json())
    await client.post(f"/api/v1/lectures/{lecture_id}/topics/0")
    fake_llm.responses.append(_quiz_json(answer_index=1))
    await client.post(f"/api/v1/lectures/{lecture_id}/topics/0/quiz")

    # Only 2/5 correct → 40% → fail.
    attempt = await client.post(
        f"/api/v1/lectures/{lecture_id}/topics/0/quiz/attempt",
        json={"answers": [1, 1, 0, 0, 0]},
    )
    result = attempt.json()
    assert result["score"] == 40
    assert result["passed"] is False
    assert result["unlocked_next"] is False
    assert result["can_retake"] is True
    # A failing attempt never reveals the correct answers.
    assert all(item["answer_index"] is None for item in result["results"])

    locked = await client.post(f"/api/v1/lectures/{lecture_id}/topics/1")
    assert locked.status_code == 403


async def test_course_progress_reflects_passed_lessons(
    client: AsyncClient, fake_text_generator: FakeTextGenerator, fake_llm: FakeLlm
) -> None:
    lecture_id = await _make_course_with_lecture(client, fake_text_generator, fake_llm)
    fake_llm.responses.append(DocDraft(title="Variables", content="# Variables").model_dump_json())
    detail = await client.post(f"/api/v1/lectures/{lecture_id}/topics/0")
    course_id = None  # discover via the courses list
    courses = (await client.get("/api/v1/courses")).json()
    course_id = courses[0]["id"]

    fake_llm.responses.append(_quiz_json(answer_index=2))
    await client.post(f"/api/v1/lectures/{lecture_id}/topics/0/quiz")
    await client.post(
        f"/api/v1/lectures/{lecture_id}/topics/0/quiz/attempt",
        json={"answers": [2, 2, 2, 2, 2]},
    )

    course = (await client.get(f"/api/v1/courses/{course_id}")).json()
    # 1 of 2 lessons passed → 50% complete; average best score over attempts = 100.
    assert course["completion_percent"] == 50
    assert course["average_score"] == 100
    assert detail.json()["lessons"][0]["topic"] == "variables"


async def test_find_resources_button(
    client: AsyncClient,
    fake_text_generator: FakeTextGenerator,
    fake_llm: FakeLlm,
    fake_curator: FakeResourceCurator,
) -> None:
    lecture_id = await _make_course_with_lecture(client, fake_text_generator, fake_llm)
    fake_curator.references = [
        ReferenceDraft(type="article", url="https://realpython.com/x", title="Real Python"),
        ReferenceDraft(type="youtube", url="https://youtube.com/watch?v=1", title="Video"),
    ]

    response = await client.post(f"/api/v1/lectures/{lecture_id}/references")
    assert response.status_code == 200
    refs = response.json()["references"]
    assert [r["type"] for r in refs] == ["article", "youtube"]


async def test_ask_tutor_answers_about_generated_lesson(
    client: AsyncClient, fake_text_generator: FakeTextGenerator, fake_llm: FakeLlm
) -> None:
    lecture_id = await _make_course_with_lecture(client, fake_text_generator, fake_llm)
    fake_llm.responses.append(DocDraft(title="Variables", content="# Variables").model_dump_json())
    await client.post(f"/api/v1/lectures/{lecture_id}/topics/0")

    fake_llm.responses.append(
        TutorReply(
            on_topic=True, answer="A variable names a value you can reuse."
        ).model_dump_json()
    )
    response = await client.post(
        f"/api/v1/lectures/{lecture_id}/topics/0/ask",
        json={"question": "What is a variable?", "history": []},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["on_topic"] is True
    assert "variable" in body["answer"].lower()


async def test_ask_tutor_off_topic_is_refused(
    client: AsyncClient, fake_text_generator: FakeTextGenerator, fake_llm: FakeLlm
) -> None:
    lecture_id = await _make_course_with_lecture(client, fake_text_generator, fake_llm)
    fake_llm.responses.append(DocDraft(title="Variables", content="# Variables").model_dump_json())
    await client.post(f"/api/v1/lectures/{lecture_id}/topics/0")

    fake_llm.responses.append(
        TutorReply(on_topic=False, answer="Let's keep it to this lesson!").model_dump_json()
    )
    response = await client.post(
        f"/api/v1/lectures/{lecture_id}/topics/0/ask",
        json={"question": "What's a good pasta recipe?"},
    )
    assert response.status_code == 200
    assert response.json()["on_topic"] is False


async def test_ask_tutor_requires_generated_lesson(
    client: AsyncClient, fake_text_generator: FakeTextGenerator, fake_llm: FakeLlm
) -> None:
    lecture_id = await _make_course_with_lecture(client, fake_text_generator, fake_llm)
    response = await client.post(
        f"/api/v1/lectures/{lecture_id}/topics/0/ask",
        json={"question": "explain this"},
    )
    assert response.status_code == 422
    assert response.json()["code"] == "lesson_not_generated"
