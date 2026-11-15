# Kolobok / LabokUS

Kolobok is a personal AI assistant project. This repository contains the first runnable foundation: a FastAPI service, a browser UI, provider adapters, a SQLite knowledge graph, chat history, and an authenticated event-ingestion endpoint.

## Current foundation

- Browser interface for chat, knowledge nodes, and system status.
- OpenAI-compatible, Gemini, and Anthropic provider adapters.
- Provider configuration through environment variables. Never commit API keys.
- SQLite storage for conversations, messages, knowledge nodes, and graph edges.
- Feedback scores and source metadata on knowledge nodes.
- Authenticated local-agent event ingestion.
- Health endpoint and Render Blueprint.

## Run locally

1. Use Python 3.11 or newer.
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and configure a provider if desired.
4. Start: `uvicorn app.main:app --reload`
5. Open http://127.0.0.1:8000

The app works without an AI provider: the knowledge graph and interface remain available, while chat reports that a provider is not configured.

## Environment

| Variable | Purpose |
| --- | --- |
| `APP_ACCESS_TOKEN` | Optional access password. Required for a public deployment; Render generates one in the Blueprint. |
| `DATABASE_PATH` | SQLite database path; defaults to `data/kolobok.db`. |
| `AI_PROVIDER` | `openai-compatible`, `gemini`, or `anthropic`. |
| `AI_API_KEY` | Provider API key. Keep it in deployment secrets only. |
| `AI_BASE_URL` | Optional OpenAI-compatible base URL. |
| `AI_MODEL` | Model name. |
| `AGENT_EVENT_TOKEN` | Separate token required for local-agent event ingestion. |

### Provider examples

- OpenAI-compatible: set `AI_PROVIDER=openai-compatible`, `AI_API_KEY`, and `AI_MODEL`. For a compatible gateway, also set `AI_BASE_URL`.
- Gemini: set `AI_PROVIDER=gemini`, `AI_API_KEY`, and `AI_MODEL` (for example, a Gemini model supported by your account).
- Anthropic: set `AI_PROVIDER=anthropic`, `AI_API_KEY`, and `AI_MODEL`.

## Important deployment notes

The initial Render Blueprint uses a free web-service plan and SQLite. Free instances may sleep and their local filesystem is ephemeral; database contents can be lost on redeploy or instance replacement. Do not use this deployment for irreplaceable personal data. A persistent database (for example, managed PostgreSQL) and a private access policy should be configured before relying on cloud persistence.

## Architecture boundaries

- The knowledge graph stores explicit records, relations, provenance, and feedback. It does not read or modify hidden neural-network weights of external models.
- Model providers are replaceable adapters. The assistant identity and stored knowledge belong to Kolobok, not to a provider.
- The event endpoint accepts structured, minimal event summaries. It is not a screenshot streamer or covert monitoring agent.
- A future Windows companion and browser extension must request scoped permissions, show when active, keep an action log, and provide an emergency stop.
- Imported conversations should retain their source and timestamps. Importers are not included in this first foundation.
- Long-running cloud jobs, multi-agent review, GitLab graph replication, desktop packaging, and automatic updates are planned next, not claimed as implemented here.

## Security

Never put API keys, passwords, access tokens, private conversation exports, or personal files in Git. Use deployment secret/environment-variable controls. Set a strong `AGENT_EVENT_TOKEN` before enabling an event-producing local agent. Public deployment should remain a test environment until authentication, persistence, and rate limits have been reviewed.
