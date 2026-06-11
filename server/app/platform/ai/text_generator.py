"""TextGenerator implemented with Google ADK + LiteLLM (provider-agnostic).

We drive structured output via *prompt + JSON parse* rather than ADK's
`output_schema`, which has known bugs with nested/optional Pydantic models under
LiteLLM. The model itself is a LiteLLM wrapper, so any provider works unchanged.
"""

import json
from typing import Any, TypeVar
from uuid import uuid4

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pydantic import BaseModel

from app.shared.contracts.llm import Message

SchemaT = TypeVar("SchemaT", bound=BaseModel)

_APP_NAME = "dynodoc"
_USER_ID = "system"


def _instruction(messages: list[Message], schema: type[BaseModel]) -> str:
    system = "\n\n".join(m.content for m in messages if m.role == "system")
    json_schema = json.dumps(schema.model_json_schema())
    return (
        f"{system}\n\n"
        "Respond with ONLY a single JSON object that conforms to this JSON Schema. "
        "Do not include markdown code fences, comments, or any text outside the JSON.\n"
        f"JSON Schema:\n{json_schema}"
    )


def _user_prompt(messages: list[Message]) -> str:
    lines = [
        f"{'User' if m.role == 'user' else 'Assistant'}: {m.content}"
        for m in messages
        if m.role != "system"
    ]
    return "\n".join(lines) or "(no input yet)"


def _extract_json(text: str) -> str:
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        return text[start : end + 1]
    return text


class AdkTextGenerator:
    def __init__(self, model: Any) -> None:
        self._model = model  # a google.adk.models.lite_llm.LiteLlm instance

    async def generate_structured(
        self, messages: list[Message], *, schema: type[SchemaT]
    ) -> SchemaT:
        agent = Agent(
            name="dynodoc_generator",
            model=self._model,
            instruction=_instruction(messages, schema),
        )
        session_service = InMemorySessionService()  # type: ignore[no-untyped-call]
        session_id = uuid4().hex
        await session_service.create_session(
            app_name=_APP_NAME, user_id=_USER_ID, session_id=session_id
        )
        runner = Runner(agent=agent, app_name=_APP_NAME, session_service=session_service)
        content = types.Content(role="user", parts=[types.Part(text=_user_prompt(messages))])

        final_text = ""
        async for event in runner.run_async(
            user_id=_USER_ID, session_id=session_id, new_message=content
        ):
            if event.is_final_response() and event.content and event.content.parts:
                part_text = event.content.parts[0].text
                if part_text:
                    final_text = part_text

        return schema.model_validate_json(_extract_json(final_text))
