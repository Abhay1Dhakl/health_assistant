import uuid
from datetime import datetime
from pinecone import Pinecone, ServerlessSpec
import dotenv
import os
from sentence_transformers import SentenceTransformer

dotenv.load_dotenv()

pc = Pinecone(
    # api_key=os.getenv("PINECONE_API_KEY"))
    api_key= "pcsk_2RGA3Z_LVfVmxNQ7A7DX7w5BuhEW4MTCGmGuSghX7GmMwizqWqVCumyrWCcMdtE1jDxgav",
    environment="aped-4627-b74a"  )

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

combined_vector_to_upsert = []
# Create a dense index with integrated embedding
index_name = "quickstart-py"
if pc.has_index(index_name):
    pc.delete_index(index_name)
pc.create_index(
    name=index_name,
    dimension=384,
    metric= "cosine",

        spec =ServerlessSpec(cloud= "aws", # Specify the cloud provider (e.g., "aws" or "gcp")
        region= "us-east-1")
            
)

def get_embedding_data(text):
    embedding = model.encode(text, convert_to_tensor=True)
    return embedding.tolist()

async def store_document(data, text_content=None):
    print("text_content:", text_content)
    print("data:", data)
    
    chunks = data.get("chunks", [])
    index = pc.Index(index_name)

    # Use the provided instance_id or generate one if missing
    instance_id = data.get("instance_id") or str(uuid.uuid4())

    # vector_id = instance_id
    vectors_to_upsert = []
    for chunk in chunks:
        # Unique ID per chunk, but tied to the same instance_id
        vector_id = f"{instance_id}_{chunk.get('page', 0)}_{chunk.get('chunk_index', 0)}"

        metadata = {
            "instance_id": instance_id,                 
            "document_type": data.get("document_type"),
            "source_type": data.get("source_type"),
            "source_system": data.get("source_system"),
            "title": data.get("document_metadata", {}).get("title"),
            "language": data.get("document_metadata", {}).get("language"),
            "region": data.get("document_metadata", {}).get("region"),
            "author": data.get("document_metadata", {}).get("author"),
            "tags": data.get("document_metadata", {}).get("tags"),
            "ingested_at": datetime.utcnow().isoformat(),
            "file_name": data.get("file_name"),
            "mime_type": data.get("mime_type"),
            "page": chunk.get("page"),
            "chunk_index": chunk.get("chunk_index"),
            "text": chunk.get("text")
        }

        # Embed just this chunk's text
        embedding = get_embedding_data(chunk["text"])
        
        vectors_to_upsert.append({
            "id": vector_id,
            "values": embedding,
            "metadata": metadata
        })
    print("Vectors to upsert:", vectors_to_upsert)
    # Upsert all chunks in a single request
    index.upsert(vectors_to_upsert)

    print(index.describe_index_stats())

    return {
        "instance_id": instance_id,
        "status": "stored",
        "chunks_stored": len(chunks),
        "last_ingested_at": datetime.utcnow().isoformat()
    }
