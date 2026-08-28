"""Thin Claude client wrapper. Every agent goes through `complete_json` so responses
are typed and validated against a Pydantic schema before leaving this layer."""

from __future__ import annotations

import json
from typing import TypeVar

from anthropic import AsyncAnthropic
from pydantic import BaseModel, ValidationError
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import settings

T = TypeVar("T", bound=BaseModel)

_client: AsyncAnthropic | None = None


def client() -> AsyncAnthropic:
    global _client
    if _client is None:
        _client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    return _client


@retry(wait=wait_exponential(min=1, max=16), stop=stop_after_attempt(4))
async def complete_json(
    *,
    system: str,
    user: str,
    schema: type[T],
    max_tokens: int = 4096,
) -> T:
    """Call Claude and parse the response as JSON matching `schema`.

    The system prompt must instruct the model to return a single JSON object with
    no prose. Parsing/validation failures raise and are retried by tenacity.
    """
    resp = await client().messages.create(
        model=settings.anthropic_model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    text = "".join(block.text for block in resp.content if getattr(block, "type", "") == "text")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Claude did not return JSON: {text[:400]}") from e
    try:
        return schema.model_validate(data)
    except ValidationError:
        raise
