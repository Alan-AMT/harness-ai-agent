from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
import uuid

class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

@dataclass
class TextPart:
    text: str

@dataclass
class ToolCallPart:
    name: str
    args: dict

@dataclass
class ToolResultPart:
    name: str
    result: Any

ChatPart = TextPart | ToolCallPart | ToolResultPart

@dataclass
class Message:
    role: Role
    parts: list[ChatPart] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __init__(self, role: Role, parts: list[ChatPart] = None, content: str = None, timestamp: datetime = None):
        self.role = role
        if parts is not None:
            self.parts = parts
        elif content is not None:
            self.parts = [TextPart(text=content)]
        else:
            self.parts = []
        self.timestamp = timestamp or datetime.now(timezone.utc)

    @property
    def content(self) -> str:
        return "".join(part.text for part in self.parts if isinstance(part, TextPart))

@dataclass
class ChatSession:
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    messages: list[Message] = field(default_factory=list)

    def add_message(self, role: Role, content: str = None, parts: list[ChatPart] = None) -> Message:
        message = Message(role=role, content=content, parts=parts)
        self.messages.append(message)
        return message
