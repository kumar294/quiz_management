from __future__ import annotations

import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from app.core.claude import complete_json

PROMPTS = Path(__file__).resolve().parent.parent / "prompts"

T = TypeVar("T", bound=BaseModel)


def load_prompt(name: str) -> str:
    return (PROMPTS / f"{name}.md").read_text(encoding="utf-8")


async def run_agent(
    *,
    prompt_name: str,
    payload: dict | BaseModel,
    schema: type[T],
    max_tokens: int = 4096,
) -> T:
    system = load_prompt(prompt_name)
    if isinstance(payload, BaseModel):
        payload = payload.model_dump(mode="json")
    user = "INPUT:\n" + json.dumps(payload, indent=2, default=str)
    return await complete_json(system=system, user=user, schema=schema, max_tokens=max_tokens)
