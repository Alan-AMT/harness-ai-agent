import asyncio
from domain.models.chat import Message, Role
from domain.models.prompt import Prompt
from domain.ports.chat_service import ChatServicePort

class DummyLLMAdapter(ChatServicePort):
    """
    A mock LLM adapter that implements the ChatServicePort.
    Useful for local development and testing without making actual third-party API calls.
    """
    
    def generate_response(self, prompt: Prompt) -> list[Message]:
        # Get the content of the current user message
        last_user_message = prompt.current_message.content
        
        # Log for development purposes
        print(f"[DummyLLM] Generating response for prompt.")
        
        content = f"This is a mocked response to your message: '{last_user_message}'. Hexagonal architecture is working successfully!"
        return [Message(role=Role.ASSISTANT, content=content)]

    async def generate_response_async(self, prompt: Prompt) -> list[Message]:
        # Simulate network latency (e.g., 500ms)
        await asyncio.sleep(0.5)
        
        return self.generate_response(prompt)
