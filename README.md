# CVTailor MCP LangGraph Agent

AI job-application assistant using MCP server, LangGraph, LangChain, and Hugging Face.

## Overview

This project provides an intelligent job application assistant that:
- Uses an MCP (Model Context Protocol) server as the tool/data layer
- Uses LangGraph as the agent workflow engine
- Uses LangChain for prompts and LLM abstraction
- Supports Hugging Face models for real LLM calls
- Includes a mock LLM mode for local demos
- Tracks applications in SQLite

## Setup

```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
# or
source .venv/bin/activate   # macOS/Linux

# Install in development mode
pip install -e ".[dev]"

# Copy and configure environment
cp .env.example .env
```

## Usage

```bash
python -m cvtailor_agent.cli run \
  --job-file examples/job_description_ai_engineer.txt \
  --company "Acme AI" \
  --role "AI Engineer"
```

## Project Structure

```
src/
├── cvtailor_mcp/      # MCP server and tools
│   ├── server.py      # MCP server implementation
│   ├── tools.py       # MCP tool definitions
│   ├── storage.py     # SQLite storage
│   ├── resume_search.py # Resume search functionality
│   └── schemas.py     # Pydantic data models
├── cvtailor_agent/    # LangGraph agent
│   ├── cli.py         # Typer CLI
│   ├── graph.py       # LangGraph workflow
│   ├── state.py       # Agent state
│   ├── llm.py         # LLM abstraction
│   ├── prompts.py     # Prompt templates
│   ├── mcp_client.py  # MCP client
│   └── output_formatter.py # Output formatting
data/                  # Local data files
examples/              # Example inputs
outputs/               # Generated outputs
tests/                 # Test suite
```

## License

MIT
