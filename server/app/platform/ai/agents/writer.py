"""The lecture writer — an ADK LlmAgent that drafts one lesson doc for a topic.

Many of these run concurrently (one per topic) via asyncio.gather in the writer
process. Structured output requested in the instruction and parsed by the caller.
"""

import json

from google.adk.agents import LlmAgent
from google.adk.models.base_llm import BaseLlm

from app.domains.course.dtos import DocDraft

_INSTRUCTION = (
    "You are an expert teacher and technical writer for DynoDoc. Write ONE clear, "
    "well-structured lesson in Markdown for the specific topic given in the user "
    "message, tailored to the learner's profile (match their level and background, "
    "use concrete short examples and analogies). Keep it focused on that single "
    "topic. Give the doc a short title.\n\n"
    "Respond with ONLY a single JSON object matching this JSON Schema "
    "(no markdown fences, no prose outside the JSON):\n" + json.dumps(DocDraft.model_json_schema())
)


def build_writer_agent(model: BaseLlm) -> LlmAgent:
    return LlmAgent(
        name="lecture_writer",
        model=model,
        instruction=_INSTRUCTION,
        output_key="doc",
    )
