from application.dto.chat_dto import ChatInputDTO
from domain.ports.input_guardrail import InputGuardrailPort

import uuid

class NaiveInputGuardrailAdapter(InputGuardrailPort):
    def validate(self, input_dto: ChatInputDTO) -> None:
        if not input_dto.message:
            raise ValueError("Message cannot be empty")
        if len(input_dto.message) > 1000:
            raise ValueError("Message is too long")
        if input_dto.session_id:
            if not input_dto.session_id.startswith("session-"):
                try:
                    uuid.UUID(input_dto.session_id)
                except ValueError:
                    raise ValueError("Session ID is not valid")
        if input_dto.file:
            if len(input_dto.file.filename) > 255:
                raise ValueError("File name is too long")
            # Check file extension
            allowed_extensions = ".pdf", ".png", ".txt", ".jpg", ".jpeg"
            if not input_dto.file.filename.endswith(allowed_extensions):
                raise ValueError(f"File must be one of {allowed_extensions}")
            # Check file size
            if input_dto.file.size > 1024 * 1024 * 50:
                raise ValueError("File is too large")
            # Check file content
            if not input_dto.file.content:
                raise ValueError("File content is empty")