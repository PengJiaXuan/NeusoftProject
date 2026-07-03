# NeusoftProject

This repository now showcases my undergraduate software engineering dissertation project:

## Hidden Fork: LLM Endpoint Evaluation Framework

**Hidden Fork** is an AI-assisted software engineering and large language model evaluation project. It measures how the same named LLM can behave differently across official API endpoints, official web applications, and third-party shadow relay endpoints.

Project folder:

[HiddenFork-LLM-Endpoint-Evaluation](./HiddenFork-LLM-Endpoint-Evaluation)

## What It Does

- Automates benchmark collection across API, Web App, and shadow relay endpoints.
- Uses Python and Playwright to collect, parse, score, retry, and audit LLM responses.
- Compares GPT-5.4, Claude Sonnet 4.6, and Gemini 3 Flash across six benchmarks.
- Produces reproducible result tables, figures, failure audits, dissertation PDF, and defense materials.

## Key Results

- GPT-5.4 scored **93.3%** on AIME 2025 through API but **66.7%** through Web App.
- Gemini 3 Flash scored **96.7%** on official API/Web App but **0.0%** through one shadow relay due to response truncation.
- Claude Sonnet 4.6 showed benchmark-dependent endpoint divergence.
- Safety behavior also varied between API and non-API endpoints.

## Repository Contents

```text
HiddenFork-LLM-Endpoint-Evaluation/
|-- run_experiment.py
|-- data/
|-- figures/
|-- results/final_merged_20260323/
|-- scripts/
`-- paper/
```

The public package intentionally excludes browser login state, local logs, API keys, and full raw run archives.

## About

Author: Peng Jiaxuan  
Program: BSc Software Engineering (Sino-Foreign Cooperative Education), Neusoft Institute Guangdong / University of the West of England, Bristol (UWE Bristol)  
Dissertation: *Hidden Fork: Measuring Behavioral Divergence Across API, Web App, and Shadow Relay Endpoints for Large Language Models*
