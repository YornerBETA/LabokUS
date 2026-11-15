import json
import os
import re
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def connect():
    path = Path(os.getenv("DATABASE_PATH", "data/kolobok.db"))
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db() -> None:
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            provider TEXT,
            model TEXT,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS nodes (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            node_type TEXT NOT NULL DEFAULT 'note',
            content TEXT NOT NULL DEFAULT '',
            tags TEXT NOT NULL DEFAULT '[]',
            importance TEXT NOT NULL DEFAULT 'ordinary',
            quality REAL,
            context_required INTEGER NOT NULL DEFAULT 0,
            source TEXT,
            feedback_score REAL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS edges (
            id TEXT PRIMARY KEY,
            source_id TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
            target_id TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
            relation TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(source_id, target_id, relation)
        );
        CREATE TABLE IF NOT EXISTS agent_events (
            id TEXT PRIMARY KEY,
            source TEXT NOT NULL,
            event_type TEXT NOT NULL,
            summary TEXT NOT NULL,
            metadata TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL
        );
        """)


def row_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row else None


def create_conversation(title: str = "Новый диалог") -> dict[str, Any]:
    cid, stamp = str(uuid.uuid4()), now_iso()
    with connect() as db:
        db.execute(
            "INSERT INTO conversations(id,title,created_at,updated_at) VALUES(?,?,?,?)",
            (cid, title[:120], stamp, stamp),
        )
    return {"id": cid, "title": title[:120], "created_at": stamp, "updated_at": stamp}


def list_conversations() -> list[dict[str, Any]]:
    with connect() as db:
        rows = db.execute(
            "SELECT * FROM conversations ORDER BY updated_at DESC LIMIT 100"
        ).fetchall()
    return [dict(r) for r in rows]


def add_message(conversation_id: str, role: str, content: str,
                provider: str | None = None, model: str | None = None) -> dict[str, Any]:
    mid, stamp = str(uuid.uuid4()), now_iso()
    with connect() as db:
        exists = db.execute("SELECT id FROM conversations WHERE id=?", (conversation_id,)).fetchone()
        if not exists:
            raise ValueError("Conversation not found")
        db.execute(
            "INSERT INTO messages(id,conversation_id,role,content,provider,model,created_at) VALUES(?,?,?,?,?,?,?)",
            (mid, conversation_id, role, content, provider, model, stamp),
        )
        db.execute("UPDATE conversations SET updated_at=? WHERE id=?", (stamp, conversation_id))
    return {"id": mid, "conversation_id": conversation_id, "role": role,
            "content": content, "provider": provider, "model": model, "created_at": stamp}


def get_messages(conversation_id: str) -> list[dict[str, Any]]:
    with connect() as db:
        rows = db.execute(
            "SELECT * FROM messages WHERE conversation_id=? ORDER BY created_at",
            (conversation_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def create_node(data: dict[str, Any]) -> dict[str, Any]:
    stamp = now_iso()
    day = stamp[:10].replace("-", "")
    slug = re.sub(r"[^a-z0-9]+", "-", data["name"].lower()).strip("-")[:32] or "knowledge"
    tags = json.dumps(data.get("tags", []), ensure_ascii=False)
    with connect() as db:
        sequence = db.execute(
            "SELECT COUNT(*) AS total FROM nodes WHERE created_at LIKE ?", (stamp[:10] + "%",)
        ).fetchone()["total"] + 1
        nid = f"KN-{slug}-{day}-{sequence:04d}"
        db.execute("""INSERT INTO nodes
            (id,name,node_type,content,tags,importance,quality,context_required,source,created_at,updated_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
            (nid, data["name"], data.get("node_type", "note"), data.get("content", ""),
             tags, data.get("importance", "ordinary"), data.get("quality"),
             int(data.get("context_required", False)), data.get("source"), stamp, stamp))
    return get_node(nid)


def get_node(node_id: str) -> dict[str, Any] | None:
    with connect() as db:
        row = db.execute("SELECT * FROM nodes WHERE id=?", (node_id,)).fetchone()
    if not row:
        return None
    result = dict(row)
    result["tags"] = json.loads(result["tags"])
    result["context_required"] = bool(result["context_required"])
    return result


def list_nodes(query: str | None = None) -> list[dict[str, Any]]:
    with connect() as db:
        if query:
            rows = db.execute("""SELECT * FROM nodes WHERE name LIKE ? OR content LIKE ?
                ORDER BY updated_at DESC LIMIT 300""", (f"%{query}%", f"%{query}%")).fetchall()
        else:
            rows = db.execute("SELECT * FROM nodes ORDER BY updated_at DESC LIMIT 300").fetchall()
    results = []
    for row in rows:
        item = dict(row)
        item["tags"] = json.loads(item["tags"])
        item["context_required"] = bool(item["context_required"])
        results.append(item)
    return results


def create_edge(source_id: str, target_id: str, relation: str) -> dict[str, Any]:
    eid, stamp = str(uuid.uuid4()), now_iso()
    with connect() as db:
        db.execute("INSERT INTO edges(id,source_id,target_id,relation,created_at) VALUES(?,?,?,?,?)",
                   (eid, source_id, target_id, relation, stamp))
    return {"id": eid, "source_id": source_id, "target_id": target_id,
            "relation": relation, "created_at": stamp}


def list_edges() -> list[dict[str, Any]]:
    with connect() as db:
        return [dict(r) for r in db.execute("SELECT * FROM edges ORDER BY created_at DESC LIMIT 1000")]


def score_node(node_id: str, score: int, reason: str | None) -> dict[str, Any] | None:
    if score not in (1, 5, 10):
        raise ValueError("Score must be 1, 5, or 10")
    with connect() as db:
        row = db.execute("SELECT feedback_score FROM nodes WHERE id=?", (node_id,)).fetchone()
        if not row:
            return None
        old = row["feedback_score"]
        # Blend repeated ratings gradually; a single rating does not permanently dominate.
        new = float(score) if old is None else round(float(old) * 0.7 + score * 0.3, 2)
        db.execute("UPDATE nodes SET feedback_score=?,updated_at=? WHERE id=?",
                   (new, now_iso(), node_id))
    return {"id": node_id, "feedback_score": new, "reason": reason}


def save_event(source: str, event_type: str, summary: str,
               metadata: dict[str, Any]) -> dict[str, Any]:
    eid, stamp = str(uuid.uuid4()), now_iso()
    with connect() as db:
        db.execute("""INSERT INTO agent_events(id,source,event_type,summary,metadata,created_at)
            VALUES(?,?,?,?,?,?)""",
            (eid, source, event_type, summary[:2000],
             json.dumps(metadata, ensure_ascii=False)[:8000], stamp))
    return {"id": eid, "source": source, "event_type": event_type,
            "summary": summary[:2000], "created_at": stamp}
