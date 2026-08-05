from abc import ABC, abstractmethod
from domain.models.prompt import Prompt
from domain.models.chat import Message

class ChatServicePort(ABC):
    @abstractmethod
    async def generate_response_async(self, prompt: Prompt) -> list[Message]:
        """
        Asynchronously generate a response based on the prompt.
        
        Args:
            prompt: The Prompt domain model containing system prompt, history, and tools.
            
        Returns:
            A list of domain Message objects representing the assistant responses and intermediate tool messages.
        """
        pass
