from __future__ import annotations

import os
import secrets
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.responses import JSONResponse

from . import db
from .providers import ProviderError, generate_reply, provider_config

mcp = FastMCP("Kolobok LabokUS", stateless_http=True, json_response=True)

@mcp.tool()
def kolobok_health() -> dict[str, str]:
    """Check the Kolobok MCP service health and current release."""
    return {"status": "ok", "name": "Kolobok", "api_version": "0.1.0"}

@mcp.tool()
def kolobok_status() -> dict[str, Any]:
    """Read configured AI provider and model status. Never returns API keys."""
    cfg = provider_config()
    return {"name": "Kolobok", "api_version": "0.1.0",
            "provider": cfg["provider"], "model": cfg["model"] or None,
            "model_configured": bool(cfg["api_key"] and cfg["model"])}

@mcp.tool()
def kolobok_list_conversations() -> list[dict[str, Any]]:
    """List saved Kolobok conversations."""
    return db.list_conversations()

@mcp.tool()
def kolobok_create_conversation(title: str = "Новый диалог") -> dict[str, Any]:
    """Create a new saved conversation."""
    return db.create_conversation(title)

@mcp.tool()
async def kolobok_send_message(conversation_id: str, message: str) -> dict[str, Any]:
    """Send a message through the configured AI provider and save the response."""
    if not message.strip() or len(message) > 12000:
        raise ValueError("Message must contain 1–12000 characters.")
    history = db.get_messages(conversation_id)
    db.add_message(conversation_id, "user", message)
    prompt = [{"role": "system", "content":
               "Ты — Колобок, персональный AI-ассистент. Отвечай по-русски, если пользователь не выбрал другой язык. Будь точным и не выдумывай выполненные действия."}]
    prompt.extend({"role": item["role"], "content": item["content"]} for item in history[-20:])
    prompt.append({"role": "user", "content": message})
    answer, provider, model = await generate_reply(prompt)
    return db.add_message(conversation_id, "assistant", answer, provider, model)

@mcp.tool()
def kolobok_list_knowledge_nodes(query: str = "") -> list[dict[str, Any]]:
    """Search or list knowledge-graph nodes."""
    return db.list_nodes(query or None)

@mcp.tool()
def kolobok_add_knowledge_node(name: str, content: str,
                               node_type: str = "note",
                               tags: list[str] | None = None,
                               importance: str = "ordinary",
                               source: str | None = None) -> dict[str, Any]:
    """Add a knowledge node. Do not store passwords, API keys or sensitive personal data."""
    if not name.strip() or len(name) > 200 or len(content) > 12000:
        raise ValueError("Name/content length is outside the allowed range.")
    return db.create_node({"name": name, "content": content, "node_type": node_type,
                           "tags": tags or [], "importance": importance,
                           "source": source, "context_required": False})

@mcp.tool()
def kolobok_rate_knowledge_node(node_id: str, score: int,
                                reason: str | None = None) -> dict[str, Any]:
    """Rate a knowledge node: 1=dislike, 5=neutral, 10=useful."""
    result = db.score_node(node_id, score, reason)
    if not result:
        raise ValueError("Knowledge node not found.")
    return result

@mcp.tool()
def kolobok_list_knowledge_edges() -> list[dict[str, Any]]:
    """List relationships between knowledge nodes."""
    return db.list_edges()

class TokenProtectedASGI:
    """Protect the MCP endpoint with the same bearer token as the REST API."""
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            supplied = headers.get(b"authorization", b"").decode("utf-8", "ignore")
            expected = os.getenv("APP_ACCESS_TOKEN", "").strip()
            valid = bool(expected) and secrets.compare_digest(supplied, "Bearer " + expected)
            if not valid:
                response = JSONResponse({"detail": "Access token required"}, status_code=401)
                await response(scope, receive, send)
                return
        await self.inner(scope, receive, send)

transport_security = TransportSecuritySettings(
    allowed_hosts=["kolobok-labokus-web.onrender.com", "kolobok-labokus-web.onrender.com:*"],
    allowed_origins=["https://kolobok-labokus-web.onrender.com"],
)
mcp_http_app = TokenProtectedASGI(mcp.streamable_http_app(transport_security=transport_security))
