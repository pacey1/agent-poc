from typing import Any

from app.integrations.mcp_client import MCPClient


class BaseToolAgent:
    namespace: str

    def __init__(self, mcp_client: MCPClient | None, mock_mode: bool = True) -> None:
        self.mcp_client = mcp_client
        self.mock_mode = mock_mode

    async def test_connection(self) -> dict[str, Any]:
        if self.mock_mode or self.mcp_client is None:
            return {"tool": self.namespace, "connected": True, "mode": "mock"}
        return await self.mcp_client.call_tool(f"{self.namespace}.test_connection", {})


class ConfluenceToolAgent(BaseToolAgent):
    namespace = "confluence"

    async def list_spaces(self, limit: int = 50) -> dict[str, Any]:
        if self.mock_mode or self.mcp_client is None:
            spaces = [
                {"key": "ENG", "name": "Engineering"},
                {"key": "OPS", "name": "Operations"},
                {"key": "HR", "name": "Human Resources"},
            ]
            return {"spaces": spaces[:limit], "total": len(spaces)}
        return await self.mcp_client.call_tool("confluence.list_spaces", {"limit": limit})

    async def create_page(self, space_key: str, title: str, body_markdown: str, parent_page_id: str | None = None) -> dict[str, Any]:
        if self.mock_mode or self.mcp_client is None:
            return {
                "page_id": "mock-page-001",
                "space_key": space_key,
                "title": title,
                "url": f"https://confluence.example.local/wiki/spaces/{space_key}/pages/mock-page-001",
                "body_preview": body_markdown[:120],
                "parent_page_id": parent_page_id,
            }
        return await self.mcp_client.call_tool(
            "confluence.create_page",
            {
                "space_key": space_key,
                "title": title,
                "body_markdown": body_markdown,
                "parent_page_id": parent_page_id,
            },
        )


class JiraToolAgent(BaseToolAgent):
    namespace = "jira"


class GitHubToolAgent(BaseToolAgent):
    namespace = "github"
