from __future__ import annotations

import json
import os
from typing import Any

from services.gitagent_loader import load_agent_system_prompt


def run_agent(agent_name: str, user_prompt: str, expect_json: bool = True) -> dict[str, Any] | str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return {"skipped": True, "reason": "ANTHROPIC_API_KEY is not configured"}

    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    system_prompt = load_agent_system_prompt(agent_name)
    if expect_json:
        system_prompt += "\n\nRespond only with valid JSON."

    message = client.messages.create(
        model=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
        max_tokens=4000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    response_text = message.content[0].text
    if not expect_json:
        return response_text

    try:
        text = response_text.strip()
        if text.startswith("```"):
            text = text.strip("`")
            text = text[4:] if text.startswith("json") else text
        return json.loads(text.strip())
    except json.JSONDecodeError:
        return {"raw_response": response_text, "parse_error": True}
