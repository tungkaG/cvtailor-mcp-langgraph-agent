"""Tests for SQLite storage functionality."""

import tempfile
from pathlib import Path

import pytest

from cvtailor_mcp.storage import init_db, log_application, list_applications


@pytest.fixture
def temp_db_path():
    """Create a temporary database path for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "test_applications.sqlite"


class TestInitDb:
    """Tests for init_db function."""
    
    def test_creates_database_file(self, temp_db_path):
        """Test that init_db creates the database file."""
        assert not temp_db_path.exists()
        init_db(temp_db_path)
        assert temp_db_path.exists()
    
    def test_creates_parent_directory(self, temp_db_path):
        """Test that init_db creates parent directories if needed."""
        nested_path = temp_db_path.parent / "subdir" / "test.sqlite"
        init_db(nested_path)
        assert nested_path.exists()
    
    def test_idempotent(self, temp_db_path):
        """Test that init_db can be called multiple times safely."""
        init_db(temp_db_path)
        init_db(temp_db_path)  # Should not raise
        assert temp_db_path.exists()


class TestLogApplication:
    """Tests for log_application function."""
    
    def test_logging_creates_record(self, temp_db_path):
        """Test that logging creates a record in the database."""
        result = log_application(
            company="Acme AI",
            role="AI Engineer",
            status="drafted",
            db_path=temp_db_path
        )
        
        assert result["id"] == 1
        assert result["company"] == "Acme AI"
        assert result["role"] == "AI Engineer"
        assert result["status"] == "drafted"
        assert "created_at" in result
    
    def test_logging_with_notes_and_output_path(self, temp_db_path):
        """Test logging with optional fields."""
        result = log_application(
            company="TechCorp",
            role="Backend Developer",
            status="submitted",
            notes="Great opportunity",
            output_path="/outputs/techcorp-app.md",
            db_path=temp_db_path
        )
        
        assert result["notes"] == "Great opportunity"
        assert result["output_path"] == "/outputs/techcorp-app.md"
    
    def test_multiple_logs_get_incrementing_ids(self, temp_db_path):
        """Test that multiple logs get unique incrementing IDs."""
        result1 = log_application("Company A", "Role A", "drafted", db_path=temp_db_path)
        result2 = log_application("Company B", "Role B", "drafted", db_path=temp_db_path)
        result3 = log_application("Company C", "Role C", "submitted", db_path=temp_db_path)
        
        assert result1["id"] == 1
        assert result2["id"] == 2
        assert result3["id"] == 3


class TestListApplications:
    """Tests for list_applications function."""
    
    def test_listing_returns_records(self, temp_db_path):
        """Test that listing returns logged records."""
        log_application("Acme AI", "AI Engineer", "drafted", db_path=temp_db_path)
        
        applications = list_applications(db_path=temp_db_path)
        
        assert len(applications) == 1
        assert applications[0]["company"] == "Acme AI"
        assert applications[0]["role"] == "AI Engineer"
        assert applications[0]["status"] == "drafted"
    
    def test_listing_empty_database(self, temp_db_path):
        """Test listing from empty database returns empty list."""
        applications = list_applications(db_path=temp_db_path)
        assert applications == []
    
    def test_filtering_by_status(self, temp_db_path):
        """Test that filtering by status works."""
        log_application("Company A", "Role A", "drafted", db_path=temp_db_path)
        log_application("Company B", "Role B", "submitted", db_path=temp_db_path)
        log_application("Company C", "Role C", "drafted", db_path=temp_db_path)
        
        drafted = list_applications(status="drafted", db_path=temp_db_path)
        submitted = list_applications(status="submitted", db_path=temp_db_path)
        
        assert len(drafted) == 2
        assert len(submitted) == 1
        assert all(app["status"] == "drafted" for app in drafted)
        assert submitted[0]["status"] == "submitted"
    
    def test_returns_dictionaries_not_rows(self, temp_db_path):
        """Test that results are dictionaries with proper keys."""
        log_application("Acme AI", "AI Engineer", "drafted", db_path=temp_db_path)
        
        applications = list_applications(db_path=temp_db_path)
        app = applications[0]
        
        assert isinstance(app, dict)
        assert "id" in app
        assert "company" in app
        assert "role" in app
        assert "status" in app
        assert "notes" in app
        assert "output_path" in app
        assert "created_at" in app
    
    def test_temp_database_path_isolation(self, temp_db_path):
        """Test that temp database path keeps tests isolated."""
        # Log to temp path
        log_application("Test Company", "Test Role", "drafted", db_path=temp_db_path)
        
        # Create another temp path
        with tempfile.TemporaryDirectory() as other_tmpdir:
            other_path = Path(other_tmpdir) / "other.sqlite"
            
            # Should be empty in the other database
            other_apps = list_applications(db_path=other_path)
            assert other_apps == []
            
            # Original should still have the record
            original_apps = list_applications(db_path=temp_db_path)
            assert len(original_apps) == 1
