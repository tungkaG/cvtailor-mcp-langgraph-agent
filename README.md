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
HF_MODEL=Qwen/Qwen2.5-72B-Instruct
TEMPERATURE=0.2
MAX_NEW_TOKENS=900
```

**Environment Variables:**
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LLM_PROVIDER` | No | `mock` | LLM provider: `mock` or `huggingface` |
| `HF_TOKEN` | Yes (for HF) | - | Hugging Face API token |
| `HF_MODEL` | No | `Qwen/Qwen2.5-72B-Instruct` | Model ID |
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
╭────────────────────────────── Results ───────────────────────────────╮
│ Success!                                                             │
│                                                                      │
│ Workflow Decisions:                                                  │
│   Evidence Quality: strong                                           │
│   Evidence Score: 0.72                                               │
│   Search Attempts: 1                                                 │
│   Review Status: approved                                            │
│   Revision Count: 0                                                  │
│                                                                      │
│ Output:                                                              │
│   Path: outputs/acme-ai-ai-engineer-application-pack.md              │
│   Application ID: 1                                                  │
╰──────────────────────────────────────────────────────────────────────╯
```

## Conditional LangGraph Workflow

The agent uses LangGraph to implement conditional routing, making the workflow adaptive rather than linear.

### Evidence Quality Routing

After searching the resume for relevant evidence, the workflow scores the matches:

```
search_resume_evidence
       ↓
 score_evidence (calculate average score)
       ↓
  ┌────┴────┐
  │ strong  │ score >= 0.50
  │  match  │───────────────→ generate_draft
  └────┬────┘
       │ weak match
       ↓
 broaden_search_query
       ↓
 search_evidence_again
       ↓
 score_evidence (loop up to max_search_attempts)
       ↓
 continue_anyway ──────────→ generate_draft
```

### Review/Revision Loop

After generating a draft, the workflow reviews and optionally revises it:

```
generate_draft
       ↓
 review_draft (LLM classifies: approved / needs_revision)
       ↓
  ┌────┴────┐
  │approved │───────────────→ save_pack → log_application → END
  └────┬────┘
       │ needs_revision
       ↓
 improve_draft (increment revision_count)
       ↓
 review_draft (loop up to max_revisions)
       ↓
 max_revisions_reached ────→ save_pack → log_application → END
```

### Why LangGraph?

- **Conditional branching**: Route based on evidence quality or review classification
- **Bounded loops**: Retry search or revision with configurable limits
- **State management**: Track scores, attempts, and revisions across nodes
- **Debuggable**: Stream node execution to see exactly which path was taken

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
