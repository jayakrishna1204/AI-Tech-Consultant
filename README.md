# AI Tech Consultant

An AI-assisted project containing three workflows: a product Knowledge Brain, an Inbox Agent for customer email drafts, and a Meeting-to-Scope assistant.

## Features

- Knowledge Brain: Retrieves product-support information and provides answers with source links.
- Inbox Agent: Classifies customer emails, retrieves relevant knowledge, and drafts replies for human review.
- Meeting to Scope: Generates project summaries, deliverables, tasks, effort estimates, assumptions, risks, and questions. Compares successive scopes to identify possible changes.

## Technology Stack

Python, Ollama, Llama 3.2, FastAPI, Streamlit, SQLite, and text-similarity-based retrieval.

## Prerequisites

- Python 3.11
- Ollama installed and running
- The `llama3.2` model downloaded in Ollama

## Setup

From the project root, create and activate a virtual environment if you have not already done so.

On Windows PowerShell:

## Powershell Commands

```
python -m venv .venv
```

```
.venv\Scripts\Activate.ps1
```

```
pip install -r requirements.txt ollama pull llama3.2
```

If `requirements.txt` does not exist yet, create it or install the dependencies documented by your project before running these commands.

## Running the Applications

Open separate terminals from the project root.

### 1. Knowledge Brain API

## Powershell 1st Terminal

```
uvicorn task1_knowledge_brain.main:app --reload
```

API documentation: `http://127.0.0.1:8000/docs`

### 2. Knowledge Brain UI

## Powershell 2nd Terminal

```
python -m streamlit run task1_knowledge_brain/ui.py
```

### 3. Inbox Agent

## Powershell 3rd Terminal

```
python -m streamlit run task2_inbox_agent/main.py
```

### 4. Meeting to Scope

## Powershell 4th Terminal

```
python -m streamlit run task3_meeting_scope/main.py
```

Keep the Knowledge Brain API running while testing the other workflows that depend on it.

## Evaluation

Evaluation cases and currently tested scope-comparison behavior are documented in `EVALS.md`. Architecture and design decisions are documented in `DESIGN.md`.

## Human Review and Limitations

AI-generated answers, email drafts, and project estimates can be incorrect. Review outputs before relying on them. The Inbox Agent produces drafts rather than automatically sending emails. Scope changes require human review. Features such as robust incremental synchronization, broader semantic matching, and persistent approval tracking may require further implementation.

## Project Structure

- `shared/` — shared LLM utilities.
- `task1_knowledge_brain/` — crawling, retrieval, API, database, and UI.
- `task2_inbox_agent/` — email classification, drafting, learning, and UI.
- `task3_meeting_scope/` — scope generation, comparison, and UI.
- `EVALS.md` — evaluation results.
- `DESIGN.md` — architecture and design.

## Conclusion

The AI Tech Consultant puts product knowledge, inbox replies, and meeting-to-scope work in one system that a small team can run at scale.The Knowledge Brain is the shared memory. The Inbox Agent and Meeting to Scope call its API, so answers stay consistent across every workflow.Together they help a software business answer customers faster, turn meetings into clear proposals, and keep getting better from the people who use it.