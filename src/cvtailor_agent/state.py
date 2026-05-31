"""Agent state definitions.

This module defines the CVTailorState TypedDict used by the LangGraph workflow.
"""

from __future__ import annotations

from typing import TypedDict


class CVTailorState(TypedDict, total=False):
    """State for the CVTailor agent workflow.

    All fields except company, role, and job_file are optional.
    The workflow progressively populates state as it moves through nodes.

    Attributes:
        company: Target company name (required).
        role: Target role/position (required).
        job_file: Path to job description file (required).
        job_description: Raw job description text loaded from file.
        requirements: Extracted requirements from job description.
        profile: Candidate profile from MCP tool.
        evidence: Resume sections matching job requirements.
        draft_application_pack: Initial generated application pack.
        review_feedback: Feedback from review step.
        final_application_pack: Improved application pack.
        output_path: Path where final pack was saved.
        application_id: ID from application tracking database.

    Conditional routing fields (for evidence quality routing):
        evidence_score: Average score of resume evidence (0.0-1.0).
        evidence_quality: Quality label ("unknown", "weak", "strong").
        search_attempts: Number of search attempts made.
        max_search_attempts: Maximum search attempts before fallback.
        expanded_search_query: Broader query for weak evidence fallback.

    Conditional routing fields (for review/revision loop):
        review_status: Review classification ("unknown", "approved", "needs_revision").
        revision_count: Number of revision iterations completed.
        max_revisions: Maximum revisions before forced save.
        route_reason: Explanation of routing decision for debugging.
    """

    # Required inputs
    company: str
    role: str
    job_file: str

    # Populated during workflow
    job_description: str | None
    requirements: dict | str | None
    profile: dict | None
    evidence: list[dict] | None
    draft_application_pack: str | None
    review_feedback: str | None
    final_application_pack: str | None
    output_path: str | None
    application_id: int | None

    # Conditional routing: evidence quality
    evidence_score: float
    evidence_quality: str
    search_attempts: int
    max_search_attempts: int
    expanded_search_query: str

    # Conditional routing: review/revision loop
    review_status: str
    revision_count: int
    max_revisions: int
    route_reason: str


# Default values for conditional routing fields
DEFAULT_STATE_VALUES: dict = {
    "evidence_score": 0.0,
    "evidence_quality": "unknown",
    "search_attempts": 0,
    "max_search_attempts": 2,
    "expanded_search_query": "",
    "review_status": "unknown",
    "revision_count": 0,
    "max_revisions": 2,
    "route_reason": "",
}
