# Kolobok / LabokUS — project brief for Claude

You are helping develop Колобок (Kolobok), a personal AI assistant. Main repository: https://github.com/YornerBETA/LabokUS. Kolobok is the product identity; GPT, Gemini, Claude, Qwen, Kimi and other models are interchangeable providers.

## Current release and naming
Current release: 1.1.0. Windows package path: 1.1.0/W/x64/ru/all/.
- W = Windows; x64 = architecture; ru = Russian human language for UI/installer; all = programming-language pack, not a human language.
- Future platform codes: LX Linux, MO macOS, AND Android, iOS iOS. Architecture is a separate level: x64, x86, arm64, etc.
- Agreed language set: Python, Java, JavaScript, TypeScript, C, C++, C#, Kotlin, Go, HTML, CSS, SQL, PowerShell, Bash; PHP optional. Catalog entries do not prove compilers are bundled.

## Hardware
Target is Windows 10 on a modest Intel Core i5 laptop with weak/integrated graphics (originally Windows 7, later upgraded to Windows 10). Keep CPU/RAM/GPU use low. Do not require Blender, Unity, Unreal, CUDA or a dedicated GPU. Prefer lightweight native UI, CPU geometry and cloud-assisted heavy work.

## Product architecture
Windows desktop app; browser UI without desktop mascot; cloud API; opt-in Windows local agent; versioned plugins/extensions. Local monitoring must be visibly indicated, scoped, permission-based, logged and stoppable. No covert monitoring. Do not auto-run untrusted extensions.

## Providers and secrets
User supplies API keys/OAuth. Support OpenAI-compatible providers and dedicated Gemini/Anthropic adapters where implemented. Store secrets in local user storage or server environment, never in GitHub, ZIPs or client-side web code. No unlimited free inference/compute claims.

## Telegram
Use official Telegram Bot API directly. The Kolobok computer need not open Telegram Web or desktop Telegram. User creates bot via @BotFather, sets token and starts the private chat once. Restrict allowed numeric user IDs. A Telegram client is still needed on the user's device to read messages. Never commit bot tokens.

## Voice
Target modes: Voice→Voice, Text→Text, Voice→Text, Text→Voice. Future features may include streaming mic capture, STT/TTS, wake phrase “Привет, Колобок”, barge-in and device routing. Current prototype is limited to local Windows TTS and transcription of a selected audio file via API. Do not claim always-on mic or full duplex until implemented and tested. Mic use must be opt-in, visibly indicated and stoppable.

## Updates
Kolobok and AI API versions are independent. Notify separately; if startup popups are suppressed, retain a persistent in-app notice. Never install automatically. Universal installer lists published GitHub Releases, filters OS/architecture/human language/programming pack, downloads only after user selection and verifies SHA-256 when a checksum is available.

## Memory and 3D/music
Knowledge nodes preserve IDs, source/provenance, tags, importance, quality, context needs, relations and feedback. Preserve timestamps when importing. Do not store credentials or sensitive data. Keep summaries/evidence/actions/results, not hidden chain-of-thought. Current 3D is a light wireframe prototype, not Blender. Current music generator makes a short original WAV motif, not a DAW; do not copy protected film cues or recordings.

## Platforms
GitHub is canonical source/releases. Render Free Web Service may sleep and its local filesystem is ephemeral; durable cloud memory needs a managed database/persistent store. Vercel is an optional static frontend and needs a GitHub Login Connection before repo linking. GitLab is an optional private knowledge mirror. Replit is a separate dev/preview project; do not modify unrelated apps. GitBook is optional. Cloudflare is optional; do not create billable resources without review. Connector access in ChatGPT does not automatically give Kolobok access; it needs its own credentials.

## Engineering rules
Read actual source before editing. Distinguish implemented/prototype/planned/unverified. Run syntax checks and tests; report what actually ran. Preserve Windows 10 compatibility. Use migrations and backups for DB changes. Use HTTPS, auth, rate limits, timeouts, retries, logs and input validation. Never commit .env, tokens, user DBs or chat exports. Avoid infinite agent loops; use budgets, checkpoints, retries and cancellation. Never claim deployment is live unless the host confirms.

## Current status
Windows 1.1.0 / x64 / ru / all ZIP exists. GitHub has version metadata and a compact desktop entrypoint; the fuller ZIP contains additional local integrations and update-notice logic. Remote MCP server code has been committed to the cloud backend but requires a successful latest Render deploy before the private connector can connect. GitHub Release asset is not yet published, so the universal installer will list no versions until the matching ZIP and checksum are attached to a Release.