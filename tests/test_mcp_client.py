"""Tests for MCPClient wrapper."""

import tempfile
from pathlib import Path

import pytest

from cvtailor_agent.mcp_client import MCPClient


@pytest.fixture
def client():
    """Create an MCPClient instance for testing."""
    return MCPClient()


class TestMCPClientProfile:
    """Tests for profile-related methods."""
    
    def test_can_load_profile(self, client):
        """Test that client can load the candidate profile."""
        profile = client.get_candidate_profile()
        
        assert isinstance(profile, dict)
        assert "name" in profile
        assert profile["name"] == "Alex Chen"
    
    def test_profile_has_skills(self, client):
        """Test that profile includes skills."""
        profile = client.get_candidate_profile()
        
        assert "skills" in profile
        assert isinstance(profile["skills"], list)
        assert "Python" in profile["skills"]


class TestMCPClientSearch:
    """Tests for resume search methods."""
    
    def test_can_search_resume_evidence(self, client):
        """Test that client can search resume evidence."""
        results = client.search_resume_evidence("Python LangGraph MCP")
        
        assert isinstance(results, list)
    
    def test_search_returns_relevant_results(self, client):
        """Test that search returns relevant results."""
        results = client.search_resume_evidence("Python LangGraph MCP", top_k=3)
        
        assert len(results) > 0
        assert len(results) <= 3
        
        # Check result structure
        assert "text" in results[0]
        assert "score" in results[0]
    
    def test_search_respects_top_k(self, client):
        """Test that top_k parameter is respected."""
        results_2 = client.search_resume_evidence("Python", top_k=2)
        results_5 = client.search_resume_evidence("Python", top_k=5)
        
        assert len(results_2) <= 2
        assert len(results_5) <= 5


class TestMCPClientSaveApplication:
    """Tests for application pack saving."""
    
    def test_can_save_application_pack(self, client):
        """Test that client can save an application pack."""
        content = "# Test Application\n\nThis is a test application pack."
        
        result = client.save_application_pack(
            company="Test Company",
            role="Test Role",
            content=content
        )
        
        assert result["success"] is True
        assert "output_path" in result
        
        # Verify file was created
        output_path = Path(result["output_path"])
        assert output_path.exists()
        assert output_path.read_text(encoding="utf-8") == content
        
        # Cleanup
        output_path.unlink()


class TestMCPClientApplicationTracking:
    """Tests for application logging and listing."""
    
    @pytest.fixture
    def temp_db_setup(self, monkeypatch):
        """Set up temporary database for testing."""
        from pathlib import Path
        from cvtailor_mcp import storage
        from cvtailor_mcp import schemas
        
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_db = Path(tmpdir) / "test.sqlite"
            
            # Monkey-patch the DATABASE_PATH
            monkeypatch.setattr(schemas, "DATABASE_PATH", temp_db)
            monkeypatch.setattr(storage, "DATABASE_PATH", temp_db)
            
            yield temp_db
    
    def test_can_log_application(self, client, temp_db_setup):
        """Test that client can log an application."""
        result = client.log_application(
            company="Test Corp",
            role="Developer",
            status="drafted"
        )
        
        assert result["id"] == 1
        assert result["company"] == "Test Corp"
        assert result["status"] == "drafted"
    
    def test_can_list_applications(self, client, temp_db_setup):
        """Test that client can list applications."""
        # Log some applications
        client.log_application("Company A", "Role A", "drafted")
        client.log_application("Company B", "Role B", "submitted")
        
        # List all
        applications = client.list_applications()
        assert len(applications) == 2
    
    def test_can_filter_applications_by_status(self, client, temp_db_setup):
        """Test that client can filter applications by status."""
        client.log_application("Company A", "Role A", "drafted")
        client.log_application("Company B", "Role B", "submitted")
        client.log_application("Company C", "Role C", "drafted")
        
        drafted = client.list_applications(status="drafted")
        submitted = client.list_applications(status="submitted")
        
        assert len(drafted) == 2
        assert len(submitted) == 1
