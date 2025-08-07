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
    model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
    embedding = model.encode(text, convert_to_tensor=True)
    return embedding.tolist()

async def store_document(data, text_content):
    doc_id = str(uuid.uuid4())
    # Mock database write
    print(f"Content Length: {len(text_content)}")
    embedding = get_embedding_data(text_content)
    metadata = {
        "instance_id": data.get("instance_id"),
        "document_type": data.get("document_type"),
        "source_type": data.get("source_type"),
        "source_system": data.get("source_system"),
        "title": data.get("document_metadata", {}).get("title"),
        "language": data.get("document_metadata", {}).get("language"),
        "region": data.get("document_metadata", {}).get("region"),
        "author": data.get("document_metadata", {}).get("author"),
        "tags": data.get("document_metadata", {}).get("tags"),
        "ingested_at": datetime.utcnow().isoformat()
    }
    # Upsert into Pinecone
    pc.Index(index_name).upsert([
        {
            "id": doc_id,
            "values": embedding,
            "metadata": metadata
        }
    ])
    index = pc.Index("quickstart-py")
    print(index.describe_index_stats())
    return {
        "document_id": doc_id,
        "status": "stored",
        "ingested_at": metadata["ingested_at"]
    }