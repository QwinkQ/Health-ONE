from __future__ import annotations

from typing import Any

from app.core.config import settings


class DeepSeekClient:
    """Small wrapper around DeepSeek's OpenAI-compatible API.

    The MVP can run without an API key. When a key is configured, this client can
    be used by AgentService to polish responses or perform function calling.
    """

    def __init__(self) -> None:
        self.enabled = bool(settings.deepseek_api_key)

    def chat(self, messages: list[dict[str, str]], tools: list[dict[str, Any]] | None = None) -> str | None:
        if not self.enabled:
            return None

        from openai import OpenAI

        client = OpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )
        response = client.chat.completions.create(
            model=settings.deepseek_model,
            messages=messages,
            tools=tools,
            stream=False,
        )
        return response.choices[0].message.content

