"""The quiz writer — an ADK LlmAgent that drafts a multiple-choice quiz for a lesson.

Generates exactly 5 questions from the lesson's content so a learner must pass
(>= 80%) before the next lesson is unlocked. Structured output requested in the
instruction and parsed by the caller.
"""

import json

from google.adk.agents import LlmAgent
from google.adk.models.base_llm import BaseLlm

from app.domains.course.dtos import QuizSpec

_INSTRUCTION = (
    "You are an assessment designer for DynoDoc. From the lesson content in the user "
    "message, write EXACTLY 5 multiple-choice questions that test real understanding "
    "(not trivia). Each question must have EXACTLY 4 options with exactly one correct "
    "answer; set `answer_index` to the 0-based index of the correct option. Cover "
    "different parts of the lesson and avoid trick questions.\n\n"
    "Respond with ONLY a single JSON object matching this JSON Schema "
    "(no markdown fences, no prose outside the JSON):\n" + json.dumps(QuizSpec.model_json_schema())
)


def build_quiz_agent(model: BaseLlm) -> LlmAgent:
    return LlmAgent(
        name="quiz_writer",
        model=model,
        instruction=_INSTRUCTION,
        output_key="quiz",
    )
