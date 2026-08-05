from abc import ABC, abstractmethod
from typing import Optional
from domain.models.chat import ChatSession

class ChatRepositoryPort(ABC):

    @abstractmethod
    def save(self, session: ChatSession) -> None:
        """
        Save or update a chat session.
        
        Args:
            session: The ChatSession entity to save.
        """
        pass

    @abstractmethod
    def get_by_id(self, session_id: str) -> Optional[ChatSession]:
        """
        Retrieve a chat session by its unique ID.
        
        Args:
            session_id: The session ID to find.
            
        Returns:
            The ChatSession entity if found, otherwise None.
        """
        pass

    @abstractmethod
    async def save_async(self, session: ChatSession) -> None:
        """
        Asynchronously save or update a chat session.
        
        Args:
            session: The ChatSession entity to save.
        """
        pass

    @abstractmethod
    async def get_by_id_async(self, session_id: str) -> Optional[ChatSession]:
        """
        Asynchronously retrieve a chat session by its unique ID.
        
        Args:
            session_id: The session ID to find.
            
        Returns:
            The ChatSession entity if found, otherwise None.
        """
        pass
