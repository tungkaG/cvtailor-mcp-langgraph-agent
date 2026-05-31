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
