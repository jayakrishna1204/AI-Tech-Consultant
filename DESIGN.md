# System Design

## 1. Overview

This project implements three AI-assisted workflows: a Knowledge Brain for product support, an Inbox Agent for customer email drafting, and a Meeting-to-Scope system for generating project scopes and detecting changes. Human review is required for important outputs.

## 2. Architecture

### Task 1: Knowledge Brain

The Knowledge Brain uses a crawler to collect public product-support articles. Article data is stored in SQLite and retrieved using text similarity. A FastAPI service exposes endpoints for asking questions, synchronizing articles, and submitting expert feedback. The interface is built with Streamlit.

The assistant returns an answer with source links when available. Retrieved answers should be verified for relevance and accuracy.

### Task 2: Inbox Agent

The Inbox Agent processes customer emails, classifies their intent, retrieves relevant product knowledge through the Task 1 API, and drafts a suggested reply. A Streamlit interface supports human review. Reviewed drafts and edits are stored for future reference.

The system does not automatically send customer emails.

### Task 3: Meeting to Scope

The Meeting-to-Scope system accepts meeting transcripts and generates a draft project summary, deliverables, implementation tasks, estimated hours, assumptions, exclusions, risks, and open questions. It retrieves product knowledge from Task 1 where relevant.

The scope comparison module compares previous and updated requirements and deliverables, calculates estimated-hour differences, and flags potential changes for human approval.

## 3. Technology Stack

- Python for application logic and AI workflows.
- Ollama with the Llama 3.2 model for local language-model inference.
- FastAPI for the Knowledge Brain API.
- Streamlit for user interfaces.
- SQLite for article data, expert feedback, and email-review records.
- Text similarity and explicit wording aliases for retrieval and scope comparison.

## 4. Human Oversight

AI-generated answers, email drafts, and project estimates can contain errors. Users must review outputs before relying on them. Scope changes require approval, and the current email workflow produces drafts rather than sending messages automatically.

## 5. Limitations and Future Work

- Improve retrieval quality and citation relevance.
- Expand tests for incorrect answers and missing knowledge.
- Improve semantic matching of requirements and deliverables.
- Evaluate model quality across representative datasets.
- Add persistent approval tracking and robust incremental synchronization.
- Measure latency, reliability, and quality using repeatable evaluation cases.