import json
from typing import Any

import httpx


class GrokAdapter:
    def __init__(self, api_key: str, model: str, base_url: str) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    async def generate_action(self, user_message: str) -> dict[str, Any]:
        system_prompt = (
            "You are a Confluence automation planner. "
            "Return JSON only with shape: "
            "{\"action\":\"list_spaces|create_page|clarify\",\"args\":{...}}. "
            "Supported actions: list_spaces, create_page. "
            "If required params are missing, use clarify."
        )
        user_prompt = f"User message (Korean possible): {user_message}"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}

        async with httpx.AsyncClient(timeout=25.0) as client:
            response = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        return json.loads(content)
