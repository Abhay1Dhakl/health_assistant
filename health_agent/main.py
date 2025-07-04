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
from dotenv import load_dotenv
from mcp_use import MCPAgent, MCPClient
from langchain_openai import ChatOpenAI
from mcp_use.adapters.langchain_adapter import LangChainAdapter
from chromadb.config import Settings
from mcp import Tool
import sys
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # your frontend port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Load environment variables
load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# app = FastAPI()

import sys
import asyncio

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

def vectorize_query(user_query):
    """Generate a vector representation of the user's query."""
    return embedding_model.encode(user_query)

import json
from langchain_core.messages import HumanMessage

async def handle_tool_selection(user_query, tools, llm):
    """
    Automatically lets the LLM select the best tool (document1/2/3) and executes it.
    Returns the tool's response.
    """
    # Bind tools to the model
    llm_with_tools = llm.bind_tools(tools)

    # Step 1: Prompt the model
    result = await llm_with_tools.ainvoke([
        HumanMessage(content=user_query)
    ])

    # Step 2: Check if it wants to call a tool
    tool_calls = result.additional_kwargs.get("tool_calls", [])
    if not tool_calls:
        print("No tool selected by LLM.")
        return result.content or "No tool needed for this query."

    tool_results = {}
    for tool_call in tool_calls:
        tool_name = tool_call["function"]["name"]
        args = json.loads(tool_call["function"]["arguments"])

        # Step 3: Find and run the selected tool
        matching_tool = next((tool for tool in tools if tool.name == tool_name), None)
        if matching_tool:
            print(f"LLM selected tool: {tool_name} with args: {args}")
            tool_output = await matching_tool.ainvoke(args)
            tool_results[tool_name] = tool_output
        else:
            print(f"Tool {tool_name} not found in tools list.")

    return tool_results

async def query_mcp(user_query: str) -> dict:
    """Return the SQL condition only.
    
    Args:
        user_query: The natural language query to convert to SQL conditions
        
    Returns:
        str: The SQL WHERE clause conditions
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

        # tool_outputs = await handle_tool_selection(user_query, tools, llm)

        # print("Final Output from tool(s):", tool_outputs)
        # filter_condition = result
        
        # System prompt - clear instruction for SQL generation
        system_prompt = f"""
            You are an expert medical information assistant with access to multiple pharmaceutical and medical documents through specialized tools.

            Available Tools and Documents:
            - document1: Azithromycin information from StatPearls/NCBI (comprehensive drug information, mechanisms, clinical uses)
            - document2: Azithromycin clinical data and research findings  
            - document3: JCLA medical journal article (clinical laboratory analysis and research)

            User's question:
            \"\"\"{user_query}\"\"\"

            Instructions:
            1. **Analyze the user's question** to determine which document(s) would be most relevant:
            - For drug information, dosage, side effects, mechanisms → prioritize document1 (StatPearls)
            - For clinical research, studies, efficacy data → consider document2 or document3
            - For laboratory analysis, clinical parameters → prioritize document3 (JCLA)
            - For comprehensive drug overview → use document1 first, then supplement with others if needed

            2. **Choose the appropriate tool(s)**:
            - Use the tool name that corresponds to the most relevant document
            - You may call multiple tools if the question requires information from different sources
            - Start with the most relevant document, then supplement with others if needed

            3. **Provide a comprehensive answer** based on the retrieved information:
            - Extract relevant information that directly answers the user's question
            - If using multiple sources, clearly indicate which information comes from which document
            - Maintain medical accuracy and cite the source document when providing specific details
            - If the information is not available in any document, clearly state this limitation

            4. **Response format**:
            - Start with a direct answer to the question
            - Provide supporting details from the relevant document(s)
            - Include any important warnings, contraindications, or clinical considerations
            - End with the source attribution (e.g., "Based on StatPearls documentation" or "According to JCLA research")

            Choose the most appropriate tool(s) and provide an accurate, comprehensive response based on the available medical literature.
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
                            "content": result  # ✅ required
                        })

        # Step 3: Feed full conversation + tool output back to LLM
        final_response = await llm_with_tools.ainvoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query},
            {
                "role": "assistant",
                "content": "",  # ✅ fix here!
                "tool_calls": response.tool_calls
            },
            *tool_messages
        ])

        print(final_response.content)
            # return second_response.content
            
        
        # Handle different response formats
        if isinstance(result, dict):
            result = result.get("filter", str(result))
            
        # Fallback for string responses
        return final_response.content
        
    except Exception as e:
        # Log the error and return a default or raise
        print(f"Error in query_mcp: {str(e)}")
        return "Error detected"  # Default safe filter, or consider raising the exception


def query_llm_with_filter(user_query,mcp_result):
    """Generate a response using the external API."""
    context = vectorize_query(user_query)
    if isinstance(context, dict):
        context = " ".join(context)
    print(context)
    if context.startswith("Error") or context.startswith("No matching"):
        return context  # Return the error or no match message directly
    
    # If a matching filter was found, proceed with LLM query
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        # "model": "gpt-3.5-turbo",  # Specify your LLM model
        "messages": [
          {
    "role": "system",
    "content": "You are a helpful assistant that generates a SQL query based on the provided context and query. Do not give any explanation, just provide the SQL query."
},
{
    "role": "user",
    "content": f"Given this context: {context}, complete the following SQL query based on the user query: '{user_query}'. Only include the relevant condition for the query in the WHERE clause, and do not add unnecessary conditions. The starting query is: 'SELECT * FROM iceberg.gold.cdp WHERE'. Context: {context} remove the fact. from the filter and just keep the column name. User Query: {user_query}"
}


        ]
    }

    # Sending request to OpenAI's API (or any other LLM API)
    try:
        response = requests.post(url=f"{OPENAI_BASE_URL}chat/completions", headers=headers, json=data)
        response_data = response.json()
        return response_data['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error querying LLM: {e}")
        return "Failed to get a response from the LLM."
   
def generate_description(result,user_query):
     # Calculate basic statistics
    row_count = len(result)
    
    # Prepare data segment examples (first 3 rows) for analysis
    sample_data = result[:3] if row_count > 0 else []

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
    Analyze this dataset and provide insights:
    
    - Total rows: {row_count}
    - Sample data: {sample_data}
    - Original user query: "{user_query}"
    
    Your task:
    1. Identify key segments in the data (e.g., categories, patterns)
    2. Note any interesting distributions or outliers
    3. Provide a concise 2-3 sentence summary
    4. Suggest potential follow-up analysis questions
    
    Format your response as JSON with these keys:
    - "segments": List the main data segments found
    - "key_observations": Notable patterns in the data  
    - "summary": Brief overall summary
    - "follow_up_questions": 2-3 suggested next questions
    
    Return ONLY the JSON object, no additional text or explanations.
    """

    data = {
        # "model": "gpt-3.5-turbo",  # Specify your LLM model
        "messages": [
          {
    "role": "system",
    "content":"You are a data analyst that provides clear insights about datasets in JSON format."
},
{
    "role": "user",
    "content":prompt
}


        ]
    }

    # Sending request to OpenAI's API (or any other LLM API)
    try:
        response = requests.post(url=f"{OPENAI_BASE_URL}chat/completions", headers=headers, json=data)
        response_data = response.json()
        return response_data['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error querying LLM: {e}")
        return "Failed to get a response from the LLM."


async def process_query(user_query):
    "Return the SQL condition only."
    
    mcp_result = await query_mcp(user_query)  # Get the result from MCP

    # if isinstance(mcp_result, str) and mcp_result.startswith("Error"):
    #     return {"error": mcp_result}  # Return error from MCP

    # Now, mcp_result contains the context or filter from ChromaDB
    print(f"Received context from MCP: {mcp_result}")
    
    # Step 1: Generate SQL query based on LLM with ChromaDB context from MCP
    # response = query_llm_with_filter(user_query, mcp_result)

    # print('sql query', response)
    # result = execute_sql_on_trino(response)

    # description = generate_description(result,user_query)
    
    return mcp_result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

