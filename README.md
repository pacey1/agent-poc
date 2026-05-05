# Confluence Agent (Chat + LLM + MCP)

사용자 자연어 요청으로 Confluence 작업을 수행하는 MVP 예제입니다.

## 변경 요약
- LLM provider를 **Grok / OpenAI** 중 선택 가능
- MCP 서버를 **Confluence / Jira / GitHub** 별도 연결
- MCP 실제 연결 확인용 API 추가: `GET /api/mcp/test`
- Tool 별 에이전트(`ConfluenceToolAgent`, `JiraToolAgent`, `GitHubToolAgent`) 분리
- 오케스트레이션을 **LangGraph** 기반으로 변경


## 빠른 시작 (.env 세팅 포함)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
# .env 파일에서 최소 아래 값만 먼저 채우세요
# - LLM_PROVIDER (grok 또는 openai)
# - GROK_API_KEY 또는 OPENAI_API_KEY
# - 실제 연동 시 MOCK_MODE=false + MCP URL들
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```


## 환경변수
- 공통 LLM
  - `LLM_PROVIDER=grok|openai`
  - `LLM_API_KEY`, `LLM_MODEL`, `LLM_BASE_URL`
- 호환용
  - `GROK_API_KEY`, `GROK_MODEL`, `GROK_BASE_URL`
  - `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_BASE_URL`
- MCP
  - `CONFLUENCE_MCP_SERVER_URL`
  - `JIRA_MCP_SERVER_URL`
  - `GITHUB_MCP_SERVER_URL`
  - `MCP_AUTH_TOKEN`
- 기타
  - `MOCK_MODE=true|false`

## MCP 연결 테스트
```bash
curl http://localhost:8000/api/mcp/test
```

`MOCK_MODE=false`일 때 각 서버의 `*.test_connection` MCP tool을 호출합니다.

## 주요 파일
- `app/main.py`: API + 의존성 조립 + MCP connection test API
- `app/agent.py`: LangGraph 기반 액션 결정/실행
- `app/integrations/llm_adapter.py`: OpenAI 호환 chat completion 호출
- `app/integrations/tool_agents.py`: 도구별 에이전트 분리
- `app/integrations/mcp_client.py`: MCP tool 호출
