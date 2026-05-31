"""Resume search functionality.

This module contains:
- Keyword-based resume section search
- Text tokenization and scoring

The search is deterministic and uses simple keyword overlap scoring.
"""

import re
import string


def tokenize(text: str) -> set[str]:
    """Tokenize text into a set of lowercase words with punctuation removed.
    
    Args:
        text: Input text to tokenize.
        
    Returns:
        Set of lowercase word tokens.
    """
    # Lowercase the text
    text = text.lower()
    
    # Remove punctuation using translation table
    translator = str.maketrans("", "", string.punctuation)
    text = text.translate(translator)
    
    # Split on whitespace and filter empty strings
    words = text.split()
    
    return set(words)


def split_resume_sections(resume_text: str) -> list[str]:
    """Split resume text into logical sections.
    
    Splits on double newlines (paragraphs) and markdown headers.
    
    Args:
        resume_text: Full resume text in markdown format.
        
    Returns:
        List of non-empty text sections.
    """
    # Split on markdown headers (## or ---) and double newlines
    # First, split on headers while keeping the header with its content
    sections = []
    
    # Split on double newlines first
    chunks = re.split(r'\n\n+', resume_text)
    
    for chunk in chunks:
        chunk = chunk.strip()
        if chunk:
            sections.append(chunk)
    
    return sections


def search_resume(query: str, resume_text: str, top_k: int = 5) -> list[dict]:
    """Search resume sections for relevance to a query.
    
    Uses keyword overlap scoring - sections with more query keywords
    get higher scores.
    
    Args:
        query: Search query string.
        resume_text: Full resume text to search.
        top_k: Maximum number of results to return.
        
    Returns:
        List of dicts with 'text' and 'score' keys, sorted by descending score.
        Returns empty list if query is empty.
    """
    # Handle empty query
    if not query or not query.strip():
        return []
    
    # Handle empty resume
    if not resume_text or not resume_text.strip():
        return []
    
    # Tokenize the query
    query_tokens = tokenize(query)
    
    if not query_tokens:
        return []
    
    # Split resume into sections
    sections = split_resume_sections(resume_text)
    
    # Score each section
    scored_sections = []
    for section in sections:
        section_tokens = tokenize(section)
        
        # Calculate overlap score (number of matching tokens / query tokens)
        overlap = query_tokens & section_tokens
        score = len(overlap) / len(query_tokens) if query_tokens else 0.0
        
        if score > 0:
            scored_sections.append({
                "text": section,
                "score": round(score, 4)
            })
    
    # Sort by score descending
    scored_sections.sort(key=lambda x: x["score"], reverse=True)
    
    # Return top_k results
    return scored_sections[:top_k]
