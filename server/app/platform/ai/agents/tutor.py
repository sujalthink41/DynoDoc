"""The lesson tutor — an ADK LlmAgent that answers questions about ONE lesson.

The lesson content, lecture, and course goal are supplied in the user prompt;
this agent grounds its answer in that content and refuses to wander off the
lesson's technical topic. Structured output is requested in the instruction and
parsed by the caller.
"""

from google.adk.agents import LlmAgent
from google.adk.models.base_llm import BaseLlm

from app.domains.course.dtos import TutorReply
from app.platform.ai import prompts

_INSTRUCTION = f"{prompts.TUTOR}\n\n{prompts.respond_json_only(TutorReply)}"


def build_tutor_agent(model: BaseLlm) -> LlmAgent:
    return LlmAgent(
        name="lesson_tutor",
        model=model,
        instruction=_INSTRUCTION,
        output_key="tutor",
    )
