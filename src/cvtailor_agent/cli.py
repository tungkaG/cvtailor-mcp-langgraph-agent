"""Typer CLI for the CVTailor agent.

This module provides CLI commands for:
- Running the full agent workflow
- Listing tracked applications
- Inspecting the candidate profile
- Testing resume search functionality
"""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from cvtailor_agent.graph import build_graph
from cvtailor_agent.mcp_client import MCPClient

app = typer.Typer(
    name="cvtailor",
    help="AI job-application assistant using MCP and LangGraph.",
    no_args_is_help=True,
)

console = Console()


@app.command()
def run(
    job_file: str = typer.Option(..., "--job-file", help="Path to job description file"),
    company: str = typer.Option(..., "--company", help="Company name"),
    role: str = typer.Option(..., "--role", help="Role/position name"),
) -> None:
    """Run the CVTailor agent to generate an application pack.

    Example:
        python -m cvtailor_agent.cli run --job-file examples/job_description_ai_engineer.txt --company "Acme AI" --role "AI Engineer"
    """
    # Validate job file exists
    job_path = Path(job_file)
    if not job_path.exists():
        console.print(f"[red]Error:[/red] Job file not found: {job_file}")
        raise typer.Exit(1)

    console.print(Panel.fit(
        f"[bold blue]CVTailor Agent[/bold blue]\n"
        f"Company: [green]{company}[/green]\n"
        f"Role: [green]{role}[/green]\n"
        f"Job File: [cyan]{job_file}[/cyan]",
        title="Starting Application Generation",
    ))

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Build the graph
            task = progress.add_task("Building workflow...", total=None)
            graph = build_graph()
            progress.update(task, description="[green]✓[/green] Workflow built")

            # Invoke the graph
            progress.update(task, description="Loading job description...")
            
            result = graph.invoke({
                "company": company,
                "role": role,
                "job_file": str(job_path.absolute()),
            })

            progress.update(task, description="[green]✓[/green] Application generated!")

        # Display results with workflow details
        console.print()

        # Extract workflow decision fields
        evidence_score = result.get("evidence_score", 0.0)
        evidence_quality = result.get("evidence_quality", "unknown")
        search_attempts = result.get("search_attempts", 0)
        review_status = result.get("review_status", "unknown")
        revision_count = result.get("revision_count", 0)
        output_path = result.get("output_path", "N/A")
        application_id = result.get("application_id", "N/A")

        # Color-code quality and status
        quality_color = "green" if evidence_quality == "strong" else "yellow"
        status_color = "green" if review_status == "approved" else "yellow"

        console.print(Panel.fit(
            f"[bold green]Success![/bold green]\n\n"
            f"[bold]Workflow Decisions:[/bold]\n"
            f"  Evidence Quality: [{quality_color}]{evidence_quality}[/{quality_color}]\n"
            f"  Evidence Score: [cyan]{evidence_score:.2f}[/cyan]\n"
            f"  Search Attempts: [cyan]{search_attempts}[/cyan]\n"
            f"  Review Status: [{status_color}]{review_status}[/{status_color}]\n"
            f"  Revision Count: [cyan]{revision_count}[/cyan]\n\n"
            f"[bold]Output:[/bold]\n"
            f"  Path: [cyan]{output_path}[/cyan]\n"
            f"  Application ID: [yellow]{application_id}[/yellow]",
            title="Results",
        ))

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("list-applications")
def list_applications(
    status: str | None = typer.Option(None, "--status", help="Filter by status"),
) -> None:
    """List all tracked job applications.

    Example:
        python -m cvtailor_agent.cli list-applications
        python -m cvtailor_agent.cli list-applications --status drafted
    """
    client = MCPClient()
    applications = client.list_applications(status=status)

    if not applications:
        console.print("[yellow]No applications found.[/yellow]")
        return

    # Create Rich table
    table = Table(title="Job Applications")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Company", style="green")
    table.add_column("Role", style="blue")
    table.add_column("Status", style="yellow")
    table.add_column("Created", style="dim")
    table.add_column("Notes", style="dim", max_width=30)

    for app_record in applications:
        table.add_row(
            str(app_record.get("id", "")),
            app_record.get("company", ""),
            app_record.get("role", ""),
            app_record.get("status", ""),
            app_record.get("created_at", "")[:19] if app_record.get("created_at") else "",
            (app_record.get("notes", "") or "")[:30],
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(applications)} application(s)[/dim]")


@app.command("inspect-profile")
def inspect_profile() -> None:
    """Display the candidate profile.

    Example:
        python -m cvtailor_agent.cli inspect-profile
    """
    client = MCPClient()
    profile = client.get_candidate_profile()

    if not profile:
        console.print("[yellow]No profile found.[/yellow]")
        return

    # Display profile in a nice format
    console.print(Panel.fit(
        f"[bold]{profile.get('name', 'Unknown')}[/bold]\n"
        f"[dim]{profile.get('title', '')}[/dim]",
        title="Candidate Profile",
    ))

    if profile.get("summary"):
        console.print(f"\n[bold]Summary:[/bold]\n{profile['summary']}")

    if profile.get("skills"):
        skills = profile["skills"]
        if isinstance(skills, list):
            skills_str = ", ".join(skills)
        else:
            skills_str = str(skills)
        console.print(f"\n[bold]Skills:[/bold]\n{skills_str}")

    if profile.get("experience_years"):
        console.print(f"\n[bold]Experience:[/bold] {profile['experience_years']} years")

    # Also show raw JSON for completeness
    console.print("\n[dim]Raw JSON:[/dim]")
    console.print_json(json.dumps(profile, indent=2))


@app.command("test-search")
def test_search(
    query: str = typer.Option(..., "--query", help="Search query keywords"),
    top_k: int = typer.Option(5, "--top-k", help="Number of results to return"),
) -> None:
    """Test resume search functionality.

    Example:
        python -m cvtailor_agent.cli test-search --query "Python LangGraph MCP"
    """
    client = MCPClient()
    results = client.search_resume_evidence(query, top_k=top_k)

    if not results:
        console.print(f"[yellow]No results found for query: {query}[/yellow]")
        return

    console.print(Panel.fit(
        f"Query: [cyan]{query}[/cyan]\n"
        f"Results: [green]{len(results)}[/green]",
        title="Resume Search Results",
    ))

    for i, result in enumerate(results, 1):
        section = result.get("section", "Unknown")
        score = result.get("score", 0)
        text = result.get("text", "")

        # Truncate long text
        if len(text) > 300:
            text = text[:300] + "..."

        console.print(f"\n[bold cyan]Result {i}:[/bold cyan] {section}")
        console.print(f"[dim]Score: {score:.3f}[/dim]")
        console.print(Panel(text, border_style="dim"))


if __name__ == "__main__":
    app()
