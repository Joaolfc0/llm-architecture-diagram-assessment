import os
import json
from pathlib import Path
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o"
OUTPUT_DIR = "evaluations_text"
SYSTEM_PROMPT = "You are a helpful assistant specialized in software architecture and diagram making"

EVALUATION_TYPES = {
    "accuracy": "prompts/architecture-accuracy-evaluation.md",
    "clarity": "prompts/architecture-clarity-evaluation.md",
    "completeness": "prompts/architecture-completeness-evaluation.md",
    "consistency": "prompts/architecture-consistency-evaluation.md",
    "level_of_detail": "prompts/architecture-level-of-detail-evaluation.md",
}


def load_diagram_text(diagram_path: str) -> str:
    """Load XML/SVG diagram as text."""
    with open(diagram_path, "r", encoding="utf-8") as f:
        return f.read()


def load_prompt_template(evaluation_type: str) -> str:
    """Load prompt template from file."""
    prompt_file = EVALUATION_TYPES.get(evaluation_type)
    if not prompt_file:
        raise ValueError(f"Invalid evaluation type: {evaluation_type}")
    
    with open(prompt_file, "r", encoding="utf-8") as f:
        return f.read()


def build_prompt(evaluation_type: str, diagram_content: str, description: str) -> str:
    """Build the prompt by replacing placeholders with actual content."""
    template = load_prompt_template(evaluation_type)
    prompt = template.replace("[Insert diagram here]", diagram_content)
    prompt = prompt.replace("[Insert textual description here]", description)
    return prompt


def save_evaluation_result(result: dict, evaluation_type: str, output_dir: str = OUTPUT_DIR) -> str:
    """Save evaluation result to JSON and TXT files."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"{evaluation_type}_{timestamp}"
    
    json_path = Path(output_dir) / f"{base_filename}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
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


def evaluate_architecture(
    evaluation_type: str,
    diagram_path: str,
    description: str,
    api_key: str = OPENAI_API_KEY
) -> dict:
    """Send architecture diagram (as text) and description to OpenAI GPT-4o for evaluation."""
    client = OpenAI(api_key=api_key)
    
    diagram_content = load_diagram_text(diagram_path)
    prompt_text = build_prompt(evaluation_type, diagram_content, description)
    
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


def evaluate_all_criteria(
    diagram_path: str, 
    description: str, 
    api_key: str = OPENAI_API_KEY,
    save_results: bool = True,
    output_dir: str = OUTPUT_DIR,
    criteria: list = None
) -> dict:
    """Evaluate architecture against all or specific criteria."""
    if criteria is None:
        criteria = list(EVALUATION_TYPES.keys())
    else:
        invalid = [c for c in criteria if c not in EVALUATION_TYPES]
        if invalid:
            raise ValueError(f"Invalid criteria: {invalid}. Valid options: {list(EVALUATION_TYPES.keys())}")
    
    results = {}
    saved_files = []
    
    for eval_type in criteria:
        print(f"Evaluating {eval_type}...")
        try:
            result = evaluate_architecture(eval_type, diagram_path, description, api_key)
            results[eval_type] = result
            
            if save_results:
                file_path = save_evaluation_result(result, eval_type, output_dir)
                saved_files.append(file_path)
                print(f"✓ {eval_type} completed - saved to {file_path}.txt/.json ({result['usage']['total_tokens']} tokens)")
            else:
                print(f"✓ {eval_type} completed ({result['usage']['total_tokens']} tokens)")
        except Exception as e:
            print(f"✗ {eval_type} failed: {str(e)}")
            results[eval_type] = {"error": str(e)}
            if save_results:
                file_path = save_evaluation_result({"error": str(e)}, eval_type, output_dir)
                saved_files.append(file_path)
    
    if save_results:
        summary_path = Path(output_dir) / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write("="*60 + "\n")
            f.write("ARCHITECTURE EVALUATION SUMMARY (TEXT-BASED)\n")
            f.write("="*60 + "\n\n")
            
            total_tokens = 0
            successful = 0
            failed = 0
            
            for eval_type, result in results.items():
                if "error" in result:
                    f.write(f"✗ {eval_type}: FAILED - {result['error']}\n")
                    failed += 1
                else:
                    tokens = result['usage']['total_tokens']
                    total_tokens += tokens
                    successful += 1
                    f.write(f"✓ {eval_type}: SUCCESS ({tokens} tokens)\n")
            
            f.write(f"\n{'='*60}\n")
            f.write(f"Total evaluations: {len(results)}\n")
            f.write(f"Successful: {successful}\n")
            f.write(f"Failed: {failed}\n")
            f.write(f"Total tokens used: {total_tokens}\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print(f"\n✓ Summary saved to {summary_path}")
    
    return results


if __name__ == "__main__":
    diagram_path = "path/to/your/diagram.xml"
    description = """
    This architecture depicts a three-tier web application with:
    - Frontend: React-based SPA
    - Backend: RESTful API built with Node.js/Express
    - Database: PostgreSQL for persistent storage
    - Cache: Redis for session management
    """
    
    result = evaluate_architecture(
        evaluation_type="accuracy",
        diagram_path=diagram_path,
        description=description
    )
    
    file_path = save_evaluation_result(result, "accuracy")
    print(f"✓ Evaluation saved to {file_path}.txt/.json")
    print(f"Tokens used: {result['usage']['total_tokens']}")
    
    # all_results = evaluate_all_criteria(diagram_path, description)
    # specific_results = evaluate_all_criteria(diagram_path, description, criteria=["accuracy", "clarity"])

