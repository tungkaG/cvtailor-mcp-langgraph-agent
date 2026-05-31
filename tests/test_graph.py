"""Tests for LangGraph workflow."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from cvtailor_agent.graph import build_graph
from cvtailor_agent.state import CVTailorState


REQUIRED_MARKDOWN_HEADINGS = [
    "# Application Pack: {role} at {company}",
    "## Job Requirement Summary",
    "## Candidate Match Score",
    "## Matched Skills Table",
    "## Tailored Resume Summary",
    "## Tailored Resume Bullets",
    "## Short Cover Letter",
    "## Gap Analysis",
    "## Next Actions",
]


# Get path to example job description
EXAMPLES_DIR = Path(__file__).parent.parent / "examples"
EXAMPLE_JOB_FILE = EXAMPLES_DIR / "job_description_ai_engineer.txt"


class TestBuildGraph:
    """Tests for build_graph function."""

    def test_build_graph_returns_compiled_graph(self) -> None:
        """build_graph should return a compiled LangGraph."""
        graph = build_graph()
        assert graph is not None
        # Check that it has an invoke method
        assert hasattr(graph, "invoke")
        assert callable(graph.invoke)

    def test_build_graph_graph_is_invokable(self) -> None:
        """The graph should be invokable with proper state."""
        graph = build_graph()

        # Should not raise when we have the invoke method
        assert hasattr(graph, "invoke")


class TestGraphInvoke:
    """Tests for full graph invocation."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self) -> None:
        """Ensure clean state before and after tests."""
        # Set mock LLM provider
        os.environ["LLM_PROVIDER"] = "mock"

        yield

        # Clean up generated files after test
        # (Optional: could delete test outputs here)

    def test_graph_invoke_with_example_job(self) -> None:
        """Graph invoke with example job should create final output."""
        # Skip if example file doesn't exist
        if not EXAMPLE_JOB_FILE.exists():
            pytest.skip(f"Example job file not found: {EXAMPLE_JOB_FILE}")

        graph = build_graph()

        initial_state: CVTailorState = {
            "company": "Acme AI",
            "role": "AI Engineer",
            "job_file": str(EXAMPLE_JOB_FILE),
        }

        result = graph.invoke(initial_state)

        # Verify required outputs are present
        assert result is not None
        assert "output_path" in result
        assert result["output_path"] is not None
        assert "application_id" in result
        assert result["application_id"] is not None
        assert result["output_path"].endswith("acme-ai-ai-engineer-application-pack.md")

    def test_graph_invoke_populates_all_fields(self) -> None:
        """Graph invoke should populate all state fields."""
        if not EXAMPLE_JOB_FILE.exists():
            pytest.skip(f"Example job file not found: {EXAMPLE_JOB_FILE}")

        graph = build_graph()

        initial_state: CVTailorState = {
            "company": "Test Corp",
            "role": "Software Engineer",
            "job_file": str(EXAMPLE_JOB_FILE),
        }

        result = graph.invoke(initial_state)

        # Check all intermediate fields are populated
        assert result.get("job_description") is not None
        assert result.get("requirements") is not None
        assert result.get("profile") is not None
        assert result.get("evidence") is not None
        assert result.get("draft_application_pack") is not None
        assert result.get("review_feedback") is not None
        assert result.get("final_application_pack") is not None
        assert result.get("output_path") is not None
        assert result.get("application_id") is not None

        expected_title = REQUIRED_MARKDOWN_HEADINGS[0].format(
            role=initial_state["role"],
            company=initial_state["company"],
        )
        assert expected_title in result["final_application_pack"]
        for heading in REQUIRED_MARKDOWN_HEADINGS[1:]:
            assert heading in result["final_application_pack"]

    def test_graph_invoke_creates_output_file(self) -> None:
        """Graph invoke should create an output file on disk."""
        if not EXAMPLE_JOB_FILE.exists():
            pytest.skip(f"Example job file not found: {EXAMPLE_JOB_FILE}")

        graph = build_graph()

        initial_state: CVTailorState = {
            "company": "FileTest Inc",
            "role": "Developer",
            "job_file": str(EXAMPLE_JOB_FILE),
        }

        result = graph.invoke(initial_state)

        # Verify output file exists
        output_path = result.get("output_path")
        assert output_path is not None
        assert Path(output_path).exists()

        # Verify file has content
        content = Path(output_path).read_text(encoding="utf-8")
        assert len(content) > 0

        expected_title = REQUIRED_MARKDOWN_HEADINGS[0].format(
            role=initial_state["role"],
            company=initial_state["company"],
        )
        assert expected_title in content
        for heading in REQUIRED_MARKDOWN_HEADINGS[1:]:
            assert heading in content

    def test_graph_invoke_file_not_found(self) -> None:
        """Graph invoke should raise FileNotFoundError for missing job file."""
        graph = build_graph()

        initial_state: CVTailorState = {
            "company": "Test",
            "role": "Test",
            "job_file": "/nonexistent/path/job.txt",
        }

        with pytest.raises(FileNotFoundError):
            graph.invoke(initial_state)


class TestGraphNodes:
    """Tests for individual graph nodes."""

    def test_load_job_description_node(self) -> None:
        """load_job_description should load file content."""
        from cvtailor_agent.graph import load_job_description

        if not EXAMPLE_JOB_FILE.exists():
            pytest.skip(f"Example job file not found: {EXAMPLE_JOB_FILE}")

        state: CVTailorState = {
            "company": "Test",
            "role": "Test",
            "job_file": str(EXAMPLE_JOB_FILE),
        }

        result = load_job_description(state)

        assert "job_description" in result
        assert len(result["job_description"]) > 0

    def test_extract_requirements_node(self) -> None:
        """extract_requirements should extract requirements."""
        from cvtailor_agent.graph import extract_requirements_with_llm

        os.environ["LLM_PROVIDER"] = "mock"

        state: CVTailorState = {
            "company": "Test Corp",
            "role": "Engineer",
            "job_file": "test.txt",
            "job_description": "Looking for Python developer with ML experience",
        }

        result = extract_requirements_with_llm(state)

        assert "requirements" in result
        assert len(result["requirements"]) > 0

    def test_get_profile_node(self) -> None:
        """get_profile should return candidate profile."""
        from cvtailor_agent.graph import get_candidate_profile_from_mcp

        state: CVTailorState = {
            "company": "Test",
            "role": "Test",
            "job_file": "test.txt",
        }

        result = get_candidate_profile_from_mcp(state)

        assert "profile" in result
        assert result["profile"] is not None
        assert "name" in result["profile"]

    def test_search_evidence_node(self) -> None:
        """search_evidence should return relevant resume sections."""
        from cvtailor_agent.graph import search_resume_evidence_from_mcp

        state: CVTailorState = {
            "company": "Test",
            "role": "Python Developer",
            "job_file": "test.txt",
            "requirements": "Python, API development, machine learning",
        }

        result = search_resume_evidence_from_mcp(state)

        assert "evidence" in result
        assert isinstance(result["evidence"], list)


class TestEvidenceScoring:
    """Tests for the evidence scoring node."""

    def test_score_evidence_no_evidence_gives_weak_quality(self) -> None:
        """No evidence should give weak quality."""
        from cvtailor_agent.graph import score_resume_evidence

        state: CVTailorState = {
            "company": "Test",
            "role": "Test",
            "job_file": "test.txt",
            "evidence": [],
        }

        result = score_resume_evidence(state)

        assert result["evidence_score"] == 0.0
        assert result["evidence_quality"] == "weak"
        assert "No resume evidence found" in result["route_reason"]

    def test_score_evidence_none_evidence_gives_weak_quality(self) -> None:
        """None evidence should give weak quality."""
        from cvtailor_agent.graph import score_resume_evidence

        state: CVTailorState = {
            "company": "Test",
            "role": "Test",
            "job_file": "test.txt",
            "evidence": None,
        }

        result = score_resume_evidence(state)

        assert result["evidence_score"] == 0.0
        assert result["evidence_quality"] == "weak"

    def test_score_evidence_high_score_gives_strong_quality(self) -> None:
        """High-score evidence should give strong quality."""
        from cvtailor_agent.graph import score_resume_evidence

        state: CVTailorState = {
            "company": "Test",
            "role": "Test",
            "job_file": "test.txt",
            "evidence": [
                {"text": "Python experience", "score": 0.85},
                {"text": "LangGraph workflow", "score": 0.75},
                {"text": "API development", "score": 0.60},
            ],
        }

        result = score_resume_evidence(state)

        assert result["evidence_score"] >= 0.50
        assert result["evidence_quality"] == "strong"
        assert ">= 0.50" in result["route_reason"]

    def test_score_evidence_low_score_gives_weak_quality(self) -> None:
        """Low-score evidence should give weak quality."""
        from cvtailor_agent.graph import score_resume_evidence

        state: CVTailorState = {
            "company": "Test",
            "role": "Test",
            "job_file": "test.txt",
            "evidence": [
                {"text": "Some text", "score": 0.20},
                {"text": "Other text", "score": 0.30},
                {"text": "More text", "score": 0.25},
            ],
        }

        result = score_resume_evidence(state)

        assert result["evidence_score"] < 0.50
        assert result["evidence_quality"] == "weak"
        assert "< 0.50" in result["route_reason"]

    def test_score_evidence_exactly_threshold_gives_strong(self) -> None:
        """Evidence at exactly 0.50 threshold should give strong quality."""
        from cvtailor_agent.graph import score_resume_evidence

        state: CVTailorState = {
            "company": "Test",
            "role": "Test",
            "job_file": "test.txt",
            "evidence": [
                {"text": "Some text", "score": 0.50},
            ],
        }

        result = score_resume_evidence(state)

        assert result["evidence_score"] == 0.50
        assert result["evidence_quality"] == "strong"

    def test_score_evidence_missing_scores_gives_weak(self) -> None:
        """Evidence items without scores should give weak quality."""
        from cvtailor_agent.graph import score_resume_evidence

        state: CVTailorState = {
            "company": "Test",
            "role": "Test",
            "job_file": "test.txt",
            "evidence": [
                {"text": "No score field"},
                {"text": "Also no score"},
            ],
        }

        result = score_resume_evidence(state)

        assert result["evidence_score"] == 0.0
        assert result["evidence_quality"] == "weak"
        assert "no scores" in result["route_reason"]


class TestEvidenceRouting:
    """Tests for conditional routing after evidence scoring."""

    def test_router_strong_evidence_routes_to_generation(self) -> None:
        """Strong evidence quality should route to strong_match."""
        from cvtailor_agent.graph import route_after_evidence_scoring

        state: CVTailorState = {
            "company": "Test",
            "role": "Test",
            "job_file": "test.txt",
            "evidence_quality": "strong",
            "search_attempts": 0,
            "max_search_attempts": 2,
        }

        route = route_after_evidence_scoring(state)

        assert route == "strong_match"

    def test_router_weak_evidence_routes_to_broaden_search(self) -> None:
        """Weak evidence with attempts remaining should route to weak_match."""
        from cvtailor_agent.graph import route_after_evidence_scoring

        state: CVTailorState = {
            "company": "Test",
            "role": "Test",
            "job_file": "test.txt",
            "evidence_quality": "weak",
            "search_attempts": 0,
            "max_search_attempts": 2,
        }

        route = route_after_evidence_scoring(state)

        assert route == "weak_match"

    def test_router_max_attempts_routes_to_continue(self) -> None:
        """Weak evidence at max attempts should route to continue_anyway."""
        from cvtailor_agent.graph import route_after_evidence_scoring

        state: CVTailorState = {
            "company": "Test",
            "role": "Test",
            "job_file": "test.txt",
            "evidence_quality": "weak",
            "search_attempts": 2,
            "max_search_attempts": 2,
        }

        route = route_after_evidence_scoring(state)

        assert route == "continue_anyway"

    def test_router_unknown_quality_routes_to_weak_match(self) -> None:
        """Unknown quality with attempts remaining should route to weak_match."""
        from cvtailor_agent.graph import route_after_evidence_scoring

        state: CVTailorState = {
            "company": "Test",
            "role": "Test",
            "job_file": "test.txt",
            "evidence_quality": "unknown",
            "search_attempts": 0,
            "max_search_attempts": 2,
        }

        route = route_after_evidence_scoring(state)

        assert route == "weak_match"

    def test_router_uses_default_max_attempts(self) -> None:
        """Router should use default max_search_attempts if not set."""
        from cvtailor_agent.graph import route_after_evidence_scoring

        state: CVTailorState = {
            "company": "Test",
            "role": "Test",
            "job_file": "test.txt",
            "evidence_quality": "weak",
            "search_attempts": 2,
            # max_search_attempts not set - should default to 2
        }

        route = route_after_evidence_scoring(state)

        assert route == "continue_anyway"


class TestBroadenSearchQuery:
    """Tests for the broaden_search_query node."""

    def test_broaden_search_creates_expanded_query(self) -> None:
        """Should create an expanded search query from role and requirements."""
        from cvtailor_agent.graph import broaden_search_query

        state: CVTailorState = {
            "company": "Test",
            "role": "AI Engineer",
            "job_file": "test.txt",
            "requirements": "Python, machine learning, NLP",
            "profile": {"skills": ["Python", "TensorFlow", "PyTorch"]},
            "search_attempts": 0,
        }

        result = broaden_search_query(state)

        assert "expanded_search_query" in result
        assert "AI Engineer" in result["expanded_search_query"]
        assert "Python" in result["expanded_search_query"]
        assert result["search_attempts"] == 1

    def test_broaden_search_increments_attempts(self) -> None:
        """Should increment search_attempts."""
        from cvtailor_agent.graph import broaden_search_query

        state: CVTailorState = {
            "company": "Test",
            "role": "Engineer",
            "job_file": "test.txt",
            "search_attempts": 1,
        }

        result = broaden_search_query(state)

        assert result["search_attempts"] == 2

    def test_broaden_search_handles_missing_profile(self) -> None:
        """Should handle missing profile gracefully."""
        from cvtailor_agent.graph import broaden_search_query

        state: CVTailorState = {
            "company": "Test",
            "role": "Engineer",
            "job_file": "test.txt",
        }

        result = broaden_search_query(state)

        assert "expanded_search_query" in result
        assert "Engineer" in result["expanded_search_query"]

    def test_broaden_search_handles_dict_requirements(self) -> None:
        """Should handle requirements as dict."""
        from cvtailor_agent.graph import broaden_search_query

        state: CVTailorState = {
            "company": "Test",
            "role": "Engineer",
            "job_file": "test.txt",
            "requirements": {"must_have": ["Python"], "nice_to_have": ["Go"]},
        }

        result = broaden_search_query(state)

        assert "expanded_search_query" in result
        assert "Python" in result["expanded_search_query"]


class TestSearchResumeEvidenceAgain:
    """Tests for the search_resume_evidence_again node."""

    def test_search_again_uses_expanded_query(self) -> None:
        """Should use expanded_search_query for search."""
        from cvtailor_agent.graph import search_resume_evidence_again

        state: CVTailorState = {
            "company": "Test",
            "role": "Engineer",
            "job_file": "test.txt",
            "expanded_search_query": "Python machine learning NLP",
        }

        result = search_resume_evidence_again(state)

        assert "evidence" in result
        # Mock client returns evidence list
        assert isinstance(result["evidence"], list)

    def test_search_again_falls_back_without_expanded_query(self) -> None:
        """Should fall back to original query logic if no expanded query."""
        from cvtailor_agent.graph import search_resume_evidence_again

        state: CVTailorState = {
            "company": "Test",
            "role": "Engineer",
            "job_file": "test.txt",
            "requirements": "Python skills",
        }

        result = search_resume_evidence_again(state)

        assert "evidence" in result
        assert isinstance(result["evidence"], list)
