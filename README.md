# Tech-News AI Summarizer

An automated, end-to-end data pipeline and web application that ingests daily technology news from Hacker News, generates structured AI summaries via the Google Gemini API, and presents them on an interactive web dashboard.

 **Live Demo:** [Tech-News AI Dashboard](https://tech-news-ai.streamlit.app/)

---

## Overview

Staying up-to-date with technical news can be time-consuming. This project automates the entire ingestion, analysis, and visualization process:
1. **Fetches** top tech articles daily via RSS feed parser.
2. **Analyzes & Summarizes** articles using Google Gemini (`gemini-3.6-flash`) with strict Pydantic JSON schema output.
3. **Persists** structured data in an SQLite database with duplicate filtering.
4. **Automates** execution serverlessly using GitHub Actions.
5. **Visualizes** content on a responsive Streamlit Cloud dashboard with dynamic filter options.

---

##  System Architecture & Data Flow

```text
[ Hacker News RSS Feed ]
           │
           ▼
[ Python Ingestion Pipeline (main.py) ]
           │
           ├──► [ Gemini API (Structured Pydantic JSON Schema) ]
           │
           ▼
[ SQLite Database (news.db) ]
           ▲
           │
┌──────────┴──────────────────────────┐
│  Automation & Presentation Layer    │
├─────────────────────────────────────┤
│ 🤖 GitHub Actions (Daily Cron Job)  │ ──► Auto-commit new records
│ 📊 Streamlit Cloud Dashboard        │ ──► Real-time data visualization
└─────────────────────────────────────┘
````
---
## Tech Stack
- Language: Python 3.11+

- Data Acquisition: feedparser

- Data Validation & Schemas: pydantic

- LLM Integration: google-genai (Model: gemini-3.6-flash)

- Database: SQLite3

- Frontend / Dashboard: Streamlit

- CI/CD & Automation: GitHub Actions

- Environment & Security: python-dotenv, GitHub Repository Secrets

 Technical Highlights & Engineering Aspects
1. Structured Output Enforcement via Pydantic
Instead of parsing unstructured LLM text responses, the application uses Structured Outputs by binding a Pydantic model (NewsAnalysis) directly to the Gemini API payload (response_schema). This guarantees type safety and consistent JSON structure for attributes such as summary, rating, and category.

2. API Rate-Limiting & Resilience
Throttling: Implemented deliberate delay loops (time.sleep(12)) between requests to respect Gemini Free-Tier rate limits (max 5 Requests Per Minute).

Retry Mechanism & Error Handling: Built-in exception handling intercepts transient API errors (429 Too Many Requests or 503 Service Unavailable) and executes exponential backoff retries before failing gracefully.

3. Deduplication Engine
To prevent unnecessary API token usage and redundant entries, the ingestion layer queries the SQLite database (article_exists()) using unique URL constraints before invoking the LLM API.

4. Headless Cloud CI/CD Automation
The daily data pipeline is orchestrated by a GitHub Actions workflow (.github/workflows/daily_pipeline.yml):

Scheduled via Cron syntax (0 8 * * * UTC).

Automatically sets up a headless Python environment and installs dependencies.

Injects the API key securely via secrets.GEMINI_API_KEY.

Commits updated database states back to the repository using a bot account (contents: write permissions).

5. Security & Secret Management
No hardcoded credentials. Local execution leverages .env files (excluded via .gitignore), while production execution relies on encrypted GitHub Repository Secrets.
