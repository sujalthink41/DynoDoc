"""The curriculum architect — an ADK LlmAgent that designs the roadmap.

Structured output is requested in the instruction (JSON Schema) and parsed by the
caller, because ADK's `output_schema` has known bugs with nested/optional models
under LiteLLM. The model is injected (LiteLlm in prod, a fake BaseLlm in tests).
"""

from google.adk.agents import LlmAgent
from google.adk.models.base_llm import BaseLlm

from app.domains.course.dtos import Roadmap
from app.platform.ai import prompts

_INSTRUCTION = f"{prompts.ARCHITECT}\n\n{prompts.respond_json_only(Roadmap)}"


def build_architect_agent(model: BaseLlm) -> LlmAgent:
    return LlmAgent(
        name="curriculum_architect",
        model=model,
        instruction=_INSTRUCTION,
        output_key="roadmap",
    )
