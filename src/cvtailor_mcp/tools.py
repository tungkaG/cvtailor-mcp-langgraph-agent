"""Shared tool functions for CVTailor MCP.

This module contains the core tool functions that can be:
1. Called directly by the agent's MCPClient wrapper (for MVP/testing)
2. Wrapped by the MCP server to expose to real MCP clients

Keeping tools in a separate module ensures they are testable without MCP.
"""

import json
import re
from pathlib import Path
from typing import Optional

from cvtailor_mcp.schemas import PROFILE_PATH, RESUME_PATH, OUTPUTS_DIR
from cvtailor_mcp.resume_search import search_resume
from cvtailor_mcp.storage import log_application, list_applications


def _slugify(text: str) -> str:
    """Convert text to a safe filename slug.
    
    Args:
        text: Text to convert.
        
    Returns:
        Lowercase slug with only alphanumeric characters and hyphens.
    """
    # Lowercase and replace spaces/underscores with hyphens
    slug = text.lower().replace(" ", "-").replace("_", "-")
    # Remove non-alphanumeric characters except hyphens
    slug = re.sub(r"[^a-z0-9\-]", "", slug)
    # Collapse multiple hyphens
    slug = re.sub(r"-+", "-", slug)
    # Strip leading/trailing hyphens
    return slug.strip("-")


def get_candidate_profile() -> dict:
    """Load and return the candidate profile from data/profile.json.
    
    Returns:
        Dictionary containing the candidate's profile data.
        
    Raises:
        FileNotFoundError: If profile.json does not exist.
        json.JSONDecodeError: If profile.json is invalid JSON.
    """
    profile_text = PROFILE_PATH.read_text(encoding="utf-8")
    return json.loads(profile_text)


def search_resume_evidence(query: str, top_k: int = 5) -> list[dict]:
    """Search the resume for sections relevant to a query.
    
    Args:
        query: Search query string.
        top_k: Maximum number of results to return.
        
    Returns:
        List of dicts with 'text' and 'score' keys.
    """
    resume_text = RESUME_PATH.read_text(encoding="utf-8")
    return search_resume(query, resume_text, top_k)


def save_application_pack(company: str, role: str, content: str) -> dict:
    """Save an application pack to a Markdown file.
    
    Creates the outputs/ directory if it doesn't exist.
    Uses safe slugified filenames.
    
    Args:
        company: Company name.
        role: Role/position name.
        content: Markdown content to save.
        
    Returns:
        Dictionary with success status and output_path.
    """
    # Ensure outputs directory exists
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create safe filename
    company_slug = _slugify(company)
    role_slug = _slugify(role)
    filename = f"{company_slug}-{role_slug}-application-pack.md"
    output_path = OUTPUTS_DIR / filename
    
    # Write the file
    output_path.write_text(content, encoding="utf-8")
    
    return {
        "success": True,
        "output_path": str(output_path),
        "company": company,
        "role": role
    }


def log_application_tool(
    company: str,
    role: str,
    status: str,
    notes: str = "",
    output_path: str = ""
) -> dict:
    """Log a job application to the database.
    
    Wrapper around storage.log_application for the tool layer.
    
    Args:
        company: Company name.
        role: Role/position name.
        status: Application status (e.g., 'drafted', 'submitted').
        notes: Optional notes about the application.
        output_path: Optional path to the generated application pack.
        
    Returns:
        Dictionary with the logged application details.
    """
    return log_application(
        company=company,
        role=role,
        status=status,
        notes=notes,
        output_path=output_path
    )


def list_applications_tool(status: Optional[str] = None) -> list[dict]:
    """List job applications from the database.
    
    Wrapper around storage.list_applications for the tool layer.
    
    Args:
        status: Optional status filter.
        
    Returns:
        List of application records as dictionaries.
    """
    return list_applications(status=status)
