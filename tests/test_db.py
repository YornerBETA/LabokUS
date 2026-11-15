from app import db


def prepare_database(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "kolobok-test.db"))
    db.init_db()


def test_conversation_and_message(monkeypatch, tmp_path):
    prepare_database(monkeypatch, tmp_path)
    conversation = db.create_conversation("Тест")
    message = db.add_message(conversation["id"], "user", "Привет")
    assert message["content"] == "Привет"
    assert db.get_messages(conversation["id"])[0]["role"] == "user"


def test_knowledge_node_has_structured_id(monkeypatch, tmp_path):
    prepare_database(monkeypatch, tmp_path)
    node = db.create_node({"name": "Test Node", "tags": ["test"]})
    assert node["id"].startswith("KN-test-node-")
    assert db.get_node(node["id"])["tags"] == ["test"]


def test_edges_and_feedback(monkeypatch, tmp_path):
    prepare_database(monkeypatch, tmp_path)
    first = db.create_node({"name": "First"})
    second = db.create_node({"name": "Second"})
    edge = db.create_edge(first["id"], second["id"], "thematic")
    assert edge in db.list_edges()
    assert db.score_node(first["id"], 10, "accurate")["feedback_score"] == 10.0
    assert db.score_node(first["id"], 1, "incorrect")["feedback_score"] == 7.3
