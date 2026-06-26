"""
Gemini Integration Client for Architecture Evaluation

This module provides functions to evaluate software architecture diagrams
using Google's Gemini models with both image (PNG) and text (SVG) inputs.
"""

import os
import json
from pathlib import Path
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
from evaluation_output import (
    format_validated_payload,
    parse_and_validate_response,
)

# Load .env from this directory
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL = "gemini-3-pro-preview"
SYSTEM_PROMPT = "You are a helpful assistant specialized in software architecture and diagram analysis."

# Evaluation criteria mapping to prompt files
EVALUATION_TYPES = {
    "accuracy": "architecture-accuracy-evaluation.md",
    "clarity": "architecture-clarity-evaluation.md",
    "completeness": "architecture-completeness-evaluation.md",
    "consistency": "architecture-consistency-evaluation.md",
    "level_of_detail": "architecture-level-of-detail-evaluation.md",
}


def _get_prompts_dir() -> Path:
    """Get the prompts directory path."""
    return Path(__file__).parent.parent / "prompts"


def _load_prompt_template(evaluation_type: str) -> str:
    """Load prompt template from file."""
    if evaluation_type not in EVALUATION_TYPES:
        raise ValueError(f"Invalid evaluation type: {evaluation_type}. Valid options: {list(EVALUATION_TYPES.keys())}")
    
    prompt_file = _get_prompts_dir() / EVALUATION_TYPES[evaluation_type]
    with open(prompt_file, "r", encoding="utf-8") as f:
        return f.read()


def _build_prompt_for_image(evaluation_type: str, description: str) -> str:
    """Build prompt for image-based evaluation."""
    template = _load_prompt_template(evaluation_type)
    prompt = template.replace("[Insert textual description here]", description)
    prompt = prompt.replace("[Insert diagram here]", "[See attached image]")
    return prompt


def _build_prompt_for_text(evaluation_type: str, svg_content: str, description: str) -> str:
    """Build prompt for text-based (SVG) evaluation."""
    template = _load_prompt_template(evaluation_type)
    prompt = template.replace("[Insert textual description here]", description)
    prompt = prompt.replace("[Insert diagram here]", svg_content)
    return prompt


def _configure_genai(api_key: str = None):
    """Configure the Gemini API with the provided or environment API key."""
    key = api_key or GOOGLE_API_KEY
    if not key:
        raise ValueError("Google API key not found. Set GOOGLE_API_KEY in .env file.")
    genai.configure(api_key=key)


def _get_model():
    """Get configured Gemini model instance."""
    return genai.GenerativeModel(
        model_name=MODEL,
        system_instruction=SYSTEM_PROMPT
    )


def _upload_image(image_path: str):
    """Upload image file to Gemini."""
    return genai.upload_file(image_path)


def evaluate_with_image(
    evaluation_type: str,
    image_path: str,
    description: str,
    api_key: str = None
) -> dict:
    """
    Evaluate architecture diagram using image input (PNG).
    
    Args:
        evaluation_type: One of 'accuracy', 'clarity', 'completeness', 'consistency', 'level_of_detail'
        image_path: Path to the PNG diagram file
        description: Textual description of the architecture
        api_key: Optional Google API key (uses env var if not provided)
    
    Returns:
        dict with 'response', 'usage', 'model', and 'finish_reason'
    """
    _configure_genai(api_key)
    model = _get_model()
    
    prompt_text = _build_prompt_for_image(evaluation_type, description)
    
    # Upload the image
    image_file = _upload_image(image_path)
    
    # Generate response with image
    response = model.generate_content([prompt_text, image_file])
    raw_response = response.text or ""
    parsed_response = parse_and_validate_response(evaluation_type, raw_response)
    
    # Extract usage metadata
    usage_metadata = response.usage_metadata
    
    return {
        "response": raw_response,
        "parsed_response": parsed_response,
        "usage": {
            "prompt_tokens": usage_metadata.prompt_token_count,
            "completion_tokens": usage_metadata.candidates_token_count,
            "total_tokens": usage_metadata.total_token_count
        },
        "model": MODEL,
        "finish_reason": response.candidates[0].finish_reason.name if response.candidates else "UNKNOWN"
    }


def evaluate_with_text(
    evaluation_type: str,
    svg_path: str,
    description: str,
    api_key: str = None
) -> dict:
    """
    Evaluate architecture diagram using text input (SVG).
    
    Args:
        evaluation_type: One of 'accuracy', 'clarity', 'completeness', 'consistency', 'level_of_detail'
        svg_path: Path to the SVG diagram file
        description: Textual description of the architecture
        api_key: Optional Google API key (uses env var if not provided)
    
    Returns:
        dict with 'response', 'usage', 'model', and 'finish_reason'
    """
    _configure_genai(api_key)
    model = _get_model()
    
    with open(svg_path, "r", encoding="utf-8") as f:
        svg_content = f.read()
    
    prompt_text = _build_prompt_for_text(evaluation_type, svg_content, description)
    
    # Generate response with text only
    response = model.generate_content(prompt_text)
    raw_response = response.text or ""
    parsed_response = parse_and_validate_response(evaluation_type, raw_response)
    
    # Extract usage metadata
    usage_metadata = response.usage_metadata
    
    return {
        "response": raw_response,
        "parsed_response": parsed_response,
        "usage": {
            "prompt_tokens": usage_metadata.prompt_token_count,
            "completion_tokens": usage_metadata.candidates_token_count,
            "total_tokens": usage_metadata.total_token_count
        },
        "model": MODEL,
        "finish_reason": response.candidates[0].finish_reason.name if response.candidates else "UNKNOWN"
    }


def save_result(result: dict, evaluation_type: str, output_dir: str) -> str:
    """
    Save evaluation result to JSON and TXT files.
    
    Args:
        result: Evaluation result dictionary
        evaluation_type: Type of evaluation performed
        output_dir: Directory to save results
    
    Returns:
        Base path of saved files (without extension)
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"{evaluation_type}_{timestamp}"
    
    # Save JSON
    json_path = Path(output_dir) / f"{base_filename}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    # Save TXT
    txt_path = Path(output_dir) / f"{base_filename}.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"{'='*60}\n")
        f.write(f"{evaluation_type.upper()} EVALUATION\n")
        f.write(f"{'='*60}\n\n")
        
        if "error" in result:
            f.write(f"ERROR: {result['error']}\n")
        else:
            parsed_response = result.get("parsed_response")
            if parsed_response:
                f.write(format_validated_payload(parsed_response))
            else:
                f.write(result["response"])
            f.write(f"\n\n{'='*60}\n")
            f.write(f"MODEL: {result['model']}\n")
            f.write(f"TOKENS USED: {result['usage']['total_tokens']} ")
            f.write(f"(prompt: {result['usage']['prompt_tokens']}, ")
            f.write(f"completion: {result['usage']['completion_tokens']})\n")
            f.write(f"FINISH REASON: {result['finish_reason']}\n")
            f.write(f"TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    return str(Path(output_dir) / base_filename)


def get_evaluation_types() -> list:
    """Return list of available evaluation types."""
    return list(EVALUATION_TYPES.keys())

