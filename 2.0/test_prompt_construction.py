"""
Test suite for verifying prompt construction in ChatGPT and Gemini integrations.

This test validates that:
1. Description text is correctly placed in prompts
2. SVG content is correctly placed in text-based prompts
3. Image placeholders are correctly set for image-based prompts
4. Both integrations produce identical prompts (since they should be using the same templates)
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from chatgpt_integration.client import (
    _build_prompt_for_image as chatgpt_build_prompt_for_image,
    _build_prompt_for_text as chatgpt_build_prompt_for_text,
    _load_prompt_template as chatgpt_load_prompt_template,
    EVALUATION_TYPES,
)
from gemini_integration.client import (
    _build_prompt_for_image as gemini_build_prompt_for_image,
    _build_prompt_for_text as gemini_build_prompt_for_text,
    _load_prompt_template as gemini_load_prompt_template,
)


# Test assets paths
ASSETS_DIR = Path(__file__).parent / "geoserver" / "assets"
DESCRIPTION_PATH = ASSETS_DIR / "description.txt"
SVG_PATH = ASSETS_DIR / "gs_cloud_architecture_diagram.svg"


def load_test_assets():
    """Load description and SVG content for testing."""
    with open(DESCRIPTION_PATH, "r", encoding="utf-8") as f:
        description = f.read()
    
    with open(SVG_PATH, "r", encoding="utf-8") as f:
        svg_content = f.read()
    
    return description, svg_content


def test_description_placeholder_replaced_chatgpt():
    """Test that description placeholder is correctly replaced in ChatGPT prompts."""
    description, _ = load_test_assets()
    
    print("\n" + "="*60)
    print("TEST: Description placeholder replacement (ChatGPT)")
    print("="*60)
    
    for eval_type in EVALUATION_TYPES:
        prompt = chatgpt_build_prompt_for_image(eval_type, description)
        
        # Check placeholder is replaced
        has_placeholder = "[Insert textual description here]" in prompt
        has_description = description in prompt
        
        status = "✓ PASS" if (not has_placeholder and has_description) else "✗ FAIL"
        print(f"  {eval_type}: {status}")
        
        if has_placeholder:
            print(f"    ERROR: Placeholder '[Insert textual description here]' still present!")
        if not has_description:
            print(f"    ERROR: Description text not found in prompt!")
    
    return True


def test_description_placeholder_replaced_gemini():
    """Test that description placeholder is correctly replaced in Gemini prompts."""
    description, _ = load_test_assets()
    
    print("\n" + "="*60)
    print("TEST: Description placeholder replacement (Gemini)")
    print("="*60)
    
    for eval_type in EVALUATION_TYPES:
        prompt = gemini_build_prompt_for_image(eval_type, description)
        
        # Check placeholder is replaced
        has_placeholder = "[Insert textual description here]" in prompt
        has_description = description in prompt
        
        status = "✓ PASS" if (not has_placeholder and has_description) else "✗ FAIL"
        print(f"  {eval_type}: {status}")
        
        if has_placeholder:
            print(f"    ERROR: Placeholder '[Insert textual description here]' still present!")
        if not has_description:
            print(f"    ERROR: Description text not found in prompt!")
    
    return True


def test_svg_placeholder_replaced_chatgpt():
    """Test that SVG placeholder is correctly replaced in ChatGPT text-based prompts."""
    description, svg_content = load_test_assets()
    
    print("\n" + "="*60)
    print("TEST: SVG placeholder replacement (ChatGPT)")
    print("="*60)
    
    for eval_type in EVALUATION_TYPES:
        prompt = chatgpt_build_prompt_for_text(eval_type, svg_content, description)
        
        # Check placeholder is replaced
        has_placeholder = "[Insert diagram here]" in prompt
        has_svg = svg_content in prompt
        
        status = "✓ PASS" if (not has_placeholder and has_svg) else "✗ FAIL"
        print(f"  {eval_type}: {status}")
        
        if has_placeholder:
            print(f"    ERROR: Placeholder '[Insert diagram here]' still present!")
        if not has_svg:
            print(f"    ERROR: SVG content not found in prompt!")
    
    return True


def test_svg_placeholder_replaced_gemini():
    """Test that SVG placeholder is correctly replaced in Gemini text-based prompts."""
    description, svg_content = load_test_assets()
    
    print("\n" + "="*60)
    print("TEST: SVG placeholder replacement (Gemini)")
    print("="*60)
    
    for eval_type in EVALUATION_TYPES:
        prompt = gemini_build_prompt_for_text(eval_type, svg_content, description)
        
        # Check placeholder is replaced
        has_placeholder = "[Insert diagram here]" in prompt
        has_svg = svg_content in prompt
        
        status = "✓ PASS" if (not has_placeholder and has_svg) else "✗ FAIL"
        print(f"  {eval_type}: {status}")
        
        if has_placeholder:
            print(f"    ERROR: Placeholder '[Insert diagram here]' still present!")
        if not has_svg:
            print(f"    ERROR: SVG content not found in prompt!")
    
    return True


def test_image_placeholder_set_correctly():
    """Test that image-based prompts have '[See attached image]' placeholder."""
    description, _ = load_test_assets()
    
    print("\n" + "="*60)
    print("TEST: Image placeholder set correctly")
    print("="*60)
    
    for eval_type in EVALUATION_TYPES:
        chatgpt_prompt = chatgpt_build_prompt_for_image(eval_type, description)
        gemini_prompt = gemini_build_prompt_for_image(eval_type, description)
        
        chatgpt_has_image_placeholder = "[See attached image]" in chatgpt_prompt
        gemini_has_image_placeholder = "[See attached image]" in gemini_prompt
        
        status_chatgpt = "✓" if chatgpt_has_image_placeholder else "✗"
        status_gemini = "✓" if gemini_has_image_placeholder else "✗"
        
        print(f"  {eval_type}: ChatGPT {status_chatgpt}, Gemini {status_gemini}")
    
    return True


def test_prompts_identical_between_integrations():
    """Test that ChatGPT and Gemini produce identical prompts."""
    description, svg_content = load_test_assets()
    
    print("\n" + "="*60)
    print("TEST: Prompts identical between ChatGPT and Gemini")
    print("="*60)
    
    all_identical = True
    
    # Test image-based prompts
    print("\n  Image-based prompts:")
    for eval_type in EVALUATION_TYPES:
        chatgpt_prompt = chatgpt_build_prompt_for_image(eval_type, description)
        gemini_prompt = gemini_build_prompt_for_image(eval_type, description)
        
        identical = chatgpt_prompt == gemini_prompt
        status = "✓ IDENTICAL" if identical else "✗ DIFFERENT"
        print(f"    {eval_type}: {status}")
        
        if not identical:
            all_identical = False
            print(f"      ChatGPT length: {len(chatgpt_prompt)}")
            print(f"      Gemini length:  {len(gemini_prompt)}")
    
    # Test text-based prompts
    print("\n  Text-based (SVG) prompts:")
    for eval_type in EVALUATION_TYPES:
        chatgpt_prompt = chatgpt_build_prompt_for_text(eval_type, svg_content, description)
        gemini_prompt = gemini_build_prompt_for_text(eval_type, svg_content, description)
        
        identical = chatgpt_prompt == gemini_prompt
        status = "✓ IDENTICAL" if identical else "✗ DIFFERENT"
        print(f"    {eval_type}: {status}")
        
        if not identical:
            all_identical = False
            print(f"      ChatGPT length: {len(chatgpt_prompt)}")
            print(f"      Gemini length:  {len(gemini_prompt)}")
    
    return all_identical


def analyze_prompt_sizes():
    """Analyze and display prompt sizes to debug token count discrepancies."""
    description, svg_content = load_test_assets()
    
    print("\n" + "="*60)
    print("ANALYSIS: Prompt and content sizes")
    print("="*60)
    
    print(f"\n  Asset sizes:")
    print(f"    Description: {len(description):,} characters")
    print(f"    SVG content: {len(svg_content):,} characters")
    
    print(f"\n  Template sizes:")
    for eval_type in EVALUATION_TYPES:
        template = chatgpt_load_prompt_template(eval_type)
        print(f"    {eval_type}: {len(template):,} characters")
    
    print(f"\n  Final prompt sizes (text-based/SVG):")
    for eval_type in EVALUATION_TYPES:
        prompt = chatgpt_build_prompt_for_text(eval_type, svg_content, description)
        # Rough token estimate (1 token ≈ 4 characters for English text)
        approx_tokens = len(prompt) // 4
        print(f"    {eval_type}: {len(prompt):,} chars (~{approx_tokens:,} tokens)")
    
    print(f"\n  Final prompt sizes (image-based):")
    for eval_type in EVALUATION_TYPES:
        prompt = chatgpt_build_prompt_for_image(eval_type, description)
        approx_tokens = len(prompt) // 4
        print(f"    {eval_type}: {len(prompt):,} chars (~{approx_tokens:,} tokens)")


def inspect_prompt_content():
    """Print actual prompt content for manual inspection."""
    description, svg_content = load_test_assets()
    
    print("\n" + "="*60)
    print("INSPECTION: Sample prompt content (accuracy evaluation)")
    print("="*60)
    
    # Show a sample of the text-based prompt
    prompt = chatgpt_build_prompt_for_text("accuracy", svg_content, description)
    
    # Show first 500 and last 500 characters
    print(f"\n  First 500 characters of prompt:")
    print("-" * 40)
    print(prompt[:500])
    print("-" * 40)
    
    print(f"\n  Last 500 characters of prompt:")
    print("-" * 40)
    print(prompt[-500:])
    print("-" * 40)
    
    # Verify SVG is properly embedded
    svg_start_idx = prompt.find("<svg")
    svg_end_idx = prompt.find("</svg>") + len("</svg>")
    
    if svg_start_idx != -1 and svg_end_idx != -1:
        embedded_svg_length = svg_end_idx - svg_start_idx
        print(f"\n  SVG embedding check:")
        print(f"    SVG found at position: {svg_start_idx}")
        print(f"    Embedded SVG length: {embedded_svg_length:,} chars")
        print(f"    Original SVG length: {len(svg_content):,} chars")
        print(f"    Match: {'✓ YES' if embedded_svg_length == len(svg_content) else '✗ NO'}")
    else:
        print("\n  ✗ ERROR: SVG tags not found in prompt!")


def compare_with_evaluation_files():
    """Compare prompt sizes with actual token counts from evaluation files."""
    print("\n" + "="*60)
    print("COMPARISON: Expected vs Actual token counts")
    print("="*60)
    
    # Look for evaluation files to get actual token counts
    eval_dirs = {
        "chatgpt_svg": Path(__file__).parent / "geoserver" / "evaluations" / "chatgpt_svg",
        "gemini_svg": Path(__file__).parent / "geoserver" / "evaluations" / "gemini_svg",
    }
    
    for provider, eval_dir in eval_dirs.items():
        print(f"\n  {provider}:")
        if not eval_dir.exists():
            print(f"    Directory not found: {eval_dir}")
            continue
        
        # Look for JSON files with usage data
        import json
        json_files = list(eval_dir.glob("*.json"))
        
        if not json_files:
            print(f"    No JSON files found in {eval_dir}")
            continue
        
        for json_file in sorted(json_files)[:5]:  # Show first 5
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "usage" in data:
                        usage = data["usage"]
                        print(f"    {json_file.name}:")
                        print(f"      Prompt tokens: {usage.get('prompt_tokens', 'N/A'):,}")
                        print(f"      Completion tokens: {usage.get('completion_tokens', 'N/A'):,}")
                        print(f"      Total tokens: {usage.get('total_tokens', 'N/A'):,}")
            except Exception as e:
                print(f"    Error reading {json_file.name}: {e}")


def run_all_tests():
    """Run all tests and analysis."""
    print("\n" + "#"*60)
    print("# Prompt Construction Test Suite")
    print("#"*60)
    
    # Run tests
    test_description_placeholder_replaced_chatgpt()
    test_description_placeholder_replaced_gemini()
    test_svg_placeholder_replaced_chatgpt()
    test_svg_placeholder_replaced_gemini()
    test_image_placeholder_set_correctly()
    test_prompts_identical_between_integrations()
    
    # Run analysis
    analyze_prompt_sizes()
    inspect_prompt_content()
    compare_with_evaluation_files()
    
    print("\n" + "#"*60)
    print("# Test Suite Complete")
    print("#"*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
