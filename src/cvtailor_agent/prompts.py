"""Prompt templates for the CVTailor agent.

This module provides LangChain prompt templates for the agent workflow:
- REQUIREMENT_EXTRACTION_PROMPT: Extract key requirements from job descriptions
- DRAFT_APPLICATION_PROMPT: Generate initial application materials
- REVIEW_PROMPT: Review and provide feedback on drafts
- IMPROVE_PROMPT: Improve drafts based on feedback
"""

from langchain_core.prompts import PromptTemplate


# Template for extracting requirements from job descriptions
REQUIREMENT_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["job_description", "company", "role"],
    template="""You are an expert job analyst. Extract the key requirements from the following job description.

Company: {company}
Role: {role}

Job Description:
{job_description}

Please identify and extract:
1. Technical Skills Required - List specific technologies, tools, and technical competencies
2. Soft Skills Required - Communication, teamwork, leadership abilities needed
3. Experience Level - Years of experience and educational requirements
4. Key Responsibilities - Main duties and expectations for the role

Format your response with clear headers and bullet points for each section.""",
)


# Template for generating initial draft application materials
DRAFT_APPLICATION_PROMPT = PromptTemplate(
    input_variables=["requirements", "profile", "resume_evidence", "company", "role"],
    template="""You are an expert cover letter writer. Create a compelling draft cover letter based on the following information.

Company: {company}
Role: {role}

Job Requirements:
{requirements}

Candidate Profile:
{profile}

Relevant Experience from Resume:
{resume_evidence}

Write a professional cover letter that:
1. Opens with enthusiasm for the specific role and company
2. Highlights 2-3 key experiences that directly match the requirements
3. Demonstrates knowledge of the company (if available)
4. Includes specific achievements with metrics where possible
5. Closes with a clear call to action

Keep the letter concise (300-400 words) and professional.""",
)


# Template for reviewing draft application materials
REVIEW_PROMPT = PromptTemplate(
    input_variables=["draft", "requirements", "company", "role"],
    template="""You are an expert career coach reviewing a job application. Provide constructive feedback on the following draft.

Company: {company}
Role: {role}

Job Requirements:
{requirements}

Draft to Review:
{draft}

Please evaluate the draft and provide your response in this exact format:

REVIEW_STATUS: [approved OR needs_revision]

FEEDBACK:
1. Strengths - What works well in this draft?
2. Areas for Improvement - What could be better?
3. Alignment with Requirements - How well does it address the job requirements?
4. Overall Assessment - Rating out of 10 with justification
5. Priority Suggestions - Top 3 specific changes to make

Use REVIEW_STATUS: approved if the draft is ready to send (score 8/10 or higher).
Use REVIEW_STATUS: needs_revision if improvements are needed (score below 8/10).

Be specific and actionable in your feedback.""",
)


# Template for improving drafts based on review feedback
IMPROVE_PROMPT = PromptTemplate(
    input_variables=["draft", "feedback", "requirements", "company", "role"],
    template="""You are an expert cover letter writer. Improve the following draft based on the feedback provided.

Company: {company}
Role: {role}

Original Draft:
{draft}

Feedback to Address:
{feedback}

Job Requirements:
{requirements}

Please revise and enhance the draft by:
1. Addressing each point raised in the feedback
2. Adding more specific achievements and metrics
3. Strengthening alignment with the job requirements
4. Improving the opening and closing paragraphs
5. Ensuring a professional yet personable tone

Provide the complete improved version of the cover letter.""",
)
