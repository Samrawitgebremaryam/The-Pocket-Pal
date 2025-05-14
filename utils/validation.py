"""
Validation utilities for checking response quality and style adherence.
"""

from typing import Dict, List, Optional
import re


class ResponseValidator:
    def __init__(self, author: str, style_context: str):
        self.author = author
        self.style_context = style_context
        self.style_keywords = self._extract_style_keywords()

    def _extract_style_keywords(self) -> List[str]:
        """Extract key style elements from the style context."""
        # This is a simple implementation - could be enhanced with NLP
        words = self.style_context.lower().split()
        return [w for w in words if len(w) > 4]  # Basic keyword extraction

    def validate_response(self, response: str) -> Dict[str, any]:
        """Validate the response for quality and style adherence."""
        validation_results = {
            "length": self._check_length(response),
            "style_adherence": self._check_style_adherence(response),
            "coherence": self._check_coherence(response),
            "errors": [],
        }

        return validation_results

    def _check_length(self, response: str) -> Dict[str, any]:
        """Check if response length is appropriate."""
        word_count = len(response.split())
        return {"word_count": word_count, "is_valid": 50 <= word_count <= 500}

    def _check_style_adherence(self, response: str) -> Dict[str, any]:
        """Check if response adheres to author's style."""
        response_lower = response.lower()
        style_matches = sum(
            1 for keyword in self.style_keywords if keyword in response_lower
        )

        return {
            "style_matches": style_matches,
            "total_keywords": len(self.style_keywords),
            "adherence_score": (
                style_matches / len(self.style_keywords) if self.style_keywords else 0
            ),
        }

    def _check_coherence(self, response: str) -> Dict[str, any]:
        """Check response coherence using basic metrics."""
        sentences = re.split(r"[.!?]+", response)
        avg_sentence_length = (
            sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        )

        return {
            "sentence_count": len(sentences),
            "avg_sentence_length": avg_sentence_length,
            "is_coherent": 5 <= avg_sentence_length <= 30,
        }


def validate_generation(
    response: str, author: str, style_context: str
) -> Dict[str, any]:
    """Convenience function to validate a generated response."""
    validator = ResponseValidator(author, style_context)
    return validator.validate_response(response)
