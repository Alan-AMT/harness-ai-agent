from domain.ports.tool import AgentTool
from typing import Any
from dataclasses import dataclass
@dataclass
class Prompt:
    """
    System prompt for the LLM
    """
    system: str
    """
    Policies to follow
    """
    policies: str
    """
    Personality of the assistant
    """
    personality: str
    """
    User related specific data
    """
    user_data: str
    """
    History of the conversation
    """
    history: list[str]
    """
    The tools the model has access too
    """
    tools: dict[str, AgentTool]
    """
    Retrieved context from RAG
    """
    rag_context: dict[str, Any]
    """
    Current message from the user
    """
    current_message: str