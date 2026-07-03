# Hidden Fork: LLM Endpoint Evaluation Framework

This repository folder contains the public, sanitized project package for my undergraduate dissertation:

**Hidden Fork: Measuring Behavioral Divergence Across API, Web App, and Shadow Relay Endpoints for Large Language Models**

The project measures how the same named large language model can behave differently when accessed through:

- official API endpoints
- official web applications
- third-party shadow relay endpoints

The final experiment compares GPT-5.4, Claude Sonnet 4.6, and Gemini 3 Flash across six benchmarks covering math, science, medicine, law, broad knowledge, and safety.

## Highlights

- Built an end-to-end Python experiment runner for LLM benchmark collection, parsing, scoring, retrying, and report generation.
- Automated web application runs with Playwright while preserving separate browser state files locally.
- Collected a final composite dataset covering 3 models x 3 endpoint types x 6 benchmarks.
- Produced paper-ready CSV tables, figures, failure audits, and a 39-page dissertation PDF.
- Identified a protocol-level shadow relay failure where Gemini 3 Flash produced 0/30 on AIME because all long reasoning responses were truncated before a final answer.

## Key Results

- GPT-5.4 scored 93.3% on AIME 2025 through the API but 66.7% through the web app, a 26.6 percentage point endpoint gap.
- Gemini 3 Flash scored 96.7% on AIME through both official API and web app, but 0.0% through one shadow relay due to response truncation.
- Claude Sonnet 4.6 showed bidirectional endpoint differences: web app beat API on AIME but lost on GPQA.
- Safety scores also varied by endpoint for Claude and Gemini.

## Repository Layout

```text
.
|-- run_experiment.py               # Main collection, scoring, retry, and reporting pipeline
|-- prepare_data.py                 # Benchmark sampling / dataset lock helper
|-- generate_figures.py             # Paper figure generator
|-- sync_final_results_and_paper.py # Result-to-paper synchronization helper
|-- convert_paper.py                # DOCX/PDF paper conversion helper
|-- experiment_state.py             # Local browser-state path definitions
|-- data/                           # Benchmark samples and dataset lock
|-- figures/                        # Paper figures in PNG/PDF
|-- results/final_merged_20260323/  # Final merged paper-ready CSV/JSON/MD results
|-- scripts/                        # Session setup, retry, and audit helpers
`-- paper/                          # Dissertation PDF, Markdown source, and defense deck
```

## Public Package Notes

This is a cleaned public version of the project. The following local-only artifacts are intentionally excluded:

- `playwright_state/`: browser profiles, cookies, and login state
- `logs/`: local runtime logs
- `results/runs/`: full raw/scored response archives, which are large and may include provider-specific output details
- `.claude/` and other local assistant settings
- API keys and environment files

One original retry helper contained a hard-coded Anthropic API key during development. The public copy has been sanitized to read from environment variables instead.

## Requirements

Install dependencies:

```bash
pip install -r requirements.txt
playwright install chromium
```

Set provider credentials only through environment variables:

```bash
set OPENAI_API_KEY=...
set ANTHROPIC_API_KEY=...
set GOOGLE_API_KEY=...
set SHADOW_BASE_URL=...
set SHADOW_KEY=...
```

For Google Vertex AI, use one of:

```bash
set VERTEX_API_KEY=...
set GOOGLE_VERTEX_API_KEY=...
```

## Example Commands

Generate final tables from already collected scored files:

```bash
python run_experiment.py --run-id formal_main_v1 --report-only
```

Run a one-item smoke test, assuming credentials are configured:

```bash
python run_experiment.py --run-id smoke_demo --models gpt-5.4 --endpoints api --benchmarks aime --max-items 1
```

Regenerate figures:

```bash
python generate_figures.py
```

Audit the Gemini shadow AIME truncation failure:

```bash
python scripts/audit_gemini_shadow_aime.py
```

## Dissertation

The dissertation PDF is available at:

```text
paper/Hidden_Fork_v4_thesis_v22.pdf
```

The Markdown source used for the paper is available at:

```text
paper/Hidden_Fork_v4_paper.md
```

## Author

Peng Jiaxuan  
BSc Software Engineering (Sino-Foreign Cooperative Education), Neusoft Institute Guangdong / University of the West of England, Bristol (UWE Bristol)
