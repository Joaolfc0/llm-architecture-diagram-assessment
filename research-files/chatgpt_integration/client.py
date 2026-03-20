"""
ChatGPT Integration Client for Architecture Evaluation

This module provides functions to evaluate software architecture diagrams
using OpenAI's GPT models with both image (PNG) and text (SVG) inputs.
"""

import os
import base64
import json
from pathlib import Path
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load .env from this directory
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-5"
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


def _encode_image_to_base64(image_path: str) -> str:
    """Encode image file to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def _get_image_mime_type(image_path: str) -> str:
    """Determine MIME type from file extension."""
    extension = Path(image_path).suffix.lower()
    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    return mime_types.get(extension, "image/png")


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


def _get_client(api_key: str = None) -> OpenAI:
    """Get OpenAI client instance."""
    key = api_key or OPENAI_API_KEY
    if not key:
        raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY in .env file.")
    return OpenAI(api_key=key)


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
        api_key: Optional OpenAI API key (uses env var if not provided)
    
    Returns:
        dict with 'response', 'usage', 'model', and 'finish_reason'
    """
    client = _get_client(api_key)
    
    image_base64 = _encode_image_to_base64(image_path)
    mime_type = _get_image_mime_type(image_path)
    prompt_text = _build_prompt_for_image(evaluation_type, description)
    
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt_text
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{image_base64}"
                    }
                }
            ]
        }
    ]
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages
    )
    
    return {
        "response": response.choices[0].message.content,
        "usage": {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        },
        "model": response.model,
        "finish_reason": response.choices[0].finish_reason
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
        api_key: Optional OpenAI API key (uses env var if not provided)
    
    Returns:
        dict with 'response', 'usage', 'model', and 'finish_reason'
    """
    client = _get_client(api_key)
    
    with open(svg_path, "r", encoding="utf-8") as f:
        svg_content = f.read()
    
    prompt_text = _build_prompt_for_text(evaluation_type, svg_content, description)
    
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": prompt_text
        }
    ]
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages
    )
    
    return {
        "response": response.choices[0].message.content,
        "usage": {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        },
        "model": response.model,
        "finish_reason": response.choices[0].finish_reason
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

