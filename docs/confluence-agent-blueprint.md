# 사용자 자연어 기반 Confluence Agent 설계안

## 1) 목표
사용자의 자연어 요청을 받아, **Confluence MCP 서버**를 통해 안전하게 Confluence 작업을 수행하는 에이전트를 구축합니다.

요구 시나리오:
1. "내 권한으로 조회 가능한 공간 목록 보여줘"
2. "A 공간에 B 페이지 생성해줘"

구성:
- UI: Chat 입력
- LLM: Grok(무료 모델)
- Agent: Confluence Agent
- Tool Layer: Confluence MCP Server

---

## 2) 권장 아키텍처

```text
[Web Chat UI]
    -> [Backend API]
        -> [Confluence Agent Orchestrator]
            -> [LLM Adapter (Grok)]
            -> [MCP Client]
                -> [Confluence MCP Server]
                    -> [Confluence Cloud]
```

### 컴포넌트 역할
- **Web Chat UI**: 사용자 메시지 입력/결과 표시
- **Backend API**: 세션, 인증, 로그, 레이트리밋 관리
- **Confluence Agent Orchestrator**:
  - 의도 분류(intent)
  - 파라미터 추출(예: space key, page title, body)
  - MCP 툴 호출 실행 및 결과 후처리
- **LLM Adapter (Grok)**:
  - 자연어를 실행 가능한 JSON 액션으로 변환
  - 액션 실행 결과를 사용자 친화형 답변으로 변환
- **MCP Client**:
  - MCP 서버의 tools/list, tools/call 인터페이스 사용
- **Confluence MCP Server**:
  - Confluence API와 직접 통신

---

## 3) 최소 기능(MVP)

### A. 공간 목록 조회
사용자 입력 예:
- "내가 볼 수 있는 공간 목록 보여줘"

실행 로직:
1. intent = `list_spaces`
2. MCP tool 호출: `confluence.list_spaces` (예시)
3. 결과를 표/목록 형태로 반환

응답 예:
- "조회 가능한 공간 12개입니다. 상위 10개: ENG, OPS, HR ..."

### B. 페이지 생성
사용자 입력 예:
- "A 공간에 B 페이지 생성해줘"

실행 로직:
1. intent = `create_page`
2. 파라미터 추출:
   - `space_key`: A
   - `title`: B
   - `body`: (없으면 템플릿 본문)
3. MCP tool 호출: `confluence.create_page`
4. 생성 결과(URL, page id) 반환

응답 예:
- "A 공간에 'B' 페이지를 생성했습니다. 링크: ..."

---

## 4) 에이전트 액션 스키마(JSON)

LLM이 반드시 아래 JSON 중 하나로만 응답하도록 강제하면 안정성이 높아집니다.

```json
{
  "action": "list_spaces",
  "args": {
    "limit": 50
  }
}
```

```json
{
  "action": "create_page",
  "args": {
    "space_key": "A",
    "title": "B",
    "body_markdown": "# B\n초안입니다.",
    "parent_page_id": null
  }
}
```

검증 규칙:
- `action`은 허용 목록에 있어야 함
- `create_page`는 `space_key`, `title` 필수
- 제목 길이, 본문 길이 상한 체크

---

## 5) Grok 연계 전략

Grok을 API로 호출하는 어댑터 계층을 분리하세요.

### 인터페이스 권장
- `generate_action(user_message, conversation_context) -> ActionJSON`
- `generate_response(user_message, action_result) -> NaturalLanguage`

### 프롬프트 핵심 규칙
- 한국어 요청 우선 처리
- 허용 액션 외 금지
- 모호하면 1회 명확화 질문
- JSON만 출력(액션 추출 단계)

시스템 프롬프트 예시(요약):
- "너는 Confluence 업무 자동화 에이전트다. 허용 액션은 list_spaces/create_page뿐이며, 반드시 JSON으로만 답해라."

---

## 6) MCP 연계 패턴

MCP 서버가 제공하는 tool 이름/스키마는 구현마다 다르므로, 시작 시 동적 탐색을 권장합니다.

1. `tools/list` 호출
2. 실제 사용 가능한 툴 확인
3. 내부 action ↔ MCP tool 매핑 구성

예시 매핑:
- `list_spaces` -> `confluence.list_spaces`
- `create_page` -> `confluence.create_page`

실행 단계:
1. 액션 JSON 생성
2. 스키마 검증
3. MCP tool 호출
4. 결과 정규화(normalize)
5. 사용자 응답 생성

---

## 7) 실패/예외 처리

- 권한 없음(403):
  - "해당 공간에 페이지 생성 권한이 없습니다."
- 공간 미존재(404):
  - "공간 키 A를 찾을 수 없습니다."
- 제목 중복/정책 위반:
  - 대체 제목 제안 (`B (2026-04-25)`)
- 네트워크/타임아웃:
  - 재시도(최대 2회, 지수 백오프)

---

## 8) 보안/운영 체크리스트

- Confluence 토큰은 서버 보관(클라이언트 노출 금지)
- 사용자별 권한 위임(impersonation 또는 OAuth)
- 감사 로그:
  - 누가, 어떤 space/page에, 어떤 작업 수행했는지
- 민감정보 마스킹
- 요청/응답 추적 ID 부여

---

## 9) 빠른 구현 순서(2주 MVP)

### 1주차
- Backend + Chat API 뼈대
- Grok Adapter 구현
- MCP client 연결
- `list_spaces` 완성

### 2주차
- `create_page` 완성
- 검증/에러처리/로그 강화
- 사용자 승인(confirm) 단계 추가
  - "A 공간에 B 페이지를 생성할까요?"

---

## 10) 승인(Confirm) UX 권장

페이지 생성은 쓰기 작업이므로 확인 단계를 두는 것을 권장합니다.

1. 사용자: "A 공간에 B 페이지 생성해줘"
2. Agent: "다음 내용으로 생성할까요? [space=A, title=B]"
3. 사용자: "응"
4. Agent: MCP 호출 후 결과 링크 반환

---

## 11) API/코드 구조 예시

```text
/agent
  /api
    chat.py
  /core
    orchestrator.py
    schema.py
    validators.py
  /integrations
    grok_adapter.py
    mcp_client.py
    confluence_tools.py
```

핵심 함수:
- `handle_chat(session_id, message)`
- `decide_action(message, context)`
- `execute_action(action_json)`
- `format_user_reply(result)`

---

## 12) 샘플 대화

### 공간 조회
- 사용자: "내 권한으로 조회 가능한 공간 목록 보여줘"
- 에이전트 내부 액션:
  - `{"action":"list_spaces","args":{"limit":50}}`
- 응답:
  - "조회 가능한 공간은 12개입니다: ENG, OPS, HR ..."

### 페이지 생성
- 사용자: "A 공간에 B 페이지 생성해줘"
- 에이전트 확인:
  - "A 공간에 제목 'B'로 생성할까요?"
- 사용자: "생성"
- 내부 액션:
  - `{"action":"create_page","args":{"space_key":"A","title":"B","body_markdown":"# B\n"}}`
- 응답:
  - "생성 완료: https://..."

---

## 13) 다음 단계 제안

원하시면 다음 턴에서 바로 아래 3가지를 만들어 드릴 수 있습니다.
1. **FastAPI 기반 최소 실행 코드**(chat endpoint + action router)
2. **Grok Adapter 실제 코드 템플릿**(환경변수 기반)
3. **MCP tool 호출 래퍼 코드**(list/create 구현)

