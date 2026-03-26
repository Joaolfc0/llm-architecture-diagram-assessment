## Research materials (for anonymous review)

This repository contains multiple artifacts, but **this README documents only** the contents under `research-files/`, which contains the study materials used for the LLM-based assessment of software architecture diagrams.

The **anonymous audit site** (including the questions/prompts used in the auditing flow) is available at:

- `https://anonymous.4open.science/w/llm-assessment-audit-1238`

## Repository organization (documented scope: `research-files/`)

### `research-files/`

Top-level contents:

- **`requirements.txt`**: Minimal Python dependencies for the evaluation clients (OpenAI + Gemini) and env var loading.
- **`test_prompt_construction.py`**: Test suite that verifies prompt template substitution and ensures the ChatGPT/Gemini integrations construct identical prompts (image- and text-based).
- **`venv/`**: Local Python virtual environment (if present on your machine). Not required to understand the study artifacts.

Subfolders:

### `research-files/prompts/`

Prompt templates used for each evaluation criterion. Each template contains placeholders:

- `[Insert diagram here]` (replaced with SVG/XML text content or an image placeholder)
- `[Insert textual description here]` (replaced with the case-study description text)

Files:

- **`architecture-accuracy-evaluation.md`**: Accuracy rubric prompt template.
- **`architecture-clarity-evaluation.md`**: Clarity rubric prompt template.
- **`architecture-completeness-evaluation.md`**: Completeness rubric prompt template.
- **`architecture-consistency-evaluation.md`**: Consistency rubric prompt template.
- **`architecture-level-of-detail-evaluation.md`**: Level-of-detail rubric prompt template.

### `research-files/chatgpt_integration/`

Python client for running the evaluation prompts with OpenAI models.

- **`client.py`**: Implements prompt loading, prompt construction for image/text inputs, API calls, and result saving.
- **`env.example`**: Example environment file showing required variables (copy to `.env` locally if you run the scripts).

### `research-files/gemini_integration/`

Python client for running the evaluation prompts with Google Gemini models.

- **`client.py`**: Implements prompt loading, prompt construction for image/text inputs, API calls, and result saving.
- **`env.example`**: Example environment file showing required variables (copy to `.env` locally if you run the scripts).

### `research-files/geoserver/`

Case study based on **GeoServer Cloud**.

- **`assets/`**: Inputs provided to the LLMs:
  - `description.txt`: Textual architecture description.
  - `gs_cloud_architecture_diagram.png`: Diagram image input.
  - `gs_cloud_architecture_diagram.svg`: Diagram text (SVG) input.
- **`scripts/`**:
  - `run_evaluation.py`: Runs all criteria across models and input types, and writes results under `evaluations/`.
- **`evaluations/`**: Saved outputs (if present). Organized by provider and input type:
  - `chatgpt_png/`, `chatgpt_svg/`, `gemini_png/`, `gemini_svg/`
  - Typical files include one `.txt` and one `.json` per criterion (e.g., `accuracy_YYYYMMDD_HHMMSS.*`) plus a `summary_*.txt`.
- **`commands.txt`**: Example commands for running `scripts/run_evaluation.py`.

### `research-files/appwrite/`

Case study based on **Appwrite**(future).

- **`assets/`**:
  - `description.txt`: Textual architecture description.
  - `overview.drawio.png`: Diagram image input.
  - `overview.drawio.svg`: Diagram text (SVG) input.
- **`scripts/`**:
  - `run_evaluation.py`: Runs all criteria across models and input types, and writes results under `evaluations/`.
- **`evaluations/`**: Saved outputs (if present). Organized by provider and input type:
  - `chatgpt_png/`, `chatgpt_svg/`, `gemini_png/`, `gemini_svg/`
  - Typical files include one `.txt` and one `.json` per criterion plus a `summary_*.txt`.
- **`commands.txt`**: Example commands for running `scripts/run_evaluation.py`.

### `research-files/spryker/`

Case study based on a containerized **Spryker demoshop stack** (future).

- **`assets/`**:
  - `description.txt`: Textual description of the stack and port allocation scheme.
  - `container-stack.png`: Diagram image input.
  - `container-stack.xml`: Diagram text input (XML export).
- **`scripts/`**:
  - `run_evaluation.py`: Runs all criteria across models and input types, and writes results under `evaluations/`.
- **`evaluations/`**: Saved outputs (if present). Intended to follow the same structure as other case studies (e.g., `chatgpt_png/`, `chatgpt_xml/`, `gemini_png/`, `gemini_xml/`), depending on what has been executed locally.
- **`commands.txt`**: Example commands for running `scripts/run_evaluation.py`.

### `research-files/analise-csv/`

Post-processing and reporting utilities for analyzing exported evaluation results.

- **`analysis_mixed.py`**: Analysis variant for mixed conditions/inputs.
- **`analysis_mixed_results.txt`**: Generated analysis outputs.
- **`Estrutura de Planilha para Análise Granular - final - Estrutura de Planilha para Anál.csv`**: Spreadsheet template used for granular analysis.
- **`generate_figures.py`**: Generates the PDF figures.
- **`figure1_criteria.pdf`**, **`figure2_conditions.pdf`**, **`figure3_errors.pdf`**: Generated figures used for reporting.
- **`extract_other.py`**: Utility script to isolate and inspect "other error" annotations in the granular analysis data.


