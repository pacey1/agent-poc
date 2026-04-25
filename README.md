# Confluence Agent (Chat + Grok + MCP)

사용자 자연어 요청으로 Confluence 작업을 수행하는 MVP 예제입니다.

## UI Framework
- 현재 구현: **FastAPI Static Chat UI (Vanilla JS)**
- 운영 확장 권장: **Next.js(React)** 로 분리하여 배포

## 기능
- 공간 목록 조회 (`list_spaces`)
- 페이지 생성 (`create_page`)
- Grok 연동(옵션) + MCP 서버 연동(옵션)
- 외부 연동 정보가 없으면 `MOCK_MODE=true`로 동작

## 실행
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

브라우저: `http://localhost:8000`

## 환경변수
- `GROK_API_KEY`, `GROK_MODEL`, `GROK_BASE_URL`
- `MCP_SERVER_URL`, `MCP_AUTH_TOKEN`
- `MOCK_MODE=true|false`

## 주요 파일
- `app/main.py`: API + 정적 UI 서빙
- `app/agent.py`: 액션 결정/실행 오케스트레이션
- `app/integrations/grok_adapter.py`: Grok 호출
- `app/integrations/mcp_client.py`: MCP tool 호출
- `app/integrations/confluence_tools.py`: Confluence tool 래퍼
- `frontend/index.html`: Chat UI
