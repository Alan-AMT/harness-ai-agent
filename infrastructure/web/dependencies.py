from infrastructure.adapters.prompt_builder.tripadvisor_prompt_builder import TripAdvisorPromptBuilderAdapter
from domain.ports.input_guardrail import InputGuardrailPort
from infrastructure.adapters.input_guardrail.naive_input_guardrail import NaiveInputGuardrailAdapter
from infrastructure.adapters.prompt_builder.hr_prompt_builder import HRPromptBuilderAdapter
from domain.ports.prompt_builder import PromptBuilderPort
import os
from fastapi import Depends
from application.use_cases.chat_use_case import ChatUseCase
from domain.ports.chat_service import ChatServicePort
from domain.ports.repository import ChatRepositoryPort
from infrastructure.adapters.agent.dummy_llm import DummyLLMAdapter
from infrastructure.adapters.sessions_repository.memory_repo import InMemoryChatRepository
from infrastructure.adapters.agent.google_genai import GoogleGenAIAdapter
from infrastructure.adapters.agent.openai import OpenAIAdapter
from dotenv import load_dotenv

# Create singletons for adapters (so they persist across requests in-memory)
_chat_repository = InMemoryChatRepository()

load_dotenv()
# Determine active LLM provider via environment variable
_provider = os.getenv("LLM_PROVIDER", "dummy").lower()

if _provider == "google":
    _chat_service = GoogleGenAIAdapter()
elif _provider == "openai":
    _chat_service = OpenAIAdapter()
else:
    _chat_service = DummyLLMAdapter()

def get_chat_repository() -> ChatRepositoryPort:
    return _chat_repository

def get_chat_service() -> ChatServicePort:
    return _chat_service

def get_prompt_builder() -> PromptBuilderPort:
    return TripAdvisorPromptBuilderAdapter()
    # return HRPromptBuilderAdapter()

def get_input_guardrail() -> InputGuardrailPort:
    return NaiveInputGuardrailAdapter()

def get_chat_use_case(
    repository: ChatRepositoryPort = Depends(get_chat_repository),
    service: ChatServicePort = Depends(get_chat_service),
    prompt_builder: PromptBuilderPort = Depends(get_prompt_builder),
    input_guardrail: InputGuardrailPort = Depends(get_input_guardrail)
) -> ChatUseCase:
    return ChatUseCase(chat_service=service, chat_repository=repository, prompt_builder=prompt_builder, input_guardrail=input_guardrail)