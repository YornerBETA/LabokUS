# Kolobok architecture

## Identity and boundaries

Kolobok is the product identity and orchestration layer. OpenAI, Gemini, Anthropic, Qwen, Kimi, and other providers are replaceable model services. They do not own Kolobok's identity or its knowledge store.

The knowledge graph stores explicit information records, links, source provenance, and user feedback. It is not a representation of external model weights or hidden reasoning. Internal chain-of-thought is not requested or stored; the system should keep concise summaries, evidence, decisions, tool results, and task state.

## Platform responsibilities

| Platform | Intended role | Current status |
| --- | --- | --- |
| GitHub | Main source code, version history, releases, build workflows | Connected; initial code committed |
| GitLab | Separate graph/knowledge mirror and structured records | Connected; no LabokUS project found; Orbit graph API unavailable to this account |
| Render | Primary cloud runtime and long-running services | Blueprint created and planned; deployment awaits review/approval |
| Replit | Supplemental development and experiments | Connected; an unrelated existing app was found and left untouched |
| Vercel | Browser frontend, previews, and web delivery | Connected; no project created yet |
| Cloudflare | Future edge security, DNS, object storage, or data services | Account connected; no resources changed |
| GitBook | Published product documentation | Connected; no accessible organization was returned |

## Runtime layers

1. Browser UI: chat, conversation history, knowledge graph, system status.
2. API service: authentication, chat orchestration, graph CRUD, event intake.
3. Provider adapters: OpenAI-compatible APIs, Gemini, and Anthropic in the first release.
4. Data layer: SQLite for local development and initial preview; migrate to managed PostgreSQL before depending on cloud persistence.
5. Cloud workers: planned queue-based execution for long-running tasks, resumable checkpoints, retries, and provider fallback.
6. Local companion: planned Windows service for permitted local events and computer actions.
7. Browser extension: planned DOM/accessibility-based page context and tab events, scoped by explicit user permission.

## Live computer context

The target is event-driven, not a screenshot stream. A local companion should collect only the events needed for an active task (window/app changes, UI Automation events, explicit user-approved file changes, and browser extension DOM changes). It should send compact deltas, not a screenshot every second. Visual capture is a separate, explicit fallback for cases where structure is insufficient.

Local monitoring must have a visible active indicator, granular permissions, an event/action log, secure transport, and an emergency stop. It must not become covert monitoring. The cloud service can continue its own queued tasks while the user's computer is offline; it cannot interact with that offline computer.

## Knowledge graph

Implemented now:
- Nodes with a structured identifier in the form KN-slug-date-sequence.
- Name, type, content, tags, importance, quality, context requirement, source, timestamps, and feedback score.
- Directed edges with a relation label.
- Feedback scale: 1 (dislike), 5 (no rating/neutral), 10 (like); repeated ratings are blended rather than allowing one rating to dominate forever.

Planned:
- Node lineage and improvement ancestry.
- Relevance decay with refresh on reuse and positive feedback.
- Evaluator metadata and reason codes.
- Search by exact ID, source, topic, task, date, language, software, and related professions.
- Graph visualization with node details, filters, edge categories, and version comparison.
- GitLab replication once a project and an available graph/storage API are configured.

The user's proposed relation vocabulary is a draft, not a finalized schema. It includes conversation/sequence, thematic, person, context, modality, provider/model, task/source similarity, exact/approximate search and time, day/week/month/year, evaluation, profession, process/task, improvement basis, agent class, language, and software relations. Preserve exact semantics and confirm the final taxonomy before enforcing it.

## Security and secrets

- Never commit API keys or access tokens.
- Provider keys belong in deployment secrets or a local secret store.
- Separate the app access token from the local-agent event token.
- Keep public deployments as non-sensitive previews until persistent storage, rate limits, backups, and access controls are reviewed.
- Validate imported extension packages and execute them in a sandbox; never auto-run arbitrary ZIP contents.
- Destructive or privileged computer actions require explicit permission and confirmation.
