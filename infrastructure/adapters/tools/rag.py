from domain.ports.tool import AgentTool
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pinecone import Pinecone

class RAGTool(AgentTool):
    name = "rag"
    description = "Search in the knowledge base"
    run_args_schema = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Query to search in the knowledge base"
            },
            "category": {
                "type": "string",
                "description": "Category to search in the knowledge base. Valid values: 'dinero', 'documentacion', 'transporte'"
            }
        },
        "required": ["query", "category"]
    }
    def __init__(self, embedding_model:str = "models/gemini-embedding-2", embedding_dim: int = 768):
        # Load environment variables
        load_dotenv()
        self.embedding_model = embedding_model
        self.embedding_dim = embedding_dim
        self.genai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.pc = Pinecone(api_key=os.getenv("PINECONE_KEY"))

    # @property
    # def genai_client(self):
    #     if self._genai_client is None:
    #         GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    #         self._genai_client = genai.Client(api_key=GEMINI_API_KEY)
    #     return self._genai_client

    # @property
    # def pc(self):
    #     if self._pc is None:
    #         PINECONE_KEY = os.getenv("PINECONE_KEY")
    #         self._pc = Pinecone(api_key=PINECONE_KEY)
    #     return self._pc

    # def __deepcopy__(self, memo):
    #     cls = self.__class__
    #     result = cls.__new__(cls)
    #     memo[id(self)] = result
    #     for k, v in self.__dict__.items():
    #         if k in ["_genai_client", "_pc"]:
    #             setattr(result, k, None)
    #         else:
    #             setattr(result, k, copy.deepcopy(v, memo))
    #     return result

    async def run(self, query: str, category: str) -> list[str]:
        """
        Run the tool
        
        Args:
            query: Query to search in the knowledge base
            category: Category to search in the knowledge base. Valid values: 'dinero', 'documentacion', 'transporte'
        
        Returns:
            The result of the tool
        """
        if category not in ['dinero', 'documentacion', 'transporte']:
            raise ValueError("Invalid category")
        try:
            embed_response = await self.genai_client.aio.models.embed_content(
                model=self.embedding_model,
                contents=query,
                config=types.EmbedContentConfig(output_dimensionality=self.embedding_dim),
            )
            query_embedding = embed_response.embeddings[0].values
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            raise e
        try:
            res = self.pc.Index("faq-index").query(vector=query_embedding, top_k=5, include_metadata=True)
            data = [r.metadata['text'] for r in res.matches]
            return data

        except Exception as e:
            print(f"Error querying Pinecone: {e}")
            raise e