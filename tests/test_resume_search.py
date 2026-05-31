"""Tests for resume search functionality."""

import pytest

from cvtailor_mcp.resume_search import tokenize, split_resume_sections, search_resume


class TestTokenize:
    """Tests for the tokenize function."""
    
    def test_tokenize_basic(self):
        """Test basic tokenization."""
        result = tokenize("Hello World")
        assert result == {"hello", "world"}
    
    def test_tokenize_removes_punctuation(self):
        """Test that punctuation is removed."""
        result = tokenize("Hello, World! How are you?")
        assert "hello" in result
        assert "world" in result
        assert "," not in result
        assert "!" not in result
    
    def test_tokenize_lowercase(self):
        """Test that text is lowercased."""
        result = tokenize("PYTHON LangGraph MCP")
        assert result == {"python", "langgraph", "mcp"}
    
    def test_tokenize_empty(self):
        """Test empty input."""
        result = tokenize("")
        assert result == set()


class TestSplitResumeSections:
    """Tests for the split_resume_sections function."""
    
    def test_split_on_double_newline(self):
        """Test splitting on double newlines."""
        text = "Section 1\n\nSection 2\n\nSection 3"
        result = split_resume_sections(text)
        assert len(result) == 3
        assert "Section 1" in result
        assert "Section 2" in result
        assert "Section 3" in result
    
    def test_ignores_empty_sections(self):
        """Test that empty sections are filtered out."""
        text = "Section 1\n\n\n\n\nSection 2"
        result = split_resume_sections(text)
        assert len(result) == 2
    
    def test_handles_single_section(self):
        """Test handling of single section text."""
        text = "Just one section"
        result = split_resume_sections(text)
        assert len(result) == 1
        assert result[0] == "Just one section"


class TestSearchResume:
    """Tests for the search_resume function."""
    
    @pytest.fixture
    def sample_resume(self):
        """Sample resume text for testing."""
        return """# Alex Chen

AI Engineer / Python Developer

## Skills

Python, LangGraph, LangChain, MCP, Hugging Face, SQL, FastAPI, Docker

## Projects

### CVTailor MCP LangGraph Agent

Built an AI-powered job application assistant using Python, LangGraph, LangChain, and MCP.

### FastAPI Microservice

Created a production-ready FastAPI template with Docker deployment.

## Experience

Junior Python Developer at TechStart GmbH.
Developed backend APIs using FastAPI and PostgreSQL.
"""
    
    def test_search_returns_relevant_results(self, sample_resume):
        """Test that search returns relevant results for query."""
        results = search_resume("Python LangGraph MCP", sample_resume)
        
        assert len(results) > 0
        # At least one result should contain Python or LangGraph or MCP
        top_result = results[0]
        assert "text" in top_result
        assert "score" in top_result
        assert top_result["score"] > 0
        
        # The top result should contain relevant keywords
        top_text_lower = top_result["text"].lower()
        has_keyword = "python" in top_text_lower or "langgraph" in top_text_lower or "mcp" in top_text_lower
        assert has_keyword
    
    def test_top_k_is_respected(self, sample_resume):
        """Test that top_k limits the number of results."""
        results_2 = search_resume("Python", sample_resume, top_k=2)
        results_5 = search_resume("Python", sample_resume, top_k=5)
        
        assert len(results_2) <= 2
        assert len(results_5) <= 5
    
    def test_empty_query_returns_empty_list(self, sample_resume):
        """Test that empty query returns empty list without crashing."""
        assert search_resume("", sample_resume) == []
        assert search_resume("   ", sample_resume) == []
    
    def test_empty_resume_returns_empty_list(self):
        """Test that empty resume returns empty list."""
        assert search_resume("Python", "") == []
        assert search_resume("Python", "   ") == []
    
    def test_results_sorted_by_score_descending(self, sample_resume):
        """Test that results are sorted by score in descending order."""
        results = search_resume("Python FastAPI Docker", sample_resume)
        
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i]["score"] >= results[i + 1]["score"]
    
    def test_score_is_between_zero_and_one(self, sample_resume):
        """Test that scores are normalized between 0 and 1."""
        results = search_resume("Python LangGraph MCP", sample_resume)
        
        for result in results:
            assert 0 <= result["score"] <= 1
