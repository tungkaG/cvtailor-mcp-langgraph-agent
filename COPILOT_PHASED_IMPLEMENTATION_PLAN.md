# CVTailor MCP LangGraph Agent - Phased Implementation Plan for GitHub Copilot

Use this file as your working implementation checklist. The app should be built in phases, not in one large generation. After each phase, run the verification commands, fix any errors, commit the working code, and only then move to the next phase.

Project name: `cvtailor-mcp-langgraph-agent`

Core idea: Build a simple AI job-application assistant that uses an MCP server as the tool/data layer, LangGraph as the agent workflow engine, LangChain for prompts and LLM abstraction, Hugging Face for real LLM calls, a mock LLM for local demos, and SQLite for application tracking.

---

## Important working rule

Do not ask Copilot to build the full app in one prompt.

Use this loop for every phase:

```text
1. Paste the phase prompt into Copilot Chat.
2. Let Copilot edit/create only the files for that phase.
3. Run the verification commands.
4. If there are errors, ask Copilot to fix only that phase.
5. Commit the phase.
6. Move to the next phase only after verification passes.
```

Recommended commit style:

```bash
git add .
git commit -m "phase 01 project scaffold"
```

---

## Final target user flow

At the end, this command should work:

```bash
python -m cvtailor_agent.cli run \
  --job-file examples/job_description_ai_engineer.txt \
  --company "Acme AI" \
  --role "AI Engineer"
```

Expected result:

```text
Application pack generated successfully.
Output path: outputs/acme-ai-ai-engineer-application-pack.md
Application ID: 1
```

The generated Markdown file should contain:

```text
Job Requirement Summary
Candidate Match Score
Matched Skills Table
Tailored Resume Summary
Tailored Resume Bullets
Short Cover Letter
Gap Analysis
Next Actions
```

---

# Phase 0 - Local setup

## Goal

Prepare your local environment before asking Copilot to build anything.

## Manual commands

```bash
mkdir cvtailor-mcp-langgraph-agent
cd cvtailor-mcp-langgraph-agent
git init
python -m venv .venv
```

Activate the virtual environment.

macOS/Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Create this file in your repo:

```text
COPILOT_PHASED_IMPLEMENTATION_PLAN.md
```

Paste this whole phased plan into that file.

## Verification

```bash
python --version
git status
```

## Expected result

Python should be 3.11 or newer. Git should show an empty/new repo.

## Commit

```bash
git add COPILOT_PHASED_IMPLEMENTATION_PLAN.md
git commit -m "phase 00 add phased implementation plan"
```

---

# Phase 1 - Project scaffold

## Goal

Create the project structure, config files, placeholder packages, and installable Python project layout.

## Copilot prompt

```text
Read COPILOT_PHASED_IMPLEMENTATION_PLAN.md.

Implement Phase 1 only.

Create the project scaffold for a Python 3.11+ project called CVTailor MCP LangGraph Agent.

Create these files and folders:

README.md
pyproject.toml
.env.example
.gitignore

data/
data/.gitkeep
examples/
examples/.gitkeep
outputs/
outputs/.gitkeep

src/
src/cvtailor_mcp/
src/cvtailor_mcp/__init__.py
src/cvtailor_mcp/server.py
src/cvtailor_mcp/tools.py
src/cvtailor_mcp/storage.py
src/cvtailor_mcp/resume_search.py
src/cvtailor_mcp/schemas.py

src/cvtailor_agent/
src/cvtailor_agent/__init__.py
src/cvtailor_agent/cli.py
src/cvtailor_agent/graph.py
src/cvtailor_agent/state.py
src/cvtailor_agent/llm.py
src/cvtailor_agent/prompts.py
src/cvtailor_agent/mcp_client.py
src/cvtailor_agent/output_formatter.py

tests/
tests/__init__.py
tests/test_placeholder.py

In pyproject.toml, configure:
- project metadata
- Python >=3.11
- dependencies: mcp, langgraph, langchain, langchain-core, langchain-huggingface, huggingface-hub, pydantic, typer, rich, python-dotenv
- dev dependency or optional dependency for pytest
- src package layout

In .env.example include:
LLM_PROVIDER=mock
HF_TOKEN=
HF_MODEL=mistralai/Mistral-7B-Instruct-v0.3
TEMPERATURE=0.2
MAX_NEW_TOKENS=900

In .gitignore include:
.venv/
__pycache__/
.pytest_cache/
.env
*.sqlite
outputs/*.md

Keep all implementation files minimal placeholders for now.
Do not implement the full app yet.
```

## Verification commands

```bash
pip install -e ".[dev]"
python -m pytest -q
python -c "import cvtailor_mcp, cvtailor_agent; print('imports ok')"
```

If `.[dev]` does not work because Copilot used a different dependency style, run:

```bash
pip install -e . pytest
```

## Expected result

```text
imports ok
1 passed
```

## Commit

```bash
git add .
git commit -m "phase 01 project scaffold"
```

---

# Phase 2 - Sample data and basic README

## Goal

Add sample candidate profile, resume, and job description so the app has local demo data.

## Copilot prompt

```text
Implement Phase 2 only.

Create realistic sample data files:

1. data/profile.json
2. data/resume.md
3. examples/job_description_ai_engineer.txt

The profile should represent an aspiring AI Engineer / Python Developer with skills:
- Python
- LangGraph
- LangChain
- MCP
- Hugging Face
- SQL
- FastAPI
- Docker
- GitHub Actions
- SQLite

The resume should include:
- summary
- skills
- projects
- experience
- education placeholder

Include a project called CVTailor MCP LangGraph Agent that mentions MCP, LangGraph, LangChain, Hugging Face, SQLite, CLI, and mock LLM mode.

The example job description should be for an AI Engineer role requiring Python, LLMs, APIs, databases, LangChain or LangGraph, and bonus MCP/Hugging Face/Docker.

Update README.md with a short placeholder overview, setup section, and target demo command.
Do not implement any app logic yet.
```

## Verification commands

```bash
python -m json.tool data/profile.json
head -n 20 data/resume.md
head -n 20 examples/job_description_ai_engineer.txt
python -m pytest -q
```

## Expected result

JSON validates. Resume and job description display readable text. Tests still pass.

## Commit

```bash
git add .
git commit -m "phase 02 add sample data"
```

---

# Phase 3 - Path helpers and schemas

## Goal

Add small shared helpers and data schemas before implementing logic.

## Copilot prompt

```text
Implement Phase 3 only.

Create or update src/cvtailor_mcp/schemas.py.

Add Pydantic models for:
- ResumeSearchResult
- SaveApplicationResult
- LogApplicationResult
- ApplicationRecord

Each model should use clear type hints.

Also add simple path constants or helper functions somewhere appropriate, either in schemas.py or a new small module if needed, for:
- PROJECT_ROOT
- DATA_DIR
- OUTPUTS_DIR
- PROFILE_PATH
- RESUME_PATH
- DATABASE_PATH

Path helpers must work when running commands from the project root.
Do not implement SQLite, resume search, MCP server, or LangGraph yet.
```

## Verification commands

```bash
python -c "from cvtailor_mcp.schemas import ResumeSearchResult; print(ResumeSearchResult(text='x', score=1.0))"
python -m pytest -q
```

## Expected result

The Pydantic model should print successfully. Tests still pass.

## Commit

```bash
git add .
git commit -m "phase 03 add schemas and paths"
```

---

# Phase 4 - Resume keyword search

## Goal

Implement a simple, deterministic resume search function. This should not use embeddings yet.

## Copilot prompt

```text
Implement Phase 4 only.

Implement src/cvtailor_mcp/resume_search.py.

Add functions:
- tokenize(text: str) -> set[str]
- split_resume_sections(resume_text: str) -> list[str]
- search_resume(query: str, resume_text: str, top_k: int = 5) -> list[dict]

Requirements:
- Split resume.md into paragraphs or logical sections.
- Lowercase text.
- Remove punctuation simply.
- Score each section by keyword overlap with the query.
- Return top_k results sorted by descending score.
- Each result should contain text and score.
- Ignore empty sections.
- Be deterministic and easy to test.

Add tests in tests/test_resume_search.py:
- search returns relevant result for query "Python LangGraph MCP"
- top_k is respected
- empty query returns empty list or safe result without crashing

Do not implement SQLite, MCP server, or LangGraph yet.
```

## Verification commands

```bash
python -m pytest tests/test_resume_search.py -q
python -m pytest -q
python -c "from pathlib import Path; from cvtailor_mcp.resume_search import search_resume; print(search_resume('Python LangGraph MCP', Path('data/resume.md').read_text(), 3))"
```

## Expected result

The printed search results should include resume text related to Python, LangGraph, or MCP.

## Commit

```bash
git add .
git commit -m "phase 04 implement resume search"
```

---

# Phase 5 - SQLite storage

## Goal

Implement application logging in SQLite.

## Copilot prompt

```text
Implement Phase 5 only.

Implement src/cvtailor_mcp/storage.py.

Add functions:
- init_db(db_path: str | Path | None = None) -> None
- log_application(company: str, role: str, status: str, notes: str = "", output_path: str = "", db_path: str | Path | None = None) -> dict
- list_applications(status: str | None = None, db_path: str | Path | None = None) -> list[dict]

SQLite table:
applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    role TEXT NOT NULL,
    status TEXT NOT NULL,
    notes TEXT,
    output_path TEXT,
    created_at TEXT NOT NULL
)

Requirements:
- Use sqlite3 from the standard library.
- Use ISO-style timestamp for created_at.
- Initialize the database automatically before logging/listing.
- Return dictionaries, not sqlite Row objects.
- Accept an optional db_path so tests can use a temporary database.

Add tests in tests/test_storage.py:
- logging creates a record
- listing returns the record
- filtering by status works
- temp database path is used in tests

Do not implement MCP server or LangGraph yet.
```

## Verification commands

```bash
python -m pytest tests/test_storage.py -q
python -m pytest -q
python -c "from cvtailor_mcp.storage import log_application, list_applications; print(log_application('Acme AI','AI Engineer','drafted')); print(list_applications())"
```

## Expected result

A record should be inserted and listed. A local SQLite database may appear under `data/`.

## Commit

```bash
git add .
git commit -m "phase 05 implement sqlite storage"
```

---

# Phase 6 - Tool functions without MCP wrapping

## Goal

Create clean tool functions that can be shared by the MCP server and the local client wrapper.

This phase intentionally avoids complex MCP client wiring. The app logic should call tool functions through a simple wrapper first. The MCP server will wrap the same functions in the next phase.

## Copilot prompt

```text
Implement Phase 6 only.

Implement src/cvtailor_mcp/tools.py as the shared tool layer.

Add functions:
- get_candidate_profile() -> dict
- search_resume_evidence(query: str, top_k: int = 5) -> list[dict]
- save_application_pack(company: str, role: str, content: str) -> dict
- log_application_tool(company: str, role: str, status: str, notes: str = "", output_path: str = "") -> dict
- list_applications_tool(status: str | None = None) -> list[dict]

Behavior:
- get_candidate_profile reads data/profile.json.
- search_resume_evidence reads data/resume.md and calls search_resume.
- save_application_pack creates outputs/ if needed and saves a Markdown file.
- Use safe slugs for filenames, for example acme-ai-ai-engineer-application-pack.md.
- log_application_tool calls storage.log_application.
- list_applications_tool calls storage.list_applications.

Add tests in tests/test_tools.py:
- profile loads
- search evidence returns list
- save application pack writes a file
- log/list application tools work

Keep functions simple and deterministic.
Do not implement the MCP server wrapper or LangGraph yet.
```

## Verification commands

```bash
python -m pytest tests/test_tools.py -q
python -m pytest -q
python -c "from cvtailor_mcp.tools import get_candidate_profile, search_resume_evidence; print(get_candidate_profile()['name']); print(search_resume_evidence('Python LangGraph MCP', 2))"
```

## Expected result

Profile loads. Resume evidence returns relevant snippets.

## Commit

```bash
git add .
git commit -m "phase 06 implement shared tool functions"
```

---

# Phase 7 - MCP server wrapper

## Goal

Expose the shared tool functions through an MCP server.

## Copilot prompt

```text
Implement Phase 7 only.

Implement src/cvtailor_mcp/server.py using the MCP Python SDK.

Use FastMCP if available from the installed MCP package.

Expose these tools:
- get_candidate_profile
- search_resume_evidence
- save_application_pack
- log_application
- list_applications

Each MCP tool should call the corresponding function from src/cvtailor_mcp/tools.py.

Requirements:
- Keep the server small.
- The shared tool functions must remain testable without MCP.
- Provide a main block so this works:
  python -m cvtailor_mcp.server
- The server may run over stdio and wait for an MCP client.
- Add a safe import smoke test in tests/test_mcp_server.py that verifies the server module imports and exposes a server object.

Do not implement LangGraph yet.
```

## Verification commands

```bash
python -m pytest tests/test_mcp_server.py -q
python -m pytest -q
python -c "import cvtailor_mcp.server; print('mcp server import ok')"
```

Optional manual smoke test:

```bash
python -m cvtailor_mcp.server
```

If the server starts and waits for input, stop it with Ctrl+C. That is acceptable for an MCP stdio server.

## Expected result

The server module imports successfully and tests pass.

## Commit

```bash
git add .
git commit -m "phase 07 expose mcp server"
```

---

# Phase 8 - Local MCP client wrapper for the agent

## Goal

Create a simple client wrapper that the agent can use. For the MVP, it may directly call shared tool functions. This keeps the workflow reliable and easy to test.

A later optional phase can replace direct calls with a true MCP stdio client.

## Copilot prompt

```text
Implement Phase 8 only.

Implement src/cvtailor_agent/mcp_client.py.

Create class MCPClient with methods:
- get_candidate_profile(self) -> dict
- search_resume_evidence(self, query: str, top_k: int = 5) -> list[dict]
- save_application_pack(self, company: str, role: str, content: str) -> dict
- log_application(self, company: str, role: str, status: str, notes: str = "", output_path: str = "") -> dict
- list_applications(self, status: str | None = None) -> list[dict]

For the MVP, these methods should call the shared functions in cvtailor_mcp.tools.

Important:
- Keep the class name MCPClient because the LangGraph workflow should depend on a client abstraction.
- Add comments explaining that this MVP wrapper calls shared MCP tool functions directly, while server.py exposes the same functions to real MCP clients.

Add tests in tests/test_mcp_client.py:
- client can load profile
- client can search resume evidence
- client can save an application pack

Do not implement LangGraph yet.
```

## Verification commands

```bash
python -m pytest tests/test_mcp_client.py -q
python -m pytest -q
python -c "from cvtailor_agent.mcp_client import MCPClient; c=MCPClient(); print(c.get_candidate_profile()['name'])"
```

## Expected result

The client wrapper can access the same capabilities as the MCP tools.

## Commit

```bash
git add .
git commit -m "phase 08 add mcp client wrapper"
```

---

# Phase 9 - Mock LLM and LangChain prompts

## Goal

Add deterministic mock LLM support and prompt templates. Do not call Hugging Face yet.

## Copilot prompt

```text
Implement Phase 9 only.

Implement src/cvtailor_agent/llm.py and src/cvtailor_agent/prompts.py.

In llm.py:
- Load environment variables using python-dotenv.
- Create a MockLLM class with invoke(prompt: str) -> str.
- MockLLM should return deterministic, useful text.
- get_llm() should read LLM_PROVIDER from environment.
- Default should be mock.
- If LLM_PROVIDER=mock, return MockLLM.
- If LLM_PROVIDER=huggingface, raise NotImplementedError for now. Hugging Face will be added in a later phase.

The MockLLM should handle four prompt types reasonably:
1. requirement extraction
2. draft generation
3. review
4. improvement

It can detect prompt content using simple keywords.

In prompts.py:
Use LangChain PromptTemplate from langchain_core.prompts.
Create:
- REQUIREMENT_EXTRACTION_PROMPT
- DRAFT_APPLICATION_PROMPT
- REVIEW_PROMPT
- IMPROVE_PROMPT

Add tests in tests/test_llm_mock.py:
- get_llm returns MockLLM by default
- MockLLM.invoke returns non-empty text
- prompt templates format successfully

Do not implement LangGraph yet.
```

## Verification commands

```bash
python -m pytest tests/test_llm_mock.py -q
python -m pytest -q
python -c "from cvtailor_agent.llm import get_llm; print(get_llm().invoke('Generate a draft application pack')[:300])"
```

## Expected result

Mock LLM returns useful deterministic text without any API key.

## Commit

```bash
git add .
git commit -m "phase 09 add mock llm and prompts"
```

---

# Phase 10 - LangGraph state and workflow skeleton

## Goal

Create the LangGraph workflow with nodes, but keep it simple and mock-LLM friendly.

## Copilot prompt

```text
Implement Phase 10 only.

Implement src/cvtailor_agent/state.py and src/cvtailor_agent/graph.py.

In state.py:
Create CVTailorState as a TypedDict with these fields:
- company: str
- role: str
- job_file: str
- job_description: optional str
- requirements: optional dict or str
- profile: optional dict
- evidence: optional list[dict]
- draft_application_pack: optional str
- review_feedback: optional str
- final_application_pack: optional str
- output_path: optional str
- application_id: optional int

In graph.py:
Implement LangGraph nodes:
1. load_job_description
2. extract_requirements_with_llm
3. get_candidate_profile_from_mcp
4. search_resume_evidence_from_mcp
5. generate_application_pack_with_llm
6. review_application_pack_with_llm
7. improve_application_pack_with_llm
8. save_application_pack_with_mcp
9. log_application_with_mcp

Graph flow:
START -> load_job_description -> extract_requirements_with_llm -> get_candidate_profile_from_mcp -> search_resume_evidence_from_mcp -> generate_application_pack_with_llm -> review_application_pack_with_llm -> improve_application_pack_with_llm -> save_application_pack_with_mcp -> log_application_with_mcp -> END

Create function build_graph() that returns the compiled LangGraph app.

Implementation requirements:
- Use get_llm() for LLM calls.
- Use MCPClient for tool calls.
- Use the LangChain PromptTemplate objects from prompts.py.
- In mock mode, the graph must run end-to-end without API keys.
- Make each node return updated state.
- Keep error handling simple but helpful.

Add tests in tests/test_graph.py:
- build_graph returns an invokable graph
- graph.invoke with the example job file creates final output
- result contains output_path and application_id

Do not implement CLI or Hugging Face yet.
```

## Verification commands

```bash
python -m pytest tests/test_graph.py -q
python -m pytest -q
python - <<'PY'
from cvtailor_agent.graph import build_graph
app = build_graph()
result = app.invoke({
    'job_file': 'examples/job_description_ai_engineer.txt',
    'company': 'Acme AI',
    'role': 'AI Engineer',
})
print(result.get('output_path'))
print(result.get('application_id'))
PY
```

## Expected result

The graph should create an output Markdown file and log an application.

## Commit

```bash
git add .
git commit -m "phase 10 implement langgraph workflow"
```

---

# Phase 11 - CLI commands

## Goal

Expose the app through user-friendly Typer CLI commands.

## Copilot prompt

```text
Implement Phase 11 only.

Implement src/cvtailor_agent/cli.py using Typer and Rich.

Commands:

1. run
Usage:
python -m cvtailor_agent.cli run --job-file examples/job_description_ai_engineer.txt --company "Acme AI" --role "AI Engineer"

Behavior:
- Builds the LangGraph workflow.
- Invokes it with job_file, company, and role.
- Prints progress messages.
- Prints final output path and application ID.

2. list-applications
Usage:
python -m cvtailor_agent.cli list-applications

Behavior:
- Uses MCPClient.list_applications.
- Displays records in a Rich table.

3. inspect-profile
Usage:
python -m cvtailor_agent.cli inspect-profile

Behavior:
- Uses MCPClient.get_candidate_profile.
- Prints profile as readable JSON or Rich output.

4. test-search
Usage:
python -m cvtailor_agent.cli test-search --query "Python LangGraph MCP"

Behavior:
- Uses MCPClient.search_resume_evidence.
- Prints matching snippets and scores.

Add tests if practical, but avoid brittle CLI tests if they slow down the phase.
Do not implement Hugging Face yet.
```

## Verification commands

```bash
python -m cvtailor_agent.cli inspect-profile
python -m cvtailor_agent.cli test-search --query "Python LangGraph MCP"
python -m cvtailor_agent.cli run --job-file examples/job_description_ai_engineer.txt --company "Acme AI" --role "AI Engineer"
python -m cvtailor_agent.cli list-applications
python -m pytest -q
```

## Expected result

The CLI should run end-to-end in mock mode and print the output path plus application ID.

## Commit

```bash
git add .
git commit -m "phase 11 add cli commands"
```

---

# Phase 12 - Hugging Face LLM mode

## Goal

Add real LLM calls through LangChain and Hugging Face while keeping mock mode as the default.

## Copilot prompt

```text
Implement Phase 12 only.

Update src/cvtailor_agent/llm.py to support Hugging Face mode.

Requirements:
- Keep mock mode as the default.
- If LLM_PROVIDER=mock, no API key should be needed.
- If LLM_PROVIDER=huggingface, read:
  - HF_TOKEN
  - HF_MODEL
  - TEMPERATURE
  - MAX_NEW_TOKENS
- Use langchain-huggingface.
- Prefer HuggingFaceEndpoint if available.
- Return an object with invoke(prompt) support.
- Raise a clear error if HF_TOKEN is missing.
- Do not print or log the token.

Example .env:
LLM_PROVIDER=huggingface
HF_TOKEN=your_token_here
HF_MODEL=mistralai/Mistral-7B-Instruct-v0.3
TEMPERATURE=0.2
MAX_NEW_TOKENS=900

Add tests that do not call the real Hugging Face API:
- mock mode still works
- huggingface mode without HF_TOKEN raises a clear error

Update README with Hugging Face setup instructions.
```

## Verification commands

Mock mode should still work:

```bash
unset LLM_PROVIDER || true
python -m cvtailor_agent.cli run --job-file examples/job_description_ai_engineer.txt --company "Acme AI" --role "AI Engineer"
python -m pytest -q
```

Test missing token behavior:

```bash
LLM_PROVIDER=huggingface HF_TOKEN= python - <<'PY'
from cvtailor_agent.llm import get_llm
try:
    get_llm()
except Exception as exc:
    print(type(exc).__name__)
    print(str(exc))
PY
```

Optional real Hugging Face test after creating `.env` with your token:

```bash
python -m cvtailor_agent.cli run --job-file examples/job_description_ai_engineer.txt --company "Acme AI" --role "AI Engineer"
```

## Expected result

Mock mode still works. Hugging Face mode gives a clear missing-token error unless configured.

## Commit

```bash
git add .
git commit -m "phase 12 add hugging face llm mode"
```

---

# Phase 13 - Output quality and formatter polish

## Goal

Make sure the generated Markdown output looks professional and CV-demo ready.

## Copilot prompt

```text
Implement Phase 13 only.

Improve output quality without changing the architecture.

Use src/cvtailor_agent/output_formatter.py if helpful.

Requirements:
- Ensure final_application_pack is valid Markdown.
- Ensure it contains these sections:
  # Application Pack: {role} at {company}
  ## Job Requirement Summary
  ## Candidate Match Score
  ## Matched Skills Table
  ## Tailored Resume Summary
  ## Tailored Resume Bullets
  ## Short Cover Letter
  ## Gap Analysis
  ## Next Actions
- If the LLM output is missing a section in mock mode, add a simple fallback section.
- Keep claims grounded in profile and resume evidence.
- Do not invent fake metrics.
- Make filenames safe and predictable.

Update tests to assert the generated Markdown contains the required section headings.
```

## Verification commands

```bash
python -m cvtailor_agent.cli run --job-file examples/job_description_ai_engineer.txt --company "Acme AI" --role "AI Engineer"
ls -la outputs
python - <<'PY'
from pathlib import Path
files = sorted(Path('outputs').glob('*.md'))
latest = files[-1]
print(latest)
print(latest.read_text(encoding='utf-8')[:1500])
PY
python -m pytest -q
```

## Expected result

The Markdown file should be readable and contain all required sections.

## Commit

```bash
git add .
git commit -m "phase 13 polish markdown output"
```

---

# Phase 14 - README and demo documentation

## Goal

Create a strong GitHub README that explains the project clearly.

## Copilot prompt

```text
Implement Phase 14 only.

Rewrite README.md into a polished portfolio README.

Include:

1. Project title
2. One-sentence summary
3. What the project demonstrates
4. Architecture diagram in text form
5. Tech stack
6. How MCP is used
7. How LangGraph is used
8. How LangChain is used
9. How Hugging Face is used
10. Why mock mode exists
11. Setup instructions
12. Example commands
13. Example input
14. Example output
15. Testing instructions
16. Project structure
17. CV bullet points
18. Future improvements

Add this architecture diagram or a similar text diagram:

User CLI
  -> LangGraph Agent Workflow
  -> LangChain Prompt Templates
  -> Mock or Hugging Face LLM
  -> MCP Client Wrapper
  -> MCP Tool Functions / MCP Server
  -> Local Data: profile.json, resume.md, SQLite, outputs

Add CV bullets:
- Built an MCP-powered AI job application assistant using Python, LangGraph, LangChain, Hugging Face, and SQLite.
- Designed a graph-based agent workflow for job requirement extraction, resume evidence retrieval, draft generation, self-review, final improvement, saving, and logging.
- Implemented a local MCP tool layer for profile lookup, resume search, Markdown output generation, and job application tracking.

Do not change core code unless README commands reveal a bug.
```

## Verification commands

```bash
python -m pytest -q
python -m cvtailor_agent.cli inspect-profile
python -m cvtailor_agent.cli test-search --query "Python LangGraph MCP"
python -m cvtailor_agent.cli run --job-file examples/job_description_ai_engineer.txt --company "Acme AI" --role "AI Engineer"
python -m cvtailor_agent.cli list-applications
```

## Expected result

README commands should match actual behavior.

## Commit

```bash
git add .
git commit -m "phase 14 write portfolio readme"
```

---

# Phase 15 - Final cleanup and GitHub readiness

## Goal

Make the repo clean before pushing to GitHub.

## Copilot prompt

```text
Implement Phase 15 only.

Do final cleanup for GitHub readiness.

Tasks:
- Review .gitignore and ensure .env, .venv, __pycache__, .pytest_cache, data/*.sqlite, and generated outputs/*.md are ignored.
- Keep outputs/.gitkeep tracked.
- Keep data/profile.json and data/resume.md tracked as sample data.
- Ensure no secrets are committed.
- Ensure tests pass.
- Add helpful comments where useful, but do not over-comment.
- Remove dead placeholder code.
- Make error messages clear.
- Ensure pyproject.toml metadata is clean.
- Ensure README setup instructions are accurate.

Do not add major new features.
```

## Verification commands

```bash
git status
python -m pytest -q
python -m cvtailor_agent.cli run --job-file examples/job_description_ai_engineer.txt --company "Acme AI" --role "AI Engineer"
git status
```

Review ignored files:

```bash
git status --ignored
```

## Expected result

Tests pass. No secrets are tracked. Generated SQLite/output files should be ignored unless you intentionally keep a sample output.

## Commit

```bash
git add .
git commit -m "phase 15 final cleanup"
```

---

# Optional Phase 16 - True MCP stdio client integration

## Goal

Replace or supplement the direct tool-function wrapper with a real MCP stdio client connection.

This is optional. The MVP already demonstrates an MCP server and an agent workflow. Do this only after everything else works.

## Copilot prompt

```text
Implement optional Phase 16 only.

Add an optional real MCP stdio client path to src/cvtailor_agent/mcp_client.py.

Requirements:
- Keep the existing direct mode as the default because it is reliable for tests and demos.
- Add an environment variable, for example MCP_CLIENT_MODE=direct or MCP_CLIENT_MODE=stdio.
- If MCP_CLIENT_MODE=direct, use the existing shared tool-function calls.
- If MCP_CLIENT_MODE=stdio, connect to the MCP server using the MCP Python SDK stdio client APIs.
- The stdio client should start or connect to python -m cvtailor_mcp.server.
- Keep the public MCPClient methods unchanged.
- Add clear README documentation.
- Add tests for direct mode only. Do not make CI depend on stdio MCP if it is fragile.

Do not break the existing CLI behavior.
```

## Verification commands

Default direct mode:

```bash
python -m pytest -q
python -m cvtailor_agent.cli run --job-file examples/job_description_ai_engineer.txt --company "Acme AI" --role "AI Engineer"
```

Optional stdio mode, only if implemented successfully:

```bash
MCP_CLIENT_MODE=stdio python -m cvtailor_agent.cli inspect-profile
```

## Expected result

Direct mode still works. Stdio mode works if implemented, but it should not be required for the main demo.

## Commit

```bash
git add .
git commit -m "phase 16 optional mcp stdio client"
```

---

# Optional Phase 17 - Docker and GitHub Actions

## Goal

Add professional polish for your CV and GitHub repo.

## Copilot prompt

```text
Implement optional Phase 17 only.

Add:
1. Dockerfile
2. .dockerignore
3. GitHub Actions workflow for tests

Dockerfile requirements:
- Python 3.11 or 3.12 slim image
- Install project dependencies
- Copy source code
- Default command should show CLI help or run tests

GitHub Actions:
- Run on push and pull request
- Set up Python
- Install dependencies
- Run pytest

Update README with Docker and CI badge/instructions if appropriate.
Do not change core app behavior.
```

## Verification commands

```bash
python -m pytest -q
```

Optional Docker test:

```bash
docker build -t cvtailor-mcp-langgraph-agent .
docker run --rm cvtailor-mcp-langgraph-agent
```

## Commit

```bash
git add .
git commit -m "phase 17 add docker and ci"
```

---

# Troubleshooting prompts for Copilot

Use these when something breaks.

## Fix only the current phase

```text
The verification command for the current phase failed.
Do not add new features.
Fix only the files related to the current phase.
Here is the error:

PASTE ERROR HERE
```

## Fix import/package issues

```text
The project has import or packaging errors.
Fix pyproject.toml and package imports so that:
- pip install -e . works
- python -c "import cvtailor_mcp, cvtailor_agent" works
- python -m pytest -q works
Do not change app behavior.
```

## Fix CLI issues

```text
The CLI command failed.
Fix only src/cvtailor_agent/cli.py or the directly related workflow function.
The command should work:
python -m cvtailor_agent.cli run --job-file examples/job_description_ai_engineer.txt --company "Acme AI" --role "AI Engineer"

Here is the error:

PASTE ERROR HERE
```

## Fix LangGraph issues

```text
The LangGraph workflow failed.
Fix only src/cvtailor_agent/graph.py, state.py, or directly related prompt/LLM code.
Keep mock mode working without API keys.
Here is the error:

PASTE ERROR HERE
```

## Fix Hugging Face issues

```text
Hugging Face mode failed.
Keep mock mode unchanged and working.
Fix only the Hugging Face branch in src/cvtailor_agent/llm.py.
Do not expose or print HF_TOKEN.
Here is the error:

PASTE ERROR HERE
```

---

# Minimal acceptance checklist

The project is ready for GitHub/CV when these commands work:

```bash
python -m pytest -q
python -m cvtailor_agent.cli inspect-profile
python -m cvtailor_agent.cli test-search --query "Python LangGraph MCP"
python -m cvtailor_agent.cli run --job-file examples/job_description_ai_engineer.txt --company "Acme AI" --role "AI Engineer"
python -m cvtailor_agent.cli list-applications
```

The README should clearly say:

```text
This project demonstrates MCP, LangGraph, LangChain, Hugging Face LLM calls, mock LLM mode, SQLite tracking, and a CLI workflow.
```

---

# Final CV bullets

Use these after the project works:

```text
CVTailor MCP LangGraph Agent
Built an MCP-powered AI job application assistant using Python, LangGraph, LangChain, Hugging Face, and SQLite.

Designed a graph-based agent workflow for job requirement extraction, resume evidence retrieval, draft generation, self-review, final improvement, Markdown saving, and application logging.

Implemented a local MCP tool layer for candidate profile lookup, resume search, generated application-pack storage, and SQLite-backed job tracking, with mock LLM mode for reproducible demos.
```
