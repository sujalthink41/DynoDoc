"""The curriculum architect — an ADK LlmAgent that designs the roadmap.

Structured output is requested in the instruction (JSON Schema) and parsed by the
caller, because ADK's `output_schema` has known bugs with nested/optional models
under LiteLLM. The model is injected (LiteLlm in prod, a fake BaseLlm in tests).
"""

import json

from google.adk.agents import LlmAgent
from google.adk.models.base_llm import BaseLlm

from app.domains.course.dtos import Roadmap

_INSTRUCTION = (
    "You are an expert curriculum architect for DynoDoc. The user message contains a "
    "learner's goal and profile. Design a focused, well-sequenced roadmap of 4 to 8 "
    "lectures that takes them from their current level to their goal. Each lecture needs "
    "a clear title, a 1-2 sentence summary, and 2-5 concrete topics. Tailor depth and "
    "pacing to the learner's experience level and weekly time, and give the course a "
    "concise title.\n\n"
    "Respond with ONLY a single JSON object matching this JSON Schema "
    "(no markdown fences, no prose):\n" + json.dumps(Roadmap.model_json_schema())
)


def build_architect_agent(model: BaseLlm) -> LlmAgent:
    return LlmAgent(
        name="curriculum_architect",
        model=model,
        instruction=_INSTRUCTION,
        output_key="roadmap",
    )
