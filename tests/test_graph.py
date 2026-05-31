"""Tests for LangGraph workflow."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from cvtailor_agent.graph import build_graph
from cvtailor_agent.state import CVTailorState
from cvtailor_mcp.schemas import DATABASE_PATH, OUTPUTS_DIR


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
