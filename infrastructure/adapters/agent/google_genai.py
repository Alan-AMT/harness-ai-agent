from domain.ports.tool import AgentTool
from domain.models.prompt import Prompt
import os
from google import genai
from google.genai import types
from domain.models.chat import Message, Role, TextPart, ToolCallPart, ToolResultPart
from domain.ports.chat_service import ChatServicePort

def from_gemini(content: types.Content) -> Message:
    parts = []
    if content.parts:
        for part in content.parts:
            if part.text:
                parts.append(TextPart(part.text))
            elif part.function_call:
                parts.append(
                    ToolCallPart(
                        name=part.function_call.name,
                        args=dict(part.function_call.args),
                    )
                )
            elif part.function_response:
                parts.append(
                    ToolResultPart(
                        name=part.function_response.name,
                        result=part.function_response.response,
                    )
                )

    if content.role == "user":
        role = Role.USER
    elif content.role == "context":
        role = Role.TOOL
    else:
        role = Role.ASSISTANT

    return Message(role=role, parts=parts)

class GoogleGenAIAdapter(ChatServicePort):
    # def __init__(self, api_key: str = None, model_name: str = "gemini-3.1-flash-lite"):
    def __init__(self, api_key: str = None, model_name: str = "gemini-3.5-flash-lite"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name

    @property
    def client(self):
        if not self.api_key:
            return None
        return genai.Client(api_key=self.api_key)

    def _ensure_client(self):
        if not self.client:
            raise ValueError(
                "Google GenAI Client is not initialized. Please set the GEMINI_API_KEY environment variable."
            )

    def _map_to_google_contents(self, history: list[Message]) -> list[types.Content]:
        """Maps domain Message list to Google GenAI Content types."""
        google_contents = []
        for msg in history:
            if msg.role == Role.USER:
                role = "user"
            elif msg.role == Role.TOOL:
                role = "context"
            else:
                role = "model"

            parts = []
            for part in msg.parts:
                if isinstance(part, TextPart):
                    parts.append(types.Part.from_text(text=part.text))
                elif isinstance(part, ToolCallPart):
                    parts.append(types.Part.from_function_call(name=part.name, args=part.args))
                elif isinstance(part, ToolResultPart):
                    parts.append(types.Part.from_function_response(
                        name=part.name,
                        response={"result": part.result} if not isinstance(part.result, dict) else part.result
                    ))
                    role = "context"

            if not parts:
                parts.append(types.Part.from_text(text=msg.content))

            google_contents.append(
                types.Content(
                    role=role,
                    parts=parts
                )
            )
        return google_contents

    async def generate_response_async(self, prompt: Prompt) -> list[Message]:
        self._ensure_client()
        contents = self._map_to_google_contents([*prompt.history, prompt.current_message])
        
        new_messages = []
        
        for i in range(10):
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                config=types.GenerateContentConfig(
                    system_instruction=f"{prompt.system}\n\n {prompt.policies} \n\n {prompt.personality}\n\n {prompt.user_data}\n\n {prompt.rag_context}",
                    temperature=0.0,
                    tools=[types.Tool(
                        function_declarations=[types.FunctionDeclaration(
                            name=t.name,
                            description=t.description,
                            parameters=t.run_args_schema
                        )]
                    ) for t in prompt.tools.values()],
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(
                        disable=True
                    )
                ),
                contents=contents,
            )
            
            if not response.candidates or not response.candidates[0].content or not response.candidates[0].content.parts:
                raise ValueError("Empty response received from Google Gemini API.")
            
            # Revisar si el modelo decidió ACTUAR (usar una herramienta)
            if response.function_calls:
                call = response.function_calls[0]
                print(f"[Agente] El modelo pide usar la herramienta: {call.name} con argumentos: {call.args}")
                
                # 1. Guardamos la petición del modelo en el historial
                google_content = response.candidates[0].content
                contents.append(google_content)
                new_messages.append(from_gemini(google_content))

                tool = prompt.tools.get(call.name)

                if tool is None:
                    raise ValueError(f"Unknown tool: {call.name}")


                try:
                    result = await tool.run(**call.args)
                except Exception as e:
                    print("Error calling: ", call.name, "Retry policy")
                try:
                    result = await tool.run(**call.args)
                except Exception as e:
                    print("Error retrying to call: ", call.name, "Retry policy")
                    raise e
                    
                function_response_part = types.Part.from_function_response(
                        name=call.name,
                        response={"result": result}
                    )
                tool_response_content = types.Content(role="context", parts=[function_response_part])
                contents.append(tool_response_content)
                new_messages.append(from_gemini(tool_response_content))
                
            else:
                final_content = response.candidates[0].content
                new_messages.append(from_gemini(final_content))
                return new_messages
        else:
            raise ValueError("Max agent loop calls reached.")
