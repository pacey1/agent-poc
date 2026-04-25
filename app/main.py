from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.agent import ConfluenceAgent
from app.config import settings
from app.integrations.confluence_tools import ConfluenceTools
from app.integrations.grok_adapter import GrokAdapter
from app.integrations.mcp_client import MCPClient
from app.schemas import ChatRequest, ChatResponse

app = FastAPI(title="Confluence Agent API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mcp_client = None
if settings.mcp_server_url and not settings.mock_mode:
    mcp_client = MCPClient(settings.mcp_server_url, settings.mcp_auth_token)

grok_adapter = None
if settings.grok_api_key:
    grok_adapter = GrokAdapter(settings.grok_api_key, settings.grok_model, settings.grok_base_url)

tools = ConfluenceTools(mcp_client=mcp_client, mock_mode=settings.mock_mode)
agent = ConfluenceAgent(grok_adapter=grok_adapter, tools=tools)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    action = await agent.decide_action(request.message)
    result, reply = await agent.execute(action)
    return ChatResponse(reply=reply, action=action, result=result)


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
