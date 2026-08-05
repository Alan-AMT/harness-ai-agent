from abc import ABC, abstractmethod
from typing import Any
from domain.models.chat import ChatSession
from domain.models.prompt import Prompt

class PromptBuilderPort(ABC):
    
    @abstractmethod
    async def build_prompt_async(self, user_id: str, session: ChatSession) -> Prompt:
        """
        Build the final prompt object that will be passed to the LLM
        
        Args:
            user_id: The ID of the user
            session: The session of the conversation
            
        Returns:
            The final prompt object
        """
        pass

    @abstractmethod
    async def build_user_data(self, user_id: str) -> dict[str, Any]:
        """
        Build the user data object that will be passed to the LLM
        
        Args:
            user_id: The ID of the user
            
        Returns:
            The user data object
        """
        pass
    
    @abstractmethod
    async def build_rag_context(self, query: str) -> dict[str, Any]:
        """
        Build the RAG context object that will be passed to the LLM
        
        Args:
            query: The query to retrieve context for
            
        Returns:
            The RAG context object
        """
        pass