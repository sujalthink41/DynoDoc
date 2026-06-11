"""Builder for a provider-agnostic LLM (ADK + LiteLLM).

Selection (provider, model, api key) is the client's choice — swapping to
OpenAI/Anthropic/etc. later is config, not code. `build_model()` yields the raw
LiteLlm (used by ADK agents in the generation pipeline); `build()` wraps it as a
TextGenerator (used by the single-call intake flow).

    builder = LlmModelBuilder().provider("openai").model("gpt-4.1-mini").api_key(key)
    model = builder.build_model()      # for ADK agents
    generator = builder.build()        # for intake's TextGenerator port
"""

from typing import Self

from google.adk.models.lite_llm import LiteLlm

from app.platform.ai.text_generator import AdkTextGenerator
from app.shared.contracts.llm import TextGenerator
from app.shared.errors import DependencyUnavailableError


class LlmModelBuilder:
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

    def build_model(self) -> LiteLlm:
        if not self._api_key:
            raise DependencyUnavailableError(
                "LLM API key is not configured", code="llm_unavailable"
            )
        # LiteLLM model naming: "<provider>/<model>" (e.g. gemini/gemini-2.0-flash,
        # openai/gpt-4.1-mini, anthropic/claude-3-5-sonnet).
        model_name = f"{self._provider}/{self._model}"
        return LiteLlm(model=model_name, api_key=self._api_key)

    def build(self) -> TextGenerator:
        return AdkTextGenerator(model=self.build_model())
