from domain.ports.input_guardrail import InputGuardrailPort
from domain.ports.prompt_builder import PromptBuilderPort
from typing import Optional
from domain.models.chat import ChatSession, Role
from domain.ports.chat_service import ChatServicePort
from domain.ports.repository import ChatRepositoryPort
from application.dto.chat_dto import ChatInputDTO, ChatOutputDTO

class ChatUseCase:
    def __init__(self, chat_service: ChatServicePort, chat_repository: ChatRepositoryPort, prompt_builder: PromptBuilderPort, input_guardrail: InputGuardrailPort):
        self._chat_service = chat_service
        self._chat_repository = chat_repository
        self._prompt_builder = prompt_builder
        self._input_guardrail = input_guardrail

    async def execute_async(self, input_dto: ChatInputDTO, user_id: str) -> ChatOutputDTO:
        """
        Asynchronously orchestrate the chat flow.
        """
        # 1. Validate the input message
        self._input_guardrail.validate(input_dto)
        # 2. Fetch or create chat session
        session: Optional[ChatSession] = None
        if input_dto.session_id:
            session = await self._chat_repository.get_by_id_async(input_dto.session_id)
            
        if not session:
            session = ChatSession(user_id=user_id)

        if user_id != session.user_id:
            raise ValueError("User ID does not match session user ID")

        # 3. Add user message
        session.add_message(role=Role.USER, content=input_dto.message)

        # 4. Call Prompt Builder Port to generate a prompt
        prompt = await self._prompt_builder.build_prompt_async(user_id, session)
        
        # 5. Call Chat Service Port to generate helper response
        response_messages = await self._chat_service.generate_response_async(prompt)

        # 6. Add assistant response messages to session
        for msg in response_messages:
            session.messages.append(msg)

        # 7. Save the updated chat history
        await self._chat_repository.save_async(session)

        # 8. Return response DTO
        final_response_content = response_messages[-1].content if response_messages else ""
        return ChatOutputDTO(
            session_id=session.session_id,
            response=final_response_content
        )
