"""Run a single ADK agent for one structured turn and parse its JSON output.

Shared by the architect and the per-topic writers. Structured output is parsed
from the model's text (ADK `output_schema` is unreliable with nested/optional
models under LiteLLM), so callers pass the Pydantic schema to validate against.
"""

from uuid import uuid4

from google.adk.agents import BaseAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pydantic import BaseModel

_APP_NAME = "dynodoc"
_USER_ID = "system"


def _extract_json(text: str) -> str:
    start, end = text.find("{"), text.rfind("}")
    return text[start : end + 1] if start != -1 and end > start else text


async def run_agent_structured[SchemaT: BaseModel](
    agent: BaseAgent, prompt: str, schema: type[SchemaT]
) -> SchemaT:
    session_service = InMemorySessionService()  # type: ignore[no-untyped-call]
    session_id = uuid4().hex
    await session_service.create_session(
        app_name=_APP_NAME, user_id=_USER_ID, session_id=session_id
    )
    runner = Runner(agent=agent, app_name=_APP_NAME, session_service=session_service)
    content = types.Content(role="user", parts=[types.Part(text=prompt)])

    final_text = ""
    async for event in runner.run_async(
        user_id=_USER_ID, session_id=session_id, new_message=content
    ):
        if event.is_final_response() and event.content and event.content.parts:
            part_text = event.content.parts[0].text
            if part_text:
                final_text = part_text

    return schema.model_validate_json(_extract_json(final_text))
