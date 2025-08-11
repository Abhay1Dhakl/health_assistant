from mcp.server.fastmcp import FastMCP 
import chromadb
import os
import json
from sentence_transformers import SentenceTransformer
from typing import Dict, Any
import sys
from pinecone.grpc import PineconeGRPC, GRPCClientConfig
from pinecone import Pinecone


embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

mcp = FastMCP(
    name="mcp_server",
    host="0.0.0.0",
    port=8001,
    debug=False
)

pc = Pinecone(
    # api_key=os.getenv("PINECONE_API_KEY"))
    api_key= "pcsk_2RGA3Z_LVfVmxNQ7A7DX7w5BuhEW4MTCGmGuSghX7GmMwizqWqVCumyrWCcMdtE1jDxgav",
    environment="aped-4627-b74a"  )

document_index_host = pc.describe_index(name="quickstart-py").host 
document_index = pc.Index(host = document_index_host, grpc_config=GRPCClientConfig(secure=False)) 

def parse_pinecone_response(pinecone_response):
    """Parse Pinecone response to extract metadata"""
    if not pinecone_response or "matches" not in pinecone_response:
        return {"matches": []}
    
    parsed = {
        "matches": []
    }
    
    for match in pinecone_response["matches"]:
        metadata = match.get("metadata", {})
        parsed["matches"].append({
            "id": match.get("id"),
            "score": match.get("score"),
            "metadata": metadata
        })
    print("Parsed Pinecone Response:", json.dumps(parsed, indent=2), file=sys.stderr)
    return parsed


def format_response(data: Any, status: str = "success") -> Dict[str, Any]:
    """Ensure all responses follow MCP JSON-RPC 2.0 format"""
    return {
        "jsonrpc": "2.0",
        "status": status,
        "result": data if status == "success" else None,
        "error": {
            "code": -32603,
            "message": str(data)
        } if status == "error" else None,
        "id": None  # Will be set by MCP framework
    }



@mcp.tool(name="lrd", description="Get structured data from ChromaDB")
def document1(query: str) -> Dict[str, Any]:
    """Get structured data from ChromaDB"""

    try:
        # Generate embeddings
        query_vector = embedding_model.encode(query)
        if hasattr(query_vector, "tolist"):
            query_vector = query_vector.tolist()
        pinecone_response = document_index.query(
            top_k=1,
            include_values=True,
            include_metadata=True,
            vector=query_vector,
            filter={"document_type": "LRD"}  # Example filter, adjust as needed
        )

        print(f"Query Response: {pinecone_response}", file=sys.stderr)
        
        response = parse_pinecone_response(pinecone_response)
        print(f"Parsed Response: {response}", file=sys.stderr)
        return response
        
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return format_response(str(e), "error")



@mcp.tool(name="pis", description="Get structured data from ChromaDB")
def document1(query: str) -> Dict[str, Any]:
    """Get structured data from ChromaDB"""

    try:
        # Generate embeddings
        query_vector = embedding_model.encode(query)
        if hasattr(query_vector, "tolist"):
            query_vector = query_vector.tolist()
        pinecone_response = document_index.query(
            top_k=5,
            include_values=True,
            include_metadata=True,
            vector=query_vector,
            filter={"document_type": "PI"}  # Example filter, adjust as needed
        )

        print(f"Query Response: {pinecone_response}", file=sys.stderr)
        
        response = parse_pinecone_response(pinecone_response)
        print(f"Parsed Response: {response}", file=sys.stderr)
        return response
        
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return format_response(str(e), "error")



@mcp.tool(name="hpl", description="Get structured data from ChromaDB")
def document1(query: str) -> Dict[str, Any]:
    """Get structured data from ChromaDB"""

    try:
        # Generate embeddings
        query_vector = embedding_model.encode(query)
        if hasattr(query_vector, "tolist"):
            query_vector = query_vector.tolist()
        pinecone_response = document_index.query(
            top_k=1,
            include_values=True,
            include_metadata=True,
            vector=query_vector,
            filter={"document_type": "hpl"}  # Example filter, adjust as needed
        )

        print(f"Query Response: {pinecone_response}", file=sys.stderr)
        
        response = parse_pinecone_response(pinecone_response)
        print(f"Parsed Response: {response}", file=sys.stderr)
        return response
        
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return format_response(str(e), "error")
    

if __name__ == "__main__":
    import asyncio
    print("Initializing MCP server with SSE transport...", file=sys.stderr)
    try:
        # Get the current event loop or create a new one if none exists
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        loop.run_until_complete(mcp.run(transport='sse'))
    except KeyboardInterrupt:
        print("MCP Server shutting down gracefully...", file=sys.stderr)
    except Exception as e:
        print(f"Error starting MCP server: {e}", file=sys.stderr)
        sys.exit(1)