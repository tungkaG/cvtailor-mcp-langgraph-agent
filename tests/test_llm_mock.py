"""Tests for LLM abstraction and prompt templates."""

from __future__ import annotations

import os
from unittest import mock

import pytest

from cvtailor_agent.llm import MockLLM, get_llm
from cvtailor_agent.prompts import (
    DRAFT_APPLICATION_PROMPT,
    IMPROVE_PROMPT,
    REQUIREMENT_EXTRACTION_PROMPT,
    REVIEW_PROMPT,
)


class TestGetLLM:
    """Tests for the get_llm factory function."""

    def test_get_llm_returns_mock_by_default(self) -> None:
        """get_llm should return MockLLM when no provider specified."""
        llm = get_llm()
        assert isinstance(llm, MockLLM)

    def test_get_llm_returns_mock_when_specified(self) -> None:
        """get_llm should return MockLLM when provider='mock'."""
        llm = get_llm(provider="mock")
        assert isinstance(llm, MockLLM)

    def test_get_llm_reads_from_environment(self) -> None:
        """get_llm should read LLM_PROVIDER from environment."""
        with mock.patch.dict(os.environ, {"LLM_PROVIDER": "mock"}):
            llm = get_llm()
            assert isinstance(llm, MockLLM)

    def test_get_llm_huggingface_not_implemented(self) -> None:
        """get_llm should raise NotImplementedError for huggingface."""
        with pytest.raises(NotImplementedError) as exc_info:
            get_llm(provider="huggingface")
        assert "Hugging Face" in str(exc_info.value)

    def test_get_llm_unknown_provider_raises_error(self) -> None:
        """get_llm should raise ValueError for unknown provider."""
        with pytest.raises(ValueError) as exc_info:
            get_llm(provider="unknown_provider")
        assert "Unknown LLM provider" in str(exc_info.value)

    def test_get_llm_provider_case_insensitive(self) -> None:
        """get_llm should handle provider names case-insensitively."""
        llm = get_llm(provider="MOCK")
        assert isinstance(llm, MockLLM)

        llm = get_llm(provider="Mock")
        assert isinstance(llm, MockLLM)


class TestMockLLM:
    """Tests for the MockLLM class."""

    def test_invoke_returns_non_empty_string(self) -> None:
        """MockLLM.invoke should return non-empty text."""
        llm = MockLLM()
        result = llm.invoke("Test prompt")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_invoke_handles_requirement_extraction(self) -> None:
        """MockLLM should handle requirement extraction prompts."""
        llm = MockLLM()
        result = llm.invoke("Extract the key requirements from this job description")
        assert "Requirements" in result or "Skills" in result

    def test_invoke_handles_draft_generation(self) -> None:
        """MockLLM should handle draft generation prompts."""
        llm = MockLLM()
        result = llm.invoke("Write a cover letter draft for this position")
        assert "Dear" in result or "Hiring Manager" in result

    def test_invoke_handles_review(self) -> None:
        """MockLLM should handle review prompts."""
        llm = MockLLM()
        result = llm.invoke("Review this draft and provide feedback")
        assert "Review" in result or "Strengths" in result or "Improvement" in result

    def test_invoke_handles_improvement(self) -> None:
        """MockLLM should handle improvement prompts."""
        llm = MockLLM()
        result = llm.invoke("Improve this draft based on the feedback")
        assert "Dear" in result or "Hiring Manager" in result

    def test_invoke_handles_unknown_prompt(self) -> None:
        """MockLLM should handle unknown prompt types gracefully."""
        llm = MockLLM()
        result = llm.invoke("Random unrelated text without keywords")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_invoke_is_deterministic(self) -> None:
        """MockLLM should return deterministic responses."""
        llm = MockLLM()
        result1 = llm.invoke("Extract requirements from job description")
        result2 = llm.invoke("Extract requirements from job description")
        assert result1 == result2


class TestPromptTemplates:
    """Tests for prompt templates."""

    def test_requirement_extraction_prompt_formats(self) -> None:
        """REQUIREMENT_EXTRACTION_PROMPT should format successfully."""
        result = REQUIREMENT_EXTRACTION_PROMPT.format(
            job_description="We are looking for a Python developer...",
            company="Acme Corp",
            role="Software Engineer",
        )
        assert "Python developer" in result
        assert "Acme Corp" in result
        assert "Software Engineer" in result

    def test_draft_application_prompt_formats(self) -> None:
        """DRAFT_APPLICATION_PROMPT should format successfully."""
        result = DRAFT_APPLICATION_PROMPT.format(
            requirements="Python, FastAPI, SQL",
            profile="Experienced software engineer",
            resume_evidence="Built APIs serving millions of users",
            company="Acme Corp",
            role="Backend Engineer",
        )
        assert "Python" in result
        assert "Acme Corp" in result
        assert "Backend Engineer" in result

    def test_review_prompt_formats(self) -> None:
        """REVIEW_PROMPT should format successfully."""
        result = REVIEW_PROMPT.format(
            draft="Dear Hiring Manager...",
            requirements="Python, leadership",
            company="Tech Inc",
            role="Tech Lead",
        )
        assert "Dear Hiring Manager" in result
        assert "Tech Inc" in result
        assert "Tech Lead" in result

    def test_improve_prompt_formats(self) -> None:
        """IMPROVE_PROMPT should format successfully."""
        result = IMPROVE_PROMPT.format(
            draft="Dear Hiring Manager...",
            feedback="Add more metrics",
            requirements="Data analysis skills",
            company="Data Corp",
            role="Data Scientist",
        )
        assert "Dear Hiring Manager" in result
        assert "Add more metrics" in result
        assert "Data Corp" in result

    def test_all_prompts_have_required_variables(self) -> None:
        """All prompts should have documented input variables."""
        assert "job_description" in REQUIREMENT_EXTRACTION_PROMPT.input_variables
        assert "company" in REQUIREMENT_EXTRACTION_PROMPT.input_variables
        assert "role" in REQUIREMENT_EXTRACTION_PROMPT.input_variables

        assert "requirements" in DRAFT_APPLICATION_PROMPT.input_variables
        assert "profile" in DRAFT_APPLICATION_PROMPT.input_variables
        assert "resume_evidence" in DRAFT_APPLICATION_PROMPT.input_variables

        assert "draft" in REVIEW_PROMPT.input_variables
        assert "requirements" in REVIEW_PROMPT.input_variables

        assert "draft" in IMPROVE_PROMPT.input_variables
        assert "feedback" in IMPROVE_PROMPT.input_variables
