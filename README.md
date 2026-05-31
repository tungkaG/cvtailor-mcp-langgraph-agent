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

## LLM Configuration

The agent supports two LLM modes:

### Mock Mode (Default)

No API keys required. Returns deterministic responses for testing and demos.

```bash
# .env
LLM_PROVIDER=mock
```

### Hugging Face Mode

Uses Hugging Face Inference API for real LLM responses.

1. Get a Hugging Face API token from https://huggingface.co/settings/tokens
2. Configure your `.env` file:

```bash
# .env
LLM_PROVIDER=huggingface
HF_TOKEN=your_token_here
HF_MODEL=mistralai/Mistral-7B-Instruct-v0.3
TEMPERATURE=0.2
MAX_NEW_TOKENS=900
```

**Environment Variables:**
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LLM_PROVIDER` | No | `mock` | LLM provider: `mock` or `huggingface` |
| `HF_TOKEN` | Yes (for HF) | - | Hugging Face API token |
| `HF_MODEL` | No | `mistralai/Mistral-7B-Instruct-v0.3` | Model ID |
| `TEMPERATURE` | No | `0.2` | Sampling temperature |
| `MAX_NEW_TOKENS` | No | `900` | Max tokens to generate |

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
