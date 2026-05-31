"""Typer CLI for the CVTailor agent.

This module will contain:
- CLI commands for running the agent
- Job file and company/role argument handling
"""

import typer

app = typer.Typer(
    name="cvtailor",
    help="AI job-application assistant using MCP and LangGraph.",
)


@app.command()
def run(
    job_file: str = typer.Option(..., "--job-file", help="Path to job description file"),
    company: str = typer.Option(..., "--company", help="Company name"),
    role: str = typer.Option(..., "--role", help="Role/position name"),
) -> None:
    """Run the CVTailor agent to generate an application pack."""
    typer.echo(f"Processing job application for {role} at {company}")
    typer.echo(f"Job file: {job_file}")
    typer.echo("CLI placeholder - implementation in later phase")


if __name__ == "__main__":
    app()
