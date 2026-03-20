import json
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = "comparison_results"


def load_evaluation_results(json_path: str) -> dict:
    """Load evaluation results from JSON file."""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def compare_evaluations(image_results_dir: str, text_results_dir: str, output_dir: str = OUTPUT_DIR) -> dict:
    """Compare evaluation results between image-based and text-based approaches."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    image_files = sorted(Path(image_results_dir).glob("*.json"))
    text_files = sorted(Path(text_results_dir).glob("*.json"))
    
    comparison = {
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "comparisons": []
    }
    
    image_results = {}
    for file in image_files:
        if not file.name.startswith("summary"):
            eval_type = file.stem.rsplit("_", 2)[0]
            image_results[eval_type] = load_evaluation_results(file)
    
    text_results = {}
    for file in text_files:
        if not file.name.startswith("summary"):
            eval_type = file.stem.rsplit("_", 2)[0]
            text_results[eval_type] = load_evaluation_results(file)
    
    for eval_type in image_results.keys():
        if eval_type in text_results:
            img_result = image_results[eval_type]
            txt_result = text_results[eval_type]
            
            comparison["comparisons"].append({
                "evaluation_type": eval_type,
                "image_tokens": img_result["usage"]["total_tokens"],
                "text_tokens": txt_result["usage"]["total_tokens"],
                "token_difference": txt_result["usage"]["total_tokens"] - img_result["usage"]["total_tokens"],
                "image_response_length": len(img_result["response"]),
                "text_response_length": len(txt_result["response"])
            })
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = Path(output_dir) / f"comparison_{timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)
    
    txt_path = Path(output_dir) / f"comparison_{timestamp}.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("="*80 + "\n")
        f.write("IMAGE vs TEXT EVALUATION COMPARISON\n")
        f.write("="*80 + "\n\n")
        
        total_img_tokens = 0
        total_txt_tokens = 0
        
        for comp in comparison["comparisons"]:
            f.write(f"\n{comp['evaluation_type'].upper()}\n")
            f.write("-" * 40 + "\n")
            f.write(f"Image tokens:    {comp['image_tokens']:,}\n")
            f.write(f"Text tokens:     {comp['text_tokens']:,}\n")
            f.write(f"Difference:      {comp['token_difference']:+,}\n")
            f.write(f"Image response:  {comp['image_response_length']:,} chars\n")
            f.write(f"Text response:   {comp['text_response_length']:,} chars\n")
            
            total_img_tokens += comp['image_tokens']
            total_txt_tokens += comp['text_tokens']
        
        f.write(f"\n{'='*80}\n")
        f.write(f"TOTALS\n")
        f.write(f"{'='*80}\n")
        f.write(f"Total image tokens:  {total_img_tokens:,}\n")
        f.write(f"Total text tokens:   {total_txt_tokens:,}\n")
        f.write(f"Total difference:    {total_txt_tokens - total_img_tokens:+,}\n")
        f.write(f"Evaluations compared: {len(comparison['comparisons'])}\n")
        f.write(f"\nTimestamp: {comparison['timestamp']}\n")
    
    print(f"✓ Comparison saved to {txt_path}")
    return comparison


if __name__ == "__main__":
    comparison = compare_evaluations(
        image_results_dir="evaluations",
        text_results_dir="evaluations_text"
    )
    
    print(f"\nCompared {len(comparison['comparisons'])} evaluations")

