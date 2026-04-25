from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User input")
    session_id: str | None = Field(default=None)


class Action(BaseModel):
    action: Literal["list_spaces", "create_page", "clarify"]
    args: dict[str, Any] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    reply: str
    action: Action
    result: dict[str, Any] = Field(default_factory=dict)
