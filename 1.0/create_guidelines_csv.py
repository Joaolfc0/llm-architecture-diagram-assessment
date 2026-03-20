import pandas as pd
import re
import os
import glob

# Define the guideline mapping for each criterion
GUIDELINE_MAPPING = {
    "clarity": {
        "G1": "Element Identification",
        "G2": "Reading Flow",
        "G3": "Symbol and Label Readability"
    },
    "completeness": {
        "G4": "Coverage of Main Components",
        "G5": "External Actors Coverage",
        "G6": "Main Interactions Coverage"
    },
    "consistency": {
        "G7": "Notation Definition and Uniformity",
        "G8": "Technology Symbols",
        "G9": "Naming and Representation Consistency"
    },
    "accuracy": {
        "G10": "Component Matching",
        "G11": "Interaction Matching",
        "G12": "Technology Representation"
    },
    "level_of_detail": {
        "G13": "Element Detail",
        "G14": "Interaction Detail",
        "G15": "Overall Appropriateness for Developers and Architects"
    }
}

def parse_guideline_checks(content, criterion):
    """
    Parse guideline checks from standardized evaluation content.
    Expected format:
    
    - Guideline Checks:
    - Guideline Name: YES/NO
    - Another Guideline: YES/NO
    
    OR
    
    Guideline Checks:
    - Guideline Name: YES/NO
    - Another Guideline: YES/NO
    """
    guidelines = {}
    
    # Find the "Guideline Checks" section (with or without leading dash)
    guideline_section_match = re.search(
        r'-?\s*Guideline Checks:\s*\n((?:-\s*.+?:\s*(?:YES|NO).*?\n?)+)',
        content,
        re.IGNORECASE | re.DOTALL
    )
    
    if not guideline_section_match:
        return guidelines
    
    guideline_section = guideline_section_match.group(1)
    
    # Pattern for format: - Name: YES/NO
    pattern = r'-\s*(.+?):\s*(YES|NO)'
    matches = re.findall(pattern, guideline_section, re.IGNORECASE)
    
    for match in matches:
        guideline_name = match[0].strip()
        value = match[1].strip().upper()
        
        # Clean up any remaining formatting
        guideline_name = re.sub(r'\*\*', '', guideline_name)
        guideline_name = guideline_name.strip()
        
        guidelines[guideline_name] = value
    
    return guidelines

def read_evaluation_file(filepath):
    """Read evaluation file and extract guideline checks."""
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return content

def normalize_guideline_name(name):
    """Normalize guideline names to match across different formats."""
    name = name.strip().lower()
    name = re.sub(r'\s+', ' ', name)
    return name

def match_guideline_name(found_name, expected_names):
    """Match found guideline name to expected names."""
    normalized_found = normalize_guideline_name(found_name)
    
    for expected_name in expected_names:
        normalized_expected = normalize_guideline_name(expected_name)
        if normalized_found == normalized_expected:
            return expected_name
    
    return None

def evaluate_reason_correctness(criterion, guideline_id, gt_label, llm_label, llm_content, model, modality):
    """
    This should be manually evaluated by reviewing each LLM justification.
    For now, we return -1 to indicate "pending manual review".
    
    TODO: Manually review each case and update reason_correct column:
    - 0 = incorrect/poor reasoning
    - 1 = correct/good reasoning
    - -1 = not yet reviewed (default)
    """
    return -1  # Pending manual review

def extract_justification(content):
    """Extract the justification section from evaluation content."""
    # Try to extract the justification part
    patterns = [
        r'Justification[:\s]+(.+?)(?=Guideline Checks:|$)',
        r'Justification[:\s]+(.+?)(?=\n- Guideline|$)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return ""

def create_guidelines_csv():
    """
    Create the guidelines CSV from evaluation files.
    
    IMPORTANT: Run normalize_evaluations.py first to ensure all files
    are in a consistent format!
    """
    
    print("=" * 70)
    print("CREATING GUIDELINES EVALUATION CSV")
    print("=" * 70)
    print("\nNote: If you haven't run normalize_evaluations.py yet,")
    print("      some evaluations may not be parsed correctly.")
    print("=" * 70)
    
    rows = []
    review_data = []  # For manual review helper file
    diagram_id = "geoserver_cloud"  # Single diagram
    
    # Define all evaluation sources
    evaluations = [
        # Ground truth
        {
            "source": "evaluation_gt",
            "model": "ground_truth",
            "modality": "gt",
            "is_gt": True
        },
        # GPT-4o with PNG image
        {
            "source": "evaluations",
            "model": "gpt5",
            "modality": "png",
            "is_gt": False
        },
        # GPT-4o with SVG text description
        {
            "source": "evaluations_text",
            "model": "gpt5",
            "modality": "svg",
            "is_gt": False
        },
        # Gemini with PNG image
        {
            "source": "evaluations_gemini",
            "model": "gemini3pro",
            "modality": "png",
            "is_gt": False
        },
        # Gemini with SVG text description
        {
            "source": "evaluations_gemini_text",
            "model": "gemini3pro",
            "modality": "svg",
            "is_gt": False
        }
    ]
    
    # Parse ground truth first
    print("\n📋 Parsing Ground Truth...")
    gt_data = {}
    for criterion in ["clarity", "completeness", "consistency", "accuracy", "level_of_detail"]:
        filepath = f"evaluation_gt/{criterion}.txt"
        content = read_evaluation_file(filepath)
        if content:
            gt_data[criterion] = parse_guideline_checks(content, criterion)
            print(f"  ✓ {criterion}: {len(gt_data[criterion])} guidelines found")
    
    # Now process each criterion
    for criterion in ["clarity", "completeness", "consistency", "accuracy", "level_of_detail"]:
        guideline_map = GUIDELINE_MAPPING[criterion]
        
        # Get ground truth values for this criterion
        gt_guidelines = gt_data.get(criterion, {})
        
        # Create a normalized mapping for ground truth
        gt_normalized = {}
        for gt_name, gt_value in gt_guidelines.items():
            for gid, expected_name in guideline_map.items():
                matched = match_guideline_name(gt_name, [expected_name])
                if matched:
                    gt_normalized[gid] = gt_value
                    break
        
        # Process each LLM evaluation
        for eval_config in evaluations:
            if eval_config["is_gt"]:
                continue  # Skip ground truth in LLM processing
            
            source = eval_config["source"]
            model = eval_config["model"]
            modality = eval_config["modality"]
            
            # Find the correct file (with or without timestamp)
            filepath = None
            
            # Handle the typo in filename for gemini level_of_detail
            if criterion == "level_of_detail" and source == "evaluations_gemini":
                typo_path = f"{source}/leve_of_detail.txt"
                if os.path.exists(typo_path):
                    filepath = typo_path
            
            # Try exact filename first
            if not filepath:
                exact_path = f"{source}/{criterion}.txt"
                if os.path.exists(exact_path):
                    filepath = exact_path
            
            # Try with timestamp pattern (for evaluations/ and evaluations_text/)
            if not filepath:
                pattern = f"{source}/{criterion}_*.txt"
                matching_files = glob.glob(pattern)
                if matching_files:
                    # Use the most recent file
                    filepath = max(matching_files, key=os.path.getmtime)
            
            if not filepath:
                print(f"  ⚠️  File not found: {source}/{criterion}.txt")
                continue
            
            content = read_evaluation_file(filepath)
            if not content:
                print(f"  ⚠️  Could not read: {filepath}")
                continue
            
            llm_guidelines = parse_guideline_checks(content, criterion)
            print(f"  → {model}/{modality}/{criterion}: {len(llm_guidelines)} guidelines found")
            
            # Match LLM guidelines to expected guidelines
            llm_normalized = {}
            for llm_name, llm_value in llm_guidelines.items():
                for gid, expected_name in guideline_map.items():
                    matched = match_guideline_name(llm_name, [expected_name])
                    if matched:
                        llm_normalized[gid] = llm_value
                        break
            
            # Extract justification for review
            justification = extract_justification(content)
            
            # Create rows for each guideline
            for gid, guideline_name in guideline_map.items():
                gt_label = gt_normalized.get(gid, "UNKNOWN")
                llm_label = llm_normalized.get(gid, "UNKNOWN")
                
                # Calculate label_correct
                if gt_label == "UNKNOWN" or llm_label == "UNKNOWN":
                    label_correct = 0
                else:
                    label_correct = 1 if gt_label == llm_label else 0
                
                # Evaluate reason correctness (this would ideally be manual)
                reason_correct = evaluate_reason_correctness(
                    criterion, gid, gt_label, llm_label, content, model, modality
                )
                
                # Calculate full agreement (only if reason_correct is evaluated)
                if reason_correct == -1:
                    full_agreement = -1  # Pending manual review
                else:
                    full_agreement = 1 if (label_correct == 1 and reason_correct == 1) else 0
                
                row = {
                    "diagram_id": diagram_id,
                    "criterion": criterion,
                    "guideline_id": gid,
                    "guideline_name": guideline_name,
                    "model": model,
                    "modality": modality,
                    "gt_label": gt_label,
                    "llm_label": llm_label,
                    "label_correct": label_correct,
                    "reason_correct": reason_correct,
                    "full_agreement": full_agreement
                }
                
                rows.append(row)
                
                # Add to review data
                review_data.append({
                    "criterion": criterion,
                    "guideline_id": gid,
                    "guideline_name": guideline_name,
                    "model": model,
                    "modality": modality,
                    "gt_label": gt_label,
                    "llm_label": llm_label,
                    "label_match": "MATCH" if gt_label == llm_label else "MISMATCH",
                    "justification": justification
                })
    
    # Create DataFrame
    df = pd.DataFrame(rows)
    
    # Sort by criterion, guideline_id, model, modality
    df = df.sort_values(["criterion", "guideline_id", "model", "modality"])
    
    # Save to CSV
    output_file = "guidelines_evaluation.csv"
    df.to_csv(output_file, index=False)
    print(f"✓ CSV created successfully: {output_file}")
    print(f"  Total rows: {len(df)}")
    
    # Create review helper file
    review_df = pd.DataFrame(review_data)
    review_file = "guidelines_review_helper.csv"
    review_df.to_csv(review_file, index=False)
    print(f"\n✓ Review helper file created: {review_file}")
    print(f"  Use this file to manually review LLM justifications")
    print(f"  and update the 'reason_correct' column in {output_file}")
    
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("1. Open 'guidelines_review_helper.csv' to see all LLM justifications")
    print("2. For each row, read the justification and decide if it's correct (0/1)")
    print("3. Update the 'reason_correct' column in 'guidelines_evaluation.csv'")
    print("4. After updating, recalculate 'full_agreement' where needed")
    print("="*60)
    
    print("\nSample rows from guidelines_evaluation.csv:")
    print(df.head(10).to_string())
    
    print("\n\nLabel accuracy by model and modality:")
    summary = df.groupby(["model", "modality"]).agg({
        "label_correct": "mean"
    }).round(3)
    print(summary)
    
    print(f"\n\nNote: reason_correct = -1 means 'pending manual review'")
    print(f"Total cases to review: {len(df[df['reason_correct'] == -1])}")
    
    return df

if __name__ == "__main__":
    df = create_guidelines_csv()

