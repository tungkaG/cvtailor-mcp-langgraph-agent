"""Pydantic schemas and path helpers for CVTailor MCP.

This module contains:
- Path constants for project directories and files
- Pydantic models for data structures used across the application
"""

from pathlib import Path
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ============================================================================
# Path Constants
# ============================================================================

# Project root is the directory containing pyproject.toml
# This works when running from the project root directory
PROJECT_ROOT = Path.cwd()
DATA_DIR = PROJECT_ROOT / "data"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
PROFILE_PATH = DATA_DIR / "profile.json"
RESUME_PATH = DATA_DIR / "resume.md"
DATABASE_PATH = DATA_DIR / "applications.sqlite"


# ============================================================================
# Pydantic Models
# ============================================================================

class ResumeSearchResult(BaseModel):
    """A single result from searching the resume."""
    
    text: str = Field(..., description="The matched text section from the resume")
    score: float = Field(..., ge=0.0, description="Relevance score for this result")


class SaveApplicationResult(BaseModel):
    """Result from saving an application pack to disk."""
    
    success: bool = Field(..., description="Whether the save operation succeeded")
    output_path: str = Field(..., description="Path to the saved Markdown file")
    company: str = Field(..., description="Company name")
    role: str = Field(..., description="Role/position name")


class LogApplicationResult(BaseModel):
    """Result from logging an application to the database."""
    
    success: bool = Field(..., description="Whether the log operation succeeded")
    application_id: int = Field(..., description="Database ID of the logged application")
    company: str = Field(..., description="Company name")
    role: str = Field(..., description="Role/position name")
    status: str = Field(..., description="Application status")


class ApplicationRecord(BaseModel):
    """A job application record from the database."""
    
    id: int = Field(..., description="Database ID")
    company: str = Field(..., description="Company name")
    role: str = Field(..., description="Role/position name")
    status: str = Field(..., description="Application status (e.g., drafted, submitted)")
    notes: Optional[str] = Field(default="", description="Additional notes")
    output_path: Optional[str] = Field(default="", description="Path to the generated application pack")
    created_at: str = Field(..., description="ISO timestamp when the application was logged")
