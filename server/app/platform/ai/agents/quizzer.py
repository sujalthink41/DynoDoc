"""The quiz writer — an ADK LlmAgent that drafts a multiple-choice quiz for a lesson.

Generates exactly 5 questions from the lesson's content so a learner must pass
(>= 80%) before the next lesson is unlocked. Structured output requested in the
instruction and parsed by the caller.
"""

from google.adk.agents import LlmAgent
from google.adk.models.base_llm import BaseLlm

from app.domains.course.dtos import QuizSpec
from app.platform.ai import prompts

_INSTRUCTION = f"{prompts.QUIZZER}\n\n{prompts.respond_json_only(QuizSpec)}"


def build_quiz_agent(model: BaseLlm) -> LlmAgent:
    return LlmAgent(
        name="quiz_writer",
        model=model,
        instruction=_INSTRUCTION,
        output_key="quiz",
    )
