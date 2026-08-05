from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class ChatInputDTO:
    message: str
    session_id: Optional[str] = None
    file: Optional[bytes] = None
    file_name: Optional[str] = None

@dataclass(frozen=True)
class ChatOutputDTO:
    session_id: str
    response: str
