import os
import secrets
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import db
from .providers import ProviderError, generate_reply, provider_config
from .mcp_server import mcp, mcp_http_app


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.init_db()
    async with mcp.session_manager.run():
        yield


app = FastAPI(title="Kolobok / LabokUS", version="0.1.0", lifespan=lifespan)
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def require_access(authorization: str | None) -> None:
    expected = os.getenv("APP_ACCESS_TOKEN", "").strip()
    if expected:
        supplied = (authorization or "").removeprefix("Bearer ").strip()
        if not secrets.compare_digest(supplied, expected):
            raise HTTPException(status_code=401, detail="Access password required")


class LoginBody(BaseModel):
    token: str = Field(min_length=1, max_length=512)


class ConversationBody(BaseModel):
    title: str = "Новый диалог"


class ChatBody(BaseModel):
    conversation_id: str
    message: str = Field(min_length=1, max_length=12000)


class NodeBody(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    node_type: str = "note"
    content: str = ""
    tags: list[str] = Field(default_factory=list)
    importance: str = "ordinary"
    quality: float | None = None
    context_required: bool = False
    source: str | None = None


class EdgeBody(BaseModel):
    source_id: str
    target_id: str
    relation: str = Field(min_length=1, max_length=80)


class FeedbackBody(BaseModel):
    score: int
    reason: str | None = None


class EventBody(BaseModel):
    source: str = Field(min_length=1, max_length=80)
    event_type: str = Field(min_length=1, max_length=80)
    summary: str = Field(min_length=1, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


@app.get("/")
async def home():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
async def health():
    return {"status": "ok", "name": "Kolobok", "version": app.version}


@app.post("/api/login")
async def login(body: LoginBody):
    expected = os.getenv("APP_ACCESS_TOKEN", "").strip()
    if not expected:
        return {"ok": True, "token_required": False}
    if not secrets.compare_digest(body.token, expected):
        raise HTTPException(status_code=401, detail="Неверный пароль")
    return {"ok": True, "token_required": True}


@app.get("/api/status")
async def status(authorization: str | None = Header(default=None)):
    require_access(authorization)
    cfg = provider_config()
    return {
        "name": "Kolobok",
        "version": app.version,
        "provider": cfg["provider"],
        "model_configured": bool(cfg["api_key"] and cfg["model"]),
        "model": cfg["model"] or None,
        "graph": "sqlite",
        "desktop_agent": "not_connected",
    }


@app.get("/api/conversations")
async def conversations(authorization: str | None = Header(default=None)):
    require_access(authorization)
    return db.list_conversations()


@app.post("/api/conversations")
async def new_conversation(body: ConversationBody,
                           authorization: str | None = Header(default=None)):
    require_access(authorization)
    return db.create_conversation(body.title)


@app.get("/api/conversations/{conversation_id}/messages")
async def conversation_messages(conversation_id: str,
                               authorization: str | None = Header(default=None)):
    require_access(authorization)
    return db.get_messages(conversation_id)


@app.post("/api/chat")
async def chat(body: ChatBody, authorization: str | None = Header(default=None)):
    require_access(authorization)
    try:
        history = db.get_messages(body.conversation_id)
        db.add_message(body.conversation_id, "user", body.message)
        prompt = [{"role": "system", "content":
                   "Ты — Колобок, самостоятельный персональный AI-ассистент. "
                   "Отвечай по-русски, если пользователь не выбрал другой язык. "
                   "Будь точным, честно обозначай ограничения и не выдумывай выполненные действия."}]
        prompt.extend({"role": m["role"], "content": m["content"]} for m in history[-20:])
        prompt.append({"role": "user", "content": body.message})
        answer, provider, model = await generate_reply(prompt)
        saved = db.add_message(body.conversation_id, "assistant", answer, provider, model)
        return {"message": saved}
    except ProviderError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.get("/api/nodes")
async def nodes(q: str | None = None, authorization: str | None = Header(default=None)):
    require_access(authorization)
    return db.list_nodes(q)


@app.post("/api/nodes")
async def add_node(body: NodeBody, authorization: str | None = Header(default=None)):
    require_access(authorization)
    return db.create_node(body.model_dump())


@app.get("/api/nodes/{node_id}")
async def node_detail(node_id: str, authorization: str | None = Header(default=None)):
    require_access(authorization)
    item = db.get_node(node_id)
    if not item:
        raise HTTPException(status_code=404, detail="Node not found")
    return item


@app.post("/api/nodes/{node_id}/feedback")
async def node_feedback(node_id: str, body: FeedbackBody,
                        authorization: str | None = Header(default=None)):
    require_access(authorization)
    try:
        result = db.score_node(node_id, body.score, body.reason)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not result:
        raise HTTPException(status_code=404, detail="Node not found")
    return result


@app.get("/api/edges")
async def edges(authorization: str | None = Header(default=None)):
    require_access(authorization)
    return db.list_edges()


@app.post("/api/edges")
async def add_edge(body: EdgeBody, authorization: str | None = Header(default=None)):
    require_access(authorization)
    try:
        return db.create_edge(body.source_id, body.target_id, body.relation)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Could not create relation: " + str(exc))


@app.post("/api/agent/events")
async def agent_event(body: EventBody, x_agent_token: str | None = Header(default=None),
                      authorization: str | None = Header(default=None)):
    require_access(authorization)
    expected = os.getenv("AGENT_EVENT_TOKEN", "").strip()
    if not expected or not x_agent_token or not secrets.compare_digest(x_agent_token, expected):
        raise HTTPException(status_code=403, detail="Local agent token is not configured or invalid")
    return db.save_event(body.source, body.event_type, body.summary, body.metadata)


# Keep the MCP mount last so existing REST routes retain priority.
app.mount("/", mcp_http_app)
