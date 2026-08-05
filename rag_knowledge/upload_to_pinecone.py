import os
import re
import yaml
from dotenv import load_dotenv
import tiktoken
from google import genai
from google.genai import types
from pinecone import Pinecone, ServerlessSpec

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PINECONE_KEY = os.getenv("PINECONE_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables.")
if not PINECONE_KEY:
    raise ValueError("PINECONE_KEY is not set in the environment variables.")

# Initialize Clients
print("Initializing Google GenAI and Pinecone clients...")
genai_client = genai.Client(api_key=GEMINI_API_KEY)
pc = Pinecone(api_key=PINECONE_KEY)

INDEX_NAME = "faq-index"
EMBEDDING_MODEL = "models/gemini-embedding-2"
DIMENSION = 768

def setup_pinecone():
    """Checks if the Pinecone index exists, and creates it if not."""
    existing_indexes = [idx.name for idx in pc.list_indexes()]
    if INDEX_NAME not in existing_indexes:
        print(f"Creating Pinecone index '{INDEX_NAME}' with dimension {DIMENSION}...")
        pc.create_index(
            name=INDEX_NAME,
            dimension=DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        print("Pinecone index created successfully.")
    else:
        print(f"Pinecone index '{INDEX_NAME}' already exists.")
    return pc.Index(INDEX_NAME)

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    """Chunks text into chunks of `chunk_size` tokens with `overlap` tokens overlap using tiktoken."""
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    
    if len(tokens) <= chunk_size:
        return [text]
        
    chunks = []
    i = 0
    while i < len(tokens):
        chunk_tokens = tokens[i:i + chunk_size]
        chunks.append(encoding.decode(chunk_tokens))
        i += chunk_size - overlap
        if i >= len(tokens):
            break
            
    return chunks

def clean_metadata(metadata: dict) -> dict:
    """Cleans metadata dictionary to ensure only supported Pinecone types are used."""
    cleaned = {}
    for k, v in metadata.items():
        if v is None:
            continue
        if isinstance(v, (str, int, float, bool)):
            cleaned[k] = v
        elif isinstance(v, list):
            cleaned[k] = [str(item) for item in v]
        elif isinstance(v, dict):
            import json
            cleaned[k] = json.dumps(v)
        else:
            cleaned[k] = str(v)
    return cleaned

def parse_markdown_faqs(file_path: str) -> list[dict]:
    """Parses markdown file with multiple FAQ blocks separated by ---."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Split content by --- on a line by itself
    parts = re.split(r"^---$", content, flags=re.MULTILINE)
    
    faqs = []
    i = 1
    file_basename = os.path.basename(file_path)
    
    while i < len(parts):
        yaml_part = parts[i].strip()
        if not yaml_part:
            i += 1
            continue
        
        # Next part should be the content
        if i + 1 >= len(parts):
            break
            
        content_part = parts[i+1].strip()
        
        try:
            metadata = yaml.safe_load(yaml_part)
            if isinstance(metadata, dict) and "id" in metadata:
                # Add source file to metadata
                metadata["source_file"] = file_basename
                faqs.append({
                    "metadata": metadata,
                    "content": content_part
                })
                i += 2  # skip past both yaml and content
                continue
        except Exception as e:
            # Not a YAML block, skip
            pass
            
        i += 1
        
    return faqs

def process_and_upload():
    # Setup Pinecone index
    index = setup_pinecone()
    
    faqs_dir = os.path.expanduser("~/Developer/learn/RH-agent/rag_knowledge/faqs")
    if not os.path.exists(faqs_dir):
        # Fallback to local workspace check
        faqs_dir = "rag_knowledge/faqs"
        
    print(f"Reading markdown files from: {faqs_dir}")
    md_files = [os.path.join(faqs_dir, f) for f in os.listdir(faqs_dir) if f.endswith(".md")]
    
    all_chunks = []
    
    for file_path in md_files:
        print(f"Parsing: {file_path}")
        faqs = parse_markdown_faqs(file_path)
        print(f"Found {len(faqs)} FAQs in {os.path.basename(file_path)}")
        
        for faq in faqs:
            metadata = faq["metadata"]
            content = faq["content"]
            faq_id = metadata["id"]
            
            # Chunk the content manually (500 tokens limit with 100 overlap)
            chunks = chunk_text(content, chunk_size=500, overlap=100)
            
            for idx, chunk in enumerate(chunks):
                chunk_metadata = metadata.copy()
                chunk_metadata["text"] = chunk
                chunk_metadata["chunk_index"] = idx
                
                # Create a unique ID for this chunk
                vector_id = f"{faq_id}-chunk-{idx}" if len(chunks) > 1 else faq_id
                
                all_chunks.append({
                    "id": vector_id,
                    "text": chunk,
                    "metadata": clean_metadata(chunk_metadata)
                })
                
    print(f"Total chunks to embed and upload: {len(all_chunks)}")
    
    # Process in batches of 50 to avoid API limits and make progress tracking easy
    batch_size = 50
    for idx in range(0, len(all_chunks), batch_size):
        batch = all_chunks[idx : idx + batch_size]
        print(f"Processing batch {idx // batch_size + 1}/{(len(all_chunks) - 1) // batch_size + 1}...")
        
        texts_to_embed = [item["text"] for item in batch]
        contents_to_embed = [
            types.Content(parts=[types.Part.from_text(text=text)])
            for text in texts_to_embed
        ]
        
        # Generate embeddings
        try:
            embed_response = genai_client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=contents_to_embed,
                config=types.EmbedContentConfig(output_dimensionality=DIMENSION),
            )
            embeddings = [e.values for e in embed_response.embeddings]
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            raise e
            
        # Build vectors payload for Pinecone
        vectors_to_upsert = []
        for item, embedding in zip(batch, embeddings):
            vectors_to_upsert.append({
                "id": item["id"],
                "values": embedding,
                "metadata": item["metadata"]
            })
            
        # Upsert to Pinecone
        try:
            upsert_response = index.upsert(vectors=vectors_to_upsert)
            print(f"Upserted {upsert_response.upserted_count} vectors.")
        except Exception as e:
            print(f"Error upserting vectors to Pinecone: {e}")
            raise e

    print("Successfully uploaded all embeddings to Pinecone!")

if __name__ == "__main__":
    process_and_upload()
