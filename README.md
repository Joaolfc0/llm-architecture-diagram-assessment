# LLM Architecture Assessment

Python integration for evaluating software architecture diagrams using OpenAI GPT-4o.

Compare GPT-4o performance on diagrams as **images** vs **text** (XML/SVG).

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root:
```bash
cp .env.example .env
```

3. Add your OpenAI API key to `.env`:
```
OPENAI_API_KEY=your-api-key-here
```

## Usage

### Image-Based Evaluation

```python
from evaluate_architecture import evaluate_architecture, save_evaluation_result

result = evaluate_architecture(
    evaluation_type="accuracy",
    diagram_path="path/to/diagram.png",
    description="Your architecture description here..."
)

file_path = save_evaluation_result(result, "accuracy")
print(f"Saved to {file_path}.txt and {file_path}.json")
```

### Text-Based Evaluation (XML/SVG)

```python
from evaluate_architecture_text import evaluate_architecture, save_evaluation_result

result = evaluate_architecture(
    evaluation_type="accuracy",
    diagram_path="path/to/diagram.xml",  # or .svg
    description="Your architecture description here..."
)

file_path = save_evaluation_result(result, "accuracy")
```

### Evaluate All Criteria

```python
# Image-based
from evaluate_architecture import evaluate_all_criteria
results = evaluate_all_criteria("diagram.png", "description...")

# Text-based
from evaluate_architecture_text import evaluate_all_criteria
results = evaluate_all_criteria("diagram.xml", "description...")
```

### Evaluate Specific Criteria Only

```python
results = evaluate_all_criteria(
    diagram_path="path/to/diagram.png",
    description="Your architecture description here...",
    criteria=["accuracy", "clarity"]
)
```

### Compare Image vs Text Results

```python
from compare_evaluations import compare_evaluations

comparison = compare_evaluations(
    image_results_dir="evaluations",
    text_results_dir="evaluations_text"
)
```

### Output Files

**Image-based evaluations:** `evaluations/` directory
**Text-based evaluations:** `evaluations_text/` directory
**Comparisons:** `comparison_results/` directory

Each evaluation creates:
- `{evaluation_type}_{timestamp}.txt` - Human-readable format
- `{evaluation_type}_{timestamp}.json` - Full structured data
- `summary_{timestamp}.txt` - Overview (when using `evaluate_all_criteria`)

## Evaluation Types

- `accuracy`: Checks alignment between diagram and description
- `clarity`: Assesses understandability for stakeholders
- `completeness`: Verifies all components and interactions are present
- `consistency`: Validates uniform use of symbols, styles, and terms
- `level_of_detail`: Evaluates appropriateness for target audience

## Supported Formats

**Image-based (`evaluate_architecture.py`):**
- PNG, JPEG, GIF, WebP

**Text-based (`evaluate_architecture_text.py`):**
- XML, SVG, or any text-based diagram format

## Configuration

Modify these constants in `evaluate_architecture.py` / `evaluate_architecture_text.py`:

- `MODEL`: OpenAI model (default: "gpt-4o")
- `OUTPUT_DIR`: Directory for saving results
- `SYSTEM_PROMPT`: System message for the assistant

