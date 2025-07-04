install uv
create a virtual environment using uv : uv venv .venv
create a ptproject.toml file and add this content:
[project]
name = "ai-ml-engineer-assignment"
version = "0.1.0"
description = "AI/ML Engineer Assignment with MCP servers"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "chromadb",
    "flask",
    "sentence-transformers",
    "python-dotenv",
    "PyPDF2",
    "mcp",
    "fastapi",
    "uvicorn",
    "torch",
    "transformers",
    "requests",
    "langchain-openai",
    "pydantic"
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = []

