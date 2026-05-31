# CVTailor MCP LangGraph Agent — Nice-to-Haves Phased Implementation Plan

## Purpose

This plan extends the existing CVTailor MCP LangGraph Agent project with three nice-to-have features, implemented in priority order.

Priority order:

1. Conditional LangGraph routing
2. Real MCP stdio client integration
3. Hybrid resume search

Important rule:

Implement one phase at a time. After each phase, stop. Do not move to the next phase until I run the verification commands and approve.

---

# Existing project assumptions

The base MVP already has or will have:

- Python 3.11+
- MCP server package: `src/cvtailor_mcp/`
- Agent package: `src/cvtailor_agent/`
- LangGraph workflow in `src/cvtailor_agent/graph.py`
- State definition in `src/cvtailor_agent/state.py`
- MCP client wrapper in `src/cvtailor_agent/mcp_client.py`
- MCP tool logic in `src/cvtailor_mcp/tools.py`
- Resume search in `src/cvtailor_mcp/resume_search.py`
- SQLite storage in `src/cvtailor_mcp/storage.py`
- LLM abstraction in `src/cvtailor_agent/llm.py`
- Prompt templates in `src/cvtailor_agent/prompts.py`
- CLI in `src/cvtailor_agent/cli.py`
- Tests in `tests/`

The current app can run in mock mode using:

    python -m cvtailor_agent.cli run \
      --job-file examples/job_description_ai_engineer.txt \
      --company "Acme AI" \
      --role "AI Engineer"

Do not rewrite the whole project. Extend the existing implementation safely.

---

# Global implementation rules

Follow these rules for every phase:

1. Keep mock mode working.
2. Do not require real Hugging Face calls for tests.
3. Do not require real MCP stdio mode for basic local execution.
4. Keep direct mode available for easier testing.
5. Add or update tests for each phase.
6. Use type hints.
7. Avoid over-engineering.
8. Keep the CLI stable.
9. Keep the README honest about what is implemented.
10. Do not commit secrets or tokens.

After each phase, run:

    python -m pytest -q

If the project has formatting/linting configured, also run the existing format/lint commands.

---

# Priority 1: Conditional LangGraph Routing

Goal:

Make the LangGraph workflow more than a linear pipeline by adding real conditional routing.

The graph should support:

- evidence quality scoring
- weak-evidence fallback path
- broadened search query generation
- LLM-based draft review classification
- bounded revision loop
- maximum revision limit to avoid infinite loops

Final target workflow:

    START
      ↓
    load_job_description
      ↓
    extract_requirements_with_llm
      ↓
    get_candidate_profile_from_mcp
      ↓
    search_resume_evidence_from_mcp
      ↓
    score_resume_evidence
      ↓
    conditional:
      strong evidence → generate_application_pack_with_llm
      weak evidence   → broaden_search_query
                          ↓
                        search_resume_evidence_again
                          ↓
                        generate_application_pack_with_llm
      ↓
    review_application_pack_with_llm
      ↓
    classify_review_result
      ↓
    conditional:
      approved       → save_application_pack_with_mcp
      needs revision → improve_application_pack_with_llm
                         ↓
                       review_application_pack_with_llm
      ↓
    save_application_pack_with_mcp
      ↓
    log_application_with_mcp
      ↓
    END

---

## Phase 1 — Extend LangGraph state for conditional routing

### Copilot task

Implement Phase 1 only.

Update the LangGraph state so the workflow can support conditional routing, evidence scoring, broadened search, and bounded revision loops.

Do not modify the graph routing yet. Only update the state model and any initialization defaults required so the existing workflow still runs.

### Files to inspect

- `src/cvtailor_agent/state.py`
- `src/cvtailor_agent/graph.py`
- `src/cvtailor_agent/cli.py`
- existing tests

### Required changes

Add state fields such as:

- `evidence_score`
- `evidence_quality`
- `search_attempts`
- `max_search_attempts`
- `expanded_search_query`
- `review_status`
- `revision_count`
- `max_revisions`
- `route_reason`

Use safe defaults.

Recommended defaults:

    evidence_score = 0.0
    evidence_quality = "unknown"
    search_attempts = 0
    max_search_attempts = 2
    expanded_search_query = ""
    review_status = "unknown"
    revision_count = 0
    max_revisions = 2
    route_reason = ""

If the state uses `TypedDict`, use `NotRequired` where appropriate.

If the state uses Pydantic, add optional fields with defaults.

Make sure the existing graph still works exactly as before.

### Verification commands

    python -m pytest -q

Then run the existing CLI command:

    python -m cvtailor_agent.cli run \
      --job-file examples/job_description_ai_engineer.txt \
      --company "Acme AI" \
      --role "AI Engineer"

### Expected result

- Tests pass.
- CLI still runs.
- No conditional routing yet.
- No behavior regression.

### Git commit

    git add .
    git commit -m "phase 01 extend graph state for conditional routing"

Stop after this phase.

---

## Phase 2 — Add evidence scoring node

### Copilot task

Implement Phase 2 only.

Add a LangGraph node that scores the quality of resume evidence returned by the resume search step.

Do not add conditional edges yet. Just calculate and store the score.

### Files to inspect

- `src/cvtailor_agent/graph.py`
- `src/cvtailor_agent/state.py`
- `tests/test_graph.py`

### Required behavior

Create a function such as:

    score_resume_evidence(state) -> state

It should inspect `state["evidence"]`.

Expected evidence items may look like:

    {
      "text": "...",
      "score": 0.75,
      "matched_keywords": ["python", "langgraph"]
    }

Calculate:

- average evidence score
- evidence quality label

Suggested logic:

    if no evidence:
        evidence_score = 0.0
        evidence_quality = "weak"

    elif average score >= 0.50:
        evidence_quality = "strong"

    else:
        evidence_quality = "weak"

Store:

- `evidence_score`
- `evidence_quality`
- `route_reason`

Add this node into the graph after:

    search_resume_evidence_from_mcp

But for this phase, route it linearly to the existing next node.

Current flow should become:

    search_resume_evidence_from_mcp
      ↓
    score_resume_evidence
      ↓
    generate_application_pack_with_llm

### Tests

Add tests for:

- no evidence gives weak quality
- high-score evidence gives strong quality
- low-score evidence gives weak quality

### Verification commands

    python -m pytest -q

Run:

    python -m cvtailor_agent.cli run \
      --job-file examples/job_description_ai_engineer.txt \
      --company "Acme AI" \
      --role "AI Engineer"

### Expected result

- Existing workflow still works.
- State now contains evidence score and quality.
- No conditional routing yet.

### Git commit

    git add .
    git commit -m "phase 02 add resume evidence scoring node"

Stop after this phase.

---

## Phase 3 — Add conditional routing after evidence scoring

### Copilot task

Implement Phase 3 only.

Use LangGraph conditional edges after the evidence scoring node.

If evidence is strong, continue normally.

If evidence is weak, route to a fallback search query node.

### Files to inspect

- `src/cvtailor_agent/graph.py`
- `src/cvtailor_agent/state.py`
- `src/cvtailor_agent/prompts.py`
- `tests/test_graph.py`

### Required graph change

Add a router function such as:

    route_after_evidence_scoring(state) -> str

Suggested behavior:

    if state["evidence_quality"] == "strong":
        return "strong_match"

    if state["search_attempts"] >= state["max_search_attempts"]:
        return "continue_anyway"

    return "weak_match"

Add conditional edges:

    graph.add_conditional_edges(
        "score_resume_evidence",
        route_after_evidence_scoring,
        {
            "strong_match": "generate_application_pack",
            "continue_anyway": "generate_application_pack",
            "weak_match": "broaden_search_query",
        },
    )

### Add fallback node

Create:

    broaden_search_query(state) -> state

For mock mode, this can be deterministic.

It should create a broader search query using:

- role
- requirements
- candidate skills if available
- important terms from job description

Store the result in:

    state["expanded_search_query"]

Increment:

    state["search_attempts"]

Then route:

    broaden_search_query
      ↓
    search_resume_evidence_again
      ↓
    score_resume_evidence

Create a second search node if cleaner:

    search_resume_evidence_again

It should use `expanded_search_query` if present.

Important:

Avoid infinite loops using `search_attempts` and `max_search_attempts`.

### Tests

Add tests for:

- strong evidence routes to generation
- weak evidence routes to broadened search
- max search attempts routes to generation anyway

### Verification commands

    python -m pytest -q

Run:

    python -m cvtailor_agent.cli run \
      --job-file examples/job_description_ai_engineer.txt \
      --company "Acme AI" \
      --role "AI Engineer"

### Expected result

- Graph now has a real conditional branch.
- Weak resume evidence triggers fallback search.
- Strong evidence continues normally.
- No infinite loop possible.

### Git commit

    git add .
    git commit -m "phase 03 add conditional evidence routing"

Stop after this phase.

---

## Phase 4 — Add LLM review classification

### Copilot task

Implement Phase 4 only.

The app already has a review step. Extend it so the review result includes a clear classification:

- `approved`
- `needs_revision`

Do not add the revision loop yet. Only classify the review.

### Files to inspect

- `src/cvtailor_agent/prompts.py`
- `src/cvtailor_agent/graph.py`
- `src/cvtailor_agent/llm.py`
- `tests/test_graph.py`
- `tests/test_llm_mock.py`

### Required behavior

Update the review prompt so it asks for a structured response.

Preferred format:

    REVIEW_STATUS: approved
    FEEDBACK:
    ...

or:

    REVIEW_STATUS: needs_revision
    FEEDBACK:
    ...

Implement a parser function such as:

    parse_review_response(response: str) -> tuple[str, str]

Rules:

- If response contains `REVIEW_STATUS: approved`, status is `approved`.
- If response contains `REVIEW_STATUS: needs_revision`, status is `needs_revision`.
- If parsing fails, default to `needs_revision`.

Store:

- `review_status`
- `review_feedback`

Update MockLLM so the mock review response is deterministic and testable.

### Tests

Add tests for:

- parser returns approved
- parser returns needs_revision
- parser fallback defaults to needs_revision

### Verification commands

    python -m pytest -q

Run:

    python -m cvtailor_agent.cli run \
      --job-file examples/job_description_ai_engineer.txt \
      --company "Acme AI" \
      --role "AI Engineer"

### Expected result

- Review step now produces a machine-readable status.
- No revision loop yet.
- Workflow still completes.

### Git commit

    git add .
    git commit -m "phase 04 add review classification"

Stop after this phase.

---

## Phase 5 — Add bounded revision loop

### Copilot task

Implement Phase 5 only.

Use LangGraph conditional edges after review classification.

If the review is approved, save the output.

If the review needs revision, improve the draft and review again.

Use a maximum revision limit to prevent infinite loops.

### Files to inspect

- `src/cvtailor_agent/graph.py`
- `src/cvtailor_agent/state.py`
- `tests/test_graph.py`

### Required graph behavior

Add a router function such as:

    route_after_review(state) -> str

Suggested logic:

    if state["review_status"] == "approved":
        return "approved"

    if state["revision_count"] >= state["max_revisions"]:
        return "max_revisions_reached"

    return "needs_revision"

Add conditional edges:

    graph.add_conditional_edges(
        "review_application_pack",
        route_after_review,
        {
            "approved": "save_application_pack",
            "max_revisions_reached": "save_application_pack",
            "needs_revision": "improve_application_pack",
        },
    )

Then:

    improve_application_pack
      ↓
    review_application_pack

Update the improve node so it increments:

    revision_count += 1

Make sure the final output is saved whether approved or max revisions reached.

### Tests

Add tests for:

- approved review routes to save
- needs revision routes to improve
- max revisions routes to save
- revision count increments
- graph does not loop forever

### Verification commands

    python -m pytest -q

Run:

    python -m cvtailor_agent.cli run \
      --job-file examples/job_description_ai_engineer.txt \
      --company "Acme AI" \
      --role "AI Engineer"

### Expected result

- The graph now has a real conditional revision loop.
- The loop is bounded.
- The CLI still produces an output file.
- The application still gets logged.

### Git commit

    git add .
    git commit -m "phase 05 add bounded LangGraph revision loop"

Stop after this phase.

---

## Phase 6 — Update CLI and README to show conditional graph behavior

### Copilot task

Implement Phase 6 only.

Add small logging or console output so users can see the conditional workflow decisions.

Do not add a complex UI.

### Files to inspect

- `src/cvtailor_agent/cli.py`
- `src/cvtailor_agent/graph.py`
- `README.md`

### Required behavior

When the workflow completes, print useful information such as:

- evidence score
- evidence quality
- search attempts
- review status
- revision count
- output path
- application ID

Example terminal output:

    Application pack generated successfully.

    Evidence quality: strong
    Evidence score: 0.72
    Search attempts: 1
    Review status: approved
    Revision count: 0
    Output path: outputs/acme-ai-ai-engineer-application-pack.md
    Application ID: 1

Update README with a section:

    Conditional LangGraph Workflow

Include a text diagram showing:

    score evidence → route strong/weak
    review draft → approve/revise loop

### Verification commands

    python -m pytest -q

Run:

    python -m cvtailor_agent.cli run \
      --job-file examples/job_description_ai_engineer.txt \
      --company "Acme AI" \
      --role "AI Engineer"

### Expected result

- User can clearly see LangGraph decisions.
- README explains why LangGraph is useful.

### Git commit

    git add .
    git commit -m "phase 06 document conditional LangGraph workflow"

Stop after this phase.

---

# Priority 2: Real MCP stdio Client Integration

Goal:

The MVP may currently call shared tool functions directly through `MCPClient`.

This upgrade adds real MCP protocol communication over stdio.

The project should support both modes:

    MCP_CLIENT_MODE=direct

and:

    MCP_CLIENT_MODE=stdio

Direct mode remains the default for testing and simplicity.

Stdio mode proves real MCP integration:

    LangGraph
      ↓
    MCP stdio client
      ↓
    MCP server process
      ↓
    MCP tools
      ↓
    shared tool functions

---

## Phase 7 — Add MCP client mode configuration

### Copilot task

Implement Phase 7 only.

Add configuration support for choosing between direct mode and stdio mode.

Do not implement real stdio communication yet.

### Files to inspect

- `src/cvtailor_agent/mcp_client.py`
- `.env.example`
- `README.md`
- tests

### Required changes

Update `.env.example`:

    MCP_CLIENT_MODE=direct
    MCP_SERVER_COMMAND=python
    MCP_SERVER_ARGS=-m cvtailor_mcp.server

Update `MCPClient` so it reads:

- `MCP_CLIENT_MODE`
- default is `direct`

Suggested structure:

    class MCPClient:
        def __init__(self, mode: str | None = None):
            self.mode = mode or os.getenv("MCP_CLIENT_MODE", "direct")

Methods still work in direct mode:

- `get_candidate_profile`
- `search_resume_evidence`
- `save_application_pack`
- `log_application`
- `list_applications`

If mode is `stdio`, temporarily raise:

    NotImplementedError("stdio MCP client mode will be implemented in a later phase")

### Tests

Add tests for:

- default mode is direct
- direct mode methods still work
- stdio mode raises NotImplementedError for now

### Verification commands

    python -m pytest -q

Run:

    python -m cvtailor_agent.cli run \
      --job-file examples/job_description_ai_engineer.txt \
      --company "Acme AI" \
      --role "AI Engineer"

### Expected result

- No behavior regression.
- Direct mode works.
- Stdio mode config exists but is not implemented yet.

### Git commit

    git add .
    git commit -m "phase 07 add MCP client mode configuration"

Stop after this phase.

---

## Phase 8 — Implement low-level MCP stdio tool call helper

### Copilot task

Implement Phase 8 only.

Implement a low-level helper that can start the MCP server over stdio and call one MCP tool by name.

Do not wire all `MCPClient` methods yet.

### Files to inspect

- `src/cvtailor_agent/mcp_client.py`
- `src/cvtailor_mcp/server.py`
- tests

### Required behavior

Use the MCP Python SDK.

Expected MCP SDK pattern may look like this:

    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    server_params = StdioServerParameters(
        command="python",
        args=["-m", "cvtailor_mcp.server"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("tool_name", arguments={...})

The exact API may differ depending on the installed MCP version. Inspect the installed SDK and adapt.

Create a helper such as:

    async def call_mcp_tool_stdio_async(tool_name: str, arguments: dict) -> Any:
        ...

and a sync wrapper:

    def call_mcp_tool_stdio(tool_name: str, arguments: dict) -> Any:
        return asyncio.run(call_mcp_tool_stdio_async(tool_name, arguments))

For this project, it is acceptable if each tool call starts a new MCP server process. Keep it simple. Do not over-engineer persistent sessions yet.

### Tool response parsing

MCP tool results may return text content or structured content.

Create a robust parser that:

- returns dict/list if JSON text is returned
- returns plain text if plain text is returned
- handles common MCP result content shapes
- raises helpful errors if parsing fails

### Tests

Add a small integration-style test that can call one simple tool through stdio, preferably:

    get_candidate_profile

If this is too slow or brittle, mark it separately or skip unless an environment variable is set:

    RUN_MCP_STDIO_TESTS=1

But still implement the code.

### Verification commands

First run normal tests:

    python -m pytest -q

Then manually test the server can start:

    python -m cvtailor_mcp.server

If the server waits for stdio input and does not print much, that is okay.

If an integration test is added behind an env variable:

    RUN_MCP_STDIO_TESTS=1 python -m pytest -q

### Expected result

- Low-level stdio call helper exists.
- At least one MCP tool can be called through real MCP stdio mode.
- Direct mode remains unaffected.

### Git commit

    git add .
    git commit -m "phase 08 implement low-level MCP stdio tool calls"

Stop after this phase.

---

## Phase 9 — Wire MCPClient methods to stdio mode

### Copilot task

Implement Phase 9 only.

Update `MCPClient` so when `MCP_CLIENT_MODE=stdio`, its methods call the real MCP server through stdio.

### Files to inspect

- `src/cvtailor_agent/mcp_client.py`
- `src/cvtailor_mcp/server.py`
- `src/cvtailor_mcp/tools.py`
- tests

### Required behavior

These methods should work in both direct and stdio modes:

- `get_candidate_profile()`
- `search_resume_evidence(query, top_k)`
- `save_application_pack(company, role, content)`
- `log_application(company, role, status, notes, output_path)`
- `list_applications(status=None)`

Direct mode:

    calls shared Python functions directly

Stdio mode:

    calls MCP server over stdio using call_mcp_tool_stdio

Make sure outputs have the same shape in both modes.

Example:

    direct_result == stdio_result

or at least the same important keys exist.

### Tests

Add tests for direct mode.

Add optional stdio integration tests behind:

    RUN_MCP_STDIO_TESTS=1

Test at least:

- get profile
- search resume evidence
- list applications

Avoid tests that create too many duplicate database records unless using a temp DB.

### Verification commands

Normal tests:

    python -m pytest -q

Direct mode CLI:

    MCP_CLIENT_MODE=direct python -m cvtailor_agent.cli run \
      --job-file examples/job_description_ai_engineer.txt \
      --company "Acme AI" \
      --role "AI Engineer"

Stdio mode CLI:

    MCP_CLIENT_MODE=stdio python -m cvtailor_agent.cli run \
      --job-file examples/job_description_ai_engineer.txt \
      --company "Acme AI" \
      --role "AI Engineer"

Optional stdio tests:

    RUN_MCP_STDIO_TESTS=1 python -m pytest -q

### Expected result

- Direct mode works.
- Stdio mode works.
- LangGraph can call MCP tools through the real MCP server when configured.

### Git commit

    git add .
    git commit -m "phase 09 wire MCP client to stdio mode"

Stop after this phase.

---

## Phase 10 — Document real MCP usage

### Copilot task

Implement Phase 10 only.

Update README to clearly explain the two MCP client modes.

### Files to inspect

- `README.md`
- `.env.example`

### Required README sections

Add:

    MCP Client Modes

Explain:

Direct mode:

    LangGraph → MCPClient → shared tool functions

Stdio mode:

    LangGraph → MCPClient → MCP server over stdio → MCP tools → shared tool functions

Add commands:

    MCP_CLIENT_MODE=direct python -m cvtailor_agent.cli run \
      --job-file examples/job_description_ai_engineer.txt \
      --company "Acme AI" \
      --role "AI Engineer"

    MCP_CLIENT_MODE=stdio python -m cvtailor_agent.cli run \
      --job-file examples/job_description_ai_engineer.txt \
      --company "Acme AI" \
      --role "AI Engineer"

Add honest wording:

    Direct mode is useful for tests and local development.
    Stdio mode demonstrates real MCP protocol communication.

### Verification commands

    python -m pytest -q

### Expected result

README clearly explains why MCP is used and how to run real MCP mode.

### Git commit

    git add .
    git commit -m "phase 10 document real MCP stdio mode"

Stop after this phase.

---

# Priority 3: Hybrid Resume Search

Goal:

Upgrade resume search from simple keyword overlap to hybrid search.

Hybrid search means:

    final score = keyword score + semantic/vector score

This helps the app find relevant resume evidence even when the job description uses different wording.

Example:

    Query: "agent orchestration"
    Resume: "Designed a LangGraph workflow"

Keyword search may miss this.

Semantic search should find it.

Recommended stack:

- `sentence-transformers`
- `faiss-cpu`
- `numpy`

But keep a fallback so tests do not require model downloads.

---

## Phase 11 — Add search mode configuration and interfaces

### Copilot task

Implement Phase 11 only.

Add configuration for resume search modes.

Do not implement embeddings yet.

### Files to inspect

- `src/cvtailor_mcp/resume_search.py`
- `src/cvtailor_mcp/tools.py`
- `.env.example`
- tests

### Required configuration

Update `.env.example`:

    RESUME_SEARCH_MODE=keyword
    EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
    HYBRID_KEYWORD_WEIGHT=0.4
    HYBRID_SEMANTIC_WEIGHT=0.6

Supported modes:

- `keyword`
- `hybrid`

Default:

    keyword

Add a clean public function such as:

    search_resume(
        query: str,
        resume_text: str,
        top_k: int = 5,
        mode: str | None = None,
    ) -> list[dict]

For now:

- `keyword` mode uses existing search
- `hybrid` mode can temporarily fall back to keyword and include a TODO or placeholder

Do not break existing behavior.

### Tests

Add tests for:

- default search mode is keyword
- explicit keyword mode works
- hybrid mode currently falls back safely or raises a clear NotImplementedError depending on your design

Prefer safe fallback for this phase.

### Verification commands

    python -m pytest -q

Run:

    python -m cvtailor_agent.cli test-search --query "Python LangGraph MCP"

### Expected result

- Existing keyword search still works.
- Config is ready for hybrid search.
- No model downloads required yet.

### Git commit

    git add .
    git commit -m "phase 11 add resume search mode configuration"

Stop after this phase.

---

## Phase 12 — Implement semantic embedding backend

### Copilot task

Implement Phase 12 only.

Add a semantic embedding backend for resume chunks.

Keep tests offline-friendly by supporting a mock embedding backend.

### Files to inspect

- `src/cvtailor_mcp/resume_search.py`
- `pyproject.toml`
- tests

### Dependencies

Add optional or normal dependencies:

    sentence-transformers
    numpy

If using FAISS in this phase, also add:

    faiss-cpu

If FAISS causes environment issues, implement cosine similarity with NumPy first and use FAISS in the next phase.

### Required implementation

Add functions such as:

    chunk_resume(resume_text: str) -> list[str]

    get_embedding_model(model_name: str | None = None):
        ...

    embed_texts(texts: list[str]) -> np.ndarray:
        ...

    semantic_search(
        query: str,
        resume_text: str,
        top_k: int = 5,
        embedding_backend: str = "sentence_transformers",
    ) -> list[dict]

Support a mock backend for tests:

    EMBEDDING_BACKEND=mock

Mock embeddings should be deterministic and not require internet.

Do not require Hugging Face token for embeddings.

Recommended model:

    sentence-transformers/all-MiniLM-L6-v2

### Result shape

Semantic search results should include:

    {
      "text": "...",
      "score": 0.82,
      "semantic_score": 0.82,
      "search_mode": "semantic"
    }

### Tests

Add tests using mock embeddings only:

- semantic search returns results
- semantic scores are present
- no internet/model download required for tests

### Verification commands

    python -m pytest -q

Manual optional test with real embeddings:

    RESUME_SEARCH_MODE=hybrid EMBEDDING_BACKEND=sentence_transformers \
    python -m cvtailor_agent.cli test-search --query "agent orchestration with LangGraph"

### Expected result

- Semantic backend exists.
- Tests use mock embeddings.
- No required internet access for tests.

### Git commit

    git add .
    git commit -m "phase 12 add semantic embedding backend"

Stop after this phase.

---

## Phase 13 — Implement hybrid scoring

### Copilot task

Implement Phase 13 only.

Combine keyword and semantic scores into a hybrid resume search.

### Files to inspect

- `src/cvtailor_mcp/resume_search.py`
- `src/cvtailor_mcp/tools.py`
- tests

### Required behavior

Implement:

    hybrid_search(
        query: str,
        resume_text: str,
        top_k: int = 5,
        keyword_weight: float = 0.4,
        semantic_weight: float = 0.6,
    ) -> list[dict]

Hybrid score:

    final_score = keyword_weight * keyword_score + semantic_weight * semantic_score

Return fields:

    {
      "text": "...",
      "score": 0.78,
      "keyword_score": 0.50,
      "semantic_score": 0.97,
      "matched_keywords": ["python", "langgraph"],
      "search_mode": "hybrid"
    }

Make sure scores are normalized between 0 and 1.

Update `search_resume()`:

    if mode == "keyword":
        return keyword_search(...)

    if mode == "hybrid":
        return hybrid_search(...)

Update MCP tool:

    search_resume_evidence

so it uses `RESUME_SEARCH_MODE`.

Default should remain keyword unless `.env` says hybrid.

### Tests

Add tests for:

- hybrid search returns keyword and semantic scores
- hybrid score is calculated correctly
- hybrid mode returns stable result shape
- keyword mode still works

Use mock embeddings for tests.

### Verification commands

    python -m pytest -q

Run keyword mode:

    RESUME_SEARCH_MODE=keyword python -m cvtailor_agent.cli test-search \
      --query "Python LangGraph MCP"

Run hybrid mode with mock embeddings:

    RESUME_SEARCH_MODE=hybrid EMBEDDING_BACKEND=mock \
    python -m cvtailor_agent.cli test-search \
      --query "agent orchestration with LangGraph"

### Expected result

- Hybrid mode works.
- Keyword mode still works.
- MCP tool returns hybrid search results when configured.

### Git commit

    git add .
    git commit -m "phase 13 implement hybrid resume search scoring"

Stop after this phase.

---

## Phase 14 — Optional FAISS index cache

### Copilot task

Implement Phase 14 only.

Add FAISS-based indexing for resume chunks if `faiss-cpu` is available.

This phase is optional. If FAISS is difficult in the current environment, implement a clean NumPy fallback and document it.

### Files to inspect

- `src/cvtailor_mcp/resume_search.py`
- `.gitignore`
- tests

### Required behavior

Add:

- FAISS index creation
- metadata mapping from vector IDs to resume chunks
- cache directory, for example `.cache/resume_search/`
- fallback to NumPy cosine similarity if FAISS is not installed

Update `.gitignore`:

    .cache/
    *.faiss

Do not commit generated index files.

Suggested behavior:

    if FAISS available:
        use FAISS
    else:
        use NumPy cosine similarity

### Tests

Do not require FAISS for tests.

Add tests for fallback behavior.

If FAISS is available, optionally test it.

### Verification commands

    python -m pytest -q

Manual hybrid search:

    RESUME_SEARCH_MODE=hybrid EMBEDDING_BACKEND=mock \
    python -m cvtailor_agent.cli test-search \
      --query "LLM workflow orchestration"

### Expected result

- Hybrid search can use vector indexing.
- Project still works without FAISS.
- Tests remain environment-friendly.

### Git commit

    git add .
    git commit -m "phase 14 add optional FAISS resume search index"

Stop after this phase.

---

## Phase 15 — Document hybrid search

### Copilot task

Implement Phase 15 only.

Update README to explain keyword, semantic, and hybrid search modes.

### Files to inspect

- `README.md`
- `.env.example`

### Required README section

Add:

    Resume Search Modes

Explain:

Keyword search:

    Finds exact matching terms like Python, MCP, SQLite.

Semantic search:

    Finds similar meaning, such as "agent orchestration" matching "LangGraph workflow".

Hybrid search:

    Combines both scores for stronger resume evidence retrieval.

Add examples:

    RESUME_SEARCH_MODE=keyword python -m cvtailor_agent.cli test-search \
      --query "Python LangGraph MCP"

    RESUME_SEARCH_MODE=hybrid EMBEDDING_BACKEND=mock python -m cvtailor_agent.cli test-search \
      --query "agent orchestration with LangGraph"

Add note:

    Tests use mock embeddings so they do not require internet or model downloads.

### Verification commands

    python -m pytest -q

### Expected result

README clearly explains the hybrid search upgrade.

### Git commit

    git add .
    git commit -m "phase 15 document hybrid resume search"

Stop after this phase.

---

# Final Acceptance Tests

After all phases are complete, run these commands.

## Normal test suite

    python -m pytest -q

## Direct MCP mode with keyword search

    MCP_CLIENT_MODE=direct RESUME_SEARCH_MODE=keyword \
    python -m cvtailor_agent.cli run \
      --job-file examples/job_description_ai_engineer.txt \
      --company "Acme AI" \
      --role "AI Engineer"

## Direct MCP mode with hybrid search and mock embeddings

    MCP_CLIENT_MODE=direct RESUME_SEARCH_MODE=hybrid EMBEDDING_BACKEND=mock \
    python -m cvtailor_agent.cli run \
      --job-file examples/job_description_ai_engineer.txt \
      --company "Acme AI" \
      --role "AI Engineer"

## Real MCP stdio mode

    MCP_CLIENT_MODE=stdio RESUME_SEARCH_MODE=keyword \
    python -m cvtailor_agent.cli run \
      --job-file examples/job_description_ai_engineer.txt \
      --company "Acme AI" \
      --role "AI Engineer"

## List applications

    python -m cvtailor_agent.cli list-applications

## Inspect profile

    python -m cvtailor_agent.cli inspect-profile

## Test search

    python -m cvtailor_agent.cli test-search --query "Python LangGraph MCP"

---

# Final README claims

After all phases are done, the README can honestly say:

    This project implements a LangGraph-based AI workflow with conditional routing, evidence-quality checks, fallback search, LLM-based review classification, and bounded revision loops.

    It includes an MCP server exposing tools for profile lookup, resume search, output saving, and SQLite application tracking.

    The LangGraph workflow can use either direct tool calls for local development or real MCP stdio communication for end-to-end MCP integration.

    Resume evidence retrieval supports keyword search and hybrid semantic search using embeddings.

---

# Final CV bullets

Use these after implementation is complete:

    Built a conditional LangGraph agent that analyzes job descriptions, retrieves resume evidence, generates tailored application packs, performs LLM-based review, and uses bounded revision loops before saving final outputs.

    Implemented an MCP server and real stdio MCP client mode, allowing the LangGraph workflow to call profile, resume search, Markdown saving, and SQLite logging tools through the MCP protocol.

    Upgraded resume retrieval from keyword matching to hybrid search using semantic embeddings and weighted keyword/vector scoring for improved evidence matching.

---

# Important stop rule for Copilot

When implementing a phase:

1. Modify only the files needed for that phase.
2. Do not skip ahead.
3. Do not implement later phases early.
4. Run or describe the verification commands.
5. Stop and summarize what changed.