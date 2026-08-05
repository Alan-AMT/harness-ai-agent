from fastapi import APIRouter, Depends, status, HTTPException, status
from application.dto.chat_dto import ChatInputDTO
from application.use_cases.chat_use_case import ChatUseCase
from infrastructure.web.schemas.chat import ChatRequest, ChatResponse
# We will import the DI helper from the app state or a dependencies module.
# Let's import it from dependencies helper which we'll define or expose.
from infrastructure.web.dependencies import get_chat_use_case

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a chat message",
    description="Processes a user message through the hexagonal use-cases, saving state and returning the response."
)
async def post_chat(
    request: ChatRequest,
    use_case: ChatUseCase = Depends(get_chat_use_case)
) -> ChatResponse:
    # 1. Convert Web schema to Application DTO
    input_dto = ChatInputDTO(
        message=request.message,
        session_id=request.session_id
    )
    
    # 1.1 Simulate getting user ID from request token
    user_id = "user123"
    
    # 2. Execute the use case
    try:
        output_dto = await use_case.execute_async(input_dto, user_id)
    except Exception as e:
        if type(e) == ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
    # 3. Convert Application DTO back to Web Response schema
    return ChatResponse(
        session_id=output_dto.session_id,
        response=output_dto.response
    )
