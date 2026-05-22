"""
Utilities for enforcing and validating structured LLM evaluation output.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List


GUIDELINES_BY_CRITERION = {
    "accuracy": [
        "component_matching",
        "interaction_matching",
    ],
    "clarity": [
        "element_identification",
        "reading_flow",
        "symbol_label_readability",
        "specific_symbology",
    ],
    "completeness": [
        "coverage_main_components",
        "external_actors_coverage",
        "main_interactions_coverage",
    ],
    "consistency": [
        "notation_uniformity",
        "technology_symbols",
        "naming_consistency",
    ],
    "level_of_detail": [
        "element_detail",
        "interaction_detail",
        "overall_appropriateness",
    ],
}

VALID_SCORES = {
    "4 (Excellent)",
    "3 (Good)",
    "2 (Fair)",
    "1 (Poor)",
}


def parse_and_validate_response(evaluation_type: str, raw_response: str) -> Dict[str, Any]:
    """Parse JSON output and validate its schema for the given criterion."""
    payload = _extract_json_payload(raw_response)
    return _validate_payload(evaluation_type, payload)


def format_validated_payload(payload: Dict[str, Any]) -> str:
    """Render a validated payload in a human-readable plain-text format."""
    lines = [
        f"Criterion: {payload['criterion']}",
        "",
        "Guidelines:",
    ]
    for guideline in payload["guidelines"]:
        lines.extend(
            [
                f"- {guideline['id']}: {guideline['score']}",
                f"  Justification: {guideline['justification']}",
            ]
        )
    return "\n".join(lines)


def _extract_json_payload(raw_response: str) -> Dict[str, Any]:
    text = raw_response.strip()

    if text.startswith("```"):
        text = _strip_markdown_fence(text)

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Model response is not valid JSON: {exc}") from exc

    if not isinstance(parsed, dict):
        raise ValueError("Model JSON must be an object.")

    return parsed


def _strip_markdown_fence(text: str) -> str:
    lines = text.splitlines()
    if not lines:
        return text

    if lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def _validate_payload(evaluation_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if payload.get("criterion") != evaluation_type:
        raise ValueError(
            f"criterion must be '{evaluation_type}', got '{payload.get('criterion')}'."
        )

    guidelines = payload.get("guidelines")
    if not isinstance(guidelines, list):
        raise ValueError("guidelines must be a list.")

    expected_ids = GUIDELINES_BY_CRITERION[evaluation_type]
    expected_set = set(expected_ids)

    normalized: List[Dict[str, str]] = []
    seen_ids = set()

    for entry in guidelines:
        if not isinstance(entry, dict):
            raise ValueError("Each guideline entry must be an object.")

        guideline_id = entry.get("id")
        score = entry.get("score")
        justification = entry.get("justification")

        if guideline_id not in expected_set:
            raise ValueError(f"Invalid guideline id '{guideline_id}' for {evaluation_type}.")
        if guideline_id in seen_ids:
            raise ValueError(f"Duplicate guideline id '{guideline_id}'.")
        if score not in VALID_SCORES:
            raise ValueError(f"Invalid score '{score}' for guideline '{guideline_id}'.")
        if not isinstance(justification, str) or not justification.strip():
            raise ValueError(f"Guideline '{guideline_id}' has empty justification.")

        seen_ids.add(guideline_id)
        normalized.append(
            {
                "id": guideline_id,
                "score": score,
                "justification": justification.strip(),
            }
        )

    missing = [guideline_id for guideline_id in expected_ids if guideline_id not in seen_ids]
    if missing:
        raise ValueError(f"Missing guideline ids: {missing}")

    by_id = {entry["id"]: entry for entry in normalized}
    ordered = [by_id[guideline_id] for guideline_id in expected_ids]

    return {
        "criterion": evaluation_type,
        "guidelines": ordered,
    }
