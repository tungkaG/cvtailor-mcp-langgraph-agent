"""LangGraph workflow definition for CVTailor agent.

This module defines the agent workflow as a LangGraph StateGraph with 9 nodes:
1. load_job_description - Load job description from file
2. extract_requirements_with_llm - Extract key requirements using LLM
3. get_candidate_profile_from_mcp - Get profile via MCP tool
4. search_resume_evidence_from_mcp - Search resume via MCP tool
5. generate_application_pack_with_llm - Generate initial draft
6. review_application_pack_with_llm - Review the draft
7. improve_application_pack_with_llm - Improve based on feedback
8. save_application_pack_with_mcp - Save final pack via MCP
9. log_application_with_mcp - Log to database via MCP

Graph flow:
START -> load_job_description -> extract_requirements -> get_profile ->
search_evidence -> generate_draft -> review -> improve -> save -> log -> END
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from langgraph.graph import StateGraph, START, END

from cvtailor_agent.llm import get_llm
from cvtailor_agent.mcp_client import MCPClient
from cvtailor_agent.output_formatter import format_application_pack
from cvtailor_agent.prompts import (
    REQUIREMENT_EXTRACTION_PROMPT,
    DRAFT_APPLICATION_PROMPT,
    REVIEW_PROMPT,
    IMPROVE_PROMPT,
)
from cvtailor_agent.state import CVTailorState

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph


# -----------------------------------------------------------------------------
# Node Functions
# -----------------------------------------------------------------------------


def load_job_description(state: CVTailorState) -> dict:
    """Load job description from file.

    Args:
        state: Current workflow state with job_file path.

    Returns:
        Updated state with job_description.

    Raises:
        FileNotFoundError: If job file doesn't exist.
    """
    job_file = Path(state["job_file"])

    if not job_file.exists():
        raise FileNotFoundError(f"Job description file not found: {job_file}")

    job_description = job_file.read_text(encoding="utf-8")

    return {"job_description": job_description}


def extract_requirements_with_llm(state: CVTailorState) -> dict:
    """Extract key requirements from job description using LLM.

    Args:
        state: Current workflow state with job_description.

    Returns:
        Updated state with requirements.
    """
    llm = get_llm()

    prompt = REQUIREMENT_EXTRACTION_PROMPT.format(
        job_description=state.get("job_description", ""),
        company=state["company"],
        role=state["role"],
    )

    requirements = llm.invoke(prompt)

    return {"requirements": requirements}


def get_candidate_profile_from_mcp(state: CVTailorState) -> dict:
    """Get candidate profile using MCP tool.

    Args:
        state: Current workflow state.

    Returns:
        Updated state with profile.
    """
    client = MCPClient()
    profile = client.get_candidate_profile()

    return {"profile": profile}


def search_resume_evidence_from_mcp(state: CVTailorState) -> dict:
    """Search resume for evidence matching job requirements.

    Uses requirements text to build search query.

    Args:
        state: Current workflow state with requirements.

    Returns:
        Updated state with evidence list.
    """
    client = MCPClient()

    # Build search query from requirements
    requirements = state.get("requirements", "")
    if isinstance(requirements, dict):
        # If requirements is a dict, convert to string
        requirements = json.dumps(requirements)

    # Extract key terms for search (use role + first 200 chars of requirements)
    search_query = f"{state['role']} {requirements[:200]}"

    evidence = client.search_resume_evidence(search_query, top_k=5)

    return {"evidence": evidence}


def generate_application_pack_with_llm(state: CVTailorState) -> dict:
    """Generate initial application pack draft using LLM.

    Args:
        state: Current workflow state with requirements, profile, and evidence.

    Returns:
        Updated state with draft_application_pack.
    """
    llm = get_llm()

    # Format profile for prompt
    profile = state.get("profile", {})
    profile_text = _format_profile(profile)

    # Format evidence for prompt
    evidence = state.get("evidence", [])
    evidence_text = _format_evidence(evidence)

    # Format requirements
    requirements = state.get("requirements", "")
    if isinstance(requirements, dict):
        requirements = json.dumps(requirements, indent=2)

    prompt = DRAFT_APPLICATION_PROMPT.format(
        requirements=requirements,
        profile=profile_text,
        resume_evidence=evidence_text,
        company=state["company"],
        role=state["role"],
    )

    draft = llm.invoke(prompt)

    return {"draft_application_pack": draft}


def review_application_pack_with_llm(state: CVTailorState) -> dict:
    """Review application pack and provide feedback using LLM.

    Args:
        state: Current workflow state with draft_application_pack.

    Returns:
        Updated state with review_feedback.
    """
    llm = get_llm()

    # Format requirements
    requirements = state.get("requirements", "")
    if isinstance(requirements, dict):
        requirements = json.dumps(requirements, indent=2)

    prompt = REVIEW_PROMPT.format(
        draft=state.get("draft_application_pack", ""),
        requirements=requirements,
        company=state["company"],
        role=state["role"],
    )

    feedback = llm.invoke(prompt)

    return {"review_feedback": feedback}


def improve_application_pack_with_llm(state: CVTailorState) -> dict:
    """Improve application pack based on review feedback using LLM.

    Args:
        state: Current workflow state with draft and feedback.

    Returns:
        Updated state with final_application_pack.
    """
    llm = get_llm()

    # Format requirements
    requirements = state.get("requirements", "")
    if isinstance(requirements, dict):
        requirements = json.dumps(requirements, indent=2)

    prompt = IMPROVE_PROMPT.format(
        draft=state.get("draft_application_pack", ""),
        feedback=state.get("review_feedback", ""),
        requirements=requirements,
        company=state["company"],
        role=state["role"],
    )

    improved = llm.invoke(prompt)

    formatted_pack = format_application_pack(
        {
            **state,
            "final_application_pack": improved,
        }
    )

    return {"final_application_pack": formatted_pack}


def save_application_pack_with_mcp(state: CVTailorState) -> dict:
    """Save the final application pack using MCP tool.

    Args:
        state: Current workflow state with final_application_pack.

    Returns:
        Updated state with output_path.
    """
    client = MCPClient()

    # Use final pack, or fall back to draft if improvement failed
    content = state.get("final_application_pack") or state.get("draft_application_pack", "")

    result = client.save_application_pack(
        company=state["company"],
        role=state["role"],
        content=content,
    )

    return {"output_path": result.get("output_path")}


def log_application_with_mcp(state: CVTailorState) -> dict:
    """Log the application to the tracking database using MCP tool.

    Args:
        state: Current workflow state with output_path.

    Returns:
        Updated state with application_id.
    """
    client = MCPClient()

    result = client.log_application(
        company=state["company"],
        role=state["role"],
        status="drafted",
        notes="Generated via CVTailor LangGraph agent",
        output_path=state.get("output_path", ""),
    )

    return {"application_id": result.get("id")}


# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------


def _format_profile(profile: dict) -> str:
    """Format profile dict as readable text for LLM prompt.

    Args:
        profile: Profile dictionary.

    Returns:
        Formatted string representation.
    """
    if not profile:
        return "No profile available"

    lines = []

    if "name" in profile:
        lines.append(f"Name: {profile['name']}")

    if "title" in profile:
        lines.append(f"Title: {profile['title']}")

    if "summary" in profile:
        lines.append(f"\nSummary: {profile['summary']}")

    if "skills" in profile:
        skills = profile["skills"]
        if isinstance(skills, list):
            lines.append(f"\nSkills: {', '.join(skills)}")
        else:
            lines.append(f"\nSkills: {skills}")

    if "experience_years" in profile:
        lines.append(f"\nYears of Experience: {profile['experience_years']}")

    return "\n".join(lines)


def _format_evidence(evidence: list[dict]) -> str:
    """Format evidence list as readable text for LLM prompt.

    Args:
        evidence: List of evidence dictionaries.

    Returns:
        Formatted string representation.
    """
    if not evidence:
        return "No relevant resume sections found"

    lines = []
    for i, item in enumerate(evidence, 1):
        section = item.get("section", "Unknown")
        text = item.get("text", "")
        score = item.get("score", 0)

        lines.append(f"--- Section {i}: {section} (relevance: {score:.2f}) ---")
        lines.append(text)
        lines.append("")

    return "\n".join(lines)


# -----------------------------------------------------------------------------
# Graph Builder
# -----------------------------------------------------------------------------


def build_graph() -> "CompiledStateGraph":
    """Build and compile the CVTailor LangGraph workflow.

    Returns:
        Compiled LangGraph StateGraph ready for invocation.

    Example:
        graph = build_graph()
        result = graph.invoke({
            "company": "Acme Corp",
            "role": "AI Engineer",
            "job_file": "job_description.txt"
        })
    """
    # Create the state graph
    graph = StateGraph(CVTailorState)

    # Add all nodes
    graph.add_node("load_job_description", load_job_description)
    graph.add_node("extract_requirements", extract_requirements_with_llm)
    graph.add_node("get_profile", get_candidate_profile_from_mcp)
    graph.add_node("search_evidence", search_resume_evidence_from_mcp)
    graph.add_node("generate_draft", generate_application_pack_with_llm)
    graph.add_node("review_draft", review_application_pack_with_llm)
    graph.add_node("improve_draft", improve_application_pack_with_llm)
    graph.add_node("save_pack", save_application_pack_with_mcp)
    graph.add_node("log_application", log_application_with_mcp)

    # Define the linear flow
    graph.add_edge(START, "load_job_description")
    graph.add_edge("load_job_description", "extract_requirements")
    graph.add_edge("extract_requirements", "get_profile")
    graph.add_edge("get_profile", "search_evidence")
    graph.add_edge("search_evidence", "generate_draft")
    graph.add_edge("generate_draft", "review_draft")
    graph.add_edge("review_draft", "improve_draft")
    graph.add_edge("improve_draft", "save_pack")
    graph.add_edge("save_pack", "log_application")
    graph.add_edge("log_application", END)

    # Compile and return
    return graph.compile()
