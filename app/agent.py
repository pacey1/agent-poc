import re
from typing import Any

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

from app.schemas import Action


class AgentState(BaseModel):
    message: str
    action: Action | None = None
    result: dict[str, Any] | None = None
    reply: str | None = None


class ConfluenceAgent:
    def __init__(self, llm_adapter, tools) -> None:
        self.llm_adapter = llm_adapter
        self.tools = tools
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(AgentState)
        graph.add_node("decide", self._decide_node)
        graph.add_node("execute", self._execute_node)
        graph.add_edge(START, "decide")
        graph.add_edge("decide", "execute")
        graph.add_edge("execute", END)
        return graph.compile()

    async def _decide_node(self, state: AgentState) -> AgentState:
        if self.llm_adapter is not None:
            try:
                raw = await self.llm_adapter.generate_action(
                    system_prompt=(
                        "You are a Confluence automation planner. Return JSON only with shape: "
                        '{"action":"list_spaces|create_page|clarify","args":{...}}.'
                    ),
                    user_message=f"User message (Korean possible): {state.message}",
                )
                state.action = Action.model_validate(raw)
                return state
            except Exception:
                pass
        state.action = self._rule_based_action(state.message)
        return state

    def _rule_based_action(self, message: str) -> Action:
        msg = message.strip().lower()
        if "공간" in msg and ("목록" in msg or "list" in msg):
            return Action(action="list_spaces", args={"limit": 50})

        pattern = r"(?P<space>[A-Za-z0-9_-]+)\s*공간에\s*(?P<title>.+?)\s*페이지\s*생성"
        matched = re.search(pattern, message)
        if matched:
            space_key = matched.group("space").strip()
            title = matched.group("title").strip(" ' \"")
            return Action(
                action="create_page",
                args={
                    "space_key": space_key,
                    "title": title,
                    "body_markdown": f"# {title}\n자동 생성된 초안입니다.",
                    "parent_page_id": None,
                },
            )

        return Action(action="clarify", args={"question": "원하는 작업을 알려주세요: (1) 공간 목록 조회, (2) 페이지 생성"})

    async def _execute_node(self, state: AgentState) -> AgentState:
        action = state.action
        if action is None:
            state.result, state.reply = {}, "요청을 이해하지 못했습니다."
            return state

        if action.action == "list_spaces":
            result = await self.tools.list_spaces(limit=int(action.args.get("limit", 50)))
            keys = ", ".join(s["key"] for s in result.get("spaces", []))
            state.result, state.reply = result, f"조회 가능한 공간은 {result.get('total', 0)}개입니다: {keys}"
            return state

        if action.action == "create_page":
            space_key = action.args.get("space_key")
            title = action.args.get("title")
            if not space_key or not title:
                state.result, state.reply = {}, "space_key와 title이 필요합니다. 예: A 공간에 B 페이지 생성해줘"
                return state
            result = await self.tools.create_page(
                space_key=space_key,
                title=title,
                body_markdown=action.args.get("body_markdown", f"# {title}\n"),
                parent_page_id=action.args.get("parent_page_id"),
            )
            state.result, state.reply = result, f"페이지를 생성했습니다: {result.get('url', 'URL 없음')}"
            return state

        state.result, state.reply = {}, action.args.get("question", "요청을 이해하지 못했습니다.")
        return state

    async def run(self, message: str) -> tuple[Action, dict[str, Any], str]:
        state = await self.graph.ainvoke(AgentState(message=message))
        return state.action or Action(action="clarify", args={}), state.result or {}, state.reply or ""
