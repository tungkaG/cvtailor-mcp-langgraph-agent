"""LangGraph workflow definition for CVTailor agent.

This module defines the agent workflow as a LangGraph StateGraph with 12 nodes:
1. load_job_description - Load job description from file
2. extract_requirements_with_llm - Extract key requirements using LLM
3. get_candidate_profile_from_mcp - Get profile via MCP tool
4. search_resume_evidence_from_mcp - Search resume via MCP tool
5. score_resume_evidence - Score evidence quality for routing
6. broaden_search_query - Generate broader search query for weak evidence
7. search_resume_evidence_again - Retry search with expanded query
8. generate_application_pack_with_llm - Generate initial draft
9. review_application_pack_with_llm - Review the draft
10. improve_application_pack_with_llm - Improve based on feedback
11. save_application_pack_with_mcp - Save final pack via MCP
12. log_application_with_mcp - Log to database via MCP

Graph flow with conditional routing:
START -> load_job_description -> extract_requirements -> get_profile ->
search_evidence -> score_evidence ->
  [strong_match] -> generate_draft
  [weak_match] -> broaden_search -> search_again -> score_evidence
  [continue_anyway] -> generate_draft
-> review -> improve -> save -> log -> END
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


def score_resume_evidence(state: CVTailorState) -> dict:
    """Score the quality of resume evidence for conditional routing.

    Calculates an average score from evidence items and assigns a quality label.
    This enables the graph to route differently based on evidence strength.

    Args:
        state: Current workflow state with evidence list.

    Returns:
        Updated state with evidence_score, evidence_quality, and route_reason.
    """
    evidence = state.get("evidence") or []

    # No evidence case
    if not evidence:
        return {
            "evidence_score": 0.0,
            "evidence_quality": "weak",
            "route_reason": "No resume evidence found",
        }

    # Calculate average score from evidence items
    scores = []
    for item in evidence:
        # Only include scores that are explicitly present
        if "score" in item:
            score = item["score"]
            if isinstance(score, (int, float)):
                scores.append(float(score))

    if not scores:
        return {
            "evidence_score": 0.0,
            "evidence_quality": "weak",
            "route_reason": "Evidence items have no scores",
        }

    average_score = sum(scores) / len(scores)

    # Determine quality based on threshold
    if average_score >= 0.50:
        quality = "strong"
        reason = f"Evidence score {average_score:.2f} >= 0.50 threshold"
    else:
        quality = "weak"
        reason = f"Evidence score {average_score:.2f} < 0.50 threshold"

    return {
        "evidence_score": average_score,
        "evidence_quality": quality,
        "route_reason": reason,
    }


# -----------------------------------------------------------------------------
# Router Functions
# -----------------------------------------------------------------------------


def route_after_evidence_scoring(state: CVTailorState) -> str:
    """Route based on evidence quality after scoring.

    Determines the next step based on evidence strength and search attempts:
    - strong evidence -> proceed to generation
    - weak evidence with attempts remaining -> broaden search
    - max attempts reached -> continue anyway

    Args:
        state: Current workflow state with evidence_quality and search_attempts.

    Returns:
        Route key: "strong_match", "weak_match", or "continue_anyway".
    """
    evidence_quality = state.get("evidence_quality", "unknown")
    search_attempts = state.get("search_attempts", 0)
    max_search_attempts = state.get("max_search_attempts", 2)

    if evidence_quality == "strong":
        return "strong_match"

    if search_attempts >= max_search_attempts:
        return "continue_anyway"

    return "weak_match"


def route_after_review(state: CVTailorState) -> str:
    """Route based on review classification and revision limits.

    Determines whether the workflow can save immediately, needs another
    improvement pass, or must stop revising because the maximum number of
    revisions has been reached.

    Args:
        state: Current workflow state with review_status and revision_count.

    Returns:
        Route key: "approved", "needs_revision", or "max_revisions_reached".
    """
    review_status = state.get("review_status", "unknown")
    revision_count = state.get("revision_count", 0)
    max_revisions = state.get("max_revisions", 2)

    if review_status == "approved":
        return "approved"

    if revision_count >= max_revisions:
        return "max_revisions_reached"

    return "needs_revision"


# -----------------------------------------------------------------------------
# Fallback Search Nodes
# -----------------------------------------------------------------------------


def broaden_search_query(state: CVTailorState) -> dict:
    """Generate a broader search query for weak evidence fallback.

    Creates an expanded query using role, requirements, and candidate skills
    to increase the chance of finding relevant resume evidence.

    Args:
        state: Current workflow state with role, requirements, and profile.

    Returns:
        Updated state with expanded_search_query and incremented search_attempts.
    """
    role = state.get("role", "")
    requirements = state.get("requirements", "")
    profile = state.get("profile") or {}

    # Extract skills from profile if available
    skills = profile.get("skills", [])
    if isinstance(skills, list):
        skills_text = " ".join(skills[:10])  # Limit to first 10 skills
    else:
        skills_text = str(skills)

    # Convert requirements to string if dict
    if isinstance(requirements, dict):
        requirements = json.dumps(requirements)

    # Build expanded query combining multiple sources
    query_parts = [
        role,
        skills_text,
        requirements[:300] if requirements else "",  # Use more of requirements
    ]

    expanded_query = " ".join(part for part in query_parts if part)

    # Increment search attempts
    current_attempts = state.get("search_attempts", 0)

    return {
        "expanded_search_query": expanded_query,
        "search_attempts": current_attempts + 1,
    }


def search_resume_evidence_again(state: CVTailorState) -> dict:
    """Retry resume search with the expanded search query.

    Uses the broader search query generated by broaden_search_query node
    to find more relevant resume evidence.

    Args:
        state: Current workflow state with expanded_search_query.

    Returns:
        Updated state with new evidence list.
    """
    client = MCPClient()

    # Use expanded query if available, otherwise fall back to original approach
    search_query = state.get("expanded_search_query", "")

    if not search_query:
        # Fall back to original query construction
        requirements = state.get("requirements", "")
        if isinstance(requirements, dict):
            requirements = json.dumps(requirements)
        search_query = f"{state['role']} {requirements[:200]}"

    evidence = client.search_resume_evidence(search_query, top_k=5)

    return {"evidence": evidence}


# -----------------------------------------------------------------------------
# LLM Generation Nodes
# -----------------------------------------------------------------------------


def parse_review_response(response: str) -> tuple[str, str]:
    """Parse the structured review response from the LLM.

    Extracts the review status and feedback from the LLM response.
    Expected format:
        REVIEW_STATUS: approved
        FEEDBACK:
        ...

    Args:
        response: The raw LLM review response.

    Returns:
        Tuple of (status, feedback) where status is 'approved' or 'needs_revision'.
        Defaults to 'needs_revision' if parsing fails.
    """
    status = "needs_revision"  # Default if parsing fails
    feedback = response  # Use full response as feedback by default

    # Look for REVIEW_STATUS line
    lines = response.split("\n")
    for i, line in enumerate(lines):
        line_stripped = line.strip().upper()
        if line_stripped.startswith("REVIEW_STATUS:"):
            # Extract status value
            status_value = line.split(":", 1)[1].strip().lower()
            if "approved" in status_value:
                status = "approved"
            else:
                status = "needs_revision"

            # Extract feedback (everything after REVIEW_STATUS line)
            remaining_lines = lines[i + 1 :]
            # Skip empty lines and look for FEEDBACK header
            feedback_start = 0
            for j, fline in enumerate(remaining_lines):
                if fline.strip().upper().startswith("FEEDBACK"):
                    feedback_start = j + 1
                    break
            feedback = "\n".join(remaining_lines[feedback_start:]).strip()
            break

    return status, feedback


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

    Parses the structured response to extract review status and feedback.

    Args:
        state: Current workflow state with draft_application_pack.

    Returns:
        Updated state with review_status and review_feedback.
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

    response = llm.invoke(prompt)

    # Parse structured response
    status, feedback = parse_review_response(response)

    return {
        "review_status": status,
        "review_feedback": feedback,
    }


def improve_application_pack_with_llm(state: CVTailorState) -> dict:
    """Improve application pack based on review feedback using LLM.

    Args:
        state: Current workflow state with draft and feedback.

    Returns:
        Updated state with final_application_pack, draft_application_pack,
        and incremented revision_count.
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

    return {
        "draft_application_pack": formatted_pack,
        "final_application_pack": formatted_pack,
        "revision_count": state.get("revision_count", 0) + 1,
    }


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

    The workflow includes conditional routing based on evidence quality:
    - Strong evidence proceeds directly to generation
    - Weak evidence triggers broadened search (up to max_search_attempts)
    - After max attempts, continues with best available evidence
    - Review classification can trigger a bounded improve/review loop

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
    graph.add_node("score_evidence", score_resume_evidence)
    graph.add_node("broaden_search", broaden_search_query)
    graph.add_node("search_evidence_again", search_resume_evidence_again)
    graph.add_node("generate_draft", generate_application_pack_with_llm)
    graph.add_node("review_draft", review_application_pack_with_llm)
    graph.add_node("improve_draft", improve_application_pack_with_llm)
    graph.add_node("save_pack", save_application_pack_with_mcp)
    graph.add_node("log_application", log_application_with_mcp)

    # Define flow: START to scoring
    graph.add_edge(START, "load_job_description")
    graph.add_edge("load_job_description", "extract_requirements")
    graph.add_edge("extract_requirements", "get_profile")
    graph.add_edge("get_profile", "search_evidence")
    graph.add_edge("search_evidence", "score_evidence")

    # Conditional routing after evidence scoring
    graph.add_conditional_edges(
        "score_evidence",
        route_after_evidence_scoring,
        {
            "strong_match": "generate_draft",
            "continue_anyway": "generate_draft",
            "weak_match": "broaden_search",
        },
    )

    # Fallback search path
    graph.add_edge("broaden_search", "search_evidence_again")
    graph.add_edge("search_evidence_again", "score_evidence")

    # Generation through review
    graph.add_edge("generate_draft", "review_draft")

    # Conditional routing after review classification
    graph.add_conditional_edges(
        "review_draft",
        route_after_review,
        {
            "approved": "save_pack",
            "max_revisions_reached": "save_pack",
            "needs_revision": "improve_draft",
        },
    )

    # Bounded revision loop
    graph.add_edge("improve_draft", "review_draft")

    # Completion
    graph.add_edge("save_pack", "log_application")
    graph.add_edge("log_application", END)

    # Compile and return
    return graph.compile()
