"""MCP server implementation using FastMCP.

This module exposes the CVTailor tools via the Model Context Protocol (MCP).
The server wraps the shared tool functions from tools.py, which remain
independently testable without MCP.

The server runs over stdio and waits for MCP client connections.

Usage:
    python -m cvtailor_mcp.server
"""

from typing import Optional

from mcp.server.fastmcp import FastMCP

from cvtailor_mcp.tools import (
    get_candidate_profile,
    search_resume_evidence,
    save_application_pack,
    log_application_tool,
    list_applications_tool,
)


# Create the MCP server
mcp = FastMCP("CVTailor MCP Server")


@mcp.tool()
def get_profile() -> dict:
    """Get the candidate's profile information.
    
    Returns the candidate's name, title, skills, experience, and contact info
    from the local profile.json file.
    """
    return get_candidate_profile()


@mcp.tool()
def search_resume(query: str, top_k: int = 5) -> list[dict]:
    """Search the candidate's resume for relevant sections.
    
    Args:
        query: Keywords to search for in the resume.
        top_k: Maximum number of results to return.
        
    Returns:
        List of matching resume sections with relevance scores.
    """
    return search_resume_evidence(query, top_k)


@mcp.tool()
def save_application(company: str, role: str, content: str) -> dict:
    """Save an application pack to a Markdown file.
    
    Args:
        company: Company name for the application.
        role: Role/position being applied for.
        content: Markdown content of the application pack.
        
    Returns:
        Result with success status and output file path.
    """
    return save_application_pack(company, role, content)


@mcp.tool()
def log_application(
    company: str,
    role: str,
    status: str,
    notes: str = "",
    output_path: str = ""
) -> dict:
    """Log a job application to the tracking database.
    
    Args:
        company: Company name.
        role: Role/position name.
        status: Application status (e.g., 'drafted', 'submitted').
        notes: Optional notes about the application.
        output_path: Optional path to the generated application pack.
        
    Returns:
        The logged application record with ID and timestamp.
    """
    return log_application_tool(company, role, status, notes, output_path)


@mcp.tool()
def list_applications(status: Optional[str] = None) -> list[dict]:
    """List job applications from the tracking database.
    
    Args:
        status: Optional filter by application status.
        
    Returns:
        List of application records.
    """
    return list_applications_tool(status)


# Expose the server object for testing
server = mcp


if __name__ == "__main__":
    # Run the server over stdio
    mcp.run()
