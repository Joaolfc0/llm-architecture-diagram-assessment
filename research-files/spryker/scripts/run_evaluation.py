"""
Spryker Architecture Evaluation Script

This script runs architecture diagram evaluations for the Spryker project
using both ChatGPT and Claude models with PNG and XML inputs.
"""

import sys
import argparse
import time
from pathlib import Path
from datetime import datetime

# Add project root (2.0/) to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from chatgpt_integration import client as chatgpt
from claude_integration import client as claude

# Asset paths relative to this script
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
DIAGRAM_PNG = ASSETS_DIR / "container-stack.png"
DIAGRAM_XML = ASSETS_DIR / "container-stack.drawio.xml"
DESCRIPTION_FILE = ASSETS_DIR / "description.txt"

# Output directory
EVALUATIONS_DIR = Path(__file__).resolve().parent.parent / "evaluations"


def load_description() -> str:
    """Load the architecture description from file."""
    with open(DESCRIPTION_FILE, "r", encoding="utf-8") as f:
        return f.read()


def run_evaluation(
    model: str,
    input_type: str,
    criteria: list,
    delay: int,
    description: str
) -> dict:
    """
    Run evaluation for a specific model and input type.
    
    Args:
        model: 'chatgpt' or 'claude'
        input_type: 'png' or 'xml'
        criteria: List of evaluation criteria to run
        delay: Seconds to wait between API calls
        description: Architecture description text
    
    Returns:
        Dictionary with results for each criterion
    """
    # Select the appropriate client and function
    if model == "chatgpt":
        client = chatgpt
    else:
        client = claude
    
    # Select the appropriate diagram path and function
    if input_type == "png":
        diagram_path = str(DIAGRAM_PNG)
        evaluate_fn = client.evaluate_with_image
    else:
        diagram_path = str(DIAGRAM_XML)
        evaluate_fn = client.evaluate_with_text
    
    # Create output directory
    output_dir = EVALUATIONS_DIR / f"{model}_{input_type}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    for i, criterion in enumerate(criteria):
        print(f"  [{i+1}/{len(criteria)}] Evaluating {criterion}...")
        
        try:
            result = evaluate_fn(criterion, diagram_path, description)
            results[criterion] = result
            
            # Save result
            file_path = client.save_result(result, criterion, str(output_dir))
            print(f"      ✓ Completed - saved to {Path(file_path).name}.txt/.json")
            print(f"        Tokens: {result['usage']['total_tokens']}")
            
        except Exception as e:
            print(f"      ✗ Failed: {str(e)}")
            results[criterion] = {"error": str(e)}
            # Save error result
            client.save_result({"error": str(e)}, criterion, str(output_dir))
        
        # Add delay between API calls (except for the last one)
        if i < len(criteria) - 1 and delay > 0:
            print(f"      Waiting {delay}s before next call...")
            time.sleep(delay)
    
    # Save summary
    save_summary(results, model, input_type, output_dir)
    
    return results


def save_summary(results: dict, model: str, input_type: str, output_dir: Path):
    """Save evaluation summary to file."""
    summary_path = output_dir / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write(f"ARCHITECTURE EVALUATION SUMMARY\n")
        f.write(f"Model: {model.upper()} | Input: {input_type.upper()}\n")
        f.write("=" * 60 + "\n\n")
        
        total_tokens = 0
        successful = 0
        failed = 0
        
        for criterion, result in results.items():
            if "error" in result:
                f.write(f"✗ {criterion}: FAILED - {result['error']}\n")
                failed += 1
            else:
                tokens = result['usage']['total_tokens']
                total_tokens += tokens
                successful += 1
                f.write(f"✓ {criterion}: SUCCESS ({tokens} tokens)\n")
        
        f.write(f"\n{'='*60}\n")
        f.write(f"Total evaluations: {len(results)}\n")
        f.write(f"Successful: {successful}\n")
        f.write(f"Failed: {failed}\n")
        f.write(f"Total tokens used: {total_tokens}\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"  Summary saved to {summary_path.name}")


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate Spryker Architecture Diagram",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all evaluations (all models, all input types)
  python run_evaluation.py
  
  # Run only ChatGPT evaluations
  python run_evaluation.py --model chatgpt
  
  # Run only PNG-based evaluations
  python run_evaluation.py --input png
  
  # Run Claude with XML input only
  python run_evaluation.py --model claude --input xml
  
  # Run with custom delay between API calls
  python run_evaluation.py --delay 60
  
  # Run specific criteria only
  python run_evaluation.py --criteria accuracy clarity
        """
    )
    
    parser.add_argument(
        "--model",
        choices=["chatgpt", "claude", "both"],
        default="both",
        help="Which model to use (default: both)"
    )
    
    parser.add_argument(
        "--input",
        choices=["png", "xml", "both"],
        default="both",
        help="Input type to use (default: both)"
    )
    
    parser.add_argument(
        "--delay",
        type=int,
        default=5,
        help="Delay in seconds between API calls (default: 5)"
    )
    
    parser.add_argument(
        "--criteria",
        nargs="+",
        choices=["accuracy", "clarity", "completeness", "consistency", "level_of_detail"],
        default=["accuracy", "clarity", "completeness", "consistency", "level_of_detail"],
        help="Evaluation criteria to run (default: all)"
    )
    
    args = parser.parse_args()
    
    # Determine which models and input types to run
    models = ["chatgpt", "claude"] if args.model == "both" else [args.model]
    input_types = ["png", "xml"] if args.input == "both" else [args.input]
    
    # Validate assets exist
    if not DIAGRAM_PNG.exists():
        print(f"Error: PNG diagram not found at {DIAGRAM_PNG}")
        sys.exit(1)
    if not DIAGRAM_XML.exists():
        print(f"Error: XML diagram not found at {DIAGRAM_XML}")
        sys.exit(1)
    if not DESCRIPTION_FILE.exists():
        print(f"Error: Description file not found at {DESCRIPTION_FILE}")
        sys.exit(1)
    
    # Load description
    description = load_description()
    
    print("=" * 80)
    print("SPRYKER ARCHITECTURE EVALUATION")
    print("=" * 80)
    print(f"\nModels: {', '.join(models)}")
    print(f"Input types: {', '.join(input_types)}")
    print(f"Criteria: {', '.join(args.criteria)}")
    print(f"Delay between calls: {args.delay}s")
    print(f"Output directory: {EVALUATIONS_DIR}")
    print()
    
    all_results = {}
    total_runs = len(models) * len(input_types)
    current_run = 0
    
    for model in models:
        for input_type in input_types:
            current_run += 1
            run_key = f"{model}_{input_type}"
            
            print("-" * 80)
            print(f"[{current_run}/{total_runs}] Running: {model.upper()} with {input_type.upper()} input")
            print("-" * 80)
            
            try:
                results = run_evaluation(
                    model=model,
                    input_type=input_type,
                    criteria=args.criteria,
                    delay=args.delay,
                    description=description
                )
                all_results[run_key] = results
                print(f"\n✓ {run_key} completed!\n")
                
            except Exception as e:
                print(f"\n✗ {run_key} failed: {str(e)}\n")
                all_results[run_key] = {"error": str(e)}
            
            # Add delay between different model/input combinations
            if current_run < total_runs and args.delay > 0:
                print(f"Waiting {args.delay}s before next run...")
                time.sleep(args.delay)
    
    # Print final summary
    print("=" * 80)
    print("EVALUATION COMPLETE!")
    print("=" * 80)
    
    for run_key, results in all_results.items():
        if "error" in results:
            print(f"✗ {run_key}: FAILED")
        else:
            successful = sum(1 for r in results.values() if "error" not in r)
            total = len(results)
            print(f"✓ {run_key}: {successful}/{total} criteria completed")
    
    print(f"\nResults saved to: {EVALUATIONS_DIR}")


if __name__ == "__main__":
    main()
