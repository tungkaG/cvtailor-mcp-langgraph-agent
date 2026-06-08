"""LLM abstraction layer.

This module provides:
- MockLLM for local demos and testing
- HuggingFaceLLM for real LLM calls via Hugging Face Inference API
- LLM provider factory with environment-based selection
"""

from __future__ import annotations

import os
from typing import Any, Protocol

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Default Hugging Face model and parameters
DEFAULT_HF_MODEL = "Qwen/Qwen2.5-72B-Instruct"
DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_NEW_TOKENS = 900


class LLMProtocol(Protocol):
    """Protocol defining the LLM interface."""

    def invoke(self, prompt: str) -> str:
        """Generate a response for the given prompt."""
        ...


class MockLLM:
    """Mock LLM for testing and local demos.

    Returns deterministic, useful text based on prompt content.
    Detects prompt type using simple keyword matching.
    """

    def invoke(self, prompt: str) -> str:
        """Generate a mock response based on prompt content.

        Handles four prompt types:
        1. Requirement extraction - extracts key requirements
        2. Draft generation - creates application materials
        3. Review - provides feedback on drafts
        4. Improvement - suggests enhanced versions

        Args:
            prompt: The input prompt text.

        Returns:
            A deterministic response based on detected prompt type.
        """
        prompt_lower = prompt.lower()

        # Detect prompt type and return appropriate response
        # Order matters: improvement/review often contain overlapping keywords
        # Check in priority order: requirement extraction > improvement > review > draft
        if self._is_requirement_extraction(prompt_lower):
            return self._requirement_extraction_response()
        elif self._is_improvement(prompt_lower):
            return self._improvement_response()
        elif self._is_review(prompt_lower):
            return self._review_response()
        elif self._is_draft_generation(prompt_lower):
            return self._draft_generation_response()
        else:
            return self._default_response()

    def _is_requirement_extraction(self, prompt: str) -> bool:
        """Check if prompt is for requirement extraction."""
        keywords = ["extract", "requirement", "identify", "key skills", "job description"]
        return any(kw in prompt for kw in keywords)

    def _is_draft_generation(self, prompt: str) -> bool:
        """Check if prompt is for draft generation."""
        keywords = ["draft", "write", "generate", "cover letter", "application", "create"]
        return any(kw in prompt for kw in keywords)

    def _is_review(self, prompt: str) -> bool:
        """Check if prompt is for review."""
        keywords = ["review", "feedback", "evaluate", "critique", "assess"]
        return any(kw in prompt for kw in keywords)

    def _is_improvement(self, prompt: str) -> bool:
        """Check if prompt is for improvement."""
        keywords = ["improve", "enhance", "revise", "refine", "strengthen"]
        return any(kw in prompt for kw in keywords)

    def _requirement_extraction_response(self) -> str:
        """Return mock requirement extraction response."""
        return """## Extracted Requirements

### Technical Skills Required
- Python programming (3+ years)
- Machine Learning / Deep Learning experience
- LLM and NLP experience
- API development (REST, FastAPI)
- Cloud platforms (AWS, GCP, or Azure)

### Soft Skills Required
- Strong communication skills
- Team collaboration
- Problem-solving ability

### Experience Level
- 3-5 years of relevant experience
- Bachelor's degree in Computer Science or related field

### Key Responsibilities
- Design and implement AI/ML solutions
- Collaborate with cross-functional teams
- Maintain and improve existing systems"""

    def _draft_generation_response(self) -> str:
        """Return mock draft generation response."""
        return """Dear Hiring Manager,

I am writing to express my strong interest in the AI Engineer position at your company. With my extensive experience in Python, machine learning, and LLM technologies, I am confident I would be a valuable addition to your team.

In my current role, I have:
- Developed and deployed production ML models serving millions of requests
- Built LLM-powered applications using LangChain and LangGraph
- Implemented robust APIs using FastAPI with comprehensive testing
- Collaborated with cross-functional teams to deliver AI solutions

My technical skills align closely with your requirements, including proficiency in Python, deep learning frameworks, and cloud platforms. I am particularly excited about the opportunity to work on innovative AI solutions at your company.

I would welcome the opportunity to discuss how my background and skills would benefit your team.

Best regards,
[Candidate Name]"""

    def _review_response(self) -> str:
        """Return mock review response with structured status."""
        return """REVIEW_STATUS: approved

FEEDBACK:

### Strengths
- Clear structure and professional tone
- Good alignment with job requirements
- Specific examples of relevant experience
- Strong opening paragraph

### Areas for Improvement
- Add more quantifiable achievements (metrics, percentages)
- Include specific technologies mentioned in job description
- Strengthen the closing call-to-action
- Consider adding a brief mention of company research

### Overall Assessment
The draft is well-written and demonstrates strong alignment with the role.
Score: 8/10

### Priority Suggestions
1. Add specific metrics (e.g., "improved model accuracy by 25%")
2. Mention specific tools from the job description
3. Research company projects and reference them"""

    def _improvement_response(self) -> str:
        """Return mock improvement response."""
        return """Dear Hiring Manager,

I am excited to apply for the AI Engineer position at your company, where I can contribute my expertise in building production-grade AI systems.

In my current role, I have delivered measurable impact:
- Increased model accuracy by 25% through advanced feature engineering
- Reduced inference latency by 40% using model optimization techniques
- Built LLM applications using LangChain and LangGraph serving 100K+ daily users
- Implemented FastAPI services with 99.9% uptime

Your focus on [specific company initiative] resonates with my passion for applying AI to solve real-world problems. I am particularly drawn to your team's work on [specific project].

My skills in Python, PyTorch, LangChain, and cloud platforms (AWS) align perfectly with your technical requirements. I thrive in collaborative environments and have a track record of mentoring junior engineers.

I would be thrilled to discuss how I can contribute to your AI initiatives. I am available for an interview at your convenience.

Best regards,
[Candidate Name]"""

    def _default_response(self) -> str:
        """Return default response for unrecognized prompts."""
        return """I understand your request. Based on the information provided, here is my response:

This is a mock LLM response for testing purposes. In production, this would be replaced with actual LLM-generated content tailored to your specific request.

Key points:
- The request has been processed
- Mock response generated successfully
- Replace with real LLM for production use"""


class HuggingFaceLLM:
    """Hugging Face LLM using Inference Providers chat completions.

    Modern instruct models on Hugging Face providers are frequently exposed as
    conversational/chat workloads rather than plain text-generation. This class
    keeps the local `invoke(prompt) -> str` contract while routing requests
    through Hugging Face chat completions first, with a text-generation
    fallback for older compatible deployments.

    Environment variables:
        HF_TOKEN: Hugging Face API token (required)
        HF_MODEL: Model ID (default: mistralai/Mistral-7B-Instruct-v0.3)
        TEMPERATURE: Sampling temperature (default: 0.2)
        MAX_NEW_TOKENS: Maximum tokens to generate (default: 900)
    """

    def __init__(self) -> None:
        """Initialize the Hugging Face LLM.

        Raises:
            ValueError: If HF_TOKEN is not set.
        """
        # Get token - required
        self.token = os.getenv("HF_TOKEN")
        if not self.token:
            raise ValueError(
                "HF_TOKEN environment variable is required for Hugging Face mode. "
                "Set it in your .env file or environment."
            )

        # Get model and parameters
        self.model_id = os.getenv("HF_MODEL", DEFAULT_HF_MODEL)
        self.temperature = float(os.getenv("TEMPERATURE", str(DEFAULT_TEMPERATURE)))
        self.max_new_tokens = int(os.getenv("MAX_NEW_TOKENS", str(DEFAULT_MAX_NEW_TOKENS)))

        # Lazy initialization of clients
        self._client = None
        self._endpoint = None

    def _get_client(self) -> Any:
        """Lazily initialize the Hugging Face inference client.

        Returns:
            InferenceClient instance.
        """
        if self._client is None:
            from huggingface_hub import InferenceClient

            self._client = InferenceClient(api_key=self.token)
        return self._client

    def _get_endpoint(self) -> Any:
        """Lazily initialize the HuggingFaceEndpoint fallback.

        Returns:
            HuggingFaceEndpoint instance.
        """
        if self._endpoint is None:
            from langchain_huggingface import HuggingFaceEndpoint

            self._endpoint = HuggingFaceEndpoint(
                repo_id=self.model_id,
                huggingfacehub_api_token=self.token,
                temperature=self.temperature,
                max_new_tokens=self.max_new_tokens,
            )
        return self._endpoint

    def _invoke_with_chat_completions(self, prompt: str) -> str:
        """Invoke the model using Hugging Face chat completions.

        Args:
            prompt: The input prompt text.

        Returns:
            Generated response text.
        """
        client = self._get_client()
        response = client.chat.completions.create(
            model=self.model_id,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=self.temperature,
            max_tokens=self.max_new_tokens,
        )
        return response.choices[0].message.content or ""

    def _invoke_with_endpoint(self, prompt: str) -> str:
        """Invoke the model using text-generation fallback."""
        endpoint = self._get_endpoint()
        response = endpoint.invoke(prompt)

        if isinstance(response, str):
            return response

        return str(response)

    def invoke(self, prompt: str) -> str:
        """Generate a response using the Hugging Face Inference API.

        Args:
            prompt: The input prompt text.

        Returns:
            Generated text from the model.
        """
        try:
            return self._invoke_with_chat_completions(prompt)
        except Exception:
            try:
                return self._invoke_with_endpoint(prompt)
            except Exception as endpoint_error:
                raise RuntimeError(
                    "Hugging Face request failed. The selected model may not be "
                    "available for either chat completions or text generation on "
                    "your configured provider. Try a conversational model deployed "
                    "in Hugging Face Inference Providers or set HF_MODEL to a known "
                    "compatible model."
                ) from endpoint_error


def get_llm(provider: str | None = None) -> LLMProtocol:
    """Get an LLM instance based on provider configuration.

    Reads LLM_PROVIDER from environment if not specified.
    Defaults to 'mock' if not set.

    Args:
        provider: Optional override for LLM provider.
                  If None, reads from LLM_PROVIDER env var.

    Returns:
        An LLM instance implementing LLMProtocol.

    Raises:
        ValueError: If provider is unknown or HF_TOKEN is missing for huggingface.
    """
    if provider is None:
        provider = os.getenv("LLM_PROVIDER", "mock")

    provider = provider.lower()

    if provider == "mock":
        return MockLLM()
    elif provider == "huggingface":
        return HuggingFaceLLM()
    else:
        raise ValueError(
            f"Unknown LLM provider: {provider}. "
            f"Supported providers: mock, huggingface"
        )
