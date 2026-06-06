# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **AI Research Hub** — a personal lab combining trend monitoring with hands-on experimentation. There are two distinct workspaces:

- `trends/` — Markdown research notes collected by Claude (automated and on-demand)
- `experiments/` — Self-contained Python experiment folders, each independently runnable

The vault doubles as an [Obsidian](https://obsidian.md) knowledge base; `Home.md` serves as the dashboard and uses Dataview queries to surface recent trends and experiment status.

## Environment Setup

All secrets live in `.env` (not committed). Copy `.env.example` and fill in the keys you need for the experiment you're running:

```bash
cp .env.example .env
```

Required keys per area:
- **Anthropic experiments**: `ANTHROPIC_API_KEY`
- **OpenAI / Azure experiments**: `OPENAI_API_KEY` (and Azure keys if needed)
- **Bedrock experiments**: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`
- **Langfuse tracing**: `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`
- **AI digest script**: `SLACK_WEBHOOK_URL`, `TWITTER_BEARER_TOKEN` (optional)

## Running Experiments

Each experiment folder is self-contained with its own `requirements.txt`. The general pattern:

```bash
cd experiments/<topic>
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py          # or the numbered script: python 01_create_guardrail.py
```

### Bedrock Guardrails (run scripts in order)

```bash
cd experiments/bedrock-guardrails
python 01_create_guardrail.py   # creates guardrail → outputs guardrailId/version for .env
python 02_apply_guardrail.py    # tests guardrail independently (no LLM call)
python 03_converse_with_guardrail.py  # full Claude conversation with guardrail active
```

`01_create_guardrail.py` must run first — it creates the AWS resource whose ID is required by the subsequent scripts.

### AI Digest Script

```bash
cd scripts
python ai_digest.py
```

Pulls from HackerNews (Algolia API), arXiv (XML feed), YouTube RSS, and optionally Threads/X. Translates titles to Korean via GPT-4o-mini and posts to Slack.

## Architecture

### Experiment Design Pattern

Each experiment folder follows a layered demonstration structure — numbered scripts build on each other (e.g., `01_` creates infrastructure, `02_` applies it standalone, `03_` integrates with an LLM). The pattern applies to both Langfuse (basic tracing → manual tracing → LLM-as-judge) and Bedrock Guardrails.

Within scripts, the common flow is:
1. Load env via `python-dotenv`
2. Initialize SDK clients (Anthropic, OpenAI, Boto3, Langfuse)
3. Define test cases or prompts inline
4. Run with `rich` console output (tables, panels) for visual validation

### LLM-as-Judge Pattern (`experiments/agent-eval/`, `experiments/langfuse/03_llm_as_judge.py`)

A generator LLM produces a response; a separate judge LLM scores it against a rubric (accuracy, completeness, conciseness). Scores are normalized 0–1 and — when Langfuse is active — attached to the trace as scores so they appear in the dashboard.

### Langfuse Integration

Two tracing styles are used across experiments:
- **Decorator-based** (`@observe()`): wraps functions automatically — used in `01_basic_tracing.py`
- **Manual context manager** (`start_as_current_observation()`): explicit span/generation control — used in `02_manual_tracing.py`

The `langfuse.openai.openai` client drop-in replaces the standard OpenAI client to auto-capture generations.

### Trends Workflow

Trend files in `trends/` use frontmatter:

```yaml
---
date: YYYY-MM-DD
tags: [tag1, tag2]
sources: [url1, url2]
---
```

The `Home.md` Dataview query surfaces the 10 most recent entries sorted by `date`. When adding a new trend note, use `templates/trend.md` as the base. New experiment notes should use `templates/experiment.md`.

### Daily Logs

Work-in-progress notes and next steps live in `daily/YYYY-MM-DD.md`. These are informal and not templated.
