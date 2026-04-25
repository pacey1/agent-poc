from typing import Any

import httpx


class MCPClient:
    def __init__(self, server_url: str, auth_token: str | None = None) -> None:
        self.server_url = server_url.rstrip("/")
        self.auth_token = auth_token

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        payload = {"tool": name, "arguments": arguments}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{self.server_url}/tools/call", json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
