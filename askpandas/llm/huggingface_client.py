"""Hugging Face Inference Providers client.

The legacy ``api-inference.huggingface.co`` endpoint used by askpandas <= 0.1.1 no
longer resolves; Hugging Face now serves hosted models through the OpenAI-compatible
router at ``https://router.huggingface.co/v1``.
"""

from __future__ import annotations

from typing import Any

from .openai_compatible import OpenAICompatibleLLM

HF_ROUTER_URL = "https://router.huggingface.co/v1"


class HuggingFaceLLM(OpenAICompatibleLLM):
    """LLM client for Hugging Face Inference Providers (online).

    Args:
        model_name: A chat model served by the router, e.g.
            ``"Qwen/Qwen2.5-Coder-7B-Instruct"`` or ``"meta-llama/Llama-3.1-8B-Instruct"``.
        api_key: Hugging Face token. Defaults to the ``HF_TOKEN`` or ``HF_API_KEY``
            environment variable.
        **kwargs: Passed to :class:`OpenAICompatibleLLM` (``temperature``, ``max_tokens``...).

    Raises:
        ValueError: If no token is provided or found in the environment.
    """

    def __init__(
        self,
        model_name: str = "Qwen/Qwen2.5-Coder-7B-Instruct",
        api_key: str | None = None,
        **kwargs: Any,
    ) -> None:
        kwargs.setdefault("base_url", HF_ROUTER_URL)
        kwargs.setdefault("api_key_env", ("HF_TOKEN", "HF_API_KEY"))
        super().__init__(model_name, api_key=api_key, **kwargs)
        if not self.api_key:
            raise ValueError(
                "A Hugging Face token is required. Pass api_key=... or set HF_TOKEN "
                "(create one at https://huggingface.co/settings/tokens)."
            )
        # Kept for backward compatibility with askpandas <= 0.1.1
        self.api_url = f"{self.base_url}/chat/completions"
