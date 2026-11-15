# Kolobok roadmap

## 0.1 — Working foundation (in repository)

- [x] FastAPI service and browser interface
- [x] Conversation and message storage
- [x] OpenAI-compatible, Gemini, and Anthropic adapters
- [x] SQLite knowledge nodes and relations
- [x] Feedback scores and source metadata
- [x] Authenticated event-ingestion endpoint
- [x] Render Blueprint for a free preview
- [ ] Automated CI run and deployment smoke test

## 0.2 — Safe cloud foundation

- [ ] Review and deploy the Render Blueprint
- [ ] Configure a durable database and automated backups
- [ ] Add request rate limits, session expiry, and audit events
- [ ] Add provider configuration UI backed by a secure secret-management flow
- [ ] Add conversation search, rename, export, and import metadata
- [ ] Add graph node detail, editing, edge management, and filters

## 0.3 — Agents and background work

- [ ] Durable task queue with retries and checkpoints
- [ ] Multi-agent review with evidence and disagreement tracking
- [ ] Tool registry, permissions, and action audit trail
- [ ] Scheduled research tasks with source attribution
- [ ] Budget limits, provider fallback, and usage visibility

## 0.4 — Local companion and browser extension

- [ ] Windows companion with explicit install and startup controls
- [ ] Event-driven UI Automation and process/window context
- [ ] Browser extension with scoped tab and page permissions
- [ ] Local voice activation and four voice/text interaction modes
- [ ] Visible monitoring state, permission manager, and emergency stop
- [ ] Remote command execution only through confirmed, logged actions

## 0.5 — Knowledge graph and version lineage

- [ ] Confirm the node and relation taxonomies
- [ ] Build interactive graph visualization and exact-ID lookup
- [ ] Add relevance/currentness and evaluator metadata
- [ ] Add source-aware importers for supported conversation exports
- [ ] Add graph replication to GitLab when project/API access is available
- [ ] Add version snapshots, migration, and improvement comparisons

## 0.6 — Distribution

- [ ] Browser/PWA build
- [ ] Windows desktop installer and signed update mechanism
- [ ] Optional Linux and macOS clients
- [ ] Vercel frontend deployment
- [ ] GitBook documentation site when an organization is available
- [ ] Replit development mirror without overwriting unrelated apps

## Release rule

A roadmap item is not complete merely because it is described. Mark it complete only after implementation and a test or deployment check proves it works.
