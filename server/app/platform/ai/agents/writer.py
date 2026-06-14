"""The lecture writer — an ADK LlmAgent that drafts one lesson doc for a topic.

Many of these run concurrently (one per topic) via asyncio.gather in the writer
process. Structured output requested in the instruction and parsed by the caller.
"""

from google.adk.agents import LlmAgent
from google.adk.models.base_llm import BaseLlm

from app.domains.course.dtos import DocDraft
from app.platform.ai import prompts

_INSTRUCTION = f"{prompts.WRITER}\n\n{prompts.respond_json_only(DocDraft)}"


def build_writer_agent(model: BaseLlm) -> LlmAgent:
    return LlmAgent(
        name="lecture_writer",
        model=model,
        instruction=_INSTRUCTION,
        output_key="doc",
    )
