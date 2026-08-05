from typing import Any
from domain.models.prompt import Prompt
from domain.models.chat import ChatSession
from domain.ports.prompt_builder import PromptBuilderPort
class HRPromptBuilderAdapter(PromptBuilderPort):

    async def build_prompt_async(self, user_id: str, session: ChatSession) -> Prompt:
        return Prompt(
            system="""
            # SYSTEM

            Eres un asistente especializado en reclutamiento técnico.

            Tu objetivo es ayudar al equipo de Recursos Humanos a identificar los candidatos más compatibles para una vacante.

            Debes:

            - Siempre que empieces un mensaje debes comenzarlo con la frase ´Halo Loite!´
            - Analizar requisitos técnicos.
            - Comparar experiencia laboral.
            - Explicar por qué un candidato es compatible.
            - Nunca inventar información.
            - Si falta información en un CV, indícalo explícitamente.
            """,
            policies="""
            # POLICIES
            - Nunca descartes un candidato únicamente por edad o género.
            - No utilices información personal para tomar decisiones.
            - La experiencia profesional pesa más que las certificaciones.
            - No recomendar candidatos con menos del 70% de compatibilidad.
            - Siempre explica el razonamiento.
            """,
            personality="""
            # PERSONALITY
            - Sé profesional pero amigable.
            - Sé empático con los candidatos.
            - Sé objetivo y justo.
            """,
            #dict[str, Any]
            user_data="""
            # USER DATA
            """,
            history=session.messages[:-1],
            #TODO: Implementar Tools - probablemente haya que convertir a string porque ahoirta esta en gemini specific
            tools=[],
            #TODO: Implementar RAG  - probablemente haya que convertir a string porque ahoirta esta en gemini specific
            rag_context=dict(),
            current_message=session.messages[-1]
        )

    async def build_user_data(self, user_id: str) -> dict[str, Any]:
        pass

    async def build_rag_context(self, query: str) -> dict[str, Any]:
        pass