## Replication package — LLM assessment of architecture diagrams

This repository supports replication and review of a study on **LLM-based evaluation of software architecture diagrams** under different input representations (image vs text).

**Paper:** *How Reliable Are LLM Evaluations of Microservice Architecture Diagrams?*

**Authors:** João Luiz Cerqueira, Mateus Dutra, Eduardo Figueiredo, and Gustavo Andrade Vale (Federal University of Minas Gerais — UFMG, Belo Horizonte, Brazil)

**Venue:** SBCARS 2026 — 20th Brazilian Symposium on Software Components, Architectures, and Reuse (September 8–11, 2026, São Paulo, SP, Brazil)

**Anonymous audit site** (survey flow, prompts shown to experts):

- https://anonymous.4open.science/w/llm-assessment-audit-1238

---

## Quick guide for reviewers

If you are checking whether the study is reproducible, start here:

| What you need | Where to look |
|---|---|
| **Expert survey responses (raw)** | [`research-files/analysis-csv/`](research-files/analysis-csv/) — three CSV files below |
| **Diagram inputs** (image + text + description) | One folder per case study under [`research-files/`](research-files/) — see [Diagrams](#diagrams-case-studies) |
| **LLM evaluation outputs** | [`research-files/analysis-csv/llm-evaluations/`](research-files/analysis-csv/llm-evaluations/) |
| **Human ground truth** (aggregated) | [`research-files/analysis-csv/ground-truth/`](research-files/analysis-csv/ground-truth/) |
| **Statistical analysis (RQ1–RQ3)** | [`research-files/analysis-csv/rq-analysis/`](research-files/analysis-csv/rq-analysis/) |
| **Prompt templates** | [`research-files/prompts/`](research-files/prompts/) |

**Privacy:** participant emails were replaced with anonymous IDs (`P001`–`P016`) in all published CSVs. The mapping file is not included in this package.

---

## Survey data (`research-files/analysis-csv/`)

All expert-facing data from the study are exported as CSV. Participants are identified by **`Expert_ID`** (e.g. `P005`).

### Study phases

| Phase | File | Rows (approx.) | What each row is |
|---|---|---:|---|
| **Demographics** | [`llm-assesment-v2 - participant_demographics.csv`](research-files/analysis-csv/llm-assesment-v2%20-%20participant_demographics.csv) | 16 | One expert: academic profile, development experience, self-reported expertise, architecture topics |
| **Ground-truth scoring** | [`llm-assesment-v2 - gt_scores.csv`](research-files/analysis-csv/llm-assesment-v2%20-%20gt_scores.csv) | 216 | One score: expert rates a `(Diagram, Criterion, Guideline)` on scale **1–4** |
| **Pairwise preference (Phase 3)** | [`llm-assesment-v2 - pairwise_preferences.csv`](research-files/analysis-csv/llm-assesment-v2%20-%20pairwise_preferences.csv) | 253 | One comparison: expert picks better LLM reasoning (image / text / tie) |

> **Why 216 ground-truth rows (not 240)?** Of the 16 participants who completed the demographics phase, 15 submitted ground-truth scores (P010 submitted none). Each responding expert scored one assigned diagram across the 15 guidelines. Fourteen experts completed all 15 guidelines (14 × 15 = 210 rows), and one expert (P001, on `sentry`) submitted 6 of the 15 guidelines (6 rows). This yields 210 + 6 = **216** rows. Equivalently: 240 − 15 (P010 absent) − 9 (P001 partial: 15 − 6) = 216.

### Key columns

**Demographics**

- `Expert_ID` — anonymous participant code  
- `Participant_Profile` — Undergraduate / Master's / PhD  
- `Development_Experience`, `Architecture_Analysis_Experience`, `Microservices_Architecture_Experience`, `Quality_Attributes_Tradeoffs_Experience` — self-reported levels (`low` / `medium` / `extensive`)  
- `Architecture_Topics` — comma-separated topics selected  

**Ground-truth scores (`gt_scores.csv`)**

- `Diagram_ID`, `Criterion`, `Guideline` — what was evaluated  
- `Human_GT_Score` — ordinal score **1 (Poor) … 4 (Excellent)**  
- `Expert_Comment` — optional free text  

**Pairwise preferences (`pairwise_preferences.csv`)**

- `Diagram_ID`, `Criterion`, `Guideline` — comparison context  
- `Internal_Source_Group` — source model of the pair: `ChatGPT` (= GPT-5) or `Claude` (= Claude Sonnet 4.6); see [Model labels](#model-labels)  
- `Response_A_Format`, `Response_B_Format` — `PNG`, `SVG`, or `XML`  
- `Preferred_Format` — `PNG` (image), `SVG`/`XML` (text), or `Tie`  
- `Comparison_Justification` — optional free text  

### Phase 3 responses by diagram

| `Diagram_ID` | Pairwise comparisons |
|---|---:|
| `magda-io` | 74 |
| `appwrite` | 42 |
| `spryker` | 39 |
| `research-modifiability-pattern-experiment` | 35 |
| `geoserver-cloud` | 32 |
| `sentry` | 31 |
| **Total** | **253** |

### Derived datasets (for analysis)

Built from the raw survey + LLM runs — see notebooks in each subfolder:

| Folder | Main outputs |
|---|---|
| [`ground-truth/`](research-files/analysis-csv/ground-truth/) | `ground_truth_ordinal.csv`, `ground_truth_binary.csv`, `selected_experts.csv` — two experts per diagram selected for GT aggregation (`build_ground_truth.ipynb`) |
| [`llm-evaluations/`](research-files/analysis-csv/llm-evaluations/) | `evaluations_ordinal.csv`, `evaluations_binary.csv` — flattened LLM JSON outputs (`build_evaluations.ipynb`) |
| [`rq-analysis/`](research-files/analysis-csv/rq-analysis/) | RQ1–RQ3 notebooks, result CSVs, figures, and narrative reports in [`rq-analysis/reports/`](research-files/analysis-csv/rq-analysis/reports/) |

**Evaluation criteria** (all phases): `accuracy`, `clarity`, `completeness`, `consistency`, `level_of_detail`. Each criterion has several **guidelines** (rubric sub-items); IDs match the prompt JSON schema (e.g. `notation_uniformity`, `component_matching`).

---

## Diagrams (case studies)

Six open-source architecture diagrams were used. Each case study lives in its own folder under `research-files/`.

### Diagram index

| `Diagram_ID` (in CSVs) | Folder | Source / topic |
|---|---|---|
| `appwrite` | [`research-files/appwrite/`](research-files/appwrite/) | Appwrite backend platform |
| `geoserver-cloud` | [`research-files/geoserver/`](research-files/geoserver/) | GeoServer Cloud |
| `magda-io` | [`research-files/magda-io/`](research-files/magda-io/) | Magda data portal |
| `spryker` | [`research-files/spryker/`](research-files/spryker/) | Spryker demoshop container stack |
| `sentry` | [`research-files/sentry/`](research-files/sentry/) | Sentry ingestion architecture |
| `research-modifiability-pattern-experiment` | [`research-files/research-modifiability-pattern-experiment/`](research-files/research-modifiability-pattern-experiment/) | Research modifiability pattern |

> **Note:** CSVs use `geoserver-cloud`; the folder name is `geoserver`.

### Standard layout (every case study)

```
<case-study>/
├── assets/
│   ├── description.txt          # Textual architecture description (always used)
│   ├── *.png                    # Image representation (PNG → "image" in analysis)
│   └── *.svg / *.xml            # Text representation (SVG/XML → "text" in analysis)
├── scripts/
│   └── run_evaluation.py        # Runs all criteria × models × formats
├── evaluations/                 # Raw LLM outputs (JSON + text per run)
│   ├── chatgpt_png/
│   ├── chatgpt_svg/  (or chatgpt_xml/)
│   ├── claude_png/
│   └── claude_svg/   (or claude_xml/)
└── commands.txt                 # Example commands
```

### Input files per diagram

| Diagram | Image (PNG) | Text (SVG/XML) | Description |
|---|---|---|---|
| appwrite | `overview.drawio.png` | `overview.drawio.svg` | `description.txt` |
| geoserver-cloud | `gs_cloud_architecture_diagram.png` | `gs_cloud_architecture_diagram.svg` | `description.txt` |
| magda-io | `magda.drawio.png` | `marketecture.svg` | `description.txt` |
| spryker | `container-stack.png` | `container-stack.drawio.xml` | `description.txt` |
| sentry | `sentry.drawio.png` | `sentry.drawio.xml` | `description.txt` |
| research-modifiability-pattern-experiment | `02_architecture-final.png` | `02_architecture-final_draw.io.xml` | `description.txt` |

### LLM experimental design (per diagram)

- **Models:** GPT-5 and Claude Sonnet 4.6 (labeled `chatgpt`/`ChatGPT` and `claude`/`Claude` respectively throughout the raw outputs and CSVs — see [Model labels](#model-labels))  
- **Representations:** PNG (image) vs SVG/XML (text)  
- **Criteria:** 5 rubrics × multiple guidelines each  
- **Runs:** one JSON (+ text log) per `(model, format, criterion)` — see [`llm-evaluations/trials_selected.csv`](research-files/analysis-csv/llm-evaluations/trials_selected.csv) for the exact file manifest  

Ground-truth and pairwise analyses use **6 diagrams**

---

## Prompts (`research-files/prompts/`)

One markdown template per criterion. Placeholders `[Insert diagram here]` and `[Insert textual description here]` are filled at runtime. The LLM must return JSON with per-guideline scores 1–4 and justifications.

- `architecture-accuracy-evaluation.md`
- `architecture-clarity-evaluation.md`
- `architecture-completeness-evaluation.md`
- `architecture-consistency-evaluation.md`
- `architecture-level-of-detail-evaluation.md`

---

## Model labels

The two models reported in the paper are **GPT-5** and **Claude Sonnet 4.6**. For historical reasons, the raw evaluation outputs, folder names (`chatgpt_*/`, `claude_*/`), CSV values (`ChatGPT`/`Claude`), and runner scripts use generic provider labels. These are kept unchanged so that existing file paths and analysis notebooks remain reproducible. The mapping is:

| Label in artifact (folders, CSVs, scripts) | Model reported in the paper | Provider / API |
|---|---|---|
| `chatgpt` / `ChatGPT` | GPT-5 | OpenAI |
| `claude` / `Claude` | Claude Sonnet 4.6 | Anthropic |

---

## LLM clients

- [`research-files/chatgpt_integration/client.py`](research-files/chatgpt_integration/client.py) — OpenAI (GPT-5)  
- [`research-files/claude_integration/`](research-files/claude_integration/) — Anthropic (Claude Sonnet 4.6)  

Batch runners: [`run_all_chatgpt.py`](research-files/run_all_chatgpt.py), [`run_all_claude.py`](research-files/run_all_claude.py).

---

## Reproducing the analysis

Install the dependencies (Python 3.10+ recommended):

```bash
pip install -r research-files/requirements.txt
```

Then run the notebooks in order:

```texts
1. ground-truth/build_ground_truth.ipynb   → ground_truth_*.csv
2. llm-evaluations/build_evaluations.ipynb → evaluations_*.csv
3. rq-analysis/rq1_overall.ipynb
4. rq-analysis/rq2_per_criterion.ipynb
5. rq-analysis/rq3_preference.ipynb
```

Shared helpers: [`rq-analysis/analysis_utils.py`](research-files/analysis-csv/rq-analysis/analysis_utils.py).

---

## Other folders (not required for survey/diagram review)

- **`aea/`** — Google Apps Script app used to collect expert responses (gitignored in full deployments; audit mirror linked above).  
- **`venv/`**, **`evaluations/`** — local/runtime artifacts; may be absent in a minimal checkout.
