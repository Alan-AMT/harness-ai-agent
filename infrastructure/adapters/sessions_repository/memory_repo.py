import copy
from typing import Optional, Dict
from datetime import datetime, timezone
from domain.models.chat import ChatSession, Message, Role
from domain.ports.repository import ChatRepositoryPort

class InMemoryChatRepository(ChatRepositoryPort):
    """
    An in-memory implementation of the ChatRepositoryPort.
    Perfect for development, testing, and blueprints.
    """

    def __init__(self):
        # Maps session_id -> ChatSession
        self._sessions: Dict[str, ChatSession] = {}
        self._init_preset_sessions()

    def _init_preset_sessions(self):
        # Pre-populate 3 sessions with conversation history
        session_1 = ChatSession(session_id="session-1", user_id="user123")
        session_1.add_message(Role.USER, "Hi, I need help with my Python code.")
        session_1.add_message(Role.ASSISTANT, "Sure! What issues are you experiencing?")
        self._sessions[session_1.session_id] = session_1

        session_2 = ChatSession(session_id="session-2", user_id="user123")
        session_2.add_message(Role.USER, "What is hexagonal architecture?")
        session_2.add_message(Role.ASSISTANT, "Hexagonal Architecture (or Ports & Adapters) is a pattern that separates core logic from external dependencies.")
        self._sessions[session_2.session_id] = session_2

        session_3 = ChatSession(session_id="session-3", user_id="user123")
        session_3.add_message(Role.USER, "Can you suggest a name for my new dog?")
        session_3.add_message(Role.ASSISTANT, "How about Antigravity?")
        self._sessions[session_3.session_id] = session_3

    def save(self, session: ChatSession) -> None:
        print(f"[InMemoryRepo] Saving session {session.session_id} with {len(session.messages)} messages.")
        # Store a deepcopy to prevent outside mutation of internal DB state
        self._sessions[session.session_id] = copy.deepcopy(session)

    def get_by_id(self, session_id: str) -> Optional[ChatSession]:
        print(f"[InMemoryRepo] Fetching session {session_id}.")
        session = self._sessions.get(session_id)
        if session:
            return copy.deepcopy(session)
        return None

    async def save_async(self, session: ChatSession) -> None:
        self.save(session)

    async def get_by_id_async(self, session_id: str) -> Optional[ChatSession]:
        session = self.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        return session
