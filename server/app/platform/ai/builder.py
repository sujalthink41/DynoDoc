"""Builder for a provider-agnostic TextGenerator (ADK + LiteLLM).

Selection (provider, model, api key) is the client's choice — swapping to
OpenAI/Anthropic/etc. later is config, not code:

    generator = (
        LlmTextGeneratorBuilder()
        .provider("gemini")
        .model("gemini-2.0-flash")
        .api_key(settings.llm_api_key)
        .build()
    )
"""

from typing import Self

from google.adk.models.lite_llm import LiteLlm

from app.platform.ai.text_generator import AdkTextGenerator
from app.shared.contracts.llm import TextGenerator
from app.shared.errors import DependencyUnavailableError


class LlmTextGeneratorBuilder:
    def __init__(self) -> None:
        self._provider = "gemini"
        self._model = "gemini-2.0-flash"
        self._api_key: str | None = None

    def provider(self, provider: str) -> Self:
        self._provider = provider
        return self

    def model(self, model: str) -> Self:
        self._model = model
        return self

    def api_key(self, api_key: str | None) -> Self:
        self._api_key = api_key
        return self

    def build(self) -> TextGenerator:
        if not self._api_key:
            raise DependencyUnavailableError(
                "LLM API key is not configured", code="llm_unavailable"
            )
        # LiteLLM model naming: "<provider>/<model>" (e.g. gemini/gemini-2.0-flash,
        # openai/gpt-4o, anthropic/claude-3-5-sonnet).
        model_name = f"{self._provider}/{self._model}"
        return AdkTextGenerator(model=LiteLlm(model=model_name, api_key=self._api_key))
