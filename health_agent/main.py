import sys
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from flask import Flask, jsonify, request
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch
import chromadb
import requests
import json
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from mcp_use import MCPAgent, MCPClient
from langchain_openai import ChatOpenAI
from mcp_use.adapters.langchain_adapter import LangChainAdapter
from chromadb.config import Settings
from mcp import Tool
import sys
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sys
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Load environment variables
load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set Windows event loop policy
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
  
# Load Sentence Transformer for query vectorization
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Define the input schema
class QueryRequest(BaseModel):
    user_query: str

@app.post("/query")
async def handle_query(request: QueryRequest):
    user_query = request.user_query
    if not user_query:
        return JSONResponse(content={"error": "Invalid input. Query is required."}, status_code=400)
    
    try:
        response = await process_query(user_query)
        return JSONResponse(content={"response": response})
    except Exception as e:
        print(f"Error processing query: {e}")
        return JSONResponse(content={"error": "An error occurred while processing the query."}, status_code=500)


async def query_mcp(user_query: str) -> str:
    """
    Query the MCP server to retrieve medical information from azithromycin documents.
    
    This function connects to the MCP server, uses AI to select the most relevant
    document(s) based on the user's query, and returns a comprehensive medical
    response with proper citations.
    
    Args:
        user_query (str): The user's medical question about azithromycin
        
    Returns:
        str: Medical information response with citations and references
        
    Raises:
        Exception: If MCP server connection fails or query processing encounters errors
    """
    print("i am here")
    config_file = 'mcp_server_config.json'
    
    try:
        client = MCPClient.from_config_file(config_file)
    
       # Initialize LLM (consider making this a global/class variable if used frequently)
        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.01,
            openai_api_key=OPENAI_API_KEY,
            openai_api_base=OPENAI_BASE_URL,
        )

        # System prompt - clear instruction 
        system_prompt = f"""
You are a medical AI assistant. You will receive extracted data from the MCP server along with metadata for each chunk. 
Your job is to choose the most relevant extracted segments and present them without altering their content, while adding precise citations.

### Available Tools and Documents:
- PI: Azithromycin information from StatPearls/NCBI (comprehensive drug information, mechanisms, clinical uses)
- LRD: Azithromycin clinical data and research findings  
- document3: JCLA medical journal article (clinical laboratory analysis and research)

### User's question:
\"\"\"{user_query}\"\"\"

---

### Instructions:
1. **Analyze the question** to determine which document(s) to use:
   - Drug information, dosage, side effects, mechanisms → PI (StatPearls)
   - Clinical research, studies, efficacy data → LRD
   - Laboratory analysis, clinical parameters → document3
   - For comprehensive overview → start with PI, supplement with others

2. **Tool Usage**:
   - You may use multiple tools if needed.
   - Always start with the most relevant document.

3. **Citation Rules**:
   - Use `page` and `chunk_index` directly from the MCP metadata.
   - Format each citation as: **(Source: document_type, Page page, Chunk chunk_index)**
   - If `page` or `chunk_index` is missing, explicitly write: **Page unknown** or **Chunk unknown**.
   - Include a "References" section at the end listing all sources.

4. **Formatting**:
   - Do NOT change the extracted text.
   - After every chunk of text from a document, append its citation in the required format.
   - Maintain medical accuracy.

---

### Example:
[Extracted text from PI] (Source: PI, Page 5, Chunk 2)

[Extracted text from LRD] (Source: LRD, Page unknown, Chunk 7)

---

### Final Output Structure:
[Answer paragraph 1] (Source: XXX, Page Y, Chunk Z)

[Answer paragraph 2] (Source: XXX, Page Y, Chunk Z)
            """
        adapter = LangChainAdapter()
        tools = await adapter.create_tools(client)
        print("Tools:", tools)
        # Create a custom LangChain agent
        llm_with_tools = llm.bind_tools(tools)
        from langchain_core.messages import ToolMessage
        response = await llm_with_tools.ainvoke([system_prompt, user_query])
        # print("this is result",result)
        # print(type(result))
        tool_messages = []
        if response.tool_calls:
            for call in response.tool_calls:
                tool_name = call["name"]
                tool_args = call["args"]
                for tool in tools:
                    if tool.name == tool_name:
                        result = await tool.ainvoke(tool_args)
                        tool_messages.append({
                            "role": "tool",
                            "tool_call_id": call["id"],
                            "content": result 
                        })

        # Step 3: Feed full conversation + tool output back to LLM
        final_response = await llm_with_tools.ainvoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query},
            {
                "role": "assistant",
                "content": "",
                "tool_calls": response.tool_calls
            },
            *tool_messages
        ])

        print(final_response.content)
            
        # Handle different response formats
        if isinstance(result, dict):
            result = result.get("filter", str(result))
            
        # Fallback for string responses
        return final_response.content
        
    except Exception as e:
        # Log the error and return a default or raise
        print(f"Error in query_mcp: {str(e)}")
        return "Error detected"

   
async def process_query(user_query):
    """
    Process a medical query and return the final response.
    
    This is the main query processing function that coordinates with the MCP server
    to provide medical information about azithromycin.
    
    Args:
        user_query (str): The user's medical question
        
    Returns:
        str: The processed medical information response with citations
    """

     # Get the result from MCP
    mcp_result = await query_mcp(user_query) 
    
    return mcp_result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

