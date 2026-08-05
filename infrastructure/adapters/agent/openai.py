import os
import openai
from domain.models.chat import Message, Role
from domain.ports.chat_service import ChatServicePort

from domain.models.prompt import Prompt
from domain.ports.chat_service import ChatServicePort

class OpenAIAdapter(ChatServicePort):
    def __init__(self, api_key: str = None, model_name: str = "gpt-4o-mini"):
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.api_key = api_key
        if not api_key:
            self.client = None
            self.aclient = None
        else:
            self.client = openai.OpenAI(api_key=api_key)
            self.aclient = openai.AsyncOpenAI(api_key=api_key)
        self.model_name = model_name

    def _ensure_clients(self):
        if not self.client:
            raise ValueError(
                "OpenAI Client is not initialized. Please set the OPENAI_API_KEY environment variable."
            )

    def _map_to_openai_messages(self, prompt: Prompt) -> list[dict]:
        """Maps domain Prompt structure to OpenAI message dictionaries."""
        openai_messages = []
        system_content = f"{prompt.system}\n\n {prompt.policies} \n\n {prompt.personality}\n\n {prompt.user_data}\n\n {prompt.rag_context}"
        openai_messages.append({
            "role": "system",
            "content": system_content
        })
        for msg in prompt.history:
            openai_messages.append({
                "role": msg.role.value,  # 'user', 'assistant', 'system'
                "content": msg.content
            })
        openai_messages.append({
            "role": prompt.current_message.role.value,
            "content": prompt.current_message.content
        })
        return openai_messages

    def generate_response(self, prompt: Prompt) -> list[Message]:
        self._ensure_clients()
        messages = self._map_to_openai_messages(prompt)
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages
        )
        
        if not response.choices or not response.choices[0].message:
            raise ValueError("Empty response received from OpenAI API.")
            
        return [Message(role=Role.ASSISTANT, content=response.choices[0].message.content)]

    async def generate_response_async(self, prompt: Prompt) -> list[Message]:
        self._ensure_clients()
        messages = self._map_to_openai_messages(prompt)
        
        response = await self.aclient.chat.completions.create(
            model=self.model_name,
            messages=messages
        )
        
        if not response.choices or not response.choices[0].message:
            raise ValueError("Empty response received from OpenAI API.")
            
        return [Message(role=Role.ASSISTANT, content=response.choices[0].message.content)]
