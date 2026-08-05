from application.dto.chat_dto import ChatInputDTO
from abc import ABC, abstractmethod

class InputGuardrailPort(ABC):
    @abstractmethod
    def validate(self, input_dto: ChatInputDTO) -> None:
        """
        Validate the input message and file.
        
        Args:
            input_dto: The input object sent from the controller layer.
            
        Returns:
            void - raises an exception if the input is invalid.
        """
        pass