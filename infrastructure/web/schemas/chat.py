from typing import Optional
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(
        ..., 
        description="The message to send to the chatbot assistant.",
        examples=["Hello, tell me a joke about programming."]
    )
    session_id: Optional[str] = Field(
        None, 
        description="The unique identifier of the chat session. If not provided, a new session is created.",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )

class ChatResponse(BaseModel):
    session_id: str = Field(
        ..., 
        description="The ID of the chat session (existing or newly generated)."
    )
    response: str = Field(
        ..., 
        description="The generated response from the chatbot assistant."
    )
