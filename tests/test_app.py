import pytest
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock

os.environ["PROJECT_ID"] = "test-project"
os.environ["LOCATION"] = "us-central1"

with patch("vertexai.init"), patch("vertexai.generative_models.GenerativeModel"):
    from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c

def test_home_loads(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"ElectionBot" in res.data

def test_health_check(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "ok"

def test_chat_no_message(client):
    res = client.post("/chat", json={})
    assert res.status_code == 400

def test_chat_empty_message(client):
    res = client.post("/chat", json={"message": ""})
    assert res.status_code == 400

def test_chat_message_too_long(client):
    res = client.post("/chat", json={"message": "x" * 501})
    assert res.status_code == 400

def test_chat_valid_message(client):
    mock_response = MagicMock()
    mock_response.text = "Elections in India are conducted by the Election Commission."
    mock_chat = MagicMock()
    mock_chat.send_message.return_value = mock_response
    with patch("app.model") as mock_model:
        mock_model.start_chat.return_value = mock_chat
        res = client.post("/chat", json={"message": "How do elections work?"})
        assert res.status_code == 200
        data = json.loads(res.data)
        assert "reply" in data