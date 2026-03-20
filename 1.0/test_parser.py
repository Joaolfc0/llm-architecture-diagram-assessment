import re

def parse_guideline_checks(content, criterion):
    """Test the guideline parser."""
    guidelines = {}
    
    # Find the "Guideline Checks" section (with or without leading dash)
    guideline_section_match = re.search(
        r'-?\s*Guideline Checks:\s*\n((?:-\s*.+?:\s*(?:YES|NO).*?\n?)+)',
        content,
        re.IGNORECASE | re.DOTALL
    )
    
    if not guideline_section_match:
        print("❌ No match found!")
        return guidelines
    
    print("✓ Match found!")
    guideline_section = guideline_section_match.group(1)
    print(f"\nExtracted section:\n{guideline_section}")
    
    # Pattern for format: - Name: YES/NO
    pattern = r'-\s*(.+?):\s*(YES|NO)'
    matches = re.findall(pattern, guideline_section, re.IGNORECASE)
    
    print(f"\nFound {len(matches)} guideline(s):")
    
    for match in matches:
        guideline_name = match[0].strip()
        value = match[1].strip().upper()
        
        # Clean up any remaining formatting
        guideline_name = re.sub(r'\*\*', '', guideline_name)
        guideline_name = guideline_name.strip()
        
        print(f"  - {guideline_name}: {value}")
        guidelines[guideline_name] = value
    
    return guidelines

# Test with evaluation_gt/clarity.txt
print("=" * 70)
print("TEST 1: evaluation_gt/clarity.txt")
print("=" * 70)

with open("evaluation_gt/clarity.txt", "r", encoding="utf-8") as f:
    content = f.read()

result = parse_guideline_checks(content, "clarity")
print(f"\nResult: {result}")

# Test with evaluations_gemini/clarity.txt
print("\n" + "=" * 70)
print("TEST 2: evaluations_gemini/clarity.txt")
print("=" * 70)

with open("evaluations_gemini/clarity.txt", "r", encoding="utf-8") as f:
    content = f.read()

result = parse_guideline_checks(content, "clarity")
print(f"\nResult: {result}")

# Test with evaluations/clarity_*.txt
print("\n" + "=" * 70)
print("TEST 3: evaluations/clarity_20251124_162642.txt")
print("=" * 70)

with open("evaluations/clarity_20251124_162642.txt", "r", encoding="utf-8") as f:
    content = f.read()

result = parse_guideline_checks(content, "clarity")
print(f"\nResult: {result}")

