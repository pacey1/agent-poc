import re
from typing import Any

from app.schemas import Action


class ConfluenceAgent:
    def __init__(self, grok_adapter, tools) -> None:
        self.grok_adapter = grok_adapter
        self.tools = tools

    async def decide_action(self, message: str) -> Action:
        if self.grok_adapter is not None:
            try:
                raw = await self.grok_adapter.generate_action(message)
                return Action.model_validate(raw)
            except Exception:
                pass
        return self._rule_based_action(message)

    def _rule_based_action(self, message: str) -> Action:
        msg = message.strip().lower()

        if "공간" in msg and ("목록" in msg or "list" in msg):
            return Action(action="list_spaces", args={"limit": 50})

        # Example: "A 공간에 B 페이지 생성해줘"
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

        return Action(
            action="clarify",
            args={
                "question": "원하는 작업을 알려주세요: (1) 공간 목록 조회, (2) 페이지 생성",
            },
        )

    async def execute(self, action: Action) -> tuple[dict[str, Any], str]:
        if action.action == "list_spaces":
            result = await self.tools.list_spaces(limit=int(action.args.get("limit", 50)))
            keys = ", ".join(s["key"] for s in result.get("spaces", []))
            return result, f"조회 가능한 공간은 {result.get('total', 0)}개입니다: {keys}"

        if action.action == "create_page":
            space_key = action.args.get("space_key")
            title = action.args.get("title")
            if not space_key or not title:
                return {}, "space_key와 title이 필요합니다. 예: A 공간에 B 페이지 생성해줘"

            result = await self.tools.create_page(
                space_key=space_key,
                title=title,
                body_markdown=action.args.get("body_markdown", f"# {title}\n"),
                parent_page_id=action.args.get("parent_page_id"),
            )
            return result, f"페이지를 생성했습니다: {result.get('url', 'URL 없음')}"

        return {}, action.args.get("question", "요청을 이해하지 못했습니다.")
