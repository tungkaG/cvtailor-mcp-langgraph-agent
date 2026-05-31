"""Tests for shared tool functions."""

import tempfile
from pathlib import Path

import pytest

from cvtailor_mcp.tools import (
    get_candidate_profile,
    search_resume_evidence,
    save_application_pack,
    log_application_tool,
    list_applications_tool,
    _slugify,
)


class TestSlugify:
    """Tests for the _slugify helper function."""
    
    def test_basic_slugify(self):
        """Test basic text slugification."""
        assert _slugify("Acme AI") == "acme-ai"
        assert _slugify("AI Engineer") == "ai-engineer"
    
    def test_removes_special_characters(self):
        """Test that special characters are removed."""
        assert _slugify("Company's Name!") == "companys-name"
        assert _slugify("Tech & Co.") == "tech-co"
    
    def test_collapses_multiple_hyphens(self):
        """Test that multiple hyphens are collapsed."""
        assert _slugify("A   B   C") == "a-b-c"
        assert _slugify("A---B") == "a-b"


class TestGetCandidateProfile:
    """Tests for get_candidate_profile function."""
    
    def test_profile_loads(self):
        """Test that profile loads successfully."""
        profile = get_candidate_profile()
        
        assert isinstance(profile, dict)
        assert "name" in profile
        assert "skills" in profile
    
    def test_profile_has_expected_fields(self):
        """Test that profile has expected structure."""
        profile = get_candidate_profile()
        
        assert profile["name"] == "Alex Chen"
        assert isinstance(profile["skills"], list)
        assert "Python" in profile["skills"]


class TestSearchResumeEvidence:
    """Tests for search_resume_evidence function."""
    
    def test_returns_list(self):
        """Test that search returns a list."""
        results = search_resume_evidence("Python LangGraph MCP")
        
        assert isinstance(results, list)
    
    def test_results_have_expected_fields(self):
        """Test that results have text and score fields."""
        results = search_resume_evidence("Python LangGraph MCP", top_k=2)
        
        assert len(results) <= 2
        if results:
            assert "text" in results[0]
            assert "score" in results[0]
    
    def test_finds_relevant_content(self):
        """Test that search finds relevant content."""
        results = search_resume_evidence("Python LangGraph MCP", top_k=3)
        
        # Should find sections mentioning these keywords
        assert len(results) > 0
        top_text = results[0]["text"].lower()
        has_keyword = "python" in top_text or "langgraph" in top_text or "mcp" in top_text
        assert has_keyword


class TestSaveApplicationPack:
    """Tests for save_application_pack function."""
    
    def test_writes_file(self):
        """Test that save creates a file."""
        content = "# Test Application Pack\n\nThis is a test."
        
        result = save_application_pack(
            company="Test Company",
            role="Test Role",
            content=content
        )
        
        assert result["success"] is True
        assert "output_path" in result
        
        # Verify file exists and has correct content
        output_path = Path(result["output_path"])
        assert output_path.exists()
        assert output_path.read_text(encoding="utf-8") == content
        
        # Cleanup
        output_path.unlink()
    
    def test_creates_safe_filename(self):
        """Test that filename is safely slugified."""
        result = save_application_pack(
            company="Acme AI",
            role="AI Engineer",
            content="# Test"
        )
        
        output_path = Path(result["output_path"])
        assert output_path.name == "acme-ai-ai-engineer-application-pack.md"
        
        # Cleanup
        output_path.unlink()
    
    def test_handles_special_characters_in_names(self):
        """Test that special characters in company/role names are handled."""
        result = save_application_pack(
            company="Tech & Co's",
            role="Sr. Developer!",
            content="# Test"
        )
        
        output_path = Path(result["output_path"])
        assert output_path.exists()
        # Should have sanitized filename
        assert "'" not in output_path.name
        assert "!" not in output_path.name
        
        # Cleanup
        output_path.unlink()


class TestLogAndListApplicationTools:
    """Tests for log_application_tool and list_applications_tool."""
    
    @pytest.fixture
    def temp_db_setup(self, monkeypatch):
        """Set up temporary database for testing."""
        import tempfile
        from pathlib import Path
        from cvtailor_mcp import storage
        from cvtailor_mcp import schemas
        
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_db = Path(tmpdir) / "test.sqlite"
            
            # Monkey-patch the DATABASE_PATH
            original_path = schemas.DATABASE_PATH
            monkeypatch.setattr(schemas, "DATABASE_PATH", temp_db)
            
            # Also patch in storage module if it caches the import
            monkeypatch.setattr(storage, "DATABASE_PATH", temp_db)
            
            yield temp_db
    
    def test_log_creates_record(self, temp_db_setup):
        """Test that logging creates a record."""
        result = log_application_tool(
            company="Test Corp",
            role="Test Engineer",
            status="drafted"
        )
        
        assert result["id"] == 1
        assert result["company"] == "Test Corp"
        assert result["status"] == "drafted"
    
    def test_list_returns_logged_records(self, temp_db_setup):
        """Test that list returns logged records."""
        log_application_tool("Company A", "Role A", "drafted")
        log_application_tool("Company B", "Role B", "submitted")
        
        applications = list_applications_tool()
        
        assert len(applications) == 2
    
    def test_list_filters_by_status(self, temp_db_setup):
        """Test that list can filter by status."""
        log_application_tool("Company A", "Role A", "drafted")
        log_application_tool("Company B", "Role B", "submitted")
        log_application_tool("Company C", "Role C", "drafted")
        
        drafted = list_applications_tool(status="drafted")
        submitted = list_applications_tool(status="submitted")
        
        assert len(drafted) == 2
        assert len(submitted) == 1
