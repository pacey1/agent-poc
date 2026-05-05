from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.agent import ConfluenceAgent
from app.config import settings
from app.integrations.llm_adapter import LLMAdapter
from app.integrations.mcp_client import MCPClient
from app.integrations.tool_agents import ConfluenceToolAgent, GitHubToolAgent, JiraToolAgent
from app.schemas import ChatRequest, ChatResponse

app = FastAPI(title="Confluence Agent API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def resolve_llm() -> LLMAdapter | None:
    provider = settings.llm_provider.lower().strip()
    if provider == "openai":
        api_key = settings.llm_api_key or settings.openai_api_key
        if api_key:
            return LLMAdapter("openai", api_key, settings.openai_model, settings.openai_base_url)
        return None

    api_key = settings.llm_api_key or settings.grok_api_key
    if api_key:
        return LLMAdapter("grok", api_key, settings.grok_model, settings.grok_base_url)
    return None


confluence_mcp = MCPClient(settings.confluence_mcp_server_url, settings.mcp_auth_token) if settings.confluence_mcp_server_url and not settings.mock_mode else None
jira_mcp = MCPClient(settings.jira_mcp_server_url, settings.mcp_auth_token) if settings.jira_mcp_server_url and not settings.mock_mode else None
github_mcp = MCPClient(settings.github_mcp_server_url, settings.mcp_auth_token) if settings.github_mcp_server_url and not settings.mock_mode else None

confluence_tools = ConfluenceToolAgent(mcp_client=confluence_mcp, mock_mode=settings.mock_mode)
jira_tools = JiraToolAgent(mcp_client=jira_mcp, mock_mode=settings.mock_mode)
github_tools = GitHubToolAgent(mcp_client=github_mcp, mock_mode=settings.mock_mode)

agent = ConfluenceAgent(llm_adapter=resolve_llm(), tools=confluence_tools)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/mcp/test")
async def test_mcp_connections() -> dict:
    return {
        "confluence": await confluence_tools.test_connection(),
        "jira": await jira_tools.test_connection(),
        "github": await github_tools.test_connection(),
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    action, result, reply = await agent.run(request.message)
    return ChatResponse(reply=reply, action=action, result=result)


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
