# Pydantic AI Examples

Five example agents built with [Pydantic AI](https://github.com/pydantic/pydantic-ai), each demonstrating different SDK
features. Runs on Docker Compose with a LiteLLM proxy routing to Gemini.

## Quick Start

```bash
cp .env.example .env    # edit with your API keys
docker compose up --build
```

Open each agent at `http://localhost:PORT`.

## Agents

| Agent              | Port | SDK Feature                           | What it does                                   |
|--------------------|------|---------------------------------------|------------------------------------------------|
| Web Researcher     | 9801 | Custom tools (Firecrawl)              | Searches and scrapes the web                   |
| Data Extractor     | 9802 | `@agent.tool` with flat params        | Extracts structured fields from text           |
| Flight Booker      | 9803 | Multi-agent delegation, `UsageLimits` | Searches flights, extracts seat preference     |
| RAG Q&A            | 9804 | Custom tools + vector store           | Ingests documents, answers via semantic search |
| Decision Framework | 9805 | `@agent.tool` structured output       | Scores options with pros/cons and recommends   |

## Architecture

```
User ──► agent.to_web() ──► Agent ──► LiteLLM proxy ──► Gemini
                                    │
                                    ├── @agent.tool (Firecrawl, ChromaDB)
                                    ├── sub-agent delegation
                                    └── flat output_type unions
```

- **`agent.to_web()`** — each agent creates its own FastAPI web chat UI
- **LiteLLM proxy** runs at `http://litellm-proxy:4000/v1`, routes `openai-chat:` prefixed models to Gemini
- **`ModelSettings(timeout=30)`** set on all agents

## Environment Variables

| Variable            | Description                                                                 |
|---------------------|-----------------------------------------------------------------------------|
| `OPENAI_API_KEY`    | Your API key (Gemini or OpenAI)                                             |
| `OPENAI_BASE_URL`   | LiteLLM proxy endpoint                                                      |
| `MODEL_STRING`      | Model routed through LiteLLM (e.g. `openai-chat:gemini/gemma-4-26b-a4b-it`) |
| `FIRECRAWL_API_KEY` | Firecrawl API key for web search                                            |

## Switching Models

Change `MODEL_STRING` in `.env` to use a different provider through LiteLLM:

- **OpenAI**: `openai:gpt-4o`
- **Anthropic**: `openai-chat:anthropic/claude-sonnet-4-20250514`
- **Google**: `openai-chat:gemini/gemma-4-26b-a4b-it`

## Project Structure

```
├── agents/
│   ├── researcher/agent.py       # Firecrawl search + fetch
│   ├── extractor/agent.py        # Flat tool-param extraction
│   ├── flight_booker/agent.py    # Multi-agent delegation
│   ├── rag_qa/agent.py           # ChromaDB vector search
│   ├── rag_qa/knowledge.py       # ONNX embedder + ChromaDB
│   └── decision/agent.py         # Structured decision tool
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── .env.example
```
