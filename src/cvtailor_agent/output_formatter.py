"""Output formatting for generated application packs."""

from __future__ import annotations

import re
from typing import Iterable

from cvtailor_agent.state import CVTailorState


REQUIRED_SECTION_HEADINGS = [
	"## Job Requirement Summary",
	"## Candidate Match Score",
	"## Matched Skills Table",
	"## Tailored Resume Summary",
	"## Tailored Resume Bullets",
	"## Short Cover Letter",
	"## Gap Analysis",
	"## Next Actions",
]


def format_application_pack(state: CVTailorState) -> str:
	"""Build a complete Markdown application pack from workflow state."""
	company = state["company"]
	role = state["role"]
	requirements_text = _stringify_requirements(state.get("requirements"))
	profile = state.get("profile") or {}
	evidence = state.get("evidence") or []
	draft = state.get("draft_application_pack") or ""
	improved = state.get("final_application_pack") or ""

	requirement_items = _extract_requirement_items(requirements_text)
	matched_skills = _collect_matched_skills(requirement_items, profile, evidence)
	match_score = _calculate_match_score(requirement_items, matched_skills)
	cover_letter = _build_cover_letter(company, role, profile, evidence, improved or draft)
	tailored_summary = _build_resume_summary(role, company, profile, evidence)
	tailored_bullets = _build_resume_bullets(evidence)
	gap_analysis = _build_gap_analysis(requirement_items, matched_skills)
	next_actions = _build_next_actions(gap_analysis)

	sections = [
		f"# Application Pack: {role} at {company}",
		"",
		"## Job Requirement Summary",
		_build_requirement_summary(requirement_items, requirements_text),
		"",
		"## Candidate Match Score",
		(
			f"Heuristic match score: **{match_score}/100** based on overlap between "
			"job requirements and documented profile skills or resume evidence."
		),
		"",
		"## Matched Skills Table",
		_build_skills_table(matched_skills),
		"",
		"## Tailored Resume Summary",
		tailored_summary,
		"",
		"## Tailored Resume Bullets",
		tailored_bullets,
		"",
		"## Short Cover Letter",
		cover_letter,
		"",
		"## Gap Analysis",
		gap_analysis,
		"",
		"## Next Actions",
		next_actions,
		"",
	]
	return "\n".join(sections)


def ensure_required_sections(markdown_text: str, state: CVTailorState) -> str:
	"""Ensure all required headings are present, adding fallback content if needed."""
	normalized = markdown_text or ""
	if not normalized.strip().startswith("# Application Pack:"):
		normalized = format_application_pack(state)

	missing = [heading for heading in REQUIRED_SECTION_HEADINGS if heading not in normalized]
	if not missing:
		return normalized

	fallback = format_application_pack(state)
	for heading in missing:
		section_text = _extract_section_block(fallback, heading)
		if section_text:
			normalized = normalized.rstrip() + "\n\n" + section_text.strip() + "\n"
	return normalized


def _stringify_requirements(requirements: object) -> str:
	if requirements is None:
		return ""
	if isinstance(requirements, dict):
		parts: list[str] = []
		for key, value in requirements.items():
			parts.append(f"{key}: {value}")
		return "\n".join(parts)
	return str(requirements)


def _extract_requirement_items(requirements_text: str) -> list[str]:
	items: list[str] = []
	for line in requirements_text.splitlines():
		cleaned = line.strip()
		if not cleaned:
			continue
		cleaned = re.sub(r"^[-*]\s+", "", cleaned)
		cleaned = re.sub(r"^\d+[.)]\s+", "", cleaned)
		if cleaned.startswith("#") or cleaned.endswith(":"):
			continue
		items.append(cleaned)

	if items:
		return items[:8]

	sentences = re.split(r"(?<=[.!?])\s+", requirements_text.strip())
	return [sentence.strip() for sentence in sentences if sentence.strip()][:5]


def _collect_matched_skills(
	requirement_items: list[str],
	profile: dict,
	evidence: list[dict],
) -> list[tuple[str, str]]:
	skills = profile.get("skills") or []
	if not isinstance(skills, list):
		skills = [str(skills)]

	evidence_text = " ".join(item.get("text", "") for item in evidence).lower()
	matches: list[tuple[str, str]] = []
	seen: set[str] = set()

	for skill in skills:
		skill_text = str(skill).strip()
		if not skill_text:
			continue
		skill_lower = skill_text.lower()
		for item in requirement_items:
			item_lower = item.lower()
			if skill_lower in item_lower or any(token in item_lower for token in _keyword_tokens(skill_text)):
				source = _find_evidence_source(skill_text, evidence_text, evidence)
				key = skill_lower
				if key not in seen:
					matches.append((skill_text, source))
					seen.add(key)
				break

	if matches:
		return matches[:8]

	fallback_matches: list[tuple[str, str]] = []
	for item in evidence[:5]:
		snippet = _compact_text(item.get("text", ""), 90)
		if snippet:
			fallback_matches.append((item.get("section", "Resume evidence"), snippet))
	return fallback_matches


def _calculate_match_score(requirement_items: list[str], matched_skills: list[tuple[str, str]]) -> int:
	if not requirement_items:
		return 50 if matched_skills else 0
	ratio = min(len(matched_skills), len(requirement_items)) / len(requirement_items)
	return int(round(ratio * 100))


def _build_requirement_summary(requirement_items: list[str], requirements_text: str) -> str:
	if requirement_items:
		return "\n".join(f"- {item}" for item in requirement_items)
	fallback = _compact_text(requirements_text, 400) or "- No requirement summary available."
	if fallback.startswith("-"):
		return fallback
	return f"- {fallback}"


def _build_skills_table(matched_skills: list[tuple[str, str]]) -> str:
	lines = ["| Skill / Theme | Grounding |", "| --- | --- |"]
	if not matched_skills:
		lines.append("| No direct skill match extracted | Resume evidence needs manual review |")
		return "\n".join(lines)
	for skill, grounding in matched_skills:
		lines.append(f"| {skill} | {grounding} |")
	return "\n".join(lines)


def _build_resume_summary(role: str, company: str, profile: dict, evidence: list[dict]) -> str:
	summary = str(profile.get("summary", "")).strip()
	evidence_snippets = [
		_compact_text(item.get("text", ""), 120)
		for item in evidence[:2]
		if item.get("text")
	]
	evidence_text = " ".join(snippet for snippet in evidence_snippets if snippet)
	pieces = [
		f"This profile is aligned to the {role} role at {company} through documented experience in the resume and candidate profile.",
	]
	if summary:
		pieces.append(summary)
	if evidence_text:
		pieces.append(f"Relevant resume evidence includes: {evidence_text}")
	return "\n\n".join(pieces)


def _build_resume_bullets(evidence: list[dict]) -> str:
	bullets: list[str] = []
	for item in evidence[:5]:
		text = _compact_text(item.get("text", ""), 180)
		if text:
			bullets.append(f"- {text}")
	if bullets:
		return "\n".join(bullets)
	return "- Resume evidence was not extracted automatically; review the source resume before sending."


def _build_cover_letter(
	company: str,
	role: str,
	profile: dict,
	evidence: list[dict],
	llm_text: str,
) -> str:
	extracted = _extract_cover_letter_paragraphs(llm_text)
	if extracted:
		return extracted

	name = profile.get("name", "The candidate")
	summary = str(profile.get("summary", "")).strip()
	snippet = _compact_text(evidence[0].get("text", ""), 160) if evidence else ""
	paragraphs = [
		f"Dear Hiring Manager,\n\nI am applying for the {role} position at {company}. My background in Python, LLM application development, and agent workflows is documented in the attached profile and resume.",
	]
	if summary:
		paragraphs.append(summary)
	if snippet:
		paragraphs.append(f"One relevant example from my resume is: {snippet}")
	paragraphs.append(f"I would welcome the opportunity to discuss how {name}'s documented experience can support your team.")
	return "\n\n".join(paragraphs)


def _build_gap_analysis(requirement_items: list[str], matched_skills: list[tuple[str, str]]) -> str:
	matched_text = " ".join(skill.lower() for skill, _ in matched_skills)
	gaps: list[str] = []
	for item in requirement_items[:5]:
		tokens = _keyword_tokens(item)
		if tokens and not any(token in matched_text for token in tokens):
			gaps.append(item)

	if gaps:
		return "\n".join(
			f"- {gap}: no direct supporting evidence was automatically matched and should be addressed carefully."
			for gap in gaps[:4]
		)
	return "- No major unsupported requirement themes were detected from the current profile and resume evidence."


def _build_next_actions(gap_analysis: str) -> str:
	actions = [
		"- Review the matched skills table against the job post before sending.",
		"- Edit the cover letter tone and specifics for the target company.",
	]
	if "no direct supporting evidence" in gap_analysis:
		actions.append("- Remove or soften claims for gaps that are not directly supported by the resume.")
	else:
		actions.append("- Validate that each highlighted claim is present in the resume or profile source files.")
	return "\n".join(actions)


def _extract_cover_letter_paragraphs(llm_text: str) -> str:
	text = llm_text.strip()
	if not text:
		return ""
	if "Dear Hiring Manager" in text or "Dear " in text:
		return text
	return ""


def _extract_section_block(markdown_text: str, heading: str) -> str:
	pattern = re.escape(heading)
	match = re.search(rf"(^{pattern}.*?)(?=^##\s|\Z)", markdown_text, flags=re.MULTILINE | re.DOTALL)
	if not match:
		return ""
	return match.group(1).strip()


def _find_evidence_source(skill: str, evidence_text: str, evidence: list[dict]) -> str:
	skill_lower = skill.lower()
	if skill_lower in evidence_text:
		for item in evidence:
			text = item.get("text", "")
			if skill_lower in text.lower():
				return _compact_text(text, 100)
	return "Listed in candidate profile skills"


def _compact_text(text: str, limit: int) -> str:
	cleaned = " ".join(text.split())
	if len(cleaned) <= limit:
		return cleaned
	return cleaned[: limit - 3].rstrip() + "..."


def _keyword_tokens(text: str) -> list[str]:
	return [token for token in re.findall(r"[a-zA-Z][a-zA-Z0-9+/.-]+", text.lower()) if len(token) > 2]
