from mcp.server.fastmcp import FastMCP 
import chromadb
import os
import json
from sentence_transformers import SentenceTransformer
from typing import Dict, Any
import sys

mcp = FastMCP(
    name="mcp_server",
    host="0.0.0.0",
    port=8001,
    debug=False
)

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

# @mcp.prompt()
# def get_ind_legal_data() -> str:
#     """Prompt the user for customer type: INDIVIDUAL or LEGAL."""
#     return "Please provide the customer type: INDIVIDUAL or LEGAL."

@mcp.tool(name="document1", description="Get structured data from ChromaDB")
def document1(query: str) -> Dict[str, Any]:
    """Get structured data from ChromaDB"""

    try:
        # Initialize ChromaDB
        client = chromadb.PersistentClient(path='chroma_db1')
        collection = client.get_collection("document1_embedded_data")
        
        # Generate embeddings
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        query_vector = embedding_model.encode(query)
        
        # Query ChromaDB
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=5,
            include=["documents", "metadatas"]
        )
        
        # Process results
        response = {"filter": "1=1", "contexts": []}  # Default safe filter
        if results.get("documents"):
            documents_list = results["documents"]
            metadatas_list = results.get("metadatas", [])

            for docs, metas in zip(documents_list, metadatas_list):
                for doc, meta in zip(docs, metas):
                    response["contexts"].append({
                        "document": doc,
                        "metadata": meta
                    })

            # Optional: update filter if one is present in the first metadata
            if metadatas_list and metadatas_list[0] and isinstance(metadatas_list[0][0], dict):
                response["filter"] = metadatas_list[0][0].get("filter", "1=1")

        return response
        
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return format_response(str(e), "error")


@mcp.tool(name="document2", description="Get structured data from ChromaDB")
def document2(query: str) -> Dict[str, Any]:
    """Get structured data from ChromaDB"""

    try:
        # Initialize ChromaDB
        client = chromadb.PersistentClient(path='chroma_db2')
        collection = client.get_collection("document2_embedded_data")
        
        # Generate embeddings
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        query_vector = embedding_model.encode(query)
        
        # Query ChromaDB
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=5,
            include=["documents", "metadatas"]
        )
        
        # Process results
        response = {"filter": "1=1", "contexts": []}  # Default safe filter
        if results.get("documents"):
            documents_list = results["documents"]
            metadatas_list = results.get("metadatas", [])

            for docs, metas in zip(documents_list, metadatas_list):
                for doc, meta in zip(docs, metas):
                    response["contexts"].append({
                        "document": doc,
                        "metadata": meta
                    })

            # Optional: update filter if one is present in the first metadata
            if metadatas_list and metadatas_list[0] and isinstance(metadatas_list[0][0], dict):
                response["filter"] = metadatas_list[0][0].get("filter", "1=1")

        return response
        
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return format_response(str(e), "error")


@mcp.tool(name="document3", description="Get structured data from ChromaDB")
def document3(query: str) -> Dict[str, Any]:
    """Get structured data from ChromaDB"""

    try:
        # Initialize ChromaDB
        client = chromadb.PersistentClient(path='chroma_db3')
        collection = client.get_collection("document3_embedded_data")
        
        # Generate embeddings
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        query_vector = embedding_model.encode(query)
        
        # Query ChromaDB
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=5,
            include=["documents", "metadatas"]
        )
        
        # Process results
        response = {"filter": "1=1", "contexts": []}  # Default safe filter
        if results.get("documents"):
            documents_list = results["documents"]
            metadatas_list = results.get("metadatas", [])

            for docs, metas in zip(documents_list, metadatas_list):
                for doc, meta in zip(docs, metas):
                    response["contexts"].append({
                        "document": doc,
                        "metadata": meta
                    })

            # Optional: update filter if one is present in the first metadata
            if metadatas_list and metadatas_list[0] and isinstance(metadatas_list[0][0], dict):
                response["filter"] = metadatas_list[0][0].get("filter", "1=1")

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