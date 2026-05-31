"""MCP client wrapper for the CVTailor agent.

This module provides an MCPClient class that abstracts access to MCP tools.

MVP Implementation Note:
------------------------
For the MVP, this wrapper calls the shared MCP tool functions directly from
cvtailor_mcp.tools. This keeps the workflow reliable and easy to test without
requiring a running MCP server.

The same tool functions are also exposed via server.py for real MCP clients
that connect over stdio. A future phase could add an optional stdio client
mode that actually connects to the MCP server.

The LangGraph workflow depends on this MCPClient abstraction, so changing
the underlying transport (direct calls vs stdio MCP) won't require changes
to the agent workflow.
"""

from typing import Optional

from cvtailor_mcp.tools import (
    get_candidate_profile as _get_profile,
    search_resume_evidence as _search_evidence,
    save_application_pack as _save_pack,
    log_application_tool as _log_app,
    list_applications_tool as _list_apps,
)


class MCPClient:
    """Client wrapper for accessing MCP tool functions.
    
    This class provides a clean interface for the LangGraph agent to call
    MCP tools. For the MVP, methods directly call shared tool functions.
    
    Example:
        client = MCPClient()
        profile = client.get_candidate_profile()
        evidence = client.search_resume_evidence("Python LangGraph")
    """
    
    def __init__(self) -> None:
        """Initialize the MCP client.
        
        For the MVP, no connection setup is needed since we call
        tool functions directly.
        """
        pass
    
    def get_candidate_profile(self) -> dict:
        """Get the candidate's profile information.
        
        Returns:
            Dictionary containing profile data (name, skills, etc.).
        """
        return _get_profile()
    
    def search_resume_evidence(self, query: str, top_k: int = 5) -> list[dict]:
        """Search the resume for sections relevant to a query.
        
        Args:
            query: Keywords to search for.
            top_k: Maximum number of results to return.
            
        Returns:
            List of matching sections with text and score.
        """
        return _search_evidence(query, top_k)
    
    def save_application_pack(self, company: str, role: str, content: str) -> dict:
        """Save an application pack to a Markdown file.
        
        Args:
            company: Company name.
            role: Role/position name.
            content: Markdown content to save.
            
        Returns:
            Result with success status and output_path.
        """
        return _save_pack(company, role, content)
    
    def log_application(
        self,
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
        return _log_app(company, role, status, notes, output_path)
    
    def list_applications(self, status: Optional[str] = None) -> list[dict]:
        """List job applications from the tracking database.
        
        Args:
            status: Optional filter by application status.
            
        Returns:
            List of application records.
        """
        return _list_apps(status)
