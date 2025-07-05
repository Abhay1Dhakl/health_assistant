# Design Notes - Medical Information System

## Design Choices

The system follows a **multi-layered architecture** with clear separation of concerns:

1. **FastAPI Backend**: Chosen for its async support, automatic API documentation, and robust request/response handling
2. **RAG Architecture with MCP**: Implements Retrieval-Augmented Generation using Model Context Protocol for standardized document retrieval and knowledge grounding
3. **Multi-Document RAG System**: Three specialized ChromaDB vector databases store embeddings for different medical documents (StatPearls, Clinical Data, JCLA) enabling semantic search and retrieval
4. **Dynamic Tool Selection**: AI-powered document selection based on query intent ensures relevant information retrieval from the appropriate vector database
5. **Vector-Based Document Retrieval**: ChromaDB enables semantic similarity search to find the most relevant document chunks for each query

## Libraries Used

- **FastAPI + Uvicorn**: High-performance async web framework with automatic OpenAPI documentation
- **LangChain**: Orchestrates LLM interactions and tool integration with structured prompting
- **OpenAI GPT-4**: Provides medical reasoning capabilities with low temperature (0.01) for consistent responses
- **MCP-Use**: Implements Model Context Protocol for standardized document server communication in RAG pipeline
- **ChromaDB**: Vector database serving as the core of the RAG system - stores document embeddings and enables semantic similarity search across medical literature
- **Sentence Transformers**: Generates high-quality embeddings for both documents and queries, enabling effective semantic retrieval in the RAG system
- **PyPDF2**: Handles PDF document processing and text extraction for vector database ingestion

## Addressing Hallucinations

The RAG system implements multiple strategies to minimize AI hallucinations:

1. **Grounded RAG Responses**: All information is retrieved from verified medical documents stored in ChromaDB vector databases, preventing fabricated content
2. **Vector-Based Retrieval**: ChromaDB ensures only semantically relevant document chunks are provided to the LLM, maintaining factual accuracy
3. **Mandatory Citations**: Every response includes paragraph-level citations (Source, DocumentX) linking information to specific sources retrieved from the vector database
4. **Reference Lists**: Structured reference sections provide full source attribution for all retrieved documents
5. **Low Temperature Setting**: Temperature of 0.01 ensures consistent, deterministic responses based on retrieved content
6. **Structured Prompting**: Detailed system prompts guide the AI to stick to retrieved document content and explicitly state limitations
7. **Document Boundaries**: Clear instructions prevent the AI from generating information not present in the ChromaDB vector stores
8. **RAG Pipeline Validation**: Multi-step retrieval process ensures only relevant, verified medical information is used for response generation

This RAG-based design ensures medical accuracy while maintaining transparency about information sources and system limitations. The ChromaDB vector database serves as the foundation for reliable, semantically-aware document retrieval in the medical domain.
