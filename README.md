# CVTailor MCP LangGraph Agent

An AI-powered job application assistant that demonstrates MCP, LangGraph, LangChain, Hugging Face, and SQLite integration.

## Overview

This project provides an intelligent job application assistant that:
- Uses an **MCP (Model Context Protocol) server** as the tool/data layer
- Uses **LangGraph** as the agent workflow engine
- Uses **LangChain** for prompts and LLM abstraction
- Supports **Hugging Face** models for real LLM calls
- Includes a **mock LLM mode** for reproducible local demos
- Tracks applications in **SQLite**

The assistant analyzes job descriptions, matches them against your resume and profile, and generates tailored application packs including a cover letter, matched skills table, and gap analysis.

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

## Demo Command

```bash
python -m cvtailor_agent.cli run \
  --job-file examples/job_description_ai_engineer.txt \
  --company "Acme AI" \
  --role "AI Engineer"
```

Expected output:
```
Application pack generated successfully.
Output path: outputs/acme-ai-ai-engineer-application-pack.md
Application ID: 1
```

## Sample Data

The project includes sample data for demos:

- `data/profile.json` - Candidate profile (skills, experience, contact info)
- `data/resume.md` - Full markdown resume with projects and experience
- `examples/job_description_ai_engineer.txt` - Sample AI Engineer job posting

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
