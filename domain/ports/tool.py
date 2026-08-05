from typing import Any
from abc import ABC, abstractmethod

class AgentTool(ABC):
    name: str
    description: str
    args_schema: dict[str, Any]
    
    @abstractmethod
    async def run(self, *args, **kwargs) -> list[str]:
        """
        Run the tool
        
        Args:
            *args: Arguments for the tool
            **kwargs: Keyword arguments for the tool
            
        Returns:
            The result of the tool
        """
        pass
    