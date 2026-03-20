"""
Gemini Integration Package for Architecture Evaluation

Provides functions to evaluate software architecture diagrams using Google's Gemini models.
"""

from .client import (
    evaluate_with_image,
    evaluate_with_text,
    save_result,
    get_evaluation_types,
    EVALUATION_TYPES,
)

__all__ = [
    "evaluate_with_image",
    "evaluate_with_text",
    "save_result",
    "get_evaluation_types",
    "EVALUATION_TYPES",
]

