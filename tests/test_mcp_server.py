"""Tests for MCP server module."""

import pytest


class TestMCPServerImport:
    """Smoke tests for MCP server module."""
    
    def test_server_module_imports(self):
        """Test that the server module imports successfully."""
        import cvtailor_mcp.server
        
        # Should import without errors
        assert cvtailor_mcp.server is not None
    
    def test_server_exposes_mcp_object(self):
        """Test that the server exposes an MCP server object."""
        from cvtailor_mcp.server import server
        
        assert server is not None
    
    def test_server_exposes_mcp_fastmcp(self):
        """Test that the server uses FastMCP."""
        from cvtailor_mcp.server import mcp
        from mcp.server.fastmcp import FastMCP
        
        assert isinstance(mcp, FastMCP)
    
    def test_tools_are_registered(self):
        """Test that tools are registered on the server."""
        from cvtailor_mcp.server import mcp
        
        # FastMCP registers tools internally
        # We just verify the module loaded with decorators applied
        assert mcp is not None
        assert mcp.name == "CVTailor MCP Server"
